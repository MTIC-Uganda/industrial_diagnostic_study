# Task Brief for Solomon: Fix the Document Intake Pipeline

Status: Ready to implement. Spec is ADR-010 (`docs/adr/ADR-010-document-intake-and-intent-cadence.md`). This brief is the executable version of that decision.

This is separate from, and on top of, your dashboard tasks from the 2026-06-23 review meeting (`meeting_transcripts/2026_06_23_dashboard_review.md`). The dashboard redesign work stands. This brief fixes the data plumbing underneath it.

## The problem in one paragraph

A document Jerome supplies never reliably becomes structured data on the dashboard. The ingestion agent only watches the flat `data/uploads/`, but Jerome and the README file documents into the sector folders (`data/<value-chain>/`), so files get copied to be processed or are never seen at all (his establishment register in `data/manufacturing-overview/` was never ingested). The agent also cannot read PDFs (it does `read_text('utf-8')`, which is garbage for a PDF). His instructions live in PR bodies the agent cannot read. The treemap data is parsed by a one-off script into static JSON, bypassing PocketBase entirely. Result: every new use of a document needs a new bespoke parser, and the automation stalls.

## What to build, in order

### Phase 1: one document home, one trigger
- Retire `data/uploads/`. The sector tree (`data/<value-chain>/`, `data/policy-framework/`, `data/manufacturing-overview/`) becomes the single intake for both humans and the pipeline.
- In `.github/workflows/deploy.yml`, change the ingest job trigger from `data/uploads/` to documents anywhere under `data/`. Process ONLY the files changed in the triggering push (use the git diff of the push), never the whole tree.
- In `agents/ingestion_agent.py`, route the value chain by the containing folder, not the filename. Keep a fixed folder-to-chain map (`automotive` to Automotive, etc.); treat `policy-framework/` as cross-cutting; raise a clear error on an unrecognised folder.
- Seed a processed-files manifest (for example `data/.ingested_manifest.json`) with every document currently in the repo, so the first run does NOT reprocess the existing ~80 documents.

### Phase 2: real document extraction (the keystone)
- In `agents/ingestion_agent.py`, replace `read_text('utf-8')` with proper extraction:
  - PDF: `pdfplumber` (fallback `pypdf`)
  - DOCX: `python-docx`
  - XLSX: `openpyxl`
  - txt and md: read directly as now.
- On extraction failure, raise a visible error and record a gap. Never send undecoded bytes to Claude.
- Add the libraries to the CI requirements for the ingest job.

### Phase 3: intent travels with the document
- Support a sidecar instruction file next to each document: `<document>.task.md` (for example `industries-register-aug2025.task.md`). Read it alongside the document and pass its content to the agent as the task instruction.
- A document with no sidecar is ingested with default behaviour for its value chain.
- Document the sidecar format in `data/README.md` with a short example.

### Phase 4: one structured store (coordinate with Hillary on infra)
- The PocketBase seed job is now fixed; the `industries` collection will be created on deploy. Complete its seeding in CI: commit `industries.json` (output of `scripts/extract_industries_to_records.py`) or fold that extraction into CI, then run `db/seed_industries.py`.
- Give `scripts/generate_dashboard.py` a PocketBase branch for the treemaps: aggregate the six treemap views from the `industries` collection at build time. Keep the last good static `treemap_*.json` as a fallback until the PocketBase path is proven, then retire the static files.
- Outcome: new views (the industry locations map, sector analysis) become queries over `industries`, not new parsers.

## Acceptance criteria
- Dropping a new PDF into the correct `data/<value-chain>/` folder and pushing triggers ingestion for that value chain, with the PDF text actually extracted (not garbage).
- A `<document>.task.md` sidecar changes what the agent does, observably.
- The existing ~80 documents are NOT reprocessed on the first run.
- The treemaps render from the `industries` collection (with the static JSON only as fallback).
- The CI Seed PocketBase job stays green.

## Do not
- Do not reintroduce the destructive collection PATCH in `db/pb_setup.py`. It was dropping every field and wiping record data on each run; the 2026-06-23 fix made it skip existing collections. Schema changes go through the PocketBase admin UI or an id-preserving migration.
- Do not duplicate documents into a flat folder to process them. That is the exact problem we are removing.
- Do not parse the same document with a new bespoke script per view. Extract once into the structured store, then query.

## References
- ADR-010 (the decision): `docs/adr/ADR-010-document-intake-and-intent-cadence.md`
- ADR-007 (agentic pipeline), ADR-009 (PocketBase backend)
- Meeting (your dashboard tasks): `meeting_transcripts/2026_06_23_dashboard_review.md`
