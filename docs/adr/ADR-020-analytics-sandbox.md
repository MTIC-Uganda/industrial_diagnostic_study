# ADR-020: Read-Only Analytics Sandbox for Ask MIDD (safe but powerful)

## Status: Accepted (2026-07-03)

## Context

The DB tool-use added in ADR-014 lets the chatbot answer data questions by turning them
into a validated PocketBase query (count / list / filter). That is safe but narrow: it can
only do what the whitelist in `query_tool.py` allows. The requirement grew: Ask MIDD should
be able to run real analysis, any read-only question the data can answer, using the full
scientific-python stack (pandas, numpy, scikit-learn, scipy, statsmodels, matplotlib, and so
on), including charts. Not limited to a fixed set of aggregations.

The power comes from executing model-written Python. On a system where PocketBase is the
single, untouchable source of truth (ADR-017), and one surface is public, that raises a hard
constraint: the analysis must be able to query anything but alter nothing, and it must not be
able to reach the operating system, the network, or the datastore's write path.

## Decision

Add `midd-brain/analytics_sandbox.py`: a four-layer read-only sandbox. Analysis code may
compute freely; it can never mutate a table or escape the namespace.

1. **AST validation** (`validate_code`, static): reject imports outside a generous
   scientific-python whitelist, reject dunder-attribute access (`__globals__`,
   `__subclasses__`, `__class__`, ...), reject dangerous builtins (eval, exec, compile, open,
   `__import__`, getattr/setattr/delattr, globals/locals/vars, ...).
2. **Restricted builtins** (`build_safe_builtins`): the exec namespace exposes only harmless
   builtins plus a guarded `__import__` that admits only whitelisted modules. Runtime
   enforcement even if the static check is bypassed.
3. **Read-only data**: the collections are passed in as in-memory pandas DataFrames. There is
   NO PocketBase handle, NO credentials, NO network client, NO write path in the namespace.
   ADR-017 holds by construction: the source is unreachable from analysis code.
4. **Process isolation** (`run_analysis`): the exec runs in a short-lived subprocess with a
   CPU + address-space rlimit and a wall-clock timeout, so a runaway or crash cannot take the
   brain down. Falls back to in-process execution (guards intact) where a subprocess cannot
   be spawned.

Charts are supported: matplotlib runs headless (Agg backend forced) and the active figure is
returned as a base64 PNG data URI.

**Reach:** this ships to the GATED team Ask MIDD first (behind Cloudflare Access, ADR-015,
trusted users). The public bubble keeps its narrow, validated `query_tool` queries. Opening
the sandbox to the public would additionally require a no-network container namespace; the
architecture supports adding that layer without changing the sandbox contract.

## Consequences

**Better:** the team tool can answer open-ended analytical questions (group-bys, correlations,
regressions, clustering, trend analysis, charts) instead of only whitelisted counts. The
read-only guarantee is enforced structurally, not by trust.

**Worse / watch for:** executing model-written code is inherently higher-risk than a query
whitelist; the mitigations are the four layers above and gating to trusted users. Python
sandboxes have historically been escaped through dunder chains and permissive builtins, which
is why both the static dunder/name checks and the restricted-builtins layer exist, and why
public exposure is deferred until container-level network isolation is in place. The module is
unit-tested (`tests/test_analytics_sandbox.py`, 93%), with the rejection cases treated as
first-class as the happy path.

## Relationship to other ADRs
- ADR-014 — the DB tool-use this extends (whitelist queries remain the public path).
- ADR-015 — Cloudflare Access gating that makes team-first exposure safe.
- ADR-017 — single source of truth; the sandbox is read-only by construction, upholding it.
- ADR-018 — testing standard; the sandbox meets the >90% coverage bar on changed code.
