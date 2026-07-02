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
