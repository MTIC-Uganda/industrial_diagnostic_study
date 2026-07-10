"""Tests for the key_indicators ingestion agent (agents/key_indicators_agent.py, ADR-020).

The agent computes derived KPI figures from a UBOS workbook by writing read-only pandas
that runs in the analytics sandbox, then applies the result additively. For PDFs it
extracts text via pypdf and asks the Claude CLI to return JSON directly.

The safety guarantee is the point: updates can only touch EXISTING slugs and only
whitelisted display fields — never create, rename, or delete a card. So the
validate_updates rejection cases matter as much as the happy path.
"""
import io
import json
import pathlib
import sys
import urllib.error

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "agents"))
import key_indicators_agent as k  # noqa: E402


# ── validate_updates: the security boundary ────────────────────────────────────
def test_validate_keeps_existing_slug_whitelisted_fields():
    raw = [{"slug": "mfg_imports", "value": "USD 7.8B", "sub_value": "40.9% of imports",
            "pct": "40.9", "year": "2025", "source": "UBOS", "bogus": "x", "id": "hack"}]
    out = k.validate_updates(raw, ["mfg_imports", "exports"])
    # pct is a PocketBase NUMBER field, so it is coerced to a float (not "40.9").
    assert out == [{"slug": "mfg_imports",
                    "fields": {"value": "USD 7.8B", "sub_value": "40.9% of imports",
                               "pct": 40.9, "year": "2025", "source": "UBOS"}}]


def test_validate_accepts_fy_fields():
    raw = [{"slug": "exports", "value": "USD 1.8B", "pct": "12.84",
            "value_fy": "USD 1.6B", "pct_fy": "14.70",
            "sub_value_fy": "14.7% of FY exports", "year_fy": "FY2024/25",
            "source_fy": "UBOS Composition of Exports",
            "import_value": "USD 7.8B", "import_sub": "40.9% of imports",
            "import_value_fy": "USD 6.3B", "import_sub_fy": "45.1% of FY imports"}]
    out = k.validate_updates(raw, ["exports"])
    assert len(out) == 1
    fields = out[0]["fields"]
    assert fields["value_fy"] == "USD 1.6B"
    assert fields["pct_fy"] == 14.7          # number field -> coerced to float
    assert fields["pct"] == 12.84            # ditto for the CY pct
    assert fields["sub_value_fy"] == "14.7% of FY exports"
    assert fields["year_fy"] == "FY2024/25"
    assert fields["source_fy"] == "UBOS Composition of Exports"
    assert fields["import_value"] == "USD 7.8B"
    assert fields["import_value_fy"] == "USD 6.3B"
    assert fields["import_sub_fy"] == "45.1% of FY imports"


def test_validate_accepts_confidence_fy():
    raw = [{"slug": "tax", "value": "UGX 5.2T", "confidence": "exact",
            "confidence_fy": "exact", "value_fy": "UGX 4.9T"}]
    out = k.validate_updates(raw, ["tax"])
    assert out[0]["fields"]["confidence_fy"] == "exact"
    assert out[0]["fields"]["value_fy"] == "UGX 4.9T"


@pytest.mark.parametrize("raw", [
    [{"slug": "not_a_card", "value": "1"}],   # unknown slug -> dropped
    [{"slug": "mfg_imports"}],                 # no updatable fields -> dropped
    ["not a dict"],                            # non-dict -> dropped
    [{"value": "1"}],                          # no slug -> dropped
    [],
])
def test_validate_drops_unsafe(raw):
    assert k.validate_updates(raw, ["mfg_imports"]) == []


def test_validate_none_becomes_empty_string():
    assert k.validate_updates([{"slug": "mfg_imports", "value": None}], ["mfg_imports"]) == \
        [{"slug": "mfg_imports", "fields": {"value": ""}}]


def test_coerce_field_numbers_and_text():
    # Number fields: parse the first numeric token out of a display string.
    assert k.coerce_field("pct", "45.1% of imports") == 45.1
    assert k.coerce_field("pct", "14.70") == 14.7
    assert k.coerce_field("pct_fy", 12) == 12.0
    assert k.coerce_field("pct", "n/a") is None      # unparseable number -> drop
    assert k.coerce_field("pct", None) is None
    # Text fields stay strings; None -> "".
    assert k.coerce_field("value", "USD 6.3B") == "USD 6.3B"
    assert k.coerce_field("source", None) == ""


def test_coerce_field_select_valid_and_invalid():
    # Valid confidence values pass through unchanged.
    assert k.coerce_field("confidence", "exact") == "exact"
    assert k.coerce_field("confidence", "estimated") == "estimated"
    assert k.coerce_field("confidence", "indicative") == "indicative"
    assert k.coerce_field("confidence_fy", "exact") == "exact"
    # Invalid values (e.g. model hallucinated "high") are dropped (None -> caller skips).
    assert k.coerce_field("confidence", "high") is None
    assert k.coerce_field("confidence", "official") is None
    assert k.coerce_field("confidence", None) is None
    assert k.coerce_field("confidence_fy", "approximate") is None


def test_validate_drops_invalid_confidence():
    # An invalid confidence value must be dropped from the PATCH fields, not sent to PocketBase.
    raw = [{"slug": "exports", "value": "USD 1.8B", "confidence": "high"}]
    out = k.validate_updates(raw, ["exports"])
    assert out[0]["fields"]["value"] == "USD 1.8B"
    assert "confidence" not in out[0]["fields"]


def test_validate_keeps_valid_confidence():
    raw = [{"slug": "exports", "value": "USD 1.8B", "confidence": "exact",
            "confidence_fy": "estimated"}]
    out = k.validate_updates(raw, ["exports"])
    assert out[0]["fields"]["confidence"] == "exact"
    assert out[0]["fields"]["confidence_fy"] == "estimated"


def test_validate_coerces_pct_and_drops_unparseable():
    # The real failure: pct arriving as a %-suffixed display string. It must become a
    # number (else PocketBase 400s the write); an unparseable pct is dropped, not sent.
    raw = [{"slug": "exports", "value": "USD 1.8B", "pct": "14.7% of exports"}]
    out = k.validate_updates(raw, ["exports"])
    assert out[0]["fields"]["pct"] == 14.7
    assert out[0]["fields"]["value"] == "USD 1.8B"

    dropped = k.validate_updates([{"slug": "exports", "value": "USD 1.8B", "pct": "n/a"}], ["exports"])
    assert "pct" not in dropped[0]["fields"] and dropped[0]["fields"]["value"] == "USD 1.8B"


# ── extract_code: fences + typographic normalization ───────────────────────────
def test_extract_code_strips_fence_and_normalizes():
    assert k.extract_code("```python\nresult = 1\n```") == "result = 1"
    assert k.extract_code("result = dfs['A']") == "result = dfs['A']"
    assert k.extract_code("NONE") == ""
    assert k.extract_code("") == ""
    dirty = "# SITC 5–8 and 6—7\nx = ‘a’ + “b” "
    clean = k.extract_code(dirty)
    assert "–" not in clean and "—" not in clean
    assert "‘" not in clean and "“" not in clean
    assert "# SITC 5-8 and 6-7" in clean


# ── extract_json ───────────────────────────────────────────────────────────────
def test_extract_json_strips_fence():
    assert k.extract_json("```json\n[]\n```") == "[]"
    assert k.extract_json('[{"slug":"tax"}]') == '[{"slug":"tax"}]'
    assert k.extract_json("") == ""


# ── preview ────────────────────────────────────────────────────────────────────
def test_preview_lists_sheets_and_shapes():
    pd = pytest.importorskip("pandas")
    dfs = {"CY_Value SITC": pd.DataFrame([[1, 2], [3, 4]]),
           "ICBT": pd.DataFrame([[5]])}
    p = k.preview(dfs)
    assert "'CY_Value SITC'" in p and "shape (2, 2)" in p
    assert "'ICBT'" in p


def test_load_dataframes_roundtrip(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    pytest.importorskip("pandas")
    wb = openpyxl.Workbook()
    wb.active.title = "CY_Value SITC"
    wb.active.append(["SITC", "2025"])
    wb.active.append(["5", 100])
    wb.create_sheet("ICBT").append(["a", 1])
    p = tmp_path / "ubos.xlsx"
    wb.save(p)
    dfs = k.load_dataframes(p)
    assert set(dfs) == {"CY_Value SITC", "ICBT"}
    assert dfs["CY_Value SITC"].shape[0] == 2


# ── code_prompt ────────────────────────────────────────────────────────────────
def test_code_prompt_has_slugs_intent_and_fy_rules():
    p = k.code_prompt("update mfg_imports", "PREVIEW HERE",
                      [{"slug": "mfg_imports", "label": "Imports", "value": "x"}])
    assert "mfg_imports: Imports" in p
    assert "update mfg_imports" in p and "PREVIEW HERE" in p
    assert "SITC" in p and "result = []" in p and "dfs" in p
    assert "value_fy" in p and "pct_fy" in p
    assert "import_value" in p and "import_sub" in p


# ── pdf_extract_prompt ─────────────────────────────────────────────────────────
def test_pdf_extract_prompt_has_required_elements():
    current = [{"slug": "tax", "label": "Tax Contribution", "value": ""}]
    p = k.pdf_extract_prompt("Extract tax figure", "TAX DOCUMENT TEXT", current)
    assert "tax: Tax Contribution" in p
    assert "Extract tax figure" in p
    assert "TAX DOCUMENT TEXT" in p
    assert "value_fy" in p
    assert "JSON array" in p
    assert "confidence" in p


def test_pdf_extract_prompt_truncates_long_text():
    long_text = "x" * 20000
    current = [{"slug": "tax", "label": "Tax", "value": ""}]
    p = k.pdf_extract_prompt("intent", long_text, current)
    assert "[truncated]" in p
    assert len(p) < 25000


# ── load_pdf_text ──────────────────────────────────────────────────────────────
def test_load_pdf_text_extracts_content(monkeypatch):
    import types
    fake_page = types.SimpleNamespace(extract_text=lambda: "Tax revenue: UGX 5.2T")
    fake_reader = types.SimpleNamespace(pages=[fake_page, fake_page])

    class FakePdf:
        PdfReader = staticmethod(lambda path: fake_reader)

    monkeypatch.setitem(sys.modules, "pypdf", FakePdf)
    text = k.load_pdf_text(pathlib.Path("dummy.pdf"))
    assert "Tax revenue: UGX 5.2T" in text


def test_load_pdf_text_skips_empty_pages(monkeypatch):
    import types

    def make_page(t):
        return types.SimpleNamespace(extract_text=lambda txt=t: txt)

    fake_reader = types.SimpleNamespace(pages=[
        make_page("page one"), make_page(""), make_page(None), make_page("page three"),
    ])

    class FakePdf:
        PdfReader = staticmethod(lambda path: fake_reader)

    monkeypatch.setitem(sys.modules, "pypdf", FakePdf)
    text = k.load_pdf_text(pathlib.Path("dummy.pdf"))
    assert "page one" in text and "page three" in text


# ── _extract_from_pdf ──────────────────────────────────────────────────────────
CURRENT = [{"slug": "tax", "label": "Tax Contribution", "value": "", "id": "rec1"}]
ALLOWED = ["tax"]


def test_extract_from_pdf_happy_path(monkeypatch, tmp_path):
    monkeypatch.setattr(k, "load_pdf_text", lambda p: "Tax revenue FY2023/24: UGX 5.2T")
    monkeypatch.setattr(k, "subprocess_claude",
                        lambda prompt: json.dumps([{
                            "slug": "tax", "value": "UGX 5.2T",
                            "pct": "19.4", "year": "FY2023/24",
                            "source": "URA Taxation Handbook FY2023/24",
                            "confidence": "exact"
                        }]))
    updates = k._extract_from_pdf(tmp_path / "ura.pdf", "Extract tax", CURRENT, ALLOWED)
    assert len(updates) == 1
    assert updates[0]["slug"] == "tax"
    assert updates[0]["fields"]["value"] == "UGX 5.2T"
    assert updates[0]["fields"]["confidence"] == "exact"


def test_extract_from_pdf_invalid_json(monkeypatch, tmp_path):
    monkeypatch.setattr(k, "load_pdf_text", lambda p: "some text")
    monkeypatch.setattr(k, "subprocess_claude", lambda prompt: "not json at all")
    updates = k._extract_from_pdf(tmp_path / "bad.pdf", "intent", CURRENT, ALLOWED)
    assert updates == []


def test_extract_from_pdf_empty_text(monkeypatch, tmp_path):
    monkeypatch.setattr(k, "load_pdf_text", lambda p: "   ")
    updates = k._extract_from_pdf(tmp_path / "empty.pdf", "intent", CURRENT, ALLOWED)
    assert updates == []


def test_extract_from_pdf_model_returns_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(k, "load_pdf_text", lambda p: "lots of text")
    monkeypatch.setattr(k, "subprocess_claude", lambda prompt: "[]")
    updates = k._extract_from_pdf(tmp_path / "nomatch.pdf", "intent", CURRENT, ALLOWED)
    assert updates == []


def test_extract_from_pdf_pypdf_failure(monkeypatch, tmp_path):
    def boom(p):
        raise RuntimeError("pypdf error")
    monkeypatch.setattr(k, "load_pdf_text", boom)
    updates = k._extract_from_pdf(tmp_path / "bad.pdf", "intent", CURRENT, ALLOWED)
    assert updates == []


def test_extract_from_pdf_strips_json_fence(monkeypatch, tmp_path):
    monkeypatch.setattr(k, "load_pdf_text", lambda p: "Tax text")
    monkeypatch.setattr(k, "subprocess_claude",
                        lambda prompt: '```json\n[{"slug":"tax","value":"UGX 5.2T"}]\n```')
    updates = k._extract_from_pdf(tmp_path / "ura.pdf", "intent", CURRENT, ALLOWED)
    assert updates[0]["fields"]["value"] == "UGX 5.2T"


# ── _compute_from_spreadsheet ──────────────────────────────────────────────────
def test_compute_from_spreadsheet_bad_file(tmp_path):
    bad = tmp_path / "notexcel.xlsx"
    bad.write_bytes(b"not an excel file")
    updates = k._compute_from_spreadsheet(bad, "intent", CURRENT, ALLOWED)
    assert updates == []


# ── main: file type dispatch ───────────────────────────────────────────────────
def test_main_dispatches_pdf_to_extract_path(monkeypatch, tmp_path):
    pdf = tmp_path / "ura.pdf"
    pdf.write_bytes(b"%PDF dummy")
    calls = []
    monkeypatch.setattr(k, "fetch_key_indicators",
                        lambda: [{"slug": "tax", "label": "Tax", "value": "", "id": "r1"}])
    monkeypatch.setattr(k, "_extract_from_pdf",
                        lambda path, intent, current, allowed: calls.append("pdf") or
                        [{"slug": "tax", "fields": {"value": "UGX 5.2T"}}])
    monkeypatch.setattr(k, "pb_auth", lambda: "tok")
    monkeypatch.setattr(k, "apply_updates", lambda updates, id_fn, patch: ["tax"])
    k.main(str(pdf))
    assert "pdf" in calls


def test_main_dispatches_xlsx_to_spreadsheet_path(monkeypatch, tmp_path):
    xlsx = tmp_path / "ubos.xlsx"
    xlsx.write_bytes(b"fake")
    calls = []
    monkeypatch.setattr(k, "fetch_key_indicators",
                        lambda: [{"slug": "exports", "label": "Exports", "value": "", "id": "r2"}])
    monkeypatch.setattr(k, "_compute_from_spreadsheet",
                        lambda path, intent, current, allowed: calls.append("xlsx") or
                        [{"slug": "exports", "fields": {"value": "USD 1.8B"}}])
    monkeypatch.setattr(k, "pb_auth", lambda: "tok")
    monkeypatch.setattr(k, "apply_updates", lambda updates, id_fn, patch: ["exports"])
    k.main(str(xlsx))
    assert "xlsx" in calls


def test_main_unsupported_type(monkeypatch, tmp_path):
    doc = tmp_path / "file.docx"
    doc.write_bytes(b"dummy")
    monkeypatch.setattr(k, "fetch_key_indicators",
                        lambda: [{"slug": "tax", "label": "Tax", "value": "", "id": "r1"}])
    result = k.main(str(doc))
    assert result == []


def test_main_no_key_indicators(monkeypatch, tmp_path):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF")
    monkeypatch.setattr(k, "fetch_key_indicators", lambda: [])
    result = k.main(str(pdf))
    assert result == []


def test_main_no_pb_token(monkeypatch, tmp_path):
    pdf = tmp_path / "ura.pdf"
    pdf.write_bytes(b"%PDF dummy")
    monkeypatch.setattr(k, "fetch_key_indicators",
                        lambda: [{"slug": "tax", "label": "Tax", "value": "", "id": "r1"}])
    monkeypatch.setattr(k, "_extract_from_pdf",
                        lambda *a, **kw: [{"slug": "tax", "fields": {"value": "UGX 5.2T"}}])
    monkeypatch.setattr(k, "pb_auth", lambda: None)
    result = k.main(str(pdf))
    assert result == []


# ── apply_updates ──────────────────────────────────────────────────────────────
def test_apply_updates_uses_injected_io():
    patched = []
    ids = {"mfg_imports": "rec1"}
    updates = [{"slug": "mfg_imports", "fields": {"value": "USD 7.8B"}},
               {"slug": "missing", "fields": {"value": "9"}}]
    done = k.apply_updates(updates, ids.get, lambda rid, f: patched.append((rid, f)))
    assert done == ["mfg_imports"]
    assert patched == [("rec1", {"value": "USD 7.8B"})]


# ── patch 400 → RuntimeError with PocketBase body ─────────────────────────────
def test_main_patch_400_raises_runtime_error_with_body(monkeypatch, tmp_path):
    """When PocketBase returns 400, the RuntimeError message includes the response body
    so the failure reason surfaces in the WhatsApp notification."""
    xlsx = tmp_path / "ubos.xlsx"
    xlsx.write_bytes(b"fake")
    monkeypatch.setattr(k, "fetch_key_indicators",
                        lambda: [{"slug": "exports", "label": "Exports", "value": "", "id": "rec9"}])
    monkeypatch.setattr(k, "_compute_from_spreadsheet",
                        lambda *a, **kw: [{"slug": "exports", "fields": {"pct": 14.7}}])
    monkeypatch.setattr(k, "pb_auth", lambda: "tok")

    err_body = b'{"code":400,"message":"Failed to create record.","data":{"pct":{"code":"validation_not_number"}}}'
    http_err = urllib.error.HTTPError(
        "http://x", 400, "Bad Request",
        {}, io.BytesIO(err_body))

    monkeypatch.setattr(k.urllib.request, "urlopen", lambda req, timeout=15: (_ for _ in ()).throw(http_err))

    with pytest.raises(RuntimeError, match="validation_not_number"):
        k.main(str(xlsx))


def test_main_patch_success_reads_response(monkeypatch, tmp_path):
    """Successful PATCH: urlopen returns a 200 response and r.read() is called (covers the
    success branch inside the try block added to surface PB error bodies)."""
    xlsx = tmp_path / "ubos.xlsx"
    xlsx.write_bytes(b"fake")
    monkeypatch.setattr(k, "fetch_key_indicators",
                        lambda: [{"slug": "exports", "label": "Exports", "value": "", "id": "rec9"}])
    monkeypatch.setattr(k, "_compute_from_spreadsheet",
                        lambda *a, **kw: [{"slug": "exports", "fields": {"pct": 14.7}}])
    monkeypatch.setattr(k, "pb_auth", lambda: "tok")

    class _FakeResp:
        def __enter__(self): return self
        def __exit__(self, *a): pass
        def read(self): return b'{"id":"rec9"}'

    monkeypatch.setattr(k.urllib.request, "urlopen", lambda req, timeout=15: _FakeResp())

    result = k.main(str(xlsx))
    assert result == ["exports"]
