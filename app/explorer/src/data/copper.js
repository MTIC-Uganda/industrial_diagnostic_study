// Copper & Allied Metals — Value Chain Explorer data
// Source: MTIC Diagnostic Study (Report 1); ITC TradeMap 2024; seed_all_chains.py STRENGTH data

const PRODUCTS = {
  "cu_cable": {
    id: "cu_cable",
    name: "Insulated Power & Data Cable",
    category: "Copper Products",
    tier: "Phase V — Fabrication",
    color: "#7c3aed",
    description: "Multi-core insulated electrical cable for power distribution, building wiring and data transmission. Uganda's primary copper finished product — Cable Corporation Ltd holds ~65% domestic market share.",
    legend: [
      { color: "#7c3aed", label: "Copper fabrication chain" },
      { color: "#4f46e5", label: "Wire drawing & stranding" },
      { color: "#2563eb", label: "Intermediate processing" },
      { color: "#1e3a8a", label: "Raw materials (imported)" },
    ],
    chains: [
      {
        title: "Copper Cable Chain",
        accent: "#7c3aed",
        nodes: [
          {
            id: "cu_cable_top",
            stage: "Finished Product",
            label: "Insulated Cable",
            color: "#7c3aed",
            textColor: "#ffffff",
            inputs: [
              "Copper wire bundle (drawn & annealed, 0.1–2.5 mm strands)",
              "PVC / XLPE insulation compound (imported resin pellets)",
              "Aluminium foil tape (moisture barrier for data cables)",
              "Steel wire armour (SWA — mechanical protection)",
              "Outer sheath compound (PVC / PE / LSZH — fire grade)"
            ],
            technology: [
              "Wire bunching / stranding machine (multi-wire lay-up)",
              "SZ stranding line (alternating lay for flexible cores)",
              "Continuous vulcanization (CV) line — XLPE cross-linking",
              "Single/twin screw extruder — PVC/LSZH sheathing",
              "Armoring machine — steel wire or tape armouring",
              "Spark tester & HV cable tester (insulation integrity)"
            ],
            skills: [
              "Cable Design Engineer — conductor sizing, insulation thickness & short-circuit rating (IEC 60228, 60502)",
              "Polymer Engineer — compound formulation, extrusion temperature & cure profile control",
              "Electrical Engineer — dielectric, capacitance & insulation resistance specification",
              "Quality Control Engineer — spark test, partial discharge & routine electrical tests",
              "Mechanical Engineer — armour lay, tensile & crush resistance design"
            ]
          },
          {
            id: "cu_wire_draw",
            stage: "Wire Drawing",
            label: "Copper Wire",
            color: "#4f46e5",
            textColor: "#ffffff",
            inputs: [
              "Copper wire rod (8 mm rod — 99.9% Cu ETP grade)",
              "Wire drawing lubricant / emulsion (soap or synthetic)",
              "Nitrogen / forming gas (annealing atmosphere)",
              "Energy (electric motor drives for drawing line)",
              "Annealing acid pickle (remove surface oxide)"
            ],
            technology: [
              "Multi-die rod breakdown machine (8 mm → 1–2 mm in single pass set)",
              "Intermediate / fine drawing machine (multi-die, up to 35 dies)",
              "Inline continuous annealing furnace (resistive or induction)",
              "Automatic spool winder / stem winder (take-up)",
              "Laser micrometer (in-line diameter control)"
            ],
            skills: [
              "Wire Drawing Engineer — die schedule design, reduction ratio & friction management",
              "Metallurgist — recrystallization & softening control during annealing (electrical conductivity recovery)",
              "Mechanical Engineer — die box alignment, lubricant pressure & cooling system maintenance",
              "Quality Engineer — conductor resistance (Ω/km), elongation & tensile testing per IEC 60228",
              "Process Technician — die wear monitoring & replacement interval optimisation"
            ]
          },
          {
            id: "cu_wirerod_node",
            stage: "Rod Production",
            label: "Copper Wire Rod",
            color: "#2563eb",
            textColor: "#ffffff",
            inputs: [
              "Refined copper cathode (99.99% Cu — imported from DRC/China/Belgium)",
              "Charcoal / carbon cover (melt surface protection from oxidation)",
              "Energy (natural gas or electricity for melting furnace)",
              "Casting lubricant (graphite or oil — continuous casting)",
              "Controlled rolling atmosphere (N2 or CO2)"
            ],
            technology: [
              "Shaft melting furnace (closed top — low oxygen uptake)",
              "Holding furnace (temperature homogenisation before casting)",
              "Upward continuous casting machine (UCF) or Properzi wheel-and-belt caster",
              "Inline rolling mill (tandem stands — 8 mm rod in one pass)",
              "Quench & pickling line (surface oxide removal)"
            ],
            skills: [
              "Pyrometallurgist — copper melt chemistry control (oxygen < 5 ppm for ETP grade)",
              "Casting Technologist — melt flow rate, casting speed & solidification structure",
              "Rolling Engineer — pass schedule, temperature & rod geometry control",
              "Quality Engineer — resistivity, bend & surface defect inspection per EN 1977",
              "Maintenance Engineer — furnace refractory and casting wheel maintenance"
            ]
          },
          {
            id: "cu_cathode_raw",
            stage: "Raw Materials (Imported)",
            label: "Copper Cathode & Materials",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Refined copper cathode (99.99%)", detail: "Imported from DRC, China, Belgium — HS 7403.11. Uganda imports USD 6.9m/yr. Phases I–IV (mining → refining) entirely absent in Uganda; Kilembe mine dormant since 1980s." },
              { name: "Copper scrap (secondary)", detail: "Limited domestic recycling — HS 7404.00. Secondary copper from electrical scrap; small volume supplements cathode imports." },
              { name: "PVC resin pellets", detail: "Imported — HS 3904.10. All insulation-grade PVC imported; domestic PVC resin awaits Kabalega petrochemical park (~2029)." },
              { name: "Steel wire (armour grade)", detail: "Imported or sourced locally from domestic steel mills (Uganda Baati, Roofings) — HS 7217. Domestic rebar and wire production active." }
            ]
          }
        ]
      }
    ]
  },

  "cu_wire": {
    id: "cu_wire",
    name: "Copper Wire & Winding Wire",
    category: "Copper Products",
    tier: "Phase V — Fabrication",
    color: "#6d28d9",
    description: "Bare and enamelled copper conductor wire for motor windings, transformers and electrical coils. Drawn from imported wire rod at Cable Corporation Ltd.",
    legend: [
      { color: "#6d28d9", label: "Wire & conductor chain" },
      { color: "#4f46e5", label: "Drawing & annealing" },
      { color: "#1e3a8a", label: "Raw materials (imported)" },
    ],
    chains: [
      {
        title: "Copper Wire Chain",
        accent: "#6d28d9",
        nodes: [
          {
            id: "cu_wire_top",
            stage: "Finished Product",
            label: "Copper Wire / Magnet Wire",
            color: "#6d28d9",
            textColor: "#ffffff",
            inputs: [
              "Fine copper conductor (0.05–1.0 mm — drawn & annealed)",
              "Enamel coating resin (polyurethane, polyesterimide or polyamide-imide)",
              "Solvent (for enamel thinning / application)",
              "Energy (continuous enamel curing ovens)",
              "Nylon / polyester outer coat (mechanical protection)"
            ],
            technology: [
              "Fine/ultra-fine wire drawing machine (up to 40+ dies for < 0.1 mm wire)",
              "Vertical enamelling machine (multiple pass dies + oven towers)",
              "Continuous annealing / soft-draw line (for flexible grades)",
              "Optical diameter gauge (in-line — tolerances ± 0.001 mm)",
              "Film build & pin-hole tester (enamel integrity per IEC 60317)"
            ],
            skills: [
              "Enamel Coating Engineer — film build specification, cure temperature profile & breakdown voltage targets",
              "Fine Wire Technician — ultra-fine die maintenance and lubricant purity management",
              "Materials Engineer — grade selection (MW35-C, MW79-C) per IEC 60317 for motor class",
              "Quality Engineer — conductor resistance, elongation, adhesion, abrasion & thermal endurance tests",
              "Electrical Engineer — winding design consultation (fill factor, coil resistance, heat dissipation)"
            ]
          },
          {
            id: "cu_wire_rod2",
            stage: "Wire Rod",
            label: "Copper Wire Rod",
            color: "#2563eb",
            textColor: "#ffffff",
            inputs: [
              "Refined copper cathode (99.99% — imported)",
              "Energy (electric furnace or gas melting)",
              "Carbon cover (melt protection)"
            ],
            technology: [
              "Continuous casting & rolling (Properzi or Contirod process)",
              "Inline rod mill (8 mm ETP rod)",
              "Quench & coiling line"
            ],
            skills: [
              "Pyrometallurgist — ETP grade oxygen control (< 5 ppm)",
              "Rolling Engineer — pass schedule & temperature control",
              "Quality Engineer — resistivity & surface inspection"
            ]
          },
          {
            id: "cu_wire_raw",
            stage: "Raw Materials (Imported)",
            label: "Cathode & Enamel Materials",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Refined copper cathode (99.99%)", detail: "Imported — HS 7403.11. All cathode imported; no electrorefining in Uganda." },
              { name: "Enamel coating resin", detail: "Imported — HS 3907.20. Polyurethane and polyesterimide resins from India/China." },
              { name: "Polyamide-imide resin (top coat)", detail: "Imported — Class H (200°C) thermal-class motor-grade wire resin." }
            ]
          }
        ]
      }
    ]
  },

  "cu_alu_cond": {
    id: "cu_alu_cond",
    name: "Aluminium Conductor (ACSR)",
    category: "Aluminium Products",
    tier: "Phase V — Fabrication (Gap)",
    color: "#1d4ed8",
    description: "Aluminium conductor steel-reinforced (ACSR) overhead power line cable. Used for high-voltage transmission lines. Entirely imported into Uganda — no domestic ACSR production exists.",
    legend: [
      { color: "#1d4ed8", label: "ACSR conductor chain" },
      { color: "#1e40af", label: "Drawing & stranding" },
      { color: "#1e3a8a", label: "Raw materials (imported)" },
    ],
    chains: [
      {
        title: "ACSR Conductor Chain",
        accent: "#1d4ed8",
        nodes: [
          {
            id: "cu_alu_cond_top",
            stage: "Finished Product (Gap)",
            label: "ACSR Overhead Conductor",
            color: "#1d4ed8",
            textColor: "#ffffff",
            inputs: [
              "Aluminium EC-grade wire strands (99.7% Al — outer layers)",
              "High-strength steel wire core (galvanized — central strength member)",
              "Lay-up grease / compound (corrosion protection at Al/steel interface)",
              "Energy (wire drawing and stranding lines)"
            ],
            technology: [
              "Aluminium rod breakdown machine (9 mm → wire)",
              "Multi-wire stranding machine (Rosette pattern — 6+12+18 wires)",
              "Steel core drawing machine (galvanized high-tensile wire)",
              "Catenary stranding line (lay-up of Al layers over steel core)",
              "Tensile & UTS test rig (breaking load per IEC 61089)"
            ],
            skills: [
              "Conductor Design Engineer — sag-tension calculation, creep allowance & thermal rating (IEC 61089)",
              "Wire Drawing Technician — aluminium die schedule, reduction ratio & surface quality",
              "Materials Engineer — Al alloy grade (1350 series) conductivity & steel core zinc coating specification",
              "Quality Engineer — conductor DC resistance, mechanical strength & surface inspection",
              "Transmission Engineer — system voltage, span length, wind-ice loading specification"
            ]
          },
          {
            id: "cu_alu_cond_raw",
            stage: "Raw Materials (Imported)",
            label: "Aluminium & Steel Inputs",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Aluminium wire rod (EC grade, 9 mm)", detail: "Imported — HS 7604.10. No domestic aluminium rod production; all aluminium absent from Uganda's metals sector." },
              { name: "High-tensile galvanized steel wire", detail: "Imported — HS 7217.20. Domestic steel wire exists but not high-tensile ACSR-core grade." },
              { name: "Aluminium alloy ingot (1350 series)", detail: "Imported — HS 7601.20. All aluminium ingot imported; no local smelter." }
            ]
          }
        ]
      }
    ]
  },

  "cu_alu_prof": {
    id: "cu_alu_prof",
    name: "Aluminium Profiles & Extrusions",
    category: "Aluminium Products",
    tier: "Phase V — Fabrication (Gap)",
    color: "#2563eb",
    description: "Extruded aluminium profiles for window frames, structural sections and architectural elements. All imported into Uganda — no domestic aluminium extrusion exists.",
    legend: [
      { color: "#2563eb", label: "Aluminium extrusion chain" },
      { color: "#1e3a8a", label: "Raw materials (imported)" },
    ],
    chains: [
      {
        title: "Aluminium Extrusion Chain",
        accent: "#2563eb",
        nodes: [
          {
            id: "cu_alu_prof_top",
            stage: "Finished Product (Gap)",
            label: "Aluminium Profiles",
            color: "#2563eb",
            textColor: "#ffffff",
            inputs: [
              "Aluminium billet (6063 or 6061 alloy — 170 mm dia.)",
              "Die tooling (profile die, mandrel, bolster — tool steel H13)",
              "Nitrogen / water quench (profile exit cooling)",
              "Anodising / powder-coat chemicals (surface finish)",
              "Energy (billet induction heater + hydraulic press drive)"
            ],
            technology: [
              "Aluminium extrusion press (500–3,600 tonne hydraulic)",
              "Profile run-out table with puller (stretch for straightness)",
              "Age-hardening oven (T5/T6 temper — strength development)",
              "Anodising line (sulfuric acid bath + sealing)",
              "Powder coating booth (polyester TGIC or PVDF topcoat)"
            ],
            skills: [
              "Extrusion Engineer — die design, bearing adjustment, billet temperature & press speed optimisation",
              "Materials Engineer — alloy temper specification (T5/T6 per EN 755) for structural grades",
              "Tooling Engineer — die design, nitriding & die correction for tight dimensional tolerances",
              "Surface Treatment Engineer — anodising bath chemistry, coating thickness & colour consistency",
              "Quality Engineer — dimensional inspection, mechanical testing & EN 12020 profile compliance"
            ]
          },
          {
            id: "cu_alu_prof_raw",
            stage: "Raw Materials (Imported)",
            label: "Aluminium Billet & Alloys",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Aluminium billet (6063 alloy)", detail: "Imported — HS 7604.21. No domestic aluminium casting or billet production in Uganda." },
              { name: "Aluminium alloy ingot (6xxx series)", detail: "Imported — HS 7601.20. Mg-Si alloy for architectural extrusions; all imported from UAE, China, Egypt." }
            ]
          }
        ]
      }
    ]
  },

  "cu_brass": {
    id: "cu_brass",
    name: "Brass Rod, Fittings & Valves",
    category: "Copper Products",
    tier: "Phase V — Fabrication (Gap)",
    color: "#b45309",
    description: "Copper-zinc alloy (brass) rod, machined fittings and valves for plumbing and hardware. No domestic brass production in Uganda — all imported from India, China and Turkey.",
    legend: [
      { color: "#b45309", label: "Brass fabrication chain" },
      { color: "#1e3a8a", label: "Raw materials (imported)" },
    ],
    chains: [
      {
        title: "Brass Production Chain",
        accent: "#b45309",
        nodes: [
          {
            id: "cu_brass_top",
            stage: "Finished Product (Gap)",
            label: "Brass Fittings & Valves",
            color: "#b45309",
            textColor: "#ffffff",
            inputs: [
              "Brass rod (CW614N — 58% Cu, 39% Zn, 3% Pb for free-machining)",
              "Cutting oils / coolants (CNC machining)",
              "Chrome plating chemicals or lacquer (corrosion finish)",
              "Energy (CNC lathe, drilling, threading, deburring)"
            ],
            technology: [
              "CNC multi-spindle lathe / Swiss-type turning centre",
              "Thread rolling / die-cutting machine",
              "Pressure die casting (complex valve bodies)",
              "Electroplating line (nickel or chrome finish)",
              "Pressure test bench (valve leak testing)"
            ],
            skills: [
              "CNC Machinist — precision turning to ± 0.05 mm for thread-form and seat dimensions",
              "Foundry Engineer — die casting parameter optimisation (temperature, injection speed, ejection)",
              "Materials Engineer — alloy selection for dezincification resistance in potable water applications",
              "Quality Engineer — pressure test, thread gauge inspection & WRAS/KTW approval compliance",
              "Production Engineer — cycle time optimisation, tooling life and burr-free output"
            ]
          },
          {
            id: "cu_brass_alloy",
            stage: "Alloy Melting (Gap)",
            label: "Brass Alloy",
            color: "#92400e",
            textColor: "#ffffff",
            inputs: [
              "Copper cathode (58–63% Cu — primary feed)",
              "Zinc ingots (SHG grade, 37–42% Zn — alloying element)",
              "Lead ingots (1–3% Pb — machinability additive, except lead-free grades)",
              "Brass scrap (returns — recycled trimmings)",
              "Energy (induction melting furnace)"
            ],
            technology: [
              "Induction melting furnace (500–2,000 kg heat)",
              "Semi-continuous casting (horizontal or vertical billet caster)",
              "Rotary piercing / extrusion press (rod & tube billet)",
              "Multi-pass wire / rod drawing (final diameter reduction)",
              "Annealing furnace (inter-pass softening)"
            ],
            skills: [
              "Pyrometallurgist — melt chemistry control (Zn loss compensation by volatilisation)",
              "Casting Technologist — solidification structure, porosity and segregation control",
              "Drawing Engineer — rod drawing pass schedule & die angle optimisation",
              "Quality Engineer — chemical composition, hardness & UTS per EN 12164/12165",
              "Health & Safety Engineer — lead exposure controls in lead-brass plants"
            ]
          },
          {
            id: "cu_brass_raw",
            stage: "Raw Materials (Imported)",
            label: "Copper, Zinc & Alloy Inputs",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Refined copper cathode", detail: "Imported — HS 7403.11. No domestic production; Kilembe mine dormant." },
              { name: "Zinc ingots (SHG grade)", detail: "Imported — HS 7901.11. No domestic zinc production in Uganda." },
              { name: "Brass rod (semi-finished)", detail: "Imported — HS 7407.21. All brass semi-finished products imported; no local alloy production." }
            ]
          }
        ]
      }
    ]
  }
};

const CATEGORIES = [
  { name: "Copper Products", color: "#7c3aed", products: ["cu_cable", "cu_wire", "cu_brass"] },
  { name: "Aluminium Products", color: "#1d4ed8", products: ["cu_alu_cond", "cu_alu_prof"] }
];

const TRADE_HS4 = {
  "7403": {
    desc: "HS 7403 — refined copper and copper alloys (unwrought), incl. cathode",
    year: 2024, imports: { uganda: 6900.0, eac: 0.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "7408": {
    desc: "HS 7408 — copper wire",
    year: 2024, imports: { uganda: 2800.0, eac: 200.0 }, exports: { uganda: 1200.0, eac: 1100.0 }
  },
  "8544": {
    desc: "HS 8544 — insulated electric conductors and cable",
    year: 2024, imports: { uganda: 57700.0, eac: 8000.0 }, exports: { uganda: 5200.0, eac: 4800.0 }
  },
  "7601": {
    desc: "HS 7601 — unwrought aluminium",
    year: 2024, imports: { uganda: 12995.0, eac: 0.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "7604": {
    desc: "HS 7604 — aluminium bars, rods and profiles",
    year: 2024, imports: { uganda: 4200.0, eac: 400.0 }, exports: { uganda: 120.0, eac: 100.0 }
  },
  "7407": {
    desc: "HS 7407 — copper bars, rods and profiles (incl. brass rod)",
    year: 2024, imports: { uganda: 1800.0, eac: 50.0 }, exports: { uganda: 30.0, eac: 20.0 }
  },
  "7614": {
    desc: "HS 7614 — stranded wire, cable, plaited bands etc. of aluminium (ACSR)",
    year: 2024, imports: { uganda: 8600.0, eac: 500.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const PRODUCT_HS4 = {
  "cu_cable":    "8544",
  "cu_wire":     "7408",
  "cu_alu_cond": "7614",
  "cu_alu_prof": "7604",
  "cu_brass":    "7407"
};

const RAW_MATERIAL_TRADE = {
  "Refined copper cathode (99.99%)": {
    desc: "HS 7403.11 — refined copper cathode. Imported from DRC, China, Belgium.",
    year: 2024, imports: { uganda: 6900.0, eac: 0.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Copper scrap (secondary)": {
    desc: "HS 7404.00 — copper waste and scrap. Limited secondary copper from recycling.",
    year: 2024, imports: { uganda: 400.0, eac: 100.0 }, exports: { uganda: 200.0, eac: 150.0 }
  },
  "Aluminium wire rod (EC grade, 9 mm)": {
    desc: "HS 7604.10 — aluminium bars and rods. No domestic production.",
    year: 2024, imports: { uganda: 4200.0, eac: 400.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Aluminium billet (6063 alloy)": {
    desc: "HS 7604.21 — aluminium alloy profiles (semi-finished). All imported.",
    year: 2024, imports: { uganda: 3100.0, eac: 200.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Zinc ingots (SHG grade)": {
    desc: "HS 7901.11 — unwrought zinc, not alloyed. No domestic zinc production in Uganda.",
    year: 2024, imports: { uganda: 1200.0, eac: 0.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const RAW_MATERIAL_PHASE = {};

const PHASE_PRODUCERS = {
  "cu_V": {
    count: 1,
    label: "Phase V — Copper Fabrication (wire drawing, cable making)",
    examples: ["Cable Corporation Ltd — wire drawing, stranding & cable production"]
  },
  "cu_VI": {
    count: null,
    label: "Phase VI — Market (domestic distribution & regional export)",
    examples: ["Cable Corporation Ltd ~65% domestic market share; regional exports to EAC"]
  }
};

const PHASE_SOURCE = "MTIC Diagnostic Study on Iron & Steel and Copper (Report 1, 2026)";

const PRODUCT_FIRMS = {
  "cu_cable": {
    status: "named",
    firms: ["Cable Corporation Ltd (~65% domestic market share in Uganda)"],
    note: "USD 57.7m cable imports remain despite domestic production — Phases I–IV entirely absent. 2040 target: USD 300–500m cable market; Kilembe copper cathode + cobalt production."
  },
  "cu_wire": {
    status: "named",
    firms: ["Cable Corporation Ltd (wire drawing and winding wire)"],
    note: "Copper wire produced from imported cathode. Winding wire for motors and transformers."
  },
  "cu_alu_cond": {
    status: "absent",
    firms: [],
    note: "ACSR conductor entirely imported. No domestic aluminium conductor production. Uganda imports ~USD 8.6m ACSR/yr (HS 7614, 2024)."
  },
  "cu_alu_prof": {
    status: "absent",
    firms: [],
    note: "Aluminium extrusions entirely imported from UAE, China, Egypt. No domestic aluminium extrusion in Uganda."
  },
  "cu_brass": {
    status: "absent",
    firms: [],
    note: "Brass rod and fittings entirely imported. No domestic brass alloy production. Uganda imports ~USD 1.8m brass rod/yr (HS 7407, 2024)."
  }
};

const INPUT_KEYWORD_HS4 = [
  { pattern: /\bcopper cathode\b|\bcathode.*99\.99\b/i, hs4: "7403" },
  { pattern: /\bcopper scrap\b/i, hs4: "7404" },
  { pattern: /\bcopper wire rod\b/i, hs4: "7408" },
  { pattern: /\bzinc ingots?\b/i, hs4: "7901" },
  { pattern: /\baluminium billet\b|\baluminium wire rod\b/i, hs4: "7604" },
  { pattern: /\bPVC.*insulation\b|\bXLPE\b/i, hs4: "3904" },
];

const INPUT_KEYWORD_PHASE = [
  { pattern: /\bcopper wire rod\b|\bwire rod.*copper\b/i, phase: "cu_V" },
  { pattern: /\brefined copper cathode\b/i, phase: "cu_V" },
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
