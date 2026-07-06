# ADR-022: Upload Progress Notifications to the WhatsApp Group

## Status: Accepted (2026-07-06)

## Context

The uploader commits an uploaded document with `[skip ci]` and launches the
orchestrator (`scripts/process_upload.py`) **detached** on the box
(`ingest-staging.sh` runs `setsid python3 scripts/process_upload.py &`). Its
stdout goes to `/var/log/mtic-orchestrator-<env>.log`, which nobody watches. So
the operator uploads, sees "processing started", then waits 10 to 20 minutes
**blind** — and when the ingest produces nothing or fails, there is no signal and
no reason. Solomon's words (2026-07-06): "You upload stuff and have absolutely no
idea if there is any cooking taking place. You wait 10 to 20 min only to be told
there was no firewood after all." This is step 1 of a two-step "realtime
feedback" ask; step 2 is a live per-upload status inside the uploader UI.

## Decision

The orchestrator posts a short line to the **MTIC WhatsApp group** at three points:
- **Start** — "Processing <file> (<env>): <route>. This takes a few minutes…"
- **Success** — "Done (<env>): <file> processed, dashboard updated."
- **Failure** — "Failed (<env>): <file> did not finish (<route>). <reason>", where
  `<reason>` is the last stderr line of the failing step.

It uses a dedicated notifier, `scripts/midd_notify.py`, which reuses the existing
whatsmeow bridge endpoint (`localhost:8080/api/send`) that
`promote_staging_to_prod.sh` already posts to. Two invariants make it safe to wire
into the live pipeline:

- **Opt-in.** `notify_group()` does nothing unless `MIDD_NOTIFY` is truthy. Tests,
  CI and local runs leave it unset, so they never touch the network or slow down.
  The box ingest scripts (`ingest-staging.sh`, `ingest-prod.sh`) set `MIDD_NOTIFY=1`.
- **Fail-safe.** It never raises. Any bridge problem (down, timeout, non-2xx) is
  swallowed and logged, returning `False`. A notification issue must never break or
  delay an ingestion. `process_upload.py` also re-raises unchanged after posting a
  failure line, so exit behaviour is identical to before.

Config env: `MIDD_NOTIFY` (enable), `MIDD_BRIDGE_URL` (default
`http://localhost:8080/api/send`), `MIDD_GROUP_JID` (default the MTIC group).

## Consequences

**Better:** the team sees uploads start, finish, or fail — with a reason — in real
time, instead of waiting blind; reuses proven group-post infrastructure; zero risk
to the pipeline (opt-in + fail-safe, fully unit-tested at 100% of changed lines).

**Worse / watch for:** the group receives more messages (each is labelled by env;
staging rehearsals are included on purpose, since that is where operators work);
the failure reason is the last stderr line, which can be terse (the full detail is
still in the box log and, in step 2, the per-stage status); delivery depends on the
bridge being up — best-effort, so a down bridge means no message, never a broken
upload.

## Relationship to other ADRs
- Extends the upload pipeline; introduces no new data source (ADR-011 / 017 hold).
- Reuses the WhatsApp bridge that ADR-independent `promote_staging_to_prod.sh` uses.
- Step 2 (live per-upload status in the uploader UI) will build on `agents/_status.py`.
