"""Covers the public app's group-mode query execution (app.run_query, ADR-025).

run_query does I/O via _pb_items, so we monkeypatch that to a stub and assert the
group branch fetches with the right params (FAC-* excluded for industries, field
projected) and aggregates the returned rows read-only.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "midd-brain"))
import app  # noqa: E402


def test_run_query_group_industries_excludes_fac_and_aggregates(monkeypatch):
    captured = {}

    def fake_pb_items(collection, params=""):
        captured["collection"] = collection
        captured["params"] = params
        return [{"sector_name": "Metals"}, {"sector_name": "Metals"},
                {"sector_name": "Textiles"}]

    monkeypatch.setattr(app, "_pb_items", fake_pb_items)
    spec = {"collection": "industries", "filters": [], "mode": "group",
            "group_by": "sector_name", "limit": 15}
    out = app.run_query(spec)

    assert out["mode"] == "group"
    assert out["group_by"] == "sector_name"
    assert out["groups"] == [{"value": "Metals", "count": 2},
                             {"value": "Textiles", "count": 1}]
    # industries group must exclude the curated map-only FAC-* rows and project the field
    assert "FAC-" in captured["params"]
    assert "sector_name" in captured["params"]
    assert captured["collection"] == "industries"


def test_run_query_group_value_chains_no_fac_filter(monkeypatch):
    captured = {}

    def fake_pb_items(collection, params=""):
        captured["params"] = params
        return [{"position_tag": "lead"}, {"position_tag": "lead"},
                {"position_tag": "watch"}]

    monkeypatch.setattr(app, "_pb_items", fake_pb_items)
    spec = {"collection": "value_chains", "filters": [], "mode": "group",
            "group_by": "position_tag", "limit": 5}
    out = app.run_query(spec)

    assert out["groups"][0] == {"value": "lead", "count": 2}
    # value_chains is not the industries collection, so no FAC-* exclusion is applied
    assert "FAC-" not in captured["params"]
