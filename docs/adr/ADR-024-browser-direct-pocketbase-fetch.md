# ADR-024: Browser-direct PocketBase fetch over a layered service

## Status: Accepted

## Context

The dashboard and Value Chain Explorer originally baked all of their data into
the HTML as static JS constants at CI build time. Any change in PocketBase only
appeared after the next push to main rebuilt the site. Solomon asked for
"refresh equals fresh data", so PR #115 moved the Explorer trade popup to a live
browser fetch, and PR #116 extends the same pattern to the main dashboard: Chain
Status and 2040 projections, the Manufacturing treemap, the Industry Locations
map, and the Explorer structure collections now fetch PocketBase directly in the
browser on page load.

This raised a design question from Solomon's agent: should the system stay on
direct browser to PocketBase fetches, or should we build the layered
Controller, Service, DAL, DB pattern that was floated earlier as a target shape.

## Decision

Keep the direct browser to PocketBase fetch. Do not build the layered service.

Reasons:

1. PocketBase's REST API is already the backend. It is a validated public read
   API, not a raw database socket, and ADR-017 already commits us to PocketBase
   as the single source of truth. A separate service layer would duplicate what
   PocketBase already gives us.
2. The scale does not justify it. This is a read-heavy ministry dashboard with a
   small user base and infrequent writes. Rate limiting, caching, and TLS are
   already provided by the Cloudflare layer that fronts every host (ADR-015,
   ADR-016).
3. Hiding the datastore shape and swapping the data source later are speculative
   needs (YAGNI). PocketBase is the committed store; the diagnostic data is meant
   to be public, not concealed.

The one legitimate weakness the layered pattern would have solved, moving heavy
aggregation off the browser, is addressed inside the direct-fetch model instead:
pre-aggregate the treemap in PocketBase (a view collection, or a build-time
computed collection) so the browser fetches small aggregate rows rather than the
full ~7,100 row industries table and computing six treemap structures client
side on every load.

## Consequences

Better:

- Editing data in PocketBase shows on a browser refresh with no rebuild, for the
  live-fetch sections.
- Far less infrastructure to build, deploy, and maintain than a service tier.
- One build serves staging and prod; a hostname check picks the right PocketBase
  origin at runtime (ADR-016).

Worse or to watch for:

- Every live-fetch section must keep the last-built static data as an offline
  fallback, so a PocketBase outage degrades to stale-but-present data rather than
  a blank section. The Explorer already does this; the dashboard sections in
  PR #116 must match this before merge, or a PocketBase outage blanks Chain
  Status, the treemap, and the locations map during a live ministry review.
- The fetches are cross-origin (midd-ug.com to db.midd-ug.com). PocketBase
  allowed-origins must list the dashboard hostnames, or, preferred, Cloudflare
  proxies the datastore as same-origin. Cloudflare same-origin is the chosen
  path because these hosts already sit behind Cloudflare.
- Client-side aggregation of the full industries table is a payload and compute
  cost (~3.5 MB per load). Pre-aggregation in PocketBase is the follow-up that
  keeps this architecture healthy as row counts grow.
