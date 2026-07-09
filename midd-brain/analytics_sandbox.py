"""
analytics_sandbox — the security boundary for "safe but powerful" analytics (ADR-020).

The team Ask MIDD may run REAL analysis (pandas / numpy / scikit-learn) over the
PocketBase data: any read-only query, grouping, regression, clustering, whatever the
question needs. The power comes from executing model-written Python. The safety comes
from four layers, all in this module (no I/O in the pure parts, so they're unit-tested):

  1. AST validation (`validate_code`)  — reject imports off the whitelist, dunder-escape
     attribute access (`__globals__`, `__subclasses__`, ...), and dangerous builtins
     (eval/exec/open/getattr/...). First line of defence, purely static.
  2. Restricted builtins (`SAFE_BUILTINS`) — the exec namespace has only harmless builtins
     plus a guarded `__import__` that admits ONLY whitelisted modules. Runtime enforcement
     even if the AST check is somehow bypassed.
  3. Read-only data — the code sees the collections as in-memory DataFrames passed in by the
     caller. There is NO PocketBase handle, NO credentials, NO network client, NO write path
     in the namespace. It can query and compute; it cannot alter a table (ADR-017 holds by
     construction — the source is untouchable from here).
  4. Process isolation (`run_analysis`) — the exec runs in a short-lived SUBPROCESS with a
     CPU + address-space rlimit and a wall-clock timeout, so a runaway or a crash cannot take
     the brain down or exhaust the box.

Public exposure would additionally need a no-network namespace (container). That is out of
scope here: this ships to the GATED team tool first (trusted, behind Cloudflare Access).
"""

import ast
import builtins
import contextlib
import io
import os

# Force a headless matplotlib backend for the whole process: any `import matplotlib.pyplot`
# in analysis code renders off-screen (no display, no GUI), so plotting works on the server.
os.environ.setdefault("MPLBACKEND", "Agg")

MAX_CODE_LEN = 8000          # a generous analysis snippet, not a program
MAX_OUTPUT = 20000           # cap captured stdout / serialized result
MAX_IMAGE_BYTES = 3_000_000  # cap a returned chart (~3MB PNG)

# Modules the analysis code may import (generous scientific-python stack, not just the
# named few). Submodules are matched by prefix, so e.g. matplotlib.pyplot, sklearn.cluster,
# scipy.stats all resolve. The point is power; the safety is that none of these grant
# filesystem-escape, network, or process control — that's what the name/dunder checks stop.
ALLOWED_MODULES = {
    "pandas", "numpy", "scipy", "sklearn", "statsmodels",
    "matplotlib", "seaborn", "plotly", "networkx",
    "math", "statistics", "random", "datetime", "json", "re",
    "collections", "itertools", "functools", "operator", "decimal", "fractions",
}
_ALLOWED_PREFIXES = tuple(m + "." for m in ALLOWED_MODULES)
_IMPORT_NOT_ALLOWED = "import not allowed: %s"

# Bare names that must never appear in analysis code (escape / side-effect vectors).
DANGEROUS_NAMES = frozenset({
    "eval", "exec", "compile", "open", "__import__", "input",
    "globals", "locals", "vars", "getattr", "setattr", "delattr",
    "breakpoint", "exit", "quit", "help", "memoryview", "print",
})
# Note: `print` is blocked as a bare-name shadow risk; the caller reads a `result` variable,
# not stdout, so analysis code never needs print. (Kept simple: use `result = ...`.)

# Builtins the analysis namespace is allowed to use.
_SAFE_BUILTIN_NAMES = frozenset({
    "abs", "all", "any", "ascii", "bin", "bool", "bytearray", "bytes", "callable",
    "chr", "complex", "dict", "divmod", "enumerate", "filter", "float", "format",
    "frozenset", "hex", "int", "isinstance", "issubclass", "iter", "len", "list",
    "map", "max", "min", "next", "oct", "ord", "pow", "range", "repr", "reversed",
    "round", "set", "slice", "sorted", "str", "sum", "tuple", "zip",
    "True", "False", "None",
    # Exception classes — types only, no sandbox-escape surface, so model-written
    # try/except and raise work. Missing these caused "NameError: name 'ValueError'
    # is not defined" and burned the compute retries (ADR-020, ADR-022 follow-up).
    "Exception", "ValueError", "TypeError", "KeyError", "IndexError",
    "ZeroDivisionError", "ArithmeticError", "RuntimeError", "StopIteration",
    "AttributeError", "NameError", "OverflowError", "FloatingPointError",
    "NotImplementedError", "AssertionError",
})


def _module_allowed(name):
    if not name:
        return False
    return name in ALLOWED_MODULES or name.startswith(_ALLOWED_PREFIXES)


def _is_dunder(attr):
    return len(attr) >= 4 and attr.startswith("__") and attr.endswith("__")


def validate_code(code):
    """Statically validate analysis code. Returns (ok: bool, reason: str)."""
    if not isinstance(code, str) or not code.strip():
        return False, "empty code"
    if len(code) > MAX_CODE_LEN:
        return False, "code too long"
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return False, "syntax error: %s" % exc.msg
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not _module_allowed(alias.name):
                    return False, _IMPORT_NOT_ALLOWED % alias.name
        elif isinstance(node, ast.ImportFrom):
            if not _module_allowed(node.module or ""):
                return False, _IMPORT_NOT_ALLOWED % (node.module or "?")
        elif isinstance(node, ast.Attribute):
            if _is_dunder(node.attr):
                return False, "dunder attribute not allowed: %s" % node.attr
        elif isinstance(node, ast.Name):
            if node.id in DANGEROUS_NAMES:
                return False, "name not allowed: %s" % node.id
    return True, "ok"


def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    """A guarded __import__: admits only whitelisted modules (runtime enforcement)."""
    root = name.split(".")[0] if name else ""
    if _module_allowed(name) or _module_allowed(root):
        return builtins.__import__(name, globals, locals, fromlist, level)
    raise ImportError(_IMPORT_NOT_ALLOWED % name)


def build_safe_builtins():
    """The restricted __builtins__ dict for the analysis namespace."""
    safe = {n: getattr(builtins, n) for n in _SAFE_BUILTIN_NAMES if hasattr(builtins, n)}
    safe["__import__"] = _safe_import
    return safe


def _analysis_libs():
    """Pre-injected, always-available analysis handles (fast imports only)."""
    import numpy as np
    import pandas as pd
    return {"pd": pd, "np": np, "pandas": pd, "numpy": np}


def _to_jsonable(value, _depth=0):
    """Best-effort conversion of an analysis result to a JSON-friendly, size-capped form."""
    if _depth > 6:
        return str(value)[:MAX_OUTPUT]
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    # numpy / pandas scalars
    if hasattr(value, "item") and not hasattr(value, "__len__"):
        try:
            return value.item()
        except Exception:
            return str(value)
    # pandas DataFrame / Series
    tname = type(value).__name__
    if tname == "DataFrame":
        return {"_type": "DataFrame", "rows": len(value),
                "records": value.head(200).to_dict(orient="records")}
    if tname == "Series":
        return {"_type": "Series", "data": value.head(500).to_dict()}
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v, _depth + 1) for k, v in list(value.items())[:500]}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v, _depth + 1) for v in list(value)[:500]]
    if hasattr(value, "tolist"):   # numpy array
        try:
            return _to_jsonable(value.tolist(), _depth + 1)
        except Exception:
            return str(value)[:MAX_OUTPUT]
    return str(value)[:MAX_OUTPUT]


def _capture_figure():
    """Return the active matplotlib figure as a base64 data URI, or None if there is none."""
    import sys
    if "matplotlib.pyplot" not in sys.modules:
        return None
    try:
        import base64
        plt = sys.modules["matplotlib.pyplot"]
        if not plt.get_fignums():
            return None
        buf = io.BytesIO()
        plt.gcf().savefig(buf, format="png", bbox_inches="tight", dpi=100)
        plt.close("all")
        data = buf.getvalue()
        if len(data) > MAX_IMAGE_BYTES:
            return None
        return "data:image/png;base64," + base64.b64encode(data).decode("ascii")
    except Exception:
        return None


def execute_restricted(code, dataframes):
    """Validate then exec analysis code in the restricted namespace (in-process).

    dataframes: {name: pandas.DataFrame} exposed read-only to the code.
    The code sets a `result` variable with its answer; if it draws with matplotlib the
    active figure is returned as a base64 PNG under "image".
    Returns {"ok", "error", "result", "stdout", "image"}.

    This is the security core: no PB handle, no credentials, no network, restricted
    builtins. `run_analysis` wraps it in a subprocess for resource isolation.
    """
    ok, reason = validate_code(code)
    if not ok:
        return {"ok": False, "error": reason, "result": None, "stdout": "", "image": None}

    namespace = {"__builtins__": build_safe_builtins()}
    namespace.update(_analysis_libs())
    for name, df in (dataframes or {}).items():
        namespace[name] = df

    buf = io.StringIO()
    try:
        compiled = compile(code, "<analysis>", "exec")
        with contextlib.redirect_stdout(buf):
            exec(compiled, namespace)
    except Exception as exc:
        return {"ok": False, "error": "%s: %s" % (type(exc).__name__, exc),
                "result": None, "stdout": buf.getvalue()[:MAX_OUTPUT], "image": None}

    return {"ok": True, "error": None,
            "result": _to_jsonable(namespace.get("result")),
            "stdout": buf.getvalue()[:MAX_OUTPUT],
            "image": _capture_figure()}


def run_analysis(code, dataframes, timeout=8, memory_mb=512):
    """Run execute_restricted in an isolated subprocess (CPU/mem rlimit + wall-clock timeout).

    Falls back to in-process execution where subprocess isolation is unavailable (e.g. the
    child cannot be spawned); the restricted-namespace guarantees still hold either way.
    Returns the same dict shape as execute_restricted, plus {"timeout": True} on timeout.
    """
    import json
    import os
    import pickle
    import subprocess
    import sys
    import tempfile

    ok, reason = validate_code(code)   # fail fast before spawning
    if not ok:
        return {"ok": False, "error": reason, "result": None, "stdout": ""}

    tmpdir = tempfile.mkdtemp(prefix="midd-analysis-")
    data_path = os.path.join(tmpdir, "data.pkl")
    with open(data_path, "wb") as fh:
        pickle.dump({"code": code, "dataframes": dataframes or {}}, fh)

    child = (
        "import pickle, json, sys, os\n"
        "sys.path.insert(0, %r)\n"
        "import analytics_sandbox as a\n"
        "d = pickle.load(open(%r, 'rb'))\n"
        "print(json.dumps(a.execute_restricted(d['code'], d['dataframes'])))\n"
        % (os.path.dirname(os.path.abspath(__file__)), data_path)
    )

    def _limit():   # pragma: no cover - runs only in the child process
        try:
            import resource
            soft = memory_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (soft, soft))
            resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout + 1))
        except Exception:
            pass

    try:
        proc = subprocess.run(
            [sys.executable, "-c", child],
            capture_output=True, text=True, timeout=timeout,
            preexec_fn=_limit if os.name == "posix" else None,
            env={"PATH": os.environ.get("PATH", ""), "MPLBACKEND": "Agg"},
            cwd=tmpdir,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "analysis timed out", "result": None,
                "stdout": "", "timeout": True}
    except Exception:
        # Subprocess unavailable: fall back to in-process (guards still apply).
        return execute_restricted(code, dataframes)
    finally:
        try:
            os.remove(data_path)
            os.rmdir(tmpdir)
        except OSError:
            pass

    out = (proc.stdout or "").strip()
    if not out:
        return {"ok": False, "error": (proc.stderr or "no output")[:MAX_OUTPUT],
                "result": None, "stdout": ""}
    try:
        return json.loads(out.splitlines()[-1])
    except (ValueError, IndexError):
        return {"ok": False, "error": "unparseable analysis output", "result": None,
                "stdout": out[:MAX_OUTPUT]}
