#!/bin/bash
# Staging-first deploy for the Ask MIDD brain (ADR-019). The brain is not part of
# the dashboard CI pipeline; this brings it into the same discipline: update the
# code, restart STAGING, verify it, and only then restart PROD. Both services run
# the same /opt/midd-brain/*.py, but each only picks up new code on restart — so
# prod keeps serving the old code until staging has passed.
set -e
BRAIN=/opt/midd-brain
FILES="app.py brief_lib.py query_tool.py"

echo "[deploy-brain] pulling latest main..."
cd "$BRAIN/repo" && git checkout -f main -q && git pull --ff-only -q
for f in $FILES; do cp "$BRAIN/repo/midd-brain/$f" "$BRAIN/$f"; done

echo "[deploy-brain] restarting STAGING brain (:8220)..."
systemctl restart midd-brain-staging
sleep 4

health=$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 http://127.0.0.1:8220/health)
alen=$(curl -s -X POST http://127.0.0.1:8220/api/ask -H 'Content-Type: application/json' \
        -d '{"q":"How many registered manufacturing establishments are in the Northern region?"}' \
        --max-time 150 | python3 -c "import sys,json;print(len(json.load(sys.stdin).get('answer','')))" 2>/dev/null || echo 0)

if [ "$health" != "200" ] || [ "${alen:-0}" -lt 15 ]; then
  echo "[deploy-brain] STAGING FAILED (health=$health, answer_len=$alen) — NOT promoting to prod."
  exit 1
fi
echo "[deploy-brain] staging OK (health=$health, answer_len=$alen). Promoting to PROD (:8221)..."
systemctl restart midd-brain-prod
sleep 4
echo "[deploy-brain] prod health: $(curl -s -o /dev/null -w '%{http_code}' --max-time 8 http://127.0.0.1:8221/health)"
echo "[deploy-brain] done — staging verified, then prod."
