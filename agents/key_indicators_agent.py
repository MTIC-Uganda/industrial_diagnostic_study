#!/usr/bin/env python3
"""
key_indicators_agent — ingest a UBOS scorecard spreadsheet into the `key_indicators`
collection, COMPUTING derived figures with the read-only analytics sandbox (ADR-020).

A UBOS "composition of imports/exports" workbook is raw SITC data, not a ready-made KPI.
So this agent loads every sheet as a pandas DataFrame and asks the Claude CLI to write
read-only Python that computes the figure the operator wants (e.g. manufactured imports
= sum of SITC sections 5-8 excluding 68 for the latest year) and sets `result` to a list
of updates for EXISTING key_indicators slugs. That code runs in analytics_sandbox — no
PocketBase handle, no network, restricted builtins, resource-limited — so it can query
and compute but never touch a data source. The result is applied additively to
PocketBase: only existing slugs, only whitelisted display fields, never creating,
renaming, or deleting a card (ADR-017). A wrong figure is caught in staging review; a
missing/uncomputable one leaves the card untouched.

Usage:  python agents/key_indicators_agent.py <spreadsheet-path>
Env:    PB_URL, PB_ADMIN_EMAIL, PB_ADMIN_PASSWORD, CLAUDE_BIN
"""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "midd-brain"))
import analytics_sandbox  # noqa: E402 - read-only compute sandbox (ADR-020)

# Only these key_indicators fields may be written from a scorecard upload.
UPDATABLE_FIELDS = {"value", "pct", "sub_value", "year", "source", "source_detail", "confidence"}
MAX_PREVIEW_ROWS = 14
MAX_PREVIEW_CHARS = 2600


def load_dataframes(path):
    """Load every sheet into a pandas DataFrame (header=None; the model reads the layout)."""
    import pandas as pd
    xl = pd.ExcelFile(path)
    return {name: xl.parse(name, header=None) for name in xl.sheet_names}


def preview(dfs):
    """Compact per-sheet preview (shape + head) so the model can write correct code."""
    parts = []
    for name, df in dfs.items():
        head = df.head(MAX_PREVIEW_ROWS).to_string(max_cols=22)[:MAX_PREVIEW_CHARS]
        parts.append("Sheet %r: shape %s\n%s" % (name, tuple(df.shape), head))
    return "\n\n".join(parts)


def code_prompt(intent, preview_text, current):
    """Prompt asking the model to write read-only code that computes + formats updates."""
    cur = "\n".join("- %s: %s (current value: %s)"
                    % (c.get("slug"), c.get("label"), c.get("value")) for c in current)
    return (
        "You update Uganda's manufacturing dashboard KPI cards from a UBOS scorecard workbook.\n"
        "The sheets are available to your code as a dict `dfs` mapping each sheet name to a pandas "
        "DataFrame (loaded with header=None, so labels are integer positions; use the preview to "
        "locate the header rows and the columns/rows you need).\n\n"
        "PREVIEW:\n" + preview_text + "\n\n"
        "EXISTING key_indicators slugs you may update (use these EXACT slugs, never invent one):\n"
        + cur + "\n\n"
        "OPERATOR INTENT:\n" + intent + "\n\n"
        "Write READ-ONLY Python (pandas as pd and numpy as np are already available; `dfs` holds the "
        "sheets) that COMPUTES the figure(s) the intent asks for and sets a variable `result` to a "
        "JSON-serializable list of updates. Each update is a dict with a `slug` from the list above "
        "plus any of: value, pct, sub_value, year, source. Format value/sub_value as human display "
        "strings (for example 'USD 6.3B' or '45.1% of imports'), not raw floats. Apply the correct "
        "domain definition (for instance, manufactured trade = SITC sections 5,6,7,8 excluding 68). "
        "Only include a slug from the list; if you cannot compute a defensible figure, set result = []. "
        "Do not import os, sys, or subprocess, do not open files or the network — only dfs, pd, np. "
        "Output ONLY the Python code: no prose, no markdown fences."
    )


def extract_code(text):
    """Strip any markdown fence and return the code (or '' for NONE/empty)."""
    if not text:
        return ""
    t = text.strip()
    if t.upper() == "NONE":
        return ""
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        if t.rstrip().endswith("```"):
            t = t.rsplit("```", 1)[0]
    t = t.strip()
    # Normalize typographic characters the model tends to emit in comments/strings
    # (en/em dash, smart quotes, non-breaking space) that would otherwise break ast.parse.
    return t.translate({0x2013: 0x2d, 0x2014: 0x2d, 0x2018: 0x27, 0x2019: 0x27,
                        0x201c: 0x22, 0x201d: 0x22, 0x00a0: 0x20})


def validate_updates(raw, allowed_slugs):
    """Keep only updates targeting an EXISTING slug, with only whitelisted fields.

    The security boundary: results can change figures on cards that already exist, nothing else.
    """
    allowed = set(allowed_slugs)
    clean = []
    for u in raw or []:
        if not isinstance(u, dict):
            continue
        slug = u.get("slug")
        if slug not in allowed:
            continue
        fields = {k: ("" if v is None else str(v))
                  for k, v in u.items() if k in UPDATABLE_FIELDS}
        if fields:
            clean.append({"slug": slug, "fields": fields})
    return clean


def apply_updates(updates, id_for_slug, patch):
    """Apply validated updates via injected id_for_slug(slug)->id and patch(id, fields)."""
    done = []
    for u in updates:
        rec_id = id_for_slug(u["slug"])
        if not rec_id:
            continue
        patch(rec_id, u["fields"])
        done.append(u["slug"])
    return done


# ── PocketBase I/O (thin; wired in main) ──────────────────────────────────────
def _pb_url():
    return os.environ.get("PB_URL", "http://127.0.0.1:8090").rstrip("/")


def pb_auth():
    email = os.environ.get("PB_ADMIN_EMAIL", "")
    pw = os.environ.get("PB_ADMIN_PASSWORD", "")
    if not email or not pw:
        return None
    for ep in ("/api/collections/_superusers/auth-with-password", "/api/admins/auth-with-password"):
        try:
            req = urllib.request.Request(
                _pb_url() + ep, method="POST",
                data=json.dumps({"identity": email, "password": pw}).encode(),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read()).get("token")
        except urllib.error.HTTPError:
            continue
        except Exception:
            return None
    return None


def fetch_key_indicators():
    url = _pb_url() + "/api/collections/key_indicators/records?perPage=200&sort=display_order"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            items = json.loads(r.read()).get("items", [])
    except Exception:
        return []
    return [{"slug": i.get("slug"), "label": i.get("label"),
             "value": i.get("value"), "id": i.get("id")} for i in items]


def subprocess_claude(prompt):
    """One Claude CLI call; returns stdout text (empty on failure)."""
    env = dict(os.environ)
    env.setdefault("HOME", "/root")
    try:
        r = subprocess.run([env.get("CLAUDE_BIN", "claude"), "-p", "--output-format", "text"],
                           input=prompt, capture_output=True, text=True, env=env, timeout=300)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


def main(path):
    path = Path(path)
    sidecar = path.with_suffix(path.suffix + ".task.md")
    intent = sidecar.read_text("utf-8") if sidecar.exists() else "(no intent provided)"
    try:
        dfs = load_dataframes(path)
    except Exception as e:  # noqa
        print("key_indicators_agent: cannot read spreadsheet: %s" % e)
        return []
    current = fetch_key_indicators()
    if not current:
        print("key_indicators_agent: no existing key_indicators to update - aborting (no create).")
        return []
    allowed = [c["slug"] for c in current if c.get("slug")]
    by_slug = {c["slug"]: c["id"] for c in current if c.get("slug")}

    # Generate + run the compute, retrying with error feedback — model-written code is
    # non-deterministic (a stray en-dash or truncated string on one attempt, clean the next).
    base = code_prompt(intent, preview(dfs), current)
    updates, last = [], ""
    for attempt in range(3):
        prompt = base if attempt == 0 else (
            base + "\n\nYour previous attempt failed with: %s\n"
            "Return VALID, plain-ASCII Python only (no smart quotes or dashes)." % last)
        code = extract_code(subprocess_claude(prompt))
        if not code:
            last = "no code produced"
            print("key_indicators_agent: attempt %d - %s" % (attempt + 1, last))
            continue
        res = analytics_sandbox.run_analysis(code, {"dfs": dfs}, timeout=25)
        if not res.get("ok"):
            last = res.get("error") or "computation error"
            print("key_indicators_agent: attempt %d - computation failed: %s" % (attempt + 1, last))
            continue
        updates = validate_updates(res.get("result") or [], allowed)
        if updates:
            break
        last = "no valid updates (result=%s)" % json.dumps(res.get("result"))[:200]
        print("key_indicators_agent: attempt %d - %s" % (attempt + 1, last))
    if not updates:
        print("key_indicators_agent: no valid updates after retries (nothing changed).")
        return []

    token = pb_auth()
    if not token:
        print("key_indicators_agent: no PocketBase admin token - cannot write. "
              "computed updates: %s" % [u["slug"] for u in updates])
        return []

    def patch(rec_id, fields):
        req = urllib.request.Request(
            _pb_url() + "/api/collections/key_indicators/records/%s" % rec_id,
            method="PATCH", data=json.dumps(fields).encode(),
            headers={"Content-Type": "application/json", "Authorization": token})
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read()

    done = apply_updates(updates, by_slug.get, patch)
    print("key_indicators_agent: updated %d card(s): %s" % (len(done), ", ".join(done)))
    return done


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: key_indicators_agent.py <spreadsheet-path>")
    main(sys.argv[1])
