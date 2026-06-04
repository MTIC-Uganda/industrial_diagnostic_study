# Web-Sourced Data — Gap Fill

Jerome's upload (PR #32) covered most chains well. He confirmed that is all the
data he could find internally. This file records the **authoritative web sources**
located to fill the five remaining gaps, so chapter work can proceed with
complete information.

For trade figures (imports/exports/partners) we do **not** rely on these pages —
our own ITC TradeMap pipeline (`scripts/trademap_fetch.py`) pulls those live and
they are cited inline per the project rule. The sources below fill the
**non-trade** gaps: reserves, capacities, firm registers, and project status.

Compiled: 2026-06-01 (web research, June 2026).

---

## Gap 1 — Copper & Allied Metals  (was: only Kilembe doc)

**Status: FILLED**

| Data needed | Source | Key figures |
|---|---|---|
| Copper/cobalt reserves & grade | [DGSM — Redevelopment of Kilembe Mines](https://dgsm.go.ug/redevelopment-of-kilembe-mines/) (official, Directorate of Geological Survey & Mines) | Copper ore in excess of **6.5M tonnes at 1.77% Cu**; **5.5M tonnes at 0.17% cobalt**; Kasese District |
| Mine redevelopment / investor | [Mining Weekly — production sharing deal](https://www.miningweekly.com/article/uganda-signs-maiden-production-sharing-deal-to-revive-copper-mine-2025-03-04); [DGSM](https://dgsm.go.ug/redevelopment-of-kilembe-mines/) | **3 March 2025**: Uganda signed first mineral production-sharing agreement with **Sarrai Group + Nile Fibreboard** (selected from 14 bidders). Plan: copper cathode + cobalt metal |
| National mineral context | [Mineral potential of Uganda (DGSM)](https://dgsm.go.ug/) — also in Jerome's `data/mineral-resources/` | Exploration & development status |
| Copper trade (imports ~US$10.5m 2023; minimal exports) | **Our TradeMap pipeline** (HS 7402/7403/7407/7408/7413) | Pull live |
| Processors / cable makers | Firm-level: cross-reference UMA membership + TradeMap importer data; regional benchmark ZAMEFA (Zambia) | Limited domestic processing — itself a finding |

**Note:** Uganda has very little domestic copper processing. The near-absence of
local cathode/cable manufacturing is a key diagnostic finding, not just a data gap.

---

## Gap 2 — Petrochemicals & Fertilizers  (was: fertiliser brief + 2014 phosphates)

**Status: FILLED**

| Data needed | Source | Key figures |
|---|---|---|
| Petrochemical feedstock / refinery | [UNOC — Uganda Refinery Project](https://www.unoc.co.ug/midstream/the-uganda-refinery-project/) and [PAU — Refinery Project](https://www.pau.go.ug/the-uganda-refinery-project/) (both official) | **60,000 bpd** refinery at Kabaale, Hoima; produces fuels + **petrochemicals** + gas derivatives |
| Refinery status / investor | [Hydrocarbon Engineering, Oct 2025](https://www.hydrocarbonengineering.com/refining/13102025/uganda-refinery-to-start-operations-by-early-2030/); [Ecofin Agency](https://www.ecofinagency.com/news-industry/0310-49257-uganda-plans-to-launch-kabaale-oil-refinery-by-2030) | **$4bn**; UAE **Alpha MBM** implementation agreement **March 2025**; govt 40%; start **late 2029–early 2030** |
| Petrochemical park | UNOC / PAU; [Kabalega Petrochemical Industrial Park](https://www.pau.go.ug/the-uganda-refinery-project/) | Petrochemicals, kerosene, fertilizers, gas processing |
| Fertilizer plant capacity | [Osukuru Industrial Complex (Wikipedia)](https://en.wikipedia.org/wiki/Osukuru_Industrial_Complex); [Free Zones Authority](https://freezones.go.ug/president-commissions-tororo-sukulu-phosphate-project/) | Sukulu/Tororo: phosphate fertilizer **100,000 t/yr** (commissioned 2018); organic fertilizer up to 300,000 t/yr; + sulphuric acid + steel; operator **Guangzhou Dongsong**; ~$620m |
| Fertilizer trade | **Our TradeMap pipeline** (HS 3102/3103/3104/3105) | Pull live |

---

## Gap 3 — Pharmaceuticals  (was: sector profiles + NDA reports; no manufacturer register)

**Status: FILLED**

| Data needed | Source | Key figures |
|---|---|---|
| Manufacturer register | [Pharmaceuticals Index — Uganda](https://pharmaceuticalsindex.com/pharmaceutical-companies-in-uganda/); [Pharmchoices full list 2026](https://pharmchoices.com/full-list-of-pharmaceutical-companies-in-uganda/) | Full company directory with addresses |
| Lead manufacturer output | [Quality Chemical Industries (Wikipedia)](https://en.wikipedia.org/wiki/Quality_Chemical_Industries_Limited); [QCIL financials](https://africanfinancials.com/company/ug-qcil/) | **Cipla QCIL: ~1.2bn pills/yr** (Mar 2024); ARVs, antimalarials, NCD drugs; FY24/25 revenue UShs 267.1bn; exports to 13 African countries |
| Key local players | Monitor, EA Health | **QCIL/Cipla, Kampala Pharmaceutical Industries (KPI), Rene Industries, Abacus Pharma**; ~**70% of essential medicines imported** |
| Regulator data | NDA reports already in Jerome's `data/pharmaceuticals/` (annual report FY22/23; services performance FY23/24) | Manufacturer licences, import data |
| Pharma trade | **Our TradeMap pipeline** (HS 3003/3004) | Pull live |

---

## Gap 4 — Cement & Building Materials  (was: status report + sector info; no plant capacity)

**Status: FILLED**

| Data needed | Source | Key figures |
|---|---|---|
| Plant-by-plant capacity | [List of cement manufacturers in Uganda (Wikipedia)](https://en.wikipedia.org/wiki/List_of_cement_manufacturers_in_Uganda); [CemNet — Uganda](https://www.cemnet.com/global-cement-report/country/uganda) | **National installed ~6.8M t/yr**: Tororo 3.0M (44%), Hima 1.9–2.0M (28%), Simba 1.0M (15%), Kampala Cement 1.0M; Metro (Mbale); Sinoma (under development) |
| Limestone reserves | [Hima Cement](https://himacement.co/About-Us) | Dura quarry (Kamwenge) — limestone sufficient to **~2036** at current capacity |
| Producer detail | [Hima Cement Ltd (Wikipedia)](https://en.wikipedia.org/wiki/Hima_Cement_Limited); [Simba Cement (Wikipedia)](https://en.wikipedia.org/wiki/Simba_Cement_Uganda_Limited) | Plants: Hima (Kasese), Namanve blending, Tororo grinding; Simba clinker plant in West Pokot, Kenya (Apr 2024) |
| Cement trade (net exporter to RWA/KEN/SS/DRC) | **Our TradeMap pipeline** (HS 2523) | Pull live |

---

## Gap 5 — Plastics & Packaging  (was: VC draft + circularity strategy; no firm data)

**Status: FILLED**

| Data needed | Source | Key figures |
|---|---|---|
| Sector strategy / volumes | [NEMA — National Strategy for Plastic Circularity 2023–2028](https://www.nema.go.ug/new_site/wp-content/uploads/2024/05/Plastic_circularity_-Report-2023-1.pdf) (official) | Waste volumes, recycling targets, policy |
| Industry outlook | [Uganda Plastic Industry Outlook 2024–2028 (Reportlinker)](https://www.reportlinker.com/clp/country/6347/726256) | Market size & forecast |
| Major manufacturers | [Nile Plastic Industries](https://www.nileplasticindustries.com/); Nice House of Plastics (est. 1970, largest); [Quality Plastics recycling (Mukono)](https://www.scrapmonster.com/company/quality-plastics-u-ltd/156277) | Firm register; Uganda is a **net plastics importer** |
| Imports study | [Plastic Packaging: A Study on Plastic Imports in Uganda (IJSCIA)](https://www.ijscia.com/wp-content/uploads/2022/01/Volume3-Issue1-Jan-Feb-No.211-19-26.pdf) | Import composition |
| Waste sector | GIZ waste brief already in Jerome's `data/plastics-packaging/` | Recycling capacity |
| Plastics trade | **Our TradeMap pipeline** (HS 3915/3923/3920/3924) | Pull live |

---

## Summary

All five gaps now have authoritative sources. Priority of source type:
1. **Official Ugandan** (DGSM, UNOC, PAU, NEMA, Free Zones Authority) — used wherever available
2. **Company / regulator** filings (QCIL, Hima, NDA)
3. **Reputable trade/industry** press (Mining Weekly, Hydrocarbon Engineering, CemNet)
4. **TradeMap** for all trade figures (live, cited inline)

With Jerome's documents + these sources + the TradeMap pipeline, **all 9 value
chains now have sufficient data to execute both reports.**
