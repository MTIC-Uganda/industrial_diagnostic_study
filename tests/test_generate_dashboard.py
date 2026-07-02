"""Tests for the generate_dashboard.py refactor (ADR-018).

The refactor moved all side effects (PocketBase fetch, file write) out of import time
and into load_data()/main(), leaving the *_html/*_js generators pure. These tests drive
the pipeline by monkeypatching the network seam (pb_get / pb_count / the treemap fetch)
with fixtures, so no live PocketBase is needed. Behaviour preservation itself is verified
separately by a byte-identical diff of the rendered HTML against live prod data.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import generate_dashboard as g  # noqa: E402


# ── fixtures: minimal but sufficient rows for every collection load_data reads ──
def _fixtures():
    return {
        "value_chains": [
            {"name": "Iron & Steel", "slug": "iron-steel", "color": "#111",
             "key_import_2024": "USD 200m", "key_export_2024": "USD 50m",
             "position_tag": "Net importer", "position_color": "red",
             "target_2040": "Self-sufficient", "priority_tag": "Priority 1",
             "priority_color": "blue", "map_title": "Iron & Steel",
             "map_phases": [], "status_current": []},
            {"name": "Textiles & Garments", "slug": "textiles", "color": "#222"},
        ],
        "industries": [
            {"name": "Steel Co", "chain_name": "Iron & Steel", "latitude": 0.3,
             "longitude": 32.5, "district": "Wakiso", "products": "rebar"},
            {"name": "Fabric Co", "chain_name": "Textiles & Garments", "latitude": 0.1,
             "longitude": 32.6, "district": "Kampala"},
        ],
        "facilities": [{"name": "Fallback Fac", "chain_name": "Iron & Steel", "lat": 0.2}],
        "macro_trend": [
            {"slug": "industry_growth", "label": "Industry Growth",
             "fy2021_value": "3.0%", "fy2025_value": "6.4%", "confidence": "exact",
             "source": "UBOS"},
            {"slug": "mfg_value_added", "label": "MVA", "trajectory": "1.0;2.0;3.0",
             "trajectory_labels": "FY21;FY23;FY25", "delta": "+50%"},
            {"slug": "mfg_exports", "label": "Exports", "fy2021_value": "USD 1bn",
             "fy2025_value": "USD 2bn", "delta": "+100%"},
            {"slug": "industrial_electricity", "label": "Electricity",
             "fy2025_value": "65%", "fy2021_value": "60%", "source": "ERA"},
        ],
        "key_indicators": [
            {"slug": s, "label": s.title(), "kind": "pie", "value": "10", "pct": "40",
             "sub_value": "sub", "icon": "★", "color": "#1565c0", "rest_color": "#eee",
             "year": "2025", "source": "UBOS", "source_detail": "UBOS GDP",
             "confidence": "exact"}
            for s in ["value_added", "growth", "tax", "exports", "hightech", "credit",
                      "establishments", "region_dist", "parks", "fdi", "employment",
                      "variety"]
        ],
        "key_indicator_categories": [
            {"indicator_slug": "tax", "category": "Manufacturing", "pct": 20,
             "value_label": "Shs 5trn", "highlight": "1"},
            {"indicator_slug": "tax", "category": "Wholesale", "pct": 30,
             "value_label": "Shs 7trn", "highlight": "0"},
            {"indicator_slug": "hightech", "category": "Pharma", "pct": 50,
             "value_label": "USD 40m", "highlight": "0"},
            {"indicator_slug": "credit", "category": "Manufacturing", "pct": 12,
             "value_label": "Shs 3trn", "highlight": "1"},
            {"indicator_slug": "region_dist", "category": "Central", "pct": 78,
             "value_label": "", "highlight": "0"},
        ],
        "kpi_indicators": [
            {"slug": s, "label": s.replace("_", " ").title(), "current_value": "USD 5B",
             "current_pct": 15, "ndp_value": "USD 10B", "ndp_pct": 20,
             "tenfold_value": "USD 50B", "tenfold_pct": 100, "sub_value": "",
             "confidence": "exact", "source": "UBOS"}
            for s in ["manufacturing_gdp", "manufacturing_tax", "mfg_exports",
                      "hightech_exports", "private_credit", "industrial_parks",
                      "fdi_manufacturing", "manufacturing_employment", "export_variety"]
        ],
        "sector_comparison": [
            {"chart": "tax", "sector": "Manufacturing", "pct": "20",
             "value_label": "Shs 5trn", "highlight": "1"},
            {"chart": "credit", "sector": "Manufacturing", "pct": "12",
             "value_label": "Shs 3trn", "highlight": "0"},
        ],
        "risk_register": [
            {"risk": "Data staleness", "category": "Data", "severity": "high",
             "likelihood": "medium", "mitigation": "Refresh", "owner": "Hillary"},
        ],
        "milestones": [
            {"year": "2025", "year_label": "2025", "value_chain": "Iron & Steel",
             "status": "in_progress", "project": "Mill", "category": "Investment",
             "note": "n"},
            {"year": "2026", "year_label": "2026", "value_chain": "All chains",
             "status": "planned", "project": "Policy", "category": "Policy", "note": "n"},
        ],
        "glossary": [{"term": "HS Code", "definition": "Harmonised System code"}],
        "chain_synergies": [{"title": "Shared inputs", "description": "steel feeds autos"}],
    }


def _treemap_agg():
    d = {"Central": {"Kampala": 5, "Wakiso": 3}}
    s = {"Food": {"Bakery": 4}}
    return (s, d, {"Central": {"Food": 4}}, {"Kampala": {"Food": 4}},
            {"Central": {"Bakery": 4}}, {"Kampala": {"Bakery": 4}})


@pytest.fixture
def wired(monkeypatch):
    """Wire the network seam to fixtures and enable PocketBase mode."""
    fx = _fixtures()
    monkeypatch.setattr(g, "pb_get", lambda coll, **kw: list(fx.get(coll, [])))
    monkeypatch.setattr(g, "pb_count", lambda coll, filter=None: 1234)
    monkeypatch.setattr(g, "_treemaps_from_pocketbase", _treemap_agg)
    monkeypatch.setattr(g, "PB_URL", "http://fixture")
    monkeypatch.setattr(g, "USE_POCKETBASE", True)
    return fx


TEMPLATE = (
    "<html><body>"
    "<!--%%CHAIN_SUMMARY_ROWS%%--><!--%%MACRO_TREND_ITEMS%%-->"
    "<!--%%TAX_DONUT%%--><!--%%KPI1_VALUE%%--><!--%%KPI7_VALUE%%-->"
    "<!--%%TENFOLD_PROGRESS_PANEL%%-->/*%%CHAINS_DATA%%*//*%%CHAIN_COLORS_DATA%%*/"
    "/*%%FACTORIES_DATA%%*//*%%TREEMAP_DATA%%*/<!--%%ESTABLISHMENT_COUNT%%-->"
    "<!--%%CHAIN_SYNERGIES%%--><!--%%GLOSSARY_ITEMS%%--><!--%%RISK_REGISTER_ROWS%%-->"
    "<!--%%MILESTONES_TABS%%--><!--%%MILESTONES_ITEMS%%--><!--%%RECENT_UPDATES%%-->"
    "<!--CHAT_BUBBLE_START-->bubble<!--CHAT_BUBBLE_END-->"
    "</body></html>"
)


# ── load_data ──────────────────────────────────────────────────────────────────
def test_load_data_populates_globals(wired):
    g.load_data()
    assert [c["name"] for c in g.chains] == ["Iron & Steel", "Textiles & Garments"]
    assert g.chain_colors["Iron & Steel"] == "#111"
    assert len(g.factories_list) == 2                       # from located industries
    assert g.ESTABLISHMENT_COUNT == 1234                    # from pb_count
    assert g.ESTABLISHMENT_COUNT_LABEL == "1,234"
    # establishments KPI value is overwritten with the live count label
    assert g.KEY_INDICATORS["establishments"]["value"] == "1,234"
    assert "tax" in {r["indicator_slug"] for r in g.key_indicator_categories}
    assert g.KPI_INDICATORS["manufacturing_gdp"]["label"] == "Manufacturing Gdp"
    assert g.glossary and g.chain_synergies and g.risk_register


def test_load_data_facilities_fallback(monkeypatch):
    fx = _fixtures()

    def fake_get(coll, **kw):
        if coll == "industries":
            return []          # no GPS rows -> facilities fallback path
        return list(fx.get(coll, []))

    monkeypatch.setattr(g, "pb_get", fake_get)
    monkeypatch.setattr(g, "pb_count", lambda coll, filter=None: 7011)
    monkeypatch.setattr(g, "USE_POCKETBASE", True)
    monkeypatch.setattr(g, "PB_URL", "http://fixture")
    g.load_data()
    assert g.factories_list[0]["name"] == "Fallback Fac"


def test_load_data_missing_kpi_slugs_uses_csv(monkeypatch):
    fx = _fixtures()
    fx["kpi_indicators"] = []                               # none in PB
    monkeypatch.setattr(g, "pb_get", lambda coll, **kw: list(fx.get(coll, [])))
    monkeypatch.setattr(g, "pb_count", lambda coll, filter=None: 7011)
    monkeypatch.setattr(g, "USE_POCKETBASE", True)
    monkeypatch.setattr(g, "PB_URL", "http://fixture")
    # the CSV backfill seam
    monkeypatch.setattr(g, "load_csv", lambda name: [
        {"id": "manufacturing_gdp", "label": "csv", "current_value": "", "current_pct": 0,
         "ndp_value": "", "ndp_pct": 0, "tenfold_value": "", "tenfold_pct": 0}])
    g.load_data()
    assert "manufacturing_gdp" in g.KPI_INDICATORS


def test_load_data_csv_fallback_branches(monkeypatch):
    # macro_trend / key_indicators / key_indicator_categories all empty in PB -> each
    # takes its CSV-fallback else branch (load_csv is the ADR-017 guard in real use,
    # stubbed here so the branches run instead of sys.exit).
    fx = _fixtures()
    for empty in ("macro_trend", "key_indicators", "key_indicator_categories"):
        fx[empty] = []
    monkeypatch.setattr(g, "pb_get", lambda coll, **kw: list(fx.get(coll, [])))
    monkeypatch.setattr(g, "pb_count", lambda coll, filter=None: 7011)
    monkeypatch.setattr(g, "_treemaps_from_pocketbase", _treemap_agg)
    monkeypatch.setattr(g, "USE_POCKETBASE", True)
    monkeypatch.setattr(g, "PB_URL", "http://fixture")
    monkeypatch.setattr(g, "load_csv", lambda name: {
        "key_indicators.csv": [{"slug": "value_added", "label": "V", "kind": "pie"}],
    }.get(name, []))
    g.load_data()
    assert g.macro_trend == []
    assert "value_added" in g.KEY_INDICATORS           # from the CSV fallback
    assert g.key_indicator_categories == []


# ── render ─────────────────────────────────────────────────────────────────────
def test_render_replaces_markers(wired):
    g.load_data()
    out = g.render(TEMPLATE)
    assert "<!--%%" not in out                              # every marker consumed
    assert "/*%%" not in out
    assert "<!--CHAT_BUBBLE_START-->" not in out
    assert "1,234" in out                                   # establishment count landed
    assert "Iron &amp; Steel" in out                        # escaped chain name in a row
    assert "TREEMAP_SECTOR_DATA" in out                     # treemap JS embedded


def test_render_warns_on_missing_marker(wired, capsys):
    g.load_data()
    g.render("<html>no markers here</html>")
    err = capsys.readouterr().err
    assert "marker not found" in err


# ── main ───────────────────────────────────────────────────────────────────────
def test_main_writes_output(tmp_path, monkeypatch, wired):
    tmpl_file = tmp_path / "tmpl.html"
    tmpl_file.write_text(TEMPLATE, "utf-8")
    out_file = tmp_path / "out.html"
    monkeypatch.setattr(g, "TMPL", tmpl_file)
    html = g.main(pb_url="http://fixture", out_path=out_file)
    assert out_file.exists()
    assert html == out_file.read_text("utf-8")
    assert "1,234" in html
    assert g.USE_POCKETBASE is True


def test_main_requires_pb_url(monkeypatch):
    monkeypatch.delenv("PB_URL", raising=False)
    with pytest.raises(SystemExit):
        g.main(pb_url="")


def test_main_missing_template(tmp_path, monkeypatch, wired):
    monkeypatch.setattr(g, "TMPL", tmp_path / "does-not-exist.html")
    with pytest.raises(SystemExit):
        g.main(pb_url="http://fixture", out_path=tmp_path / "o.html")


# ── import is inert (the core promise of the refactor) ─────────────────────────
def test_import_has_no_side_effects():
    import importlib
    m = importlib.reload(g)
    assert m.PB_URL == ""          # not read from env at import
    assert m.USE_POCKETBASE is False
