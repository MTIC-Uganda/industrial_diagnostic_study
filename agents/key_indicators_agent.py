#!/usr/bin/env python3
"""
key_indicators_agent — ingest a UBOS-style scorecard spreadsheet into the
`key_indicators` collection (the manufacturing-overview KPI cards).

Reads the uploaded spreadsheet plus the operator's intent sidecar, asks the Claude
CLI to map them to updates for EXISTING key_indicators slugs, and applies them to
PocketBase. Safety is structural (ADR-017): it only ever PATCHes a slug that already
exists, only the whitelisted value/label fields, and never creates, renames, or
deletes a record. So a wrong intent can change a figure (caught in staging review)
but can never invent or destroy a card, and nothing is written to a file.

Usage:  python agents/key_indicators_agent.py <spreadsheet-path>
Env:    PB_URL, PB_ADMIN_EMAIL, PB_ADMIN_PASSWORD, CLAUDE_BIN
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# Only these key_indicators fields may be updated from a scorecard upload.
UPDATABLE_FIELDS = {"value", "pct", "sub_value", "year", "source", "source_detail", "confidence"}
MAX_SHEET_CHARS = 12000


def read_sheet(path):
    """Read a spreadsheet into a compact text view (sheet names + non-empty cells)."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    out = []
    for ws in wb.worksheets:
        out.append(f"# sheet: {ws.title}")
        for row in ws.iter_rows(values_only=True):
            cells = [str(c) for c in row if c not in (None, "")]
            if cells:
                out.append(" | ".join(cells))
            if sum(len(x) for x in out) > MAX_SHEET_CHARS:
                out.append("... (truncated)")
                wb.close()
                return "\n".join(out)
    wb.close()
    return "\n".join(out)


def plan_prompt(intent, sheet_text, current):
    """Build the LLM prompt. `current` = list of {slug, label, value} already in PocketBase."""
    cur = "\n".join(f"- {c.get('slug')}: {c.get('label')} (current value: {c.get('value')})"
                    for c in current)
    return (
        "You update Uganda's manufacturing dashboard KPI cards from a UBOS scorecard.\n"
        "These are the EXISTING key_indicators slugs you may update (use these slugs EXACTLY, "
        "never invent new ones):\n" + cur + "\n\n"
        "OPERATOR INTENT:\n" + intent + "\n\n"
        "SPREADSHEET DATA:\n" + sheet_text + "\n\n"
        "Output ONLY a JSON array of updates, each an object with a \"slug\" that is one of the "
        "existing slugs above, plus any of these fields to change: value, pct, sub_value, year, "
        "source, source_detail. Do not include a slug that is not in the list. Match the operator's "
        "intent to the correct slug (e.g. import figures go to an imports card, never the exports "
        "card). If nothing should change, output []. No prose, no markdown."
    )


def parse_plan(text):
    """Pull the JSON array of updates out of the model reply. Returns a list (possibly empty)."""
    if not text:
        return []
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end <= start:
        return []
    try:
        data = json.loads(text[start:end + 1])
    except ValueError:
        return []
    return data if isinstance(data, list) else []


def validate_updates(raw, allowed_slugs):
    """Keep only updates targeting an EXISTING slug, with only whitelisted fields.

    This is the security boundary: the returned updates can change figures on cards
    that already exist, and nothing else.
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
    """Apply validated updates via injected id_for_slug(slug)->id and patch(id, fields).

    Returns the list of slugs actually updated.
    """
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
    """Return an admin token, or None if creds are missing/rejected."""
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
    """[{slug,label,value,id}] for the existing key_indicators (public read)."""
    url = _pb_url() + "/api/collections/key_indicators/records?perPage=200&sort=display_order"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            items = json.loads(r.read()).get("items", [])
    except Exception:
        return []
    return [{"slug": i.get("slug"), "label": i.get("label"),
             "value": i.get("value"), "id": i.get("id")} for i in items]


def main(path):
    path = Path(path)
    sidecar = path.with_suffix(path.suffix + ".task.md")
    intent = sidecar.read_text("utf-8") if sidecar.exists() else "(no intent provided)"
    try:
        sheet_text = read_sheet(path)
    except Exception as e:  # noqa
        print(f"key_indicators_agent: cannot read spreadsheet: {e}")
        return []
    current = fetch_key_indicators()
    if not current:
        print("key_indicators_agent: no existing key_indicators to update — aborting (no create).")
        return []
    allowed = [c["slug"] for c in current if c.get("slug")]
    by_slug = {c["slug"]: c["id"] for c in current if c.get("slug")}

    prompt = plan_prompt(intent, sheet_text, current)
    out = subprocess_claude(prompt)
    updates = validate_updates(parse_plan(out), allowed)
    if not updates:
        print("key_indicators_agent: no valid updates proposed (nothing changed).")
        return []

    token = pb_auth()
    if not token:
        print("key_indicators_agent: no PocketBase admin token — cannot write. "
              f"Proposed updates: {[u['slug'] for u in updates]}")
        return []

    def patch(rec_id, fields):
        req = urllib.request.Request(
            _pb_url() + f"/api/collections/key_indicators/records/{rec_id}",
            method="PATCH", data=json.dumps(fields).encode(),
            headers={"Content-Type": "application/json", "Authorization": token})
        with urllib.request.urlopen(req, timeout=15) as r:
            r.read()

    done = apply_updates(updates, by_slug.get, patch)
    print(f"key_indicators_agent: updated {len(done)} card(s): {', '.join(done)}")
    return done


def subprocess_claude(prompt):
    """One Claude CLI call; returns stdout text (empty on failure)."""
    import subprocess
    env = dict(os.environ)
    env.setdefault("HOME", "/root")
    try:
        r = subprocess.run([env.get("CLAUDE_BIN", "claude"), "-p", "--output-format", "text"],
                           input=prompt, capture_output=True, text=True, env=env, timeout=300)
        return r.stdout.strip() if r.returncode == 0 else ""
    except Exception:
        return ""


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: key_indicators_agent.py <spreadsheet-path>")
    main(sys.argv[1])
