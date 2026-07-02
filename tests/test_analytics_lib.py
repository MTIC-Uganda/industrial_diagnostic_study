"""Tests for analytics_lib — the snapshot + orchestration glue for the analytics
sandbox (ADR-020). Pure helpers, no network (fetch is injected)."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "midd-brain"))
import analytics_lib as al  # noqa: E402


def _fetch(coll):
    data = {
        "industries": [{"region": "Central", "district": "Wakiso", "employees": 10},
                       {"region": "Northern", "district": "Gulu", "employees": 5}],
        "value_chains": [{"name": "Iron & Steel", "slug": "iron-steel"}],
    }
    return data.get(coll, [])


def test_build_dataframes_shapes():
    dfs = al.build_dataframes(_fetch)
    assert set(dfs) == set(al.ANALYTICS_COLLECTIONS.values())
    assert len(dfs["industries"]) == 2
    assert list(dfs["value_chains"]["name"]) == ["Iron & Steel"]
    assert len(dfs["macro_trend"]) == 0            # empty collection -> empty frame


def test_schema_hint_lists_columns_and_counts():
    dfs = al.build_dataframes(_fetch)
    hint = al.schema_hint(dfs)
    assert "industries (2 rows)" in hint
    assert "region" in hint
    assert "value_chains (1 rows)" in hint
    assert "(empty)" in hint                        # macro_trend has no columns


def test_planner_prompt_mentions_readonly_and_result():
    p = al.planner_prompt("- industries (2 rows): region")
    assert "read-only" in p.lower()
    assert "result" in p
    assert "NONE" in p


def test_extract_code_variants():
    assert al.extract_code("NONE") is None
    assert al.extract_code("") is None
    assert al.extract_code(None) is None
    assert al.extract_code("   \n  ") is None
    assert al.extract_code("result = industries.shape[0]") == "result = industries.shape[0]"
    fenced = "```python\nresult = 1\n```"
    assert al.extract_code(fenced) == "result = 1"
    assert al.extract_code("```\nNONE\n```") is None


def test_format_analysis_result():
    assert al.format_analysis_result(None) == ""
    assert al.format_analysis_result({"ok": False, "error": "x"}) == ""
    out = al.format_analysis_result({"ok": True, "result": {"Central": 1},
                                     "stdout": "hi", "image": "data:image/png;base64,AAA"})
    assert "ANALYSIS RESULT" in out
    assert "Central" in out
    assert "printed output: hi" in out
    assert "a chart was generated" in out


def test_end_to_end_with_sandbox():
    """analytics_lib + analytics_sandbox together: plan-shaped code runs read-only."""
    import analytics_sandbox as sb
    dfs = al.build_dataframes(_fetch)
    code = "result = int(industries['employees'].sum())"
    res = sb.execute_restricted(code, dfs)
    assert res["ok"]
    assert res["result"] == 15
    block = al.format_analysis_result(res)
    assert "15" in block
