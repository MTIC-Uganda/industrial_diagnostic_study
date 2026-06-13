#!/usr/bin/env python3
"""
Generate report/sources-of-truth.html from template + data.

Data source (auto-detected):
  • If PB_URL is set  →  fetch from PocketBase (CI / prod)
  • Otherwise         →  fall back to local CSV/JSON files in data/dashboard/

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

PB_URL      = os.environ.get('PB_URL', '').rstrip('/')
USE_POCKETBASE = bool(PB_URL)

# ── Data loading ──────────────────────────────────────────────────────────────

def pb_get(collection, sort=None, per_page=500):
    """Fetch all records from a PocketBase collection (public read)."""
    url = f'{PB_URL}/api/collections/{collection}/records?perPage={per_page}'
    if sort:
        url += f'&sort={sort}'
    try:
        with urllib.request.urlopen(url) as r:
            return json.loads(r.read()).get('items', [])
    except urllib.error.HTTPError as e:
        sys.exit(f'PocketBase error {e.code} fetching {collection}: {e.read().decode()[:200]}')
    except Exception as e:
        sys.exit(f'Cannot reach PocketBase at {PB_URL}: {e}')

def load_csv(name):
    with open(DATA / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

if USE_POCKETBASE:
    print(f'Data source: PocketBase ({PB_URL})')

    raw_chains    = pb_get('value_chains', sort='display_order')
    raw_kpis      = pb_get('kpi_indicators', sort='display_order')
    raw_facilities = pb_get('facilities', sort='chain_name,name')

    # Reshape for the generators below
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
        'id':            r['slug'],
        'label':         r['label'],
        'current_value': r.get('current_value') or '',
        'sub_value':     r.get('sub_value') or '',
    } for r in raw_kpis]

    chain_colors = {r['name']: r['color'] for r in raw_chains}

    chains = [{
        'id':   r['slug'],
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

    factories_list = [{
        'name':               f['name'],
        'chain':              f.get('chain_name') or '',
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
    raw_fac        = load_csv('factories.csv')
    factories_list = [{**f, 'loc': f.get('loc', '')} for f in raw_fac]

# ── HTML generators ───────────────────────────────────────────────────────────

TAG_COLOR = {'green':'tag-green','amber':'tag-yellow','red':'tag-red','blue':'tag-blue'}

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
        pc = TAG_COLOR.get(r['position_color'], 'tag-yellow')
        rc = TAG_COLOR.get(r['priority_color'], 'tag-blue')
        rows.append(
            f'<tr>'
            f'<td><strong>{esc(r["chain"])}</strong></td>'
            f'<td>{esc(r["key_import_2024"])}</td>'
            f'<td>{esc(r["key_export_2024"])}</td>'
            f'<td><span class="tag {pc}">{esc(r["position_tag"])}</span></td>'
            f'<td>{esc(r["target_2040"])}</td>'
            f'<td><span class="tag {rc}">{esc(r["priority_tag"])}</span></td>'
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
        fields = ','.join(
            f"{k}:'{js_str(f.get(fk,''))}'"
            for k, fk in [
                ('loc','loc'),('products','products'),
                ('capacity_installed','capacity_installed'),
                ('capacity_utilised','capacity_utilised'),
                ('employees','employees'),('est','est'),
                ('ownership','ownership'),('exports','exports'),
            ]
        )
        lines.append(
            f"  {{name:'{js_str(f['name'])}',chain:'{js_str(f['chain'])}'"
            f",lat:{lat},lng:{lng},{fields}}}{comma}"
        )
    lines.append('];')
    return '\n'.join(lines)

def chain_colors_js():
    body = ',\n'.join(f"  '{js_str(k)}':'{v}'" for k, v in chain_colors.items())
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
        print(f'WARNING: marker not found: {marker}', file=sys.stderr)
    out = out.replace(marker, content, 1)

OUTPUT.write_text(out, 'utf-8')
print(f'Generated {OUTPUT}  ({len(out):,} bytes, {out.count(chr(10)):,} lines)')
