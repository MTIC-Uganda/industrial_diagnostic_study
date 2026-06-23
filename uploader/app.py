"""
MTIC Document Uploader — gets Jerome off Git.

He opens a web page, picks the value chain, writes as much intent as he wants,
attaches a document of any form, and submits. The app drops the file into the
correct data/<value-chain>/ folder of the repo (exactly where every other source
document lives), writes a <file>.task.md sidecar carrying his full intent, and
commits it. Prod pushes to main (which triggers the pipeline); staging commits
to an isolated branch and does not push, so we can rehearse end to end without
touching prod.

Config via env:
  MTIC_ENV        staging | prod        (default staging)
  MTIC_PORT       listen port           (default 8210)
  MTIC_PASSWORD   shared password Jerome types
  MTIC_REPO       repo working tree     (default /opt/mtic-uploader/repo)
  MTIC_PUSH       "1" to push to main   (prod sets this)
  MTIC_INGEST_CMD optional shell cmd run after commit (the brain trigger)
"""
import os, re, subprocess, datetime, html, hashlib, urllib.parse
from pathlib import Path
from fastapi import FastAPI, UploadFile, Form, File
from fastapi.responses import HTMLResponse

ENV        = os.environ.get("MTIC_ENV", "staging")
REPO       = Path(os.environ.get("MTIC_REPO", "/opt/mtic-uploader/repo"))
PASSWORD   = os.environ.get("MTIC_PASSWORD", "changeme")
PUSH       = os.environ.get("MTIC_PUSH", "0") == "1"
INGEST_CMD = os.environ.get("MTIC_INGEST_CMD", "")
IS_PROD    = ENV == "prod"
STAGING_BRANCH = "uploads-staging"
# The matching PocketBase admin, reachable from this uploader (gated by its own
# admin login). Inspection surface; data corrections go through Ask MIDD.
PB_ADMIN_URL = "https://db.midd-ug.com/_/" if IS_PROD else "https://staging-db.midd-ug.com/_/"
# Staging only: the one-way "Apply to production" promotion command.
PROMOTE_CMD  = os.environ.get("MTIC_PROMOTE_CMD", "")

FOLDERS = {
    "Iron & Steel": "iron-steel",
    "Copper & Allied Metals": "copper-allied-metals",
    "Automotive": "automotive",
    "Textiles & Garments": "textiles-garments",
    "Pharmaceuticals": "pharmaceuticals",
    "Petrochemicals & Fertilizers": "petrochemicals-fertilizers",
    "Sugar & Confectionery": "sugar-confectionery",
    "Plastics & Packaging": "plastics-packaging",
    "Cement & Building Materials": "cement-building-materials",
    "Manufacturing overview / industries register": "manufacturing-overview",
    "Policy framework (cross-cutting)": "policy-framework",
}

app = FastAPI()


def find_duplicate(data: bytes):
    """Return the existing repo path if this exact document is already present
    (matched by content hash, so a rename does not sneak a duplicate past us)."""
    h, size = hashlib.sha256(data).hexdigest(), len(data)
    base = REPO / "data"
    if not base.exists():
        return None
    for p in base.rglob("*"):
        if (p.is_file() and not p.name.endswith(".task.md")
                and p.stat().st_size == size
                and hashlib.sha256(p.read_bytes()).hexdigest() == h):
            return p.relative_to(REPO)
    return None

def git(*args, check=True):
    env = dict(os.environ); env["HOME"] = "/root"
    return subprocess.run(["git", "-C", str(REPO), *args],
                          capture_output=True, text=True, env=env, check=check)


def prepare_tree():
    """Start each upload from the latest main, cleanly."""
    git("fetch", "origin", "--quiet", check=False)
    if IS_PROD:
        git("checkout", "main", check=False)
        git("reset", "--hard", "origin/main")
    else:
        # isolated branch off latest main; never pushed
        git("checkout", "-B", STAGING_BRANCH, "origin/main")


def shell(title, color, inner):
    badge = "PRODUCTION" if IS_PROD else "STAGING — rehearsal, not pushed to prod"
    bcol = "#166534" if IS_PROD else "#b45309"
    # Environment-coloured favicon (green = prod, amber = staging) so the browser
    # tab itself signals which uploader you are on. An upload-arrow glyph in an
    # SVG data URI; no separate file to serve.
    _fav = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'>"
            f"<rect width='24' height='24' rx='5' fill='{bcol}'/>"
            "<path d='M12 5l4.2 4.2h-2.8V14h-2.8V9.2H7.8z' fill='#fff'/>"
            "<rect x='7.6' y='16' width='8.8' height='1.9' rx='0.95' fill='#fff'/></svg>")
    favicon = "data:image/svg+xml," + urllib.parse.quote(_fav)
    tab_title = ("MIDD Uploader" if IS_PROD else "MIDD Uploader (staging)")
    return f"""<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<link rel="icon" href="{favicon}">
<title>{html.escape(title)} &middot; {tab_title}</title>
<style>
 body{{font-family:Inter,system-ui,Arial,sans-serif;background:#0f1722;color:#e6edf3;margin:0;padding:0}}
 .bar{{background:{bcol};color:#fff;padding:8px 20px;font-weight:700;font-size:13px;letter-spacing:.3px}}
 .wrap{{max-width:760px;margin:32px auto;padding:0 20px}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#9fb0c0;font-size:13px;margin-bottom:24px}}
 label{{display:block;font-weight:600;font-size:13px;margin:18px 0 6px}}
 select,input[type=password],input[type=file],textarea{{width:100%;box-sizing:border-box;padding:10px 12px;
   background:#1b2735;border:1px solid #2d3e50;border-radius:8px;color:#e6edf3;font-size:14px}}
 textarea{{min-height:160px;resize:vertical;line-height:1.5}}
 .hint{{color:#7f93a6;font-size:12px;margin-top:4px}}
 button{{margin-top:24px;background:#2563eb;color:#fff;border:0;border-radius:8px;padding:12px 22px;
   font-size:15px;font-weight:700;cursor:pointer}}
 .card{{background:#16202c;border:1px solid #25303d;border-radius:12px;padding:24px}}
 code{{background:#1b2735;padding:2px 6px;border-radius:5px;font-size:13px}}
 .ok{{color:#4ade80}} .err{{color:#f87171}}
</style></head><body>
<div class=bar>MTIC Document Uploader &middot; {badge}</div>
<div class=wrap>{inner}</div></body></html>"""


FORM = """
<h1>Upload a document</h1>
<div class=sub>Pick the value chain, describe what you want done with it in as much
detail as you like, attach the file, and submit. The file is saved into the repo
and your description is kept with it as the working instructions.</div>
<div class=card>
<form method=post action=upload enctype="multipart/form-data">
  <label>Value chain / area</label>
  <select name=value_chain required>{options}</select>

  <label>What is this document, and what should be done with it?</label>
  <textarea name=intent required placeholder="Describe it fully. e.g. This is the updated National Industries Register for September 2025. The table now has an extra column for employment numbers. Extract every establishment with its district, sector, sub-sector and employment, store it in the industries database, and rebuild the distribution treemaps. Also use it to refresh the establishment counts on the overview cards."></textarea>
  <div class=hint>This becomes the instruction the system follows, and is saved to the knowledge base.</div>

  <label>Document (PDF, Word, Excel, anything)</label>
  <input type=file name=file required>

  <label>Password</label>
  <input type=password name=password required>

  <button type=submit>Upload &amp; submit</button>
</form>
</div>"""


PROMOTE_FORM = """
<hr style="border-color:#25303d;margin:18px 0">
<h1 style="font-size:16px;margin:0 0 4px">Apply to production</h1>
<p class=hint style="margin-bottom:6px">When this staging result is good, promote it.
This copies the approved staging data to production and rebuilds the live dashboard.
One-way; un-promoted changes are discarded on the next refresh.</p>
<form method=post action=promote onsubmit="return confirm('Apply the CURRENT staging state to PRODUCTION? This updates the live dashboard.');">
  <label>Password</label>
  <input type=password name=password required>
  <button type=submit style="background:#166534">Apply to production</button>
</form>"""

TOOLS = """
<div class=card style="margin-top:20px">
  <h1 style="font-size:16px;margin:0 0 4px">Data store</h1>
  <p style="margin:0"><a style="color:#60a5fa" href="{pb}" target="_blank" rel="noopener">Open the data store (PocketBase) &rarr;</a></p>
  <p class=hint>Inspect what was extracted. Corrections go through Ask MIDD, not hand-edits.</p>
  {promote}
</div>"""


@app.get("/health")
def health():
    return {"ok": True, "env": ENV}


@app.get("/", response_class=HTMLResponse)
def home():
    options = "".join(f"<option>{html.escape(k)}</option>" for k in FOLDERS)
    tools = TOOLS.format(pb=PB_ADMIN_URL,
                         promote=("" if IS_PROD or not PROMOTE_CMD else PROMOTE_FORM))
    return shell("MTIC Uploader", "", FORM.format(options=options) + tools)


@app.post("/promote", response_class=HTMLResponse)
def promote(password: str = Form(...)):
    """Staging-only: one-way 'Apply to production'. Runs the promote script
    (staging PocketBase -> prod + rebuild prod dashboard). Never on prod."""
    if IS_PROD or not PROMOTE_CMD:
        return shell("Not available", "", "<div class=card><p class=err>Promotion runs "
                     "from the staging uploader only.</p><p><a style='color:#60a5fa' "
                     "href='/'>Back</a></p></div>")
    if password != PASSWORD:
        return shell("Denied", "", "<div class=card><p class=err>Wrong password.</p>"
                     "<p><a style='color:#60a5fa' href='/'>Back</a></p></div>")
    env = dict(os.environ); env["HOME"] = "/root"
    r = subprocess.run(PROMOTE_CMD, shell=True, capture_output=True, text=True, env=env)
    out = (r.stdout + r.stderr)[-2500:]
    ok = r.returncode == 0
    body = (f"<h1 class={'ok' if ok else 'err'}>"
            f"{'Applied to production' if ok else 'Promotion failed'}</h1>"
            f"<div class=card><p>{'The approved staging state is now live — the prod dashboard is rebuilt.' if ok else 'Production was NOT changed. See the output below.'}</p>"
            f"<pre>{html.escape(out)}</pre>"
            f"<p><a style='color:#60a5fa' href='/'>Back</a></p></div>")
    return shell("Apply to production", "", body)


@app.post("/upload", response_class=HTMLResponse)
async def upload(password: str = Form(...), value_chain: str = Form(...),
                 intent: str = Form(...), file: UploadFile = File(...)):
    if password != PASSWORD:
        return shell("Denied", "", "<div class=card><p class=err>Wrong password.</p>"
                     "<p><a style='color:#60a5fa' href='/'>Back</a></p></div>")
    folder = FOLDERS.get(value_chain)
    if not folder:
        return shell("Error", "", "<div class=card><p class=err>Unknown value chain.</p></div>")

    safe = re.sub(r"[^A-Za-z0-9._-]", "-", file.filename or "document").lower()
    data = await file.read()

    try:
        prepare_tree()
        dup = find_duplicate(data)
        if dup:
            return shell("Already uploaded", "",
                         f"<div class=card><p class=err>This exact document is already "
                         f"in the system as <code>{html.escape(str(dup))}</code>.</p>"
                         f"<p>Re-uploading the same work is blocked. If this is a genuinely "
                         f"newer version, change its content (or tell Hillary) so it is treated "
                         f"as an update, not a duplicate.</p>"
                         f"<p><a style='color:#60a5fa' href='/'>Back</a></p></div>")
        dest_dir = REPO / "data" / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / safe
        dest.write_bytes(data)

        ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        sidecar = dest_dir / (safe + ".task.md")
        sidecar.write_text(
            f"---\nuploaded_by: Jerome (via uploader)\nuploaded_at: {ts}\n"
            f"value_chain: {value_chain}\nenv: {ENV}\nsource_file: {safe}\n---\n\n"
            f"{intent.strip()}\n", encoding="utf-8")

        git("add", f"data/{folder}/{safe}", f"data/{folder}/{safe}.task.md")
        # [skip ci] keeps GitHub Actions out of the data path: the Hetzner
        # orchestrator owns seeding + rebuild + publish, so CI must not also
        # redeploy and race it. The commit is for provenance (doc lives in repo).
        commit_msg = (f"data: Jerome uploaded {safe} to {folder} (uploader/{ENV}) [skip ci]"
                      f"\n\n{intent.strip()[:500]}")
        git("commit", "-m", commit_msg, check=False)
        commit = git("rev-parse", "--short", "HEAD", check=False).stdout.strip()

        pushed = False
        if PUSH:
            pr = git("push", "origin", "main", check=False)
            pushed = pr.returncode == 0

        ingest_out = ""
        if INGEST_CMD:
            env = dict(os.environ); env["HOME"] = "/root"
            env["MTIC_FILE"] = str(dest); env["MTIC_VC_FOLDER"] = folder
            ir = subprocess.run(INGEST_CMD, shell=True, capture_output=True, text=True, env=env)
            ingest_out = (ir.stdout + ir.stderr)[-1200:]
    except subprocess.CalledProcessError as e:
        return shell("Failed", "", f"<div class=card><p class=err>Git step failed:</p>"
                     f"<pre>{html.escape((e.stderr or str(e))[:800])}</pre></div>")

    note = ("Committed and pushed to main — the pipeline will pick it up."
            if pushed else
            ("Committed on the staging branch (not pushed — this is a rehearsal)."
             if not IS_PROD else "Committed (push skipped)."))
    body = (f"<h1 class=ok>Received</h1><div class=card>"
            f"<p><b>{html.escape(safe)}</b> saved to <code>data/{folder}/</code></p>"
            f"<p>Sidecar: <code>data/{folder}/{html.escape(safe)}.task.md</code></p>"
            f"<p>Commit: <code>{html.escape(commit)}</code> &middot; {note}</p>"
            + (f"<p>Brain output:</p><pre>{html.escape(ingest_out)}</pre>" if ingest_out else "")
            + "<p><a style='color:#60a5fa' href='/'>Upload another</a></p></div>")
    return shell("Received", "", body)
