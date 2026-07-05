# ADR-021: HS Is the Primary Trade Code; SITC Is Derived via a Translator

## Status: Accepted (2026-07-06)

## Context

Uganda's trade figures exist in several classification systems: HS (the customs standard, what ITC TradeMap and URA publish), SITC (what several indicator *definitions* use, e.g. manufactured exports = SITC 5,6,7,8 excl 68; the high-tech and medium-tech bands are also defined by exact SITC codes), and ISIC (manufacturing). The same product has a different code in each.

Two problems forced a decision:
1. **Which source, and is it current?** We had assumed the granular HS source (ITC TradeMap) was not up to date. On inspection it is: querying TradeMap *by month* gives data current to the latest month (e.g. 2026-M03) AND granular to HS 6-digit. So one source can be both current and granular.
2. **How to serve SITC-defined indicators from HS data without duplicating storage.** Several indicators (manufactured/high-tech exports and imports) are *defined* by SITC code sets, but our primary data is in HS. Storing the same figure in both HS and SITC is duplication and a second source of truth per record, which the single-source rule (ADR-017) forbids.

The 2026-07-06 meeting (Jerome, Solomon, Hillary) settled the model, building on the earlier finding that the key-indicator cards should be *computed* from primary data (ADR-020 gave the agent the ability to compute), not hand-entered.

## Decision

**HS is the single primary code for all trade data. SITC (and any other classification an indicator needs) is derived on demand through a translator table in PocketBase. Derived indicators are computed by official, pre-defined code-aggregation rules — never hand-entered.**

Concretely:
- **Primary data enters as HS codes** (from ITC TradeMap), one row per figure, one source of truth per record (ADR-017). We do NOT also store the SITC form of the same figure.
- **A HS → SITC mapping table lives in PocketBase** (the "translator": HS code → corresponding SITC code). It is reference data, loaded from a mapping file, used only to facilitate calculations — not for display.
- **Derived indicators are calculated, not entered.** Manufactured exports, high-tech/medium-tech exports, and the import equivalents are computed by the official rules, which name the exact codes to aggregate. When a rule is defined in SITC, the HS data is translated to SITC via the table and then the named codes are summed; when a rule is HS-based, HS is used directly. The value shown on a card is the indicator, independent of which code system was used underneath.
- **The LLM only injects data into PocketBase.** Translation, aggregation, and display are deterministic Python plus the rule sets — not the model. (The scorecard-ingestion agent, ADR-020, is the injection path; the computation it writes is read-only and rule-driven.)
- **Every figure names its authentic source** (which specific report/publication), kept in the background as a brief source rather than full text on the card.
- **Updates are incremental**: once loaded to a given month, only the new month is added; history persists in PocketBase.

## Consequences

**Better:** one source of truth per record is preserved even though indicators span HS and SITC; adding a new SITC-defined indicator means adding a rule, not a second data feed; TradeMap-by-month gives current + granular data from one source; the derived figures are reproducible from the primary data plus fixed official rules, so they are defensible and traceable to a named source.

**Worse / watch for:** the HS↔SITC mapping is large and must be correct — a bad mapping silently skews every SITC-defined indicator, so the table is reference data to be validated, not guessed. The official code sets must be transcribed exactly (they name precise codes; "looks like it belongs" is not allowed). A second trade source would reintroduce a comparator/discrepancy problem and is explicitly avoided unless a real cross-check is wanted. Translation and aggregation must stay in deterministic Python; pushing that reasoning into the LLM would make figures non-reproducible.

## Relationship to other ADRs
- ADR-011 / 017 — single source of truth per record; this keeps it while serving multiple classifications.
- ADR-020 — the analytics sandbox / key_indicators agent is how computed figures are produced and injected, read-only.
