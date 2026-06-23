#!/usr/bin/env python3
"""
Keep STATUS.md's live numbers current from the running system (ADR-012: the brain
keeps its own records up to date). Queries PocketBase for the live counts, updates
the relevant lines in docs/STATUS.md, and commits + pushes [skip ci] only if
something actually changed. Run on a cron from a pushable clone.

Env: MIDD_REPO (default /opt/midd-brain/repo), PB_URL (default prod :8090).
"""
import os, re, json, subprocess, datetime, urllib.request, urllib.parse
from pathlib import Path

REPO = Path(os.environ.get("MIDD_REPO", "/opt/midd-brain/repo"))
PB   = os.environ.get("PB_URL", "http://127.0.0.1:8090").rstrip("/")
STATUS = REPO / "docs" / "STATUS.md"

def count(coll, filt=None):
    url = f"{PB}/api/collections/{coll}/records?perPage=1"
    if filt:
        url += "&filter=" + urllib.parse.quote(filt)
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return json.load(r).get("totalItems", "?")
    except Exception:
        return "?"

ind = count("industries")
reg = count("industries", 'reg_number !~ "FAC-"')
gps = count("industries", "latitude != 0 || longitude != 0")
vc  = count("value_chains")
kpi = count("kpi_indicators")
day = datetime.datetime.utcnow().strftime("%Y-%m-%d")

text = STATUS.read_text("utf-8")
orig = text
# Update the dated line and the live counts line.
text = re.sub(r"Last updated: .*", f"Last updated: {day} (live counts auto-refreshed)", text, count=1)
live = (f"- Live counts (auto): industries {ind} total = {reg} register + curated; "
        f"with GPS {gps}; value_chains {vc}; kpi_indicators {kpi}.")
if "- Live counts (auto):" in text:
    text = re.sub(r"- Live counts \(auto\):.*", live, text, count=1)
else:
    # insert just after the "## Data" heading's first line
    text = text.replace("## Data (single source of truth — ADR-011)\n",
                        "## Data (single source of truth — ADR-011)\n\n" + live + "\n", 1)

if text == orig:
    print("STATUS.md already current; no change.")
    raise SystemExit(0)

STATUS.write_text(text, "utf-8")
env = dict(os.environ); env.setdefault("HOME", "/root")
def g(*a): return subprocess.run(["git", "-C", str(REPO), *a], env=env,
                                 capture_output=True, text=True, timeout=40)
g("pull", "--ff-only", "-q")
STATUS.write_text(text, "utf-8")  # re-apply in case pull touched it
g("add", "docs/STATUS.md")
g("commit", "-m", "chore: refresh STATUS.md live counts [skip ci]")
r = g("push", "origin", "main")
if r.returncode != 0:
    g("pull", "--rebase", "-q"); g("push", "origin", "main")
print(f"STATUS.md refreshed: industries {ind} (register {reg}, gps {gps}).")
