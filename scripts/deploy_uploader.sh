#!/bin/bash
# Staging-first deploy for the uploader (ADR-019). Same discipline as the brain:
# update code, restart STAGING uploader, verify, then restart PROD uploader.
set -e
U=/opt/mtic-uploader

echo "[deploy-uploader] pulling latest main..."
cd "$U/repo" && git checkout -f main -q && git pull --ff-only -q
cp "$U/repo/uploader/app.py" "$U/app.py"
cp "$U/repo/scripts/promote_staging_to_prod.sh" "$U/promote.sh" && chmod +x "$U/promote.sh"

echo "[deploy-uploader] restarting STAGING uploader (:8210)..."
systemctl restart mtic-uploader-staging
sleep 3
health=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 http://127.0.0.1:8210/)
if [ "$health" != "200" ]; then
  echo "[deploy-uploader] STAGING FAILED (health=$health) — NOT promoting to prod."
  exit 1
fi
echo "[deploy-uploader] staging OK. Promoting to PROD (:8211)..."
systemctl restart mtic-uploader-prod
sleep 3
echo "[deploy-uploader] prod: $(curl -s -o /dev/null -w '%{http_code}' --max-time 8 http://127.0.0.1:8211/)"
echo "[deploy-uploader] done — staging verified, then prod."
