"""
One-time migration: extract hardcoded data from sources-of-truth.html
into the CSV/JSON source files that generate_dashboard.py will consume.

Run once from the repo root:
    python scripts/extract_to_csv.py
"""

import re, json, csv, os
from pathlib import Path

HTML = Path('report/sources-of-truth.html')
OUT  = Path('data/dashboard')
OUT.mkdir(parents=True, exist_ok=True)

src = HTML.read_text(encoding='utf-8')

# ── 1. Extract FACTORIES array ────────────────────────────────────────────────
# Grab the JS source between "const FACTORIES=[" and the matching "];"
m = re.search(r'const FACTORIES\s*=\s*(\[[\s\S]*?\n\];)', src)
if not m:
    raise RuntimeError('FACTORIES array not found')

factories_js = m.group(1)

# Convert JS object literal → JSON:
#   - quote unquoted keys
#   - single → double quotes (carefully, preserving apostrophes in values)
def js_to_json(js):
    # quote bare keys: word:  →  "word":
    js = re.sub(r'(\b[a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'"\1":', js)
    # swap single-quoted strings to double-quoted (handle escaped \' inside)
    def sq(m):
        inner = m.group(1).replace('"', '\\"').replace("\\'", "'")
        return f'"{inner}"'
    js = re.sub(r"'((?:[^'\\]|\\.)*)'", sq, js)
    # strip trailing commas before ] or }
    js = re.sub(r',(\s*[}\]])', r'\1', js)
    return js

factories = json.loads(js_to_json(factories_js))
print(f'Extracted {len(factories)} factories')

fields = ['name','chain','lat','lng','loc','products',
          'capacity_installed','capacity_utilised','employees',
          'est','ownership','exports']

with open(OUT / 'factories.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    w.writeheader()
    for fac in factories:
        w.writerow({k: fac.get(k, '—') for k in fields})

print(f'Written {OUT}/factories.csv')

# ── 2. Extract chains array → chains.json ─────────────────────────────────────
m2 = re.search(r'const chains\s*=\s*(\[[\s\S]*?\n\]);', src)
if not m2:
    raise RuntimeError('chains array not found')

chains_js = m2.group(1)
try:
    chains = json.loads(js_to_json(chains_js))
    print(f'Extracted {len(chains)} chains')
    with open(OUT / 'chains.json', 'w', encoding='utf-8') as f:
        json.dump(chains, f, indent=2, ensure_ascii=False)
    print(f'Written {OUT}/chains.json')
except json.JSONDecodeError as e:
    print(f'WARNING: chains JSON parse error ({e}) — writing raw JS for manual fix')
    (OUT / 'chains_raw.js').write_text(chains_js, encoding='utf-8')

# ── 3. Extract CHAIN_COLORS → chain_colors.json ───────────────────────────────
m3 = re.search(r'const CHAIN_COLORS\s*=\s*(\{[\s\S]*?\})\s*;', src)
if m3:
    colors_js = m3.group(1)
    colors = json.loads(js_to_json(colors_js))
    with open(OUT / 'chain_colors.json', 'w', encoding='utf-8') as f:
        json.dump(colors, f, indent=2, ensure_ascii=False)
    print(f'Written {OUT}/chain_colors.json  ({len(colors)} chains)')

print('\nDone. Check data/dashboard/ for output files.')
