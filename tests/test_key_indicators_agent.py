"""Tests for the key_indicators ingestion agent (agents/key_indicators_agent.py, ADR-018).

The safety guarantee is the point: updates can only touch EXISTING slugs and only the
whitelisted value/label fields — never create, rename, or delete a card. So the
rejection cases in validate_updates matter as much as the happy path.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "agents"))
import key_indicators_agent as k  # noqa: E402


# ── validate_updates: the security boundary ────────────────────────────────────
def test_validate_keeps_existing_slug_whitelisted_fields():
    raw = [{"slug": "exports", "value": "USD 85M", "pct": "12", "year": "2024",
            "source": "UBOS", "bogus": "drop me", "id": "hack"}]
    out = k.validate_updates(raw, ["exports", "imports"])
    assert out == [{"slug": "exports",
                    "fields": {"value": "USD 85M", "pct": "12", "year": "2024", "source": "UBOS"}}]


@pytest.mark.parametrize("raw", [
    [{"slug": "not_a_card", "value": "1"}],     # unknown slug -> dropped
    [{"slug": "exports"}],                       # no updatable fields -> dropped
    ["not a dict"],                              # non-dict -> dropped
    [{"value": "1"}],                            # no slug -> dropped
    [],
])
def test_validate_drops_unsafe(raw):
    assert k.validate_updates(raw, ["exports"]) == []


def test_validate_none_becomes_empty_string():
    out = k.validate_updates([{"slug": "exports", "value": None}], ["exports"])
    assert out == [{"slug": "exports", "fields": {"value": ""}}]


# ── parse_plan ─────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("text,expected", [
    ('[{"slug":"a","value":"1"}]', [{"slug": "a", "value": "1"}]),
    ("noise before [{\"slug\":\"a\"}] noise after", [{"slug": "a"}]),
    ("no json here", []),
    ("[not valid json", []),
    ('{"slug":"a"}', []),        # object, not array
    ("", []),
])
def test_parse_plan(text, expected):
    assert k.parse_plan(text) == expected


# ── plan_prompt ────────────────────────────────────────────────────────────────
def test_plan_prompt_lists_slugs_and_rules():
    p = k.plan_prompt("update imports", "sheet data here",
                      [{"slug": "imports", "label": "Imports", "value": "x"}])
    assert "imports: Imports" in p
    assert "update imports" in p and "sheet data here" in p
    assert "never the exports" in p            # the anti-mixup instruction


# ── apply_updates ──────────────────────────────────────────────────────────────
def test_apply_updates_uses_injected_io():
    patched = []
    ids = {"exports": "rec1", "imports": "rec2"}
    updates = [{"slug": "exports", "fields": {"value": "1"}},
               {"slug": "missing", "fields": {"value": "9"}}]
    done = k.apply_updates(updates, ids.get, lambda rid, f: patched.append((rid, f)))
    assert done == ["exports"]                 # 'missing' has no id -> skipped
    assert patched == [("rec1", {"value": "1"})]


# ── read_sheet (real openpyxl round-trip) ──────────────────────────────────────
def test_read_sheet_roundtrip(tmp_path):
    openpyxl = pytest.importorskip("openpyxl")
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Imports"
    ws.append(["Manufactured imports", "USD 6.3B", "45.1%"])
    ws.append([None, None, None])
    p = tmp_path / "ubos.xlsx"
    wb.save(p)
    text = k.read_sheet(p)
    assert "# sheet: Imports" in text
    assert "Manufactured imports | USD 6.3B | 45.1%" in text


# ── main(): early-return branches + happy path (seams monkeypatched) ───────────
def _wire(monkeypatch, current, plan_out, token):
    monkeypatch.setattr(k, "read_sheet", lambda p: "SHEET")
    monkeypatch.setattr(k, "fetch_key_indicators", lambda: current)
    monkeypatch.setattr(k, "subprocess_claude", lambda prompt: plan_out)
    monkeypatch.setattr(k, "pb_auth", lambda: token)


def test_main_no_existing_indicators(monkeypatch, tmp_path):
    _wire(monkeypatch, [], "[]", "tok")
    assert k.main(tmp_path / "x.xlsx") == []


def test_main_bad_sheet_returns_empty(monkeypatch, tmp_path):
    monkeypatch.setattr(k, "read_sheet", lambda p: (_ for _ in ()).throw(ValueError("boom")))
    assert k.main(tmp_path / "x.xlsx") == []


def test_main_no_valid_updates(monkeypatch, tmp_path):
    _wire(monkeypatch, [{"slug": "exports", "id": "r1"}], '[{"slug":"nope","value":"1"}]', "tok")
    assert k.main(tmp_path / "x.xlsx") == []


def test_main_no_token(monkeypatch, tmp_path):
    _wire(monkeypatch, [{"slug": "exports", "id": "r1"}], '[{"slug":"exports","value":"9"}]', None)
    assert k.main(tmp_path / "x.xlsx") == []


def test_main_happy_path_patches(monkeypatch, tmp_path):
    _wire(monkeypatch, [{"slug": "imports", "id": "r9"}], '[{"slug":"imports","value":"USD 6.3B"}]', "tok")
    calls = []

    class FakeResp:
        def read(self): return b"{}"
        def __enter__(self): return self
        def __exit__(self, *a): return False

    def fake_urlopen(req, timeout=0):
        calls.append((req.method, req.full_url, req.data))
        return FakeResp()

    monkeypatch.setattr(k.urllib.request, "urlopen", fake_urlopen)
    # write a real sidecar so the intent branch is exercised too
    (tmp_path / "x.xlsx.task.md").write_text("update the manufactured imports card", "utf-8")
    done = k.main(tmp_path / "x.xlsx")
    assert done == ["imports"]
    assert any(m == "PATCH" and "key_indicators/records/r9" in u for m, u, _ in calls)
