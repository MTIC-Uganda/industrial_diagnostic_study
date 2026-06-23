"""
Ask MIDD — a scoped brain UI for the team.

Jerome (and the team) ask questions or leave feedback about the Manufacturing
Industry Diagnostics Dashboard project. The backend runs the Claude CLI on the
Hetzner host, scoped to ONLY the MIDD project records (ADRs, meeting transcripts,
docs, data), so it is not Hillary's personal WhatsApp agent and carries no
unrelated context (ADR-012). Every exchange is logged as feedback.

v1 is read-only: it answers and records feedback. Applying a correction to the
data still flows through the ingestion/review agents; this UI captures the intent
and the brain explains how it will be handled.

Config via env:
  MIDD_ENV       staging | prod
  MIDD_PORT      listen port
  MIDD_PASSWORD  shared password
  MIDD_REPO      repo clone the brain reads from
  CLAUDE_BIN     claude CLI path (default: claude)
"""
import os, subprocess, datetime, html, json, urllib.parse
from pathlib import Path
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

ENV      = os.environ.get("MIDD_ENV", "staging")
REPO     = Path(os.environ.get("MIDD_REPO", "/opt/mtic-uploader/repo"))
PASSWORD = os.environ.get("MIDD_PASSWORD", "changeme")
IS_PROD  = ENV == "prod"
FEEDBACK_LOG = Path(f"/opt/midd-brain/feedback-{ENV}.jsonl")
# Windowed conversation memory, mirroring the WhatsApp agent: replay the last few
# exchanges so follow-ups work, but cap by turns AND characters so a long session
# can never overflow the model's context (the WhatsApp agent's Groq-413 lesson).
HISTORY_TURNS      = 8
HISTORY_CHAR_LIMIT = 12000

SCOPE = (
    "You are the assistant for the MIDD project (Manufacturing Industry Diagnostics "
    "Dashboard) for Uganda's Ministry of Trade, Industry and Cooperatives. Answer ONLY "
    "from this project's own records in the current repository: the ADRs in docs/adr, "
    "the meeting transcripts in meeting_transcripts, docs/, and the data under data/. "
    "Be concise and concrete. If asked something outside the MIDD project, say it is "
    "outside scope. If the user gives a correction or instruction about the data or the "
    "dashboard, acknowledge it clearly and explain that it will be applied through the "
    "ingestion pipeline (data is corrected through the system, never by editing the "
    "datastore directly). Do not make any changes yourself; only answer and advise."
)

app = FastAPI()


def recent_history():
    """The last few Q&A exchanges from this env's feedback log, as conversation
    memory. Windowed exactly like the WhatsApp agent: keep the last HISTORY_TURNS
    turns, then drop the oldest until under HISTORY_CHAR_LIMIT, so the injected
    history is bounded and a long session cannot overflow the context."""
    if not FEEDBACK_LOG.exists():
        return ""
    try:
        lines = FEEDBACK_LOG.read_text(encoding="utf-8").strip().splitlines()
    except Exception:
        return ""
    turns = []
    for ln in lines[-HISTORY_TURNS:]:
        try:
            e = json.loads(ln)
            turns.append(f"Q: {e.get('q','')}\nMIDD: {e.get('a','')}")
        except Exception:
            continue
    # sliding window by characters — drop oldest turns until under the cap
    while turns and sum(len(t) for t in turns) > HISTORY_CHAR_LIMIT:
        turns.pop(0)
    if not turns:
        return ""
    return ("EARLIER IN THIS CONVERSATION (oldest first; for context on follow-ups "
            "like 'what about the other one?'):\n\n" + "\n\n".join(turns) + "\n\n")


def shell(title, inner):
    badge = "PRODUCTION" if IS_PROD else "STAGING"
    bcol = "#166534" if IS_PROD else "#b45309"
    fav = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'>"
           f"<rect width='24' height='24' rx='5' fill='{bcol}'/>"
           "<circle cx='12' cy='10' r='4.3' fill='none' stroke='#fff' stroke-width='1.8'/>"
           "<rect x='11.1' y='13.5' width='1.8' height='4.5' rx='0.9' fill='#fff'/></svg>")
    favicon = "data:image/svg+xml," + urllib.parse.quote(fav)
    return f"""<!doctype html><html><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<link rel="icon" href="{favicon}">
<title>{html.escape(title)} &middot; Ask MIDD{'' if IS_PROD else ' (staging)'}</title>
<style>
 body{{font-family:Inter,system-ui,Arial,sans-serif;background:#0f1722;color:#e6edf3;margin:0}}
 .bar{{background:{bcol};color:#fff;padding:8px 20px;font-weight:700;font-size:13px}}
 .wrap{{max-width:760px;margin:32px auto;padding:0 20px}}
 h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#9fb0c0;font-size:13px;margin-bottom:20px}}
 textarea{{width:100%;box-sizing:border-box;padding:12px;background:#1b2735;border:1px solid #2d3e50;
   border-radius:8px;color:#e6edf3;font-size:14px;min-height:90px}}
 input[type=password]{{width:100%;box-sizing:border-box;padding:10px 12px;background:#1b2735;
   border:1px solid #2d3e50;border-radius:8px;color:#e6edf3;font-size:14px;margin-top:12px}}
 button{{margin-top:14px;background:#2563eb;color:#fff;border:0;border-radius:8px;padding:12px 22px;
   font-size:15px;font-weight:700;cursor:pointer}}
 .card{{background:#16202c;border:1px solid #25303d;border-radius:12px;padding:22px}}
 .ans{{white-space:pre-wrap;line-height:1.55;background:#11202e;border:1px solid #25303d;
   border-radius:10px;padding:16px;margin-bottom:18px}}
 label{{display:block;font-weight:600;font-size:13px;margin-bottom:6px}}
 a{{color:#60a5fa}}
</style></head><body>
<div class=bar>Ask MIDD &middot; {badge}</div>
<div class=wrap>{inner}</div></body></html>"""


FORM = """
<h1>Ask MIDD</h1>
<div class=sub>Ask anything about the Manufacturing Industry Diagnostics Dashboard, or
leave a correction or instruction. The assistant answers from the project's own records.
Data corrections are applied through the pipeline, not by editing the database directly.</div>
<div class=card>
<form method=post action=ask>
  {prior}
  <label>Your question or feedback</label>
  <textarea name=q required placeholder="e.g. Which table feeds the distribution treemaps, and how do I update the employment figures? Or: the Central region count looks too high, please check it."></textarea>
  <input type=password name=password placeholder="Password" required>
  <button type=submit>Ask</button>
</form>
</div>"""


@app.get("/health")
def health():
    return {"ok": True, "env": ENV}


@app.get("/", response_class=HTMLResponse)
def home():
    return shell("Ask MIDD", FORM.format(prior=""))


@app.post("/ask", response_class=HTMLResponse)
def ask(password: str = Form(...), q: str = Form(...)):
    if password != PASSWORD:
        return shell("Denied", "<div class=card><p style='color:#f87171'>Wrong password.</p>"
                     "<p><a href='/'>Back</a></p></div>")
    env = dict(os.environ); env.setdefault("HOME", "/root")
    try:
        r = subprocess.run([os.environ.get("CLAUDE_BIN", "claude"), "-p", "--output-format", "text"],
                           input=f"{SCOPE}\n\n{recent_history()}QUESTION OR FEEDBACK:\n{q}",
                           capture_output=True, text=True, env=env, cwd=str(REPO), timeout=420)
        answer = (r.stdout.strip() or r.stderr.strip() or "(no response)") if r.returncode == 0 \
                 else f"(brain error: {r.stderr.strip()[:300]})"
    except Exception as e:
        answer = f"(could not reach the brain: {e})"

    try:
        FEEDBACK_LOG.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        with FEEDBACK_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"at": ts, "env": ENV, "q": q, "a": answer[:2000]},
                               ensure_ascii=False) + "\n")
    except Exception:
        pass

    prior = (f"<div class=ans><b>Q:</b> {html.escape(q)}\n\n<b>MIDD:</b> {html.escape(answer)}</div>")
    return shell("Ask MIDD", FORM.format(prior=prior))
