#!/usr/bin/env python3
"""
One-time seed: migrate existing CSV/JSON data files into Supabase.

Requirements:
    pip install requests

Usage:
    Set environment variables, then run from repo root:

    $env:SUPABASE_URL      = "https://<project-ref>.supabase.co"
    $env:SUPABASE_SERVICE_KEY = "<service-role-key>"   # NOT the anon key
    python db/seed.py

The service role key bypasses RLS and can INSERT.
Find it in: Supabase Dashboard → Project Settings → API → service_role key.
"""

import csv, json, os, sys
import urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'dashboard'

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').rstrip('/')
SERVICE_KEY  = os.environ.get('SUPABASE_SERVICE_KEY', '')

if not SUPABASE_URL or not SERVICE_KEY:
    sys.exit(
        'ERROR: Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables.\n'
        'Service key is in: Supabase Dashboard → Project Settings → API → service_role'
    )

# ── Supabase helpers ──────────────────────────────────────────────────────────

def api(method, table, payload=None):
    url  = f'{SUPABASE_URL}/rest/v1/{table}'
    data = json.dumps(payload).encode() if payload else None
    req  = urllib.request.Request(url, data=data, method=method, headers={
        'apikey':        SERVICE_KEY,
        'Authorization': f'Bearer {SERVICE_KEY}',
        'Content-Type':  'application/json',
        'Prefer':        'return=minimal',
    })
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read()
            return json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        print(f'  ERROR {e.code} on {method} {table}: {msg[:300]}')
        raise

def upsert(table, rows, conflict='id'):
    req = urllib.request.Request(
        f'{SUPABASE_URL}/rest/v1/{table}',
        data=json.dumps(rows).encode(),
        method='POST',
        headers={
            'apikey':        SERVICE_KEY,
            'Authorization': f'Bearer {SERVICE_KEY}',
            'Content-Type':  'application/json',
            'Prefer':        f'resolution=merge-duplicates,return=minimal',
        }
    )
    try:
        with urllib.request.urlopen(req) as r:
            r.read()
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        print(f'  ERROR upserting {table}: {msg[:300]}')
        raise

# ── Load source data ──────────────────────────────────────────────────────────

def load_csv(name):
    with open(DATA / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

chains_data   = json.loads((DATA / 'chains.json').read_text('utf-8'))
chain_colors  = json.loads((DATA / 'chain_colors.json').read_text('utf-8'))
chain_summary = load_csv('chain_summary.csv')
factories_csv = load_csv('factories.csv')
kpis          = load_csv('overview_kpis.csv')

# ── 1. value_chains ───────────────────────────────────────────────────────────
print('\n── 1. Seeding value_chains ──')

# Index chains.json by name for merging
chains_by_name = {c['name']: c for c in chains_data}

rows_vc = []
for i, row in enumerate(chain_summary):
    name = row['chain']
    c    = chains_by_name.get(name, {})
    m    = c.get('map', {})
    s    = c.get('status', {})

    rows_vc.append({
        'id':            c.get('id', name.lower().replace(' ', '-').replace('&', 'and')),
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
    })

upsert('value_chains', rows_vc)
print(f'  Upserted {len(rows_vc)} value chains')

# ── 2. facilities ─────────────────────────────────────────────────────────────
print('\n── 2. Seeding facilities ──')

# Build chain name → id map
chain_id_by_name = {r['name']: r['id'] for r in rows_vc}

rows_f = []
for f in factories_csv:
    chain_id = chain_id_by_name.get(f['chain'])
    if not chain_id:
        print(f'  WARNING: unknown chain "{f["chain"]}" for facility "{f["name"]}" — skipping')
        continue
    try:
        lat = float(f['lat'])
        lng = float(f['lng'])
    except (ValueError, KeyError):
        lat = lng = None

    rows_f.append({
        'chain_id':           chain_id,
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
    })

# Facilities have no natural unique key — delete all and re-insert
# (safe for seeding; a production system would match on name+chain_id)
print('  Deleting existing facilities...')
api('DELETE', 'facilities?id=neq.00000000-0000-0000-0000-000000000000')

BATCH = 20
for i in range(0, len(rows_f), BATCH):
    upsert('facilities', rows_f[i:i+BATCH])
print(f'  Inserted {len(rows_f)} facilities')

# ── 3. kpi_indicators ─────────────────────────────────────────────────────────
print('\n── 3. Seeding kpi_indicators ──')

rows_k = []
for i, r in enumerate(kpis):
    rows_k.append({
        'id':            r['id'],
        'label':         r['label'],
        'current_value': r['current_value'],
        'current_pct':   int(r['current_pct']),
        'ndp_value':     r['ndp_value'],
        'ndp_pct':       int(r['ndp_pct']),
        'tenfold_value': r['tenfold_value'],
        'tenfold_pct':   int(r['tenfold_pct']),
        'sub_value':     r['sub_value'],
        'display_order': i,
    })

upsert('kpi_indicators', rows_k)
print(f'  Upserted {len(rows_k)} KPI indicators')

print('\nSeed complete.')
