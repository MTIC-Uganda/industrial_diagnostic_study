#!/bin/bash
# Refresh the STAGING environment to mirror current PRODUCTION (ADR-013).
# Data flows DOWN only: copies prod PocketBase -> staging PocketBase and rebuilds
# the staging dashboard from it. Run whenever you want a clean, realistic sandbox.
# This NEVER touches prod. There is no reverse (staging never promotes data to prod).
set -e
PROD_DIR=/var/lib/pocketbase
STG_DIR=/var/lib/pocketbase-staging
STG_ADMIN_EMAIL=staging@mtic.local
STG_ADMIN_PASS=StagingMtic2026

echo "[refresh] checkpointing prod WAL so the copy is current..."
sqlite3 "$PROD_DIR/data.db" 'PRAGMA wal_checkpoint(TRUNCATE);' >/dev/null 2>&1 || true

echo "[refresh] stopping staging PocketBase..."
systemctl stop pocketbase-staging
sleep 1

echo "[refresh] copying prod data -> staging..."
cp -a "$PROD_DIR/data.db" "$STG_DIR/data.db"
cp -a "$PROD_DIR/logs.db" "$STG_DIR/logs.db" 2>/dev/null || true

echo "[refresh] restoring the staging admins (prod copy overwrote the admin table)..."
while read -r email pass; do
  /usr/local/bin/pocketbase admin create "$email" "$pass" --dir="$STG_DIR" >/dev/null 2>&1 \
    || /usr/local/bin/pocketbase admin update "$email" "$pass" --dir="$STG_DIR" >/dev/null 2>&1 || true
done <<ADMINS
admin@midd-ug.com MiddAdmin2026
$STG_ADMIN_EMAIL $STG_ADMIN_PASS
ADMINS

echo "[refresh] starting staging PocketBase..."
systemctl start pocketbase-staging
sleep 4

echo "[refresh] rebuilding the staging dashboard from staging PocketBase..."
export HOME=/root PB_URL=http://127.0.0.1:8091 PB_ADMIN_EMAIL="$STG_ADMIN_EMAIL" PB_ADMIN_PASSWORD="$STG_ADMIN_PASS"
cd /opt/mtic-uploader/repo && git checkout -f main -q && git pull --ff-only -q
python3 scripts/generate_dashboard.py 2>&1 | grep -iE "Treemaps|Locations" || true
cp report/sources-of-truth.html /var/www/mtic-staging/index.html

IND=$(curl -s "http://127.0.0.1:8091/api/collections/industries/records?perPage=1" | python3 -c "import sys,json;print(json.load(sys.stdin).get('totalItems','?'))" 2>/dev/null)
echo "[refresh] DONE — staging now mirrors prod (industries=$IND). Staging dashboard rebuilt."
