# Document Uploader — How It Works and How to Access It

Built 2026-06-23. This is the no-Git path for getting documents into the system,
per ADR-010. Jerome opens a web page, describes what he wants in as much detail as
he likes, attaches a document of any form, and the system extracts the data into
PocketBase and rebuilds the dashboard. Everything runs on the Hetzner host.

## What happens when a document is uploaded

1. Jerome opens the uploader, picks the value chain, writes his full intent, attaches the file, submits.
2. The file is saved into `data/<value-chain>/` (exactly where every other source document lives) and a `<file>.task.md` sidecar is written carrying his intent. The change is committed.
3. The orchestrator (`scripts/process_upload.py`) runs on the host:
   - The Claude CLI reads the intent and states what the document is and what to do.
   - Register (manufacturing-overview) → deterministic parse → `industries.json` → seed the PocketBase `industries` collection. Value-chain study document → the LLM ingestion agent → `diagnostic_datapoints`.
   - The dashboard is rebuilt with the distribution treemaps aggregated live from PocketBase, then published.
4. The dashboard updates within a few minutes.

## Two environments — do not confuse them

| | STAGING (rehearsal) | PRODUCTION (real) |
|---|---|---|
| Uploader | http://89.167.121.193:8210 | http://89.167.121.193:8211 |
| Dashboard | http://89.167.121.193:8200 | http://89.167.121.193:8201 |
| PocketBase | http://89.167.121.193:8091 | http://89.167.121.193:8090 |
| Commits | branch `uploads-staging`, not pushed | `main`, pushed with `[skip ci]` |
| Use for | testing, safe to break | real Commissioner-facing data |

Passwords for the uploaders and the PocketBase automation account are shared
separately (not stored in Git). Jerome's own PocketBase admin login is unchanged.

## Services on the host (systemd)

- `mtic-uploader-staging` / `mtic-uploader-prod` — the upload web apps
- `pocketbase` (prod, :8090) / `pocketbase-staging` (:8091) — the datastores
- Orchestrator logs: `/var/log/mtic-orchestrator-staging.log`, `/var/log/mtic-orchestrator-prod.log`

## Notes / limits

- The brain is the Claude CLI on the host; it does not run in GitHub Actions. Ingestion therefore runs on the host, not in CI.
- The register parser is deterministic and matches the August 2025 layout. A genuinely new table layout needs the LLM extraction path (the same one used for value-chain study documents).
- Treemaps read from PocketBase, with the committed static `treemap_*.json` as a fallback if PocketBase is unavailable.

See ADR-010 for the design and `docs/solomon-brief-intake-pipeline.md` for the implementation plan.
