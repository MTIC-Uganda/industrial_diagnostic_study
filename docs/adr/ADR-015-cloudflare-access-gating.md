# ADR-015: Cloudflare Access Gating of the Internal Tools

## Status: Accepted (2026-06-23)

## Context

midd-ug.com fronts both public surfaces (the dashboards) and internal tools (the uploaders, the team Ask MIDD, PocketBase admin). The dashboards are meant for the public/Commissioner; the tools are not. An app password alone is weak and shared. We needed a real gate on the internal tools without touching the public dashboards.

## Decision

Use **Cloudflare Zero Trust Access** to gate the internal tool hostnames, leaving the dashboards public.

- **Access application** (self-hosted) covering the four tool hostnames: `upload`, `ask`, `staging-upload`, `staging-ask` (.midd-ug.com).
- **Policy "MIDD team" (Allow)** with an email **allow-list** — the only people admitted:
  - `arinda.hillary@gmail.com` (Hillary)
  - `jnuwabaasa@gmail.com` (Jerome)
  - `arihosolomon@gmail.com` (Solomon)
- **Preauthorized:** because their addresses are on the allow-list, admitted teammates are let straight through after authenticating to Cloudflare — there is **no one-time PIN** step in the normal flow. (Cloudflare team domain: `fragrant-field-4fd5.cloudflareaccess.com`.)
- **Public, NOT gated:** `midd-ug.com` and `staging.midd-ug.com` (the dashboards) load freely for anyone.
- **PocketBase** (`db`, `staging-db`) is **not** in the Access application — it keeps its own admin login (`admin@midd-ug.com`). This is partly the 5-destinations-per-app limit and partly that PocketBase already has a strong native gate.
- The app password inside each tool (e.g. `jerome-test`) remains as a second, lightweight layer behind Access.

Verified: the four tool hosts 302-redirect to the Cloudflare Access login for anyone not signed in; the two dashboards return 200 publicly.

## Consequences

**Better:** only the three of us can reach the uploaders and team Ask MIDD; the public dashboards are unaffected; no per-tool account management — membership is one allow-list. The public Ask MIDD bubble (ADR-014) deliberately lives on the public dashboard origin, NOT behind Access, which is why it must be cheap+rate-limited rather than gated.

**Worse / watch for:** the allow-list is managed in the Cloudflare dashboard, so adding a teammate is a console step, not a repo change (record it here when it changes). The 5-destinations-per-app limit is why PocketBase stays on its own login rather than joining the app. If we ever want the team Ask MIDD answers to be SSO-attributed per person, we would wire a named identity provider; today the allow-list is the whole policy.

## Relationship to other ADRs
- ADR-014 — the public Ask MIDD bubble, which sits OUTSIDE this gate on purpose.
- ADR-013 — environment model; the gated tools are the team workshop, the public dashboards the showroom.
