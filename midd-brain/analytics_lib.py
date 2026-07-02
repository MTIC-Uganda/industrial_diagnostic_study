"""
analytics_lib — wire the analytics sandbox (ADR-020) into Ask MIDD.

Builds a READ-ONLY snapshot of the PocketBase collections as pandas DataFrames and
holds the small pure helpers that turn a question into analysis code and an analysis
result into answer context. The network fetch and the CLI/sandbox calls are injected
by app.py, so everything here is import-safe and unit-testable (ADR-018).

The DataFrames are a snapshot: the analysis code (run in analytics_sandbox) can query
and compute over them, but there is no PocketBase handle in that namespace, so it can
never alter a table (ADR-017 holds by construction).
"""
import json

# PocketBase collection -> DataFrame name the analysis code sees. The read-only
# surface the team may analyse (no per-establishment contact/owner PII beyond what
# the dashboard already shows publicly).
ANALYTICS_COLLECTIONS = {
    "industries": "industries",
    "value_chains": "value_chains",
    "key_indicators": "key_indicators",
    "kpi_indicators": "kpi_indicators",
    "key_indicator_categories": "key_indicator_categories",
    "sector_comparison": "sector_comparison",
    "macro_trend": "macro_trend",
}


def build_dataframes(fetch):
    """fetch(collection) -> list[dict]. Returns {name: pandas.DataFrame} (read-only snapshot)."""
    import pandas as pd
    return {name: pd.DataFrame(fetch(coll) or [])
            for coll, name in ANALYTICS_COLLECTIONS.items()}


def schema_hint(dataframes):
    """LLM-readable list of the available DataFrames, their row counts and columns."""
    lines = []
    for name, df in dataframes.items():
        cols = ", ".join(map(str, list(df.columns))) if len(df.columns) else "(empty)"
        lines.append(f"- {name} ({len(df)} rows): {cols}")
    return "\n".join(lines)


def planner_prompt(schema):
    """Prompt that asks the model to EITHER write read-only pandas analysis code OR pass."""
    return (
        "You can run read-only Python (pandas as pd, numpy as np, plus scikit-learn, scipy, "
        "statsmodels and matplotlib) over these in-memory DataFrames to answer the question:\n"
        f"{schema}\n\n"
        "Rules:\n"
        "- The DataFrames are read-only snapshots; you may query/aggregate/model/plot but you "
        "cannot and must not modify any data source.\n"
        "- Assign your answer to a variable named `result`. To return a chart, draw it with "
        "matplotlib (it is captured automatically).\n"
        "- Do NOT import os/sys/subprocess or open files; only the analysis libraries above.\n"
        "- If the question needs NO computation over the data (it is conceptual, about the "
        "project, or off-topic), reply with exactly: NONE\n"
        "Output ONLY the Python code (or NONE), no prose, no markdown fences."
    )


def extract_code(text):
    """Pull analysis code out of the planner's reply. Returns code str or None."""
    if not text:
        return None
    t = text.strip()
    if t.upper() == "NONE" or not t:
        return None
    # strip a ```python ... ``` fence if the model added one
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        if t.rstrip().endswith("```"):
            t = t.rsplit("```", 1)[0]
    t = t.strip()
    # a bare "NONE" wrapped in a fence, or an empty body -> no analysis
    if not t or t.upper() == "NONE":
        return None
    return t


def format_analysis_result(res):
    """Turn an analytics_sandbox result dict into an answer-context block (text)."""
    if not res or not res.get("ok"):
        return ""
    parts = ["ANALYSIS RESULT (computed live from the data — use these exact figures):"]
    if res.get("result") is not None:
        parts.append(json.dumps(res["result"], ensure_ascii=False)[:3000])
    if res.get("stdout"):
        parts.append("printed output: " + res["stdout"][:1000])
    if res.get("image"):
        parts.append("(a chart was generated and will be shown to the user)")
    return "\n".join(parts) + "\n\n"
