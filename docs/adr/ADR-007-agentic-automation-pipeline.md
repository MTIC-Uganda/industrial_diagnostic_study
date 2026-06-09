# ADR-007: Agentic Automation Pipeline (Ingest → Synthesize → Review → Deploy)

## Status: Accepted (Phase 2 in progress)

## Context

Phase 1 (manual) required Solomon to manually prompt Claude chapter by chapter, and Jerome to manually trigger reviews. This created bottlenecks at both ends: Solomon needed to be available to drive the AI, and Jerome's review feedback was asynchronous and slow. The meeting on 2026-06-10 established that the goal is full automation: Jerome uploads data, the system does the rest.

## Decision

Build a closed agentic loop on the Hetzner server triggered by GitHub push events:

1. **Ingestion Agent** — reads Jerome's uploaded file + context note, maps to the value chain schema, writes structured JSON, flags data gaps.
2. **Synthesis Agent** — reads all stage JSONs for one chain, produces a diagnostic assessment (current status, gap vs Tenfold 2040, bottleneck ranking, project profile sketches).
3. **Review Agent** — validates synthesis output against Jerome's quality matrix. PASS: opens PR to main. FAIL: sends specific feedback via WhatsApp and loops back to synthesis.
4. **Deploy** — existing GitHub Actions pipeline promotes to prod on merge.

This is a **closed loop** (not open): Jerome defines the quality matrix upfront, the AI iterates until it meets Jerome's standard, and the loop terminates on PASS. This keeps token spend bounded and output quality high.

## Consequences

Better: Jerome's only job is uploading data with context notes; Solomon's only job is maintaining the dashboard display logic; the pipeline self-corrects on FAIL; WhatsApp notifications keep the team informed without anyone needing to check GitHub.

Worse: Jerome must invest time upfront writing the quality matrix (ADR-003 pattern applied again); if the matrix is too strict the loop will cycle unnecessarily; if too loose, low-quality output reaches prod.

Watch for: loop guard needed (cap retry count to prevent infinite FAIL cycles); quality matrix must be versioned alongside the data schema so changes are traceable; TradeMap session expiry can break the ingestion agent (handle gracefully with data gap flag, not crash).

## Bottlenecks in this architecture

Identified in the Structurizr dynamic DataFlow view:
- **Schema definition** — Jerome must complete `data/schema/` before Phase 2 agents can run.
- **Quality matrix** — Jerome must complete `docs/quality-matrix.md` before the review agent can score.
- **Review FAIL loop** — if synthesis repeatedly fails, the bottleneck is either missing source data or an overly strict quality criterion. Check the WhatsApp FAIL message for the specific gap.
- **TradeMap data gaps** — import/export figures not in the synthesized store will surface as explicit gap flags, not errors. This is by design.
