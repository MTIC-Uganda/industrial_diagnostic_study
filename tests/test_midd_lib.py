"""Unit tests for scripts/midd_lib.py — the pure helpers (ADR-018).

These are the model for the coverage ratchet: pure logic, imported directly,
covered line-by-line (not via subprocess).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import midd_lib as m  # noqa: E402


# ── pb_filter / slug_filter / two_field_filter ────────────────────────────────
def test_pb_filter_encodes_space_and_ampersand():
    out = m.pb_filter('(category="Wholesale & Retail")')
    assert " " not in out and "&" not in out.replace("%26", "")
    assert "%20" in out and "%26" in out


def test_slug_filter_shape_and_encoding():
    assert m.slug_filter("iron-steel") == m.pb_filter('(slug="iron-steel")')
    assert "slug" in urllib_unquote(m.slug_filter("x"))


def test_two_field_filter_builds_and_query():
    raw = '(indicator_slug="tax"&&category="Wholesale & Retail")'
    assert m.two_field_filter("indicator_slug", "tax", "category", "Wholesale & Retail") == m.pb_filter(raw)


def urllib_unquote(s):
    import urllib.parse
    return urllib.parse.unquote(s)


# ── is_real_establishment ─────────────────────────────────────────────────────
def test_is_real_establishment_true_for_registered():
    assert m.is_real_establishment({"reg_number": "NIR-2025-000123"}) is True


def test_is_real_establishment_false_for_curated_pin():
    assert m.is_real_establishment({"reg_number": "FAC-007"}) is False


def test_is_real_establishment_missing_reg_number():
    assert m.is_real_establishment({}) is True


# ── confidence_badge ──────────────────────────────────────────────────────────
def test_confidence_badge_known_levels():
    assert m.confidence_badge("exact")[1] == "conf-exact"
    assert m.confidence_badge("indicative")[0].endswith("indicative")
    assert m.confidence_badge("not_available")[1] == "conf-na"


def test_confidence_badge_unknown_defaults_to_estimated():
    assert m.confidence_badge("wat") == m.CONFIDENCE_BADGE["estimated"]


# ── aggregate_counts ──────────────────────────────────────────────────────────
def test_aggregate_counts_two_levels():
    rows = [
        {"region": "Central", "sector": "Food"},
        {"region": "Central", "sector": "Food"},
        {"region": "Central", "sector": "Metals"},
        {"region": "Eastern", "sector": "Food"},
    ]
    assert m.aggregate_counts(rows, "region", "sector") == {
        "Central": {"Food": 2, "Metals": 1},
        "Eastern": {"Food": 1},
    }


def test_aggregate_counts_skips_rows_missing_a_key():
    rows = [
        {"region": "Central", "sector": "Food"},
        {"region": "Central", "sector": ""},     # skipped (blank)
        {"region": "Central"},                    # skipped (missing)
    ]
    assert m.aggregate_counts(rows, "region", "sector") == {"Central": {"Food": 1}}


def test_aggregate_counts_single_level():
    rows = [{"region": "Central"}, {"region": "Central"}, {"region": "Western"}]
    assert m.aggregate_counts(rows, "region") == {"Central": 2, "Western": 1}
