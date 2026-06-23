# MIDD — Current System Status

One always-current page so any agent (Solomon's, the server brain, Hillary's) reads the
latest state from one place instead of diffing the whole repo. Keep this updated whenever
something material changes. Decisions live in the ADRs; this is the live snapshot.

Last updated: 2026-06-23

## Environments (all on Hetzner 89.167.121.193, behind midd-ug.com via Cloudflare, SSL Full)

| Surface | Production | Staging |
|---|---|---|
| Dashboard | https://midd-ug.com (:8201) | https://staging.midd-ug.com (:8200) |
| Uploader | https://upload.midd-ug.com (:8211) | https://staging-upload.midd-ug.com (:8210) |
| Ask MIDD | :8221 (friendly URL pending) | :8220 (friendly URL pending) |
| PocketBase | https://db.midd-ug.com (:8090) | https://staging-db.midd-ug.com (:8091) |

Rule: all development and Jerome's experimentation happen on staging first, then promote.

## Data (single source of truth — ADR-011)

- `industries` is the one establishment table. One row per establishment, keyed by `reg_number`,
  updated in place (columns added over time, blanks where missing). Curated map factories are
  merged in as `FAC-*` rows.
- The distribution **treemaps** read `industries` excluding `FAC-*` (the 7,011 register).
- The industry **locations map** reads `industries` where GPS is present (~574, includes FAC-*).
- `value_chains` (Sankey + value-chain views), `kpi_indicators` (overview), `diagnostic_datapoints`
  (value-chain study facts from LLM ingestion).
- Current prod `industries`: 7,100 rows (7,011 register + 89 curated).

## Pipeline

- Documents enter via the uploader → committed to `data/<value-chain>/` + a `<file>.task.md`
  intent sidecar → orchestrator (`scripts/process_upload.py`) on Hetzner: Claude CLI reads the
  intent, routes register→deterministic parse / sector→LLM ingestion, seeds PocketBase, rebuilds
  + publishes the dashboard.
- Duplicate documents are rejected by content hash (even if renamed).
- Treemaps/locations build from PocketBase (static JSON fallback when PB is off — Solomon's local).

## Done (phase 2)

ADR-011 schema; uploader dedup; domain + HTTPS; single-source migration (map + treemaps from
`industries`, staging + prod); Ask MIDD scoped brain v1 (read-only, feedback logged).

## In flight / next

- Solomon: dashboard redesign (12 indicators as donut/pie with year+source, 10-fold toggle,
  treemap legend/tooltip/back-button) — see TASKS.md and the 2026-06-23 dashboard review.
- Jerome: upload documents (register first, then other establishment/sector reports) on staging.
- Hillary: deeper harness loop (feedback improves agents; brain auto-updates records),
  automated staging→prod promotion, containerization.

## Brain / subscriptions

All MIDD server intelligence (Ask MIDD, ingestion, orchestrator) runs on the Claude CLI on the
Hetzner host = Hillary's Max plan, for now. Solomon codes with his own subscription. MIDD gets its
own model/key when containerized and shipped (ADR-012).
