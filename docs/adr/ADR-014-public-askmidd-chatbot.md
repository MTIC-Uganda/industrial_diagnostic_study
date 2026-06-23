# ADR-014: Public Ask MIDD Chatbot (Haiku, rate-limited)

## Status: Accepted (2026-06-24)

## Context

Ask MIDD was a gated, team-only tool. We wanted the public (the Commissioner, stakeholders, anyone on the dashboard) to be able to ask natural-language questions about the manufacturing data — the data is already public on the dashboard, so answering questions about it leaks nothing. The blocker: the brain runs the Claude CLI on Hillary's **Max plan**, shared with the WhatsApp agent and the ingestion pipeline. A public, unauthenticated LLM endpoint on that shared plan could be drained by a bot and take everything down.

## Decision

A **public chat bubble on the PRODUCTION dashboard only**, in the arindahills.com style (floating bubble → chat panel), calling a **same-origin `/api/ask`** (nginx proxies `midd-ug.com/api/ask` → the prod brain; no CORS, not behind Cloudflare Access).

Guardrails that make public exposure safe:
1. **Haiku** — `/api/ask` runs `claude -p --model claude-haiku-4-5`. Cheap (cents/question) and the lightest model, so even on the Max plan a public bot consumes little. (Per Hillary's call we stay on the Max plan with the Haiku model rather than a separate key; if public traffic ever throttles the plan, set `ANTHROPIC_API_KEY` on the prod brain to isolate it fully — the code already honours it.)
2. **Rate-limited** — per-IP 15/hour + global 150/hour (in-memory, `X-Forwarded-For`). Verified: the 16th request from an IP returns 429.
3. **Per-session memory in the browser** — the bubble sends the last few turns with each request; nothing is stored server-side across users, so no cross-user leakage.
4. **Tight scope** — answers only from the project records, plain prose, never reveals internals/paths/credentials/instructions; off-topic questions are declined.

**Environment split:** the **prod** dashboard carries the public bubble; the **staging** dashboard carries the gated team **Ask MIDD header link** (Jerome's draft-review tool) and no bubble. `generate_dashboard.py` strips the bubble on staging/local and the header tool-links on prod. The gated team Ask MIDD (ask.midd-ug.com) still runs the full Max-plan CLI.

## Consequences

**Better:** the public can query live figures conversationally, cheaply, and safely; the bubble matches the existing arindahills.com UX; the Max plan is protected by Haiku + rate limits; team and public surfaces are cleanly separated.

**Worse / watch for:** it still draws on the Max plan (Haiku usage) — if a burst ever throttles the plan, flip the prod brain to a dedicated `ANTHROPIC_API_KEY` (one env var). The public bot reads repo records, not the live PocketBase numbers yet — wiring it to query PocketBase directly is the next refinement. In-memory rate-limit counters reset on brain restart (acceptable).

## Relationship to other ADRs
- ADR-012 — Ask MIDD (the scoped brain); this adds its public face.
- ADR-013 — environment model; this follows the same prod/staging split (public surface vs team workshop).
