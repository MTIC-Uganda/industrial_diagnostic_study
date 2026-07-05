"""Tests for the key_indicators ingestion agent (agents/key_indicators_agent.py, ADR-020).

The agent computes derived KPI figures from a UBOS workbook by writing read-only pandas
that runs in the analytics sandbox, then applies the result additively. The safety
guarantee is the point: updates can only touch EXISTING slugs and only whitelisted
display fields — never create, rename, or delete a card. So the validate_updates
rejection cases matter as much as the happy path.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "agents"))
import key_indicators_agent as k  # noqa: E402


# ── validate_updates: the security boundary ────────────────────────────────────
def test_validate_keeps_existing_slug_whitelisted_fields():
    raw = [{"slug": "mfg_imports", "value": "USD 7.8B", "sub_value": "40.9% of imports",
            "pct": "40.9", "year": "2025", "source": "UBOS", "bogus": "x", "id": "hack"}]
    out = k.validate_updates(raw, ["mfg_imports", "exports"])
    assert out == [{"slug": "mfg_imports",
                    "fields": {"value": "USD 7.8B", "sub_value": "40.9% of imports",
                               "pct": "40.9", "year": "2025", "source": "UBOS"}}]


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


# ── extract_code: fences + typographic normalization ───────────────────────────
def test_extract_code_strips_fence_and_normalizes():
    assert k.extract_code("```python\nresult = 1\n```") == "result = 1"
    assert k.extract_code("result = dfs['A']") == "result = dfs['A']"
    assert k.extract_code("NONE") == ""
    assert k.extract_code("") == ""
    # en-dash / em-dash / smart quotes / nbsp normalized so ast.parse won't choke
    dirty = "# SITC 5–8 and 6—7\nx = ‘a’ + “b” "
    clean = k.extract_code(dirty)
    assert "–" not in clean and "—" not in clean
    assert "‘" not in clean and "“" not in clean and " " not in clean
    assert "# SITC 5-8 and 6-7" in clean


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


def test_code_prompt_has_slugs_intent_and_rules():
    p = k.code_prompt("update mfg_imports", "PREVIEW HERE",
                      [{"slug": "mfg_imports", "label": "Imports", "value": "x"}])
    assert "mfg_imports: Imports" in p
    assert "update mfg_imports" in p and "PREVIEW HERE" in p
    assert "SITC" in p and "result = []" in p and "dfs" in p


# ── apply_updates ──────────────────────────────────────────────────────────────
def test_apply_updates_uses_injected_io():
    patched = []
    ids = {"mfg_imports": "rec1"}
    updates = [{"slug": "mfg_imports", "fields": {"value": "USD 7.8B"}},
               {"slug": "missing", "fields": {"value": "9"}}]
    done = k.apply_updates(updates, ids.get, lambda rid, f: patched.append((rid, f)))
    assert done == ["mfg_imports"]
    assert patched == [("rec1", {"value": "USD 7.8B"})]


def test_subprocess_claude(monkeypatch):
    import types
    monkeypatch.setattr(k.subprocess, "run",
                        lambda *a, **kw: types.SimpleNamespace(returncode=0, stdout="  code  "))
    assert k.subprocess_claude("p") == "code"
    monkeypatch.setattr(k.subprocess, "run",
                        lambda *a, **kw: types.SimpleNamespace(returncode=1, stdout="x"))
    assert k.subprocess_claude("p") == ""

    def boom(*a, **kw):
        raise RuntimeError("no cli")
    monkeypatch.setattr(k.subprocess, "run", boom)
    assert k.subprocess_claude("p") == ""


# ── main(): compute flow with the sandbox seam mocked ──────────────────────────
def _wire(monkeypatch, current, run_results, code="result=[]"):
    monkeypatch.setattr(k, "load_dataframes", lambda p: {"CY_Value SITC": object()})
    monkeypatch.setattr(k, "fetch_key_indicators", lambda: current)
    monkeypatch.setattr(k, "preview", lambda dfs: "PREVIEW")
    monkeypatch.setattr(k, "subprocess_claude", lambda prompt: code)
    seq = list(run_results)
    monkeypatch.setattr(k.analytics_sandbox, "run_analysis",
                        lambda code, dfs, timeout=25: seq.pop(0) if seq else {"ok": False, "error": "x"})
    monkeypatch.setattr(k, "pb_auth", lambda: "tok")


def test_main_happy_path_patches(monkeypatch, tmp_path):
    _wire(monkeypatch, [{"slug": "mfg_imports", "id": "r9"}],
          [{"ok": True, "result": [{"slug": "mfg_imports", "value": "USD 7.8B",
                                    "sub_value": "40.9% of imports"}]}])
    calls = []

    class FakeResp:
        def read(self): return b"{}"
        def __enter__(self): return self
        def __exit__(self, *a): return False

    monkeypatch.setattr(k.urllib.request, "urlopen",
                        lambda req, timeout=0: (calls.append((req.method, req.full_url)), FakeResp())[1])
    done = k.main(tmp_path / "x.xlsx")
    assert done == ["mfg_imports"]
    assert any(m == "PATCH" and "mfg_imports" not in u and "r9" in u for m, u in calls)


def test_main_retries_then_succeeds(monkeypatch, tmp_path):
    # first run errors (bad code), second returns a valid update
    _wire(monkeypatch, [{"slug": "mfg_imports", "id": "r9"}],
          [{"ok": False, "error": "syntax error"},
           {"ok": True, "result": [{"slug": "mfg_imports", "value": "USD 7.8B"}]}])
    monkeypatch.setattr(k.urllib.request, "urlopen",
                        lambda req, timeout=0: type("R", (), {"read": lambda s: b"{}",
                        "__enter__": lambda s: s, "__exit__": lambda s, *a: False})())
    assert k.main(tmp_path / "x.xlsx") == ["mfg_imports"]


def test_main_no_valid_after_retries(monkeypatch, tmp_path):
    _wire(monkeypatch, [{"slug": "mfg_imports", "id": "r9"}],
          [{"ok": True, "result": []}, {"ok": True, "result": []}, {"ok": True, "result": []}])
    assert k.main(tmp_path / "x.xlsx") == []


def test_main_no_existing_indicators(monkeypatch, tmp_path):
    _wire(monkeypatch, [], [{"ok": True, "result": []}])
    assert k.main(tmp_path / "x.xlsx") == []


def test_main_no_code_produced(monkeypatch, tmp_path):
    # subprocess_claude returns nothing on every attempt -> "no code produced" branch
    _wire(monkeypatch, [{"slug": "mfg_imports", "id": "r9"}], [], code="")
    assert k.main(tmp_path / "x.xlsx") == []


def test_main_bad_spreadsheet(monkeypatch, tmp_path):
    monkeypatch.setattr(k, "load_dataframes", lambda p: (_ for _ in ()).throw(ValueError("boom")))
    assert k.main(tmp_path / "x.xlsx") == []


def test_main_no_token(monkeypatch, tmp_path):
    _wire(monkeypatch, [{"slug": "mfg_imports", "id": "r9"}],
          [{"ok": True, "result": [{"slug": "mfg_imports", "value": "USD 7.8B"}]}])
    monkeypatch.setattr(k, "pb_auth", lambda: None)
    assert k.main(tmp_path / "x.xlsx") == []
