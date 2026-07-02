# ADR-018: Testing Standard — Unit + Integration, >90% on New Code, CI-Gated

## Status: Accepted (2026-07-02)

## Context

The pipeline had no automated tests. Bugs (the PocketBase URL-encoding crash, the migration-replay outages, the fallback bypasses) were all caught in production or by eye. Hillary's directive: going forward, clear, well-written unit and integration tests with >90% coverage.

## Decision

1. **Every new or changed pipeline/generator/agent change ships with tests.** No feature merges without them.
2. **>90% coverage on new/changed code**, measured with `diff-cover` against the merge base (not a flat repo-wide number — the existing monoliths are refactored and covered incrementally, a ratchet, not a big-bang retrofit).
3. **Two layers:**
   - **Unit** — pure functions tested in isolation (mocked I/O). This requires code be written *importable*: real logic in functions, side effects behind `if __name__ == "__main__":`. Refactoring `generate_dashboard.py`, `generate_explorer_data.py`, `db/pb_setup.py` into importable units is the first coverage task.
   - **Integration** — the real flow against an ephemeral/test PocketBase (seed a throwaway PB, run the generator, assert the output). To be added with the refactor.
4. **CI-gated.** `pytest` runs in the build job (`deploy.yml`) before anything is generated or deployed; a failing test fails the build, the deploy, and the auto-merge. Harness: `pytest`, `pytest-cov`, `diff-cover` (`requirements-dev.txt`), tests in `tests/`.
5. **Guardrails get negative tests.** e.g. the single-source guard (ADR-017) has tests asserting the generators refuse to run without PocketBase and that a reintroduced file read is detected (`tests/test_single_source.py`).

## Consequences

**Better:** regressions are caught before prod; the single-source and migration-safety rules are now executable checks, not just prose; new code is written testable by default.

**Worse / watch for:** the existing scripts run top-level code at import (auth, PB fetch), so they are not yet unit-importable — current tests exercise them via subprocess (behavioural), which does not register line coverage. Reaching the >90% figure requires the refactor in point 3; that is the active ratchet, tracked in TASKS.md. Integration tests need a disposable PocketBase in CI, not yet wired.

## Relationship to other ADRs
- ADR-017 — single source; its guard is the first thing under test here.
- ADR-008 — the auto-merge/self-heal loop that these tests now gate.
