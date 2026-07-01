# MIDD Meeting, 2026-07-01: Progress Review and Next Steps

Present: Hillary Arinda, Jerome Nuwabaasa, Solomon Ariho.
Raw transcript: `2026_07_01_progress_and_next_steps.txt`.

## Context

The new MTIC minister is data driven. His line to the commissioner: "if you don't have data, don't talk to me; back everything with numbers and defendable sources." The commissioner has pushed that onto Jerome. So this project is no longer a one off report, it is continuous diagnostics work (paid, quote going in). Target: have something interactive to demonstrate to the minister by Monday next week.

## Summary of decisions

1. **Every figure needs a specific, defendable source.** Not "UBOS" but which UBOS document or report or link. Source shown as a footer on every card, same level on all cards, with the detailed source revealed on hover.
2. **UBOS is the primary source.** Get data from UBOS first; use ITC TradeMap only where UBOS has no data or cannot break it down. UBOS is the official national source; even industry-register data we compile is handed to UBOS to become official.
3. **HS codes on every product/stage of the value chain.** A product can have more than one HS code (for example used clothing versus new clothing). Import value for a product is the sum across its HS codes. Value chain level import/export needs TradeMap (HS 6 digit); UBOS only goes to SITC level 2, too broad for chain analysis.
4. **The minister's per product questions must be answerable** (design the slots now, fill later): how much imported, how much exported, how many industries produce it, and the total installed capacity of those industries. Example he pushed: steel wire (HS 7217.20).
5. **Bug:** the value chain map shows "trade data not yet available" even when the HS code is linked. TradeMap data exists for the code; yellow/estimated just means not yet harmonised, still usable. It should pull.
6. **Single uploader = Solomon.** Jerome does not want to upload. All documents enter through the one workflow: staging uploader, then Ask MIDD for corrections, then Apply to Production. Corrections go through Ask MIDD, never direct PocketBase edits; do not hand create collections, let the AI, then correct via Ask MIDD.
7. **Hard rule: all data comes from the central database, nothing hardcoded.** Jerome's explicit requirement. Hillary to verify tonight.
8. **Mobile app must be cross platform, not Android only** (a public facing app should not be Android only). This drives the tech stack choice; decide now.

## Action points

### Jerome
- Call UBOS tomorrow after 9am to request more broken down data (HS 6 digit level). If unavailable, we stay on TradeMap.
- Send the manufacturing value added and tax contribution table with both percentages and figures, early tomorrow morning.
- Send the Tenfold Growth detailed table.
- Provide the specific, defendable source for each figure (which UBOS document/report/link).

### Solomon
- Sources as a footer on every card, consistent placement, with the detailed source shown on hover.
- Apply the UBOS first data policy; TradeMap only where UBOS cannot provide or break down.
- Show HS code(s) on every product/stage; support multiple HS codes per product; import value = sum across a product's codes.
- Add per product data slots (can be blank for now): imports, exports, number of industries, total installed capacity.
- Fix the "trade data not yet available" case: pull TradeMap data when the HS code is linked (estimated/yellow is still usable).
- Value chain map visuals: icons only (no labels), icons resembling the item; more vivid colours (current blue too dull); wider spacing between groups; drill down by district on the map, both sides drillable. Reference: OEC (Observatory of Economic Complexity).
- Become the single document uploader via the staging workflow (upload, Ask MIDD, Apply to Production). No direct PocketBase edits, no hand created collections.
- Clarify the estimated vs indicative labels for laymen.

### Hillary
- Tonight: verify all dashboard data comes from PocketBase, nothing hardcoded. Fix immediately if any is.
- Wire Ask MIDD to read the live data so it can answer the per product questions; add the self improvement loop (rate answers, learn from failures).
- Drive the cross platform mobile stack decision (affects technology choice).
- Send Jerome and Solomon their messages (Jerome: action points only; Solomon: the detail).

## Deadline
Interactive demo ready for the minister by Monday next week.
