# ADR-010: Document Intake and Intent Cadence

## Status: Proposed (pending team review, 2026-06-23)

## Context

The Phase 2 automation has a broken front door. Turning a document Jerome supplies into structured data on the dashboard is still manual and fragile. The 2026-06-23 retrospective surfaced six concrete problems:

1. **Two competing document locations.** The sector library (`data/<value-chain>/`, plus `policy-framework/` and `manufacturing-overview/`) is where humans and Jerome naturally put documents; `data/README.md` instructs exactly that. But the ingestion agent only watches the flat `data/uploads/`. Files have to be copied out of their sector home into `uploads/` to be processed. Commit `63894e9` ("fix sugar upload, rename and add to data/uploads/ for pipeline") is the proof: a document was duplicated out of `sugar-confectionery/` into `uploads/` just to be seen.

2. **Jerome's register was never ingested.** He added `data/manufacturing-overview/industries-register-aug2025.pdf` following the README convention (PR #67), but the pipeline does not watch that folder, so the ingestion agent never saw it. The treemaps exist only because a one-off script (`scripts/extract_industries_register.py`) read that PDF by a hardcoded path and wrote static JSON.

3. **Intent lives where the agent cannot read it.** Jerome's instruction to route the register through a database and have the dashboard read from it was written in PR #68's body and commit message, not next to the document. A human reading the PR would see it; the agent never does.

4. **The ingestion agent cannot read PDFs.** `agents/ingestion_agent.py` reads uploads with `read_text('utf-8')`. A PDF decodes to garbage, so mining a real PDF silently fails. `data/ingested/`, `data/proposed/`, and `data/revision/` contain only `.gitkeep`; no pipeline run has produced output.

5. **Three disconnected data planes.** `app/backend/graph.db` (SQLite) feeds the Sankey app; PocketBase is the intended dashboard backend (ADR-009); static JSON and CSV in `data/dashboard/` is what actually feeds the dashboard today, including all six treemaps. Nothing shares a source of truth.

6. **Every new use of a document needs a new parser.** The register is meant to power the treemaps, the industry locations map, and further analysis. Today each view is a fresh bespoke extractor that re-parses the PDF and commits static output. This does not scale and keeps a human in the loop for every twist.

The net effect: the curated sector corpus (around 80 documents across 9 value chains) is orphaned from the automation, and the automation dream stalls because a document never reliably becomes structured data.

## Decision

Adopt a single intake cadence: **one document home, one trigger, intent that travels with the document, and one structured data store.**

1. **One document home.** The sector tree (`data/<value-chain>/`, `policy-framework/`, `manufacturing-overview/`) is the single canonical intake for both humans and the pipeline. Retire `data/uploads/`. No document is ever duplicated to be processed.

2. **One trigger, folder-based routing.** CI ingestion triggers on changes to documents anywhere under `data/`, and processes only the files changed in the triggering push. The value chain is inferred from the containing folder (`automotive/` maps to Automotive), not guessed from the filename. `policy-framework/` documents are treated as cross-cutting.

3. **Real document extraction.** The ingestion agent gains proper text extraction: PDF via `pdfplumber` (fallback `pypdf`), DOCX via `python-docx`, XLSX via `openpyxl`. Plain text and markdown continue to be read directly. Extraction failure raises a visible error, never a silent garbage-to-Claude path.

4. **Intent travels with the document.** Each document may carry a sidecar instruction file, `<document>.task.md`, holding a short structured note (purpose, what to build, special handling). The agent reads the sidecar alongside the document. This replaces intent buried in PR bodies. A document with no sidecar is ingested with default behaviour for its value chain.

5. **One structured data store.** Extracted data lands in PocketBase as the single source of truth (the `industries` and `diagnostic_datapoints` collections). Static `treemap_*.json` is retired once `scripts/generate_dashboard.py` aggregates the treemaps from PocketBase at build time. Downstream views (treemaps, locations map, sector analysis) become queries over the structured store, not new parsers.

6. **No-git upload for Jerome (target state).** Jerome uploads through a PocketBase web form, selecting the value chain and typing a purpose note, then attaching the file. A CI step lands the file into the correct `data/<value-chain>/` folder, writes the sidecar from the purpose note, and triggers ingestion. This delivers the no-git goal of ADR-009 without abandoning the sector structure.

## Consequences

**Better:**
- The way the README already tells Jerome to file documents becomes the way the pipeline ingests them. No duplicate convention, no copying into a flat dump.
- A document reliably becomes structured rows in one store; new views are cheap queries, so Solomon's agent keeps up without a new parser per document.
- Intent is captured where the agent reads it, so instructions stop getting lost between PRs.
- The three data planes converge toward PocketBase for dashboard data; the Sankey `graph.db` remains separate by design but is no longer confused with dashboard data.

**Worse or cost:**
- Folder-based routing requires discipline in folder naming; a misfiled document routes to the wrong value chain. Mitigated by a fixed folder-to-chain map and a clear error when a folder is unrecognised.
- Processing only changed files needs reliable diffing in CI; a force-push or history rewrite could miss or re-process files. Mitigated by a processed-files manifest as a backstop.
- Retiring static `treemap_*.json` makes the dashboard build depend on PocketBase being healthy and seeded. Mitigated by keeping the last good JSON as a build-time fallback until the PocketBase path is proven.

**Watch for:**
- Re-ingesting the existing 80 documents: the first rollout must NOT reprocess the whole corpus. Seed the processed-files manifest with everything currently present so only genuinely new documents are ingested.
- Do not reintroduce the destructive collection PATCH that broke the seed job (see the 2026-06-23 fix in `db/pb_setup.py`). Schema changes go through the PocketBase admin UI or an id-preserving migration.
- Large documents and extraction cost: cap per-document Claude calls and degrade a failed extraction to a visible gap, not a crash (consistent with ADR-007).

## Phasing

- **Phase 1 (unify location):** retire `data/uploads/`; point the CI ingest trigger at `data/` documents; route by folder; seed the processed-files manifest. Edits in `.github/workflows/deploy.yml` and `agents/ingestion_agent.py`.
- **Phase 2 (front door):** add PDF, DOCX, XLSX extraction to `agents/ingestion_agent.py`.
- **Phase 3 (intent):** add `<document>.task.md` sidecar reading to the ingestion agent; document the sidecar format in `data/README.md`.
- **Phase 4 (one store):** complete the `industries` collection seeding in CI; add a PocketBase branch to `scripts/generate_dashboard.py` for the treemaps; retire static `treemap_*.json` with a fallback.
- **Phase 5 (no-git upload):** PocketBase web upload to sector folder plus sidecar, then ingest.

## Relationship to other ADRs

- **ADR-007 (agentic pipeline):** this ADR fixes the ingestion front door that ADR-007 assumed worked. The ingest, synthesize, review, deploy loop is unchanged; it simply starts receiving real data.
- **ADR-009 (PocketBase backend):** this ADR makes ADR-009's "Jerome edits without Git" real by giving documents, not just structured fields, a no-git path, and by converging the dashboard data onto PocketBase.
- **ADR-002 (markdown as source of truth):** the sidecar instruction files are markdown, consistent with this principle.
