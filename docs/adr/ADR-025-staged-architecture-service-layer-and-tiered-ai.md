# ADR-025: Staged architecture, a service layer and tiered AI analytics

## Status: Accepted

## Context

The project is moving from a short demo into a multi-year platform whose value is deep, precise analytics (grouping, ranking, gap analysis, capacity versus target). Two structural facts now dominate the design:

1. The workload is becoming aggregation-heavy, which is exactly PocketBase's weak spot. PocketBase is excellent for ingestion, admin, auth, and simple row queries, but it has no server-side GROUP BY, COUNT, or SUM through its REST API (ADR-024 records the browser-direct-fetch consequence of this).
2. The UI talks to the datastore directly, with no layer in between. This couples the frontend to the datastore shape and makes changing the datastore expensive. The problem is not PocketBase, it is the missing layer.

Separately, the public Ask MIDD assistant can answer simple lookups (how many industries) but not aggregation (which sectors are those industries in, where is the biggest bottleneck), because its query tool only supports count and list, and PocketBase cannot aggregate for it.

## Decision

Adopt a staged direction rather than a single big change.

1. Keep PocketBase for this phase and the demo. It stays the ingestion store and system of record. No migration now; a migration now would risk the demo.
2. Introduce a thin backend or service layer between the UI and the data as the first work after the demo. The UI calls the API; the API talks to the data. This is database-agnostic and is the highest-leverage move: it removes the lock-in, gives aggregation a home, and provides a place for caching and rate limiting.
3. Add Postgres behind that layer later, only when analytics demand outgrows PocketBase. Because the layer exists, this becomes an invisible backend change, not a migration the frontend feels.
4. Tier the AI analytics:
   - Public assistant: a cheap model plus a set of validated, parameterised, server-side analytical tools (count, list, and now group and rank), plus a semantic layer of metric definitions, plus heavy caching. It never runs arbitrary code, so it stays safe for a public endpoint.
   - Authenticated power users: keep the read-only pandas sandbox (ADR-020) for open-ended analysis that does not fit a predefined tool.
5. Close the loop: every question the assistant fails to answer is logged and becomes either a new tool or metric, or a test case, so analytical coverage compounds.

Relationship to ADR-024: ADR-024 (browser-direct-fetch, no service layer) remains correct for the demo timeframe. This ADR sets the direction that supersedes it once the demo is delivered. The service layer is the point at which the frontend stops fetching PocketBase directly.

## Consequences

Better:

- The database choice becomes reversible instead of a lock-in, so the PocketBase versus Postgres decision no longer has to be made under pressure.
- Aggregation, caching, and rate limiting get a single home, which is what makes the read workload scale cheaply (the static shell already scales on the CDN; the cost that remains is the AI, which the tiering and caching contain).
- The public assistant can answer real analytical questions (breakdowns, rankings, gap analysis) without arbitrary code execution.

Worse or to watch for:

- A service layer is more infrastructure to build and run than direct fetch. It is deliberately deferred until after the demo so it does not compete with the demo deadline.
- Until the layer exists, aggregation for the public assistant is done by fetching whitelisted, field-projected rows and counting them server-side in Python (bounded by collection size). This is the interim approach shipped with this ADR and should move behind the service layer, ideally onto pre-aggregated PocketBase views or Postgres, as volumes grow.
- Two AI tiers means two code paths to maintain; the public tier must never gain code-execution capability.

## First increment shipped with this ADR

The public query tool gains a group mode: the model may propose a GROUP BY over a whitelisted dimension, validated exactly like the existing count and list modes, executed read-only, and aggregated server-side. This directly fixes the which-sectors and ranking questions the assistant could not answer.
