#!/usr/bin/env python3
"""
One-time script: create sources-of-truth.template.html from the live HTML.

Replaces the 5 data-driven sections with placeholder markers so that
generate_dashboard.py can regenerate them from the CSV/JSON data files.

Run from repo root:
    python scripts/create_template.py

DO NOT run this again after the template has been edited manually — it will
overwrite your edits.
"""

import re, sys
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
SRC    = ROOT / 'report' / 'sources-of-truth.html'
OUTPUT = ROOT / 'report' / 'sources-of-truth.template.html'

if OUTPUT.exists():
    print(f'Template already exists: {OUTPUT}')
    print('Delete it first if you want to recreate it.')
    sys.exit(0)

html = SRC.read_text('utf-8')

# ── 1. KPI cards (children of <div class="kpi-grid">) ────────────────────────
# Replace everything between the opening kpi-grid div and its closing tag
html = re.sub(
    r'(<div class="kpi-grid">)\n(.*?)(\n  </div>\n\n  <div class="card" style="margin-bottom:24px">)',
    r'\1\n    <!--%%OVERVIEW_KPIS_CARDS%%-->\n  </div>\n\n  <div class="card" style="margin-bottom:24px">',
    html,
    count=1,
    flags=re.DOTALL,
)

# ── 2. Chain summary table rows (inside <tbody>) ──────────────────────────────
html = re.sub(
    r'(<tbody>)\n(.*?)(\n      </tbody>)',
    r'\1\n        <!--%%CHAIN_SUMMARY_ROWS%%-->\n      </tbody>',
    html,
    count=1,
    flags=re.DOTALL,
)

# ── 3. chains JS variable declaration ────────────────────────────────────────
# const chains = [ ... ]; — ends at the first standalone ];
html = re.sub(
    r'const chains = \[[\s\S]*?\n\];',
    '/*%%CHAINS_DATA%%*/',
    html,
    count=1,
)

# ── 4. CHAIN_COLORS JS variable declaration ───────────────────────────────────
html = re.sub(
    r'const CHAIN_COLORS=\{[\s\S]*?\};',
    '/*%%CHAIN_COLORS_DATA%%*/',
    html,
    count=1,
)

# ── 5. FACTORIES JS variable declaration ─────────────────────────────────────
html = re.sub(
    r'const FACTORIES=\[[\s\S]*?\n\];',
    '/*%%FACTORIES_DATA%%*/',
    html,
    count=1,
)

# ── Verify all markers are present ────────────────────────────────────────────
markers = [
    '<!--%%OVERVIEW_KPIS_CARDS%%-->',
    '<!--%%CHAIN_SUMMARY_ROWS%%-->',
    '/*%%CHAINS_DATA%%*/',
    '/*%%CHAIN_COLORS_DATA%%*/',
    '/*%%FACTORIES_DATA%%*/',
]
missing = [m for m in markers if m not in html]
if missing:
    print('ERROR: these markers were not inserted:', missing)
    sys.exit(1)

OUTPUT.write_text(html, 'utf-8')
print(f'Created {OUTPUT}  ({len(html):,} bytes)')
print('Markers inserted:')
for m in markers:
    print(f'  ✓ {m}')
