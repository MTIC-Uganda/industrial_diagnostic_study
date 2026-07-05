"""Tests for the upload orchestrator routing (scripts/process_upload.py, ADR-018).

route() decides scorecard vs register vs sector; main() drives it. The external
steps (subprocess run, the CLI 'understand', the file copy) are monkeypatched so the
flow + branch selection are covered without a live PocketBase or Claude CLI.
"""
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))
import process_upload as pu  # noqa: E402


@pytest.mark.parametrize("folder,suffix,expected", [
    ("manufacturing-overview", ".xlsx", "scorecard"),
    ("manufacturing-overview", ".XLSX", "scorecard"),
    ("manufacturing-overview", ".csv", "scorecard"),
    ("manufacturing-overview", ".pdf", "register"),
    ("manufacturing-overview", ".docx", "register"),
    ("automotive", ".pdf", "sector"),
    ("textiles", ".xlsx", "sector"),      # spreadsheet only means scorecard in manufacturing-overview
])
def test_route(folder, suffix, expected):
    assert pu.route(folder, suffix) == expected


@pytest.fixture
def wired(monkeypatch):
    calls = []
    monkeypatch.setattr(pu, "run", lambda cmd, *a, **k: calls.append(cmd))
    monkeypatch.setattr(pu, "understand", lambda intent, env="staging": None)
    monkeypatch.setattr(pu.shutil, "copy", lambda a, b: None)
    return calls


def _www_with_markers(tmp_path, good=True):
    body = "TREEMAP_DISTRICT_DATA function squarify" if good else "nothing here"
    (tmp_path / "index.html").write_text(body, "utf-8")
    return tmp_path


def test_main_scorecard_branch(wired, tmp_path):
    www = _www_with_markers(tmp_path)
    ok = pu.main(file=str(tmp_path / "ubos.xlsx"), folder="manufacturing-overview",
                 env="staging", www=str(www))
    assert ok is True
    assert any("key_indicators_agent.py" in " ".join(c) for c in wired)


def test_main_register_branch(wired, tmp_path):
    www = _www_with_markers(tmp_path)
    pu.main(file=str(tmp_path / "register.pdf"), folder="manufacturing-overview",
            env="staging", www=str(www))
    joined = [" ".join(c) for c in wired]
    assert any("extract_industries_to_records.py" in j for j in joined)
    assert any("seed_industries.py" in j for j in joined)


def test_main_sector_branch_and_selfcheck_fail(wired, tmp_path):
    www = _www_with_markers(tmp_path, good=False)
    ok = pu.main(file=str(tmp_path / "study.pdf"), folder="automotive",
                 env="staging", www=str(www))
    assert ok is False        # markers missing -> self-check fails
    assert any("ingestion_agent.py" in " ".join(c) for c in wired)


def test_import_is_inert():
    # Importing must not read MTIC_FILE or run anything (that's the ADR-018 refactor).
    import importlib
    m = importlib.reload(pu)
    assert hasattr(m, "route") and hasattr(m, "main")


def test_run_success_and_failure():
    r = pu.run([sys.executable, "-c", "print('ok')"])
    assert r.returncode == 0 and "ok" in r.stdout
    with pytest.raises(SystemExit):
        pu.run([sys.executable, "-c", "import sys; sys.stderr.write('boom'); sys.exit(3)"])


def test_understand_logs_and_swallows_errors(monkeypatch, capsys):
    import types
    monkeypatch.setattr(pu.subprocess, "run",
                        lambda *a, **k: types.SimpleNamespace(stdout="it is a scorecard", returncode=0))
    pu.understand("some intent")
    assert "LLM understanding" in capsys.readouterr().out

    def boom(*a, **k):
        raise RuntimeError("cli missing")
    monkeypatch.setattr(pu.subprocess, "run", boom)
    pu.understand("some intent")     # must not raise
    assert "understanding skipped" in capsys.readouterr().out
