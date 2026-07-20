# Data Architecture Options — Research Note

**Date:** 2026-07-21  
**Context:** 2026-07-21 strategy call. Hillary and Solomon each to research the aggregation-engine vs backend-layer vs database-change options and weigh them on ability to deliver. Continue with PocketBase for this phase; plan a clean migration path.

---

## The problem

PocketBase's core limitation is **aggregation**. A query like "count industries by sector" requires a full table scan in the browser (7,100 rows → ~3.5 MB payload) or a view collection workaround. The REST API exposes collections and records, not arbitrary SQL. Three architectural responses exist.

---

## Option A — Aggregation engine on PocketBase (current path)

**What:** SQLite view collections (GROUP BY at the database level) exposed as REST endpoints. Already implemented for treemaps (`v_treemap_sector_subsector` etc., PR #116).

**Pros:**
- Zero new infrastructure. Same deployment, same CORS config, same PocketBase auth.
- Delivers immediately — already proven with the 6 treemap views.
- Read-heavy workload (no concurrent writes) suits SQLite perfectly at current scale.
- View collections are live SQL, so they always reflect the latest register state with no cache-invalidation logic.

**Cons:**
- PocketBase view collections are read-only; no aggregation across collections in one query.
- Complex multi-dimension analytics (e.g., "top 5 inputs by gap × essentiality, grouped by region") still require multiple fetches + client-side join.
- No API versioning, no middleware for rate-limiting (Cloudflare handles that externally).
- Locks us to SQLite semantics (no window functions in older SQLite).

**Verdict for this phase:** ✅ **Correct choice.** The remaining aggregation needs (capacity gap summaries, input priority ranking) are manageable with additional view collections. No new infra required.

---

## Option B — Backend layer (FastAPI / Express between browser and PocketBase)

**What:** A thin API service that accepts high-level queries, talks to PocketBase internally, and returns pre-shaped responses. Already partially exists as `app/backend/main.py` (FastAPI).

**Pros:**
- Clean API contract — UI talks to `/api/v1/capacity-gaps`, not raw PocketBase endpoints.
- Enables complex multi-step aggregations (join, window functions, custom ranking).
- Decouples UI from the datastore — migrating PocketBase → Postgres later only requires changing the backend, not the frontend.
- Can add caching, auth, rate-limiting at the API layer.

**Cons:**
- Adds a deployment unit: another process to run, monitor, and keep in sync with PocketBase schema.
- Increases latency (two hops: browser → backend → PocketBase).
- At current scale (~5 users, read-heavy) it is pure overhead. ADR-024 confirmed YAGNI.
- The existing `app/backend/main.py` is wired to SQLite (not PocketBase), so it would need rewriting anyway.

**Verdict for this phase:** ❌ **Premature.** The overhead is real; the gain is hypothetical at this scale. Revisit when: (a) aggregation complexity exceeds what view collections can handle, OR (b) the team grows to the point where UI/backend separation has velocity value.

---

## Option C — Migrate database (Postgres / Supabase)

**What:** Replace PocketBase's SQLite with Postgres (self-hosted or Supabase cloud). Supabase was the original proposal before PocketBase was chosen.

**Pros:**
- Full SQL including window functions, CTEs, materialized views.
- Supabase provides PostgREST (REST over Postgres), real-time subscriptions, auth — roughly feature-equivalent to PocketBase but on Postgres.
- Clean migration path: Supabase's API shape is similar enough that the browser fetch code changes minimally.
- Removes the aggregation ceiling entirely.

**Cons:**
- **Delivery risk is high.** Migration requires: schema mapping, data export/import, updating all collection names/field names if Supabase's PostgREST conventions differ, re-testing all PB-facing code paths, new admin UI for Jerome.
- Supabase has a free tier with row limits that may require a paid plan as the register grows.
- Self-hosted Postgres needs more devops attention than PocketBase (backups, vacuuming, connection pooling).
- Breaks the existing PocketBase hooks that the orchestrator pipeline relies on.

**Verdict for this phase:** ❌ **Not now.** The migration cost is measured in weeks, not days — incompatible with the demo timeline. Plan the migration path (schema parity map, Supabase project stub) so it is a one-sprint lift when the time comes.

---

## Recommendation

**Continue on PocketBase + view collections for this phase.** The aggregation needs are bounded and solvable with additional view collections (next: capacity-gap summary view, input-priority ranking view). Cloudflare provides the rate-limiting and edge caching ADR-024 noted.

**Migration path to prepare now (low effort, high future value):**

1. Keep all collection names and field names in a single file (`docs/schema.md` or a migration script) so a Supabase table definition can be generated by diffing it.
2. Enforce consistent field naming (`snake_case`, no PocketBase-specific types that have no Postgres equivalent) — already the case.
3. Document the 6 aggregation view collections created for treemaps as the template for future views — the SQL is plain ANSI-compatible.
4. When a backend layer does become necessary (likely when a third party needs programmatic access, or when analytics complexity exceeds what view collections handle), wire it to PocketBase first, then swap the datastore — the contract is isolated to the backend.

**Scale note** (Hillary's action): at 1,000 peak concurrent readers, PocketBase on a 4-vCPU/8 GB Hetzner VPS with Cloudflare caching in front handles the read load without read replicas. Set a monitoring alert at 500 concurrent connections as the trigger to plan the backend-layer or replica step.

---

*This note records the research for the 2026-07-21 strategy call. The decision is in ADR-024 (browser-direct PocketBase fetch, confirmed correct at current scale). Update this note when the scale or aggregation complexity changes.*
