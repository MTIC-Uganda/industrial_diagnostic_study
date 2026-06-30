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
import urllib.request, urllib.error, urllib.parse
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
key_indicators_csv  = load_csv('key_indicators.csv')
key_indicator_cats_csv = load_csv('key_indicator_categories.csv')
macro_trend_csv = load_csv('macro_trend.csv')
sector_comparison_csv = load_csv('sector_comparison.csv')
risk_register_csv = load_csv('risk_register.csv')
milestones_csv = load_csv('milestones.csv')
glossary_csv  = load_csv('glossary.csv')
chain_synergies_csv = load_csv('chain_synergies.csv')

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
            sel('confidence', ['exact', 'estimated', 'indicative']),
            text('source'),
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
            # Facility columns (ADR-011): the curated map factories are merged in
            # here so the locations map and the treemaps read one table.
            text('chain_slug'),
            text('chain_name'),
            text('location'),
            text('capacity_installed'),
            text('capacity_utilised'),
            text('employees'),
            text('established'),
            text('ownership'),
            text('exports'),
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
    {
        # The 12 Manufacturing Industry Key Indicator cards (2026-06-23 dashboard
        # review redesign). One row per card. Single source of truth for
        # generate_dashboard.py's kpi_* chart functions (ADR-011) — replaces
        # data/dashboard/key_indicators.csv once seeded (CSV stays as the
        # local-dev/first-deploy fallback).
        'name': 'key_indicators',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('label'),
            sel('kind', ['pie', 'donut_multi', 'icon_figure', 'icon_figure_top', 'region_strip', 'bar']),
            text('value'),
            num('pct'),
            text('sub_value'),
            text('icon'),
            text('color'),
            text('rest_color'),
            text('year'),
            text('source'),
            sel('confidence', ['exact', 'estimated', 'indicative']),
            num('display_order'),
        ],
    },
    {
        # Category rows for the multi-category donuts (tax, hightech, credit)
        # and the region-distribution strip (card 8) — one row per slice.
        'name': 'key_indicator_categories',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('indicator_slug', required=True),  # matches key_indicators.slug
            text('category', required=True),
            num('pct'),
            text('value_label'),
            sel('highlight', ['0', '1']),
            num('display_order'),
        ],
    },
    {
        # "Momentum — FY20/21 -> FY24/25" panel. generate_dashboard.py has
        # been reading this collection since it was added (pb_get('macro_trend',
        # ...)), but the collection itself was never created here -- a real,
        # currently-live gap found in the 2026-06-30 dashboard data-source
        # audit: the panel renders "No trend data available" in prod right
        # now because PocketBase has no macro_trend collection to read.
        'name': 'macro_trend',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('label'),
            text('fy2021_value'),
            text('fy2025_value'),
            num('fy2021_pct'),
            num('fy2025_pct'),
            text('delta'),
            sel('direction', ['up', 'down']),
            text('trajectory'),
            text('trajectory_labels'),
            sel('confidence', ['exact', 'estimated', 'indicative']),
            text('source'),
            num('display_order'),
        ],
    },
    {
        # "Chain Status & 2040 Projections" tab — Tax-by-Sector donut and
        # Private Credit-by-Sector bars (and the unused-by-the-dashboard-today
        # 'exports'/'hightech' chart rows, kept for parity with the CSV).
        # 2026-06-30 data-source audit: was CSV-only, no PocketBase path at all.
        'name': 'sector_comparison',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            sel('chart', ['tax', 'credit', 'exports', 'hightech']),
            text('sector', required=True),
            text('value_label'),
            text('usd_label'),
            num('pct'),
            sel('highlight', ['0', '1']),
            num('display_order'),
        ],
    },
    {
        # "Chain Status & 2040 Projections" tab — Risk Register table.
        # 2026-06-30 data-source audit: was CSV-only, no PocketBase path at all.
        'name': 'risk_register',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('risk', required=True),
            text('category'),
            sel('severity', ['high', 'medium', 'low']),
            sel('likelihood', ['high', 'medium', 'low']),
            text('mitigation'),
            text('owner'),
            num('display_order'),
        ],
    },
    {
        # "Chain Status & 2040 Projections" tab — Milestone Roadmap.
        # 2026-06-30 data-source audit: was CSV-only, no PocketBase path at all.
        'name': 'milestones',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            num('year', required=True),
            text('year_label'),
            text('project', required=True),
            text('value_chain'),
            sel('status', ['complete', 'in_progress', 'planned', 'proposed', 'stalled', 'milestone']),
            text('category'),
            text('note'),
            num('display_order'),
        ],
    },
    {
        # Glossary modal, available from any tab.
        # 2026-06-30 data-source audit: was CSV-only, no PocketBase path at all.
        'name': 'glossary',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('term', required=True),
            text('definition'),
            num('display_order'),
        ],
    },
    {
        # "How the 9 chains form one integrated industrial system" card.
        # 2026-06-30 data-source audit: was hardcoded narrative text directly
        # in the template, with specific figures (37,300 t, USD 37m, ~2029)
        # baked into the HTML rather than sourced from any data file.
        'name': 'chain_synergies',
        'type': 'base',
        'listRule': '',
        'viewRule': '',
        'createRule': None,
        'updateRule': None,
        'deleteRule': None,
        'schema': [
            text('slug', required=True),
            text('title', required=True),
            text('description'),
            num('display_order'),
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
        # Do NOT PATCH an existing collection with our hand-built schema.
        # PocketBase 0.22 diffs a collection's fields by id, and our text()/num()/
        # sel() helpers emit fields with no id (and without system/presentable/
        # unique), so any PATCH is read as "drop every existing field and add new
        # ones". That is destructive: it regenerates field ids and WIPES the
        # column data of every existing record (and on some states 400s outright,
        # which is what was breaking CI). Existing collections already have the
        # correct schema, so we just reuse the id and re-seed the records below.
        # To genuinely change an existing collection's schema, edit it in the
        # PocketBase admin UI (or add a dedicated, id-preserving migration).
        cid = existing[name]
        print(f'  Exists   {name}  (schema left intact)')
    else:
        # Race/duplicate-safe: a concurrent run (or an earlier partial run) may have
        # created this collection already. PocketBase 0.22's duplicate-name 400 does
        # not always contain the literal "already exist", so a create can fail even
        # though the collection ends up present. Re-fetch and treat present-after as
        # success; only re-raise if it genuinely is not there. (Fixes the CI 400 from
        # the 13:46/13:55 overlapping runs — see Issue #70.)
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

# ── Additive field migration ────────────────────────────────────────────────
# The big comment above explains why a full schema PATCH on an existing
# collection is destructive (resets every field's id, wiping data). This is
# the "dedicated, id-preserving migration" it points to: fetch the live
# schema (with real ids), append ONLY fields genuinely missing from it, PATCH
# with existing-fields-untouched + new-fields-appended. Never reorders or
# touches an existing field, so it's safe to run on every CI seed, not just
# once. (First needed 2026-06-30: kpi_indicators gained confidence/source
# columns after the collection already existed — those fields were being
# sent in the seed payload below but silently dropped by PocketBase since
# they didn't exist on the live collection yet.)
for col in COLLECTIONS:
    name = col['name']
    if name not in existing:
        continue  # just created above with the full schema already
    current = pb('GET', f'/api/collections/{collection_ids[name]}')
    live_field_names = {f['name'] for f in current.get('schema', [])}
    missing = [f for f in col['schema'] if f['name'] not in live_field_names]
    if not missing:
        continue
    # PocketBase 0.22's collection PATCH rejects a {'schema': [...]}-only
    # body (400, no detail) — it expects the mutable collection fields, not
    # just the one being changed. Send everything current already has,
    # minus read-only metadata (id is in the URL, created/updated/system
    # are server-managed), with schema swapped for the appended version.
    payload = {k: v for k, v in current.items() if k not in ('id', 'created', 'updated', 'system')}
    payload['schema'] = current['schema'] + missing
    pb('PATCH', f'/api/collections/{collection_ids[name]}', payload)
    print(f'  Added field(s) to {name}: {", ".join(f["name"] for f in missing)}')

# ── Helper: upsert by slug field ──────────────────────────────────────────────

def find_by_slug(collection, slug):
    flt = urllib.parse.quote(f'(slug="{slug}")')
    result = pb('GET', f'/api/collections/{collection}/records?filter={flt}&perPage=1')
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
        'current_pct':   float(r['current_pct']),
        'ndp_value':     r['ndp_value'],
        'ndp_pct':       float(r['ndp_pct']),
        'tenfold_value': r['tenfold_value'],
        'tenfold_pct':   float(r['tenfold_pct']),
        'sub_value':     r['sub_value'],
        'confidence':    r.get('confidence') or 'estimated',
        'source':        r.get('source') or '',
        'display_order': i,
    }
    upsert_record('kpi_indicators', 'slug', r['id'], payload)
    print(f'  {r["label"]}')

# ── 3b. key_indicators (the 12 KPI cards, 2026-06-23 redesign) ────────────────

print('\n── Seeding key_indicators ──')

for i, r in enumerate(key_indicators_csv):
    payload = {
        'slug':          r['slug'],
        'label':         r['label'],
        'kind':          r['kind'],
        'value':         r.get('value') or '',
        'pct':           float(r['pct']) if r.get('pct') else None,
        'sub_value':     r.get('sub_value') or '',
        'icon':          r.get('icon') or '',
        'color':         r.get('color') or '',
        'rest_color':    r.get('rest_color') or '',
        'year':          r.get('year') or '',
        'source':        r.get('source') or '',
        'confidence':    r.get('confidence') or 'estimated',
        'display_order': i,
    }
    upsert_record('key_indicators', 'slug', r['slug'], payload)
    print(f'  {r["label"]}')

# ── 3c. key_indicator_categories (donut/region-strip slices) ──────────────────

def find_category_record(indicator_slug, category):
    f = urllib.parse.quote(f'(indicator_slug="{indicator_slug}"&&category="{category}")')
    result = pb('GET', f'/api/collections/key_indicator_categories/records?filter={f}&perPage=1')
    items = result.get('items', [])
    return items[0]['id'] if items else None

print('\n── Seeding key_indicator_categories ──')

for i, r in enumerate(key_indicator_cats_csv):
    payload = {
        'indicator_slug': r['indicator_slug'],
        'category':       r['category'],
        'pct':            float(r['pct']),
        'value_label':    r.get('value_label') or '',
        'highlight':      r.get('highlight') or '0',
        'display_order':  int(r.get('display_order') or i),
    }
    existing_id = find_category_record(r['indicator_slug'], r['category'])
    if existing_id:
        pb('PATCH', f'/api/collections/key_indicator_categories/records/{existing_id}', payload)
    else:
        pb('POST', '/api/collections/key_indicator_categories/records', payload)
    print(f'  {r["indicator_slug"]}: {r["category"]}')

# ── 3d. macro_trend (Momentum panel) ────────────────────────────────────────

print('\n── Seeding macro_trend ──')

for i, r in enumerate(macro_trend_csv):
    payload = {
        'slug':              r['id'],
        'label':             r['label'],
        'fy2021_value':      r.get('fy2021_value') or '',
        'fy2025_value':      r.get('fy2025_value') or '',
        'fy2021_pct':        float(r['fy2021_pct']) if r.get('fy2021_pct') else None,
        'fy2025_pct':        float(r['fy2025_pct']) if r.get('fy2025_pct') else None,
        'delta':             r.get('delta') or '',
        'direction':         r.get('direction') or 'up',
        'trajectory':        r.get('trajectory') or '',
        'trajectory_labels': r.get('trajectory_labels') or '',
        'confidence':        r.get('confidence') or 'estimated',
        'source':            r.get('source') or '',
        'display_order':     i,
    }
    upsert_record('macro_trend', 'slug', r['id'], payload)
    print(f'  {r["label"]}')

# ── 3e. sector_comparison (tax/credit donuts) ───────────────────────────────

print('\n── Seeding sector_comparison ──')

for i, r in enumerate(sector_comparison_csv):
    payload = {
        'slug':          r['slug'],
        'chart':         r['chart'],
        'sector':        r['sector'],
        'value_label':   r.get('value_label') or '',
        'usd_label':     r.get('usd_label') or '',
        'pct':           float(r['pct']) if r.get('pct') else None,
        'highlight':     r.get('highlight') or '0',
        'display_order': i,
    }
    upsert_record('sector_comparison', 'slug', r['slug'], payload)
    print(f'  {r["chart"]}: {r["sector"]}')

# ── 3f. risk_register ───────────────────────────────────────────────────────

print('\n── Seeding risk_register ──')

for i, r in enumerate(risk_register_csv):
    payload = {
        'slug':          r['slug'],
        'risk':          r['risk'],
        'category':      r.get('category') or '',
        'severity':      r.get('severity') or 'medium',
        'likelihood':    r.get('likelihood') or 'medium',
        'mitigation':    r.get('mitigation') or '',
        'owner':         r.get('owner') or '',
        'display_order': i,
    }
    upsert_record('risk_register', 'slug', r['slug'], payload)
    print(f'  {r["slug"]}')

# ── 3g. milestones ───────────────────────────────────────────────────────────

print('\n── Seeding milestones ──')

for i, r in enumerate(milestones_csv):
    payload = {
        'slug':          r['slug'],
        'year':          int(r['year']),
        'year_label':    r.get('year_label') or '',
        'project':       r['project'],
        'value_chain':   r.get('value_chain') or '',
        'status':        r.get('status') or 'planned',
        'category':      r.get('category') or '',
        'note':          r.get('note') or '',
        'display_order': i,
    }
    upsert_record('milestones', 'slug', r['slug'], payload)
    print(f'  {r["project"]}')

# ── 3h. glossary ─────────────────────────────────────────────────────────────

print('\n── Seeding glossary ──')

for i, r in enumerate(glossary_csv):
    payload = {
        'slug':          r['slug'],
        'term':          r['term'],
        'definition':    r.get('definition') or '',
        'display_order': i,
    }
    upsert_record('glossary', 'slug', r['slug'], payload)
    print(f'  {r["term"]}')

# ── 3i. chain_synergies (Integration card) ──────────────────────────────────

print('\n── Seeding chain_synergies ──')

for i, r in enumerate(chain_synergies_csv):
    payload = {
        'slug':          r['slug'],
        'title':         r['title'],
        'description':   r.get('description') or '',
        'display_order': i,
    }
    upsert_record('chain_synergies', 'slug', r['slug'], payload)
    print(f'  {r["title"]}')

print('\nSetup complete. Verify at:', f'{PB_URL}/_/')
