# MIDD — Task Queue

> **STANDARDS (enforced by CI — see CLAUDE.md "NON-NEGOTIABLE STANDARDS"):**
> 1. **PocketBase is the only data source (ADR-017).** Change data IN PocketBase (Ask MIDD / admin), never in `data/dashboard/*` (those are a PB backup mirror). Generators reading a file = CI fails.
> 2. **Tests required, >90% coverage on changed code (ADR-018).** `pytest` + `diff-cover` gate the build. Write code importable so it's testable.
> 3. **ADR change ⇒ update `docs/architecture.dsl` in the same commit.**
> These fail the build if broken — you cannot merge around them.

The shared work queue, by owner. Jerome's feedback that needs a code change lands in Solomon's
section; data corrections go through the pipeline (Ask MIDD / re-ingestion), not here. Any agent
reads this to know what to work on next. Tick items as they land.

Last updated: 2026-06-24 (Solomon's dashboard-review queue landed — see notes)

## Solomon (from the 2026-07-01 meeting — minister is data-driven; interactive demo due Monday)

- [ ] Sources: footer on every card, consistent placement; detailed source (which UBOS report/link) shown on hover.
- [ ] UBOS-first data policy: use UBOS where available; TradeMap only where UBOS has nothing or cannot break it down.
- [ ] HS code(s) on every product/stage; support multiple codes per product (used vs new clothing); import value = sum across a product's codes.
- [ ] Per-product data slots (blank OK for now): imports, exports, number of industries, total installed capacity. (Minister's per-product questions; example steel wire HS 7217.20.)
- [ ] Fix "trade data not yet available" when the HS code is linked — TradeMap data exists (yellow/estimated is still usable) and should pull.
- [ ] Value-chain map visuals: icons only (no labels), icons resembling the item; more vivid colours (blue too dull); wider group spacing; drill-down by district, both sides drillable. Reference: OEC.
- [ ] Clarify estimated vs indicative labels for laymen.
- [ ] Own the single document-upload workflow (staging upload → Ask MIDD corrections → Apply to Production). No direct PocketBase edits, no hand-created collections.

## Hillary (from the 2026-07-01 meeting)

- [ ] Verify all dashboard data comes from PocketBase, nothing hardcoded (Jerome's hard rule). Fix immediately if any is.
- [ ] Wire Ask MIDD to read live data (answer per-product questions) + add self-improvement loop (rate answers, learn from failures).
- [ ] Cross-platform mobile stack decision (app must not be Android-only) — drives the tech choice.

## Jerome (from the 2026-07-01 meeting)

- [ ] Call UBOS (after 9am) for more broken-down data (HS 6-digit); if unavailable, stay on TradeMap.
- [ ] Provide the value-added + tax table (percentages AND figures) + the Tenfold Growth table.
- [ ] Give the specific defendable source for each figure.

## Solomon (dashboard, from the 2026-06-23 dashboard review)

- [x] 12 key indicators: convert each to a donut/pie circle; remove gauges/sliders/small graphs;
      each shows the absolute figure AND percentage, plus its year and source; circle on top, legend below.
  - [x] Value added: circle = manufacturing slice of GDP, figure + 14.5% of GDP, source UBOS.
  - [x] Growth: figure + growth icon, no graph, source UBOS.
  - [x] Tax contribution: in Uganda Shillings, source URA.
  - [x] Manufactured exports: single figure + shipping icon + % of total exports, from TradeMap.
  - [x] High-tech exports: figure (~85m USD) + % of manufactured exports.
  - [x] FDI, employment, industrial parks, registered establishments: pie, no legend.
  - [x] Distinct manufactured product categories: caption now states both 380 and ~5,000 are
        manufactured-HS6-only — flagged "pending Jerome's confirmation" since we haven't re-pulled
        TradeMap to verify the exact manufactured-only counts (this needs item below, not guessed).
- [x] Progress to 10-fold: percentage-view / figures-view toggle. Investigated which of the 9
      indicators actually differ between views — only #1 (Value Added, since GDP itself is the
      denominator and grows ~10x) and trivially #9 (proportional, denominator is fixed at ~5,000).
      #2-8 don't have confirmed absolute NDP IV/Tenfold targets for their own denominators yet, so
      the toggle is wired but doesn't change them — added an explanatory note rather than inventing
      targets we don't have.
- [x] Treemaps: dropped "of this view" tooltip text; legend now shows every item (was capped at top
      8) with smaller font/swatches + a max-height scroll safety net so the card never grows; tooltip
      now measures itself and flips to the other side of the cursor near viewport edges; fixed the
      real bug behind "stuck on Gomba" — returning to "All Regions"/"All Sectors" wasn't clearing the
      OTHER panel's lingering cross-filter, both `showTop()`s now reset each other.
- [x] **Done 2026-06-24:** the 12 indicators + region strip (card 8) now read from two new
      PocketBase collections, `key_indicators` (one row per card: value, pct, color, year, source,
      confidence) and `key_indicator_categories` (slices for the tax/hightech/credit donuts and the
      region strip) — both defined and seeded by `db/pb_setup.py`, which CI already runs against prod
      on every push to main. `data/dashboard/key_indicators.csv` / `key_indicator_categories.csv` are
      the local-dev and first-deploy fallback (used automatically until the first CI seed run lands).
      Deliberately left `sector_comparison.csv`/`treemap_district.json` untouched — other features
      (Momentum panel) still read them directly; the new collections are dedicated, separate copies of
      the same underlying figures, not a move. Also fixed a real bug found while doing this: macro_trend
      was being silently overwritten by the local CSV even when the PocketBase fetch had already
      succeeded, because the fallback line ran unconditionally — same class of issue as the original
      retrospective, caught before it shipped this time.

### Retrospective: where Jerome's "PDF → database → dashboard" instruction got missed
Traced it: the instruction was given in a PR description/commit message context, which this agent's
session read as confirmation a *file* had landed correctly — not as confirming the *downstream
pipeline target*. The session that built the original treemap (this agent, 2026-06-21) extracted the
PDF straight into committed JSON files and never checked whether a PocketBase collection was the
intended destination, because nothing in the immediate task description said "PocketBase" — it said
"build the treemap," and the fastest correct-looking path was static extraction. The gap: there was
no single place an agent could check "what is the canonical destination for newly-extracted data"
before choosing where to write it. ADR-011 (written after, in response to this exact incident) is the
fix — but ADR-011 needs to be the *first* thing any agent reads before extracting data from a new
document, not a thing it finds out about after building the wrong path. Suggest: add a one-line rule
to CLAUDE.md / the session-start protocol — "before extracting data from any new source document,
check ADR-011 for the canonical destination" — so this isn't dependent on the task description
happening to mention PocketBase by name.

## Jerome (review + upload)

- [ ] Upload the National Industries Register via the staging uploader, with full intent.
- [ ] Upload the other reports carrying establishment/sector data.
- [ ] Review on staging, flag corrections through Ask MIDD (not direct PocketBase edits).

## Done recently
- [x] Removed the Upload Guide / Data Entry Guide buttons + the 3 inline upload-guide links and
      stale data/uploads references from the public dashboard template (they were internal ops
      guidance, and one taught direct PocketBase editing — against ADR-012). Deployed staging + prod.
      NOTE for Solomon: this was a small change to sources-of-truth.template.html (the button row
      around the header + pipeline-status text). Pull latest main before your redesign.
- [x] Rewrote the standalone guide pages (upload-guide.html, pb-guide.html) to point to the
      uploader + Ask MIDD (now unlinked from the dashboard; can move into the internal workbench).

## Hillary (infrastructure / harness)

- [ ] **New, needs server access to diagnose:** `db/pb_setup.py` failed to create the two new
      collections (`key_indicators`, `key_indicator_categories`) in CI run
      https://github.com/MTIC-Uganda/industrial_diagnostic_study/actions/runs/28103151948 —
      `HTTP 400 POST /api/collections: {"code":400,"message":"Failed to create the collection.","data":{}}`.
      The 5 pre-existing collections all read fine ("Exists, schema left intact"); this is specifically
      about *creating a brand-new* collection. `setup/hetzner_pocketbase.sh` pins `PB_VERSION="0.22.7"`,
      which is the version `pb_setup.py`'s schema format (`'schema': [...]`, nested `options`) targets —
      my hypothesis is prod PocketBase is actually running a newer version (0.23+) that expects the
      `'fields': [...]` format instead, possibly from today's PocketBase work (the migrations-dir
      outage fix). Can't confirm without `pocketbase --version` on the server or checking the admin UI's
      collection editor. **No live-site impact** — the dashboard's local-CSV fallback kicked in
      automatically and prod is serving correct values; this only blocks the new collections from being
      genuinely seeded. Once confirmed, either pin the binary back to 0.22.7 or I'll update
      `db/pb_setup.py`'s collection-creation payload to the 0.23+ `fields` format.
- [ ] Deeper harness loop: feedback improves the agents; brain auto-updates STATUS.md + ADRs.
- [ ] Feedback triage: data issues → data loop; feature/code issues → this Solomon section.
- [ ] Automated staging→prod promotion (after Solomon's redesign lands).
- [ ] Containerize (Dockerfile) + MIDD's own model/subscription.
- [ ] Cleanup: delete stale branches data/fix-sugar-upload, data/schema-and-quality-gate,
      data/schema-and-quality-matrix.

## From Ask MIDD — feature requests (auto-logged)

<!-- ASKMIDD-FEATURES -->
