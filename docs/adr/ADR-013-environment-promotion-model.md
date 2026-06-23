# ADR-013: Environment Model — Code Auto-Promotes, Data Promotes on Approval

## Status: Accepted (2026-06-23), revised (2026-06-24)

## Context

Staging and production exist for all three planes (dashboard, uploader, PocketBase). The first version of this ADR said "code up, data down, data never up": a tested document was re-uploaded to prod rather than promoted. In practice that loses the refinement — re-running the LLM in prod can extract differently than the version Jerome approved in staging, and any corrections he made in staging would not carry over. Hillary's clearer model: **staging is the workshop, production is the showroom; nothing reaches prod except by an explicit "Apply to production" that promotes the exact approved state.**

## Decision

Two promotions, gated differently because "good" means different things.

1. **Code / dashboard — auto-promotes, health-gated (up).** Solomon pushes (a branch normally, or main for a hotfix). CI always builds → deploys to the **staging** dashboard → health-check → if healthy, promotes to **prod** and merges to main (ADR-006/008). Staging is always in the path; there is no way to skip it. "Good" is objective (does it build and deploy healthy), so the machine decides. Solomon never manually promotes and is never blocked.

2. **Data — promotes on approval, judgment-gated (up).** All document work happens in staging: upload → LLM extracts → review → feedback → corrections → preview, repeatedly, against the disposable staging PocketBase. When Jerome is satisfied, he clicks **"Apply to production"** in the staging uploader. That runs `scripts/promote_staging_to_prod.sh`: it backs up prod, copies the approved staging PocketBase to prod, recreates the prod admin, and rebuilds the prod dashboard. It is one-way, deterministic, and **never re-runs the LLM** — what was approved in staging is byte-for-byte what goes live. "Good" is Jerome's judgment (is this extraction correct?), which a machine cannot decide, so it waits for the click.

3. **Reset (down) — `refresh_staging_from_prod.sh`.** Resets the staging datastore + staging dashboard to mirror current prod, discarding staging experiments. Run it before a meaningful rehearsal, or any time staging should be a clean copy of live. Prod is untouched.

**Staging is therefore exactly like a Git feature branch:** refine until good, promote to "main" (prod); un-promoted chaff is thrown away on the next reset. Experiments you do NOT want in prod stay in staging simply by not clicking Apply.

## Consequences

**Better:**
- The refined, corrected, human-approved state is what goes live — no second LLM run, no drift between what Jerome saw and what publishes.
- The brain/LLM mess is contained to staging (its own PocketBase, its own per-env feedback log). Prod only ever receives an approved promotion, so it stays clean.
- One mental model for the team: code self-promotes on health; data promotes on Jerome's approval; reset wipes staging back to prod.

**Worse / watch for:**
- Promotion overwrites the whole prod datastore with staging's. Therefore **staging must be a refresh of prod before refinement** — otherwise stale staging data would clobber prod. The promote script keeps a `data.db.pre-promote` backup for rollback.
- **PocketBase migration trap (caused a prod outage on 2026-06-24):** both PocketBases MUST run with their own empty `--migrationsDir`. Prod was reading the shared `/var/lib/pb_migrations`; copying a db in made it replay an old auto-migration (`duplicate column: established`) and prod PB would not start. Fix: prod now runs `--migrationsDir=/var/lib/pocketbase/pb_migrations` (its own, empty), mirroring the staging fix. Never let either PB read the shared migrations dir.
- The staging admin (and, after promotion, prod's admin table) is overwritten by the copied db; both scripts recreate the automation admin afterward.

## Relationship to other ADRs

- ADR-006 / ADR-008 — the code auto-promotion + self-heal path.
- ADR-009 / ADR-011 — PocketBase, single source of truth — the data this governs.
- ADR-010 — the uploader / intake action; "Apply to production" now lives in the staging uploader.
- ADR-012 — Ask MIDD feedback is logged per-env; routing it into TASKS/CORRECTIONS is still future work.
