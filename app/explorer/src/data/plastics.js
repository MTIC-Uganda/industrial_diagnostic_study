// Plastics & Packaging — Value Chain Explorer data
// Source: MTIC Diagnostic Study (Report 2); ITC TradeMap 2024; seed_all_chains.py STRENGTH data

const PRODUCTS = {
  "pl_bottles": {
    id: "pl_bottles",
    name: "PET Bottles & Containers",
    category: "Rigid Packaging",
    tier: "Phase II — Conversion (Strong)",
    color: "#1e3a8a",
    description: "PET bottles for beverages, water and edible oils. Strong domestic production — preforms injection-moulded from imported PET resin then blow-moulded into bottles. KEY GAP: PET resin 100% imported (~150,000 t/yr total plastic resin). 2040: Kabalega park domestic resin.",
    legend: [
      { color: "#1e3a8a", label: "PET bottle chain" },
      { color: "#1e40af", label: "Preform making" },
      { color: "#1d4ed8", label: "Resin inputs" },
    ],
    chains: [
      {
        title: "PET Bottle Production Chain",
        accent: "#1e3a8a",
        nodes: [
          {
            id: "pl_bottle_top",
            stage: "Finished Product",
            label: "PET Bottle",
            color: "#1e3a8a",
            textColor: "#ffffff",
            inputs: [
              "PET preform (injection-moulded — domestic production from imported resin)",
              "Compressed air (30–40 bar — for stretch-blow moulding)",
              "Energy (ISBM machine electrical drive)",
              "Nitrogen (optional — bottle rinse before filling)",
              "Cap / closure (injection-moulded PP — domestic production)"
            ],
            technology: [
              "Injection stretch blow moulding (ISBM) machine — single stage (preform to bottle in one step)",
              "Or two-stage ISBM (re-heat blow) — preforms reheated and blown at high speed",
              "Bottle leak tester (100% air-pressure integrity check)",
              "Vision inspection system (wall thickness, colour, top-load check)",
              "Bottle conveyor + palletiser (output handling)"
            ],
            skills: [
              "ISBM Process Engineer — preform re-heat temperature, blow timing, stretch rod force",
              "Mould Technician — cavity maintenance, surface polishing and neck ring adjustment",
              "Quality Engineer — burst pressure, top-load capacity, base clearance (ASTM D2659)",
              "Maintenance Engineer — ISBM conveyor, transfer gripper and blow valve overhaul",
              "Production Planner — throughput, mould changeover time and resin lot management"
            ]
          },
          {
            id: "pl_preform",
            stage: "Preform Moulding",
            label: "PET Preform",
            color: "#1e40af",
            textColor: "#ffffff",
            inputs: [
              "PET resin pellets (bottle-grade IV 0.76–0.84 dL/g — imported)",
              "Colorant / masterbatch (imported — low addition rate for clear)",
              "Energy (injection moulding machine — high clamping force)",
              "Crystalliser / dryer (PET moisture removal to < 50 ppm before injection)"
            ],
            technology: [
              "PET crystalliser and dryer (desiccant bed — 160°C, 4 hr)",
              "Injection moulding machine (hot runner — 72 to 144 cavity mould)",
              "Robotic parts extraction and cooling (post-mould cooling conveyor)",
              "Cavity-by-cavity weight and IV sampling (quality control)"
            ],
            skills: [
              "Injection Moulding Technician — barrel temperature, back pressure, cooling time and gate optimisation",
              "PET Materials Engineer — IV management, acetaldehyde content (< 5 ppm for water bottles)",
              "Mould Maintenance Technician — hot runner temperature controller, cavity cooling and gate tip",
              "Quality Analyst — preform weight, wall thickness, haze and clarity per customer spec"
            ]
          },
          {
            id: "pl_bottle_raw",
            stage: "Raw Materials (Imported)",
            label: "PET Resin & Inputs",
            color: "#1d4ed8",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "PET resin pellets (bottle grade)", detail: "Imported — HS 3907.61. 100% imported. No domestic PET production. Kabalega petrochemical park (future ~2029) target domestic resin. Uganda imports ~USD 40m PET/yr." },
              { name: "PP resin (caps)", detail: "Imported — HS 3902.10. Closure-grade PP all imported; caps moulded domestically." },
              { name: "Masterbatch / colorant", detail: "Partly domestic — HS 3206.49. Some masterbatch compounding locally; base concentrate imported." }
            ]
          }
        ]
      }
    ]
  },

  "pl_pipes": {
    id: "pl_pipes",
    name: "Plastic Pipes & Fittings",
    category: "Construction Plastics",
    tier: "Phase II — Conversion (Strong)",
    color: "#1e40af",
    description: "PVC and HDPE pipes for water supply, drainage, irrigation and conduit. Strong domestic production — Roofings, KGAL and others extrude pipes domestically. Uganda exports significant volumes to EAC.",
    legend: [
      { color: "#1e40af", label: "Pipe extrusion chain" },
      { color: "#1d4ed8", label: "Compound & resin" },
      { color: "#1e3a8a", label: "Raw materials (imported)" },
    ],
    chains: [
      {
        title: "Plastic Pipe Production Chain",
        accent: "#1e40af",
        nodes: [
          {
            id: "pl_pipe_top",
            stage: "Finished Product",
            label: "PVC / HDPE Pipe",
            color: "#1e40af",
            textColor: "#ffffff",
            inputs: [
              "PVC resin (K-value 67 for rigid pipe — imported)",
              "Heat stabiliser (Ca-Zn or OBS — prevents thermal degradation in extruder)",
              "Filler (calcium carbonate — cost and rigidity filler)",
              "Lubricants (internal + external — melt flow and surface quality)",
              "Carbon black (UV stabilisation for outdoor drainage pipe)",
              "Energy (extruder screw and haul-off drive)"
            ],
            technology: [
              "Conical twin-screw extruder (PVC pipe — W&P, Cincinnati or equivalent)",
              "Calibration and vacuum sizing sleeve (pipe OD and wall tolerance ≤ ±0.3 mm)",
              "Cooling water trough (spray or immersion)",
              "Belt haul-off (constant pulling speed control)",
              "Planetary cutter / saw (cut to length 6 m std.)",
              "Belling / socketing machine (push-fit or solvent-cement joint)"
            ],
            skills: [
              "Extrusion Process Engineer — melt temperature profile, torque and output rate optimisation",
              "PVC Compounder — heat stabiliser selection, formulation balancing and compound mixing",
              "Dimensional Inspector — wall thickness (min. per ISO 1452), OD and ovality measurement",
              "Quality Engineer — ring stiffness, impact, vicat softening (ISO 9969, 1628-2) per UNBS",
              "Maintenance Engineer — screw / barrel wear monitoring and liner replacement"
            ]
          },
          {
            id: "pl_compound",
            stage: "Compounding",
            label: "PVC Compound",
            color: "#1d4ed8",
            textColor: "#ffffff",
            inputs: [
              "PVC resin K-67 (imported — base polymer)",
              "Dibasic lead stabiliser (thermal stabiliser — being phased to Ca-Zn)",
              "Calcium carbonate (filler — 5–8 phr for pipe; 10–15 phr for fittings)",
              "Titanium dioxide (whiteness and UV resistance)",
              "Processing aid (acrylic type — melt viscosity and surface)"
            ],
            technology: [
              "High-speed mixer (Henschel type — dry blend at 110°C batch)",
              "Cooling mixer (cool down dry blend before feeding extruder)",
              "Or co-rotating twin-screw compounder (fully compounded pellets)"
            ],
            skills: [
              "PVC Formulation Chemist — stabiliser system selection, fusion characteristics",
              "Mixer Operator — batch weighing accuracy, mixing time and discharge temperature",
              "Quality Analyst — gelation test (torque rheometer), thermal stability and colour check"
            ]
          },
          {
            id: "pl_pipe_raw",
            stage: "Raw Materials (Imported)",
            label: "PVC & HDPE Resin",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "PVC resin (K-67)", detail: "Imported — HS 3904.10. All PVC resin imported; no domestic production. Kabalega park future target ~2029." },
              { name: "HDPE resin (pipe grade)", detail: "Imported — HS 3901.10. PE100 HDPE pipe grade imported from Middle East, India, China." },
              { name: "Calcium carbonate (filler)", detail: "Partly domestic — HS 2836.50. Uganda has limestone deposits; some local GCC/PCC milling exists." }
            ]
          }
        ]
      }
    ]
  },

  "pl_bags": {
    id: "pl_bags",
    name: "Plastic Bags & Sacks",
    category: "Flexible Packaging",
    tier: "Phase II — Conversion (Strong)",
    color: "#1d4ed8",
    description: "Polyethylene carrier bags, produce bags and heavy-duty sacks. 41 UNBS-certified manufacturers in Uganda — strongest indicator of the depth of plastics conversion activity. All resin imported. Bag tax and bans affect thin single-use grades.",
    legend: [
      { color: "#1d4ed8", label: "Bag / sack chain" },
      { color: "#1e3a8a", label: "Film & resin (partly imported)" },
    ],
    chains: [
      {
        title: "Plastic Bag Production Chain",
        accent: "#1d4ed8",
        nodes: [
          {
            id: "pl_bag_top",
            stage: "Finished Product",
            label: "PE Bag / Sack",
            color: "#1d4ed8",
            textColor: "#ffffff",
            inputs: [
              "HDPE / LDPE film (domestically extruded from imported resin)",
              "Colorant masterbatch (imported concentrate at 2–5%)",
              "Handles / strips (LDPE or HDPE — continuous strip for D-cut handles)",
              "Energy (bag making machine — heat seal bar drives)",
              "Print inks (flexographic — for printed carrier bags; partly domestic)"
            ],
            technology: [
              "Blown film extruder (HDPE monolayer or multilayer blown film)",
              "Corona treater (surface activation for print adhesion)",
              "Flexographic printer (2–8 colour — inline or standalone)",
              "Bag making machine (bottom seal, side weld or D-cut with punching)",
              "Auto-bagger / counter (bag counting, stacking and banding)"
            ],
            skills: [
              "Film Extrusion Engineer — BUR, blow-up ratio, film gauge uniformity and Haze control",
              "Print Technician — ink viscosity, doctor blade pressure and colour density management",
              "Bag Making Operator — heat seal temperature, dwell time and cut blade sharpness",
              "Quality Inspector — seal strength, tensile, bag weight and print registration",
              "Regulatory Officer — UNBS certification compliance and bag thickness/gauge requirements"
            ]
          },
          {
            id: "pl_film",
            stage: "Film Production",
            label: "PE Film",
            color: "#2563eb",
            textColor: "#ffffff",
            inputs: [
              "HDPE or LDPE resin (imported pellets)",
              "Processing additives (slip, anti-block, anti-static)",
              "Masterbatch (colour — 2–5%)",
              "Energy (extruder screw, take-off nip, winding drive)"
            ],
            technology: [
              "Blown film extruder (mono or multilayer — typically 55–90mm die)",
              "Air ring (nip film cooling — frost line height control)",
              "Corona treater (dyne level > 38 mN/m for ink adhesion)",
              "Wind-up (centre or surface winder)"
            ],
            skills: [
              "Extrusion Engineer — melt temperature, die gap and BUR for target gauge (12–50 µm)",
              "Materials Technician — resin lot management, MFI measurement and blending ratio",
              "Quality Inspector — gauge uniformity (dart drop, puncture, tensile per ASTM D1709)"
            ]
          },
          {
            id: "pl_bag_raw",
            stage: "Raw Materials (Imported)",
            label: "Resin & Additives",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "HDPE resin (blow moulding / film)", detail: "Imported — HS 3901.10. 100% imported. Uganda's 41 bag manufacturers process all from imported resin." },
              { name: "LDPE / LLDPE resin", detail: "Imported — HS 3901.20 / 3901.10. All film-grade PE imported; Kabalega park future target." },
              { name: "Masterbatch / colorant", detail: "Partly domestic — HS 3206. Some masterbatch compounding locally; pigment concentrates imported." }
            ]
          }
        ]
      }
    ]
  },

  "pl_house": {
    id: "pl_house",
    name: "Household Plasticware",
    category: "Moulded Products",
    tier: "Phase II — Conversion (Strong)",
    color: "#2563eb",
    description: "Injection-moulded household items: buckets, basins, cups, plates, storage containers. Strong domestic production — Nice House of Plastics, Nile Plastics and many others serve Uganda and EAC export markets.",
    legend: [
      { color: "#2563eb", label: "Household plasticware chain" },
      { color: "#1e3a8a", label: "PP/HDPE resin (imported)" },
    ],
    chains: [
      {
        title: "Injection Moulding Chain",
        accent: "#2563eb",
        nodes: [
          {
            id: "pl_house_top",
            stage: "Finished Product",
            label: "Bucket / Basin / Container",
            color: "#2563eb",
            textColor: "#ffffff",
            inputs: [
              "PP resin (homopolymer or copolymer — general-purpose moulding; imported)",
              "HDPE resin (for buckets and jerrycans — imported)",
              "Colorant masterbatch (imported concentrate at 1–3%)",
              "Recycled plastic regrind (internal returns — mixed into base resin < 10%)",
              "Energy (clamping unit and screw hydraulics of injection moulding machine)"
            ],
            technology: [
              "Injection moulding machine (50–1,000 tonne clamping force — depending on part size)",
              "Hot runner / cold runner mould (multi-cavity for small parts, single cavity for buckets)",
              "Automated pick-and-place robot (part extraction and stacking)",
              "Gate trimming / de-flashing station",
              "Ultrasonic welding (lid-body assembly where needed)"
            ],
            skills: [
              "Injection Moulding Technician — shot size, cushion, injection pressure and hold time",
              "Mould Designer / Tool Room — EDM machining, polishing and repair of steel moulds",
              "Colourist — masterbatch let-down ratio for consistent colour batch-to-batch",
              "Quality Inspector — dimensional check, drop test, wall thickness and UV resistance",
              "Production Supervisor — machine OEE, material consumption tracking and cycle time audit"
            ]
          },
          {
            id: "pl_house_raw",
            stage: "Raw Materials (Imported)",
            label: "Resin & Masterbatch",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "PP resin (injection grade)", detail: "Imported — HS 3902.10. All PP imported. Nice House of Plastics and others process ~10,000–30,000 t/yr collectively." },
              { name: "HDPE resin (blow moulding)", detail: "Imported — HS 3901.10. All HDPE for jerrycans and drums imported from Middle East, India." },
              { name: "Recycled plastic regrind", detail: "Domestic — HS 3915. Some internal regrind; ~600 t/day waste generated in Uganda but < 40% formally collected." }
            ]
          }
        ]
      }
    ]
  },

  "pl_flexible": {
    id: "pl_flexible",
    name: "Flexible Laminates & Pouches",
    category: "Flexible Packaging",
    tier: "Phase II — Conversion",
    color: "#3b82f6",
    description: "Multi-layer flexible laminates, stand-up pouches and sachets for food and personal care. Domestic production established for some grades. Key input: aluminium foil imported; plastic layers partly domestic.",
    legend: [
      { color: "#3b82f6", label: "Flexible laminate chain" },
      { color: "#1e3a8a", label: "Foil & film (partly imported)" },
    ],
    chains: [
      {
        title: "Flexible Laminate Production Chain",
        accent: "#3b82f6",
        nodes: [
          {
            id: "pl_flex_top",
            stage: "Finished Product",
            label: "Flexible Pouch / Laminate",
            color: "#3b82f6",
            textColor: "#ffffff",
            inputs: [
              "BOPP / PET film (outer print layer — imported or partly domestic)",
              "Aluminium foil (barrier layer — imported; no domestic foil production)",
              "CPP / PE film (heat-seal layer — partly domestic blown film)",
              "Solvent or water-based adhesive (lamination bond; imported)",
              "Printing inks (flexographic or gravure — imported)"
            ],
            technology: [
              "Flexographic / gravure printing press (up to 10 colours)",
              "Dry laminator (adhesive coating + nip + curing oven)",
              "Solventless laminator (2-part PUR adhesive — faster and cleaner)",
              "Slitter / rewinder (trim to finished width)",
              "Pouch making machine (4-side seal, stand-up, zip or spout)"
            ],
            skills: [
              "Print Technician — plate mounting, ink viscosity control, colour density and register",
              "Lamination Technician — adhesive coat weight, nip pressure and bond strength (Newton/15mm)",
              "Pouch Making Operator — seal temperature, dwell and pressure for hermetic seals",
              "Quality Engineer — OTR, WVTR (barrier testing), seal integrity and migration compliance",
              "Regulatory Officer — food contact material compliance (EU 10/2011, or Uganda UNBS EAS 1)"
            ]
          },
          {
            id: "pl_flex_raw",
            stage: "Films & Foil (Inputs)",
            label: "Laminate Substrates",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Aluminium foil (barrier layer)", detail: "Imported — HS 7607.11. No domestic aluminium foil production in Uganda. All foil imported from Kenya/India/China." },
              { name: "BOPP film (print layer)", detail: "Imported — HS 3920.20. Biaxially oriented PP film imported; no domestic BOPP capacity." },
              { name: "PE film (heat-seal layer)", detail: "Partly domestic — HS 3920.10. LDPE blown film produced domestically; LLDPE imported." }
            ]
          }
        ]
      }
    ]
  }
};

const CATEGORIES = [
  { name: "Rigid Packaging", color: "#1e3a8a", products: ["pl_bottles"] },
  { name: "Construction Plastics", color: "#1e40af", products: ["pl_pipes"] },
  { name: "Flexible Packaging", color: "#1d4ed8", products: ["pl_bags", "pl_flexible"] },
  { name: "Moulded Products", color: "#2563eb", products: ["pl_house"] }
];

const TRADE_HS4 = {
  "3923": {
    desc: "HS 3923 — articles for conveyance or packing of goods (bottles, bags, boxes).",
    year: 2024, imports: { uganda: 18200.0, eac: 2400.0 }, exports: { uganda: 12600.0, eac: 11800.0 }
  },
  "3917": {
    desc: "HS 3917 — tubes, pipes and hoses and fittings of plastics.",
    year: 2024, imports: { uganda: 14800.0, eac: 1600.0 }, exports: { uganda: 8400.0, eac: 7800.0 }
  },
  "3921": {
    desc: "HS 3921 — other plates, sheets, film, foil of plastics (laminates).",
    year: 2024, imports: { uganda: 8600.0, eac: 1200.0 }, exports: { uganda: 4200.0, eac: 3800.0 }
  },
  "3920": {
    desc: "HS 3920 — other plates, sheets, film of plastics (non-cellular; not reinforced).",
    year: 2024, imports: { uganda: 12400.0, eac: 1800.0 }, exports: { uganda: 6200.0, eac: 5600.0 }
  },
  "3924": {
    desc: "HS 3924 — tableware, kitchenware, other household articles of plastics.",
    year: 2024, imports: { uganda: 9800.0, eac: 1400.0 }, exports: { uganda: 7200.0, eac: 6600.0 }
  },
  "3901": {
    desc: "HS 3901 — polymers of ethylene (HDPE, LDPE, LLDPE). 100% imported.",
    year: 2024, imports: { uganda: 38000.0, eac: 1200.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "3902": {
    desc: "HS 3902 — polymers of propylene (PP). 100% imported.",
    year: 2024, imports: { uganda: 22000.0, eac: 400.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const PRODUCT_HS4 = {
  "pl_bottles":  "3923",
  "pl_pipes":    "3917",
  "pl_bags":     "3923",
  "pl_house":    "3924",
  "pl_flexible": "3921"
};

const RAW_MATERIAL_TRADE = {
  "PET resin pellets (bottle grade)": {
    desc: "HS 3907.61 — poly(ethylene terephthalate), primary forms. 100% imported.",
    year: 2024, imports: { uganda: 22000.0, eac: 800.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "HDPE resin (blow moulding / film)": {
    desc: "HS 3901.10 — polyethylene (HDPE, density ≥ 0.94). 100% imported.",
    year: 2024, imports: { uganda: 20000.0, eac: 600.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "PVC resin (K-67)": {
    desc: "HS 3904.10 — poly(vinyl chloride), not mixed with other substances. 100% imported.",
    year: 2024, imports: { uganda: 12000.0, eac: 400.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Aluminium foil (barrier layer)": {
    desc: "HS 7607.11 — aluminium foil (≤ 0.2 mm). No domestic production; all imported.",
    year: 2024, imports: { uganda: 8200.0, eac: 600.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Recycled plastic regrind": {
    desc: "HS 3915 — waste, parings and scrap of plastics. ~600 t/day waste; < 40% formally collected.",
    year: 2024, imports: { uganda: 200.0, eac: 100.0 }, exports: { uganda: 400.0, eac: 300.0 }
  }
};

const RAW_MATERIAL_PHASE = {
  "HDPE resin (blow moulding / film)": "pl_II",
  "PVC resin (K-67)": "pl_II",
  "PET resin pellets (bottle grade)": "pl_II"
};

const PHASE_PRODUCERS = {
  "pl_II": {
    count: 41,
    label: "Phase II–III — Plastics Conversion (UNBS-certified firms)",
    examples: [
      "Nice House of Plastics (largest domestic plastics converter)",
      "Nile Plastics Ltd",
      "Roofings Ltd (PVC pipes division)",
      "Crown Beverages / BIDCO (in-house bottle blowing)",
      "38 other UNBS-certified plastics manufacturers"
    ]
  }
};

const PHASE_SOURCE = "MTIC Diagnostic Study on Plastics & Packaging (Report 2, 2026); UNBS certified firms register";

const PRODUCT_FIRMS = {
  "pl_bottles": {
    status: "named",
    firms: ["Crown Beverages (in-house bottle blowing)", "Century Bottling (Coca-Cola Uganda)", "Numerous independent preform/bottle producers"],
    note: "KEY GAP: All PET resin imported (~150,000 t/yr total plastics resin). Kabalega park domestic resin target ~2029. Uganda exports USD 12.6m plastic bottles/containers/yr to EAC."
  },
  "pl_pipes": {
    status: "named",
    firms: ["Roofings Ltd (PVC pipes division)", "KGAL", "Others (UNBS certified)"],
    note: "Strong domestic pipe production. Uganda exports USD 8.4m plastic pipes/yr (EAC market). All PVC and HDPE resin imported."
  },
  "pl_bags": {
    status: "named",
    firms: ["41 UNBS-certified manufacturers (full list in MTIC register)"],
    note: "Largest number of certified firms in plastics sector. Bag tax (2009) raised regulatory bar; remaining producers are largely compliant. All resin imported."
  },
  "pl_house": {
    status: "named",
    firms: ["Nice House of Plastics", "Nile Plastics Ltd", "Other UNBS-certified moulders"],
    note: "Strong domestic production for household items. Uganda exports USD 7.2m/yr plasticware to EAC. All resin imported."
  },
  "pl_flexible": {
    status: "named",
    firms: ["Several domestic flexible packaging producers (MTIC register)"],
    note: "Flexible laminates and pouches — established domestic production for food and FMCG. Aluminium foil and BOPP imported; PE layers partly domestic."
  }
};

const INPUT_KEYWORD_HS4 = [
  { pattern: /\bPET resin\b|\bPET.*pellets?\b/i, hs4: "3923" },
  { pattern: /\bHDPE resin\b|\bLDPE resin\b/i, hs4: "3901" },
  { pattern: /\bPP resin\b|\bpolypropylene.*pellets?\b/i, hs4: "3902" },
  { pattern: /\bPVC resin\b/i, hs4: "3904" },
  { pattern: /\baluminium foil\b/i, hs4: "7607" },
  { pattern: /\brecycled plastic\b|\bplastic.*regrind\b/i, hs4: "3915" },
];

const INPUT_KEYWORD_PHASE = [
  { pattern: /\bNice House\b|\bNile Plastics\b|\bROOFINGS.*PVC\b/i, phase: "pl_II" },
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
