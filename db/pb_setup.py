#!/usr/bin/env python3
"""
One-time setup: create PocketBase collections and seed all data.

Run from repo root after PocketBase is running and you have created
the first admin account via the web UI (http://<server>:8090/_/).

Usage:
    $env:PB_URL           = "http://89.167.121.193:8090"
    $env:PB_ADMIN_EMAIL   = "admin@mtic.go.ug"
    $env:PB_ADMIN_PASSWORD = "your-admin-password"
    python db/pb_setup.py

Re-running is safe — existing collections and records are updated, not duplicated.
"""

import csv, json, os, sys, time
import urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'dashboard'

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
        # 400 with "already exists" is fine for collections
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

chains_data   = json.loads((DATA / 'chains.json').read_text('utf-8'))
chain_colors  = json.loads((DATA / 'chain_colors.json').read_text('utf-8'))
chain_summary = load_csv('chain_summary.csv')
factories_csv = load_csv('factories.csv')
kpis          = load_csv('overview_kpis.csv')

chains_by_name = {c['name']: c for c in chains_data}

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
        'name': 'value_chains',
        'type': 'base',
        'listRule': '',   # empty string = public read
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('name', required=True),
            text('color'),
            num('display_order'),
            text('key_import_2024'),
            text('key_export_2024'),
            text('position_tag'),
            sel('position_color', ['green','amber','red']),
            text('target_2040'),
            text('priority_tag'),
            sel('priority_color', ['red','blue','green','amber']),
            text('map_title'),
            text('map_description'),
            text('map_gap'),
            js('map_phases'),
            js('status_current'),
            js('status_companies'),
            js('status_constraints'),
            js('status_priorities'),
            js('status_proj'),
        ],
    },
    {
        'name': 'facilities',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('chain_slug'),   # slug of the value chain (e.g. 'iron-steel')
            text('chain_name'),   # display name (e.g. 'Iron & Steel') — for the map JS
            text('name', required=True),
            num('lat'),
            num('lng'),
            text('location'),
            text('products'),
            text('capacity_installed'),
            text('capacity_utilised'),
            text('employees'),
            text('established'),
            text('ownership'),
            text('exports'),
        ],
    },
    {
        'name': 'kpi_indicators',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('label'),
            text('current_value'),
            num('current_pct'),
            text('ndp_value'),
            num('ndp_pct'),
            text('tenfold_value'),
            num('tenfold_pct'),
            text('sub_value'),
            num('display_order'),
        ],
    },
    {
        # One record per registered manufacturing establishment (7,011 total).
        # Populated by db/seed_industries.py after running scripts/extract_industries_to_records.py.
        # This is the SINGLE SOURCE OF TRUTH for all manufacturing establishment data.
        'name': 'industries',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('reg_number', required=True),    # NIR-2025-XXXXXX
            num('row_no'),
            text('name_products'),                # raw combined text from PDF (editable)
            text('name'),                         # editable: industry/company name
            text('products'),                     # editable: specific products manufactured
            text('district'),
            sel('region', ['Central', 'Eastern', 'Northern', 'Western', 'Unclassified']),
            text('contact'),
            num('latitude'),
            num('longitude'),
            text('isic_4digit'),
            text('isic_4digit_desc'),
            text('isic_2digit'),
            text('isic_2digit_desc'),
            num('subsector_num'),
            text('subsector_name'),
            num('sector_num'),
            text('sector_name'),
            sel('status', ['active', 'inactive', 'unverified']),
            text('source'),
            text('notes'),                        # free-text field for manual corrections/annotations
        ],
    },
    {
        # One row per field × value-chain datapoint collected by the agents.
        # Schema mirrors the record envelope in diagnostic_schema.json.
        'name': 'diagnostic_datapoints',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('field_id', required=True),        # e.g. D1.01
            text('value_chain_id', required=True),   # VC01..VC09
            text('value'),                           # measured value (stored as text; typed in agent)
            text('raw_source'),                      # citation/document/interviewee
            sel('source_type', [
                'secondary_statistic','admin_record','key_informant_interview',
                'field_visit_observation','firm_survey','policy_document',
                'desk_estimate','triangulated','upload_mined','trusted_api',
            ]),
            text('reporting_year'),                  # e.g. 2024 or FY2023/24
            sel('confidence', ['high','medium','low','estimated','not_available']),
            text('disaggregation_values'),
            text('collection_notes'),
            text('collected_by'),                    # agent run id / timestamp
            text('triangulation_refs'),
            sel('ingestion_method', ['manual','upload_mining','trusted_source','web_gap_fill']),
            text('trusted_source_id'),               # for trusted_source method
            text('source_document_ref'),             # for upload_mining: filename + page/cell
            text('source_url'),                      # for web_gap_fill
            sel('approval_status', [
                'not_required','pending_approval','approved','rejected',
            ]),
            text('approved_by'),
            text('approved_at'),
            text('approval_pr'),
        ],
    },
]

# ── Create / update collections ───────────────────────────────────────────────

print('\n── Creating collections ──')

# Get existing collections
existing = {c['name']: c['id'] for c in pb('GET', '/api/collections?perPage=200').get('items', [])}

collection_ids = {}
for col in COLLECTIONS:
    name = col['name']
    if name in existing:
        cid = existing[name]
        pb('PATCH', f'/api/collections/{cid}', col)
        print(f'  Updated  {name}')
    else:
        result = pb('POST', '/api/collections', col)
        cid = result.get('id', '')
        print(f'  Created  {name}  (id={cid})')
    collection_ids[name] = cid

# ── Helper: upsert by slug field ──────────────────────────────────────────────

def find_by_slug(collection, slug):
    result = pb('GET', f'/api/collections/{collection}/records?filter=(slug="{slug}")&perPage=1')
    items = result.get('items', [])
    return items[0]['id'] if items else None

def upsert_record(collection, slug_field, slug_val, payload):
    existing_id = find_by_slug(collection, slug_val)
    if existing_id:
        pb('PATCH', f'/api/collections/{collection}/records/{existing_id}', payload)
        return existing_id
    else:
        result = pb('POST', f'/api/collections/{collection}/records', payload)
        return result.get('id')

# ── 1. value_chains ───────────────────────────────────────────────────────────

print('\n── Seeding value_chains ──')
chain_slug_to_id = {}

for i, row in enumerate(chain_summary):
    name = row['chain']
    c    = chains_by_name.get(name, {})
    m    = c.get('map', {})
    s    = c.get('status', {})
    slug = c.get('id', name.lower().replace(' ', '-').replace('&', 'and').replace('/', '-'))

    payload = {
        'slug':          slug,
        'name':          name,
        'color':         chain_colors.get(name, '#1565c0'),
        'display_order': i,

        'key_import_2024': row['key_import_2024'],
        'key_export_2024': row['key_export_2024'],
        'position_tag':    row['position_tag'],
        'position_color':  row['position_color'],
        'target_2040':     row['target_2040'],
        'priority_tag':    row['priority_tag'],
        'priority_color':  row['priority_color'],

        'map_title':       m.get('title', ''),
        'map_description': m.get('desc', ''),
        'map_gap':         m.get('gap', ''),
        'map_phases':      m.get('phases', []),

        'status_current':     s.get('current', []),
        'status_companies':   s.get('companies', []),
        'status_constraints': s.get('constraints', []),
        'status_priorities':  s.get('priorities', []),
        'status_proj':        s.get('proj', {}),
    }

    rid = upsert_record('value_chains', 'slug', slug, payload)
    chain_slug_to_id[slug] = rid
    chain_slug_to_id[name] = rid   # also index by display name
    print(f'  {name}')

# ── 2. facilities ─────────────────────────────────────────────────────────────

print('\n── Seeding facilities ──')

# Delete all existing facilities and re-insert (no natural unique key)
existing_fac = pb('GET', '/api/collections/facilities/records?perPage=500').get('items', [])
for fac in existing_fac:
    pb('DELETE', f'/api/collections/facilities/records/{fac["id"]}')
if existing_fac:
    print(f'  Cleared {len(existing_fac)} existing records')

for f in factories_csv:
    chain_name = f['chain']
    slug = next(
        (c.get('id', '') for c in chains_data if c['name'] == chain_name),
        chain_name.lower().replace(' ', '-').replace('&', 'and').replace('/', '-')
    )
    try:
        lat = float(f['lat'])
        lng = float(f['lng'])
    except (ValueError, KeyError):
        lat = lng = 0

    payload = {
        'chain_slug':         slug,
        'chain_name':         chain_name,
        'name':               f['name'],
        'lat':                lat,
        'lng':                lng,
        'location':           f.get('loc', ''),
        'products':           f.get('products', ''),
        'capacity_installed': f.get('capacity_installed', ''),
        'capacity_utilised':  f.get('capacity_utilised', ''),
        'employees':          f.get('employees', ''),
        'established':        f.get('est', ''),
        'ownership':          f.get('ownership', ''),
        'exports':            f.get('exports', ''),
    }
    pb('POST', '/api/collections/facilities/records', payload)
    time.sleep(0.02)   # avoid hammering the API

print(f'  Inserted {len(factories_csv)} facilities')

# ── 3. kpi_indicators ─────────────────────────────────────────────────────────

print('\n── Seeding kpi_indicators ──')

for i, r in enumerate(kpis):
    payload = {
        'slug':          r['id'],
        'label':         r['label'],
        'current_value': r['current_value'],
        'current_pct':   int(r['current_pct']),
        'ndp_value':     r['ndp_value'],
        'ndp_pct':       int(r['ndp_pct']),
        'tenfold_value': r['tenfold_value'],
        'tenfold_pct':   int(r['tenfold_pct']),
        'sub_value':     r['sub_value'],
        'display_order': i,
    }
    upsert_record('kpi_indicators', 'slug', r['id'], payload)
    print(f'  {r["label"]}')

print('\nSetup complete. Verify at:', f'{PB_URL}/_/')
