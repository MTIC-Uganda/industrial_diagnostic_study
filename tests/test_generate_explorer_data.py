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


def test_build_trade_trend_groups_and_sorts():
    rows = [
        {"hs4_code": "7208", "year": "2021", "imports_uganda": "180000", "unit_value_usd_t": "620"},
        {"hs4_code": "7208", "year": "2019", "imports_uganda": "155000", "unit_value_usd_t": ""},
        {"hs4_code": "7208", "year": "2024", "imports_uganda": "219496", "unit_value_usd_t": "580"},
        {"hs4_code": "3907", "year": "2024", "imports_uganda": "153242", "unit_value_usd_t": None},
    ]
    out = g.build_trade_trend(rows)
    assert set(out.keys()) == {"7208", "3907"}
    yrs = [r["year"] for r in out["7208"]]
    assert yrs == [2019, 2021, 2024], "must be sorted by year"
    assert out["7208"][0]["unit_value_usd_t"] is None, "empty string → None"
    assert out["7208"][1]["unit_value_usd_t"] == 620.0
    assert out["3907"][0]["imports_uganda"] == 153242.0


def test_build_trade_trend_empty():
    assert g.build_trade_trend([]) == {}
    assert g.build_trade_trend(None) == {}


def test_build_trade_partners_groups_and_sorts():
    rows = [
        {"hs4_code": "7208", "rank": "2", "partner_name": "India", "partner_code": "356", "imports_value_usd_k": "35000"},
        {"hs4_code": "7208", "rank": "1", "partner_name": "China", "partner_code": "156", "imports_value_usd_k": "150000"},
        {"hs4_code": "3907", "rank": "1", "partner_name": "Germany", "partner_code": "276", "imports_value_usd_k": "80000"},
    ]
    out = g.build_trade_partners(rows)
    assert set(out.keys()) == {"7208", "3907"}
    assert out["7208"][0]["name"] == "China", "rank 1 must come first"
    assert out["7208"][1]["name"] == "India"
    assert out["7208"][0]["value"] == 150000.0
    assert out["3907"][0]["code"] == 276


def test_build_trade_partners_empty():
    assert g.build_trade_partners([]) == {}
    assert g.build_trade_partners(None) == {}


def test_build_priority_scores_basic():
    trade = {
        "7208": {"imports": {"uganda": 219496.0, "eac": 500000.0, "global": None},
                 "exports": {"uganda": 1000.0, "eac": 2000.0, "global": None}, "desc": "d", "year": 2024},
    }
    trend = {"7208": [
        {"year": 2019, "imports_uganda": 155000.0, "unit_value_usd_t": None},
        {"year": 2024, "imports_uganda": 219496.0, "unit_value_usd_t": None},
    ]}
    partners = {"7208": [
        {"rank": 1, "name": "China", "code": 156, "value": 180000.0},
        {"rank": 2, "name": "India", "code": 356, "value": 35000.0},
    ]}
    out = g.build_priority_scores(trade, trend, partners)
    assert "7208" in out
    s = out["7208"]
    assert 0 <= s["score"] <= 100
    assert s["components"]["import"] > 0
    assert s["components"]["gap"] > 0   # minimal exports → large gap
    assert s["components"]["conc"] > 0  # China dominates
    # Total should equal sum of components (within rounding)
    assert abs(s["score"] - sum(s["components"].values())) <= 2


def test_build_priority_scores_skips_tiny_imports():
    trade = {"9999": {"imports": {"uganda": 100.0, "eac": 200.0, "global": None},
                      "exports": {"uganda": 0.0, "eac": 0.0, "global": None}, "desc": "", "year": 2024}}
    out = g.build_priority_scores(trade, {}, {})
    assert "9999" not in out   # < $500k threshold


def test_build_priority_scores_empty():
    assert g.build_priority_scores({}, {}, {}) == {}
    assert g.build_priority_scores(None, None, None) == {}


def test_build_priority_scores_no_trend_or_partners():
    trade = {"7208": {"imports": {"uganda": 50000.0, "eac": 100000.0, "global": None},
                      "exports": {"uganda": 500.0, "eac": 1000.0, "global": None}, "desc": "", "year": 2024}}
    out = g.build_priority_scores(trade, {}, {})
    assert "7208" in out
    assert out["7208"]["components"]["cagr"] == 0   # no trend → 0
    assert out["7208"]["components"]["conc"] == 0   # no partners → 0


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
    "trade_trend": [{"hs4_code": "0901", "year": "2024", "imports_uganda": "1", "unit_value_usd_t": "500"}],
    "trade_partners": [{"hs4_code": "0901", "rank": "1", "partner_name": "Kenya", "partner_code": "404", "imports_value_usd_k": "600"}],
}


def test_build_all_shapes():
    d = g.build_all(SAMPLE_RAW)
    assert set(d) >= {"PRODUCTS", "CATEGORIES", "TRADE_HS4", "PRODUCT_HS4",
                      "RAW_MATERIAL_TRADE", "RAW_MATERIAL_PHASE", "PHASE_PRODUCERS",
                      "PHASE_SOURCE", "PRODUCT_FIRMS", "INPUT_KEYWORD_HS4", "INPUT_KEYWORD_PHASE",
                      "TRADE_TREND", "TRADE_PARTNERS", "OPPORTUNITY_SCORES"}
    assert d["PRODUCT_HS4"] == {"coffee": "0901"}
    assert d["PHASE_SOURCE"] == "S"
    assert d["TRADE_TREND"]["0901"][0]["imports_uganda"] == 1.0
    assert d["TRADE_PARTNERS"]["0901"][0]["name"] == "Kenya"
    # 0901 imports=1 USD thousands < 500 threshold → not scored
    assert "0901" not in d["OPPORTUNITY_SCORES"]


def test_build_all_handles_missing_trend_and_partners():
    raw_no_new = {k: v for k, v in SAMPLE_RAW.items() if k not in ("trade_trend", "trade_partners")}
    d = g.build_all(raw_no_new)
    assert d["TRADE_TREND"] == {}
    assert d["TRADE_PARTNERS"] == {}


def test_render_js_is_valid_module_text():
    js = g.render_js(g.build_all(SAMPLE_RAW))
    assert js.startswith("// GENERATED FILE")
    assert "const PRODUCTS =" in js and "export {" in js
    assert "matchInputTrade" in js
    assert "const TRADE_TREND =" in js
    assert "const TRADE_PARTNERS =" in js
    assert "matchInputHs4" in js
    assert "const OPPORTUNITY_SCORES =" in js
    assert "OPPORTUNITY_SCORES" in js.split("export {")[1]


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
