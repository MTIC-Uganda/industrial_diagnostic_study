"""Unit tests for scripts/generate_explorer_data.py (ADR-018).

First real monolith conversion: the script is now importable (no top-level side
effects), so its logic is covered line-by-line instead of via subprocess.
"""
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import generate_explorer_data as g  # noqa: E402


# ── _maybe_json ───────────────────────────────────────────────────────────────
def test_maybe_json_passthrough_non_string():
    assert g._maybe_json({"a": 1}) == {"a": 1}
    assert g._maybe_json(["x"]) == ["x"]


def test_maybe_json_parses_string():
    assert g._maybe_json('["a","b"]') == ["a", "b"]


def test_maybe_json_empty_string_returns_default():
    assert g._maybe_json("", default=[]) == []
    assert g._maybe_json("", default=None) is None


# ── pure builders ─────────────────────────────────────────────────────────────
def test_build_products():
    rows = [{"slug": "coffee", "name": "Coffee", "category": "Cash crop",
             "color": "#6f4e37", "description": "beans", "chains": '["agro"]'}]
    out = g.build_products(rows)
    assert out["coffee"]["id"] == "coffee"
    assert out["coffee"]["chains"] == ["agro"]


def test_build_categories():
    rows = [{"name": "Metals", "color": "#999", "products": '["steel"]'}]
    assert g.build_categories(rows) == [{"name": "Metals", "color": "#999", "products": ["steel"]}]


def test_build_trade_hs4_and_trade_block():
    rows = [{"hs4_code": "0901", "desc": "Coffee", "year": "2024",
             "imports_uganda": "1.5", "imports_eac": "2", "exports_uganda": "10", "exports_eac": "3"}]
    out = g.build_trade_hs4(rows)
    assert out["0901"]["year"] == 2024
    assert out["0901"]["exports"]["uganda"] == 10.0
    assert out["0901"]["imports"]["eac"] == 2.0


def test_build_product_hs4_skips_missing_code():
    rows = [{"slug": "coffee", "hs4_code": "0901"}, {"slug": "tea"}]
    assert g.build_product_hs4(rows) == {"coffee": "0901"}


def test_build_raw_material_splits_trade_and_phase():
    rows = [{"item_name": "Scrap", "desc": "iron scrap", "year": "2023",
             "imports_uganda": "1", "imports_eac": "1", "exports_uganda": "1", "exports_eac": "1",
             "phase": "Phase 1"}]
    trade, phase = g.build_raw_material(rows)
    assert trade["Scrap"]["year"] == 2023
    assert phase == {"Scrap": "Phase 1"}


def test_build_phase_producers():
    rows = [{"phase": "Phase 1", "count": "5", "label": "Smelting",
             "examples": '["A","B"]', "source": "UBOS 2024"}]
    producers, source = g.build_phase_producers(rows)
    assert producers["Phase 1"]["count"] == 5
    assert producers["Phase 1"]["examples"] == ["A", "B"]
    assert source == "UBOS 2024"


def test_build_product_firms_with_and_without_phase_context():
    rows = [
        {"product_slug": "coffee", "status": "active", "firms": '["Firm A"]', "note": "n",
         "phase_context": '{"x":1}'},
        {"product_slug": "tea", "status": "none", "firms": "", "note": ""},
    ]
    out = g.build_product_firms(rows)
    assert out["coffee"]["firms"] == ["Firm A"]
    assert out["coffee"]["phaseContext"] == {"x": 1}
    assert out["tea"]["firms"] == [] and "phaseContext" not in out["tea"]


def test_build_input_keywords_splits_by_target_type():
    rows = [
        {"pattern_source": "coffee", "pattern_flags": "i", "target_value": "0901", "target_type": "hs4"},
        {"pattern_source": "smelt", "pattern_flags": "", "target_value": "Phase 1", "target_type": "phase"},
    ]
    hs4, phase = g.build_input_keywords(rows)
    assert hs4[0]["value"] == "0901" and phase[0]["value"] == "Phase 1"


# ── build_all + render_js ─────────────────────────────────────────────────────
SAMPLE_RAW = {
    "products": [{"slug": "coffee", "name": "Coffee", "category": "Cash", "color": "#6f4e37",
                  "description": "d", "chains": ["agro"], "hs4_code": "0901"}],
    "categories": [{"name": "Cash", "color": "#6f4e37", "products": ["coffee"]}],
    "trade_hs4": [{"hs4_code": "0901", "desc": "Coffee", "year": "2024",
                   "imports_uganda": "1", "imports_eac": "1", "exports_uganda": "9", "exports_eac": "2"}],
    "raw_material": [{"item_name": "Scrap", "desc": "d", "year": "2024", "imports_uganda": "1",
                      "imports_eac": "1", "exports_uganda": "1", "exports_eac": "1", "phase": "P1"}],
    "phase_producers": [{"phase": "P1", "count": "3", "label": "L", "examples": ["A"], "source": "S"}],
    "product_firms": [{"product_slug": "coffee", "status": "active", "firms": ["F"], "note": ""}],
    "input_keywords": [{"pattern_source": "coffee", "pattern_flags": "i", "target_value": "0901", "target_type": "hs4"}],
}


def test_build_all_shapes():
    d = g.build_all(SAMPLE_RAW)
    assert set(d) >= {"PRODUCTS", "CATEGORIES", "TRADE_HS4", "PRODUCT_HS4",
                      "RAW_MATERIAL_TRADE", "RAW_MATERIAL_PHASE", "PHASE_PRODUCERS",
                      "PHASE_SOURCE", "PRODUCT_FIRMS", "INPUT_KEYWORD_HS4", "INPUT_KEYWORD_PHASE"}
    assert d["PRODUCT_HS4"] == {"coffee": "0901"}
    assert d["PHASE_SOURCE"] == "S"


def test_render_js_is_valid_module_text():
    js = g.render_js(g.build_all(SAMPLE_RAW))
    assert js.startswith("// GENERATED FILE")
    assert "const PRODUCTS =" in js and "export {" in js
    assert "matchInputTrade" in js


def test_js_obj_and_regex_array():
    assert g.js_obj({"a": 1}).strip().startswith("{")
    arr = g.js_regex_array([{"source": "coffee", "flags": "i", "value": "0901"}], "hs4")
    assert "pattern: /coffee/i" in arr and 'hs4: "0901"' in arr


# ── single-source guards ──────────────────────────────────────────────────────
def test_load_csv_and_load_json_hard_fail():
    for fn in (g.load_csv, g.load_json):
        with pytest.raises(SystemExit):
            fn("x.csv")


# ── pb_get (mocked network) ───────────────────────────────────────────────────
class _Resp:
    def __init__(self, payload):
        self._b = json.dumps(payload).encode()
    def read(self):
        return self._b
    def __enter__(self):
        return self
    def __exit__(self, *a):
        return False


def test_pb_get_paginates(monkeypatch):
    pages = {
        1: {"items": [{"id": 1}], "totalPages": 2},
        2: {"items": [{"id": 2}], "totalPages": 2},
    }
    calls = {"n": 0}
    def fake_urlopen(url):
        calls["n"] += 1
        return _Resp(pages[calls["n"]])
    monkeypatch.setattr(g.urllib.request, "urlopen", fake_urlopen)
    rows = g.pb_get("http://pb", "explorer_products", sort="display_order")
    assert [r["id"] for r in rows] == [1, 2]


def test_pb_get_returns_none_on_error(monkeypatch):
    def boom(url):
        raise OSError("refused")
    monkeypatch.setattr(g.urllib.request, "urlopen", boom)
    assert g.pb_get("http://pb", "explorer_products") is None


def test_fetch_all_uses_pb_get(monkeypatch):
    monkeypatch.setattr(g, "pb_get", lambda url, coll, sort=None: [{"c": coll}])
    out = g.fetch_all("http://pb")
    assert set(out) == set(g.COLLECTIONS)
    assert out["products"] == [{"c": "explorer_products"}]


# ── main ──────────────────────────────────────────────────────────────────────
def test_main_writes_output(tmp_path):
    out = tmp_path / "ironSteel.js"
    js = g.main(pb_url="http://pb", out=out, fetcher=lambda u: SAMPLE_RAW)
    assert out.exists() and "const PRODUCTS =" in out.read_text()
    assert "coffee" in js


def test_main_requires_pb_url():
    with pytest.raises(SystemExit):
        g.main(pb_url="", out=None, fetcher=lambda u: SAMPLE_RAW)


def test_main_exits_when_no_products(tmp_path):
    empty = {k: [] for k in g.COLLECTIONS}
    with pytest.raises(SystemExit):
        g.main(pb_url="http://pb", out=tmp_path / "x.js", fetcher=lambda u: empty)
