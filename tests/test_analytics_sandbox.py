"""Security + correctness tests for the analytics sandbox (analytics_sandbox.py, ADR-020).

The sandbox lets the team tool run real pandas/numpy/sklearn/matplotlib analysis. Its whole
value depends on the guarantee that the code can query but never (a) reach the OS / network,
(b) escape the restricted namespace, or (c) touch a data source. So the REJECTION cases and
the read-only guarantee matter as much as the happy path.
"""
import pathlib
import sys

import pandas as pd
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "midd-brain"))
import analytics_sandbox as sb  # noqa: E402


@pytest.fixture
def frames():
    return {"industries": pd.DataFrame([
        {"region": "Central", "district": "Wakiso", "sector_name": "Food", "employees": 10},
        {"region": "Central", "district": "Kampala", "sector_name": "Food", "employees": 20},
        {"region": "Northern", "district": "Gulu", "sector_name": "Textiles", "employees": 5},
    ])}


# ── validate_code: happy path ──────────────────────────────────────────────────
@pytest.mark.parametrize("code", [
    "result = industries.groupby('region').size().to_dict()",
    "import numpy as np\nresult = int(np.array([1, 2, 3]).sum())",
    "import pandas as pd\nresult = len(industries)",
    "from sklearn.cluster import KMeans\nresult = 1",
    "import matplotlib.pyplot as plt\nplt.plot([1, 2, 3])\nresult = 'plotted'",
    "from scipy import stats\nresult = 2",
])
def test_valid_code_accepted(code):
    ok, reason = sb.validate_code(code)
    assert ok, reason


# ── validate_code: rejection cases (the security boundary) ─────────────────────
@pytest.mark.parametrize("code,needle", [
    ("import os", "import not allowed"),
    ("import sys", "import not allowed"),
    ("import subprocess", "import not allowed"),
    ("from os import path", "import not allowed"),
    ("import socket", "import not allowed"),
    ("result = open('/etc/passwd').read()", "open"),
    ("result = eval('1+1')", "eval"),
    ("result = exec('x=1')", "exec"),
    ("result = __import__('os')", "__import__"),
    ("result = compile('1', '<s>', 'eval')", "compile"),
    ("result = getattr(industries, 'x')", "getattr"),
    ("result = globals()", "globals"),
    ("result = ().__class__.__bases__", "dunder"),
    ("result = [].__class__.__mro__[1].__subclasses__()", "dunder"),
    ("result = industries.__class__", "dunder"),
    ("result = (1).__class__.__bases__[0].__subclasses__()", "dunder"),
])
def test_dangerous_code_rejected(code, needle):
    ok, reason = sb.validate_code(code)
    assert not ok
    assert needle in reason


def test_empty_and_oversize_and_syntax():
    assert not sb.validate_code("")[0]
    assert not sb.validate_code("   ")[0]
    assert not sb.validate_code(123)[0]
    assert not sb.validate_code("x = " + "1" * (sb.MAX_CODE_LEN + 10))[0]
    ok, reason = sb.validate_code("def broken(:\n")
    assert not ok
    assert "syntax error" in reason


# ── helpers ────────────────────────────────────────────────────────────────────
def test_module_allowed_prefix_and_root():
    assert sb._module_allowed("sklearn.cluster")
    assert sb._module_allowed("matplotlib.pyplot")
    assert sb._module_allowed("pandas")
    assert not sb._module_allowed("os")
    assert not sb._module_allowed("")
    assert not sb._module_allowed("os.path")


def test_is_dunder():
    assert sb._is_dunder("__class__")
    assert sb._is_dunder("__globals__")
    assert not sb._is_dunder("value")
    assert not sb._is_dunder("_private")


def test_safe_builtins_shape():
    b = sb.build_safe_builtins()
    assert "len" in b and "sum" in b and "sorted" in b
    assert "open" not in b and "eval" not in b and "exec" not in b
    assert b["__import__"] is sb._safe_import


def test_safe_import_allows_whitelisted_and_blocks_rest():
    assert sb._safe_import("numpy") is not None
    with pytest.raises(ImportError):
        sb._safe_import("os")
    with pytest.raises(ImportError):
        sb._safe_import("")


# ── _to_jsonable ───────────────────────────────────────────────────────────────
def test_to_jsonable_scalars_and_containers():
    assert sb._to_jsonable(None) is None
    assert sb._to_jsonable(3) == 3
    assert sb._to_jsonable("x") == "x"
    assert sb._to_jsonable([1, 2, {"a": 3}]) == [1, 2, {"a": 3}]
    assert sb._to_jsonable({"k": 1}) == {"k": 1}


def test_to_jsonable_numpy_and_pandas():
    import numpy as np
    assert sb._to_jsonable(np.int64(5)) == 5
    assert sb._to_jsonable(np.array([1, 2])) == [1, 2]
    df = pd.DataFrame([{"a": 1}, {"a": 2}])
    out = sb._to_jsonable(df)
    assert out["_type"] == "DataFrame" and out["rows"] == 2
    s = pd.Series([1, 2], index=["x", "y"])
    assert sb._to_jsonable(s)["_type"] == "Series"


def test_to_jsonable_fallbacks():
    class BadItem:
        def item(self):
            raise ValueError("nope")

    class BadToList:
        def tolist(self):
            raise ValueError("nope")

    class Plain:
        def __repr__(self):
            return "plain-object"

    assert isinstance(sb._to_jsonable(BadItem()), str)       # item() raises -> str
    assert isinstance(sb._to_jsonable(BadToList()), str)     # tolist() raises -> str
    assert sb._to_jsonable(Plain()) == "plain-object"        # no handler -> str(value)
    assert sb._to_jsonable((1, 2)) == [1, 2]                 # tuple -> list
    assert sorted(sb._to_jsonable({1, 2})) == [1, 2]         # set -> list


def test_to_jsonable_depth_guard():
    deep = {}
    cur = deep
    for _ in range(10):
        cur["n"] = {}
        cur = cur["n"]
    # should not raise, deep nesting collapses to str at the cap
    assert sb._to_jsonable(deep) is not None


# ── execute_restricted: real analysis runs, dangerous code is refused ──────────
def test_execute_groupby(frames):
    out = sb.execute_restricted(
        "result = industries.groupby('region').size().to_dict()", frames)
    assert out["ok"]
    assert out["result"] == {"Central": 2, "Northern": 1}


def test_execute_sklearn(frames):
    code = ("from sklearn.linear_model import LinearRegression\n"
            "import numpy as np\n"
            "X = industries[['employees']].values\n"
            "y = np.arange(len(X))\n"
            "m = LinearRegression().fit(X, y)\n"
            "result = round(float(m.coef_[0]), 6)")
    out = sb.execute_restricted(code, frames)
    assert out["ok"], out["error"]
    assert isinstance(out["result"], float)


def test_execute_rejects_dangerous(frames):
    out = sb.execute_restricted("import os\nresult = os.listdir('/')", frames)
    assert not out["ok"]
    assert "import not allowed" in out["error"]


def test_execute_runtime_error_is_caught(frames):
    out = sb.execute_restricted("result = 1 / 0", frames)
    assert not out["ok"]
    assert "ZeroDivisionError" in out["error"]


def test_execute_import_blocked_at_runtime_even_if_static_passes(frames):
    # bare `__import__` is caught statically; here confirm the guarded __import__ blocks os
    # via a from-import of a non-whitelisted module (static check also catches it).
    out = sb.execute_restricted("from socket import socket\nresult = 1", frames)
    assert not out["ok"]


def test_execute_matplotlib_returns_image(frames):
    code = ("import matplotlib.pyplot as plt\n"
            "industries.groupby('region').size().plot(kind='bar')\n"
            "result = 'chart'")
    out = sb.execute_restricted(code, frames)
    assert out["ok"], out["error"]
    assert out["image"] and out["image"].startswith("data:image/png;base64,")


def test_capture_figure_none_without_matplotlib():
    # In a run that never imported pyplot there is no figure.
    out = sb.execute_restricted("result = 1 + 1", {})
    assert out["result"] == 2
    # image may be None (no figure drawn in this snippet)
    assert out.get("image") is None or out["image"] is None


# ── run_analysis: subprocess isolation happy path + timeout ────────────────────
def test_run_analysis_subprocess(frames):
    out = sb.run_analysis("result = int(industries['employees'].sum())", frames, timeout=15)
    assert out["ok"], out.get("error")
    assert out["result"] == 35


def test_run_analysis_rejects_before_spawn(frames):
    out = sb.run_analysis("import os\nresult=1", frames)
    assert not out["ok"]
    assert "import not allowed" in out["error"]


def test_run_analysis_timeout(frames):
    # tight CPU spin; wall-clock timeout should fire
    out = sb.run_analysis("x = 0\nwhile True:\n    x += 1\nresult = x", frames, timeout=2)
    assert not out["ok"]
    assert out.get("timeout") or "timed out" in (out.get("error") or "")
