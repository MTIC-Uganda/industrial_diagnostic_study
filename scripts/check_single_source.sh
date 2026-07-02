#!/bin/bash
# ── SINGLE SOURCE OF TRUTH guard (ADR-017) ────────────────────────────────────
# The dashboard + explorer are built ONLY from PocketBase. No committed-file data
# source, no fallback. This runs in CI (blocking the build/merge) and as a
# pre-commit hook, so NO agent — Solomon's, Hillary's, or any other — can quietly
# reintroduce a file-based data source. Exit non-zero on any violation.
set -u
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$ROOT" || exit 1
fail=0
GENS="scripts/generate_dashboard.py scripts/generate_explorer_data.py"

# 1. Each generator must keep its "PB_URL required" guard and its raising fallbacks.
for g in $GENS; do
  [ -f "$g" ] || continue
  grep -q "SINGLE SOURCE (ADR-017): PB_URL is required" "$g" \
    || { echo "FAIL: $g lost its PB_URL-required guard"; fail=1; }
  grep -q "SINGLE SOURCE VIOLATION" "$g" \
    || { echo "FAIL: $g lost its file-read guard (a file fallback was reintroduced?)"; fail=1; }
done

# 2. No generator may read a data file directly. csv.DictReader / reading from the
#    DATA dir only exist in a real (forbidden) loader; the guard versions sys.exit.
if grep -nE "csv\.DictReader|json\.loads\(\(DATA|open\(\s*DATA|DATA / name" $GENS 2>/dev/null; then
  echo "FAIL: a generator reads a data file directly — data must come from PocketBase"; fail=1
fi

# 3. No NEW committed data files under data/dashboard/ (the duplication surface).
BASE="$(git merge-base HEAD origin/main 2>/dev/null || echo '')"
if [ -n "$BASE" ]; then
  ADDED="$(git diff --diff-filter=A --name-only "$BASE" HEAD 2>/dev/null | grep -E '^data/dashboard/.*\.(csv|json)$' || true)"
  if [ -n "$ADDED" ]; then
    echo "FAIL: new committed data files under data/dashboard/ (single-source bypass):"
    echo "$ADDED" | sed 's/^/  - /'; fail=1
  fi
fi

if [ "$fail" -eq 0 ]; then
  echo "single-source guard: OK (PocketBase is the only data source, ADR-017)"
else
  echo ""
  echo "SINGLE-SOURCE GUARD FAILED (ADR-017): the dashboard/explorer must read only"
  echo "from PocketBase. Put the data in PocketBase; do not add files or fallbacks."
fi
exit $fail
