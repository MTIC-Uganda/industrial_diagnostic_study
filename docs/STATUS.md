# MIDD — Current System Status

One always-current page so any agent (Solomon's, the server brain, Hillary's) reads the
latest state from one place instead of diffing the whole repo. Keep this updated whenever
something material changes. Decisions live in the ADRs; this is the live snapshot.

Last updated: 2026-07-12 (live counts auto-refreshed)

## Environments (all on Hetzner 89.167.121.193, behind midd-ug.com via Cloudflare, SSL Full)

| Surface | Production | Staging |
|---|---|---|
| Dashboard | https://midd-ug.com (:8201) | https://staging.midd-ug.com (:8200) |
| Uploader | https://upload.midd-ug.com (:8211) | https://staging-upload.midd-ug.com (:8210) |
| Ask MIDD | https://ask.midd-ug.com (:8221) | https://staging-ask.midd-ug.com (:8220) |
| PocketBase | https://db.midd-ug.com (:8090) | https://staging-db.midd-ug.com (:8091) |

Rule: all development and Jerome's experimentation happen on staging first, then promote.

## Data (single source of truth — ADR-011)

- Live counts (auto): industries 7100 total = 7011 register + curated; with GPS 574; value_chains 9; kpi_indicators 13.

- `industries` is the one establishment table. One row per establishment, keyed by `reg_number`,
  updated in place (columns added over time, blanks where missing). Curated map factories are
  merged in as `FAC-*` rows.
- The distribution **treemaps** read `industries` excluding `FAC-*` (the 7,011 register).
- The industry **locations map** reads `industries` where GPS is present (~574, includes FAC-*).
- `value_chains` (Sankey + value-chain views), `kpi_indicators` (old 6-card overview, legacy —
  superseded by the two below but left in place since `refresh_status.py`'s live count still
  reads it), `key_indicators` + `key_indicator_categories` (the 12 Manufacturing Industry Key
  Indicator cards, 2026-06-24), `diagnostic_datapoints` (value-chain study facts from LLM ingestion).
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

- Solomon: dashboard redesign landed 2026-06-24 (12 indicators as donut/pie with year+source,
  10-fold % /figure toggle, treemap legend/tooltip/back-button) — see TASKS.md for the full
  per-indicator checklist. The 12 indicators + region strip now read from two new PocketBase
  collections, `key_indicators` and `key_indicator_categories` (db/pb_setup.py defines + seeds
  both; CI runs it against prod on every push). CSV fallback stays for local dev / before the
  first seed run lands.
- Jerome: upload documents (register first, then other establishment/sector reports) on staging.
- Hillary: deeper harness loop (feedback improves agents; brain auto-updates records),
  automated staging→prod promotion, containerization.

## Brain / subscriptions

All MIDD server intelligence (Ask MIDD, ingestion, orchestrator) runs on the Claude CLI on the
Hetzner host = Hillary's Max plan, for now. Solomon codes with his own subscription. MIDD gets its
own model/key when containerized and shipped (ADR-012).

## Contributor setup (one-time per clone)

Enable the repo's git hooks so the ADR<->DSL gate works locally before you even push:

    git config core.hooksPath .githooks

Then a commit that changes an ADR without docs/architecture.dsl is blocked at commit time
(--no-verify to override). CI enforces the same gate post-push for everyone.

## Environment model (ADR-013, revised 2026-06-24): code auto-promotes, data promotes on approval

- CODE/dashboard: staging -> prod promotion via CI, health-gated, automatic. Solomon never manually promotes.
- DATA/uploads: all document work happens in staging (upload, extract, review, correct, preview).
  When Jerome is satisfied, "Apply to production" in the staging uploader runs
  scripts/promote_staging_to_prod.sh — backs up prod, copies the exact approved staging
  PocketBase state over (never re-runs the LLM), recreates the prod admin, rebuilds prod.
  Direct prod uploads are disabled; staging+promote is the only path.
- POCKETBASE RESET (down only): refresh_staging_from_prod.sh resets staging to mirror prod,
  discarding staging experiments. Run before a meaningful rehearsal.
- Rule: code promotes on health (machine decides); data promotes on Jerome's click (his judgment).

## Access & navigation

- Dashboards (midd-ug.com, staging.midd-ug.com) are PUBLIC. The four tools (upload, ask, staging-upload, staging-ask) are behind Cloudflare Access — allow-list: arinda.hillary@, jnuwabaasa@, arihosolomon@ (email one-time-PIN login). PocketBase (db, staging-db) keeps its own admin login.
- Each dashboard header has env-aware Upload + Ask MIDD links (prod->prod tools, staging->staging tools), gated by Access.
- The internal Pipeline status tab was removed from the public dashboard.
