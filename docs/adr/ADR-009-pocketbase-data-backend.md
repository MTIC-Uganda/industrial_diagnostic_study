# ADR-009: PocketBase as Live Data Backend

## Status: Accepted (Phase 1+ in production)

## Context

Phase 1 reports are complete. Phase 2 requires Jerome to edit live data frequently without touching Git or the terminal. Static files (hardcoded JSON, CSV) require a rebuild and deploy cycle even for tiny data changes. The dashboard needs to reflect the latest data automatically.

Evaluation matrix:
- **Supabase:** PostgreSQL, full-featured, $25+/month, learning curve
- **Neon:** PostgreSQL serverless, $0.3/compute-hour, cold starts
- **Firebase:** Google's realtime DB, $0.1/100k reads, vendor lock-in
- **PocketBase:** Single binary, embedded SQLite, zero cost, no DevOps

## Decision

**PocketBase (https://pocketbase.io)** on Hetzner port 8090.

Single binary that runs on the existing Hetzner server. No additional infrastructure, no monthly cost, no auth complexity. Jerome gets a web admin UI (`:8090/_/`) to edit data like a spreadsheet. CI reads data via REST API on every push and regenerates the dashboard.

## Consequences

**Better:**
- Zero cost (vs $25/mo Supabase, $250/mo enterprise Postgres)
- No DevOps: runs on Hetzner alongside nginx/staging/prod, managed by systemd
- No learning curve: Jerome uses a web form, not SQL or terminal
- Schema flexibility: Jerome can add/remove fields without touching code
- Offline capable: SQLite file can be backed up and synced to Git (optional)
- Full ownership: data lives on MTIC's own server, not a third party

**Worse:**
- Single-server database (no HA/replication out of the box; acceptable for MTIC)
- SQLite row-size limits (~2GB per row; not a concern for diagnostic data)
- No built-in audit log (add one if compliance requires it)

**Watch for:**
- Data backup strategy: set up automated `.db` exports to GitHub
- Concurrent edits: PocketBase handles them, but batch imports should avoid conflicts
- Admin account security: change `MticPB2026!Admin` in production
- API rate limits: none by default; add if needed (unlikely for small team)

## Implementation

Installed 2026-06-13 on Hetzner 89.167.121.193:8090.

- Admin account: admin@mtic.go.ug (password set)
- Systemd service: `pocketbase.service` (auto-restart on failure)
- Data dir: `/var/lib/pocketbase/pb_data/` (SQLite file + media uploads)
- UFW firewall: port 8090 open to 0.0.0.0

## Phase 2 Integration

CI pipeline (`scripts/generate_dashboard.py`) reads PocketBase via REST API → regenerates dashboard on every push. Jerome's edits in the web UI trigger a manual GitHub push (or auto-webhook later), which re-runs CI, which pulls fresh data, which deploys.

ADR-007 (agentic automation) still applies: Phase 2 agents will read from PocketBase instead of hardcoded files.
