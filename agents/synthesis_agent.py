#!/usr/bin/env python3
"""
MTIC Synthesis Agent — Phase 2

Reads approved datapoints from PocketBase (diagnostic_datapoints collection)
for one or all value chains, then calls Claude to write the full diagnostic
chapter for each chain following Jerome's schema synthesis_guidance.

Usage:
    python agents/synthesis_agent.py              # all chains with data
    python agents/synthesis_agent.py --vc VC01    # Iron & Steel only

Output:
    report/chapters/<vc_id>_diagnostic.md   (e.g. VC01_diagnostic.md)
    Also commits to git if run in CI.
"""

import json, os, sys, textwrap, datetime, urllib.request, urllib.error
from pathlib import Path

ROOT        = Path(__file__).resolve().parent.parent
SCHEMA_FILE = ROOT / 'data' / 'schema' / 'diagnostic_schema.json'
CHAPTERS_DIR= ROOT / 'report' / 'chapters'

PB_URL            = os.environ.get('PB_URL', 'http://89.167.121.193:8090').rstrip('/')
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

RUN_ID = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')

CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)

# ── Load schema ───────────────────────────────────────────────────────────────

schema   = json.loads(SCHEMA_FILE.read_text('utf-8'))
FIELDS   = {f['field_id']: f for f in schema['fields']}
DOMAINS  = {d['domain_id']: d for d in schema['domains']}
VC_NAMES = {vc['id']: vc['name'] for vc in schema['value_chains']}

# ── PocketBase (public read — no auth needed) ─────────────────────────────────

def pb_get(path):
    url = f'{PB_URL}/{path.lstrip("/")}'
    try:
        with urllib.request.urlopen(url) as r:
            return json.loads(r.read())
    except urllib.error.URLError as e:
        sys.exit(f'PocketBase unreachable at {PB_URL}: {e}')

def fetch_datapoints(value_chain_id: str) -> list[dict]:
    """Fetch all approved datapoints for one chain from PocketBase."""
    items, page, total_pages = [], 1, 1
    while page <= total_pages:
        result = pb_get(
            f'/api/collections/diagnostic_datapoints/records'
            f'?filter=(value_chain_id="{value_chain_id}"'
            f'&&approval_status!="pending_approval"'
            f'&&approval_status!="rejected")'
            f'&perPage=500&page={page}&sort=field_id'
        )
        items.extend(result.get('items', []))
        total_pages = result.get('totalPages', 1)
        page += 1
    return items

def fetch_chains_with_data() -> list[str]:
    """Return VC IDs that have at least one approved datapoint."""
    result = pb_get(
        '/api/collections/diagnostic_datapoints/records'
        '?filter=(approval_status!="pending_approval"&&approval_status!="rejected")'
        '&perPage=1&fields=value_chain_id'
    )
    if result.get('totalItems', 0) == 0:
        return []
    # Fetch all to get unique chain IDs
    result = pb_get(
        '/api/collections/diagnostic_datapoints/records'
        '?filter=(approval_status!="pending_approval"&&approval_status!="rejected")'
        f'&perPage=500&fields=value_chain_id'
    )
    return sorted(set(dp['value_chain_id'] for dp in result.get('items', [])))

# ── Claude API ────────────────────────────────────────────────────────────────

def claude(system_prompt: str, user_prompt: str,
           model: str = 'claude-sonnet-4-6') -> str:
    if not ANTHROPIC_API_KEY:
        sys.exit('ERROR: ANTHROPIC_API_KEY not set.')
    payload = {
        'model': model,
        'max_tokens': 16000,
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

# ── Build the synthesis prompt ────────────────────────────────────────────────

SYSTEM_PROMPT = textwrap.dedent("""
You are the MTIC Synthesis Agent for Uganda's Industrial Diagnostic Study,
commissioned by the Ministry of Trade, Industry and Cooperatives (MTIC) under
the Uganda-UNIDO Programme for Country Partnership (PCP).

Your job is to write one chapter of the diagnostic report for a given value chain,
strictly from the populated datapoints provided. Every analytical claim must trace
directly to a populated datapoint. You do not introduce external knowledge.

WRITING RULES:
1. Write at the same standard as a World Bank or UNIDO sector diagnostic — dense,
   precise, evidence-based. Data tables where appropriate.
2. For every claim built on a field where evidence_required=true, cite the raw_source
   inline: (Source, year) or footnote style.
3. If a field value is "not_available", note the gap explicitly in the relevant section
   rather than skipping it — gaps are findings too.
4. Use the synthesis_guidance in each field's metadata to decide how to frame it.
5. Produce the Priority Action Matrix (from D9.* fields) and Investment Portfolio
   (from D10.* fields) as structured tables.
6. The Tenfold Growth Strategy governs all analysis. Every constraint and recommendation
   must be framed in terms of what it means for Uganda achieving tenfold growth by 2040.
7. Write in British English. Use USD for all financial figures unless UGX is specified.
8. Do not pad. Do not repeat. Say it once, precisely.

OUTPUT FORMAT:
Return the full chapter as Markdown. Use the heading structure:
# Chapter: <Chain Name>
## <Domain name> (one H2 per domain with data)
### <Sub-section> (optional H3 for major sub-topics)
Finish with:
## Priority Action Matrix  (table from D9.*)
## Investment Portfolio    (table from D10.*)
## Data Gaps & Limitations (list all not_available mandatory fields)

Do not include front-matter or meta-text — start directly with the # heading.
""").strip()

def build_user_prompt(vc_id: str, vc_name: str, datapoints: list[dict]) -> str:
    # Group datapoints by domain
    by_domain: dict[str, list[dict]] = {}
    for dp in datapoints:
        fid = dp.get('field_id', '')
        domain = fid.split('.')[0] if '.' in fid else 'UNKNOWN'
        by_domain.setdefault(domain, []).append(dp)

    # Build data section — domain by domain
    data_lines = []
    for domain_id in sorted(by_domain):
        domain_name = DOMAINS.get(domain_id, {}).get('name', domain_id)
        data_lines.append(f'\n### DOMAIN {domain_id}: {domain_name}')
        for dp in sorted(by_domain[domain_id], key=lambda x: x.get('field_id', '')):
            fid   = dp.get('field_id', '')
            field = FIELDS.get(fid, {})
            data_lines.append(f"""
FIELD {fid} — {field.get('label', '')}
  synthesis_guidance : {field.get('synthesis_guidance', '')}
  evidence_required  : {field.get('evidence_required', False)}
  value              : {dp.get('value', 'not_available')}
  raw_source         : {dp.get('raw_source', '')}
  reporting_year     : {dp.get('reporting_year', '')}
  confidence         : {dp.get('confidence', '')}
  collection_notes   : {dp.get('collection_notes', '')}""")

    # List mandatory gaps
    populated_fids = {dp['field_id'] for dp in datapoints
                      if dp.get('value') and dp.get('value') != 'not_available'}
    mandatory_gaps = [
        f"{fid} — {FIELDS[fid]['label']}"
        for fid in (f['field_id'] for f in schema['fields']
                    if f['required_level'] == 'mandatory')
        if fid not in populated_fids and fid in FIELDS
    ]

    return textwrap.dedent(f"""
VALUE CHAIN: {vc_name} ({vc_id})
SYNTHESIS RUN: {RUN_ID}

=== POPULATED DATAPOINTS ===
{"".join(data_lines)}

=== MANDATORY FIELDS WITH NO DATA ({len(mandatory_gaps)}) ===
{chr(10).join(mandatory_gaps) if mandatory_gaps else "None — all mandatory fields populated."}

Write the full diagnostic chapter for {vc_name}.
""").strip()

# ── Write chapter ─────────────────────────────────────────────────────────────

def synthesise(vc_id: str) -> Path:
    vc_name = VC_NAMES.get(vc_id)
    if not vc_name:
        sys.exit(f'Unknown value chain ID: {vc_id}')

    print(f'\n── Synthesising {vc_name} ({vc_id}) ──')

    datapoints = fetch_datapoints(vc_id)
    if not datapoints:
        print(f'  No approved datapoints in PocketBase for {vc_id}. Skipping.')
        return None

    print(f'  {len(datapoints)} datapoints loaded from PocketBase')

    user_prompt = build_user_prompt(vc_id, vc_name, datapoints)
    print(f'  Calling Claude (claude-sonnet-4-6)...')
    chapter_md  = claude(SYSTEM_PROMPT, user_prompt)

    # Prepend generation metadata as a hidden comment
    header = textwrap.dedent(f"""\
    <!-- GENERATED by synthesis_agent.py  run={RUN_ID}
         Chain: {vc_name} ({vc_id})
         Datapoints: {len(datapoints)}
         Do not edit manually — re-run the agent to regenerate. -->

    """)
    output = header + chapter_md

    out_path = CHAPTERS_DIR / f'{vc_id}_diagnostic.md'
    out_path.write_text(output, encoding='utf-8')
    print(f'  Written → {out_path.relative_to(ROOT)}')
    return out_path

# ── Main ──────────────────────────────────────────────────────────────────────

def run(vc_ids: list[str] | None = None):
    print(f'\n══ MTIC Synthesis Agent  run={RUN_ID} ══')

    if vc_ids is None:
        vc_ids = fetch_chains_with_data()
        if not vc_ids:
            print('  No approved datapoints found in PocketBase.')
            print('  Run the ingestion agent first: python agents/ingestion_agent.py')
            return

    written = []
    for vc_id in vc_ids:
        path = synthesise(vc_id)
        if path:
            written.append(path)

    print(f'\n══ Done — {len(written)} chapter(s) written ══')
    for p in written:
        print(f'  {p.relative_to(ROOT)}')

    if written:
        print('\n  Next: run the review agent to validate.')
        print('  python agents/review_agent.py')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='MTIC Synthesis Agent')
    parser.add_argument('--vc', nargs='+',
                        help='Value chain IDs to synthesise (e.g. VC01 VC02). '
                             'Default: all chains with approved data.')
    args = parser.parse_args()
    run(vc_ids=args.vc)
