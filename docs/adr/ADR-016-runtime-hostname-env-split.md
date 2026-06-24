# ADR-016: Dashboard Env Split is Runtime (Hostname), Not Build-Time

## Status: Accepted (2026-06-24) — supersedes the build-time split in ADR-014

## Context

ADR-014 split the dashboard by environment **at build time**: `generate_dashboard.py` checked `PB_URL` and stripped the public chat bubble on staging / the team header links on prod. That worked for the box-side builds (orchestrator, promote, refresh — each runs with the right per-env `PB_URL`), but it broke under CI.

CI (`deploy.yml`) builds the dashboard **once** with `secrets.PB_URL` (prod), rsyncs that single artifact to **staging**, then promotes staging→prod. So CI's one build is always a *prod* build, and it lands on staging too — flipping staging to the prod layout (bubble showing, team links gone) on every CI run. The split silently broke the next time anyone pushed.

## Decision

Decide the split **at runtime, by hostname**, so a single build is correct on both origins.

- `generate_dashboard.py` now **always emits both** the public chat bubble and the team header links (the team links wrapped in `#midd-team-nav`, hidden by default).
- A small script in the bubble block checks `location.hostname`:
  - **`staging.midd-ug.com`** → reveal the team Upload/Ask MIDD links **and keep the public bubble**, so the bubble can be tested against the staging brain before it reaches prod (Issue #71). The staging bubble hits `staging.midd-ug.com/api/ask` → the staging brain (:8220), so testing never touches prod.
  - **`midd-ug.com`** (anything not starting with `staging`) → public bubble only, team links hidden.

One artifact renders correctly on both hosts. CI's build-once-deploy-both model is now harmless.

## Consequences

**Better:** immune to CI clobbering the env config; the box-side builds and the CI build all produce the same correct artifact; no `PB_URL`-based branching for presentation.

**Worse / watch for:** the staging URLs for the team tools are present in the prod HTML (just hidden) — harmless, they're gated by Cloudflare Access anyway. A brief render before the script runs is possible (team-nav defaults hidden to avoid a flash on prod; the bubble is removed on staging on load).

## Relationship to other ADRs
- ADR-014 — defined the public bubble + the (now-replaced) build-time split.
- ADR-015 — Cloudflare Access; the team links the staging view reveals are gated by it.
