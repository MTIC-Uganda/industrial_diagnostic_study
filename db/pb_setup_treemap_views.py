#!/usr/bin/env python3
"""
One-time setup: create six PocketBase view collections that pre-aggregate the
industries register into the treemap breakdowns.

Run once (or after schema changes). Re-running is safe — existing view collections
are deleted and re-created. No data is seeded; the views are live SQL on the
existing `industries` table so they always reflect the latest register state.

Why view collections instead of fetching 7,100 raw rows client-side:
  ADR-024 confirms direct browser→PocketBase fetch is the right architecture.
  View collections keep that pattern while moving the GROUP BY computation to
  the database, reducing the browser payload from ~3.5 MB to ~50 KB.

Usage:
    $env:PB_URL            = "https://db.midd-ug.com"       # or staging-db
    $env:PB_ADMIN_EMAIL    = "admin@mtic.go.ug"
    $env:PB_ADMIN_PASSWORD = "your-admin-password"
    python db/pb_setup_treemap_views.py
"""

import json, os, sys
import urllib.request, urllib.error
from pathlib import Path

PB_URL   = os.environ.get('PB_URL', 'http://89.167.121.193:8090').rstrip('/')
PB_EMAIL = os.environ.get('PB_ADMIN_EMAIL', '')
PB_PASS  = os.environ.get('PB_ADMIN_PASSWORD', '')

if not PB_EMAIL or not PB_PASS:
    sys.exit(
        'ERROR: set PB_ADMIN_EMAIL and PB_ADMIN_PASSWORD.\n'
        'Example:\n'
        '  $env:PB_URL            = "https://db.midd-ug.com"\n'
        '  $env:PB_ADMIN_EMAIL    = "admin@mtic.go.ug"\n'
        '  $env:PB_ADMIN_PASSWORD = "your-password"\n'
        '  python db/pb_setup_treemap_views.py'
    )

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
        if e.code == 404:
            return None
        raise RuntimeError(f'HTTP {e.code} {method} {path}: {body[:400]}') from e

def authenticate():
    global TOKEN
    resp = req('POST', '/api/admins/auth-with-password',
               {'identity': PB_EMAIL, 'password': PB_PASS})
    TOKEN = resp['token']
    print(f'Authenticated as {PB_EMAIL}')

def delete_if_exists(name):
    existing = req('GET', f'/api/collections/{name}', token=TOKEN)
    if existing:
        req('DELETE', f'/api/collections/{name}', token=TOKEN)
        print(f'  Deleted existing collection: {name}')

# Each view has: name, (k1_col, k2_col) to group by, and a human label.
# Rows will have fields: id (synthetic), k1, k2, cnt.
# The browser's _buildNested() function reads these generic field names so all
# six views can be processed with the same code.
VIEWS = [
    ('v_treemap_sector_subsector',    'sector_name',   'subsector_name'),
    ('v_treemap_region_district',     'region',        'district'),
    ('v_treemap_region_sector',       'region',        'sector_name'),
    ('v_treemap_district_sector',     'district',      'sector_name'),
    ('v_treemap_region_subsector',    'region',        'subsector_name'),
    ('v_treemap_district_subsector',  'district',      'subsector_name'),
]

FAC_FILTER = "reg_number NOT LIKE 'FAC-%'"

def create_view(name, col1, col2):
    # Synthetic id: concatenate the two grouping keys so PocketBase has a stable,
    # unique identifier per row (GROUP BY guarantees uniqueness of this pair).
    query = (
        f"SELECT ({col1} || '__' || {col2}) AS id, "
        f"{col1} AS k1, {col2} AS k2, COUNT(*) AS cnt "
        f"FROM industries "
        f"WHERE {FAC_FILTER} "
        f"GROUP BY {col1}, {col2}"
    )
    schema = [
        {'name': 'k1',  'type': 'text',   'required': False, 'options': {}},
        {'name': 'k2',  'type': 'text',   'required': False, 'options': {}},
        {'name': 'cnt', 'type': 'number', 'required': False, 'options': {'min': None, 'max': None, 'noDecimal': True}},
    ]
    payload = {
        'name':         name,
        'type':         'view',
        'viewQuery':    query,
        'schema':       schema,
        'listRule':     '',   # publicly readable (empty string = allow all)
        'viewRule':     '',
    }
    req('POST', '/api/collections', payload, token=TOKEN)
    print(f'  Created: {name}  ({col1} × {col2})')

def main():
    authenticate()
    print(f'\nSetting up {len(VIEWS)} treemap view collections on {PB_URL} …')
    for name, col1, col2 in VIEWS:
        delete_if_exists(name)
        create_view(name, col1, col2)
    print('\nDone. Verify at: ' + PB_URL + '/_/#/collections')
    print('Test one view:   ' + PB_URL + '/api/collections/v_treemap_sector_subsector/records?perPage=5')

if __name__ == '__main__':
    main()
