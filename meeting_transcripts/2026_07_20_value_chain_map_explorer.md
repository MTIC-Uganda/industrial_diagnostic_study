# MIDD Catch-up, 2026-07-20

**Date:** 2026-07-20
**Attendees:** Jerome Nuwabaasa, Solomon Ariho, Hillary Arinda
**Topics:** MIDD value-chain map vs Explorer consistency, PocketBase data fetching; UTIMBER handled separately in its own minutes

---

## Summary

A working review of the MIDD value-chain platform focused on two structural fixes before any data-correctness pass. First, the **map and the Explorer must show the same products**, with the map as the birds-eye view (inputs to products only) and the Explorer as the detail (technologies, labour, trade). Iron and steel currently differs between the two. Second, some Explorer views are **not fetching trade data from PocketBase**, so pages must be made to read live from the database rather than show stale or generic content. Jerome wants the assignment closed this week so July payment can be processed, and asked Solomon to work close to full-time on it, delivering the structural alignment by tomorrow.

---

## MIDD

### Map vs Explorer consistency
- The **map is the birds-eye view**: it should carry only **inputs leading to products** (and product stages). Technologies and labour do **not** belong on the map; they are seen more clearly in the Explorer.
- The **Explorer is the detail of the map**: same value chain, but it goes deep (technologies, the professionals/labour needed, trade data). Jerome's framing: "the Explorer is the detail, the map is the birds-eye view," and the two must be structured identically per product.
- **Iron and steel** is the current mismatch: the products in the map and the products in the Explorer are not the same, and Solomon added some extra products in the Explorer that still need rearranging. Align them exactly.
- Jerome liked the more colourful map styling; it reads better.

### PocketBase data fetching
- On **cold rolled coil**, one view returns data (import HS code, exports Uganda HS code) while another shows "no HS-code specific trade data fetched yet." So the data exists in the database, but some Explorer views are not fetching it.
- Requirement: pages must **fetch live from PocketBase** for all products. If the database genuinely has no data, the page should say so, but it should still be fetching, not showing hardcoded or generic content.
- Jerome wants to **clarify which trade data and which industries data sit in PocketBase**, so that when he gives instructions the pages reliably pick from there and any remaining issue is just a matter of correcting the data.
- Hillary walked through the fetch-and-render architecture (database, then data-access/repository layer, then service layer, then controller/API, then the UI viewer) and stressed that a **refresh should re-fetch**: if a record is updated in the database, refreshing the UI should reflect the new value. Data should never be fetched once and rendered forever. Solomon to confirm whether the current pages fetch live or cache, and Hillary to send him the explainer diagram.

### Sequence
1. Fix structure first: align iron and steel (and then all products) in the Explorer to the map, strip technologies/labour from the map.
2. Make the pages fetch live from PocketBase.
3. Only then do the data-correctness pass (correct wrong values; the structure is otherwise considered good).

---

## Other business: dairy cooperative opportunity (separate from MIDD)

Jerome and Solomon visited a **40-member dairy cooperative in Rwemondo** (near Kazo, about five minutes from the trading centre), chaired by an enthusiastic older farmer. The cooperative runs a milk cooler collecting about **2,500 litres per day combined** (roughly 62 litres per farmer). The plan is to organise them for financing: capture each farmer's data (farmland, production potential, capital needs), build financials, and present to a financier to scale from **2,500 to about 30,000 litres per day** (roughly 10x) over a few years, with per-farmer targets. Field forms have been collected; Solomon has sent them to Jerome, and data entry will be done by someone on Jerome's side (Solomon not to do the data entry). Noted here as a distinct opportunity, not part of the industrial diagnostic study.

---

## Action points

### Solomon
- Dedicate close to full-time this week to MIDD.
- **By tomorrow:** align the iron and steel products in the Explorer to match the map exactly; strip technologies and labour from the map so it shows only inputs to products; make the pages fetch live from PocketBase for all products.
- Confirm whether the current pages fetch live from the database or cache, then alert Jerome to review the structure.
- After structure is agreed, move to the data-correctness pass.

### Hillary
- Send Solomon the fetch-and-render architecture explainer (database, repository, service, controller/API, UI; refresh re-fetches).
- Share the action points with Solomon.

### Jerome
- Review the structure once Solomon alerts that the alignment and fetching are done.
- Process the July payment next week; wants the assignment fully closed this week.
