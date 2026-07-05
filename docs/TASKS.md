# MIDD — Task Queue

> **STANDARDS (enforced by CI — see CLAUDE.md "NON-NEGOTIABLE STANDARDS"):**
> 1. **PocketBase is the only data source (ADR-017).** Change data IN PocketBase (Ask MIDD / admin), never in `data/dashboard/*` (those are a PB backup mirror). Generators reading a file = CI fails.
> 2. **Tests required, >90% coverage on changed code (ADR-018).** `pytest` + `diff-cover` gate the build. Write code importable so it's testable.
> 3. **ADR change ⇒ update `docs/architecture.dsl` in the same commit.**
> These fail the build if broken — you cannot merge around them.

The shared work queue, by owner. Jerome's feedback that needs a code change lands in Solomon's
section; data corrections go through the pipeline (Ask MIDD / re-ingestion), not here. Any agent
reads this to know what to work on next. Tick items as they land.

Last updated: 2026-07-06 (2026-07-06 meeting queue landed — HS/SITC translator model)

## Solomon (from the 2026-07-06 meeting — HS-primary + SITC translator)

- [ ] Review the Manufactured Imports card on staging (now displaying after Hillary's fix). Have your agent read Hillary's agent's fix, confirm the figure, then **Apply to production** if it looks right.
- [ ] Build the **HS → SITC mapping table** (the translator) in PocketBase from the mapping file Jerome will share.
- [ ] Model: all import/export data is stored as **HS**. Derived indicators (manufactured / high-tech exports & imports) are **computed** by the official code-aggregation rules — translate HS→SITC via the table when the rule is SITC-based, else use HS directly. The LLM only injects data; translation, aggregation, and display are Python + the rules (one source of truth per record, never store both HS and SITC).
- [ ] Take Jerome's **source-annotated export-data Excel** and do the work to make the indicators display; upload the source reports it references where needed.
- [ ] Keep the download-then-upload flow (manual) for now. Explore whether the AI can pull directly from TradeMap (needs data sorted before download). Continue one-month-at-a-time updates (loaded to 03/2026; 04 next).

## Jerome (from the 2026-07-06 meeting)

- [ ] Finish + share the **source-annotated Excel** (authentic source named per indicator) + the export data, with Solomon.
- [ ] Provide the **HS → SITC mapping file** to load into PocketBase as the translator.
- [ ] Later (market analysis): provide East African countries trade data.

## Solomon (from the 2026-07-03 meeting — data sources + manufactured-exports card)

- [ ] Clear yesterday's backlog first (the work agreed last session that was not done).
- [ ] Fix the dashboard so it actually reads from the database: the card shows the UBOS section but no data comes through (link present, but it is not seeing data in the DB). Values must render from PocketBase.
- [ ] Download the UBOS composition-of-exports Excel (UBOS site, Statistics, External Trade, composition of exports, 1996 to March 2026). Use **calendar** year (matches TradeMap). Also grab composition of imports. Jerome will share the exact location.
- [ ] Upload that Excel through the pipeline (staging upload, Ask MIDD, Apply to Production). Doubles as an end-to-end pipeline test.
- [ ] Manufactured-exports + high-tech-exports indicators: use **UBOS aggregated** data = SITC sections 5, 6, 7, 8 **excluding 68** (non-ferrous metals). Keep the granular **HS-code TradeMap** data for the per-value-chain product breakdowns.
- [ ] Manufactured exports + imports on the **same card** (inflow vs outflow, for the import-substitution story), not a single aggregate number.
- [ ] On update, **never overwrite or delete** existing data: retain all years in the backend, group by year, display the latest but allow year selection + a trend view.

## Solomon (from the 2026-07-01 meeting — minister is data-driven; interactive demo due Monday)

- [x] Sources: footer on every KPI card, consistent placement; source shown on hover (dotted underline tooltip). `source_detail` field added to key_indicators schema — Jerome fills in specific doc names/links via Ask MIDD when available.
- [ ] UBOS-first data policy: use UBOS where available; TradeMap only where UBOS has nothing or cannot break it down. (Blocked on Jerome's UBOS Excel URL and data upload.)
- [x] HS code(s) on every product/stage in Explorer: shown in sidebar below product name + as blue pill badge in chain header. Compound codes displayed as "7305 + 7306".
- [x] Per-product data slots in Explorer: trade block (imports/exports) moved to top of popup; installed capacity slot added (pending MTIC register data per product); HS code shown in footer.
- [x] Fix "trade data not yet available": wire_trademap.py run, 75 nodes now show Uganda trade data in Sankey node detail panel.
- [x] Value-chain map visuals: vivid OEC palette (Sankey), wider node spacing, labels on hover only; OEC treemap palette applied to Manufacturing Industry Distribution (bold saturated colours).
- [x] Clarify estimated vs indicative labels: "Official figure" / "Estimated" / "Approximate" with plain-English legend. Live on prod.
- [ ] Own the single document-upload workflow — ongoing process task, not a code item.

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
