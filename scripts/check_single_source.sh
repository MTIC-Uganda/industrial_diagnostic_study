#!/bin/bash
# ── SINGLE SOURCE OF TRUTH guard (ADR-017) ────────────────────────────────────
# The dashboard + explorer are built ONLY from PocketBase, with NO file fallback.
# (The data/dashboard/*.csv|json files are a git-tracked BACKUP mirror of PocketBase,
# kept in sync PB->files by the scheduled Drift Check — they are downstream of PB,
# never a source, and the generators must never read them.) This runs in CI
# (blocking the build/merge) and as a pre-commit hook, so NO agent can quietly
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

# (Note: we do NOT forbid files under data/dashboard/ — they are the PB->files
# backup mirror maintained by the Drift Check. The real guarantee is that the
# GENERATORS never read them, enforced by checks 1 and 2 above.)

if [ "$fail" -eq 0 ]; then
  echo "single-source guard: OK (PocketBase is the only data source, ADR-017)"
else
  echo ""
  echo "SINGLE-SOURCE GUARD FAILED (ADR-017): the dashboard/explorer must read only"
  echo "from PocketBase. Put the data in PocketBase; do not add files or fallbacks."
fi
exit $fail
