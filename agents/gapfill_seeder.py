#!/usr/bin/env python3
"""
MTIC Gap-fill Seeder

Triggered by the gapfill-seed CI job after Jerome merges a gap-fill PR.
Reads all JSON files in data/proposed/, marks the records approved, and
upserts them into PocketBase. The synthesis + review agents then re-run
automatically (also in the same CI job) to pick up the new data.

Usage:
    python agents/gapfill_seeder.py
"""

import json, os, sys, datetime, urllib.request, urllib.error
from pathlib import Path

ROOT         = Path(__file__).resolve().parent.parent
PROPOSED_DIR = ROOT / 'data' / 'proposed'

PB_URL   = os.environ.get('PB_URL', 'http://89.167.121.193:8090').rstrip('/')
PB_EMAIL = os.environ.get('PB_ADMIN_EMAIL', '')
PB_PASS  = os.environ.get('PB_ADMIN_PASSWORD', '')

RUN_ID   = datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')


def pb_auth() -> str | None:
    for path in ['/api/admins/auth-with-password', '/api/collections/_superusers/auth-with-password']:
        try:
            req = urllib.request.Request(
                f'{PB_URL}{path}',
                data=json.dumps({'identity': PB_EMAIL, 'password': PB_PASS}).encode(),
                method='POST',
                headers={'Content-Type': 'application/json'},
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read()).get('token')
        except urllib.error.URLError:
            continue
    return None


def pb_upsert(token: str, records: list[dict]):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}',
    }
    seeded = 0
    for rec in records:
        # Check if record already exists by (field_id, value_chain_id)
        fid = rec.get('field_id', '')
        vc  = rec.get('value_chain_id', '')
        try:
            search_url = (
                f'{PB_URL}/api/collections/diagnostic_datapoints/records'
                f'?filter=(field_id="{fid}"&&value_chain_id="{vc}")'
                f'&perPage=1'
            )
            with urllib.request.urlopen(urllib.request.Request(search_url, headers=headers)) as r:
                existing = json.loads(r.read())
            items = existing.get('items', [])

            rec['approval_status'] = 'approved'
            rec['approved_by']     = 'gap_fill_pr_merge'
            rec['approved_at']     = RUN_ID
            rec['ingestion_method']= 'web_gap_fill'

            if items:
                # Update existing record
                rec_id = items[0]['id']
                req = urllib.request.Request(
                    f'{PB_URL}/api/collections/diagnostic_datapoints/records/{rec_id}',
                    data=json.dumps(rec).encode(),
                    method='PATCH',
                    headers=headers,
                )
            else:
                req = urllib.request.Request(
                    f'{PB_URL}/api/collections/diagnostic_datapoints/records',
                    data=json.dumps(rec).encode(),
                    method='POST',
                    headers=headers,
                )
            with urllib.request.urlopen(req, timeout=15):
                seeded += 1
        except urllib.error.URLError as e:
            print(f'  WARN: Could not seed {fid}/{vc}: {e}')
    return seeded


def run():
    print(f'\n══ MTIC Gap-fill Seeder  run={RUN_ID} ══')

    proposal_files = sorted(PROPOSED_DIR.glob('web_gap_fill_*.json'))
    if not proposal_files:
        print('  No proposal files found in data/proposed/ — nothing to seed.')
        return

    all_records: list[dict] = []
    for f in proposal_files:
        try:
            records = json.loads(f.read_text('utf-8'))
            if isinstance(records, list):
                all_records.extend(records)
                print(f'  Loaded {len(records)} proposals from {f.name}')
        except (json.JSONDecodeError, OSError) as e:
            print(f'  WARN: Could not read {f.name}: {e}')

    if not all_records:
        print('  No valid proposals found.')
        return

    print(f'  Total: {len(all_records)} approved proposals to seed')

    token = pb_auth()
    if not token:
        sys.exit('ERROR: PocketBase authentication failed. '
                 'Check PB_ADMIN_EMAIL and PB_ADMIN_PASSWORD.')

    seeded = pb_upsert(token, all_records)
    print(f'  Seeded {seeded}/{len(all_records)} records to PocketBase')
    print('  Synthesis and review agents will now re-run on the updated data.')


if __name__ == '__main__':
    run()
