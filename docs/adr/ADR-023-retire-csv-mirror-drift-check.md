# ADR-023: Retire the CSV Mirror Drift-Check

## Status: Accepted (2026-07-10)

## Context

ADR-011 introduced a committed CSV mirror of PocketBase (`data/dashboard/*.csv`) plus a scheduled `drift-check` CI job (cron every 6h) that ran `scripts/detect_drift.py`, compared live PocketBase against the committed CSVs, and opened a PR whenever they differed so a human could accept (merge) or reject (close + `restore_from_git.py`) a suspected direct admin-UI edit.

ADR-017 later made PocketBase the **single source of truth**: the generators read only PocketBase, there is no file fallback, and `check_single_source.sh` enforces it in CI and pre-commit. Under ADR-017 the CSVs are no longer read at runtime; they are only the drift-check's comparison target.

That combination made the drift-check pure noise:
- Uploads, Apply-to-Production, and the ingestion agent all write to PocketBase continuously by design, so the CSV mirror is perpetually behind. Every 6-hourly run therefore found "drift".
- Once GitHub Actions was permitted to create PRs (2026-07-06, needed so the job could open its review PR at all), the job opened a **new PR every 6 hours** with no reviewer. 17 piled up in four days.
- Cancelled runs in the scheduled slot also produced false "BUILD FAILED" notifications to the team.

## Decision

**Retire the drift-check.** Remove the scheduled `drift-check` job and the `schedule` cron trigger from `.github/workflows/deploy.yml`. CI now runs only on `push` and `workflow_dispatch`.

PocketBase is authoritative (ADR-017), so the CSV mirror and its drift PR are no longer a meaningful control or backup. `scripts/detect_drift.py`, `scripts/restore_from_git.py`, and the `data/dashboard/*.csv` files stay in the repo as a historical snapshot and a manual tool, but CI no longer maintains them.

## Consequences

**Better:** no more 6-hourly drift-PR noise, no false failure pings from cancelled scheduled runs, and CI no longer wakes on a timer. One fewer moving part.

**Worse / watch for:** there is no longer an automated detector of a direct PocketBase admin-UI edit. The committed `data/dashboard/*.csv` are now a **stale historical snapshot, not a live mirror** — do not treat them as a backup. If a real PocketBase backup is wanted, snapshot at the PB level (`data.db`), not via the CSV mirror.

## Relationship to other ADRs
- ADR-011 — introduced the CSV pipeline + drift-check; this supersedes the drift-check portion of it.
- ADR-017 — PocketBase as the single source of truth; the reason the CSV mirror is now redundant.
