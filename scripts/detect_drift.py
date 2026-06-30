#!/usr/bin/env python3
"""
Detect drift between PocketBase's live data and the committed fallback
files in data/dashboard/.

Per ADR-011, all writes are supposed to go through the CSV -> db/pb_setup.py
-> PocketBase pipeline, never a direct edit in the PocketBase admin UI. This
script is the check that catches it if that rule gets broken: it fetches
PocketBase's CURRENT data for every CSV/JSON-backed collection and writes it
into the same files git already tracks, in the same format. If that produces
a git diff, something changed in PocketBase outside the normal pipeline.

Used by the scheduled "Drift Check" CI job (.github/workflows/deploy.yml):
that job runs this script, and if it changes any files, opens a PR showing
exactly what's different. From there:
  - Merge the PR  -> accepts the PocketBase-side change (git catches up to
    match what's now live).
  - Close the PR (don't merge), then run scripts/restore_from_git.py
    -> rejects the change (pushes git's last-known values back into
    PocketBase, including deleting any record PocketBase has that git
    doesn't, which db/pb_setup.py's upsert-only seeding never does).

Scope: the CSV/JSON-backed "simple" collections wired up on 2026-06-30
(key_indicators, key_indicator_categories, kpi_indicators, macro_trend,
sector_comparison, risk_register, milestones, glossary, chain_synergies).
Does NOT cover industries/value_chains/facilities/diagnostic_datapoints
(populated by the document-ingestion pipeline, not a CSV fallback -- a
different reconciliation problem) or the explorer_* collections (JSON-blob
shaped; same idea would apply but isn't built here yet).

Usage:
    $env:PB_URL = "http://89.167.121.193:8090"
    python scripts/detect_drift.py
"""

import csv, json, os, sys, urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data' / 'dashboard'

PB_URL = os.environ.get('PB_URL', '').rstrip('/')
if not PB_URL:
    sys.exit('ERROR: set PB_URL (e.g. http://89.167.121.193:8090) — drift can only be checked against a live PocketBase.')

def pb_get(collection, sort=None):
    items, page = [], 1
    while True:
        url = f'{PB_URL}/api/collections/{collection}/records?perPage=500&page={page}'
        if sort:
            url += f'&sort={urllib.parse.quote(sort)}'
        try:
            with urllib.request.urlopen(url) as r:
                payload = json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f'  (collection {collection} does not exist in PocketBase — skipping)')
                return None
            raise
        items.extend(payload.get('items', []))
        if page >= payload.get('totalPages', 1) or not payload.get('items'):
            break
        page += 1
    return items

def write_csv(path, fieldnames, rows):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in fieldnames})

def num_str(v):
    """PocketBase numbers round-trip as floats (3.0); CSVs were hand-written
    with the minimal form (3). Strip a trailing .0 so a value that hasn't
    actually changed doesn't show up as drift over formatting alone."""
    if v is None or v == '':
        return ''
    f = float(v)
    return str(int(f)) if f == int(f) else str(f)

# ── Per-collection: fetch PocketBase, write back into the committed file ──────

def sync_key_indicators():
    rows = pb_get('key_indicators', sort='display_order')
    if rows is None:
        return
    out = [{
        'slug': r['slug'], 'label': r['label'], 'kind': r['kind'],
        'value': r.get('value', ''), 'pct': num_str(r.get('pct')),
        'sub_value': r.get('sub_value', ''), 'icon': r.get('icon', ''),
        'color': r.get('color', ''), 'rest_color': r.get('rest_color', ''),
        'year': r.get('year', ''), 'source': r.get('source', ''),
        'confidence': r.get('confidence', 'estimated'),
        'display_order': num_str(r.get('display_order')),
    } for r in rows]
    write_csv(DATA / 'key_indicators.csv',
              ['slug','label','kind','value','pct','sub_value','icon','color','rest_color','year','source','confidence','display_order'], out)

def sync_key_indicator_categories():
    rows = pb_get('key_indicator_categories', sort='indicator_slug,display_order')
    if rows is None:
        return
    out = [{
        'indicator_slug': r['indicator_slug'], 'category': r['category'],
        'pct': num_str(r.get('pct')), 'value_label': r.get('value_label', ''),
        'highlight': r.get('highlight', '0'), 'display_order': num_str(r.get('display_order')),
    } for r in rows]
    write_csv(DATA / 'key_indicator_categories.csv',
              ['indicator_slug','category','pct','value_label','highlight','display_order'], out)

def sync_kpi_indicators():
    rows = pb_get('kpi_indicators', sort='display_order')
    if rows is None:
        return
    out = [{
        'id': r['slug'], 'label': r['label'],
        'current_value': r.get('current_value', ''), 'current_pct': num_str(r.get('current_pct')),
        'ndp_value': r.get('ndp_value', ''), 'ndp_pct': num_str(r.get('ndp_pct')),
        'tenfold_value': r.get('tenfold_value', ''), 'tenfold_pct': num_str(r.get('tenfold_pct')),
        'sub_value': r.get('sub_value', ''), 'confidence': r.get('confidence', 'estimated'),
        'source': r.get('source', ''),
    } for r in rows]
    write_csv(DATA / 'overview_kpis.csv',
              ['id','label','current_value','current_pct','ndp_value','ndp_pct','tenfold_value','tenfold_pct','sub_value','confidence','source'], out)

def sync_macro_trend():
    rows = pb_get('macro_trend', sort='display_order')
    if rows is None:
        return
    out = [{
        'id': r['slug'], 'label': r['label'],
        'fy2021_value': r.get('fy2021_value', ''), 'fy2025_value': r.get('fy2025_value', ''),
        'fy2021_pct': num_str(r.get('fy2021_pct')), 'fy2025_pct': num_str(r.get('fy2025_pct')),
        'delta': r.get('delta', ''), 'direction': r.get('direction', 'up'),
        'trajectory': r.get('trajectory', ''), 'trajectory_labels': r.get('trajectory_labels', ''),
        'confidence': r.get('confidence', 'estimated'), 'source': r.get('source', ''),
    } for r in rows]
    write_csv(DATA / 'macro_trend.csv',
              ['id','label','fy2021_value','fy2025_value','fy2021_pct','fy2025_pct','delta','direction','trajectory','trajectory_labels','confidence','source'], out)

def sync_sector_comparison():
    rows = pb_get('sector_comparison', sort='display_order')
    if rows is None:
        return
    out = [{
        'slug': r['slug'], 'chart': r['chart'], 'sector': r['sector'],
        'value_label': r.get('value_label', ''), 'usd_label': r.get('usd_label', ''),
        'pct': num_str(r.get('pct')), 'highlight': r.get('highlight', '0'),
    } for r in rows]
    write_csv(DATA / 'sector_comparison.csv',
              ['slug','chart','sector','value_label','usd_label','pct','highlight'], out)

def sync_risk_register():
    rows = pb_get('risk_register', sort='display_order')
    if rows is None:
        return
    out = [{
        'slug': r['slug'], 'risk': r['risk'], 'category': r.get('category', ''),
        'severity': r.get('severity', 'medium'), 'likelihood': r.get('likelihood', 'medium'),
        'mitigation': r.get('mitigation', ''), 'owner': r.get('owner', ''),
    } for r in rows]
    write_csv(DATA / 'risk_register.csv',
              ['slug','risk','category','severity','likelihood','mitigation','owner'], out)

def sync_milestones():
    rows = pb_get('milestones', sort='display_order')
    if rows is None:
        return
    out = [{
        'slug': r['slug'], 'year': num_str(r.get('year')), 'year_label': r.get('year_label', ''),
        'project': r['project'], 'value_chain': r.get('value_chain', ''),
        'status': r.get('status', 'planned'), 'category': r.get('category', ''), 'note': r.get('note', ''),
    } for r in rows]
    write_csv(DATA / 'milestones.csv',
              ['slug','year','year_label','project','value_chain','status','category','note'], out)

def sync_glossary():
    rows = pb_get('glossary', sort='display_order')
    if rows is None:
        return
    out = [{'slug': r['slug'], 'term': r['term'], 'definition': r.get('definition', '')} for r in rows]
    write_csv(DATA / 'glossary.csv', ['slug','term','definition'], out)

def sync_chain_synergies():
    rows = pb_get('chain_synergies', sort='display_order')
    if rows is None:
        return
    out = [{'slug': r['slug'], 'title': r['title'], 'description': r.get('description', '')} for r in rows]
    write_csv(DATA / 'chain_synergies.csv', ['slug','title','description'], out)

print(f'Checking PocketBase ({PB_URL}) against committed data/dashboard/ files...\n')
for fn in [sync_key_indicators, sync_key_indicator_categories, sync_kpi_indicators,
           sync_macro_trend, sync_sector_comparison, sync_risk_register,
           sync_milestones, sync_glossary, sync_chain_synergies]:
    fn()
print('\nDone. Run `git diff --stat data/dashboard/` to see if anything changed.')
