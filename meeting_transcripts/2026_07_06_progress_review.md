# MIDD Meeting, 2026-07-06: Display Fix, and the HS-to-SITC Data Model

Present: Hillary Arinda, Jerome Nuwabaasa, Solomon Ariho.
Raw transcript: `2026_07_06_progress_review.txt`.

## Context

Solomon is back on his laptop (the audio problem was a driver conflict, now uninstalled). Jerome has set up a small physical workspace for the team, meeting-first, work-from-anywhere, with video conferencing and meeting recording to be added. Two MIDD threads were the focus: Solomon's dashboard-display problem, and the data model for imports and exports.

## Thread 1: the dashboard display issue (resolved)

The upload pipeline itself is working and Jerome is very happy with it: every figure is traceable to the source file it came from, because the AI packages the file and tells Solomon exactly what to select, and Solomon reviews it before uploading. Jerome asked that this curated flow stay as it is ("better, until it becomes a bottleneck"), even though the AI could technically do the whole upload itself, because the human-review-and-trace step is worth keeping.

The one remaining problem was that data which had gone through the pipeline was not displaying. This is the Manufactured Imports card landing in staging PocketBase (8091) but not showing. Hillary took this as his own task to fix with his own agent (it was judged too critical to risk on Solomon's agent), and it is now resolved: the staging dashboard renders from staging PocketBase, so uploaded-but-unpromoted figures show for review before Apply to production.

## Thread 2: the data model (HS primary, SITC translator) — decisions

Jerome interrogated the current indicators source by source and found some figures were wrong or from unclear sources, so he is rebuilding the data with the authentic source named for every figure.

1. **One source of truth per record, and the primary trade data is HS codes.** All import and export data enters as HS codes (from ITC TradeMap). We do NOT store the same figure in both HS and SITC; that is duplication and bad design.
2. **A HS-to-SITC translator lives in PocketBase.** A mapping table (HS code to its corresponding SITC code) is loaded into PocketBase. Jerome provides the mapping file; Solomon uploads it. It is used only to facilitate the calculations, not for display.
3. **Derived indicators are CALCULATED, not entered by hand.** Load the primary base data (exports and imports by HS). Indicators like manufactured exports and high-tech exports are then computed automatically by pre-defined, official, mathematical rules that name the exact codes to aggregate. Where a rule is defined in SITC, the data is translated HS to SITC first, then aggregated; where a rule is HS-based, HS is used directly. The value shown on a card is the indicator, independent of whether HS or SITC was used underneath.
4. **The LLM only injects data into PocketBase.** Translation, aggregation, and display are pure, deterministic Python plus the code rules, not the LLM. Hillary's point: keep the LLM's role to data population; everything downstream is rule-based.
5. **ITC TradeMap is the primary source, and it is both up to date and granular.** Querying by month gives data current to month 03 of 2026 and granular to level 6. The earlier belief that TradeMap was not current was wrong.
6. **Every figure must name its authentic source** (which specific report or publication, for example UBOS Annual GDP FY2024/25 June 2026 release, or the UIA Industrial Park summary of 6 Feb 2025). Sources are kept in the background, a brief source rather than the full text on the card.
7. **Incremental monthly updates.** Once data is loaded up to month 03/2026, only one new month is added at a time (04 next). History stays in PocketBase.
8. Database cleanup is done on demand, not as a big upfront job.

## Action points

### Solomon
- Review the Manufactured Imports card on staging (now displaying after Hillary's fix). Have your agent read through what Hillary's agent did, confirm the figure is sensible, then Apply to production if it looks right.
- Build the HS to SITC mapping table (the translator) in PocketBase from the mapping file Jerome will share.
- Implement the model: all import and export data is stored as HS. Derived indicators (manufactured and high-tech exports and imports) are computed by the official code-aggregation rules. When a rule is SITC-based, translate HS to SITC via the table then aggregate; when HS-based, use HS directly. The LLM only injects the data; translation, aggregation, and display are Python plus the rules.
- Take Jerome's source-annotated export-data Excel and do the work to make the indicators display, and upload the source reports it references where needed.
- Keep the download-then-upload flow for now (manual). Explore whether the AI can pull directly from TradeMap (which needs the data sorted before download) rather than downloading by hand. Continue with one-month-at-a-time updates.

### Jerome
- Finish and share the source-annotated Excel (the authentic source named for every indicator) plus the export data, with Solomon.
- Provide the HS to SITC mapping file so it can be loaded into PocketBase as the translator.
- Later, for market analysis, provide the East African countries trade data (not now).

### Hillary
- Fix the Manufactured Imports display issue (staging 8091 vs prod 8090). Done: staging now renders from staging PocketBase.

## Off-topic (not MIDD, noted only)
- UTIMBER: Jerome asked Hillary to help set up video conferencing and Tactiq meeting recording for the new office; Hillary to finish the remaining UTIMBER stages (stage 7, CoC) and push, with letters expected by Tuesday.
- A KimFam tangent on the NSSF dividend model (cut-off-date interest) was discussed at the end; it belongs to KimFam, not MIDD.
