#!/usr/bin/env python3
"""
Seed the PocketBase 'industries' collection from data/dashboard/industries.json.

Run AFTER:
  1. python scripts/extract_industries_to_records.py   (produces industries.json)
  2. python db/pb_setup.py                              (creates the collection schema)

Usage:
    $env:PB_URL            = "http://89.167.121.193:8090"
    $env:PB_ADMIN_EMAIL    = "admin@mtic.go.ug"
    $env:PB_ADMIN_PASSWORD = "your-admin-password"
    python db/seed_industries.py

Re-running is safe: clears existing records and reloads from industries.json.
To update a single record, edit it directly in the PocketBase admin UI.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'data' / 'dashboard' / 'industries.json'

PB_URL  = os.environ.get('PB_URL', 'http://89.167.121.193:8090').rstrip('/')
PB_EMAIL = os.environ.get('PB_ADMIN_EMAIL', '')
PB_PASS  = os.environ.get('PB_ADMIN_PASSWORD', '')

if not PB_EMAIL or not PB_PASS:
    sys.exit(
        'ERROR: set PB_ADMIN_EMAIL and PB_ADMIN_PASSWORD.\n'
        'Create the admin account first at: http://89.167.121.193:8090/_/'
    )

if not SOURCE.exists():
    sys.exit(
        f'ERROR: {SOURCE} not found.\n'
        'Run:  python scripts/extract_industries_to_records.py  first.'
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
auth  = req('POST', '/api/admins/auth-with-password',
            {'identity': PB_EMAIL, 'password': PB_PASS})
TOKEN = auth['token']
print(f'  Authenticated as {PB_EMAIL}')

# ── Ensure collection exists ──────────────────────────────────────────────────

existing_cols = {c['name']: c['id']
                 for c in pb('GET', '/api/collections?perPage=200').get('items', [])}

if 'industries' not in existing_cols:
    sys.exit(
        'ERROR: industries collection not found in PocketBase.\n'
        'Run:  python db/pb_setup.py  first to create the schema.'
    )

# ── Load source data ──────────────────────────────────────────────────────────

industries = json.loads(SOURCE.read_text('utf-8'))
print(f'Loaded {len(industries)} records from {SOURCE.name}')

# ── Clear existing records (batch delete via pagination) ──────────────────────

print('\nClearing existing industries records...')
cleared = 0
while True:
    result = pb('GET', '/api/collections/industries/records?perPage=200&fields=id')
    items  = result.get('items', [])
    if not items:
        break
    for item in items:
        pb('DELETE', f'/api/collections/industries/records/{item["id"]}')
        cleared += 1
    time.sleep(0.1)

if cleared:
    print(f'  Cleared {cleared} existing records')

# ── Insert all records ────────────────────────────────────────────────────────

print(f'\nInserting {len(industries)} records...')
inserted = 0
errors   = 0

for i, rec in enumerate(industries, 1):
    payload = {
        'reg_number':       rec['reg_number'],
        'row_no':           rec['row_no'],
        'name_products':    rec['name_products'],
        'name':             rec.get('name', ''),
        'products':         rec.get('products', ''),
        'district':         rec.get('district', ''),
        'region':           rec.get('region', 'Unclassified'),
        'contact':          rec.get('contact', ''),
        'latitude':         rec['latitude'] if rec['latitude'] is not None else 0,
        'longitude':        rec['longitude'] if rec['longitude'] is not None else 0,
        'isic_4digit':      rec.get('isic_4digit', ''),
        'isic_4digit_desc': rec.get('isic_4digit_desc', ''),
        'isic_2digit':      rec.get('isic_2digit', ''),
        'isic_2digit_desc': rec.get('isic_2digit_desc', ''),
        'subsector_num':    rec.get('subsector_num', 0),
        'subsector_name':   rec.get('subsector_name', ''),
        'sector_num':       rec.get('sector_num', 0),
        'sector_name':      rec.get('sector_name', ''),
        'status':           rec.get('status', 'active'),
        'source':           rec.get('source', ''),
        'notes':            rec.get('notes', ''),
    }

    try:
        pb('POST', '/api/collections/industries/records', payload)
        inserted += 1
    except Exception as e:
        errors += 1
        print(f'  ERROR row {rec["row_no"]}: {e}')

    # Progress report every 500 records
    if i % 500 == 0:
        print(f'  {i}/{len(industries)} inserted...')

    time.sleep(0.05)   # ~20 req/sec — polite to the API

print(f'\nDone: {inserted} inserted, {errors} errors')
print(f'View at: {PB_URL}/_/#/collections/industries')
