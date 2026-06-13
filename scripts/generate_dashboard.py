#!/usr/bin/env python3
"""
Generate report/sources-of-truth.html from template + data files.

Usage:
    python scripts/generate_dashboard.py

Inputs (all under data/dashboard/):
    overview_kpis.csv     6 KPI cards + progress bar data
    chain_summary.csv     9-row chain overview table
    chains.json           Full chain status + value-chain map data
    chain_colors.json     Chain name → hex colour
    factories.csv         89 manufacturing facilities

Output:
    report/sources-of-truth.html   (overwrites the live dashboard)
"""

import csv, json, sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
DATA   = ROOT / 'data' / 'dashboard'
TMPL   = ROOT / 'report' / 'sources-of-truth.template.html'
OUTPUT = ROOT / 'report' / 'sources-of-truth.html'

# ── Load ──────────────────────────────────────────────────────────────────────

def load_csv(name):
    with open(DATA / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

overview_kpis = load_csv('overview_kpis.csv')
chain_summary = load_csv('chain_summary.csv')
chains        = json.loads((DATA / 'chains.json').read_text('utf-8'))
chain_colors  = json.loads((DATA / 'chain_colors.json').read_text('utf-8'))
factories_csv = load_csv('factories.csv')

# ── HTML generators ───────────────────────────────────────────────────────────

TAG_COLOR = {
    'green': 'tag-green',
    'amber': 'tag-yellow',
    'red':   'tag-red',
    'blue':  'tag-blue',
}

def esc(s):
    """HTML-escape a plain-text value."""
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
    """Escape value for a JS single-quoted string literal."""
    return str(v).replace('\\', '\\\\').replace("'", "\\'")

def factories_js():
    lines = ['const FACTORIES=[']
    for i, f in enumerate(factories_csv):
        comma = '' if i == len(factories_csv) - 1 else ','
        try:
            lat = float(f['lat'])
            lng = float(f['lng'])
        except (ValueError, KeyError):
            lat, lng = 0, 0
        fields = ','.join(
            f"{k}:'{js_str(f.get(k, '—'))}'"
            for k in ['loc','products','capacity_installed',
                      'capacity_utilised','employees','est','ownership','exports']
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
    # JSON is valid JS — use compact pretty-print
    serialised = json.dumps(chains, ensure_ascii=False, indent=2)
    return f'const chains = {serialised};'

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
