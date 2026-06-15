#!/usr/bin/env python3
"""
MTIC Review Agent — Phase 2

Validates synthesised chapters against Jerome's quality_gate.json (32 checks
across 5 stages). Follows the review_agent_protocol exactly:

  STAGE_1 mandatory → must all pass before proceeding
  STAGE_2..5        → accumulate failures
  Verdict: PUBLISH (all mandatory pass) or RETURN_FOR_REVISION (any mandatory fail)

On PUBLISH:  opens a GitHub PR to merge the chapter into main.
On REVISION: writes a revision notice to data/revision/<vc_id>_revision.md
             (Hillary's WhatsApp hook picks this up and notifies the team).

Usage:
    python agents/review_agent.py              # review all new chapters
    python agents/review_agent.py --vc VC01    # Iron & Steel only
"""

import json, os, sys, textwrap, datetime, subprocess, urllib.request, urllib.error
from pathlib import Path
import sys as _sys; _sys.path.insert(0, str(Path(__file__).parent))
from _status import update_status

ROOT         = Path(__file__).resolve().parent.parent
SCHEMA_FILE  = ROOT / 'data' / 'schema' / 'diagnostic_schema.json'
QG_FILE      = ROOT / 'docs' / 'quality_gate.json'
CHAPTERS_DIR = ROOT / 'report' / 'chapters'
REVISION_DIR = ROOT / 'data' / 'revision'

PB_URL            = os.environ.get('PB_URL', 'http://89.167.121.193:8090').rstrip('/')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
GH_TOKEN          = os.environ.get('GH_TOKEN', os.environ.get('GITHUB_TOKEN', ''))
GITHUB_REF_NAME   = os.environ.get('GITHUB_REF_NAME', 'feat/synthesis')

RUN_ID = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

REVISION_DIR.mkdir(parents=True, exist_ok=True)

# ── Load schema + quality gate ────────────────────────────────────────────────

schema    = json.loads(SCHEMA_FILE.read_text('utf-8'))
FIELDS    = {f['field_id']: f for f in schema['fields']}
DOMAINS   = {d['domain_id']: d for d in schema['domains']}
VC_NAMES  = {vc['id']: vc['name'] for vc in schema['value_chains']}

quality_gate = json.loads(QG_FILE.read_text('utf-8'))
CHECKS       = quality_gate['checks']
PROTOCOL     = quality_gate['review_agent_protocol']
STAGES       = ['STAGE_1_EVIDENCE','STAGE_2_ANALYSIS','STAGE_3_PRIORITIZATION',
                'STAGE_4_INVESTMENT','STAGE_5_NARRATIVE_INTEGRITY']

# ── PocketBase ────────────────────────────────────────────────────────────────

def pb_get(path):
    url = f'{PB_URL}/{path.lstrip("/")}'
    try:
        with urllib.request.urlopen(url) as r:
            return json.loads(r.read())
    except urllib.error.URLError as e:
        sys.exit(f'PocketBase unreachable: {e}')

def fetch_datapoints(vc_id: str) -> list[dict]:
    items, page, total_pages = [], 1, 1
    while page <= total_pages:
        result = pb_get(
            f'/api/collections/diagnostic_datapoints/records'
            f'?filter=(value_chain_id="{vc_id}"'
            f'&&approval_status!="pending_approval"'
            f'&&approval_status!="rejected")'
            f'&perPage=500&page={page}&sort=field_id'
        )
        items.extend(result.get('items', []))
        total_pages = result.get('totalPages', 1)
        page += 1
    return items

# ── Claude API ────────────────────────────────────────────────────────────────

def claude(system_prompt: str, user_prompt: str,
           model: str = 'claude-sonnet-4-6') -> str:
    if not ANTHROPIC_API_KEY:
        sys.exit('ERROR: ANTHROPIC_API_KEY not set.')
    payload = {
        'model': model,
        'max_tokens': 8192,
        'system': system_prompt,
        'messages': [{'role': 'user', 'content': user_prompt}],
    }
    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=json.dumps(payload).encode(),
        method='POST',
        headers={
            'Content-Type': 'application/json',
            'x-api-key': ANTHROPIC_API_KEY,
            'anthropic-version': '2023-06-01',
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())['content'][0]['text']

# ── Review prompt ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""
You are the MTIC Review Agent. Your job is to validate a synthesised diagnostic
chapter against Jerome's quality gate. You are strict and precise — this chapter
will be published to Uganda's Ministry of Trade and UNIDO partners.

You follow the review_agent_protocol exactly:
1. Run STAGE_1 mandatory checks first. If any fail, set verdict=RETURN_FOR_REVISION
   and STOP — do not evaluate later stages.
2. If STAGE_1 passes, run STAGE_2, 3, 4, 5 in order, accumulating failures.
3. Verdict: PUBLISH if every mandatory check passed; RETURN_FOR_REVISION otherwise.
4. For RETURN_FOR_REVISION: produce a revision notice grouped by stage. Each item
   must cite: check_id, the statement, failing field_ids/domains, ToR criterion
   protected, and the concrete fix required.
5. Non-mandatory (conditional) failures are advisories — log them but do not block.

OUTPUT FORMAT — return a JSON object only, no prose:
{
  "verdict": "PUBLISH" | "RETURN_FOR_REVISION",
  "run_id": "<RUN_ID>",
  "vc_id": "<VC_ID>",
  "vc_name": "<VC_NAME>",
  "stage_results": {
    "STAGE_1_EVIDENCE": {"passed": true/false, "failures": [...]},
    "STAGE_2_ANALYSIS": {"passed": true/false, "failures": [...]},
    ...
  },
  "mandatory_failures": [
    {
      "check_id": "E-01",
      "stage": "STAGE_1_EVIDENCE",
      "statement": "...",
      "failing_fields": ["D0.01", ...],
      "tor_criterion": "completeness",
      "fix_required": "Specific action the ingestion or synthesis agent must take."
    }
  ],
  "advisories": [...],
  "revision_summary": "One paragraph summarising what must be fixed before publication."
}

If verdict is PUBLISH, set mandatory_failures=[] and revision_summary=null.
""").strip()

def build_review_prompt(vc_id: str, vc_name: str,
                        datapoints: list[dict], chapter_md: str) -> str:
    # Summarise datapoints: which fields are populated vs not_available
    populated = {dp['field_id']: dp for dp in datapoints
                 if dp.get('value') and dp.get('value') != 'not_available'}
    not_available = {dp['field_id']: dp for dp in datapoints
                     if dp.get('value') == 'not_available'}
    missing = [fid for fid in FIELDS if fid not in populated and fid not in not_available]

    mandatory_fields = [f['field_id'] for f in schema['fields']
                        if f['required_level'] == 'mandatory']

    dp_summary = []
    for fid in sorted(FIELDS):
        field = FIELDS[fid]
        if fid in populated:
            dp_summary.append(f"  {fid} POPULATED  conf={populated[fid].get('confidence')}  "
                              f"src={populated[fid].get('raw_source','')[:60]}")
        elif fid in not_available:
            dp_summary.append(f"  {fid} NOT_AVAILABLE  reason={not_available[fid].get('collection_notes','')[:80]}")
        elif field['required_level'] == 'mandatory':
            dp_summary.append(f"  {fid} MISSING (mandatory — no record at all)")
        else:
            dp_summary.append(f"  {fid} MISSING (optional)")

    checks_json = json.dumps(CHECKS, indent=2)

    return textwrap.dedent(f"""
VALUE CHAIN: {vc_name} ({vc_id})
REVIEW RUN:  {RUN_ID}

=== QUALITY GATE CHECKS ===
{checks_json}

=== REVIEW PROTOCOL ===
{json.dumps(PROTOCOL, indent=2)}

=== DATAPOINT STATUS ({len(datapoints)} records) ===
Mandatory fields: {len(mandatory_fields)} total
Populated:        {len(populated)}
Not_available:    {len(not_available)}
Missing entirely: {len(missing)}

{chr(10).join(dp_summary)}

=== SYNTHESISED CHAPTER (to validate) ===
{chapter_md[:40000]}
{"[... chapter truncated at 40,000 chars for context ...]" if len(chapter_md) > 40000 else ""}

Now run the quality gate checks and return your verdict as JSON.
""").strip()

# ── Verdict handling ──────────────────────────────────────────────────────────

def write_revision_notice(verdict: dict, vc_id: str) -> Path:
    vc_name = verdict.get('vc_name', vc_id)
    lines = [
        f'# Revision Notice — {vc_name} ({vc_id})',
        f'**Run:** {verdict.get("run_id")}',
        f'**Verdict:** RETURN_FOR_REVISION',
        '',
        '## What must be fixed',
        '',
    ]
    for fail in verdict.get('mandatory_failures', []):
        lines += [
            f'### {fail["check_id"]} — {fail["stage"]}',
            f'**Check:** {fail["statement"]}',
            f'**Failing fields:** {", ".join(fail.get("failing_fields", []))}',
            f'**ToR criterion:** {fail["tor_criterion"]}',
            f'**Fix required:** {fail["fix_required"]}',
            '',
        ]
    if verdict.get('advisories'):
        lines += ['## Advisories (non-blocking)', '']
        for adv in verdict['advisories']:
            lines.append(f'- **{adv.get("check_id")}**: {adv.get("statement")}')
        lines.append('')
    if verdict.get('revision_summary'):
        lines += ['## Summary', verdict['revision_summary'], '']

    out = REVISION_DIR / f'{vc_id}_revision.md'
    out.write_text('\n'.join(lines), encoding='utf-8')
    return out

def open_publish_pr(vc_id: str, vc_name: str, chapter_path: Path):
    """Open a GitHub PR to merge the chapter into main."""
    if not GH_TOKEN:
        print('  WARN: GH_TOKEN not set — cannot open PR. Commit the chapter manually.')
        return

    branch = f'publish/{vc_id.lower()}-diagnostic-{datetime.date.today().isoformat()}'
    try:
        subprocess.run(['git', 'checkout', '-b', branch], check=True, capture_output=True)
        subprocess.run(['git', 'add', str(chapter_path)], check=True, capture_output=True)
        subprocess.run(['git', 'commit', '-m',
                        f'feat: {vc_name} diagnostic chapter (review PASSED)'],
                       check=True, capture_output=True)
        subprocess.run(['git', 'push', 'origin', branch],
                       check=True, capture_output=True)

        # gh CLI
        body = textwrap.dedent(f"""\
        ## {vc_name} Diagnostic Chapter — Ready to Publish

        The review agent has validated this chapter against all 32 quality gate checks
        (5 stages). All mandatory checks PASSED.

        **Chain:** {vc_name} ({vc_id})
        **Review run:** {RUN_ID}
        **Chapter:** `{chapter_path.relative_to(ROOT)}`

        Review the chapter and merge to publish to the diagnostic report.

        /cc @jnuwabaasa-spec @arihosolomon @arindahills
        """)
        subprocess.run([
            'gh', 'pr', 'create',
            '--title', f'publish: {vc_name} diagnostic chapter (review PASSED)',
            '--body', body,
            '--base', 'main',
            '--head', branch,
        ], check=True, env={**os.environ, 'GH_TOKEN': GH_TOKEN})
        print(f'  PR opened for {vc_name} chapter.')

    except subprocess.CalledProcessError as e:
        print(f'  WARN: Could not open PR: {e.stderr.decode()[:200] if e.stderr else e}')

# ── Main review loop ──────────────────────────────────────────────────────────

def review(vc_id: str) -> dict:
    vc_name = VC_NAMES.get(vc_id)
    if not vc_name:
        sys.exit(f'Unknown value chain ID: {vc_id}')

    chapter_path = CHAPTERS_DIR / f'{vc_id}_diagnostic.md'
    if not chapter_path.exists():
        print(f'  No chapter found at {chapter_path.relative_to(ROOT)} — run synthesis first.')
        return {}

    print(f'\n── Reviewing {vc_name} ({vc_id}) ──')
    chapter_md = chapter_path.read_text('utf-8')
    datapoints = fetch_datapoints(vc_id)

    print(f'  {len(datapoints)} datapoints, chapter {len(chapter_md):,} chars')
    print(f'  Calling Claude for quality gate evaluation...')

    prompt     = build_review_prompt(vc_id, vc_name, datapoints, chapter_md)
    raw        = claude(SYSTEM_PROMPT, prompt)

    raw = raw.strip()
    if raw.startswith('```'):
        raw = raw.split('\n', 1)[1].rsplit('```', 1)[0]

    try:
        verdict = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f'  WARN: Claude returned invalid JSON: {e}')
        print(f'  Raw (first 500 chars): {raw[:500]}')
        return {}

    verdict['run_id'] = RUN_ID
    verdict['vc_id']  = vc_id
    verdict['vc_name']= vc_name

    v = verdict.get('verdict', 'UNKNOWN')
    mandatory_fails = len(verdict.get('mandatory_failures', []))
    advisories      = len(verdict.get('advisories', []))

    print(f'  Verdict: {v}  '
          f'(mandatory failures: {mandatory_fails}, advisories: {advisories})')

    if v == 'PUBLISH':
        print(f'  ✅ PUBLISH — opening PR...')
        open_publish_pr(vc_id, vc_name, chapter_path)
    else:
        print(f'  ❌ RETURN_FOR_REVISION')
        rev_path = write_revision_notice(verdict, vc_id)
        print(f'  Revision notice → {rev_path.relative_to(ROOT)}')
        print('  Fix the flagged gaps and re-run ingestion + synthesis.')

    update_status('review', vc_id, {
        'run_id': RUN_ID,
        'verdict': v,
        'mandatory_failures': mandatory_fails,
        'advisories': advisories,
        'revision_file': f'data/revision/{vc_id}_revision.md' if v != 'PUBLISH' else None,
        'revision_summary': verdict.get('revision_summary') if v != 'PUBLISH' else None,
    })

    return verdict


def run(vc_ids: list[str] | None = None):
    print(f'\n══ MTIC Review Agent  run={RUN_ID} ══')

    if vc_ids is None:
        # Review all chains that have a chapter file
        vc_ids = [
            vc_id for vc_id in VC_NAMES
            if (CHAPTERS_DIR / f'{vc_id}_diagnostic.md').exists()
        ]
        if not vc_ids:
            print('  No synthesised chapters found.')
            print('  Run the synthesis agent first: python agents/synthesis_agent.py')
            return

    verdicts = {}
    for vc_id in vc_ids:
        verdicts[vc_id] = review(vc_id)

    # Summary
    publish  = [vc for vc, v in verdicts.items() if v.get('verdict') == 'PUBLISH']
    revise   = [vc for vc, v in verdicts.items() if v.get('verdict') == 'RETURN_FOR_REVISION']

    print(f'\n══ Review complete ══')
    print(f'  PUBLISH:           {len(publish)} chains: {[VC_NAMES[v] for v in publish]}')
    print(f'  RETURN_FOR_REVISION: {len(revise)} chains: {[VC_NAMES[v] for v in revise]}')
    if revise:
        print('  Check data/revision/ for revision notices.')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='MTIC Review Agent')
    parser.add_argument('--vc', nargs='+',
                        help='Value chain IDs to review (e.g. VC01 VC02). '
                             'Default: all chains with a synthesised chapter.')
    args = parser.parse_args()
    run(vc_ids=args.vc)
