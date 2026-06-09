# ADR-008: Auto-merge and Self-healing Deploy Loop

## Status: Accepted

## Context

The staging/prod pipeline (ADR-006) required a manual PR merge step to promote from staging to prod. This created friction: Solomon or Hillary had to actively merge each branch. Additionally, transient failures (SSH blip, nginx restart) caused false-fail CI runs that blocked deployment without any real code problem.

Two gaps: (1) no auto-merge from feature branch to main when staging passes; (2) no retry on transient infrastructure failure.

## Decision

Single `deploy-prod` job that runs whenever staging passes, regardless of branch:

1. **Auto-merge:** After prod promotion succeeds, if the push came from a non-main branch, the workflow merges the branch to main automatically (`git merge --no-ff` + `git push origin main` using `GITHUB_TOKEN`). Merge conflicts cause a warning (not a failure) because prod was already successfully updated. `GITHUB_TOKEN` pushes do not re-trigger workflows by design, keeping main current without a redundant CI run.

2. **Self-heal retry loop:** The staging deploy+health-check sequence retries up to `MAX_HEAL_ATTEMPTS` (default 3) times before failing. Each attempt re-runs `scp` then polls for HTTP 200. This handles transient SSH failures and nginx restarts without human intervention. Persistent failures (bad file, server down) still fail loudly after the limit.

3. **Prod short URL** baked into the workflow env (`PROD_SHORT_URL`): `https://tinyurl.com/28lxntmc` — printed on every successful prod deploy for easy sharing.

## Consequences

Better: Solomon pushes a branch, CI handles the rest without any manual step. Transient failures self-recover without paging the team. Main is always in sync with what is in prod.

Worse: If two feature branches race (both pass staging simultaneously), both auto-merge commits land on main. For single-file HTML this is low risk. If the repo adds multiple files, switch to a PR-based merge queue.

Watch for: `MAX_HEAL_ATTEMPTS` is tunable via the env block. Increase if the Hetzner server restarts are slower than the retry window. The self-heal loop here is infrastructure-level (retry the scp). Phase 2 adds a code-level self-heal loop in the review agent (synthesis FAIL → fix → resubmit).
