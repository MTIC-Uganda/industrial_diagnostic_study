#!/usr/bin/env python3
"""
Generate report/sources-of-truth.html from template + data.

Data source (auto-detected):
  • If SUPABASE_URL + SUPABASE_ANON_KEY are set → fetch from Supabase (CI/prod)
  • Otherwise → fall back to local CSV/JSON files in data/dashboard/ (local dev)

Usage:
    python scripts/generate_dashboard.py

Template:
    report/sources-of-truth.template.html   (5 placeholder markers)

Output:
    report/sources-of-truth.html
"""

import csv, json, os, sys, urllib.request, urllib.error
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
DATA   = ROOT / 'data' / 'dashboard'
TMPL   = ROOT / 'report' / 'sources-of-truth.template.html'
OUTPUT = ROOT / 'report' / 'sources-of-truth.html'

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SUPABASE_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)

# ── Data loading ──────────────────────────────────────────────────────────────

def supabase_get(table, select='*', order=None):
    url = f'{SUPABASE_URL}/rest/v1/{table}?select={select}'
    if order:
        url += f'&order={order}'
    req = urllib.request.Request(url, headers={
        'apikey':        SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
    })
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f'Supabase error {e.code} on {table}: {e.read().decode()[:300]}')

def load_csv(name):
    with open(DATA / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

if USE_SUPABASE:
    print(f'Data source: Supabase ({SUPABASE_URL})')
    raw_chains    = supabase_get('value_chains', order='display_order')
    raw_kpis      = supabase_get('kpi_indicators', order='display_order')
    raw_facilities = supabase_get('facilities', order='chain_id,name')

    # Reshape Supabase rows into the same shape the generators expect
    chain_summary = [{
        'chain':           r['name'],
        'key_import_2024': r.get('key_import_2024') or '',
        'key_export_2024': r.get('key_export_2024') or '',
        'position_tag':    r.get('position_tag') or '',
        'position_color':  r.get('position_color') or 'amber',
        'target_2040':     r.get('target_2040') or '',
        'priority_tag':    r.get('priority_tag') or '',
        'priority_color':  r.get('priority_color') or 'blue',
    } for r in raw_chains]

    overview_kpis = [{
        'id':            r['id'],
        'label':         r['label'],
        'current_value': r.get('current_value') or '',
        'sub_value':     r.get('sub_value') or '',
    } for r in raw_kpis]

    chain_colors = {r['name']: r['color'] for r in raw_chains}

    # Rebuild chains array (matches original JS structure)
    chains = [{
        'id':   r['id'],
        'name': r['name'],
        'map': {
            'title':  r.get('map_title') or '',
            'desc':   r.get('map_description') or '',
            'phases': r.get('map_phases') or [],
            'gap':    r.get('map_gap') or '',
        },
        'status': {
            'current':     r.get('status_current') or [],
            'companies':   r.get('status_companies') or [],
            'constraints': r.get('status_constraints') or [],
            'priorities':  r.get('status_priorities') or [],
            'proj':        r.get('status_proj') or {},
        },
    } for r in raw_chains]

    # Rebuild factories list (matches original JS structure)
    chain_id_to_name = {r['id']: r['name'] for r in raw_chains}
    factories_list = [{
        'name':               f['name'],
        'chain':              chain_id_to_name.get(f['chain_id'], ''),
        'lat':                f.get('lat') or 0,
        'lng':                f.get('lng') or 0,
        'loc':                f.get('location') or '',
        'products':           f.get('products') or '',
        'capacity_installed': f.get('capacity_installed') or '',
        'capacity_utilised':  f.get('capacity_utilised') or '',
        'employees':          f.get('employees') or '',
        'est':                f.get('established') or '',
        'ownership':          f.get('ownership') or '',
        'exports':            f.get('exports') or '',
    } for f in raw_facilities]

else:
    print('Data source: local files (data/dashboard/)')
    chain_summary  = load_csv('chain_summary.csv')
    overview_kpis  = load_csv('overview_kpis.csv')
    chains         = json.loads((DATA / 'chains.json').read_text('utf-8'))
    chain_colors   = json.loads((DATA / 'chain_colors.json').read_text('utf-8'))
    factories_list = load_csv('factories.csv')
    # Rename CSV columns to match JS field names
    for f in factories_list:
        f['loc'] = f.pop('loc', f.get('loc', ''))

# ── HTML generators ───────────────────────────────────────────────────────────

TAG_COLOR = {'green': 'tag-green', 'amber': 'tag-yellow', 'red': 'tag-red', 'blue': 'tag-blue'}

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def kpi_cards_html():
    parts = []
    for r in overview_kpis:
        parts.append(
            f'<div class="card">'
            f'<h3>{esc(r["label"])}</h3>'
            f'<div class="value">{esc(r["current_value"])}</div>'
            f'<div class="sub-value">{r["sub_value"]}</div>'
            f'</div>'
        )
    return '\n    '.join(parts)

def chain_table_rows_html():
    rows = []
    for r in chain_summary:
        pos_cls = TAG_COLOR.get(r['position_color'], 'tag-yellow')
        pri_cls = TAG_COLOR.get(r['priority_color'], 'tag-blue')
        rows.append(
            f'<tr>'
            f'<td><strong>{esc(r["chain"])}</strong></td>'
            f'<td>{esc(r["key_import_2024"])}</td>'
            f'<td>{esc(r["key_export_2024"])}</td>'
            f'<td><span class="tag {pos_cls}">{esc(r["position_tag"])}</span></td>'
            f'<td>{esc(r["target_2040"])}</td>'
            f'<td><span class="tag {pri_cls}">{esc(r["priority_tag"])}</span></td>'
            f'</tr>'
        )
    return '\n        '.join(rows)

# ── JS generators ─────────────────────────────────────────────────────────────

def js_str(v):
    return str(v).replace('\\', '\\\\').replace("'", "\\'")

def factories_js():
    lines = ['const FACTORIES=[']
    for i, f in enumerate(factories_list):
        comma = '' if i == len(factories_list) - 1 else ','
        try:
            lat = float(f.get('lat') or 0)
            lng = float(f.get('lng') or 0)
        except (ValueError, TypeError):
            lat = lng = 0
        loc = f.get('loc') or f.get('location') or ''
        fields = ','.join(
            f"{k}:'{js_str(f.get(fk,''))}'"
            for k, fk in [
                ('loc', 'loc'), ('products','products'),
                ('capacity_installed','capacity_installed'),
                ('capacity_utilised','capacity_utilised'),
                ('employees','employees'), ('est','est'),
                ('ownership','ownership'), ('exports','exports'),
            ]
        )
        lines.append(
            f"  {{name:'{js_str(f['name'])}',chain:'{js_str(f['chain'])}'"
            f",lat:{lat},lng:{lng},{fields}}}{comma}"
        )
    lines.append('];')
    return '\n'.join(lines)

def chain_colors_js():
    items = list(chain_colors.items())
    body  = ',\n'.join(f"  '{js_str(k)}':'{v}'" for k, v in items)
    return f'const CHAIN_COLORS={{\n{body}\n}};'

def chains_js():
    return 'const chains = ' + json.dumps(chains, ensure_ascii=False, indent=2) + ';'

# ── Assemble ──────────────────────────────────────────────────────────────────

if not TMPL.exists():
    sys.exit(f'ERROR: template not found: {TMPL}\nRun scripts/create_template.py first.')

tmpl = TMPL.read_text('utf-8')

replacements = {
    '<!--%%OVERVIEW_KPIS_CARDS%%-->': kpi_cards_html(),
    '<!--%%CHAIN_SUMMARY_ROWS%%-->':  chain_table_rows_html(),
    '/*%%CHAINS_DATA%%*/':            chains_js(),
    '/*%%CHAIN_COLORS_DATA%%*/':      chain_colors_js(),
    '/*%%FACTORIES_DATA%%*/':         factories_js(),
}

out = tmpl
for marker, content in replacements.items():
    if marker not in out:
        print(f'WARNING: marker not found in template: {marker}', file=sys.stderr)
    out = out.replace(marker, content, 1)

OUTPUT.write_text(out, 'utf-8')
print(f'Generated {OUTPUT}  ({len(out):,} bytes, {out.count(chr(10)):,} lines)')
