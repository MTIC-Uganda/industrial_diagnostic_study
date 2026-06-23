#!/bin/bash
# APPLY TO PRODUCTION (ADR-013, revised): one-way, explicit promotion of the
# approved STAGING state to PRODUCTION. Copies the staging PocketBase -> prod,
# recreates the prod automation admin, rebuilds the prod dashboard from it.
# The exact reverse of refresh_staging_from_prod.sh. Deterministic: what was
# approved in staging is byte-for-byte what goes live. NEVER runs the LLM.
set -e
PROD=/var/lib/pocketbase
STG=/var/lib/pocketbase-staging

echo "[promote] checkpointing staging WAL..."
sqlite3 "$STG/data.db" 'PRAGMA wal_checkpoint(TRUNCATE);' >/dev/null 2>&1 || true

echo "[promote] stopping prod PocketBase..."
systemctl stop pocketbase
sleep 1

echo "[promote] backing up current prod data (recoverable rollback)..."
cp -a "$PROD/data.db" "$PROD/data.db.pre-promote"

echo "[promote] copying staging data -> prod..."
cp -a "$STG/data.db" "$PROD/data.db"
cp -a "$STG/logs.db" "$PROD/logs.db" 2>/dev/null || true

echo "[promote] restoring prod admins (staging copy overwrote the admin table)..."
while read -r email pass; do
  /usr/local/bin/pocketbase admin create "$email" "$pass" --dir="$PROD" >/dev/null 2>&1 \
    || /usr/local/bin/pocketbase admin update "$email" "$pass" --dir="$PROD" >/dev/null 2>&1 || true
done <<'ADMINS'
admin@midd-ug.com MiddAdmin2026
automation@mtic.local AutoMtic2026Prod
ADMINS

echo "[promote] starting prod PocketBase..."
systemctl start pocketbase
sleep 4

echo "[promote] rebuilding the prod dashboard from prod PocketBase..."
export HOME=/root PB_URL=http://127.0.0.1:8090 PB_ADMIN_EMAIL=automation@mtic.local PB_ADMIN_PASSWORD=AutoMtic2026Prod
cd /opt/mtic-uploader/repo-prod && git checkout -f main -q && git pull --ff-only -q
python3 scripts/generate_dashboard.py 2>&1 | grep -iE "Treemaps|Locations" || true
cp report/sources-of-truth.html /var/www/mtic-prod/index.html

IND=$(curl -s "http://127.0.0.1:8090/api/collections/industries/records?perPage=1" | python3 -c "import sys,json;print(json.load(sys.stdin).get('totalItems','?'))" 2>/dev/null)
echo "[promote] DONE — production now reflects the approved staging state (industries=$IND)."

# Acknowledge the promotion in the MTIC WhatsApp group (data promotions are not git
# events, so the receiver can't see them — notify directly via the bridge).
curl -s -X POST http://localhost:8080/api/send -H 'Content-Type: application/json' \
  -d "{\"recipient\":\"256775102684-1629659312@g.us\",\"message\":\"MIDD: a reviewed document was promoted to production. The live dashboard now reflects it (industries=$IND).\"}" \
  >/dev/null 2>&1 || true
