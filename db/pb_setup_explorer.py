#!/usr/bin/env python3
"""
One-time setup: create PocketBase collections and seed the Value Chain
Explorer's data (currently Iron & Steel only).

Mirrors db/pb_setup.py's structure and conventions exactly -- separate
script because the Explorer is a separate app (app/explorer/), not part of
the sources-of-truth dashboard.

2026-06-30 dashboard data-source audit: app/explorer/src/data/ironSteel.js
was hand-written, hardcoded JS with no PocketBase path at all -- the one
section of the whole platform with no database wiring. From now on,
PocketBase is the canonical source and ironSteel.js (and any future
per-chain data file) is generated from it by
scripts/generate_explorer_data.py, the same way generate_dashboard.py
generates the main dashboard.

Usage:
    $env:PB_URL           = "http://89.167.121.193:8090"
    $env:PB_ADMIN_EMAIL   = "admin@mtic.go.ug"
    $env:PB_ADMIN_PASSWORD = "your-admin-password"
    python db/pb_setup_explorer.py

Re-running is safe -- existing collections and records are updated, not duplicated.
"""

import csv, json, os, re, sys
import urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'dashboard' / 'explorer'

PB_URL    = os.environ.get('PB_URL', 'http://89.167.121.193:8090').rstrip('/')
PB_EMAIL  = os.environ.get('PB_ADMIN_EMAIL', '')
PB_PASS   = os.environ.get('PB_ADMIN_PASSWORD', '')

if not PB_EMAIL or not PB_PASS:
    sys.exit(
        'ERROR: set PB_ADMIN_EMAIL and PB_ADMIN_PASSWORD.\n'
        'Create the admin account first at: http://89.167.121.193:8090/_/'
    )

# ── HTTP helpers ──────────────────────────────────────────────────────────────

TOKEN = None

def req(method, path, payload=None, token=None):
    url  = f'{PB_URL}/{path.lstrip("/")}'
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    hdrs = {'Content-Type': 'application/json'}
    if token:
        hdrs['Authorization'] = token
    r = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(r) as resp:
            body = resp.read()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if e.code == 400 and 'already exist' in body.lower():
            return {'_exists': True}
        print(f'  HTTP {e.code} {method} {path}: {body[:300]}')
        raise

def pb(method, path, payload=None):
    return req(method, path, payload, token=TOKEN)

# ── Authenticate ──────────────────────────────────────────────────────────────

print('Authenticating...')
auth = req('POST', '/api/admins/auth-with-password',
           {'identity': PB_EMAIL, 'password': PB_PASS})
TOKEN = auth['token']
print(f'  Authenticated as {PB_EMAIL}')

# ── Load source data ──────────────────────────────────────────────────────────

def load_csv(name):
    with open(DATA / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def load_json(name):
    return json.loads((DATA / name).read_text('utf-8'))

products_data        = load_json('products.json')
categories_data       = load_json('categories.json')
trade_hs4_csv         = load_csv('trade_hs4.csv')
raw_material_csv      = load_csv('raw_material_trade.csv')
phase_producers_data  = load_json('phase_producers.json')
product_firms_data    = load_json('product_firms.json')
input_keywords_data   = load_json('input_keywords.json')

def slugify(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]+', '-', s)
    return s.strip('-')

# ── Collection definitions ────────────────────────────────────────────────────

def text(name, **kw):
    return {'name': name, 'type': 'text', 'required': kw.get('required', False),
            'options': {'min': None, 'max': None, 'pattern': ''}}

def num(name, **kw):
    return {'name': name, 'type': 'number', 'required': False,
            'options': {'min': None, 'max': None, 'noDecimal': False}}

def js(name):
    return {'name': name, 'type': 'json', 'required': False,
            'options': {'maxSize': 2000000}}

def sel(name, values):
    return {'name': name, 'type': 'select', 'required': False,
            'options': {'maxSelect': 1, 'values': values}}

COLLECTIONS = [
    {
        # One row per finished product (e.g. Galvanized Sheet). `chains` is
        # the full nested chain-of-stages structure (inputs/technology/
        # skills per node, including dual/triple-route and grouped nodes) --
        # kept as one JSON blob per product rather than exploded into
        # per-node rows, matching the precedent already set by
        # value_chains.status_current etc. in pb_setup.py. The node-level
        # detail is internal to one product's diagram; nothing elsewhere
        # needs to query into it.
        'name': 'explorer_products',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('name', required=True),
            text('category'),
            text('color'),
            text('description'),
            text('hs4_code'),
            js('chains'),
            num('display_order'),
        ],
    },
    {
        'name': 'explorer_categories',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('name', required=True),
            text('color'),
            js('products'),
            num('display_order'),
        ],
    },
    {
        # ITC TradeMap bilateral trade data at HS-4-digit level. Several
        # finished products can share one HS4 code (TradeMap doesn't fetch
        # finer than that), so this is keyed by hs4_code, not product.
        'name': 'explorer_trade_hs4',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('hs4_code', required=True),
            text('desc'),
            num('year'),
            num('imports_uganda'),
            num('imports_eac'),
            num('imports_global'),
            num('exports_uganda'),
            num('exports_eac'),
            num('exports_global'),
            num('display_order'),
        ],
    },
    {
        'name': 'explorer_raw_material_trade',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('item_name', required=True),
            text('desc'),
            num('year'),
            num('imports_uganda'),
            num('imports_eac'),
            num('exports_uganda'),
            num('exports_eac'),
            text('phase'),
            num('display_order'),
        ],
    },
    {
        # Verified plant-by-phase participation counts (NPA/UDC register).
        'name': 'explorer_phase_producers',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('phase', required=True),
            num('count'),
            text('label'),
            js('examples'),
            text('source'),
            num('display_order'),
        ],
    },
    {
        # Per-product producer attribution -- deliberately separate from the
        # phase-level counts above (see the long comment this collection's
        # data carries in ironSteel.js: conflating "how many plants operate
        # at this phase" with "how many plants make this specific product"
        # was a real mistake caught and fixed earlier in this project).
        'name': 'explorer_product_firms',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('product_slug', required=True),
            sel('status', ['named', 'absent', 'unknown']),
            js('firms'),
            text('note'),
            js('phase_context'),
            text('current_capacity'),   # e.g. "120,000 t/yr (Roofings, Kiira)" — shown in detail panel
            text('target_capacity'),    # e.g. "500,000 t/yr (NDP IV target)" — capacity-vs-target traceability
            text('capacity_gap_note'),  # narrative explaining the gap
            num('display_order'),
        ],
    },
    {
        # Keyword -> HS4/Phase matching rules for free-text "Inputs" lines.
        # Order matters (first match wins), hence display_order + full
        # delete-and-reinsert reseeding below rather than upsert-by-key.
        'name': 'explorer_input_keywords',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            sel('target_type', ['hs4', 'phase']),
            text('pattern_source', required=True),
            text('pattern_flags'),
            text('target_value'),
            # essentiality × scarcity weighting (each 0–10): essentiality = how critical
            # to the process; scarcity = how unavailable domestically. weight = their product.
            # Populated via PocketBase admin or by AI analysis of the value chain report.
            num('essentiality'),
            num('scarcity'),
            num('display_order'),
        ],
    },
]

# ── Create / update collections ───────────────────────────────────────────────

print('\n── Creating collections ──')

existing = {c['name']: c['id'] for c in pb('GET', '/api/collections?perPage=200').get('items', [])}

collection_ids = {}
for col in COLLECTIONS:
    name = col['name']
    if name in existing:
        cid = existing[name]
        print(f'  Exists   {name}  (schema left intact)')
    else:
        try:
            result = pb('POST', '/api/collections', col)
            if result.get('_exists'):
                raise RuntimeError('already exists')
            cid = result.get('id', '')
            print(f'  Created  {name}  (id={cid})')
        except Exception:
            now = {c['name']: c['id'] for c in pb('GET', '/api/collections?perPage=200').get('items', [])}
            if name in now:
                cid = now[name]
                print(f'  Exists   {name}  (already present after create attempt)')
            else:
                raise
    collection_ids[name] = cid

# SINGLE SOURCE (ADR-017): schema-only in CI. Re-seeding explorer records from the
# committed files on every deploy would overwrite live PocketBase data. PocketBase
# is authoritative; the seeding below is BOOTSTRAP-ONLY (run without PB_SCHEMA_ONLY).
if os.environ.get('PB_SCHEMA_ONLY') == '1':
    print('\nPB_SCHEMA_ONLY=1 — explorer collections ensured; skipping record seeding (ADR-017).')
    sys.exit(0)

# ── Helper: upsert by an arbitrary unique field ─────────────────────────────

def find_by_field(collection, field, value):
    flt = urllib.parse.quote(f'({field}="{value}")')
    result = pb('GET', f'/api/collections/{collection}/records?filter={flt}&perPage=1')
    items = result.get('items', [])
    return items[0]['id'] if items else None

def upsert_record(collection, field, value, payload):
    existing_id = find_by_field(collection, field, value)
    if existing_id:
        pb('PATCH', f'/api/collections/{collection}/records/{existing_id}', payload)
        return existing_id
    result = pb('POST', f'/api/collections/{collection}/records', payload)
    return result.get('id')

def replace_all(collection, rows):
    """Full delete-and-reinsert -- for collections with no natural unique key
    where row order matters (explorer_input_keywords)."""
    existing_rows = pb('GET', f'/api/collections/{collection}/records?perPage=500').get('items', [])
    for r in existing_rows:
        pb('DELETE', f'/api/collections/{collection}/records/{r["id"]}')
    if existing_rows:
        print(f'  Cleared {len(existing_rows)} existing records')
    for r in rows:
        pb('POST', f'/api/collections/{collection}/records', r)

# ── 1. explorer_products ────────────────────────────────────────────────────

print('\n── Seeding explorer_products ──')
for r in products_data:
    payload = {
        'slug': r['slug'], 'name': r['name'], 'category': r['category'],
        'color': r['color'], 'description': r['description'],
        'hs4_code': r['hs4_code'], 'chains': r['chains'],
        'display_order': r['display_order'],
    }
    upsert_record('explorer_products', 'slug', r['slug'], payload)
    print(f'  {r["name"]}')

# ── 2. explorer_categories ──────────────────────────────────────────────────

print('\n── Seeding explorer_categories ──')
for r in categories_data:
    slug = slugify(r['name'])
    payload = {
        'slug': slug, 'name': r['name'], 'color': r['color'],
        'products': r['products'], 'display_order': r['display_order'],
    }
    upsert_record('explorer_categories', 'slug', slug, payload)
    print(f'  {r["name"]}')

# ── 3. explorer_trade_hs4 ───────────────────────────────────────────────────

print('\n── Seeding explorer_trade_hs4 ──')
for i, r in enumerate(trade_hs4_csv):
    payload = {
        'hs4_code': r['hs4_code'], 'desc': r['desc'], 'year': int(r['year']),
        'imports_uganda': float(r['imports_uganda']), 'imports_eac': float(r['imports_eac']),
        'exports_uganda': float(r['exports_uganda']), 'exports_eac': float(r['exports_eac']),
        'display_order': i,
    }
    upsert_record('explorer_trade_hs4', 'hs4_code', r['hs4_code'], payload)
    print(f'  HS {r["hs4_code"]}')

# ── 4. explorer_raw_material_trade ──────────────────────────────────────────

print('\n── Seeding explorer_raw_material_trade ──')
for i, r in enumerate(raw_material_csv):
    slug = slugify(r['item_name'])
    payload = {
        'slug': slug, 'item_name': r['item_name'], 'desc': r['desc'], 'year': int(r['year']),
        'imports_uganda': float(r['imports_uganda']), 'imports_eac': float(r['imports_eac']),
        'exports_uganda': float(r['exports_uganda']), 'exports_eac': float(r['exports_eac']),
        'phase': r['phase'], 'display_order': i,
    }
    upsert_record('explorer_raw_material_trade', 'slug', slug, payload)
    print(f'  {r["item_name"]}')

# ── 5. explorer_phase_producers ─────────────────────────────────────────────

print('\n── Seeding explorer_phase_producers ──')
for i, r in enumerate(phase_producers_data):
    payload = {
        'phase': r['phase'], 'count': r['count'], 'label': r['label'],
        'examples': r['examples'], 'source': r['source'], 'display_order': i,
    }
    upsert_record('explorer_phase_producers', 'phase', r['phase'], payload)
    print(f'  Phase {r["phase"]}')

# ── 6. explorer_product_firms ───────────────────────────────────────────────

print('\n── Seeding explorer_product_firms ──')
for i, r in enumerate(product_firms_data):
    payload = {
        'product_slug': r['product_slug'], 'status': r['status'], 'firms': r['firms'],
        'note': r['note'], 'phase_context': r['phase_context'], 'display_order': i,
    }
    upsert_record('explorer_product_firms', 'product_slug', r['product_slug'], payload)
    print(f'  {r["product_slug"]}')

# ── 7. explorer_input_keywords (order-sensitive — full replace) ────────────

print('\n── Seeding explorer_input_keywords ──')
replace_all('explorer_input_keywords', [
    {
        'target_type': r['target_type'], 'pattern_source': r['pattern_source'],
        'pattern_flags': r['pattern_flags'], 'target_value': r['target_value'],
        'essentiality': r.get('essentiality'), 'scarcity': r.get('scarcity'),
        'display_order': r['display_order'],
    } for r in input_keywords_data
])
print(f'  {len(input_keywords_data)} rules')

print('\nSetup complete. Verify at:', f'{PB_URL}/_/')
