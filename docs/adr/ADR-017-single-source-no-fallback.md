# ADR-017: PocketBase Is the Only Source — No File Fallback, Enforced

## Status: Accepted (2026-07-02)

## Context

ADR-011 said PocketBase is the single source of truth, but it was a *document an agent had to choose to read*, while the fast path (write a committed JSON/CSV, or fall back to one) was never blocked. A forensic scan (2026-07-02) found the rule had been bypassed repeatedly: treemaps + factories rendered from committed JSON (`ccf1fa4`, `9904e3c`), the register extracted to `industries.json` (`532c740`), KPI figures hardcoded in the generator, and four sections that were CSV-only with no PocketBase path at all. Each was caught and migrated later — but the *pattern* kept recurring because nothing enforced the rule at build time. Hillary's directive: single source is the database, full stop; no fallback; write guardrails that no agent (Solomon's or Hillary's) can break.

## Decision

**PocketBase is the ONLY runtime data source. There is no CSV/JSON fallback. This is enforced in code and CI, not by convention.**

1. **Generators fail loudly, never fall back.** `scripts/generate_dashboard.py` and `scripts/generate_explorer_data.py` require `PB_URL`; if it is unset, or any needed collection is empty, they `sys.exit` with a `SINGLE SOURCE (ADR-017)` message. Their old file-reading helpers (`load_csv`, `load_json`, the treemap `_load`) are now guards that `sys.exit('SINGLE SOURCE VIOLATION …')` instead of reading a file. The dead local-file branches were removed.

2. **A guard blocks reintroduction — `scripts/check_single_source.sh`.** It fails if a generator loses its PB-required guard or its raising fallbacks, if a generator reads a data file directly (`csv.DictReader` / reading the `DATA` dir), or if a PR adds a `.csv`/`.json` under `data/dashboard/`. It runs:
   - **In CI** as the first step of the build job (`deploy.yml`) — server-side, on every push, so a failing guard fails the build, the deploy, and the auto-merge. No agent can bypass it.
   - **As a pre-commit hook** (`.githooks/pre-commit`) for fast local feedback.

3. **Data enters only through the pipeline.** New/established data reaches PocketBase via the ingestion + validation pipeline (Hillary) or curated in PocketBase; corrections go through Ask MIDD. Never a committed file, never a hardcoded literal.

## Consequences

**Better:** the dashboard/explorer can only render from PocketBase; if data is missing the build fails visibly instead of showing stale file data; the recurring bypass is structurally prevented, not just documented.

**Worse / watch for:** the build now hard-depends on PocketBase being up and seeded — that is intended (surfaces gaps immediately), and both env PBs are verified populated.

**The full data-flow, now single-source and coherent:**
- **Runtime** (`generate_dashboard`/`generate_explorer`) reads ONLY PocketBase, hard-fails otherwise (this ADR).
- **CI deploy** runs `db/pb_setup.py` / `db/pb_setup_explorer.py` with `PB_SCHEMA_ONLY=1` — ensures collections + missing fields, but **never re-seeds records**, so a deploy can no longer overwrite live PocketBase data (this closed the last hole: previously the CSVs overwrote PB on every deploy).
- **`data/dashboard/*.csv|json` are a git-tracked BACKUP mirror of PocketBase**, downstream of it, kept in sync **PB → files** by the scheduled Drift Check (`scripts/detect_drift.py`, opens a PR when PB changes). They are the DR copy + review surface + the bootstrap seed for an empty PB (`pb_setup` run WITHOUT `PB_SCHEMA_ONLY`). They are never a source, and the generators never read them.
- **DR restore** is `scripts/restore_from_git.py` (files → PB), manual only.

So there is one source (PocketBase); the files are its backup, not a competing source. The guard prevents any generator from reading a file; CI schema-only prevents any deploy from clobbering PB.

## Testing (ADR-018 to follow)
Going forward, all new pipeline/generator code ships with unit + integration tests at >90% coverage, gated in CI. The single-source guard itself has a negative test (reintroducing a fallback must fail it).

## Relationship to other ADRs
- ADR-011 — declared the single source; this ADR *enforces* it and removes fallbacks.
- ADR-013 / ADR-016 — promotion + hostname split; unaffected, both already PB-driven.
