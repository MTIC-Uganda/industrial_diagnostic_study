"""Security + correctness tests for the chatbot DB tool validator (query_tool.py, ADR-018).

This is the boundary that stops a public LLM issuing arbitrary queries, so the
rejection cases matter as much as the happy path.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "midd-brain"))
import query_tool as qt  # noqa: E402


# ── happy path ────────────────────────────────────────────────────────────────
def test_valid_count_spec():
    spec = qt.validate_spec({
        "collection": "industries",
        "filters": [{"field": "district", "op": "=", "value": "Gulu"}],
        "mode": "count",
    })
    assert spec["collection"] == "industries"
    assert spec["filters"] == [{"field": "district", "op": "=", "value": "Gulu"}]
    assert spec["mode"] == "count"


def test_valid_list_spec_caps_limit():
    spec = qt.validate_spec({
        "collection": "industries",
        "filters": [{"field": "region", "op": "=", "value": "Central"}],
        "mode": "list", "limit": 9999,
    })
    assert spec["limit"] == qt.MAX_LIMIT


def test_no_filters_is_allowed_match_all():
    spec = qt.validate_spec({"collection": "value_chains", "filters": [], "mode": "list"})
    assert spec["filters"] == []


# ── whitelist rejections ──────────────────────────────────────────────────────
def test_reject_unknown_collection():
    assert qt.validate_spec({"collection": "_admins", "filters": [], "mode": "count"}) is None
    assert qt.validate_spec({"collection": "users", "filters": [], "mode": "list"}) is None


def test_reject_off_whitelist_filter_field():
    # contact / owner / password-ish fields are not filterable
    assert qt.validate_spec({"collection": "industries",
                             "filters": [{"field": "contact", "op": "=", "value": "x"}],
                             "mode": "count"}) is None


def test_reject_bad_operator():
    for op in ("!=", ">", "~~", "OR", ";"):
        assert qt.validate_spec({"collection": "industries",
                                 "filters": [{"field": "region", "op": op, "value": "Central"}],
                                 "mode": "count"}) is None


# ── injection / abuse rejections ──────────────────────────────────────────────
def test_reject_value_with_quote_or_backslash():
    for bad in ['Central" || reg_number~"', 'x\\y', 'a"b']:
        assert qt.validate_spec({"collection": "industries",
                                 "filters": [{"field": "region", "op": "=", "value": bad}],
                                 "mode": "count"}) is None


def test_reject_overlong_value():
    assert qt.validate_spec({"collection": "industries",
                             "filters": [{"field": "district", "op": "=", "value": "x" * 200}],
                             "mode": "count"}) is None


def test_reject_too_many_filters():
    fs = [{"field": "region", "op": "=", "value": "Central"}] * 10
    assert qt.validate_spec({"collection": "industries", "filters": fs, "mode": "count"}) is None


def test_reject_non_dict_and_bad_mode():
    assert qt.validate_spec("DROP TABLE") is None
    assert qt.validate_spec(None) is None
    assert qt.validate_spec({"collection": "industries", "filters": [], "mode": "delete"}) is None


def test_reject_boolean_value():
    assert qt.validate_spec({"collection": "industries",
                             "filters": [{"field": "status", "op": "=", "value": True}],
                             "mode": "count"}) is None


def test_reject_non_list_filters():
    assert qt.validate_spec({"collection": "industries",
                             "filters": "region=Central", "mode": "count"}) is None


def test_bad_limit_falls_back_to_default():
    spec = qt.validate_spec({"collection": "industries", "filters": [],
                             "mode": "list", "limit": "abc"})
    assert spec["limit"] == 20


# ── build_filter + return_fields ──────────────────────────────────────────────
def test_build_filter_single_and_multi():
    assert qt.build_filter([{"field": "district", "op": "=", "value": "Gulu"}]) == 'district="Gulu"'
    two = qt.build_filter([
        {"field": "region", "op": "=", "value": "Eastern"},
        {"field": "sector_name", "op": "~", "value": "pharma"},
    ])
    assert two == 'region="Eastern"&&sector_name~"pharma"'


def test_build_filter_empty():
    assert qt.build_filter([]) == ""


def test_return_fields_excludes_contact():
    fields = qt.return_fields("industries")
    assert "name" in fields and "contact" not in fields and "notes" not in fields
