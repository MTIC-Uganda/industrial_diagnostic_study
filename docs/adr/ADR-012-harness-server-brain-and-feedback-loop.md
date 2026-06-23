# ADR-012: Harness, Server Brain, and Feedback Loop

## Status: Accepted (2026-06-23, from the harness + data architecture meeting)

## Context

The pipeline now has a working front (uploader), a single datastore (PocketBase, ADR-009/011), and a dashboard. What it lacks is a brain that improves and a shared memory. Today: corrections would be made by hand in PocketBase (untracked, and PocketBase is not smart); Jerome talks to the system through a personal WhatsApp agent that carries unrelated context; and the project's knowledge (decisions, current state) lives partly in Hillary's local machine and partly in the repo, so the three teammates' LLMs do not share one record. The result is lost context and a human kept in every loop.

The framing from the meeting: build a harness. A harness is the structure of dos, don'ts, and how, that an agent runs inside. On top of it sits a loop (the harness on a cadence, with an independent reviewer), and above that a self-improving system (the loop plus a memory that compounds). Every correction should improve an agent and be tracked, not applied blindly to the store.

## Decision

1. **One record of truth, on the server, that all teammates read.** The architecture decisions (these ADRs), the current-state file (hot file), and the agent definitions live in the repo and are mirrored to the server brain. The server brain keeps them current: when something changes, the brain updates the ADRs, the hot file, and the relevant docs, so Jerome's, Solomon's, and Hillary's agents all work from the same up-to-date record. Knowledge stops living only on one laptop.

2. **The three agents are the harness's workers.** Ingestion (reads an uploaded document via the Claude CLI on the server, extracts structured rows), synthesis (turns datastore rows into report and dashboard content), review (an independent check before anything is published). These exist in `agents/`; the harness gives them their dos and don'ts and wires them to the uploader and the datastore.

3. **Feedback routes through the LLM, never direct PocketBase edits.** PocketBase is the store, not the editor (ADR-009). When Jerome corrects something, the correction goes to the brain, which applies it through the ingestion/review agents and records it. Every piece of feedback improves one agent (a rule added, a mapping fixed) and is written to a tracked feedback log, so the next run is sharper and the change is auditable.

4. **A dedicated MIDD UI for Jerome.** A scoped web interface that talks only to the MIDD brain, with the knowledge of this project and nothing else. Jerome uses it to give feedback and pull information, instead of WhatsApp (a personal agent with too much unrelated context) or VSCode. Corrections he makes there flow through the LLM per point 3.

5. **Staging-first, with automated promotion.** All development and all of Jerome's experimentation happen on staging. Promotion to production is an automated, guarded pipeline, because production is live and the changes are large. (See the staging/prod split already in place: ADR-006, and the midd-ug.com domain with staging and production subdomains.)

6. **Portable by container.** The whole harness, agents, brain records, and the services, are packaged so they can move to another server or another LLM later (a Dockerfile). For this stage the brain uses the Claude CLI already on the Hetzner server; the model is swappable once the system is containerized and shipped.

## Consequences

**Better:**
- Corrections compound: each one improves an agent and is recorded, so the system gets sharper instead of being re-corrected the same way.
- One shared, current record means the three teammates' agents do not drift apart or re-derive context; work done by any of them updates the same ADRs and hot file.
- Jerome gets a clean, scoped interface and stops losing context in a personal chat agent.
- Production is protected by staging-first and an independent review step before publish.
- Portability is designed in, so the Hetzner CLI is a stage, not a lock-in.

**Worse or cost:**
- Building the harness, the feedback log, the self-updating record mechanism, and the MIDD UI is real work, sequenced after the data foundation (ADR-011).
- An independent reviewer and a feedback log add steps to each change; that is the deliberate cost of auditability and improvement.
- The server brain writing its own records needs write access and discipline so it does not corrupt the shared record; changes should be reviewable.

**Watch for:**
- Keep the standing record small and factual; procedures belong in the agents/skills, not in an ever-growing context file.
- The reviewer must be independent (a fresh context), or it rubber-stamps the producer's work.
- Do not let feedback bypass the loop into direct PocketBase edits; that breaks the audit trail and the learning.

## Relationship to other ADRs

- ADR-006 (staging/prod pipeline) and the midd-ug.com domain — the environments this runs in.
- ADR-007 (agentic pipeline) — the ingestion/synthesis/review agents the harness drives.
- ADR-009 (PocketBase backend) and ADR-011 (single-source structure) — the store the agents write to.
- ADR-010 (document intake and intent cadence) — the uploader and intent sidecars that feed the agents.

## Implementation order (Hillary)

1. Single record of truth: server brain keeps ADRs + hot file current (this ADR set is the start).
2. Feedback log + wire corrections through the ingestion/review agents.
3. Dedicated MIDD UI (scoped chat).
4. Automated staging-to-prod promotion.
5. Containerize.
