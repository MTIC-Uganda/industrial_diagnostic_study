// Sugar & Confectionery — Value Chain Explorer data
// Source: MTIC Diagnostic Study (Report 2); ITC TradeMap 2024; seed_all_chains.py STRENGTH data

const PRODUCTS = {
  "sg_white": {
    id: "sg_white",
    name: "Refined White Sugar",
    category: "Sugar",
    tier: "Phase III — Refining",
    color: "#713f12",
    description: "Industrial refined white sugar (sulfitation or carbonatation process). Uganda produces ~822,000 t/yr raw/mill-white sugar — Kakira ~50% of national output. KEY GAP: Industrial refining (Phase III) under-exploited; USD 38.1m still imported despite Uganda's structural surplus. 2040 target: downstream-dominated chain.",
    legend: [
      { color: "#713f12", label: "Sugar refining chain" },
      { color: "#854d0e", label: "Milling & extraction" },
      { color: "#a16207", label: "Cane growing" },
    ],
    chains: [
      {
        title: "Sugar Refining Chain",
        accent: "#713f12",
        nodes: [
          {
            id: "sg_white_top",
            stage: "Finished Product",
            label: "Refined White Sugar",
            color: "#713f12",
            textColor: "#ffffff",
            inputs: [
              "Raw / mill-white sugar (Uganda domestic — from Kakira, Kinyara, SCOUL, Mayuge mills)",
              "Phosphoric acid (juice clarification — acidification flocculation)",
              "Lime (calcium hydroxide — clarification pH adjustment)",
              "Sulphur dioxide (SO2 — sulfitation bleaching) or CO2 (carbonatation route)",
              "Activated carbon / bone char (decolourisation filter bed)",
              "Energy (steam from bagasse boilers — abundant by-product)"
            ],
            technology: [
              "Affination mixer (raw sugar + heavy syrup — removes molasses film)",
              "Clarifier / flotation tank (phosphatation or carbonatation — colour bodies removed)",
              "Decolourisation columns (GAC or bone char beds)",
              "Multiple-effect evaporators (concentration to massecuite)",
              "Vacuum pan (batch crystallisation of white sugar crystals)",
              "Centrifuge battery (white sugar crystal/liquor separation)"
            ],
            skills: [
              "Sugar Technologist — massecuite consistency, boiling time and crystal size control",
              "Chemical Engineer — juice clarification, decolourisation efficiency and sulphitation SO2 concentration",
              "Process Engineer — multi-effect evaporator energy balance and steam economy",
              "Quality Chemist — ICUMSA colour, pol (sucrose %), moisture and ash per CODEX standard",
              "Energy Engineer — bagasse combustion efficiency, co-generation optimisation"
            ]
          },
          {
            id: "sg_milling",
            stage: "Milling",
            label: "Raw Sugar & Juice Extraction",
            color: "#854d0e",
            textColor: "#ffffff",
            inputs: [
              "Sugarcane (12–17% sucrose content — freshly harvested to minimise dextran formation)",
              "Imbibition water (hot water — multiple juice dilution stages for maximum extraction)",
              "Lime (quick lime — pH adjustment for juice preservation)",
              "Sulphur dioxide (SO2 — juice preservation and clarification)",
              "Energy (bagasse — self-sufficient fuel for all Uganda mills)"
            ],
            technology: [
              "Cane preparation (chopper + shredder — maximum cell rupture for extraction)",
              "Tandem mill set (4–7 rollers — 93–97% extraction efficiency)",
              "Or diffuser (continuous counter-current extraction — higher efficiency)",
              "Juice heater (rapid heating to 70–75°C — prevents fermentation)",
              "Juice clarifier (rake or tray — mud/bagacillo separation)",
              "Multi-effect evaporators (juice concentration from 15 to 65 Brix)"
            ],
            skills: [
              "Mechanical Engineer — mill roller alignment, roller profile and mill extraction ratio",
              "Process Engineer — diffuser/mill juice extraction optimisation, imbibition rate",
              "Cane Supply Manager — harvesting schedule, cane freshness monitoring (>90 brix)",
              "Boiler Engineer — bagasse combustion, steam generation and energy self-sufficiency",
              "Quality Technician — juice purity, pol, brix and CCS (commercial cane sugar) measurement"
            ]
          },
          {
            id: "sg_cane",
            stage: "Sugarcane Growing",
            label: "Sugarcane",
            color: "#a16207",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Sugarcane (fresh)", detail: "Domestic — HS 1212.93. Uganda structural surplus ~822,000 t/yr. Kakira ~50% of national output. Smallholder and outgrower scheme alongside estate farming." },
              { name: "Phosphoric acid (clarification)", detail: "Imported — HS 2809.20. Used in juice clarification. Small volumes relative to cane throughput." },
              { name: "Lime (CaO / Ca(OH)2)", detail: "Domestic/imported — HS 2522. Lime for pH control in juice treatment. Some domestic lime production." }
            ]
          }
        ]
      }
    ]
  },

  "sg_ethanol": {
    id: "sg_ethanol",
    name: "Ethanol & Spirits",
    category: "Sugar Downstream",
    tier: "Phase IV — Downstream (Gap / Under-exploited)",
    color: "#854d0e",
    description: "Fuel ethanol and potable spirits from cane molasses. Uganda's most under-exploited sugar downstream — molasses is abundant (largely exported raw or used as animal feed) but ethanol production is minimal. Kabalega Industrial Park targets ethanol distillery investment.",
    legend: [
      { color: "#854d0e", label: "Ethanol production chain" },
      { color: "#a16207", label: "Molasses feedstock" },
    ],
    chains: [
      {
        title: "Ethanol Distillation Chain",
        accent: "#854d0e",
        nodes: [
          {
            id: "sg_eth_top",
            stage: "Finished Product (Under-exploited)",
            label: "Fuel Ethanol / Potable Spirit",
            color: "#854d0e",
            textColor: "#ffffff",
            inputs: [
              "Cane molasses (final by-product of sugar centrifugation — ~40% fermentable sugars)",
              "Yeast (Saccharomyces cerevisiae — molasses fermentation)",
              "Enzymes (invertase, glucoamylase — optional saccharification)",
              "Nutrients (DAP, urea — yeast nutrition)",
              "Distillation steam (bagasse or natural gas)",
              "Water (dilution, wash and cooling)"
            ],
            technology: [
              "Molasses dilution and conditioning tank (40–60 Brix dilution)",
              "Fermentation vessel (80,000–500,000 L batch or continuous)",
              "Beer still (distillation column — 5–6% → ~45% ethanol)",
              "Rectifier column (45% → 94–96% ethanol)",
              "Dehydration unit (molecular sieve — 99.5% anhydrous for fuel grade)",
              "Effluent treatment plant (vinasse — BOD 50,000 mg/L; high-strength waste)"
            ],
            skills: [
              "Fermentation Engineer — yeast pitching rate, temperature, pH and dissolved oxygen control",
              "Distillation Engineer — reflux ratio, plate efficiency and energy balance optimisation",
              "Environmental Engineer — vinasse treatment (irrigation, biodigestion or biogas recovery)",
              "Quality Chemist — ethanol assay, congener profile (aldehydes, fusel oils) per Uganda Bureau of Standards",
              "Energy Engineer — bagasse-to-ethanol energy balance (>50% self-sufficient if steam optimised)"
            ]
          },
          {
            id: "sg_molasses",
            stage: "Molasses (Abundant By-Product)",
            label: "Cane Molasses",
            color: "#a16207",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Cane molasses", detail: "Domestic — HS 1703.10. Abundant by-product at all Uganda sugar mills. ~8–10% of cane processed as molasses. Largely exported raw to Kenya/EAC or used as animal feed. Underutilised as ethanol feedstock." },
              { name: "Distillers yeast", detail: "Imported — HS 2102.10. Saccharomyces cerevisiae strains for high-temperature molasses fermentation. Most imported from Europe/India." }
            ]
          }
        ]
      }
    ]
  },

  "sg_hardcandy": {
    id: "sg_hardcandy",
    name: "Hard-Boiled Sweets & Lollipops",
    category: "Confectionery",
    tier: "Phase IV — Confectionery",
    color: "#a16207",
    description: "Boiled sugar candies, lollipops and hard sweets. Some domestic production exists in Uganda using locally refined sugar, imported flavours and colours. Growing segment with high domestic and regional demand.",
    legend: [
      { color: "#a16207", label: "Hard candy production chain" },
      { color: "#713f12", label: "Sugar input" },
    ],
    chains: [
      {
        title: "Hard Candy Production Chain",
        accent: "#a16207",
        nodes: [
          {
            id: "sg_candy_top",
            stage: "Finished Product",
            label: "Hard-Boiled Sweets / Lollipops",
            color: "#a16207",
            textColor: "#ffffff",
            inputs: [
              "White sugar (refined domestic — Kinyara or Kakira mill-white)",
              "Glucose syrup (imported or domestic — 43 DE corn/cane syrup)",
              "Citric acid (souring agent — imported)",
              "Flavours and colours (imported — fruit-flavour compounds, tartrazine etc.)",
              "Sticks for lollipops (paper or plastic — imported)",
              "Packaging wrappers (BOPP twist-wrap film — imported)"
            ],
            technology: [
              "Vacuum cooking kettle (sugar + glucose syrup boiled to 150–160°C, < 1% moisture)",
              "Batch roller / continuous rope former (forms sugar mass into ropes)",
              "Candy size former / cutting machine (cuts ropes to piece size)",
              "Cooling conveyor (crystallisation prevention — keep below Tg)",
              "Lollipop stick inserter (automatic for moulded pops)",
              "Twist wrapping machine (individual piece wrapping in BOPP)"
            ],
            skills: [
              "Confectionery Technologist — sugar-glucose ratio for glass body, cooking temperature and anti-graining",
              "Flavourist — flavour application rate, volatile loss compensation at high temperature",
              "Production Engineer — equipment speed balance from cooker to wrapper (throughput optimisation)",
              "Quality Technician — moisture (< 2%), colour, flavour intensity and shelf-life assessment",
              "Packaging Technician — twist-wrap tension, seal integrity and label registration"
            ]
          },
          {
            id: "sg_candy_raw",
            stage: "Sugar & Flavour Inputs",
            label: "Key Inputs",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Refined white sugar", detail: "Domestic — HS 1701.99. Kinyara white sugar and Kakira mill-white available. USD 38.1m white sugar still imported despite domestic surplus." },
              { name: "Glucose syrup", detail: "Imported — HS 1702.30. 43 DE corn or cane glucose syrup. Some limited domestic glucose production; most imported." },
              { name: "Flavour compounds", detail: "Imported — HS 3302.10. All synthetic fruit and non-fruit flavours imported from India, Germany (Givaudan, IFF, Firmenich distribution)." },
              { name: "Food colours", detail: "Imported — HS 3204.17. Synthetic food dyes (tartrazine, sunset yellow) imported; natural colour options limited." }
            ]
          }
        ]
      }
    ]
  },

  "sg_softdrink": {
    id: "sg_softdrink",
    name: "Sweetened Beverages",
    category: "Beverages",
    tier: "Phase IV — Downstream (Strong)",
    color: "#ca8a04",
    description: "Carbonated soft drinks, squashes and juices sweetened with sugar or HFCS. Strong domestic production — Coca-Cola Uganda, Century Bottling (Pepsi), Crown Beverages and others. One of Uganda's highest-output manufacturing sub-sectors.",
    legend: [
      { color: "#ca8a04", label: "Beverage production chain" },
      { color: "#a16207", label: "Sugar syrup" },
      { color: "#1e3a8a", label: "Ingredients (partly imported)" },
    ],
    chains: [
      {
        title: "Soft Drink Manufacturing Chain",
        accent: "#ca8a04",
        nodes: [
          {
            id: "sg_bev_top",
            stage: "Finished Product",
            label: "Carbonated Beverage",
            color: "#ca8a04",
            textColor: "#ffffff",
            inputs: [
              "White sugar (locally sourced — Kakira/Kinyara) or imported HFCS",
              "Flavour concentrate / syrup (imported — proprietary concentrate per brand)",
              "CO2 (carbonation — locally produced at some plants; imported cylinders at smaller ones)",
              "Treated water (reverse osmosis or ion exchange — municipal source)",
              "PET preforms (domestic production from imported PET resin)",
              "Closures, labels and packaging (domestic + imported)"
            ],
            technology: [
              "Water treatment plant (RO, UV sterilisation, ozone — WHO potable water standard)",
              "Syrup preparation room (sugar dissolving, mixing, pasteurisation)",
              "Carbonation unit (CO2 injection at 2.5–4 vol CO2)",
              "Filler and crowner / capper (high-speed 20,000–50,000 bottles/hr)",
              "Bottle blower (on-site ISBM from PET preforms — major converters)",
              "Coding, inspection and case packer"
            ],
            skills: [
              "Food Technologist — syrup recipe, Brix, acidity (pH 2.8–3.5) and carbonation specification",
              "Water Treatment Engineer — RO membrane management, TDS < 10 ppm product water quality",
              "Packaging Engineer — bottle integrity (burst pressure, top load), closure torque, label adhesion",
              "Quality Analyst — Brix, CO2 volume, pH, sensory evaluation and microbiological testing per UNBS",
              "Production Engineer — filler efficiency, downtime, CIP (clean-in-place) cycle management"
            ]
          },
          {
            id: "sg_syrup_prep",
            stage: "Syrup Preparation",
            label: "Beverage Syrup",
            color: "#a16207",
            textColor: "#ffffff",
            inputs: [
              "White sugar (Brix measurement: target 60–65 Brix simple syrup)",
              "Treated water (RO product water)",
              "Brand flavour concentrate (imported — Coca-Cola, PepsiCo, etc.)",
              "Citric acid (acidulant; tartaric acid for some variants)"
            ],
            technology: [
              "Sugar dissolving tank (steam-jacketed, agitated)",
              "Activated carbon filter (decolourisation before blending)",
              "Sterile filter (0.45 µm — final syrup filtration)",
              "Blending tank (simple syrup + concentrate + acid + water)"
            ],
            skills: [
              "Syrup Room Operator — Brix measurement, acid addition and concentrate dosing",
              "QC Analyst — sugar syrup Brix, clarity, smell and concentrate ratio confirmation",
              "CIP Operator — cleaning and sanitisation of syrup tanks and lines"
            ]
          },
          {
            id: "sg_bev_raw",
            stage: "Raw Materials",
            label: "Key Inputs",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "White sugar", detail: "Domestic — HS 1701.99. Purchased from Kakira, Kinyara. Uganda is a net sugar exporter but white sugar for industrial beverage use still partly imported." },
              { name: "PET preforms", detail: "Domestic — made from imported PET resin. Century Bottling and others blow their own bottles on-site from preforms." },
              { name: "CO2 gas", detail: "Partly domestic — HS 2811.21. Some industrial CO2 produced domestically (fermentation by-product); larger plants also import cylinders." },
              { name: "Flavour concentrate", detail: "Imported — HS 3302.10. All brand flavour concentrates are proprietary imports (Coca-Cola, Pepsi, Red Bull etc.)." }
            ]
          }
        ]
      }
    ]
  },

  "sg_brown": {
    id: "sg_brown",
    name: "Brown / Raw Sugar",
    category: "Sugar",
    tier: "Phase II — Milling (Strong)",
    color: "#b45309",
    description: "Mill-white and brown sugar from cane milling. Uganda's strongest sugar product — net regional exporter. ~822,000 t/yr total output; Kakira alone ~50%. Exports to DRC, South Sudan, Rwanda and broader EAC.",
    legend: [
      { color: "#b45309", label: "Brown sugar chain" },
      { color: "#a16207", label: "Cane growing" },
    ],
    chains: [
      {
        title: "Brown Sugar Production Chain",
        accent: "#b45309",
        nodes: [
          {
            id: "sg_brown_top",
            stage: "Finished Product",
            label: "Mill-White / Brown Sugar",
            color: "#b45309",
            textColor: "#ffffff",
            inputs: [
              "Sugarcane (12–17% sucrose — fresh cut)",
              "Imbibition water (counter-current extraction dilution)",
              "Lime (Ca(OH)2 — juice clarification and pH control)",
              "Sulphur dioxide (SO2 — partial bleaching / sulfitation mill-white)",
              "Steam from bagasse (all energy self-generated at Uganda mills)"
            ],
            technology: [
              "Cane preparation (chopper + shredder)",
              "Mill tandem (5–6 rol — continuous juice extraction)",
              "Juice clarifier (sulphitation or defecation)",
              "Multiple-effect evaporator (40–65 Brix concentration)",
              "Vacuum pan (A/B/C massecuite crystallisation)",
              "Basket centrifuge (A-sugar separation)"
            ],
            skills: [
              "Mill Engineer — roller press extraction and mill setting optimisation",
              "Process Chemist — juice quality, purity and ICUMSA color control",
              "Cane Supply Agronomist — harvesting cycle, cane quality and dextran monitoring",
              "Boiler Engineer — bagasse-fired boiler operation and steam pressure",
              "Packhouse Manager — bulk / 50 kg / 1 kg bagging and export certification"
            ]
          },
          {
            id: "sg_brown_raw",
            stage: "Sugarcane",
            label: "Sugarcane & Inputs",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Sugarcane (fresh)", detail: "Domestic — HS 1212.93. Uganda structural surplus. Kakira, Kinyara, SCOUL, Mayuge mills plus outgrowers and block farms supply ~822,000 t/yr." },
              { name: "Sulphur for SO2", detail: "Imported — HS 2503. Used as SO2 generator for sulfitation. Modest annual import volumes." }
            ]
          }
        ]
      }
    ]
  }
};

const CATEGORIES = [
  { name: "Sugar", color: "#713f12", products: ["sg_white", "sg_brown"] },
  { name: "Sugar Downstream", color: "#854d0e", products: ["sg_ethanol"] },
  { name: "Confectionery", color: "#a16207", products: ["sg_hardcandy"] },
  { name: "Beverages", color: "#ca8a04", products: ["sg_softdrink"] }
];

const TRADE_HS4 = {
  "1701": {
    desc: "HS 1701 — cane or beet sugar and chemically pure sucrose.",
    year: 2024, imports: { uganda: 38100.0, eac: 3200.0 }, exports: { uganda: 62000.0, eac: 58000.0 }
  },
  "1703": {
    desc: "HS 1703 — molasses from extraction or refining of sugar.",
    year: 2024, imports: { uganda: 200.0, eac: 100.0 }, exports: { uganda: 4800.0, eac: 3600.0 }
  },
  "2207": {
    desc: "HS 2207 — undenatured ethyl alcohol (≥80% vol.) and denatured alcohol.",
    year: 2024, imports: { uganda: 6400.0, eac: 1200.0 }, exports: { uganda: 1200.0, eac: 900.0 }
  },
  "1704": {
    desc: "HS 1704 — sugar confectionery (not cocoa-containing).",
    year: 2024, imports: { uganda: 8200.0, eac: 1400.0 }, exports: { uganda: 2600.0, eac: 2200.0 }
  },
  "2202": {
    desc: "HS 2202 — waters including mineral waters, sweetened or flavoured.",
    year: 2024, imports: { uganda: 4600.0, eac: 600.0 }, exports: { uganda: 12000.0, eac: 10000.0 }
  }
};

const PRODUCT_HS4 = {
  "sg_white":    "1701",
  "sg_brown":    "1701",
  "sg_ethanol":  "2207",
  "sg_hardcandy":"1704",
  "sg_softdrink":"2202"
};

const RAW_MATERIAL_TRADE = {
  "Sugarcane (fresh)": {
    desc: "HS 1212.93 — sugar cane. Domestic production ~822,000 t/yr. No import needed.",
    year: 2024, imports: { uganda: 0.0, eac: 0.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Cane molasses": {
    desc: "HS 1703.10 — cane molasses. Abundant domestic by-product; largely exported raw.",
    year: 2024, imports: { uganda: 200.0, eac: 100.0 }, exports: { uganda: 4800.0, eac: 3600.0 }
  },
  "Glucose syrup": {
    desc: "HS 1702.30 — glucose and glucose syrup. Largely imported for confectionery.",
    year: 2024, imports: { uganda: 3200.0, eac: 400.0 }, exports: { uganda: 200.0, eac: 150.0 }
  },
  "Flavour compounds": {
    desc: "HS 3302.10 — odoriferous mixtures and flavourings. All imported from India, Europe.",
    year: 2024, imports: { uganda: 4800.0, eac: 600.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const RAW_MATERIAL_PHASE = {
  "Sugarcane (fresh)": "sg_I"
};

const PHASE_PRODUCERS = {
  "sg_I": {
    count: 4,
    label: "Phase I — Cane Growing (strong — major estates + outgrowers)",
    examples: [
      "Kakira Sugar Works (~50% of national output; Jinja)",
      "Kinyara Sugar Ltd (Masindi)",
      "SCOUL (Sugar Corporation of Uganda Ltd, Lugazi)",
      "Mayuge Sugar Industries (Mayuge)"
    ]
  },
  "sg_II": {
    count: 4,
    label: "Phase II — Cane Milling & Raw Sugar",
    examples: [
      "Kakira Sugar Works",
      "Kinyara Sugar Ltd (~75,000 t refined/yr)",
      "SCOUL",
      "Mayuge Sugar Industries"
    ]
  },
  "sg_IV": {
    count: null,
    label: "Phase IV — Confectionery & Beverages (domestic production active)",
    examples: [
      "Coca-Cola Uganda / Century Bottling (soft drinks)",
      "Crown Beverages (Pepsi, Mirinda)",
      "Several domestic confectionery producers (names in MTIC register)"
    ]
  }
};

const PHASE_SOURCE = "MTIC Diagnostic Study on Sugar & Confectionery (Report 2, 2026)";

const PRODUCT_FIRMS = {
  "sg_white": {
    status: "emerging",
    firms: ["Kinyara Sugar Ltd (~75,000 t/yr industrial white)", "Kakira Sugar Works (mill-white)"],
    note: "Industrial white sugar: Kinyara leads; USD 38.1m still imported despite structural surplus. KEY GAP: Industrial sugar refining (Phase III) + downstream (Phase IV) under-exploited. 2040: Downstream-dominated chain."
  },
  "sg_brown": {
    status: "named",
    firms: ["Kakira Sugar Works", "Kinyara Sugar Ltd", "SCOUL", "Mayuge Sugar Industries"],
    note: "Uganda net regional exporter of brown/raw sugar. 4 major mills + outgrowers. ~822,000 t/yr total output."
  },
  "sg_ethanol": {
    status: "absent",
    firms: [],
    note: "Ethanol from molasses largely unexploited — KEY downstream gap. Molasses abundant but mostly exported raw. Kabalega park targets ethanol distillery investment."
  },
  "sg_hardcandy": {
    status: "emerging",
    firms: ["Several local confectioners in Kampala and Jinja (names in MTIC register)"],
    note: "Some hard-boiled sweets produced locally. Imported sugar and flavours. Growing regional demand."
  },
  "sg_softdrink": {
    status: "named",
    firms: [
      "Coca-Cola Uganda / Century Bottling (Kampala)",
      "Crown Beverages — Pepsi, Mirinda (Kampala)",
      "BIDCO Uganda (Riham Cola and other drinks)"
    ],
    note: "Largest manufacturing sub-sector by output. Uganda exports USD 12m sweetened beverages/yr (EAC market). Local sugar consumption is a major driver of sugar demand."
  }
};

const INPUT_KEYWORD_HS4 = [
  { pattern: /\bwhite sugar\b|\brefined.*sugar\b|\bmill.white sugar\b/i, hs4: "1701" },
  { pattern: /\bcane molasses\b|\bmolasses\b/i, hs4: "1703" },
  { pattern: /\bethanol\b|\bspirits\b/i, hs4: "2207" },
  { pattern: /\bglucose syrup\b/i, hs4: "1702" },
  { pattern: /\bflavour.*concentrate\b|\bflavouring\b|\bflavours and colours\b/i, hs4: "3302" },
  { pattern: /\bphosphoric acid\b/i, hs4: "2809" },
  { pattern: /\blime\b|\bcalcium hydroxide\b|\bquicklime\b/i, hs4: "2522" },
  { pattern: /\bsulphur dioxide\b|\bSO2\b/i, hs4: "2811" },
  { pattern: /\bactivated carbon\b|\bbone char\b/i, hs4: "3802" },
  { pattern: /\bsugarcane\b/i, hs4: "1212" },
  { pattern: /\byeast\b|\bSaccharomyces\b/i, hs4: "2102" },
  { pattern: /\bcitric acid\b/i, hs4: "2918" },
  { pattern: /\belemental sulphur\b|\bsulphur for\b|\bsulphur.*SO2\b/i, hs4: "2503" },
  { pattern: /\bCO2\b|\bcarbon dioxide\b.*carbonat/i, hs4: "2811" },
];

const INPUT_KEYWORD_PHASE = [
  { pattern: /\bcane.*harvest\b|\bsugarcane\b/i, phase: "sg_I" },
  { pattern: /\bKakira\b|\bKinyara\b|\bSCOUL\b/i, phase: "sg_II" },
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
