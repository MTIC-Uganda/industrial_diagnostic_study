# MIDD — Task Queue

The shared work queue, by owner. Jerome's feedback that needs a code change lands in Solomon's
section; data corrections go through the pipeline (Ask MIDD / re-ingestion), not here. Any agent
reads this to know what to work on next. Tick items as they land.

Last updated: 2026-06-23

## Solomon (dashboard, from the 2026-06-23 dashboard review)

- [ ] 12 key indicators: convert each to a donut/pie circle; remove gauges/sliders/small graphs;
      each shows the absolute figure AND percentage, plus its year and source; circle on top, legend below.
  - [ ] Value added: circle = manufacturing slice of GDP, figure + 14.5% of GDP, source UBOS.
  - [ ] Growth: figure + growth icon, no graph, source UBOS.
  - [ ] Tax contribution: in Uganda Shillings, source URA.
  - [ ] Manufactured exports: single figure + shipping icon + % of total exports, from TradeMap.
  - [ ] High-tech exports: figure (~85m USD) + % of manufactured exports.
  - [ ] FDI, employment, industrial parks, registered establishments: pie, no legend.
  - [ ] Distinct manufactured product categories: confirm counts are manufactured categories only.
- [ ] Progress to 10-fold: percentage-view / figures-view toggle.
- [ ] Treemaps: drop "of this view" tooltip text; full legend with smaller font; keep tooltip in
      viewport; fix the back button after drilling into a district via the legend.
- [ ] All reads come from the `industries` table (ADR-011), not static files or separate tables.

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
