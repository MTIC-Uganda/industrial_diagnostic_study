"""Public analytics tier wiring in app.py (ADR-025).

Covers the sanitized DataFrame snapshot, the best-effort augment (skip-when-busy / no-code
/ happy), and the /api/ask endpoint feeding an analysis block + returning a chart. CLI,
sandbox and PocketBase are monkeypatched.
"""
import pathlib
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "midd-brain"))
pytest.importorskip("fastapi")
import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture(autouse=True)
def _reset(monkeypatch):
    app._df_cache.update(dfs=None, at=0.0)
    app._public_df_cache.update(dfs=None, at=0.0)
    app._public_analysis_active["n"] = 0
    yield
    app._public_analysis_active["n"] = 0


def test_get_public_dataframes_is_sanitized(monkeypatch):
    df = pd.DataFrame([{"name": "Acme", "sector_name": "Metals", "owner_name": "Jane"}])
    monkeypatch.setattr(app, "get_dataframes", lambda: {"industries": df})
    out = app.get_public_dataframes()
    assert "owner_name" not in out["industries"].columns
    assert {"name", "sector_name"} <= set(out["industries"].columns)


def test_public_augment_skips_when_all_slots_busy(monkeypatch):
    app._public_analysis_active["n"] = app.MAX_CONCURRENT_PUBLIC_ANALYSIS
    # must not even build data / call the planner when saturated
    monkeypatch.setattr(app, "get_public_dataframes",
                        lambda: (_ for _ in ()).throw(AssertionError("should not run")))
    assert app.public_analytics_augment("anything") == ("", "")


def test_public_augment_no_code(monkeypatch):
    monkeypatch.setattr(app, "get_public_dataframes", lambda: {"industries": pd.DataFrame()})
    monkeypatch.setattr(app, "plan_analysis", lambda q, schema: None)
    assert app.public_analytics_augment("what is this project?") == ("", "")
    assert app._public_analysis_active["n"] == 0            # slot released


def test_public_augment_happy_hardened(monkeypatch):
    monkeypatch.setattr(app, "get_public_dataframes", lambda: {"industries": pd.DataFrame()})
    monkeypatch.setattr(app, "plan_analysis", lambda q, schema: "result = 42")
    seen = {}

    def fake_run(code, dfs, timeout=8, memory_mb=512, harden=False):
        seen["harden"] = harden
        return {"ok": True, "result": 42, "stdout": "", "image": "data:image/png;base64,AAA"}

    monkeypatch.setattr(app.analytics_sandbox, "run_analysis", fake_run)
    block, img = app.public_analytics_augment("biggest bottleneck?")
    assert "ANALYSIS RESULT" in block and "42" in block
    assert img == "data:image/png;base64,AAA"
    assert seen["harden"] is True                           # public tier runs hardened
    assert app._public_analysis_active["n"] == 0            # slot released


def test_api_ask_feeds_analysis_and_returns_chart(monkeypatch):
    monkeypatch.setattr(app, "_rate_ok", lambda ip: (True, ""))
    monkeypatch.setattr(app, "build_public_brief", lambda: "BRIEF")
    monkeypatch.setattr(app, "plan_query", lambda q: None)
    monkeypatch.setattr(app, "public_analytics_augment",
                        lambda q: ("ANALYSIS RESULT: 42\n\n", "data:image/png;base64,AAA"))
    captured = {}

    def fake_run_claude(prompt, timeout):
        captured["prompt"] = prompt
        return "Food Products leads with 1,952 establishments."

    monkeypatch.setattr(app, "_run_claude", fake_run_claude)
    client = TestClient(app.app)
    r = client.post("/api/ask", json={"q": "which sectors have the most establishments?"})
    assert r.status_code == 200
    body = r.json()
    assert "Food Products" in body["answer"]
    assert body["image"] == "data:image/png;base64,AAA"     # chart returned to the bubble
    assert "ANALYSIS RESULT: 42" in captured["prompt"]       # analysis fed into the answer
