# Data Freshness Audit

A full review of **every** data source we hold — Jerome's uploads (PR #32) and
the web-sourced gap fill — checking each against the latest available
information (web research, June 2026). Goal: every part of both reports rests
on the best, most up-to-date data.

**Legend:** 🟢 current & sufficient · 🟡 usable but supplement with newer ·
🔴 stale — must replace before writing.

Audited: 2026-06-01.

---

## Macro / cross-cutting figures

| Figure used in our drafts | Status | Correction / latest |
|---|---|---|
| "Manufacturing ~16% of GDP" (inception reports Ch2) | 🔴 **Stale** | Latest: **15.2% (2024, World Bank)**, down from 16.4% (2022). Update the baseline. [World Bank](https://data.worldbank.org/country/UG) / [TradingEconomics](https://tradingeconomics.com/uganda/manufacturing-value-added-percent-of-gdp-wb-data.html) |
| "30% capacity utilization" | 🟡 Verify | Could not confirm a current figure online; pull from latest **UBOS Statistical Abstract / BoS surveys**. Flag to confirm. |
| NDP IV period & targets | 🟢 Current | NDP IV = **FY2025/26–2029/30**, approved by Parliament **9 Jan 2026**. Theme: "Sustainable Industrialization." GDP target US$158bn by FY29/30. Official full text: [WHO repository PDF](https://extranet.who.int/cpcd/sites/default/files/public_file_repository/UGA_Uganda_Fourth-National-Development-Plan_2025-2029.pdf), [NPA](https://npa.go.ug/national-development-plan/) |
| Tenfold Growth Strategy (US$50bn→US$500bn) | 🟢 Current | Confirmed in NDP IV launch materials. Jerome's `tenfold-growth-strategy.pdf` is fine. |

---

## REPORT 1

### Iron & Steel  🟢 (refresh with 2025 plant news)
- Jerome's **Oct 2025 VC mapping** is current and primary. ✓
- **Add 2025 developments not in older sources:**
  - Tembo Steels: 2nd DRI plant launched **Jan 2025** (~250,000 t); combined ~350,000 t; only primary steel producer. [VoiceUganda](https://voiceuganda.com/2025/09/29/how-tembo-steels-limited-is-shaping-ugandas-steel-industry/), [State House](https://statehouse.go.ug/president-museveni-commissions-new-tembo-steels-plant-in-iganga/)
  - **Devki Group $500m steel plant**, broke ground **Nov 2025**. [The Independent](https://www.independent.co.ug/devki-group-bets-500m-on-uganda-steel-production/), [allAfrica](https://allafrica.com/stories/202511240740.html)
  - Uganda still imports **80–90% of steel demand** (>500,000 t/yr) — key finding.
- Trade: live TradeMap (HS 72/73).

### Copper & Allied Metals  🟢 (was weak — now filled)
- Reserves: **6.5M t ore @ 1.77% Cu** + cobalt — [DGSM official](https://dgsm.go.ug/redevelopment-of-kilembe-mines/). ✓ current
- **March 2025 Sarrai/Nile Fibreboard production-sharing deal** (from 14 bidders). [Mining Weekly](https://www.miningweekly.com/article/uganda-signs-maiden-production-sharing-deal-to-revive-copper-mine-2025-03-04) ✓ current
- Minimal domestic processing = finding. Trade via TradeMap (HS 74).

### Automotive  🔴→🟢 (Jerome's main report was 2017 — now refreshed)
- **`automotive-final-report-apr2017.pdf` is 9 years old — do NOT use for current state.** Use only for history.
- **Latest (must be the basis):** Kiira Motors **vehicle plant commissioned 27 Sept 2025**; capacity **~5,000 vehicles/yr** (22/day phase 1); **3,700 e-bus export deal to West Africa**; first 6 Kayoola EVS delivered to UCAA June 2025; UGX 50bn funding gap FY25/26. [Wikipedia](https://en.wikipedia.org/wiki/Kiira_Motors_Corporation), [AutoMag](https://automag.ug/2025/08/25/kiira-motors-unveils-kayoola-electric-buses-for-public-transport/), [Monitor](https://www.monitor.co.ug/uganda/news/national/kiira-motors-to-roll-out-e-xpress-buses-across-major-cities-by-2026-5273336)
- Jerome's Dec 2025 sector minutes + EAC regs + his TradeMap files = current. ✓

---

## REPORT 2

### Textiles & Garments  🟢
- Jerome's docs (CTA strategy, Lira set 2023, manufacturers list) current. ✓
- Web confirms: **Southern Range Nyanza (Nytil) + Fine Spinners** the two vertically integrated mills; **90% of lint exported** (~US$30m); Fine Spinners ~18,000 jobs. [ChimpReports](https://chimpreports.com/inside-fine-spinners-spinning-ugandas-cotton-to-european-garment-stores/), [UIA](https://www.ugandainvest.go.ug/uia-cdo-team-up-to-boost-import-substitution-in-cotton-sector/)

### Pharmaceuticals  🟢 (register gap now filled)
- **NDA National Drug Register — June 2024** (the manufacturer register we needed). [NDA](https://www.nda.or.ug/wp-content/uploads/2024/06/NATIONAL-DRUG-REGISTER-OF-UGANDA-HUMAN-MEDICINES-JUNE-2024.pdf) ✓
- NDA Pharmacovigilance Report 2023–24. Jerome's NDA reports (FY22/23, FY23/24) current.
- Cipla **QCIL ~1.2bn pills/yr**, FY24/25 revenue UShs 267bn; ~70% essential medicines imported. [QCIL Wikipedia](https://en.wikipedia.org/wiki/Quality_Chemical_Industries_Limited)

### Petrochemicals & Fertilizers  🔴→🟢 (Jerome's phosphates data was **2014** — replaced)
- **`phosphates-value-chain-analysis-jan2014.pdf` is 12 years old — use only for geology, not current state.**
- **Fertilizer — corrected story:** Sukulu/Osukuru plant (Guangzhou Dongsong, commissioned 2018, ~100,000 t/yr design) **shut in 2021, briefly resumed 2023, halted again** — a stalled-plant finding, not a success. [Milling MEA](https://www.millingmea.com/tororo-fertiliser-factory-in-limbo-five-months-after-resuming-operations/), [Osukuru (Wikipedia)](https://en.wikipedia.org/wiki/Osukuru_Industrial_Complex). Uganda imports ~50,000 t but needs ~1M t.
- **Petrochemicals:** Kabaale **60,000 bpd refinery** + **Kabalega Petrochemical Industrial Park**; Alpha MBM agreement **March 2025**, $4bn, start ~2029/30. [UNOC](https://www.unoc.co.ug/midstream/the-uganda-refinery-project/), [PAU](https://www.pau.go.ug/the-uganda-refinery-project/), [Hydrocarbon Engineering Oct 2025](https://www.hydrocarbonengineering.com/refining/13102025/uganda-refinery-to-start-operations-by-early-2030/)

### Sugar & Confectionery  🟢
- Jerome's **USMA 2024 annual report** + **May 2026 brief** are the latest. ✓
- Web confirms ~**822,000 t** output (2022), surplus over ~370k consumption; Kakira ~half of output; Kinyara industrial refinery expanded to 75,000 t (2023); oversupply/over-licensing is the live issue. [Sugar industry (Wikipedia)](https://en.wikipedia.org/wiki/Sugar_industry_in_Uganda), [Monitor](https://www.monitor.co.ug/uganda/news/national/surge-in-sugar-factories-imperils-industry-s-future-3943728)

### Plastics & Packaging  🟢 (firm data now filled, plus fresh 2025 policy)
- **NEMA single-use plastic bag ban push — 2025** (amend National Environment Act); aligns with EAC. Major policy shift for the chapter. [Margherita News Mar 2025](https://margheritanews.ug/2025/03/nema-pushes-for-total-polythene-bags-of-kevera-in-uganda/), [NEMA plastics](https://www.nema.go.ug/en/plastics/)
- **UNBS: 41 certified plastic-bag manufacturers, 67 permits** (Kampala/Wakiso/Jinja/Mukono). Uganda imports ~150,000 t/yr; produces 600 t plastic waste/day.
- NEMA Plastic Circularity Strategy 2023–2028 (Jerome's + web). ✓

### Cement & Building Materials  🔴→🟢 (capacity figure was stale)
- **National installed capacity is no longer 6.8M t (2018).** New plants since:
  - **$300m plant in NE Uganda** (>6,000 t clinker/day) commissioned. [Ecofin](https://www.ecofinagency.com/news-industry/2104-54866-uganda-to-commission-300-million-cement-plant-to-cut-imports-amid-rising-demand)
  - **West International Holding $200m Buikwe plant**, ~4,000 t/day, due **Aug 2025**. [CemNet](https://www.cemnet.com/News/story/181356/uganda-launching-us-300m-cement-plant-to-boost-industry.html)
  - Established: Tororo 3.0M, Hima ~2.0M, Simba 1.0M, Kampala Cement 1.0M. [Wikipedia list](https://en.wikipedia.org/wiki/List_of_cement_manufacturers_in_Uganda), [CemNet country](https://www.cemnet.com/global-cement-report/country/uganda)
  - Uganda still imports >50% of clinker — key finding.
- Hima Dura limestone quarry sufficient to ~2036.

---

## Actions before writing

| # | Action | Chain |
|---|---|---|
| 1 | Update macro baseline: manufacturing **15.2% of GDP (2024)**, not 16% | Inception reports / Ch2 both reports |
| 2 | Confirm current capacity-utilization figure from latest UBOS | Cross-cutting |
| 3 | Treat automotive 2017 report as **history only**; base current state on Kiira 2025 plant | Automotive |
| 4 | Treat phosphates 2014 doc as **geology only**; base fertilizer current state on Sukulu stall + refinery park | Petrochemicals/Fertilizers |
| 5 | Update cement national capacity beyond 2018's 6.8M t with 2024–25 plants | Cement |
| 6 | Fold in 2025 steel plant news (Tembo Jan 2025, Devki Nov 2025) | Iron & Steel |
| 7 | Fold in NEMA 2025 plastic-ban push | Plastics |
| 8 | Pull all trade figures live from TradeMap at write time | All |

**Conclusion:** With these corrections applied, every chapter of both reports
will rest on current (2024–2026) data. The three genuinely stale items Jerome's
pack contained — the **2017 automotive report**, the **2014 phosphates study**,
and the **2018 cement capacity figure** — are now superseded by the sources above.
