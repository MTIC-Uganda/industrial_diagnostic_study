# Meeting Minutes: Inception Report Dry-Run

**Date:** 2026-05-29
**Attendees:** Jerome Nuwabaasa (MTIC), Hillary Arinda (technical advisor), Solomon Ariho (lead executor)
**Type:** Dry-run presentation of inception reports before Commissioner submission

## Purpose

Solomon presented the two inception reports (Report 1: Iron & Steel, Copper & Allied Metals, Automotives; Report 2: remaining 6 value chains) to Jerome and Hillary as a rehearsal before Jerome presents to the Commissioner and the Technical Working Group.

## Summary

The structural design of the inception reports was endorsed by Jerome. Solomon read from the markdown document rather than presenting, which prompted an extended coaching session on presentation skills. Several positive surprises were discovered in the Claude-generated content, alongside specific factual errors that need fixing. Jerome will personally take over refinement of the documents and presentations over the weekend and will request a Commissioner slot for early next week. A new technical direction emerged: connecting Claude directly to ITC TradeMap for automated trade data extraction.

## Key Discussion Points

### 1. Presentation Skills Coaching (Jerome to Solomon)

Solomon read the document verbatim rather than presenting from understanding. Jerome's framework:

- Every presentation opens with a **table of contents** to manage expectations. People disengage when they do not know how many sections remain.
- A presentation is **pointers, not prose**. The presenter must hold the content in their head from prior reading, and use slides only as anchors.
- The **first slide must excite the audience** about what is coming next. Put 40% of design effort into the first slide.
- Close with a **clear ask**, not "any comments". An open ask invites filler questions and wastes time.
- The presenter is a **salesperson**. Every presentation is a pitch, regardless of audience.
- The only trick of presentations is genuine understanding of the content. There is no shortcut.

Solomon acknowledged that with repetition this becomes natural. Jerome confirmed: continue the current presentation as a learning vehicle, and the next one will be sharper.

### 2. Strong Points in the Generated Content

- **Cross-chain linkage discovered by Claude**: the three value chains in Report 1 were independently connected by Claude as a single integrated chain (mineral, processing, consumer product) ending at Kira Motors. This linkage was never explicit in the ToR. Jerome was excited by this framing and intends to use it with the Commissioner.
- **Tenfold Growth Strategy and ATMs framework**: Claude correctly referenced the ATMs acronym (Agro-industrialisation, Tourism, Mineral Value Addition, STI) and the underlying Ministry of Finance growth strategy, without those documents being shared in advance. Jerome will now formally upload these references.
- **Closing slide structure**: the ask slide (confirm scope, confirm prioritisation weights, confirm data sources) was well framed and is the right pattern to keep.

### 3. Content Issues to Fix

| Issue | Where | Fix |
|---|---|---|
| UDB (Uganda Development Bank) placed under "Industrial Association" | Stakeholder mapping slide | Move UDB to "Financial Institutions" |
| Prioritisation criteria use descriptive labels only | Prioritisation framework section | Convert to numeric weights (percentages) |
| A quoted line attributed to Hillary that does not appear in any shared input | Recommendations section | Remove or de-attribute |

### 4. Report Structure (endorsed)

1. Executive Summary (written last)
2. Background and Policy Context
3. Methodology and Analytical Framework
4. Diagnostic Analysis of the three value chains
5. Cross-Cutting Priority Options and Policy Recommendations
6. Investment Portfolio and Roadmap

The Investment Portfolio chapter is the most consequential. It must enable a clear decision. A report that does not enable a decision has failed.

### 5. Prioritisation Criteria Framework (endorsed)

- Accessible market (regional first, global second)
- Uganda's comparative advantage (raw material availability)
- Feasibility (technical and capital capacity)
- Job creation and income potential
- Import substitution impact (national sovereignty)

Each criterion needs a numeric weight. Solomon to update.

### 6. Data Source: ITC TradeMap

Jerome introduced [ITC TradeMap](https://www.trademap.org) as the canonical source for trade statistics. Run by the International Trade Centre (UN agency). UN Comtrade is the same underlying data. Both are used by the World Trade Organisation.

Hillary proposed connecting Claude directly to TradeMap so that data extraction stops being a manual exercise. Jerome confirmed this would significantly speed up the analysis for the remaining six value chains.

This becomes Solomon's next major assignment. See `setup/ASSIGNMENT_TRADEMAP_29MAY2026.md`.

### 7. Open Pull Requests

Hillary's instruction: Solomon should ask Claude to merge all open PRs to main. No human reviewer is available in the current window, and they are accumulating without serving a purpose. Once merged, the main branch reflects current state for Jerome to read.

## Decisions

1. **Inception reports are structurally accepted.** Content fine-tuning will be done by Jerome over the weekend.
2. **Jerome presents to the Commissioner**, not Solomon. Justification: ownership of the document by the ministry, and the consultant's role is to support, not to front the deliverable.
3. **The Commissioner meeting will be online and recorded** so the recording can be transcribed and fed back to Claude as Technical Working Group feedback.
4. **Jerome uploads supporting reference files** (ATM strategy, NDP IV, sector reports already in his possession) into the repo tomorrow morning, starting with files relevant to Report 1.
5. **Chapter work remains on hold** until the Commissioner meeting concludes and feedback is received.
6. **Document improvements go through Claude**, not direct edits, so Claude accumulates the design and content rules. Exception: when speed matters and the change is fully specified, direct edit is acceptable.

## Action Points

| # | Owner | Action | Due |
|---|---|---|---|
| 1 | Jerome | Fine-tune both inception reports, build PowerPoint versions | 2026-05-31 |
| 2 | Jerome | Request Commissioner slot to present inception reports | 2026-05-30 |
| 3 | Jerome | Upload supporting reference files into the repo | 2026-05-30 morning |
| 4 | Hillary | Help Jerome convert documents to polished PowerPoints via Claude or Gemini | On Jerome's request |
| 5 | Solomon | Fix UDB categorisation, convert prioritisation criteria to numeric weights, remove or de-attribute the misquoted line | 2026-05-30 |
| 6 | Solomon | Merge all open PRs to main via Claude | 2026-05-30 |
| 7 | Solomon | Set up Claude access to ITC TradeMap using his account (full brief in `ASSIGNMENT_TRADEMAP_29MAY2026.md`) | 2026-06-02 |
| 8 | All | Commissioner presentation meeting (online, recorded) | Early week of 2026-06-01 |

## Next Session

Jerome convenes the team once the Commissioner meeting recording is available. That recording becomes the official TWG feedback input. Chapter work resumes only after that.
