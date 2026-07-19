// Petrochemicals & Fertilizers — Value Chain Explorer data
// Source: MTIC Diagnostic Study (Report 2); ITC TradeMap 2024; seed_all_chains.py STRENGTH data

const PRODUCTS = {
  "pc_npk": {
    id: "pc_npk",
    name: "NPK Compound Fertilizer",
    category: "Fertilizers",
    tier: "Phase IV — Blending (Gap / Future)",
    color: "#78350f",
    description: "Multi-nutrient N-P-K compound fertilizer. Uganda's most critical agricultural input gap — imports ~50,000 t/yr vs ~1m t demand; a 950,000 t annual supply gap. All production currently absent. Future: Kabalega petrochemical park (operational ~2029) + Sukulu phosphate plant could enable domestic blending.",
    legend: [
      { color: "#78350f", label: "NPK fertilizer chain" },
      { color: "#92400e", label: "Nutrient components" },
      { color: "#b45309", label: "Intermediates" },
      { color: "#1e3a8a", label: "Feedstocks (imported / future)" },
    ],
    chains: [
      {
        title: "NPK Fertilizer Chain",
        accent: "#78350f",
        nodes: [
          {
            id: "pc_npk_top",
            stage: "Finished Product (Gap)",
            label: "NPK Compound Fertilizer",
            color: "#78350f",
            textColor: "#ffffff",
            inputs: [
              "Ammonium nitrate / urea (N source — imported currently)",
              "Diammonium phosphate / SSP (P source — imported or future Sukulu SSP)",
              "Muriate of potash — MOP (K source — all imported; no potash deposits in Uganda)",
              "Inert filler / conditioning agent (anti-caking)",
              "Energy (blending, granulation and drying)"
            ],
            technology: [
              "Dry blending plant (mixing pre-ground nutrient salts — lowest investment entry)",
              "Granulation drum / pan granulator (agglomeration for slow-release grades)",
              "Dryer and cooler (moisture control for storage stability)",
              "Screening and sizing (target granule size distribution)",
              "Bag packing line (25 / 50 kg net weight)"
            ],
            skills: [
              "Agricultural Chemist — nutrient ratio formulation (N:P:K ratio by crop/soil type)",
              "Process Engineer — granulation moisture control, recycling of fines",
              "Quality Agronomist — dissolution rate, nutrient content (ICP-OES) & soil-test correlation",
              "Packaging Technician — moisture-barrier bag selection, weight control & batch coding",
              "Supply Chain Manager — bulk import logistics (ammonium nitrate ADR compliance)"
            ]
          },
          {
            id: "pc_npk_n",
            stage: "Nitrogen Component (Gap)",
            label: "Nitrogen Nutrient",
            color: "#92400e",
            textColor: "#ffffff",
            dual: true,
            routeA: {
              label: "Urea (Future — Kabalega park ~2029)",
              inputs: [
                "Ammonia (from natural gas reforming or green H2 — future Lake Albert gas)",
                "CO2 (from reforming off-gas — reacted with ammonia for urea synthesis)",
                "Steam (high-pressure — reforming and stripping)",
                "Energy (compressor drives for syngas loop)"
              ],
              technology: [
                "Steam methane reformer (SMR) — syngas from Lake Albert associated gas",
                "CO2 removal unit (amine scrubber — isolates CO2 for urea loop)",
                "Ammonia synthesis loop (Haber-Bosch — high-pressure converter)",
                "Urea reactor (high-pressure carbamate conversion at 200 bar)",
                "Prilling tower or granulation drum (solidification)"
              ],
              skills: [
                "Chemical Process Engineer — SMR catalyst management, syngas H2/CO ratio control",
                "Ammonia Synthesis Specialist — converter temperature, pressure and iron-catalyst management",
                "Urea Process Engineer — carbamate decomposition, recirculation and prilling",
                "Maintenance Engineer — high-pressure valves, heat exchangers and compressor overhaul",
                "Safety Engineer — ammonia leak detection, pressure relief and HAZOP compliance"
              ]
            },
            routeB: {
              label: "Ammonium Nitrate / CAN (Import → Blend)",
              inputs: [
                "Imported ammonia or CAN (calcium ammonium nitrate — sourced from EAC/India)",
                "Imported urea prill (46% N — from Middle East / EAC via Mombasa)",
                "Energy (blending mill power)"
              ],
              technology: [
                "Urea crusher / mill (particle size reduction for blending)",
                "Rotary drum blender (intimate mixing with P and K sources)",
                "Conditioning coater (oil or wax anti-cake treatment)"
              ],
              skills: [
                "Quality Technician — N content assay, moisture measurement & anti-cake testing",
                "Safety Officer — ammonium nitrate handling, storage classification & detonation risk",
                "Blending Operator — batch recipe management and discharge sampling"
              ]
            }
          },
          {
            id: "pc_npk_p",
            stage: "Phosphate Component (Gap)",
            label: "Phosphate Nutrient",
            color: "#b45309",
            textColor: "#ffffff",
            inputs: [
              "Phosphate rock (Sukulu deposit — 100,000 tpa design; plant stalled since 2021)",
              "Sulphuric acid (acidulation agent for SSP — all sulphur imported)",
              "Granulation water / steam (SSP or DAP granulation)"
            ],
            technology: [
              "Phosphate rock crushing and drying (run-of-mine to ground rock)",
              "Single superphosphate (SSP) reactor (sulphuric acid + rock → SSP slurry)",
              "Acidulation den (curing and maturation — 3–4 weeks)",
              "Granulation drum (SSP pelletisation for handling)"
            ],
            skills: [
              "Process Chemist — P2O5 availability, acidulation ratio & free acid control",
              "Mechanical Engineer — den scraper, cutter and belt conveyor maintenance",
              "Safety Engineer — H2SO4 handling, HF gas monitoring and scrubber management"
            ]
          },
          {
            id: "pc_npk_raw",
            stage: "Raw Materials / Feedstocks",
            label: "Key Feedstocks",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Natural gas (Lake Albert)", detail: "Future — HS 2711.21. Lake Albert reserves confirmed; pre-FID. Associated gas could feed ammonia/urea plant. Commercial production expected ~2025–2030." },
              { name: "Phosphate rock (Sukulu)", detail: "Domestic (stalled) — HS 2510.10. Sukulu phosphate plant (100,000 tpa design) stalled since 2021; ore confirmed but processing plant non-operational." },
              { name: "Muriate of potash (MOP)", detail: "Imported — HS 3104.20. No potash deposits in Uganda. All potassium fertilizer imported (Canada, Russia, Belarus). Uganda imports ~USD 8m MOP/yr." },
              { name: "Sulphur / sulphuric acid", detail: "Imported — HS 2503 / 2807. All sulphur imported. No domestic production. Critical for SSP manufacturing from Sukulu phosphate." }
            ]
          }
        ]
      }
    ]
  },

  "pc_urea": {
    id: "pc_urea",
    name: "Urea",
    category: "Fertilizers",
    tier: "Phase III — Production (Gap / Future)",
    color: "#92400e",
    description: "High-analysis nitrogen fertilizer (46% N). Entirely imported into Uganda. Future production possible if Lake Albert associated gas is commercialised and a urea plant is established at Kabalega Industrial Park (target ~2029).",
    legend: [
      { color: "#92400e", label: "Urea production chain" },
      { color: "#1e3a8a", label: "Feedstocks (future / imported)" },
    ],
    chains: [
      {
        title: "Urea Synthesis Chain",
        accent: "#92400e",
        nodes: [
          {
            id: "pc_urea_top",
            stage: "Finished Product (Gap / Future)",
            label: "Urea Prill / Granule",
            color: "#92400e",
            textColor: "#ffffff",
            inputs: [
              "Ammonia (82.5% N — synthesised from syngas via Haber-Bosch)",
              "Carbon dioxide (CO2 — from reformer off-gas; reacted with NH3)",
              "High-pressure steam (200 bar — synthesis and stripping loop)",
              "Cooling water (condenser and absorber cooling)",
              "Formaldehyde (prill hardening additive)"
            ],
            technology: [
              "Urea reactor (high-pressure stripping — 180–200 bar, 180–190°C)",
              "Decomposition / stripping section (carbamate decomposition, NH3 and CO2 recovery)",
              "Vacuum concentration section (evaporation to 99.7% melt)",
              "Prilling tower (melt sprayed upward; air-cooled pellets fall)",
              "Cooler and screening (product sizing and packaging)"
            ],
            skills: [
              "Urea Process Engineer — reactor temperature/pressure control, biuret formation management",
              "Safety Engineer — high-pressure NH3 system HAZOP, relief valve management",
              "Instrument Engineer — pressure transmitter and flow control in high-pressure loop",
              "Quality Chemist — total N, moisture, biuret and granule crush strength per IFA/GOST",
              "Logistics Manager — 50 kg bag packing, bulk loading and storage management (dome silo)"
            ]
          },
          {
            id: "pc_urea_raw",
            stage: "Feedstocks (Future / Imported)",
            label: "Gas & Ammonia Feedstocks",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Natural gas (Lake Albert associated gas)", detail: "Future — HS 2711.21. Lake Albert reserves are the future source. Commercial production pre-FID. Kabalega park planning timeline ~2029." },
              { name: "Urea prill (imported currently)", detail: "Imported — HS 3102.10. All urea currently imported; part of USD 32.1m fertilizer imports. Middle East (Saudi Arabia), Egypt and EAC neighbours supply Uganda." },
              { name: "Ammonia (anhydrous)", detail: "Imported — HS 2814.10. All ammonia for industry currently imported; no domestic production." }
            ]
          }
        ]
      }
    ]
  },

  "pc_pe": {
    id: "pc_pe",
    name: "Polyethylene (PE) Resin",
    category: "Polymer Resins",
    tier: "Phase III — Production (Gap / Future)",
    color: "#b45309",
    description: "HDPE and LDPE polymer resins for film, bottles, pipes and packaging. Entirely imported (100%) — Uganda's plastics conversion sector is strong but entirely dependent on imported resin. Kabalega petrochemical park (~2029) aims to change this.",
    legend: [
      { color: "#b45309", label: "PE resin chain" },
      { color: "#1e3a8a", label: "Feedstocks (future / imported)" },
    ],
    chains: [
      {
        title: "Polyethylene Production Chain",
        accent: "#b45309",
        nodes: [
          {
            id: "pc_pe_top",
            stage: "Finished Product (Gap / Future)",
            label: "PE Resin (HDPE / LDPE / LLDPE)",
            color: "#b45309",
            textColor: "#ffffff",
            inputs: [
              "Ethylene monomer (C2H4 — from steam cracking of naphtha or gas; future Uganda)",
              "Ziegler-Natta or metallocene catalyst (polymerisation initiator)",
              "Hydrogen (molecular weight regulator — controls melt index)",
              "Co-monomers (1-butene, 1-hexene — for LLDPE)",
              "Additives (antioxidant, UV stabiliser, slip agent)"
            ],
            technology: [
              "Gas-phase polymerisation reactor (Unipol process — fluidised bed at 70–100°C)",
              "Or slurry loop reactor (Philips / Ineos process)",
              "Catalyst injection system (Ziegler-Natta or metallocene)",
              "Powder degassing silo (residual monomer removal)",
              "Twin-screw extruder + pelletiser (compounding + additive incorporation)",
              "Pneumatic conveying system (pellet transfer to silo and bagging)"
            ],
            skills: [
              "Polymer Process Engineer — catalyst productivity, melt index and density control",
              "Chemical Engineer — monomer conversion efficiency, heat removal and catalyst deactivation",
              "Polymer Chemist — molecular weight distribution, co-monomer content & branch architecture",
              "Quality Engineer — MFR, density, tensile and ESCR testing per ISO 1133 / ASTM D638",
              "HSE Engineer — static discharge controls, flammable monomer HAZOP, dust explosion prevention"
            ]
          },
          {
            id: "pc_ethylene",
            stage: "Ethylene (Gap / Future)",
            label: "Ethylene Monomer",
            color: "#d97706",
            textColor: "#ffffff",
            inputs: [
              "Naphtha from Kabalega refinery (future — C6–C8 distillate fraction)",
              "Or ethane from Lake Albert associated gas (future option)",
              "High-pressure steam (cracking heat carrier — ~850°C)",
              "Quench water and dilution steam (cracker output cooling)"
            ],
            technology: [
              "Steam cracker furnace (pyrolysis coils — residence time < 0.5 s at 850°C)",
              "Transfer line exchanger (TLE — rapid quench to stop reactions)",
              "Cryogenic separation train (de-ethaniser, splitter — C2 fractionation)",
              "Hydrogen recovery section (PSA or cryogenic)"
            ],
            skills: [
              "Cracker Process Engineer — furnace pass temperature, run length and coking management",
              "Cryogenics Engineer — low-temperature column operation and heat integration",
              "Process Control Engineer — advanced process control for ethylene yield optimisation"
            ]
          },
          {
            id: "pc_pe_raw",
            stage: "Raw Materials (Imported / Future)",
            label: "Feedstocks",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "PE resin (HDPE/LDPE) — imported currently", detail: "Imported — HS 3901.10 / 3901.20. 100% imported; ~150,000 t/yr for Uganda plastics sector. Kabalega park targets domestic supply ~2029." },
              { name: "Crude oil / naphtha (Lake Albert)", detail: "Future — HS 2709 / 2710.12. Lake Albert fields pre-FID. Kabalega refinery required before petrochemical feedstock available." },
              { name: "Natural gas (Lake Albert)", detail: "Future — HS 2711.21. Associated gas is alternative ethane cracker feedstock. Commercialisation timeline 2028–2032." }
            ]
          }
        ]
      }
    ]
  },

  "pc_dap": {
    id: "pc_dap",
    name: "DAP / MAP Phosphate Fertilizer",
    category: "Fertilizers",
    tier: "Phase III–IV — Production (Gap)",
    color: "#d97706",
    description: "Diammonium phosphate (DAP) and monoammonium phosphate (MAP) — key P-N fertilizers for Uganda's agricultural sector. All imported. Future production tied to Sukulu phosphate rock activation and ammonia supply from Lake Albert gas.",
    legend: [
      { color: "#d97706", label: "DAP / phosphate chain" },
      { color: "#1e3a8a", label: "Feedstocks (gap / future)" },
    ],
    chains: [
      {
        title: "DAP Production Chain",
        accent: "#d97706",
        nodes: [
          {
            id: "pc_dap_top",
            stage: "Finished Product (Gap)",
            label: "DAP / MAP Granule",
            color: "#d97706",
            textColor: "#ffffff",
            inputs: [
              "Phosphoric acid (H3PO4 — from sulphuric acid + phosphate rock; Sukulu future)",
              "Anhydrous ammonia (NH3 — neutralisation with phosphoric acid)",
              "Granulation steam / water",
              "Anti-caking oil coating (product treatment)",
              "Sulphur-coated urea (optional blending component)"
            ],
            technology: [
              "Pipe reactor (direct phosphoric acid + ammonia reaction — Jacobs/Norsk-Hydro process)",
              "Preneutraliser tank (partial ammoniation before granulation)",
              "Rotary drum granulator (agglomeration of DAP slurry)",
              "Rotary dryer + cooler (moisture control, final 1–1.5% H2O)",
              "Screening + milling circuit (on-size granule separation)"
            ],
            skills: [
              "Chemical Process Engineer — ammoniation ratio control, pH and temperature optimisation",
              "Safety Engineer — phosphoric acid and ammonia HAZOP; toxic gas release prevention",
              "Quality Chemist — total P2O5, N content, granule size distribution and moisture",
              "Mechanical Engineer — drum granulator and dryer liner maintenance"
            ]
          },
          {
            id: "pc_dap_raw",
            stage: "Feedstocks (Gap / Future)",
            label: "Phosphate & Ammonia",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "DAP / MAP (imported currently)", detail: "Imported — HS 3105.30. All DAP/MAP imported from Saudi Arabia (SABIC), Morocco, Jordan. USD 18m/yr Uganda imports." },
              { name: "Phosphate rock (Sukulu)", detail: "Domestic (stalled) — HS 2510.10. Sukulu phosphate deposit could supply SSP/DAP plant. Plant stalled since 2021 — investor/financing needed." },
              { name: "Sulphuric acid", detail: "Imported — HS 2807. All H2SO4 imported. Required to convert phosphate rock to phosphoric acid. USD 1.3m imports/yr." }
            ]
          }
        ]
      }
    ]
  }
};

const CATEGORIES = [
  { name: "Fertilizers", color: "#78350f", products: ["pc_npk", "pc_urea", "pc_dap"] },
  { name: "Polymer Resins", color: "#b45309", products: ["pc_pe"] }
];

const TRADE_HS4 = {
  "3102": {
    desc: "HS 3102 — mineral or chemical fertilizers, nitrogenous (incl. urea). All imported.",
    year: 2024, imports: { uganda: 18400.0, eac: 2200.0 }, exports: { uganda: 200.0, eac: 150.0 }
  },
  "3105": {
    desc: "HS 3105 — mineral or chemical fertilizers N+P+K (incl. DAP, NPK). All imported.",
    year: 2024, imports: { uganda: 13700.0, eac: 1800.0 }, exports: { uganda: 100.0, eac: 80.0 }
  },
  "3901": {
    desc: "HS 3901 — polymers of ethylene (HDPE, LDPE, LLDPE). 100% imported.",
    year: 2024, imports: { uganda: 38000.0, eac: 1200.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "3104": {
    desc: "HS 3104 — mineral or chemical fertilizers, potassic (MOP). All imported.",
    year: 2024, imports: { uganda: 8000.0, eac: 600.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "2709": {
    desc: "HS 2709 — crude petroleum oils. Lake Albert future feedstock.",
    year: 2024, imports: { uganda: 0.0, eac: 0.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const PRODUCT_HS4 = {
  "pc_npk":  "3105",
  "pc_urea": "3102",
  "pc_pe":   "3901",
  "pc_dap":  "3105"
};

const RAW_MATERIAL_TRADE = {
  "Muriate of potash (MOP)": {
    desc: "HS 3104.20 — potassium chloride. All potash imported from Canada/Russia/EAC.",
    year: 2024, imports: { uganda: 8000.0, eac: 600.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Sulphur / sulphuric acid": {
    desc: "HS 2807 — sulphuric acid. All imported; needed for phosphate processing.",
    year: 2024, imports: { uganda: 1306.0, eac: 1219.0 }, exports: { uganda: 5.0, eac: 5.0 }
  },
  "PE resin (HDPE/LDPE) — imported currently": {
    desc: "HS 3901 — polyethylene primary forms. 100% imported; ~150,000 t/yr.",
    year: 2024, imports: { uganda: 38000.0, eac: 1200.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "DAP / MAP (imported currently)": {
    desc: "HS 3105.30 — diammonium phosphate. Imported from Saudi Arabia, Morocco, Jordan.",
    year: 2024, imports: { uganda: 13700.0, eac: 1800.0 }, exports: { uganda: 100.0, eac: 80.0 }
  }
};

const RAW_MATERIAL_PHASE = {};

const PHASE_PRODUCERS = {
  "pc_IV": {
    count: 0,
    label: "Phase IV — Fertilizer blending (absent; only import distribution active)",
    examples: [
      "No domestic fertilizer producer; all blending plants absent",
      "Distribution: Yara Uganda, Balton CP, Greenfields (all import traders)"
    ]
  }
};

const PHASE_SOURCE = "MTIC Diagnostic Study on Petrochemicals & Fertilizers (Report 2, 2026)";

const PRODUCT_FIRMS = {
  "pc_npk": {
    status: "absent",
    firms: [],
    note: "No NPK production in Uganda. 950,000 t annual supply gap. Future: Kabalega park + Sukulu phosphate. USD 32.1m fertilizer imports (2024). 2040 target: 1.5–2m tonnes domestic demand; Kabalega operational."
  },
  "pc_urea": {
    status: "absent",
    firms: [],
    note: "All urea imported. Future production requires Lake Albert gas commercialisation and urea plant at Kabalega (~2029). Currently part of USD 18.4m nitrogenous fertilizer imports."
  },
  "pc_pe": {
    status: "absent",
    firms: [],
    note: "All PE resin (HDPE/LDPE/LLDPE) imported. ~150,000 t/yr. Kabalega petrochemical park targets domestic resin production ~2029. 2040 target: Kabalega operational supplying domestic plastics converters."
  },
  "pc_dap": {
    status: "absent",
    firms: [],
    note: "All DAP/MAP imported. Sukulu phosphate plant stalled — revival + H2SO4 supply needed. Until then, ~USD 13.7m DAP/MAP imports continue."
  }
};

const INPUT_KEYWORD_HS4 = [
  { pattern: /\burea\b/i, hs4: "3102" },
  { pattern: /\bDAP\b|\bdiammonium phosphate\b/i, hs4: "3105" },
  { pattern: /\bNPK\b|\bcompound fertilizer\b/i, hs4: "3105" },
  { pattern: /\bPE resin\b|\bpolyethylene.*resin\b/i, hs4: "3901" },
  { pattern: /\bsulphuric acid\b|\bH2SO4\b/i, hs4: "2807" },
  { pattern: /\bpotash\b|\bMOP\b|\bmuriate of potash\b/i, hs4: "3104" },
];

const INPUT_KEYWORD_PHASE = [];

function matchInputTrade(text) {
  const hit = INPUT_KEYWORD_HS4.find(k => k.pattern.test(text));
  return hit ? TRADE_HS4[hit.hs4] : null;
}

function matchInputPhase(text) {
  const hit = INPUT_KEYWORD_PHASE.find(k => k.pattern.test(text));
  return hit ? PHASE_PRODUCERS[hit.phase] : null;
}

export { PRODUCTS, CATEGORIES, TRADE_HS4, PRODUCT_HS4, RAW_MATERIAL_TRADE, matchInputTrade, matchInputPhase, PRODUCT_FIRMS, PHASE_PRODUCERS, PHASE_SOURCE, RAW_MATERIAL_PHASE };
