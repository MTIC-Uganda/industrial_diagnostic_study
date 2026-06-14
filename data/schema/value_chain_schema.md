# Value Chain Diagnostic Schema
**Author:** Jerome Nuwabaasa, MTIC
**Purpose:** Defines every field the diagnostic must measure for each of the 9 priority value chains. This schema is the contract between the ingestion agent (data collection), synthesis agent (report writing), and review agent (quality check). All three agents work from these field definitions.

**Governing framework:** Every field must ultimately connect to the Tenfold Growth Strategy. Fields that cannot inform a tenfold-growth decision are not included.

---

## SECTION A — Identity Fields
*Applies to all 9 value chains*

- Value chain name (text)
- Report number (Report 1 / Report 2)
- ToR reference document (filename)
- Chapter number in report (integer)
- Primary data source(s) (list)
- Date of last data update (YYYY-MM-DD)
- Data status (Complete / Partial / Gap)

---

## SECTION B — Current State Fields
*Applies to all 9 value chains. Units specified per field.*

### B1 — Production & Capacity
- Total installed capacity (tonnes/year or units/year — specify unit per chain)
- Capacity utilised (tonnes/year or units/year)
- Capacity utilisation rate (%)
- Number of active firms (integer)
- Number of production facilities/plants (integer)
- Total sector investment (USD million)
- Direct employment (number of workers)
- Indirect employment estimate (number of workers)

### B2 — Trade (sourced from ITC TradeMap, HS code specified per chain)
- Primary HS codes monitored (list)
- Total imports — value (USD million, most recent year)
- Total imports — volume (tonnes or units, most recent year)
- Top 3 import source countries (country names + USD value each)
- Total exports — value (USD million, most recent year)
- Total exports — volume (tonnes or units, most recent year)
- Top 3 export destination countries (country names + USD value each)
- Trade balance — surplus or deficit (USD million)
- Import dependency ratio (imports as % of domestic consumption)

### B3 — Raw Materials & Inputs
- Primary raw material(s) (name + source: domestic/imported)
- Raw material self-sufficiency (% sourced domestically)
- Key energy input (electricity / thermal / both)
- Energy cost (USD cents/kWh or USD/GJ)
- Water requirement (yes/no; intensity level)

### B4 — Key Players
- Name of company (text)
- Location (district/city)
- Value chain phase(s) operated (Phase I / II / III etc.)
- Installed capacity (tonnes/year or units/year)
- Ownership (domestic private / foreign private / state / joint venture)
- Notable facts (text — max 1 line)

### B5 — Market Size
- Domestic market size — current (USD million)
- Domestic market growth rate (% per year)
- EAC/regional market size — current (USD million)
- Uganda's current share of EAC market (%)
- Continental (Africa) market size — current (USD million)
- Global market size — current (USD billion)
- Uganda's current global export position (text — brief)

### B6 — Value Chain Map
- Number of phases in the chain (integer)
- Phase name (text, one per row)
- Phase description (text, one per row)
- Uganda's strength in phase (Strong / Emerging / Gap/Absent)
- Key bottleneck phase (phase name + 1-line explanation)

### B7 — Greening & Sustainability
- Current sustainability status (text — brief)
- Green technologies currently applied (list)
- Upcoming/emerging green solutions (list)
- Competitiveness impact of greening (High / Medium / Low + rationale)
- Circular economy opportunities (text)

---

## SECTION C — Constraints Fields
*Each constraint must have a weight and a data point. Minimum 5 constraints per chain.*

- Constraint name (text)
- Constraint category (Inputs/Raw Materials | Energy | Finance & Capital | Logistics | Skills & Workforce | Technology & Productivity | Standards & Quality | Policy & Regulatory | Water & Waste)
- Weight / severity (Critical = 5 | High = 4 | Medium = 3 | Low = 2 | Minor = 1)
- Evidence / data point (text — must cite a number or source)
- Regional benchmark (comparator country + figure, where available)
- Is this cross-cutting across multiple chains? (Yes / No)

---

## SECTION D — Market Projections to 2040
*Tenfold Growth Strategy governs Uganda projections. Business-as-usual for other markets.*

- Uganda domestic demand — 2040 projection (value + unit)
- Basis for Uganda projection (tenfold growth logic — explain the chain of reasoning, do not simply multiply by 10)
- EAC/regional market — 2040 projection (USD million, BAU growth)
- Continental market — 2040 projection (USD billion, BAU growth)
- Global market — 2040 projection (USD billion, BAU growth)
- Uganda's target market share by 2040 (% of EAC market)
- Uganda's target export revenue by 2040 (USD million)

---

## SECTION E — Priority Products
*3–4 products or sub-sectors Uganda should concentrate on. Each scored against the 5-criterion framework.*

For each priority product:
- Product / sub-sector name (text)
- Priority rank (1 = highest)
- Score — accessible market size (1–5)
- Score — Uganda comparative advantage (1–5)
- Score — feasibility (1–5)
- Score — job creation potential (1–5)
- Score — import substitution impact (1–5)
- Composite score (weighted average out of 5)
- Rationale (text — max 3 lines)
- Explicitly deprioritized products (name + reason, for each)

---

## SECTION F — Priority Action Matrix
*Three timeframes. At least 2 actions per timeframe.*

For each action:
- Timeframe (Quick win 0–12 months | Policy reform 1–3 years | Investment 3–5 years)
- Action description (text)
- Responsible institution(s) (list)
- Estimated investment required (USD million, or "policy — no capital cost")
- Expected output/result (text)
- Tenfold Growth alignment (text — 1 line)
- Green/sustainability dimension (text — 1 line, or "N/A")

---

## SECTION G — Chain-Specific Additional Fields

### Iron & Steel only
- Iron ore reserves (million tonnes)
- Ore grade (% Fe)
- Sponge iron / DRI capacity (tonnes/year)
- Scrap collection volume (tonnes/year)
- Cost per tonne of billet — DRI route (USD)
- Cost per tonne of billet — scrap import route (USD)

### Copper & Allied Metals only
- Copper ore reserves at Kilembe (million tonnes)
- Cobalt content (% Co)
- Mine status (Active / Dormant / Under development)
- PSA/mining agreement status (text)
- National grid electrification rate (%) — as proxy for cable demand

### Automotives only
- Annual vehicle registrations (units)
- Annual used vehicle imports (units)
- Domestic assembly capacity (units/year)
- Local content ratio (%)
- KMC plant status (text)

### Textiles & Garments only
- Cotton output (bales/year)
- Ginnery utilisation rate (%)
- Lint processed domestically (% of total lint)
- Number of ginneries (integer)
- Number of integrated mills (integer)

### Pharmaceuticals only
- Domestic market size (USD million)
- Import dependence rate (%)
- Number of WHO-GMP aligned manufacturers (integer)
- NDA-registered products manufactured locally (integer)

### Petrochemicals & Fertilizers only
- Fertiliser supply (tonnes/year)
- Fertiliser demand (tonnes/year)
- Fertiliser supply gap (tonnes/year)
- Refinery status (text)
- Refinery expected commissioning (year)

### Sugar & Confectionery only
- Annual sugar output (tonnes)
- Structural surplus/deficit (tonnes)
- Ethanol production capacity (litres/year)
- Molasses utilisation rate (%)
- Co-generation installed capacity (MW)

### Plastics & Packaging only
- Virgin resin imports (tonnes/year)
- Plastic waste generated (tonnes/day)
- Plastic waste formally collected (%)
- Number of UNBS-certified converters (integer)

### Cement & Building Materials only
- Clinker production capacity (Mtpa)
- Clinker import dependency (%)
- Cement grinding capacity (Mtpa)
- Cement export volume/value (tonnes / USD million)
- New clinker investment under construction (USD million)
