"""Unit tests for the public chatbot data brief (midd-brain/brief_lib.py, ADR-018).

The brief is the ONLY context the public bubble gets. These tests pin the shape and,
crucially, that it emits only the sanitized aggregates it is handed — never people or
fields it wasn't given (the guardrail that stops the name leak).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "midd-brain"))
import brief_lib as b  # noqa: E402


def test_brief_lists_chains_with_trade_and_target():
    chains = [{"name": "Iron & Steel", "key_export_2024": "US$10M",
               "key_import_2024": "US$50M", "target_2040": "US$1B"}]
    out = b.format_public_brief(chains, [], {}, {})
    assert "Iron & Steel" in out
    assert "exports US$10M" in out and "imports US$50M" in out and "2040 target US$1B" in out


def test_brief_chain_without_figures_still_listed():
    out = b.format_public_brief([{"name": "Sugar & Confectionery"}], [], {}, {})
    assert "Sugar & Confectionery" in out


def test_brief_totals_regions_sectors():
    out = b.format_public_brief([], [], {"Food": 100, "Metals": 40}, {"Central": 90, "Eastern": 50})
    assert "Registered manufacturing establishments: 140" in out
    assert "Central: 90" in out and "Eastern: 50" in out
    assert "Food: 100" in out and "Metals: 40" in out


def test_brief_kpi_with_source_and_year():
    out = b.format_public_brief(
        [], [{"label": "Mfg value added", "value": "14.5%", "year": "2024",
              "source_detail": "UBOS FY24/25"}], {}, {})
    assert "Mfg value added: 14.5%, 2024 (source: UBOS FY24/25)" in out


def test_brief_drops_kpi_without_value():
    out = b.format_public_brief([], [{"label": "incomplete"}], {}, {})
    assert "incomplete" not in out


def test_brief_emits_only_given_aggregates():
    # A record with a name field must not leak: the formatter is never handed people,
    # and given only a chain name it emits only that.
    out = b.format_public_brief([{"name": "Textiles"}], [], {}, {})
    assert out.count("\n") == 1  # scope line + one chain line
    assert "Textiles" in out


def test_brief_empty_inputs_is_just_scope():
    out = b.format_public_brief([], [], {}, {})
    assert out.strip().startswith("Scope:")
    assert "establishments" not in out


def test_brief_renders_category_breakdowns():
    cats = [
        {"indicator_slug": "tax", "category": "Wholesale & Retail", "pct": 39, "value_label": "Shs 6.1trn"},
        {"indicator_slug": "tax", "category": "Manufacturing", "pct": 34, "value_label": "Shs 7.19trn"},
        {"indicator_slug": "credit", "category": "Real Estate", "pct": 25, "value_label": "Shs 5.0trn"},
    ]
    out = b.format_public_brief([], [], {}, {}, categories=cats)
    assert "Manufacturing tax contribution by sector:" in out
    assert "Wholesale & Retail 39% (Shs 6.1trn)" in out
    assert "Manufacturing 34% (Shs 7.19trn)" in out
    assert "Private sector credit by sector:" in out
    assert "Real Estate 25% (Shs 5.0trn)" in out


def test_brief_category_unknown_slug_falls_back_to_slug():
    cats = [{"indicator_slug": "widgets", "category": "A", "pct": 10}]
    out = b.format_public_brief([], [], {}, {}, categories=cats)
    assert "widgets: A 10%." in out


def test_brief_renders_macro_trends():
    macro = [
        {"label": "Manufacturing growth", "fy2021_value": "3.0%", "fy2025_value": "6.4%", "delta": "+3.4pts"},
        {"label": "Manufactured exports", "fy2025_value": "USD 85M"},
    ]
    out = b.format_public_brief([], [], {}, {}, macro=macro)
    assert "Manufacturing growth: 3.0% (FY20/21) to 6.4% (FY24/25), change +3.4pts." in out
    assert "Manufactured exports: USD 85M." in out


def test_brief_macro_without_values_dropped():
    out = b.format_public_brief([], [], {}, {}, macro=[{"label": "empty"}])
    assert "empty" not in out


def test_brief_macro_only_fy2021():
    out = b.format_public_brief([], [], {}, {}, macro=[{"label": "Old metric", "fy2021_value": "2.0%"}])
    assert "Old metric: 2.0%." in out


def test_as_list_variants():
    assert b._as_list(None) == []
    assert b._as_list(["a", " b ", ""]) == ["a", "b"]
    assert b._as_list('["x", "y"]') == ["x", "y"]
    assert b._as_list("plain") == ["plain"]
    assert b._as_list("[broken") == ["[broken"]
    assert b._as_list(5) == ["5"]


def test_brief_chain_diagnostics():
    chains = [{"name": "Textiles", "position_tag": "Net importer", "priority_tag": "Priority 1",
               "target_2040": "US$1B", "current": ["2 mills running"],
               "constraints": '["high yarn cost", "old machines"]',
               "priorities": ["local yarn"], "gap": "no local yarn production",
               "companies": ["Fine Spinners", "Southern Range Nyanza"]}]
    out = b.format_public_brief(chains, [], {}, {})
    assert "position: Net importer" in out and "priority: Priority 1" in out
    assert "current state: 2 mills running" in out
    assert "constraints: high yarn cost; old machines" in out
    assert "priorities: local yarn" in out
    assert "gap/opportunity: no local yarn production" in out
    assert "companies: Fine Spinners; Southern Range Nyanza" in out


def test_brief_targets_glossary_synergies():
    out = b.format_public_brief(
        [], [], {}, {},
        targets=[{"label": "Mfg GDP", "current_value": "USD 5B", "ndp_value": "USD 10B",
                  "tenfold_value": "USD 50B"}],
        glossary=[{"term": "HS Code", "definition": "Harmonised System code"}],
        synergies=[{"title": "Shared inputs", "description": "steel feeds autos"}])
    assert "Tenfold growth targets" in out
    assert "Mfg GDP: USD 5B -> USD 10B -> USD 50B" in out
    assert "HS Code = Harmonised System code" in out
    assert "Shared inputs: steel feeds autos" in out


def test_brief_risks_exclude_owner_names():
    out = b.format_public_brief(
        [], [], {}, {},
        risks=[{"risk": "Data staleness", "severity": "high",
                "mitigation": "refresh often", "owner": "Hillary Arinda"}],
        milestones=[{"year_label": "2025", "value_chain": "Iron & Steel",
                     "project": "Steel mill", "status": "in_progress"}])
    assert "Data staleness (severity high); mitigation: refresh often" in out
    assert "Hillary" not in out                       # owner/person never enters the brief
    assert "2025 Iron & Steel: Steel mill (in_progress)" in out
