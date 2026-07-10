#!/usr/bin/env python3
# v2 — pct coercion + sandbox exceptions (Hillary c1691dc); brain redeploy triggered here
"""
key_indicators_agent — ingest a UBOS scorecard spreadsheet OR a KPI source PDF
into the `key_indicators` collection, COMPUTING derived figures with the read-only
analytics sandbox (ADR-020) for spreadsheets, or extracting them directly via the
Claude CLI for PDFs.

Spreadsheet path (UBOS composition workbook):
  Loads every sheet as a pandas DataFrame, asks the Claude CLI to write read-only
  Python that computes the figure (e.g. manufactured imports = sum of SITC 5-8
  excluding 68 for the latest year) and sets `result` to a list of updates for
  EXISTING key_indicators slugs. Code runs in analytics_sandbox — no PocketBase
  handle, no network, restricted builtins — so it can query and compute but never
  touch a data source.

PDF path (URA tax handbook, banking sector report, UIA memo, UBOS NLFS, etc.):
  Extracts text from the PDF via pypdf, then asks the Claude CLI to read the
  operator intent and return the relevant figure(s) as a JSON array directly.
  No sandbox needed — the model extracts, not computes.

Both paths apply results additively to PocketBase: only existing slugs, only
whitelisted display fields, never creating, renaming, or deleting a card (ADR-017).
A wrong figure is caught in staging review; a missing/uncomputable one leaves the
card untouched.

Usage:  python agents/key_indicators_agent.py <spreadsheet-or-pdf-path>
Env:    PB_URL, PB_ADMIN_EMAIL, PB_ADMIN_PASSWORD, CLAUDE_BIN
"""
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "midd-brain"))
import analytics_sandbox  # noqa: E402 - read-only compute sandbox (ADR-020)

SPREADSHEET_SUFFIXES = (".xlsx", ".xls", ".csv")
PDF_SUFFIXES = (".pdf",)

# Only these key_indicators fields may be written from an upload.
# Includes FY variants and the import side of the exports card.
UPDATABLE_FIELDS = {
    "value", "pct", "sub_value", "year", "source", "source_detail", "confidence",
    "value_fy", "pct_fy", "sub_value_fy", "year_fy", "source_fy", "confidence_fy",
    "import_value", "import_sub", "import_value_fy", "import_sub_fy",
}

# PocketBase stores these key_indicators fields as NUMBER, not text. A display
# string like "45.1% of imports" must be coerced to 45.1 or PocketBase 400s the
# whole write (the real cause of the ubos_exports upload failure).
NUMBER_FIELDS = {"pct", "pct_fy"}

# PocketBase SELECT fields: only these values are accepted. Any other value causes a 400.
SELECT_FIELDS = {
    "confidence": {"exact", "estimated", "indicative"},
    "confidence_fy": {"exact", "estimated", "indicative"},
}

# ── Deterministic UBOS SITC computation (bypasses the LLM for known workbook formats) ──
# These sheets appear in every UBOS Composition of Exports/Imports workbook.
# CY year columns are stored as numpy.float64 (e.g. 2025.0); FY as strings ("2024/25").
_UBOS_EXP_CY = "CY_EXP_Value_SITC"
_UBOS_EXP_FY = "FY_EXP_Value_SITC"
_UBOS_IMP_CY = "CY_Value SITC"
_UBOS_IMP_FY_BASE = "FY_Value SITC"   # may have trailing space in the actual file


def _sitc_mfg_compute(df):
    """Sum SITC sections 5,6,7,8 excl. 68 for the latest non-zero year in a UBOS SITC sheet.

    Sheet layout (header=None): rows 0-2 notes, row 3 = year labels, row 4+ = data.
    Column 0 = SITC 2-digit code, column 1 = description, columns 2+ = values by year.

    Returns (mfg_usd_thousands, total_usd_thousands, year_label) or None.
    """
    try:
        import pandas as pd
    except ImportError:
        return None
    if df.shape[0] < 5 or df.shape[1] < 3:
        return None
    header = df.iloc[3].tolist()
    data = df.iloc[4:]
    codes = data.iloc[:, 0].astype(str).str.strip()
    is_mfg = codes.str.match(r"^[5-8]\d") & (codes != "68")
    for ci in range(df.shape[1] - 1, 1, -1):
        col = pd.to_numeric(data.iloc[:, ci], errors="coerce")
        total = float(col.dropna().sum())
        if total <= 0:
            continue
        mfg = float(col[is_mfg.values].sum())
        raw = str(header[ci]) if ci < len(header) else ""
        try:
            year_label = str(int(float(raw)))   # float64 2025.0 -> "2025"
        except (ValueError, TypeError):
            year_label = raw.strip()             # "2024/25" already a string
        return mfg, total, year_label
    return None


def _try_ubos_sitc_compute(dfs, allowed_slugs):
    """Deterministic manufactured-trade computation for UBOS SITC workbooks.

    Detects the workbook type (exports vs imports) from sheet names, computes
    CY and FY figures without calling the LLM, and returns a raw updates list
    (suitable for validate_updates) or None if the sheets are not recognised.
    """
    sheets = set(dfs.keys())

    if _UBOS_EXP_CY in sheets and _UBOS_EXP_FY in sheets:
        slug, direction = "exports", "exports"
        cy_sheet, fy_sheet = _UBOS_EXP_CY, _UBOS_EXP_FY
    elif _UBOS_IMP_CY in sheets:
        slug, direction = "mfg_imports", "imports"
        cy_sheet = _UBOS_IMP_CY
        fy_sheet = next((s for s in sheets if s.strip() == _UBOS_IMP_FY_BASE), None)
    else:
        return None

    if slug not in allowed_slugs:
        return None

    cy = _sitc_mfg_compute(dfs[cy_sheet]) if cy_sheet in dfs else None
    fy = _sitc_mfg_compute(dfs[fy_sheet]) if fy_sheet and fy_sheet in dfs else None

    if not cy and not fy:
        return None

    src_base = "UBOS Composition of %s (SITC 5-8 excl. 68)" % direction.capitalize()
    update = {"slug": slug}

    if cy:
        mfg, total, year = cy
        pct = round(mfg / total * 100, 2)
        update.update({
            "value": "USD %.1fB" % (mfg / 1e6),
            "pct": pct,
            "sub_value": "%.1f%% of total %s" % (pct, direction),
            "year": year,
            "source": src_base,
            "confidence": "exact",
        })

    if fy:
        mfg_fy, total_fy, year_fy = fy
        pct_fy = round(mfg_fy / total_fy * 100, 2)
        update.update({
            "value_fy": "USD %.1fB" % (mfg_fy / 1e6),
            "pct_fy": pct_fy,
            "sub_value_fy": "%.1f%% of total %s" % (pct_fy, direction),
            "year_fy": year_fy,
            "source_fy": src_base,
            "confidence_fy": "exact",
        })

    return [update]


def coerce_field(name, value):
    """Coerce one field to what PocketBase's schema expects.

    Number fields -> the first numeric token as a float ("45.1% of imports" -> 45.1);
    returns None when a number field carries no parseable number, so the caller drops
    it rather than send a bad type and 400 the record.
    SELECT fields -> validated against the allowed set; returns None for invalid values
    so the caller drops them rather than sending an invalid option and 400ing the record.
    Text fields -> str (None -> "").
    """
    if name in NUMBER_FIELDS:
        if value is None:
            return None
        m = re.search(r"-?\d+(?:\.\d+)?", str(value))
        return float(m.group()) if m else None
    if name in SELECT_FIELDS:
        if value is None or str(value) not in SELECT_FIELDS[name]:
            return None
        return str(value)
    return "" if value is None else str(value)

MAX_PREVIEW_ROWS = 14
MAX_PREVIEW_CHARS = 2600
MAX_PDF_CHARS = 9000


def load_dataframes(path):
    """Load every sheet into a pandas DataFrame (header=None; the model reads the layout)."""
    import pandas as pd
    xl = pd.ExcelFile(path)
    return {name: xl.parse(name, header=None) for name in xl.sheet_names}


def load_pdf_text(path):
    """Extract all text from a PDF using pypdf."""
    import pypdf
    reader = pypdf.PdfReader(str(path))
    parts = []
    for page in reader.pages:
        t = page.extract_text() or ""
        if t.strip():
            parts.append(t)
    return "\n\n".join(parts)


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
        "plus any of: value, pct, sub_value, year, source, source_detail, "
        "confidence (MUST be exactly 'exact', 'estimated', or 'indicative' — no other value accepted), "
        "value_fy, pct_fy, sub_value_fy, year_fy, source_fy, confidence_fy, import_value, import_sub, "
        "import_value_fy, import_sub_fy. "
        "Format value/sub_value/import_value/import_sub as human display strings "
        "(for example 'USD 6.3B' or '45.1% of imports'), not raw floats. "
        "If Calendar Year (CY) and Financial Year (FY) data are both available in the workbook, "
        "include both: CY figures in the main fields (value/pct/sub_value/year), "
        "FY figures in the _fy fields (value_fy/pct_fy/sub_value_fy/year_fy). "
        "Apply the correct domain definition (for instance, manufactured trade = SITC sections "
        "5,6,7,8 excluding 68). "
        "Only include a slug from the list; if you cannot compute a defensible figure, set result = []. "
        "Do not import os, sys, or subprocess, do not open files or the network — only dfs, pd, np. "
        "Output ONLY the Python code: no prose, no markdown fences."
    )


def pdf_extract_prompt(intent, text, current):
    """Prompt asking the model to extract KPI figures directly from PDF text as JSON."""
    cur = "\n".join("- %s: %s (current value: %s)"
                    % (c.get("slug"), c.get("label"), c.get("value")) for c in current)
    truncated = text[:MAX_PDF_CHARS] + ("\n...[truncated]..." if len(text) > MAX_PDF_CHARS else "")
    return (
        "You update Uganda's manufacturing dashboard KPI cards from a source document.\n"
        "Read the OPERATOR INTENT to know which figure(s) to extract, then return ONLY "
        "a JSON array of updates. Each update is a dict with a `slug` from the existing "
        "list plus any of: value, pct, sub_value, year, source, source_detail, confidence, "
        "value_fy, pct_fy, sub_value_fy, year_fy, source_fy.\n"
        "Format value/sub_value as human display strings (e.g. 'UGX 5.2T' or '19.4% of tax revenue'). "
        "confidence and confidence_fy MUST be exactly 'exact', 'estimated', or 'indicative' — "
        "no other value is accepted. Use 'exact' for official published figures, "
        "'estimated' for derived or approximated ones, 'indicative' for rough order-of-magnitude.\n\n"
        "EXISTING key_indicators slugs:\n" + cur + "\n\n"
        "OPERATOR INTENT:\n" + intent + "\n\n"
        "DOCUMENT TEXT (may be truncated):\n" + truncated + "\n\n"
        "Return ONLY a valid JSON array, no prose, no markdown fences. "
        "Example: [{\"slug\": \"tax\", \"value\": \"UGX 5.2T\", \"pct\": \"19.4\", "
        "\"year\": \"FY2023/24\", \"source\": \"URA Taxation Handbook FY2023/24\", "
        "\"confidence\": \"exact\"}]\n"
        "If you cannot find a defensible figure, return []."
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
    return t.translate({0x2013: 0x2d, 0x2014: 0x2d, 0x2018: 0x27, 0x2019: 0x27,
                        0x201c: 0x22, 0x201d: 0x22, 0x00a0: 0x20})


def extract_json(text):
    """Strip markdown fences from a JSON response and return the raw JSON string."""
    if not text:
        return ""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else ""
        if t.rstrip().endswith("```"):
            t = t.rsplit("```", 1)[0]
    return t.strip()


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
        fields = {}
        for k, v in u.items():
            if k not in UPDATABLE_FIELDS:
                continue
            cv = coerce_field(k, v)
            if cv is None:      # unparseable number -> skip it, never 400 the write
                continue
            fields[k] = cv
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


# ── PocketBase I/O ─────────────────────────────────────────────────────────────
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


def _compute_from_spreadsheet(path, intent, current, allowed):
    """Excel/CSV path: deterministic UBOS SITC path first, then LLM sandbox fallback."""
    try:
        dfs = load_dataframes(path)
    except Exception as e:
        print("key_indicators_agent: cannot read spreadsheet: %s" % e)
        return []

    det = _try_ubos_sitc_compute(dfs, allowed)
    if det is not None:
        updates = validate_updates(det, allowed)
        if updates:
            print("key_indicators_agent: deterministic UBOS SITC path produced %d update(s)." % len(updates))
            return updates
        print("key_indicators_agent: deterministic UBOS SITC compute yielded no valid updates.")

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
    return updates


def _extract_from_pdf(path, intent, current, allowed):
    """PDF path: extract text and ask the model to return updates as JSON directly."""
    try:
        text = load_pdf_text(path)
    except Exception as e:
        print("key_indicators_agent: cannot read PDF: %s" % e)
        return []
    if not text.strip():
        print("key_indicators_agent: PDF yielded no extractable text.")
        return []

    prompt = pdf_extract_prompt(intent, text, current)
    raw_json = extract_json(subprocess_claude(prompt))
    if not raw_json:
        print("key_indicators_agent: model returned no output for PDF extraction.")
        return []

    try:
        raw = json.loads(raw_json)
    except (json.JSONDecodeError, ValueError) as e:
        print("key_indicators_agent: PDF extraction returned invalid JSON: %s" % e)
        return []

    updates = validate_updates(raw, allowed)
    if not updates:
        print("key_indicators_agent: PDF extraction: no valid updates (result=%s)" % str(raw)[:200])
    return updates


def main(path):
    path = Path(path)
    sidecar = path.with_suffix(path.suffix + ".task.md")
    intent = sidecar.read_text("utf-8") if sidecar.exists() else "(no intent provided)"

    current = fetch_key_indicators()
    if not current:
        print("key_indicators_agent: no existing key_indicators to update - aborting (no create).")
        return []
    allowed = [c["slug"] for c in current if c.get("slug")]
    by_slug = {c["slug"]: c["id"] for c in current if c.get("slug")}

    suffix = path.suffix.lower()
    if suffix in SPREADSHEET_SUFFIXES:
        updates = _compute_from_spreadsheet(path, intent, current, allowed)
    elif suffix in PDF_SUFFIXES:
        updates = _extract_from_pdf(path, intent, current, allowed)
    else:
        print("key_indicators_agent: unsupported file type %s" % path.suffix)
        return []

    if not updates:
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
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                r.read()
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:400]
            # Raise with body in message so it surfaces in the WhatsApp failure line.
            raise RuntimeError("PB PATCH %s 400 | fields=%s | %s" % (
                rec_id, json.dumps(fields), body)) from e

    done = apply_updates(updates, by_slug.get, patch)
    print("key_indicators_agent: updated %d card(s): %s" % (len(done), ", ".join(done)))
    return done


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: key_indicators_agent.py <spreadsheet-or-pdf-path>")
    main(sys.argv[1])
