#!/usr/bin/env python3
"""
Migrate the curated `facilities` rows into `industries` so there is one
establishment table (ADR-011). Two steps, both idempotent and safe:

  1. Add the facility-only columns to `industries` if missing. This is an
     ADDITIVE schema change: existing fields are sent back exactly as stored
     (ids intact) and the new fields are appended. The script ABORTS if the
     PATCH would change any existing field id (the destructive case that broke
     the seed job before).
  2. Upsert each facility as an `industries` row keyed by reg_number `FAC-<id>`,
     so re-running never duplicates and the locations map can read one table.

Env: PB_URL, PB_ADMIN_EMAIL, PB_ADMIN_PASSWORD.
"""
import json, os, sys, time, urllib.request, urllib.error

PB_URL  = os.environ['PB_URL'].rstrip('/')
EMAIL   = os.environ['PB_ADMIN_EMAIL']
PASS    = os.environ['PB_ADMIN_PASSWORD']

NEW_FIELDS = ['chain_slug', 'chain_name', 'location', 'capacity_installed',
              'capacity_utilised', 'employees', 'established', 'ownership', 'exports']

def req(method, path, payload=None, token=None):
    data = json.dumps(payload).encode() if payload is not None else None
    h = {'Content-Type': 'application/json'}
    if token: h['Authorization'] = token
    r = urllib.request.Request(f'{PB_URL}{path}', data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r) as resp:
            b = resp.read(); return json.loads(b) if b else {}
    except urllib.error.HTTPError as e:
        print(f'  HTTP {e.code} {method} {path}: {e.read().decode()[:300]}'); raise

tok = req('POST', '/api/admins/auth-with-password', {'identity': EMAIL, 'password': PASS})['token']
print(f'Authenticated {EMAIL} @ {PB_URL}')

cols = {c['name']: c for c in req('GET', '/api/collections?perPage=200', token=tok)['items']}
ind = cols['industries']
cid = ind['id']
existing_names = {f['name'] for f in ind['schema']}
existing_ids = {f['name']: f['id'] for f in ind['schema']}

# ── Step 1: additive column add ───────────────────────────────────────────────
to_add = [n for n in NEW_FIELDS if n not in existing_names]
if to_add:
    print(f'Adding columns to industries: {to_add}')
    new_schema = [dict(f) for f in ind['schema']]   # existing fields verbatim, ids intact
    for n in to_add:
        new_schema.append({'name': n, 'type': 'text', 'required': False,
                           'options': {'min': None, 'max': None, 'pattern': ''}})
    patched = dict(ind); patched['schema'] = new_schema
    req('PATCH', f'/api/collections/{cid}', patched, token=tok)
    # Verify no existing id changed (abort loudly if it did)
    after = {c['name']: c for c in req('GET', '/api/collections?perPage=200', token=tok)['items']}['industries']
    after_ids = {f['name']: f['id'] for f in after['schema']}
    drifted = [n for n, i in existing_ids.items() if after_ids.get(n) != i]
    if drifted:
        sys.exit(f'ABORT: existing field ids changed for {drifted} — schema add was destructive.')
    print(f'  OK: {len(to_add)} columns added, all existing field ids preserved.')
else:
    print('Columns already present, skipping schema change.')

# ── Step 2: upsert facilities as industries rows ──────────────────────────────
facilities = req('GET', '/api/collections/facilities/records?perPage=500', token=tok).get('items', [])
print(f'Migrating {len(facilities)} facilities into industries...')
done = 0
for f in facilities:
    reg = f'FAC-{f["id"]}'
    payload = {
        'reg_number': reg, 'name': f.get('name', ''),
        'name_products': f.get('name', ''), 'products': f.get('products', ''),
        'latitude': f.get('lat') or 0, 'longitude': f.get('lng') or 0,
        'location': f.get('location', ''), 'chain_name': f.get('chain_name', ''),
        'chain_slug': f.get('chain_slug', ''),
        'capacity_installed': f.get('capacity_installed', ''),
        'capacity_utilised': f.get('capacity_utilised', ''),
        'employees': f.get('employees', ''), 'established': f.get('established', ''),
        'ownership': f.get('ownership', ''), 'exports': f.get('exports', ''),
        'status': 'active', 'source': 'curated facilities (migrated)',
    }
    found = req('GET', f'/api/collections/industries/records?filter=(reg_number="{reg}")&perPage=1', token=tok).get('items', [])
    if found:
        req('PATCH', f'/api/collections/industries/records/{found[0]["id"]}', payload, token=tok)
    else:
        req('POST', '/api/collections/industries/records', payload, token=tok)
    done += 1
    time.sleep(0.02)
print(f'Done: {done} facilities upserted into industries.')
gps = req('GET', '/api/collections/industries/records?filter=(latitude>0)&perPage=1', token=tok).get('totalItems', '?')
print(f'industries rows with GPS now: {gps}')
