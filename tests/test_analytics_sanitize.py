"""Public-tier hardening tests (ADR-025): column sanitization + sandbox arg wrapping.

sanitize_dataframes is the structural guarantee that the public analytics sandbox cannot
surface a person; hardened_argv composes the network-isolation + privilege-drop wrappers.
"""
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "midd-brain"))
import analytics_lib as al  # noqa: E402
import analytics_sandbox as asb  # noqa: E402


def test_sanitize_drops_person_columns_keeps_business_columns():
    df = pd.DataFrame([{
        "name": "Acme Steel Ltd", "sector_name": "Basic Metals", "district": "Jinja",
        "employees": 42, "persons_engaged": 50,          # employment stays (not "person" token)
        "owner_name": "Jane Doe", "contact_phone": "0700000000",
        "director": "John Roe", "notes": "call before visit",
    }])
    out = al.sanitize_dataframes({"industries": df})["industries"]
    cols = set(out.columns)
    assert {"name", "sector_name", "district", "employees", "persons_engaged"} <= cols
    assert not ({"owner_name", "contact_phone", "director", "notes"} & cols)


def test_sanitize_handles_empty_and_no_sensitive_columns():
    clean = pd.DataFrame([{"sector_name": "Food", "count": 3}])
    out = al.sanitize_dataframes({"a": clean, "b": pd.DataFrame()})
    assert list(out["a"].columns) == ["sector_name", "count"]  # untouched
    assert out["b"].empty


def test_hardened_argv_composes_unshare_and_setpriv():
    base = ["/usr/bin/python3", "-c", "print(1)"]
    argv = asb.hardened_argv(base, unshare_path="/usr/bin/unshare",
                             setpriv_path="/usr/bin/setpriv")
    # unshare --net wraps the outside; setpriv drops privilege just inside it
    assert argv[:3] == ["/usr/bin/unshare", "--net", "--"]
    assert "/usr/bin/setpriv" in argv and "--reuid" in argv and "nobody" in argv
    assert argv[-3:] == base


def test_hardened_argv_noops_without_tools():
    base = ["/usr/bin/python3", "-c", "print(1)"]
    assert asb.hardened_argv(base) == base                     # neither tool present
    only_unshare = asb.hardened_argv(base, unshare_path="/u")
    assert only_unshare[:3] == ["/u", "--net", "--"] and only_unshare[3:] == base


def test_run_analysis_harden_executes_when_tools_absent():
    # On a host without unshare/setpriv (e.g. macOS CI runner), harden falls back to a
    # plain subprocess and still runs — proving the harden path doesn't break execution.
    res = asb.run_analysis("result = 6 * 7", {}, timeout=10, harden=True)
    assert res["ok"] is True
    assert res["result"] == 42
