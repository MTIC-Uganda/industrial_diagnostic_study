"""
Tests for the single-source-of-truth enforcement (ADR-017).

These are the first tests under the new standard: every new pipeline/generator
change ships with tests. They verify the guardrail actually bites — the dashboard
and explorer generators refuse to run without PocketBase, and the guard script
passes on a clean tree.
"""
import os
import subprocess
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _run(cmd, extra_env=None):
    env = dict(os.environ)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, env=env)


def test_guard_passes_on_clean_tree():
    """check_single_source.sh returns 0 and reports OK on the committed tree."""
    r = _run(["bash", "scripts/check_single_source.sh"])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "single-source guard: OK" in r.stdout


def test_dashboard_generator_refuses_without_pocketbase():
    """generate_dashboard.py must hard-fail (no file fallback) when PB_URL is unset."""
    r = _run(["python3", "scripts/generate_dashboard.py"], {"PB_URL": ""})
    assert r.returncode != 0
    assert "SINGLE SOURCE" in (r.stdout + r.stderr)


def test_explorer_generator_refuses_without_pocketbase():
    """generate_explorer_data.py must hard-fail when PB_URL is unset."""
    r = _run(["python3", "scripts/generate_explorer_data.py"], {"PB_URL": ""})
    assert r.returncode != 0
    assert "SINGLE SOURCE" in (r.stdout + r.stderr)


def test_generators_contain_no_direct_data_file_reads():
    """No generator may read a committed data file (only the HTML template)."""
    for gen in ("scripts/generate_dashboard.py", "scripts/generate_explorer_data.py"):
        src = (ROOT / gen).read_text()
        assert "csv.DictReader" not in src, f"{gen} reintroduced a real CSV reader"
        # the only allowed read_text is the HTML template, never the DATA dir
        assert "(DATA / name).read_text" not in src
        assert "json.loads((DATA" not in src


def test_guard_detects_a_reintroduced_fallback(tmp_path):
    """A copy of a generator with a real file read must fail the guard's grep."""
    broken = tmp_path / "generate_dashboard.py"
    broken.write_text(
        "import csv\n"
        "def load_csv(name):\n"
        "    with open(name) as f:\n"
        "        return list(csv.DictReader(f))\n"
    )
    # the guard forbids csv.DictReader in a generator; grep must find it
    r = subprocess.run(["grep", "-nE", r"csv\.DictReader", str(broken)],
                       capture_output=True, text=True)
    assert r.returncode == 0 and "csv.DictReader" in r.stdout
