"""Tests for the Ask MIDD analytics wiring in app.py (ADR-020).

Covers the snapshot cache, the code planner, the best-effort augment (happy / no-code /
error), and the /ask endpoint rendering a chart. The network + CLI + sandbox are
monkeypatched, so no PocketBase / Claude CLI is needed.
"""
import pathlib
import sys
import types

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "midd-brain"))
pytest.importorskip("fastapi")
import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_cache():
    app._df_cache.update(dfs=None, at=0.0)
    yield


def _fixture_rows(coll):
    return {"industries": [{"region": "Central", "employees": 10},
                           {"region": "Northern", "employees": 5}]}.get(coll, [])


def test_get_dataframes_caches(monkeypatch):
    calls = {"n": 0}

    def fake_items(coll, params=""):
        calls["n"] += 1
        return _fixture_rows(coll)

    monkeypatch.setattr(app, "_pb_items", fake_items)
    d1 = app.get_dataframes()
    d2 = app.get_dataframes()
    assert d1 is d2                        # second call served from cache
    first_round = calls["n"]
    assert app.get_dataframes() is d1
    assert calls["n"] == first_round       # no extra fetches while cached


def test_plan_analysis(monkeypatch):
    monkeypatch.setattr(app, "_run_claude", lambda prompt, t: "result = len(industries)")
    assert app.plan_analysis("how many?", "schema") == "result = len(industries)"
    monkeypatch.setattr(app, "_run_claude", lambda prompt, t: "NONE")
    assert app.plan_analysis("who built this?", "schema") is None


def test_analytics_augment_happy(monkeypatch):
    monkeypatch.setattr(app, "_pb_items", _fixture_rows)
    monkeypatch.setattr(app, "_run_claude",
                        lambda prompt, t: "result = int(industries['employees'].sum())")
    monkeypatch.setattr(app.analytics_sandbox, "run_analysis",
                        lambda code, dfs, timeout=12: {"ok": True, "result": 15,
                                                       "stdout": "", "image":
                                                       "data:image/png;base64,AAA"})
    block, chart = app.analytics_augment("total employees?")
    assert "ANALYSIS RESULT" in block and "15" in block
    assert chart.startswith("<div") and "<img" in chart and "data:image/png" in chart


def test_analytics_augment_no_code(monkeypatch):
    monkeypatch.setattr(app, "_pb_items", _fixture_rows)
    monkeypatch.setattr(app, "_run_claude", lambda prompt, t: "NONE")
    assert app.analytics_augment("what is this project?") == ("", "")


def test_analytics_augment_swallows_errors(monkeypatch):
    def boom():
        raise RuntimeError("pandas missing on host")
    monkeypatch.setattr(app, "get_dataframes", boom)
    assert app.analytics_augment("anything") == ("", "")


def test_ask_endpoint_renders_chart(monkeypatch):
    monkeypatch.setattr(app, "PASSWORD", "secret")
    monkeypatch.setattr(app, "analytics_augment",
                        lambda q: ("ANALYSIS RESULT: 15\n\n",
                                   '<div class=ans><img src="data:image/png;base64,AAA"></div>'))
    monkeypatch.setattr(app.subprocess, "run",
                        lambda *a, **k: types.SimpleNamespace(
                            returncode=0, stdout="Central leads with 10.", stderr=""))
    client = TestClient(app.app)
    r = client.post("/ask", data={"password": "secret", "q": "employees by region?"})
    assert r.status_code == 200
    assert "Central leads with 10." in r.text
    assert "<img" in r.text                # the chart was embedded


def test_ask_endpoint_wrong_password():
    client = TestClient(app.app)
    r = client.post("/ask", data={"password": "nope", "q": "x"})
    assert "Wrong password" in r.text


def test_build_public_brief_includes_breakdowns(monkeypatch):
    data = {
        "value_chains": [{"name": "Iron & Steel", "key_export_2024": "US$10M"}],
        "key_indicators": [{"label": "Value added", "value": "14.5%"}],
        "key_indicator_categories": [
            {"indicator_slug": "tax", "category": "Manufacturing", "pct": 34,
             "value_label": "Shs 7.19trn"}],
        "macro_trend": [{"label": "Mfg growth", "fy2021_value": "3%", "fy2025_value": "6.4%"}],
        "industries": [{"sector_name": "Food", "region": "Central"}],
    }
    monkeypatch.setattr(app, "_pb_items", lambda coll, params="": list(data.get(coll, [])))
    app._brief_cache.update(text="", at=0.0)              # bust the TTL cache
    brief = app.build_public_brief()
    assert "Iron & Steel" in brief
    assert "tax contribution by sector" in brief and "Manufacturing 34%" in brief
    assert "Mfg growth" in brief
    app._brief_cache.update(text="", at=0.0)              # leave cache clean for other tests
