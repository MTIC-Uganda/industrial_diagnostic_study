# ADR-019: Every Component Is Staging-First; Staging Mirrors Production

## Status: Accepted (2026-07-03)

## Context

The environment model (ADR-013) made the *dashboard* (via CI) and the *data* (via Apply-to-production) staging-first. But two components were still deployed straight to prod by hand: the **Ask MIDD brain** and the **uploader** (both are FastAPI apps on the box, outside the CI pipeline). That is how a chatbot change was validated on prod instead of staging. Hillary's requirement: staging must be a faithful mirror of prod, and *nothing* reaches prod without passing staging first.

## Decision

**No component is deployed straight to prod. Each flows staging → verify → prod, and staging is kept a faithful mirror of prod.**

Per component:

| Component | Staging-first mechanism |
|---|---|
| Dashboard (code) | CI: build → deploy staging → health-check → promote prod → auto-merge (ADR-006/008/016) |
| Data (PocketBase) | Jerome uploads to the **staging** uploader → ingest → review → **Apply to production** copies the approved staging PB to prod (ADR-013). `refresh_staging_from_prod.sh` resets staging to a clean prod mirror. |
| Ingestion | Runs on **staging** (staging uploader → staging orchestrator → staging PB). The *result* is what gets promoted — the LLM never re-runs in prod. So ingestion is staging-first by construction. |
| Ask MIDD brain | **CI job `deploy-brain`** (runs on main when `midd-brain/` changes, after build+tests) SSHes to the box and runs `scripts/deploy_brain.sh`: restart **staging** brain → verify (health + a live query) → only then restart **prod** brain. (Shared file, but each service picks up new code only on restart, so prod serves old code until staging passes.) |
| Uploader | **CI job `deploy-uploader`** runs `scripts/deploy_uploader.sh`: same pattern (restart staging → verify → restart prod). |

**Staging mirrors prod:** at every Apply-to-production, staging *is* prod (promotion copies staging→prod). Between changes, staging is the workspace; `refresh_staging_from_prod.sh` re-mirrors it from prod whenever a clean baseline is wanted. Code deploys land on staging first for every component, so what you validate on staging is what prod becomes.

## Consequences

**Better:** one consistent rule across code, data, brain, and uploader — validate on staging, promote to prod, never test in prod. The brain and uploader are no longer straight-to-prod exceptions.

**Worse / watch for:** the brain/uploader deploys are now **CI jobs** (`deploy-brain`, `deploy-uploader`) triggered on `main` when their code changes — no hand-run script, no `cp && restart` shortcut. A staging-verify failure fails the CI job (prod untouched) and shows up as a `workflow_run` failure in the group. Staging PB drifts from prod as new uploads accumulate (by design — it's the workspace); run `refresh_staging_from_prod.sh` for a clean mirror before a from-scratch rehearsal.

## Relationship to other ADRs
- ADR-013 — data/code promotion model this generalises to every component.
- ADR-016 — the dashboard's runtime hostname split (staging vs prod surfaces).
