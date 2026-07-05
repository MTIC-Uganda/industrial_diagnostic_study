#!/usr/bin/env python3
"""
Upload orchestrator — turns one uploaded document into datastore records and a
rebuilt dashboard. The uploader (staging) launches this detached after committing
the file. Production goes through CI instead (which holds the prod secrets).

Flow:
  1. The Claude CLI reads the operator's intent (the .task.md sidecar) and states,
     in plain language, what the document is and what to do with it. Logged only.
  2. Route by folder AND file type:
       manufacturing-overview + register PDF   -> deterministic register parse
                                                  -> seed the `industries` collection
       manufacturing-overview + spreadsheet    -> key_indicators agent (updates the
                                                  KPI cards from a UBOS scorecard)
       any value-chain folder                  -> LLM ingestion agent -> diagnostic_datapoints
  3. Rebuild the dashboard with treemaps aggregated from PocketBase, deploy it.
  4. Self-check: confirm the treemap data made it into the page.

Structured so importing this module is inert (ADR-018): env reads + side effects run
under main(); the routing decision is the pure, unit-tested route().

Env:
  MTIC_FILE, MTIC_VC_FOLDER, MTIC_ENV, MTIC_WWW
  PB_URL, PB_ADMIN_EMAIL, PB_ADMIN_PASSWORD, CLAUDE_BIN
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPREADSHEET_SUFFIXES = (".xlsx", ".xls", ".csv")


def log(m, env="staging"):
    print(f"[orchestrator/{env}] {m}", flush=True)


def route(folder, suffix):
    """Pure routing decision -> 'scorecard' | 'register' | 'sector'."""
    if folder == "manufacturing-overview":
        return "scorecard" if suffix.lower() in SPREADSHEET_SUFFIXES else "register"
    return "sector"


def run(cmd, env_name="staging", cwd=ROOT):
    env = dict(os.environ)
    env.setdefault("HOME", "/root")
    log("RUN " + (" ".join(cmd) if isinstance(cmd, list) else cmd), env_name)
    r = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True,
                       text=True, shell=isinstance(cmd, str))
    if r.stdout:
        log(r.stdout[-2000:], env_name)
    if r.returncode != 0:
        log("STDERR " + (r.stderr or "")[-2000:], env_name)
        raise SystemExit(f"step failed ({r.returncode}): {cmd}")
    return r


def understand(intent, env_name="staging"):
    """Log the CLI's plain-language read of the upload (routing is not driven by this)."""
    prompt = ("You are the MTIC ingestion router. An operator uploaded a document with "
              "the instruction below. In 3 to 5 short lines, state: (1) what the document is, "
              "(2) which datastore collection it feeds — `industries` for the establishments "
              "register, `key_indicators` for a manufacturing-overview scorecard, "
              "`diagnostic_datapoints` for a value-chain study document, (3) what "
              "should be rebuilt. Be concise, no preamble.\n\nINSTRUCTION:\n" + intent)
    try:
        env = dict(os.environ)
        env.setdefault("HOME", "/root")
        r = subprocess.run([os.environ.get("CLAUDE_BIN", "claude"), "-p", "--output-format", "text"],
                           input=prompt, capture_output=True, text=True, env=env, timeout=300)
        log("LLM understanding:\n" + (r.stdout.strip() or "(empty)"), env_name)
    except Exception as e:  # noqa
        log(f"LLM understanding skipped: {e}", env_name)


def main(file=None, folder=None, env=None, www=None):
    file = Path(file if file is not None else os.environ["MTIC_FILE"])
    folder = folder if folder is not None else os.environ.get("MTIC_VC_FOLDER", "")
    env = env if env is not None else os.environ.get("MTIC_ENV", "staging")
    www = Path(www if www is not None else os.environ.get("MTIC_WWW", "/var/www/mtic-staging"))

    # 1. LLM understands the instruction (logged only)
    sidecar = file.with_suffix(file.suffix + ".task.md")
    intent = sidecar.read_text("utf-8") if sidecar.exists() else "(no intent provided)"
    understand(intent, env)

    # 2. Extract + store — route by folder AND file type
    kind = route(folder, file.suffix)
    if kind == "scorecard":
        log("Scorecard path: key_indicators agent -> update KPI cards from the spreadsheet", env)
        run([sys.executable, "agents/key_indicators_agent.py", str(file)], env)
    elif kind == "register":
        log("Register path: deterministic parse -> industries.json -> seed PocketBase industries", env)
        run([sys.executable, "scripts/extract_industries_to_records.py"], env)
        run([sys.executable, "db/seed_industries.py"], env)
    else:
        log("Sector path: LLM ingestion agent -> diagnostic_datapoints", env)
        run([sys.executable, "agents/ingestion_agent.py", str(file)], env)

    # 3. Rebuild dashboard (treemaps come from PocketBase) + publish
    run([sys.executable, "scripts/generate_dashboard.py"], env)
    www.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "report" / "sources-of-truth.html", www / "index.html")
    log(f"Published dashboard -> {www}/index.html", env)

    # 4. Self-check
    html = (www / "index.html").read_text("utf-8")
    ok = ("TREEMAP_DISTRICT_DATA" in html) and ("function squarify" in html)
    log(f"Self-check: treemap data present = {ok}", env)
    log("DONE" if ok else "DONE (warning: treemap data missing)", env)
    return ok


if __name__ == "__main__":
    main()
