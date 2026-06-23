# ADR-011: Single-Source Database Structure

## Status: Accepted (2026-06-23, from the harness + data architecture meeting)

## Context

The dashboard grew as a prototype that read data from many places: static JSON and CSV in `data/dashboard/`, the register PDF parsed into static treemap files, the Sankey app's separate `app/backend/graph.db`, and a few PocketBase collections seeded from repo CSVs. The result is that the same kind of fact lives in several disconnected sources, and the industry locations map reads from a different table than the distribution treemaps even though they describe the same establishments.

Jerome's requirement (2026-06-23) is explicit: one structured database as the single source of truth. A document of any form is shredded by the LLM brain and its data lands in one place. Establishments live once; new documents update existing rows (for example adding an employment figure), new information may add a column, missing information stays blank. Related tables (value chains, etc.) link to the establishments so questions like "how many industries in Uganda make this product" are a query, not a separate dataset. The structure will change a lot early, then stabilize.

Current PocketBase collections: `value_chains`, `facilities` (89 curated map factories with GPS, capacity, ownership), `kpi_indicators`, `diagnostic_datapoints` (empty), `industries` (7,011 establishments from the register, mostly without GPS).

## Decision

PocketBase remains the single datastore. Inside it, a small set of structured, related collections, with `industries` as the canonical establishment table.

1. **`industries` is the one establishment table.** One row per establishment, keyed by `reg_number` (the National Industries Register number) as the natural identity. An establishment appears exactly once. Re-ingestion updates the existing row by `reg_number`; it never creates a duplicate. New facts fill columns; new kinds of fact add a column; absent facts stay blank. This is the table the distribution treemaps and the industry locations map both read from.

2. **Merge `facilities` into `industries`.** The 89 curated map factories carry fields the register lacks (latitude, longitude, products, capacity_installed, capacity_utilised, employees, established, ownership, exports). Those fields become columns on `industries`, and the curated factories become enriched `industries` rows. The locations map then reads `industries` where latitude and longitude are present. The separate `facilities` collection is retired once the merge is verified (kept transitionally as a fallback, not as a second source of truth).

3. **`value_chains` stays as a related table.** It is the source for the Sankey and the value-chain views. It links to `industries` so a value-chain stage can resolve "the industries under this stage" and counts like "six industries make this product" by querying `industries` (matched on sector, sub-sector, or product). The link is by shared classification fields now (sector_name, subsector_name, products) and can become an explicit relation field as the schema stabilizes.

4. **`kpi_indicators` stays** as the overview metrics table.

5. **`diagnostic_datapoints` stays** as the value-chain study facts table, populated by the LLM ingestion agent for unstructured study documents (one fact per row, mapped to the diagnostic schema).

6. **All writes go through the LLM brain, never by editing PocketBase directly.** PocketBase is the store, not the editor. Corrections route through the ingestion/review agents so they are tracked and the agents improve (see ADR-010 and the harness work). The PocketBase admin UI is for inspection, not authoritative edits.

7. **Two levels of de-duplication.** At the document level, the uploader detects a document it already holds (by content hash) even if renamed, and refuses to re-ingest it. At the record level, `industries` upserts by `reg_number`, so the same establishment is never duplicated across documents.

## Consequences

**Better:**
- One place for establishment data; the treemaps, the locations map, and value-chain counts all read from `industries`, so they are always consistent.
- Updates are in place: Jerome adds an employment column once and every establishment can carry it, blanks where unknown.
- New documents enrich the same rows instead of spawning parallel tables.
- The Sankey can ask real questions of the establishment data through the value-chain relation.

**Worse or cost:**
- Merging `facilities` into `industries` is a one-time migration that must preserve the 89 curated rows' GPS and rich fields and match them to register rows where possible.
- A wide, sparse table (many columns, many blanks) is the deliberate trade for "one table, updated in place." Acceptable per Jerome; revisit only if it becomes unwieldy.
- `value_chains` to `industries` linking starts as soft matching on classification fields; a hard relation field is a later tightening.

**Watch for:**
- `reg_number` must be present and stable for upsert identity; rows without one (curated factories, future sources) need an assigned identity.
- The Sankey's separate `app/backend/graph.db` remains its own store by design; do not confuse it with the dashboard's PocketBase. Converging the two is out of scope here.
- Do not let any feature regress to reading static files once it reads from `industries`; keep the static JSON only as a build-time fallback (ADR-010).

## Relationship to other ADRs

- ADR-009 (PocketBase as the backend) — this ADR defines the structure inside it.
- ADR-010 (document intake and intent cadence) — the uploader and ingestion that fill this structure; document-level dedup lives there.
- ADR-007 (agentic pipeline) — the ingestion/synthesis/review agents are how writes reach this structure.
