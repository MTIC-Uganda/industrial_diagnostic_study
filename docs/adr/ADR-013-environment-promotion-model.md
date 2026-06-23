# ADR-013: Environment Model — Code Up, Data Down

## Status: Accepted (2026-06-23)

## Context

Staging and production exist for all three planes (dashboard, uploader, PocketBase), but the promotion semantics differ by plane and were unclear. The dashboard/code path has a real staging→prod promotion (CI), so that one felt clear. But "what does staging mean for the uploader?" and "how do the two PocketBases relate?" were muddled, which made it risky to use staging confidently.

## Decision

One rule: **code flows up, data flows down, data never flows up.**

1. **Code / dashboard — promotion is real (up).** Solomon pushes a branch; CI builds and deploys to the staging dashboard; if healthy it is promoted to the prod dashboard and merged to main (ADR-006/008). What is promoted is the built dashboard (UI/code).

2. **Uploads — no promotion; staging is a rehearsal.** The staging uploader lets Jerome rehearse a document: confirm it extracts correctly and renders right on the staging dashboard, against a copy of prod data, with zero effect on live data. The prod uploader is the real action: it lands the document in the repo and the live datastore and rebuilds the public dashboard. A staging upload is never promoted; when Jerome is satisfied, he re-uploads the same document to the prod uploader. The extraction is deterministic, so prod matches the staging rehearsal. Re-running a cheap, deterministic upload is safer than promoting half-processed data.

3. **PocketBase — refresh down only.** Prod PocketBase is the single source of truth for live data. Staging PocketBase is a disposable copy that staging rehearsals write to harmlessly. Sync is prod→staging only, via `scripts/refresh_staging_from_prod.sh` (copies prod data into staging and rebuilds the staging dashboard). There is no staging→prod data path; prod data changes only through a real prod upload or the prod admin UI.

## Consequences

**Better:**
- A single memorable rule removes the confusion: code up, data down, never data up.
- Staging is a safe, faithful sandbox: refresh it from prod, rehearse, and nothing you do there can harm live data.
- No fragile "promote half-processed data" machinery; the real action is simply re-done in prod, deterministically.

**Worse / watch for:**
- Staging data drifts from prod between refreshes (staging uploads accumulate there). Run `refresh_staging_from_prod.sh` to reset to current prod before a meaningful rehearsal.
- The staging admin account is overwritten by the prod copy on refresh; the refresh script recreates it.
- A document must be uploaded twice (staging then prod) for a "tested then live" flow. Acceptable; it is the safe trade.

## Relationship to other ADRs

- ADR-006 (staging/prod deploy pipeline) — the code promotion path.
- ADR-009 / ADR-011 (PocketBase, single source) — the data this governs.
- ADR-010 (uploader / intake) — the upload action that this says is re-done in prod rather than promoted.
