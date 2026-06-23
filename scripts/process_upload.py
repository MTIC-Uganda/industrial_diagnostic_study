#!/usr/bin/env python3
"""
Upload orchestrator — turns one uploaded document into datastore records and a
rebuilt dashboard. The uploader (staging) launches this detached after committing
the file. Production goes through CI instead (which holds the prod secrets).

Flow:
  1. The Claude CLI reads the operator's intent (the .task.md sidecar) and states,
     in plain language, what the document is and what to do with it. This is the
     "LLM understands the instruction" step, and it is logged.
  2. Route by folder:
       manufacturing-overview -> deterministic register parse -> industries.json
                                 -> seed the PocketBase `industries` collection
       any value-chain folder -> LLM ingestion agent -> diagnostic_datapoints
  3. Rebuild the dashboard with treemaps aggregated from PocketBase, deploy it.
  4. Self-check: confirm the treemap data made it into the page.

Env:
  MTIC_FILE       absolute path to the uploaded file (inside the repo clone)
  MTIC_VC_FOLDER  sector folder (manufacturing-overview, automotive, ...)
  MTIC_ENV        staging | prod
  MTIC_WWW        dir to publish index.html into (/var/www/mtic-staging)
  PB_URL, PB_ADMIN_EMAIL, PB_ADMIN_PASSWORD   target PocketBase
  CLAUDE_BIN      claude CLI path (default: claude)
"""
import os, sys, subprocess, shutil
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
FILE   = Path(os.environ["MTIC_FILE"])
FOLDER = os.environ.get("MTIC_VC_FOLDER", "")
ENV    = os.environ.get("MTIC_ENV", "staging")
WWW    = Path(os.environ.get("MTIC_WWW", "/var/www/mtic-staging"))

def log(m): print(f"[orchestrator/{ENV}] {m}", flush=True)

def run(cmd, cwd=ROOT):
    env = dict(os.environ); env.setdefault("HOME", "/root")
    log("RUN " + (" ".join(cmd) if isinstance(cmd, list) else cmd))
    r = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True,
                       text=True, shell=isinstance(cmd, str))
    if r.stdout: log(r.stdout[-2000:])
    if r.returncode != 0:
        log("STDERR " + (r.stderr or "")[-2000:])
        raise SystemExit(f"step failed ({r.returncode}): {cmd}")
    return r

# 1. LLM understands the instruction
sidecar = FILE.with_suffix(FILE.suffix + ".task.md")
intent  = sidecar.read_text("utf-8") if sidecar.exists() else "(no intent provided)"
try:
    prompt = ("You are the MTIC ingestion router. An operator uploaded a document with "
              "the instruction below. In 3 to 5 short lines, state: (1) what the document is, "
              "(2) which datastore collection it feeds — `industries` for the establishments "
              "register, `diagnostic_datapoints` for a value-chain study document, (3) what "
              "should be rebuilt. Be concise, no preamble.\n\nINSTRUCTION:\n" + intent)
    env = dict(os.environ); env.setdefault("HOME", "/root")
    r = subprocess.run([os.environ.get("CLAUDE_BIN", "claude"), "-p", "--output-format", "text"],
                       input=prompt, capture_output=True, text=True, env=env, timeout=300)
    log("LLM understanding:\n" + (r.stdout.strip() or "(empty)"))
except Exception as e:
    log(f"LLM understanding skipped: {e}")

# 2. Extract + store
if FOLDER == "manufacturing-overview":
    log("Register path: deterministic parse -> industries.json -> seed PocketBase industries")
    run([sys.executable, "scripts/extract_industries_to_records.py"])
    run([sys.executable, "db/seed_industries.py"])
else:
    log("Sector path: LLM ingestion agent -> diagnostic_datapoints")
    run([sys.executable, "agents/ingestion_agent.py", str(FILE)])

# 3. Rebuild dashboard (treemaps come from PocketBase) + publish
run([sys.executable, "scripts/generate_dashboard.py"])
WWW.mkdir(parents=True, exist_ok=True)
shutil.copy(ROOT / "report" / "sources-of-truth.html", WWW / "index.html")
log(f"Published dashboard -> {WWW}/index.html")

# 4. Self-check
html = (WWW / "index.html").read_text("utf-8")
ok = ("TREEMAP_DISTRICT_DATA" in html) and ("function squarify" in html)
log(f"Self-check: treemap data present = {ok}")
log("DONE" if ok else "DONE (warning: treemap data missing)")
