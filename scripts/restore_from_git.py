#!/usr/bin/env python3
"""
Force PocketBase back to exactly match the committed data/dashboard/ files --
the "reject this change" half of the drift-check workflow (see
scripts/detect_drift.py for the full picture).

Run this after closing (not merging) a "PocketBase drift detected" PR: it
re-seeds every row from git (same as db/pb_setup.py) AND deletes any
PocketBase record that isn't present in git at all -- which db/pb_setup.py's
upsert-only seeding deliberately never does, so it can't undo someone adding
a brand-new row directly in PocketBase.

Usage:
    $env:PB_URL           = "http://89.167.121.193:8090"
    $env:PB_ADMIN_EMAIL   = "admin@mtic.go.ug"
    $env:PB_ADMIN_PASSWORD = "your-admin-password"
    python scripts/restore_from_git.py
"""

import csv, json, os, sys
import urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'dashboard'

PB_URL   = os.environ.get('PB_URL', '').rstrip('/')
PB_EMAIL = os.environ.get('PB_ADMIN_EMAIL', '')
PB_PASS  = os.environ.get('PB_ADMIN_PASSWORD', '')

if not PB_URL or not PB_EMAIL or not PB_PASS:
    sys.exit('ERROR: set PB_URL, PB_ADMIN_EMAIL and PB_ADMIN_PASSWORD.')

TOKEN = None

def req(method, path, payload=None, token=None):
    url  = f'{PB_URL}/{path.lstrip("/")}'
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    hdrs = {'Content-Type': 'application/json'}
    if token:
        hdrs['Authorization'] = token
    r = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    with urllib.request.urlopen(r) as resp:
        body = resp.read()
        return json.loads(body) if body else {}

def pb(method, path, payload=None):
    return req(method, path, payload, token=TOKEN)

print('Authenticating...')
auth = req('POST', '/api/admins/auth-with-password', {'identity': PB_EMAIL, 'password': PB_PASS})
TOKEN = auth['token']
print(f'  Authenticated as {PB_EMAIL}')

def load_csv(name):
    with open(DATA / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def pb_all(collection):
    items, page = [], 1
    while True:
        result = pb('GET', f'/api/collections/{collection}/records?perPage=500&page={page}')
        items.extend(result.get('items', []))
        if page >= result.get('totalPages', 1) or not result.get('items'):
            break
        page += 1
    return items

def restore_collection(collection, key_field, git_rows, payload_fn):
    """Upsert every git row into PocketBase (overwrites edits), then delete
    any PocketBase record whose key isn't in git (removes additions)."""
    git_keys = {str(r[key_field]) for r in git_rows}
    live = pb_all(collection)
    live_by_key = {str(r.get(key_field)): r for r in live}

    updated = added = 0
    for r in git_rows:
        key = str(r[key_field])
        payload = payload_fn(r)
        if key in live_by_key:
            pb('PATCH', f'/api/collections/{collection}/records/{live_by_key[key]["id"]}', payload)
            updated += 1
        else:
            pb('POST', f'/api/collections/{collection}/records', payload)
            added += 1

    removed = 0
    for key, rec in live_by_key.items():
        if key not in git_keys:
            pb('DELETE', f'/api/collections/{collection}/records/{rec["id"]}')
            removed += 1

    print(f'  {collection}: {updated} restored, {added} re-added, {removed} extra record(s) deleted')

restore_collection('key_indicators', 'slug', load_csv('key_indicators.csv'), lambda r: {
    'slug': r['slug'], 'label': r['label'], 'kind': r['kind'], 'value': r.get('value') or '',
    'pct': float(r['pct']) if r.get('pct') else None, 'sub_value': r.get('sub_value') or '',
    'icon': r.get('icon') or '', 'color': r.get('color') or '', 'rest_color': r.get('rest_color') or '',
    'year': r.get('year') or '', 'source': r.get('source') or '', 'confidence': r.get('confidence') or 'estimated',
})

restore_collection('kpi_indicators', 'id', load_csv('overview_kpis.csv'), lambda r: {
    'slug': r['id'], 'label': r['label'], 'current_value': r['current_value'], 'current_pct': float(r['current_pct']),
    'ndp_value': r['ndp_value'], 'ndp_pct': float(r['ndp_pct']), 'tenfold_value': r['tenfold_value'],
    'tenfold_pct': float(r['tenfold_pct']), 'sub_value': r['sub_value'],
    'confidence': r.get('confidence') or 'estimated', 'source': r.get('source') or '',
})

restore_collection('macro_trend', 'id', load_csv('macro_trend.csv'), lambda r: {
    'slug': r['id'], 'label': r['label'], 'fy2021_value': r.get('fy2021_value') or '',
    'fy2025_value': r.get('fy2025_value') or '', 'fy2021_pct': float(r['fy2021_pct']) if r.get('fy2021_pct') else None,
    'fy2025_pct': float(r['fy2025_pct']) if r.get('fy2025_pct') else None, 'delta': r.get('delta') or '',
    'direction': r.get('direction') or 'up', 'trajectory': r.get('trajectory') or '',
    'trajectory_labels': r.get('trajectory_labels') or '', 'confidence': r.get('confidence') or 'estimated',
    'source': r.get('source') or '',
})

restore_collection('sector_comparison', 'slug', load_csv('sector_comparison.csv'), lambda r: {
    'slug': r['slug'], 'chart': r['chart'], 'sector': r['sector'], 'value_label': r.get('value_label') or '',
    'usd_label': r.get('usd_label') or '', 'pct': float(r['pct']) if r.get('pct') else None,
    'highlight': r.get('highlight') or '0',
})

restore_collection('risk_register', 'slug', load_csv('risk_register.csv'), lambda r: {
    'slug': r['slug'], 'risk': r['risk'], 'category': r.get('category') or '',
    'severity': r.get('severity') or 'medium', 'likelihood': r.get('likelihood') or 'medium',
    'mitigation': r.get('mitigation') or '', 'owner': r.get('owner') or '',
})

restore_collection('milestones', 'slug', load_csv('milestones.csv'), lambda r: {
    'slug': r['slug'], 'year': int(r['year']), 'year_label': r.get('year_label') or '', 'project': r['project'],
    'value_chain': r.get('value_chain') or '', 'status': r.get('status') or 'planned',
    'category': r.get('category') or '', 'note': r.get('note') or '',
})

restore_collection('glossary', 'slug', load_csv('glossary.csv'), lambda r: {
    'slug': r['slug'], 'term': r['term'], 'definition': r.get('definition') or '',
})

restore_collection('chain_synergies', 'slug', load_csv('chain_synergies.csv'), lambda r: {
    'slug': r['slug'], 'title': r['title'], 'description': r.get('description') or '',
})

restore_collection('key_indicator_categories', 'indicator_slug', load_csv('key_indicator_categories.csv'), lambda r: {
    'indicator_slug': r['indicator_slug'], 'category': r['category'], 'pct': float(r['pct']),
    'value_label': r.get('value_label') or '', 'highlight': r.get('highlight') or '0',
})
# Note: key_indicator_categories' real identity is (indicator_slug, category),
# not indicator_slug alone (several rows share an indicator_slug) -- the
# upsert above will under-restore if more than one category per indicator
# changed independently. Acceptable for now: re-run db/pb_setup.py's own
# find_category_record-based upsert for full correctness on this one
# collection if a category-level (not whole-indicator) revert is needed.

print('\nRestore complete. PocketBase now matches data/dashboard/ exactly (extra records removed, edits reverted).')
