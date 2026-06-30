#!/usr/bin/env python3
"""
Generate app/explorer/src/data/ironSteel.js from PocketBase + data/dashboard/explorer/*.

2026-06-30 dashboard data-source audit: this file used to be hand-written,
hardcoded JS -- the one part of the whole platform with no PocketBase path
at all. From now on PocketBase (explorer_products, explorer_categories,
explorer_trade_hs4, explorer_raw_material_trade, explorer_phase_producers,
explorer_product_firms, explorer_input_keywords -- see db/pb_setup_explorer.py)
is the canonical source, and this script regenerates the JS data file the
Explorer's vite build bundles, the same way scripts/generate_dashboard.py
regenerates the main dashboard from PocketBase.

Data source (auto-detected):
  - If PB_URL is set  -> fetch from PocketBase (CI / prod)
  - Otherwise         -> fall back to data/dashboard/explorer/*.json|csv

Usage:
    python scripts/generate_explorer_data.py

Output:
    app/explorer/src/data/ironSteel.js
"""

import csv, json, os, sys, urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
DATA   = ROOT / 'data' / 'dashboard' / 'explorer'
OUTPUT = ROOT / 'app' / 'explorer' / 'src' / 'data' / 'ironSteel.js'

PB_URL = os.environ.get('PB_URL', '').rstrip('/')
USE_POCKETBASE = bool(PB_URL)

# ── Data loading ──────────────────────────────────────────────────────────────

def pb_get(collection, sort=None):
    items, page = [], 1
    while True:
        url = f'{PB_URL}/api/collections/{collection}/records?perPage=500&page={page}'
        if sort:
            url += f'&sort={urllib.parse.quote(sort)}'
        try:
            with urllib.request.urlopen(url) as r:
                payload = json.loads(r.read())
        except Exception as e:
            print(f'  Cannot reach PocketBase for {collection}: {e}')
            return None
        items.extend(payload.get('items', []))
        if page >= payload.get('totalPages', 1) or not payload.get('items'):
            break
        page += 1
    return items

def load_csv(name):
    with open(DATA / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_json(name):
    return json.loads((DATA / name).read_text('utf-8'))

def _pb_or_local(collection, sort, local_loader):
    rows = pb_get(collection, sort=sort) if USE_POCKETBASE else None
    if rows:
        return rows
    if USE_POCKETBASE:
        print(f'  (no {collection} data in PocketBase yet — using local fallback)')
    return local_loader()

products_rows       = _pb_or_local('explorer_products', 'display_order', lambda: load_json('products.json'))
categories_rows      = _pb_or_local('explorer_categories', 'display_order', lambda: load_json('categories.json'))
trade_hs4_rows        = _pb_or_local('explorer_trade_hs4', 'display_order', lambda: load_csv('trade_hs4.csv'))
raw_material_rows     = _pb_or_local('explorer_raw_material_trade', 'display_order', lambda: load_csv('raw_material_trade.csv'))
phase_producers_rows  = _pb_or_local('explorer_phase_producers', 'display_order', lambda: load_json('phase_producers.json'))
product_firms_rows    = _pb_or_local('explorer_product_firms', 'display_order', lambda: load_json('product_firms.json'))
input_keywords_rows   = _pb_or_local('explorer_input_keywords', 'display_order', lambda: load_json('input_keywords.json'))

if not products_rows:
    sys.exit('ERROR: no explorer_products data available (PocketBase empty/unreachable and no local fallback found).')

# ── Reshape into the JS module's data shapes ───────────────────────────────────

PRODUCTS = {}
for r in products_rows:
    chains = r['chains']
    if isinstance(chains, str):
        chains = json.loads(chains)
    PRODUCTS[r['slug']] = {
        'id': r['slug'], 'name': r['name'], 'category': r['category'],
        'color': r['color'], 'description': r['description'], 'chains': chains,
    }

CATEGORIES = []
for r in categories_rows:
    products = r['products']
    if isinstance(products, str):
        products = json.loads(products)
    CATEGORIES.append({'name': r['name'], 'color': r['color'], 'products': products})

TRADE_HS4 = {}
for r in trade_hs4_rows:
    TRADE_HS4[r['hs4_code']] = {
        'desc': r['desc'], 'year': int(float(r['year'])),
        'imports': {'uganda': float(r['imports_uganda']), 'eac': float(r['imports_eac'])},
        'exports': {'uganda': float(r['exports_uganda']), 'eac': float(r['exports_eac'])},
    }

PRODUCT_HS4 = {r['slug']: r['hs4_code'] for r in products_rows if r.get('hs4_code')}

RAW_MATERIAL_TRADE = {}
RAW_MATERIAL_PHASE = {}
for r in raw_material_rows:
    RAW_MATERIAL_TRADE[r['item_name']] = {
        'desc': r['desc'], 'year': int(float(r['year'])),
        'imports': {'uganda': float(r['imports_uganda']), 'eac': float(r['imports_eac'])},
        'exports': {'uganda': float(r['exports_uganda']), 'eac': float(r['exports_eac'])},
    }
    if r.get('phase'):
        RAW_MATERIAL_PHASE[r['item_name']] = r['phase']

PHASE_PRODUCERS = {}
PHASE_SOURCE = ''
for r in phase_producers_rows:
    examples = r['examples']
    if isinstance(examples, str):
        examples = json.loads(examples)
    PHASE_PRODUCERS[r['phase']] = {'count': int(float(r['count'])), 'label': r['label'], 'examples': examples}
    PHASE_SOURCE = r.get('source') or PHASE_SOURCE

PRODUCT_FIRMS = {}
for r in product_firms_rows:
    firms = r['firms']
    if isinstance(firms, str):
        firms = json.loads(firms) if firms else []
    phase_context = r.get('phase_context')
    if isinstance(phase_context, str):
        phase_context = json.loads(phase_context) if phase_context else None
    entry = {'status': r['status'], 'firms': firms, 'note': r.get('note') or ''}
    if phase_context:
        entry['phaseContext'] = phase_context
    PRODUCT_FIRMS[r['product_slug']] = entry

INPUT_KEYWORD_HS4, INPUT_KEYWORD_PHASE = [], []
for r in input_keywords_rows:
    row = {'source': r['pattern_source'], 'flags': r['pattern_flags'], 'value': r['target_value']}
    (INPUT_KEYWORD_HS4 if r['target_type'] == 'hs4' else INPUT_KEYWORD_PHASE).append(row)

# ── Emit JS ──────────────────────────────────────────────────────────────────

def js_obj(value):
    """json.dumps output is valid JS object/array literal syntax."""
    return json.dumps(value, indent=2, ensure_ascii=False)

def js_regex_array(rows, target_key):
    lines = ['[']
    for r in rows:
        lines.append(f'  {{ pattern: /{r["source"]}/{r["flags"]}, {target_key}: {json.dumps(r["value"])} }},')
    lines.append(']')
    return '\n'.join(lines)

out = f'''// GENERATED FILE — do not hand-edit. Regenerate with:
//   python scripts/generate_explorer_data.py
// Source of truth: PocketBase (explorer_products, explorer_categories,
// explorer_trade_hs4, explorer_raw_material_trade, explorer_phase_producers,
// explorer_product_firms, explorer_input_keywords — see db/pb_setup_explorer.py).
// Local fallback: data/dashboard/explorer/*.

const PRODUCTS = {js_obj(PRODUCTS)};

const CATEGORIES = {js_obj(CATEGORIES)};

const TRADE_HS4 = {js_obj(TRADE_HS4)};

const PRODUCT_HS4 = {js_obj(PRODUCT_HS4)};

const RAW_MATERIAL_TRADE = {js_obj(RAW_MATERIAL_TRADE)};

const RAW_MATERIAL_PHASE = {js_obj(RAW_MATERIAL_PHASE)};

const PHASE_PRODUCERS = {js_obj(PHASE_PRODUCERS)};

const PHASE_SOURCE = {json.dumps(PHASE_SOURCE)};

const PRODUCT_FIRMS = {js_obj(PRODUCT_FIRMS)};

// Keyword -> HS-4 group, for matching free-text "Inputs" tab line items
// to the same trade data used for raw materials and products above.
const INPUT_KEYWORD_HS4 = {js_regex_array(INPUT_KEYWORD_HS4, 'hs4')};

function matchInputTrade(text) {{
  const hit = INPUT_KEYWORD_HS4.find((k) => k.pattern.test(text));
  return hit ? TRADE_HS4[hit.hs4] : null;
}}

// Keyword -> verified Phase, for the same free-text "Inputs" line items.
const INPUT_KEYWORD_PHASE = {js_regex_array(INPUT_KEYWORD_PHASE, 'phase')};

function matchInputPhase(text) {{
  const hit = INPUT_KEYWORD_PHASE.find((k) => k.pattern.test(text));
  return hit ? PHASE_PRODUCERS[hit.phase] : null;
}}

export {{ PRODUCTS, CATEGORIES, TRADE_HS4, PRODUCT_HS4, RAW_MATERIAL_TRADE, matchInputTrade, matchInputPhase, PRODUCT_FIRMS, PHASE_PRODUCERS, PHASE_SOURCE, RAW_MATERIAL_PHASE }};
'''

if USE_POCKETBASE:
    print(f'Data source: PocketBase ({PB_URL})')
else:
    print('Data source: local files (data/dashboard/explorer/)')

OUTPUT.write_text(out, 'utf-8')
print(f'Generated {OUTPUT}  ({len(out):,} bytes, {len(PRODUCTS)} products)')
