# MIDD — Task Queue

The shared work queue, by owner. Jerome's feedback that needs a code change lands in Solomon's
section; data corrections go through the pipeline (Ask MIDD / re-ingestion), not here. Any agent
reads this to know what to work on next. Tick items as they land.

Last updated: 2026-06-24 (Solomon's dashboard-review queue landed — see notes)

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
- [ ] **NOT done — flagging honestly rather than repeating the mistake the retrospective is about:**
      the 12 indicators and treemap-card visuals above still read from `data/dashboard/*.csv` /
      `treemap_district.json` (the same local files built earlier this session), not from PocketBase.
      The big drillable treemaps already migrated to the `industries` table (Hillary, ADR-011) — this
      item is specifically about the macro/indicator figures (GDP, tax, FDI, employment, etc.), which
      have no PocketBase collection yet (`kpi_indicators` has 6 old rows from the original 6-card
      design, not these 12). Time-boxed today to ship the visual redesign Jerome is waiting on before
      the 06-28 deadline; the data-source migration is the next item, not skipped indefinitely.

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

- [ ] Deeper harness loop: feedback improves the agents; brain auto-updates STATUS.md + ADRs.
- [ ] Feedback triage: data issues → data loop; feature/code issues → this Solomon section.
- [ ] Automated staging→prod promotion (after Solomon's redesign lands).
- [ ] Containerize (Dockerfile) + MIDD's own model/subscription.
- [ ] Cleanup: delete stale branches data/fix-sugar-upload, data/schema-and-quality-gate,
      data/schema-and-quality-matrix.

## From Ask MIDD — feature requests (auto-logged)

<!-- ASKMIDD-FEATURES -->
