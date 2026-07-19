// Cement & Building Materials — Value Chain Explorer data
// Source: MTIC Diagnostic Study (Report 2); ITC TradeMap 2024; seed_all_chains.py STRENGTH data

const PRODUCTS = {
  "cm_opc": {
    id: "cm_opc",
    name: "Ordinary Portland Cement (OPC)",
    category: "Cement",
    tier: "Phase III — Cement Grinding (Strong)",
    color: "#1c1917",
    description: "General-purpose Portland cement (CEM I, 42.5R and 52.5). Uganda grinds and exports OPC — 7 Mtpa installed grinding capacity at Tororo (3 Mtpa), Hima (2 Mtpa), Simba (1 Mtpa), Kampala (1 Mtpa). KEY GAP: Clinker >50% imported (USD 162.2m, 2024). Two new plants (USD 500m) under construction.",
    legend: [
      { color: "#1c1917", label: "Cement grinding chain" },
      { color: "#292524", label: "Clinker production" },
      { color: "#44403c", label: "Quarrying & raw meal" },
      { color: "#57534e", label: "Limestone" },
    ],
    chains: [
      {
        title: "Portland Cement Chain",
        accent: "#1c1917",
        nodes: [
          {
            id: "cm_opc_top",
            stage: "Finished Product",
            label: "OPC Cement",
            color: "#1c1917",
            textColor: "#ffffff",
            inputs: [
              "Portland cement clinker (domestic from Tororo/Hima kilns OR imported — >50% of Uganda need imported)",
              "Gypsum (set retarder — 4–6% addition; partly domestic, partly imported)",
              "Limestone filler (optional — minor addition for CEM I/A-L grades)",
              "Grinding media (steel balls — 60–90mm forged or cast; domestic or imported)",
              "Energy (electric motor drives for ball mill — 35–45 kWh/tonne cement)"
            ],
            technology: [
              "Ball mill (open circuit or closed circuit with separator — most common in Uganda)",
              "Vertical roller mill (VRM — energy-saving alternative; used at newer plants)",
              "High-efficiency separator (O-Sepa, QDK — classifies fine cement from coarse returns)",
              "Cement storage silos (flat-bottom with aeration discharge)",
              "Bulk loading spout and bagging plant (50 kg and 25 kg bags)"
            ],
            skills: [
              "Cement Process Engineer — Blaine fineness control (3,200–4,200 cm2/g), mill throughput and separator cut",
              "Quality Control Chemist — LSF, SM, AM (moduli) control; 28-day strength compliance (EN 197-1)",
              "Energy Manager — mill kWh/t cement, peak-load management and fan energy optimisation",
              "Mechanical Engineer — ball charge audit, mill liner management and fan bearing maintenance",
              "Bagging Plant Operator — fill weight accuracy (50 ± 0.5 kg), bag integrity and dust control"
            ]
          },
          {
            id: "cm_clinker_make",
            stage: "Clinker Production",
            label: "Cement Clinker",
            color: "#292524",
            textColor: "#ffffff",
            dual: true,
            routeA: {
              label: "Dry Process Kiln (Uganda Kilns — Tororo, Hima)",
              inputs: [
                "Raw meal (ground limestone + clay/shale — blended and ground to < 90 µm)",
                "Kiln fuel — coal (largely imported; alt-fuel opportunity for biomass and waste)",
                "Secondary air (from clinker cooler — energy recovery)",
                "Pre-calciner fuel (60–65% of total thermal energy)",
                "Corrective materials (bauxite, silica sand, iron ore — chemistry trim)"
              ],
              technology: [
                "Multi-stage cyclone preheater (4 or 5 stages — raw meal preheat)",
                "Pre-calciner (flash calciner — 90% calcination before kiln)",
                "Rotary kiln (60 m × 4 m — 1,450°C clinkering zone)",
                "Clinker cooler (grate cooler — rapid quench for free-lime control)",
                "Online X-ray analyser (raw meal chemistry — real-time feed correction)"
              ],
              skills: [
                "Kiln Operator — burning zone temperature, flame shape and free-lime target",
                "Process Engineer — preheater draught, ring formation prevention and kiln shell management",
                "Chemical Engineer — raw mix moduli (C3S, C3A targets), corrective additions optimisation",
                "Refractory Engineer — kiln lining inspection and high-alumina brick replacement campaign",
                "Fuel Engineer — coal calorific value, fineness (< 12% residue at 90 µm) and stoichiometry"
              ]
            },
            routeB: {
              label: "Clinker Import (>50% of Uganda demand currently)",
              inputs: [
                "Imported clinker (bulk shipment via Mombasa then rail/road — China, India, UAE)",
                "Port handling and logistics (Mombasa port, SGR rail, truck to plant)",
                "Storage dome / shed (bulk clinker storage at grinding plant)"
              ],
              technology: [
                "Pneumatic ship unloading (for Mombasa port receipt)",
                "Belt conveyor and bucket elevator (clinker to storage dome)",
                "Reclaimer (bulk storage withdrawal to grinding mill)"
              ],
              skills: [
                "Procurement Specialist — clinker quality spec (C3S, Fe2O3, SO3, LOI per EN 197-1)",
                "Logistics Manager — shipping schedule, demurrage, rail/road capacity and lead time management",
                "Quality Analyst — incoming clinker assay, grinding suitability and free-lime check"
              ]
            }
          },
          {
            id: "cm_raw_meal",
            stage: "Raw Meal & Quarrying",
            label: "Raw Meal",
            color: "#44403c",
            textColor: "#ffffff",
            inputs: [
              "Limestone (primary calcium source — quarried at Tororo, Dura/Kamwenge, Karamoja)",
              "Clay / shale (silica-alumina source — quarried alongside limestone)",
              "Corrective materials (bauxite for Al correction; iron ore for Fe — partly imported)",
              "Grinding water (wet process — very limited use in Uganda; mostly dry process)"
            ],
            technology: [
              "Limestone jaw crusher (primary — 1 m → 80 mm)",
              "Secondary / tertiary crusher (cone or impact — 80 → 25 mm)",
              "Raw mill (ball mill or VRM — limestone + clay to < 90 µm powder)",
              "X-ray fluorescence (XRF) analyser (raw meal chemistry — CaO, SiO2, Al2O3, Fe2O3)",
              "Blending silo (continuous blending — mix homogeneity ≤ 1% CaCO3 std. dev.)"
            ],
            skills: [
              "Quarry Engineer — blast design, fragmentation and primary crusher feed management",
              "Raw Mill Process Engineer — grinding efficiency, circulating load and classifier cut",
              "Geologist — limestone deposit quality assessment (CaO > 50%, MgO < 3%)",
              "Process Control Engineer — XRF-to-mill feedback loop for LSF/SM/AM targets",
              "Maintenance Engineer — crusher wear part (jaw plates, liners) and conveyor belt management"
            ]
          },
          {
            id: "cm_limestone",
            stage: "Raw Materials",
            label: "Limestone & Quarry Inputs",
            color: "#57534e",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Limestone (quarried)", detail: "Domestic — HS 2521. Established deposits at Tororo, Dura (Kamwenge), Hima (Kasese), Karamoja. Strong domestic supply for all Uganda cement plants." },
              { name: "Coal (kiln fuel)", detail: "Largely imported — HS 2701. Uganda imports coal from Tanzania (EAC). Alt-fuel (biomass, waste) opportunity to reduce import dependence." },
              { name: "Gypsum", detail: "Partly domestic — HS 2520. Some deposits in Uganda; partly imported from Kenya/Tanzania for pharma-grade and top-quality cement." },
              { name: "Clinker (imported)", detail: "Imported — HS 2523.10. >50% of Uganda clinker demand is imported (USD 162.2m, 2024). Two new plants (USD 500m) under construction to close gap by 2028–2030." }
            ]
          }
        ]
      }
    ]
  },

  "cm_ppc": {
    id: "cm_ppc",
    name: "Pozzolana / Blended Cement (PPC)",
    category: "Cement",
    tier: "Phase III — Cement Grinding (Strong)",
    color: "#292524",
    description: "Portland pozzolana cement (CEM II/B-P or CEM IV) — lower-carbon blended cement using pozzolana or fly ash. Strong in Uganda due to natural pozzolana availability. Lower clinker factor (55–70%) reduces import dependence and CO2.",
    legend: [
      { color: "#292524", label: "Blended cement chain" },
      { color: "#1c1917", label: "Clinker + pozzolana" },
    ],
    chains: [
      {
        title: "Pozzolana Cement Chain",
        accent: "#292524",
        nodes: [
          {
            id: "cm_ppc_top",
            stage: "Finished Product",
            label: "PPC Blended Cement",
            color: "#292524",
            textColor: "#ffffff",
            inputs: [
              "Portland cement clinker (55–70% — domestic or imported)",
              "Natural pozzolana (volcanic ash — domestic; 25–35% addition)",
              "Gypsum (4–6% — set retarder)",
              "Limestone (0–5% filler — optional CEM II/A-L)",
              "Energy (electric grinding — slightly lower kWh/t than pure OPC)"
            ],
            technology: [
              "Ball mill or VRM (co-grinding or separate grinding of pozzolana)",
              "Separate pozzolana dryer + mill (reduces feed moisture for efficient grinding)",
              "High-efficiency separator (fines classification)",
              "Blending weigh feeder (accurate clinker/pozzolana/gypsum proportioning)"
            ],
            skills: [
              "Cement Chemist — pozzolanic activity index (PAI per EN 450), water demand and setting time",
              "Process Engineer — separate pozzolana grinding for optimum blend performance",
              "Quality Engineer — 28-day and 56-day strength, expansion and fineness per EN 197-1",
              "Sustainability Officer — CO2 footprint calculation and carbon reduction certification"
            ]
          },
          {
            id: "cm_ppc_raw",
            stage: "Materials",
            label: "Clinker, Pozzolana & Gypsum",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Portland cement clinker", detail: "Domestic + imported — HS 2523.10. >50% imported (USD 162.2m); Uganda kilns supply balance. Two new plants under construction." },
              { name: "Natural pozzolana / volcanic ash", detail: "Partly domestic — HS 2621.90. Some pozzolana available from volcanic areas. Slag from Steel sector limited but growing." },
              { name: "Gypsum (set retarder)", detail: "Partly domestic — HS 2520.10. Small domestic gypsum deposits; partly imported." }
            ]
          }
        ]
      }
    ]
  },

  "cm_blocks": {
    id: "cm_blocks",
    name: "Concrete Blocks & Bricks",
    category: "Building Materials",
    tier: "Phase IV — Products (Emerging)",
    color: "#44403c",
    description: "Hollow and solid concrete masonry units for walling. Growing domestic production — increasingly mechanised block-making plants in Kampala, Jinja, Mbarara. Market expanding with Uganda's rapid urbanisation and housing demand.",
    legend: [
      { color: "#44403c", label: "Concrete block chain" },
      { color: "#57534e", label: "Cement + aggregate" },
    ],
    chains: [
      {
        title: "Concrete Block Production Chain",
        accent: "#44403c",
        nodes: [
          {
            id: "cm_block_top",
            stage: "Finished Product",
            label: "Concrete Block",
            color: "#44403c",
            textColor: "#ffffff",
            inputs: [
              "OPC cement (domestic — Tororo, Hima, Simba or Kampala brands)",
              "Sand (river or quarried — domestic; abundant in Uganda)",
              "Crushed aggregate (domestic quarries — graded 10–14mm)",
              "Water (potable — municipality or borehole)",
              "Admixtures (optional — water reducer, air-entraining agent)"
            ],
            technology: [
              "Pan mixer / drum mixer (aggregate + cement + water batch mixing)",
              "Hydraulic block press (vibro-compaction; semi or fully automatic)",
              "Curing yard (shade covered — 7–14 days moist curing or steam curing)",
              "Block testing press (compressive strength per EN 771-3 / UNBS)",
              "Fork lift / pallet handler (block storage and despatch)"
            ],
            skills: [
              "Concrete Technologist — mix design, water/cement ratio and target strength (2.5–10 MPa depending on grade)",
              "Block Mould Technician — mould plate maintenance, vibration frequency and compaction cycle",
              "QC Inspector — block dimension, density, absorption and crushing strength per UNBS EAS 36",
              "Site Manager — production scheduling, curing management and logistics to construction sites",
              "Sales / Technical Representative — spec promotion to architects, quantity surveyors and contractors"
            ]
          },
          {
            id: "cm_block_raw",
            stage: "Materials",
            label: "Cement, Aggregate & Water",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "OPC / PPC cement", detail: "Domestic — HS 2523.29. Abundant domestic supply. Uganda net cement exporter. Tororo, Hima, Simba and Kampala brands cover the country." },
              { name: "River sand", detail: "Domestic — HS 2505. Abundant in Uganda. Environmental regulation increasing for river sand dredging; quarry dust becoming alternative." },
              { name: "Crushed stone aggregate", detail: "Domestic — HS 2517. Extensive quarry operations across Uganda. Abundant domestic supply." }
            ]
          }
        ]
      }
    ]
  },

  "cm_rmc": {
    id: "cm_rmc",
    name: "Ready-Mix Concrete",
    category: "Building Materials",
    tier: "Phase IV — Products (Emerging)",
    color: "#57534e",
    description: "Site-delivered fresh concrete. Growing segment in Kampala and major towns — driven by high-rise construction and infrastructure projects. Served by few operators currently; large market for standardised RMC vs. site-mixed concrete.",
    legend: [
      { color: "#57534e", label: "Ready-mix concrete chain" },
      { color: "#44403c", label: "Batching inputs" },
    ],
    chains: [
      {
        title: "Ready-Mix Concrete Chain",
        accent: "#57534e",
        nodes: [
          {
            id: "cm_rmc_top",
            stage: "Finished Product",
            label: "Ready-Mix Concrete",
            color: "#57534e",
            textColor: "#ffffff",
            inputs: [
              "OPC / PPC cement (domestic brands)",
              "Coarse aggregate (20mm and 10mm — domestic quarried crushed stone)",
              "Fine aggregate (sand — river sand or quarry dust)",
              "Water (potable — batch plant metered)",
              "Chemical admixtures (superplasticiser, retarder — imported; e.g. BASF MasterGlenium)"
            ],
            technology: [
              "Dry batch or wet batch plant (weighing hoppers, conveyor, mixer)",
              "Horizontal drum or twin-shaft mixer (thorough homogenisation in 60–90 s)",
              "Transit mixer truck (drum truck — 6 m3 to 8 m3 capacity; drum rotates on transit)",
              "Slump cone and temperature test kit (quality check at plant and on-site)",
              "Admixture dosing pump (accurate ml-level dosing to batch)"
            ],
            skills: [
              "Concrete Mix Designer — mix design for target strength/slump/durability per EN 206 / ACI 318",
              "Batch Plant Operator — aggregate moisture correction, admixture dosing and batch accuracy (± 1% cement, ± 3% aggregate)",
              "Transit Mixer Driver — charge volume, mixing revolutions, delivery window (< 90 min to discharge)",
              "QC Technician — slump, air content and cube sampling per UNBS EAS 41",
              "Technical Sales Engineer — structural spec assistance to civil engineers and contractors"
            ]
          },
          {
            id: "cm_rmc_raw",
            stage: "Materials",
            label: "Cement, Aggregates & Admixtures",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "OPC cement (bagged or bulk)", detail: "Domestic — HS 2523.29. Uganda has abundant cement supply. Bulk delivery to RMC batch plants from Tororo, Hima, Simba." },
              { name: "Crushed stone aggregate (20mm, 10mm)", detail: "Domestic — HS 2517.10. Abundant quarry operations around Kampala (Kasubi, Buloba, Mbalala quarries)." },
              { name: "Superplasticiser admixture", detail: "Imported — HS 3824.90. PCE-based superplasticisers imported (BASF, Sika, CHRYSO). Small volumes but critical for high-performance grades." }
            ]
          }
        ]
      }
    ]
  },

  "cm_tiles": {
    id: "cm_tiles",
    name: "Ceramic Tiles",
    category: "Finishing Materials",
    tier: "Phase IV — Products (Gap / Opportunity)",
    color: "#6b7280",
    description: "Ceramic floor and wall tiles. All imported — USD 40m+/yr into Uganda. Major market opportunity: Uganda has the clay, feldspar and kaolin deposits for tile manufacturing. No domestic ceramic tile plant currently.",
    legend: [
      { color: "#6b7280", label: "Ceramic tile chain (gap)" },
      { color: "#1e3a8a", label: "Raw materials (available domestically)" },
    ],
    chains: [
      {
        title: "Ceramic Tile Production Chain",
        accent: "#6b7280",
        nodes: [
          {
            id: "cm_tile_top",
            stage: "Finished Product (Gap)",
            label: "Ceramic Floor / Wall Tile",
            color: "#6b7280",
            textColor: "#ffffff",
            inputs: [
              "Ceramic body clay (Uganda deposits available — kaolinite, ball clay blend)",
              "Feldspar (fluxing agent — reduces sintering temperature; local deposits exist)",
              "Silica sand (skeleton material — local deposits abundant)",
              "Glaze materials (frit, colourants, opacifiers — specialist imports)",
              "Energy (kiln fuel — gas or electricity; major cost item)"
            ],
            technology: [
              "Raw material preparation (jaw crusher + ball mill — ceramic body slurry)",
              "Spray dryer (slurry → granulate — controlled moisture for pressing)",
              "Hydraulic press (semi-dry pressing — 25–50 MPa; tile formation)",
              "Dryer (removal of pressing moisture — pre-kiln)",
              "Glaze line (single or multiple glaze layers — digital inkjet decoration is modern standard)",
              "Roller kiln (1,100–1,200°C — 60–120 min cycle)"
            ],
            skills: [
              "Ceramics Technologist — body composition, firing curve and shrinkage control",
              "Glaze Chemist — frit composition, thermal expansion matching and glaze defect prevention",
              "Kiln Engineer — temperature profile, roller speed and atmosphere control",
              "Digital Print Technician — inkjet printer parameter setting for texture and colour accuracy",
              "Quality Engineer — tile dimensions, water absorption, breaking strength per ISO 13006"
            ]
          },
          {
            id: "cm_tile_raw",
            stage: "Raw Materials (Partly Available Domestically)",
            label: "Clay, Feldspar & Kiln Energy",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Ceramic body clay (kaolin, ball clay)", detail: "Domestic (untapped) — HS 2508. Uganda has clay deposits suitable for ceramic body. No commercial ceramic-grade clay mining yet." },
              { name: "Feldspar", detail: "Partly domestic — HS 2529. Feldspar deposits in Uganda; no commercial mining for ceramics currently." },
              { name: "Silica sand", detail: "Domestic — HS 2505. Abundant silica sand deposits; quarrying active for other uses." },
              { name: "Ceramic tiles (imported currently)", detail: "Imported — HS 6907.21. USD 40m+/yr floor and wall tile imports from China, India, Italy, Egypt. No domestic producer." }
            ]
          }
        ]
      }
    ]
  }
};

const CATEGORIES = [
  { name: "Cement", color: "#1c1917", products: ["cm_opc", "cm_ppc"] },
  { name: "Building Materials", color: "#44403c", products: ["cm_blocks", "cm_rmc"] },
  { name: "Finishing Materials", color: "#6b7280", products: ["cm_tiles"] }
];

const TRADE_HS4 = {
  "2523": {
    desc: "HS 2523 — Portland cement, aluminous cement and similar hydraulic cements (incl. clinker).",
    year: 2024, imports: { uganda: 162200.0, eac: 42000.0 }, exports: { uganda: 48000.0, eac: 44000.0 }
  },
  "2521": {
    desc: "HS 2521 — limestone flux (quicklime / unburnt limestone). Domestic quarrying active.",
    year: 2024, imports: { uganda: 165.0, eac: 165.0 }, exports: { uganda: 12.0, eac: 12.0 }
  },
  "6810": {
    desc: "HS 6810 — articles of cement, concrete or artificial stone (blocks, pavers, pipes).",
    year: 2024, imports: { uganda: 4200.0, eac: 800.0 }, exports: { uganda: 6800.0, eac: 6200.0 }
  },
  "6907": {
    desc: "HS 6907 — ceramic flags and paving, hearth or wall tiles (unglazed).",
    year: 2024, imports: { uganda: 42000.0, eac: 4200.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "7005": {
    desc: "HS 7005 — float glass and surface-ground / polished glass.",
    year: 2024, imports: { uganda: 18000.0, eac: 2400.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "2701": {
    desc: "HS 2701 — coal and similar solid fuels (used as kiln fuel). Uganda imports from Tanzania.",
    year: 2024, imports: { uganda: 9639.0, eac: 8295.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const PRODUCT_HS4 = {
  "cm_opc":    "2523",
  "cm_ppc":    "2523",
  "cm_blocks": "6810",
  "cm_rmc":    "3824",
  "cm_tiles":  "6907"
};

const RAW_MATERIAL_TRADE = {
  "Limestone (quarried)": {
    desc: "HS 2521 — limestone flux. Domestic quarrying at Tororo, Dura, Hima, Karamoja. Minimal imports.",
    year: 2024, imports: { uganda: 165.0, eac: 165.0 }, exports: { uganda: 12.0, eac: 12.0 }
  },
  "Coal (kiln fuel)": {
    desc: "HS 2701 — coal. Used as kiln fuel. Uganda imports primarily from Tanzania (EAC). USD 9.6m/yr.",
    year: 2024, imports: { uganda: 9639.0, eac: 8295.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Clinker (imported)": {
    desc: "HS 2523.10 — cement clinker. >50% of Uganda clinker demand imported. USD 162.2m/yr (2024).",
    year: 2024, imports: { uganda: 162200.0, eac: 42000.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Ceramic tiles (imported currently)": {
    desc: "HS 6907 — ceramic floor and wall tiles. USD 42m/yr imports. No domestic producer.",
    year: 2024, imports: { uganda: 42000.0, eac: 4200.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const RAW_MATERIAL_PHASE = {
  "Limestone (quarried)": "cm_I"
};

const PHASE_PRODUCERS = {
  "cm_I": {
    count: 4,
    label: "Phase I — Limestone Quarrying (strong)",
    examples: [
      "Hima Cement Ltd quarry (Kasese — near Hima plant)",
      "Tororo Cement quarry (Tororo district)",
      "Simba Cement quarry (Dura, Kamwenge)",
      "Kampala Cement Co. quarry"
    ]
  },
  "cm_II": {
    count: 2,
    label: "Phase II — Clinker Production (emerging — >50% imported)",
    examples: [
      "Tororo Cement Ltd (rotary kiln — Tororo)",
      "Hima Cement Ltd (rotary kiln — Kasese)",
      "Sinoma/Siam City new plant (USD 350m — under construction 2025)",
      "Second new plant (USD 150m — under construction)"
    ]
  },
  "cm_III": {
    count: 4,
    label: "Phase III — Cement Grinding (strong — 7 Mtpa installed)",
    examples: [
      "Tororo Cement Ltd (3 Mtpa)",
      "Hima Cement Ltd (2 Mtpa)",
      "Simba Cement (1 Mtpa)",
      "Kampala Cement Co. (1 Mtpa)"
    ]
  }
};

const PHASE_SOURCE = "MTIC Diagnostic Study on Cement & Building Materials (Report 2, 2026)";

const PRODUCT_FIRMS = {
  "cm_opc": {
    status: "named",
    firms: [
      "Tororo Cement Ltd (3 Mtpa)",
      "Hima Cement Ltd / LafargeHolcim (2 Mtpa)",
      "Simba Cement (1 Mtpa)",
      "Kampala Cement Co. (1 Mtpa)"
    ],
    note: "KEY GAP: Clinker >50% imported — USD 162.2m (2024). Two new plants (USD 500m) under construction. 2040 target: >90% clinker self-sufficiency; Uganda as dominant regional cement supplier."
  },
  "cm_ppc": {
    status: "named",
    firms: ["Tororo Cement (PPC brand)", "Hima Cement (Rhino PPC)", "Simba Cement", "Kampala Cement"],
    note: "PPC / blended cement strong — lower clinker factor reduces import dependence. Uganda net cement exporter (USD 48m, 2024)."
  },
  "cm_blocks": {
    status: "emerging",
    firms: ["Numerous small and medium block producers in Kampala, Jinja, Mbarara (MTIC register)"],
    note: "Block making growing rapidly with urbanisation. Increasingly mechanised. Most producers serve local construction market."
  },
  "cm_rmc": {
    status: "emerging",
    firms: ["Few operators (Athi River Cement RMC, others) — market under-served relative to construction volume"],
    note: "Ready-mix concrete mostly imported practice — most construction in Uganda still uses site-mixed concrete. RMC market growing for high-rise and infrastructure."
  },
  "cm_tiles": {
    status: "absent",
    firms: [],
    note: "Ceramic tiles entirely imported — USD 42m/yr (HS 6907, 2024). Uganda has the raw materials (clay, feldspar, silica) but no domestic ceramic tile plant. Significant market opportunity."
  }
};

const INPUT_KEYWORD_HS4 = [
  { pattern: /\bclinker\b/i, hs4: "2523" },
  { pattern: /\blimestone\b/i, hs4: "2521" },
  { pattern: /\bcoal.*kiln\b|\bkiln.*fuel\b/i, hs4: "2701" },
  { pattern: /\bceramic tiles?\b/i, hs4: "6907" },
  { pattern: /\bflat glass\b|\bfloat glass\b/i, hs4: "7005" },
];

const INPUT_KEYWORD_PHASE = [
  { pattern: /\bTororo\b|\bHima\b|\bSimba Cement\b|\bKampala Cement\b/i, phase: "cm_III" },
  { pattern: /\blimestone.*quarr\b|\bquarr.*limestone\b/i, phase: "cm_I" },
];

function matchInputTrade(text) {
  const hit = INPUT_KEYWORD_HS4.find(k => k.pattern.test(text));
  return hit ? TRADE_HS4[hit.hs4] : null;
}

function matchInputPhase(text) {
  const hit = INPUT_KEYWORD_PHASE.find(k => k.pattern.test(text));
  return hit ? PHASE_PRODUCERS[hit.phase] : null;
}

export { PRODUCTS, CATEGORIES, TRADE_HS4, PRODUCT_HS4, RAW_MATERIAL_TRADE, matchInputTrade, matchInputPhase, PRODUCT_FIRMS, PHASE_PRODUCERS, PHASE_SOURCE, RAW_MATERIAL_PHASE };
