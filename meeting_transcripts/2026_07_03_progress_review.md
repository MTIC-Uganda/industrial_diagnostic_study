# MIDD Meeting, 2026-07-03: Data Sources, Coding Standards, and the Manufactured-Exports Card

Present: Hillary Arinda, Jerome Nuwabaasa, Solomon Ariho.
Raw transcript: `2026_07_03_progress_review.txt`.

## Context

Two updates framed the call. Hillary hardened the harness: more single-source rules so the AI cannot fetch from the wrong source by mistake, removal of data that could have leaked in via a hardcoded path, and a test suite so any new development must pass existing tests and add new ones before it can change a system that is now large enough that a careless change could hurt stability. He also tightened the public chatbot, which previously had access to information that should not be public (how the whole system is set up); it is now being limited to the database, with an ask, rate, repeat improvement loop to tune it over time.

Jerome had visited UBOS in person and came back with a data problem that forces a decision about which trade data the dashboard uses, and how it is coded.

## The data and coding problem

Three coding systems describe the same product with three different codes:

- HS codes: the customs standard. This is what URA captures at the border and what ITC TradeMap publishes.
- SITC (Standard International Trade Classification): what UBOS uses. UBOS converts URA's HS data into SITC because SITC is its capture standard.
- ISIC: what the manufacturing statisticians use. Different again.

So the same product, for example cotton yarn, has one code in HS, a different one in SITC, and another in ISIC. This is a legacy of different organisations in the same country each adopting a different standard.

The real constraint is not the coding, it is granularity versus recency:

- UBOS has recent data (up to 2025, monthly into 2026) but only aggregated, roughly SITC level 2. It gives "meat and meat preparations" as one total, not the breakdown into specific cuts. UBOS holds the granular detail but does not publish it; access would need an official written request.
- ITC TradeMap has granular data (broken down to specific products by HS code, so cotton yarn can be isolated) but it is older, 2024.

So the choice is granular but old (TradeMap), or recent but aggregated (UBOS). We want granular and recent, which currently means URA, and we do not yet have a URA plug.

## The legal definition of "manufactured"

Manufacturing has a legal statistical definition, not a layman one. For manufactured exports, UBOS counts SITC sections 5, 6, 7 and 8, excluding 68 (non-ferrous metals). Sections 0 to 4 are not counted as manufactured (food, live animals, animal oils and fats, gas, electric current, crude materials, textile fibres, pulp). High-tech manufactured exports are a further defined subset. Jerome's point: you must use the legal definition, the way citizenship has a legal definition regardless of where someone was born.

## Summary of decisions

1. Split the data by purpose. For the aggregate indicators (manufactured exports, high-tech exports), use UBOS aggregated data because it is recent and granularity is not needed for a single total. For the value chain breakdown, product by product, use the HS-code TradeMap data because it is granular, even though it is 2024, and label the data year clearly.
2. Manufactured exports on the dashboard uses UBOS SITC sections 5, 6, 7, 8 excluding 68. Solomon uploads the UBOS composition-of-exports Excel through the pipeline; Jerome will point him to it.
3. Show manufactured exports and manufactured imports on the same card, inflow against outflow, not a single number. Imports matter for the import-substitution story.
4. Never overwrite or delete data on update. Keep every year in the database, display the latest by default, but let the user pick years and see a trend. TradeMap is 2024; when recent URA data arrives it updates rather than replaces, so the history is preserved. Hillary was firm on this: we went through a lot to get this data, group it by year in the backend, keep it even if it is not displayed.
5. The pitch to the minister: the system is already configured to analyse by HS code on old data. All the minister needs to do is get us a plug into URA for recent granular data, and the same analysis runs on current numbers. Do the analysis on old data first so there is a working demonstration to justify the URA access.
6. The longer aim: with per-HS-code trade plus a count of industries producing each product (and eventually installed capacity), the system can flag gaps automatically, high imports with few local producers is an opportunity, and surface them on the Sankey so a user can drill into where the opportunity is.

## Action points

Only Solomon has action points. Hillary and Jerome both confirmed they have none from this meeting; everything actionable flows to Solomon.

### Solomon
- Clear yesterday's backlog first (the work agreed in the previous session that was not done).
- Fix the dashboard so it actually reads from the database. Right now the card shows the UBOS section but no data is coming through; the link is there but it is not seeing data in the database. Rectify so the values render from PocketBase.
- Download the UBOS composition-of-exports Excel: UBOS website, hover Statistics, External Trade, composition of exports (1996 to March 2026). Use calendar year, not financial year, to match TradeMap. Jerome will share the exact location. Also grab composition of imports for the import side.
- Upload that Excel through the pipeline (staging upload, Ask MIDD, Apply to Production). This doubles as an end-to-end test of the pipeline.
- Manufactured-exports and high-tech-exports indicators: use UBOS aggregated data, SITC sections 5, 6, 7, 8 excluding 68 (non-ferrous metals). Keep the granular HS-code TradeMap data for the per value chain product breakdowns.
- Put manufactured exports and imports on the same card, showing what comes in against what goes out, not one aggregate figure.
- On update, do not overwrite or delete existing data. Retain all years in the backend, group by year, display the latest but allow year selection and a trend view.

## Admin and cadence (no action for the dev pipeline)

- Payment: the payment to the company was not processed before the financial year closed (the solicitor did not clear it). The commissioner has said to complete the administrative requirements and the payment will be processed through the first portal; a route will be found either way. Contracts are backdated to the 24th (start date 1 July, so we are treated as already started) and will most likely land next week.
- Meeting cadence: no Sunday meeting. Jerome will limit standing meetings and request one only when a decision or a blocker needs him. General meetings when necessary.
