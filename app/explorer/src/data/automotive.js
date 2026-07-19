// Automotive — Value Chain Explorer data
// Source: MTIC Diagnostic Study (Report 1); ITC TradeMap 2024; seed_all_chains.py STRENGTH data

const PRODUCTS = {
  "au_ev": {
    id: "au_ev",
    name: "Battery Electric Vehicle (BEV)",
    category: "Assembled Vehicles",
    tier: "Phase III — Assembly",
    color: "#065f46",
    description: "Fully electric passenger vehicle and bus. Uganda's primary vehicle assembly: KMC (Kiira Motors Corporation) Kayoola EV bus — commissioned Sept 2025, ~2,500 vehicles/yr capacity. Critical gap: Components (Phase II) are almost entirely imported; local content near zero.",
    legend: [
      { color: "#065f46", label: "EV assembly chain" },
      { color: "#047857", label: "Component sub-assembly" },
      { color: "#059669", label: "Materials & sub-systems" },
      { color: "#1e3a8a", label: "Raw materials (imported)" },
    ],
    chains: [
      {
        title: "KMC EV Assembly Chain",
        accent: "#065f46",
        nodes: [
          {
            id: "au_ev_top",
            stage: "Finished Vehicle",
            label: "EV Bus / Car",
            color: "#065f46",
            textColor: "#ffffff",
            inputs: [
              "Body-in-white (BIW) shell — steel stampings (CKD or locally fabricated)",
              "EV battery pack (lithium-ion modules + BMS — imported)",
              "Electric drive motor + inverter (imported sub-assembly)",
              "Chassis & suspension components (imported or local fabrication for buses)",
              "Interior trim, seats, glass, HVAC (mix of local and imported)",
              "Wiring harness (imported — no domestic harness assembly)"
            ],
            technology: [
              "Body-in-white welding jig (MIG/TIG, manual or semi-automated at KMC scale)",
              "Paint shop (surface preparation, primer, colour coat, clear coat)",
              "Powertrain integration line (motor, controller, reduction gearbox mounting)",
              "Battery pack installation bay (BMS commissioning, high-voltage safety checks)",
              "End-of-line test track (brake test, headlamp aim, HVAC, infotainment)",
              "Torque management system (steer-by-wire / drive-by-wire calibration for EV)"
            ],
            skills: [
              "Automotive Assembly Engineer — BIW build, fit-and-finish tolerance management & process sequencing",
              "EV Systems Engineer — battery pack integration, BMS commissioning & high-voltage safety protocols",
              "Electrical Engineer — vehicle architecture (HV/LV bus, CAN/LIN networks, OBC wiring)",
              "Quality Engineer — NVH assessment, squeak-and-rattle, corrosion test & homologation compliance",
              "Mechatronics Engineer — drive-by-wire, ADAS sensor calibration & OTA update management"
            ]
          },
          {
            id: "au_battery_pack",
            stage: "Battery Pack (Imported)",
            label: "EV Battery Pack",
            color: "#047857",
            textColor: "#ffffff",
            inputs: [
              "Lithium-ion cell modules (NMC or LFP chemistry — imported from China/Korea)",
              "Battery management system (BMS IC, cell balancing circuits)",
              "Pack housing (aluminium extrusion or sheet — structural enclosure)",
              "Thermal management system (cooling plates, coolant, TIM)",
              "High-voltage contactors, fuses & pre-charge circuit",
              "Energy (cell formation cycling at cell factory)"
            ],
            technology: [
              "Cell formation & grading (charge-discharge cycles to select matched cells)",
              "Module assembly (cell welding — laser or ultrasonic)",
              "Pack assembly line (module mounting, busbar connection, HV wiring)",
              "BMS software calibration (SoC estimation, thermal model, cell balancing algorithm)",
              "Environmental test chamber (temperature cycling, vibration, IP67 sealing)"
            ],
            skills: [
              "Battery Engineer — cell chemistry selection, pack architecture & energy density optimisation",
              "Electrical Engineer — BMS algorithm design, SoC/SoH estimation & safety (ISO 26262)",
              "Thermal Engineer — cooling system design (liquid, phase-change or air cooling per use case)",
              "Materials Engineer — cell electrode, separator & electrolyte compatibility review",
              "Quality Engineer — pack-level capacity, resistance & safety test per IEC 62660 / GB/T 38031"
            ]
          },
          {
            id: "au_chassis_body",
            stage: "Chassis & Body",
            label: "Body & Chassis",
            color: "#059669",
            textColor: "#ffffff",
            dual: true,
            routeA: {
              label: "Bus Body Building (Local)",
              inputs: [
                "Steel tube/section (domestic supply from Roofings, Steel & Tube)",
                "Mild steel sheet (imported flat steel — domestic narrow-strip only)",
                "Fibreglass / GRP panels (body cladding — imported or local moulding)",
                "Glazing (tempered safety glass — imported)",
                "Seat frames and upholstery (domestic foam; imported fabric)"
              ],
              technology: [
                "MIG/TIG welding frame jig (bus body frame)",
                "CNC plasma cutter (steel tube / sheet cutting)",
                "GRP laminating table (body panel moulding)",
                "Spray paint booth (primer + topcoat)",
                "Seat trim workshop"
              ],
              skills: [
                "Bodybuilder Engineer — structural frame design, weld sequence & torsional stiffness",
                "Welder (Certified) — MIG/TIG structural tube welding (AWS D1.1)",
                "GRP Laminator — hand lay-up, infusion or press moulding of body panels",
                "Trim Technician — seat, headliner, flooring and glazing installation",
                "Inspector — dimensional check, weld visual inspection & paint adhesion test"
              ]
            },
            routeB: {
              label: "CKD/SKD Kit Assembly (Imported Shell)",
              inputs: [
                "CKD body stampings (imported — door, roof, floor panels)",
                "Structural chassis frame (imported semi-knocked-down)",
                "Suspension components (imported — struts, arms, springs)",
                "Steering system (imported — EPS or hydraulic)",
                "Brake system (imported — discs, calipers, ABS unit)"
              ],
              technology: [
                "CKD assembly jig (locating fixtures for panel alignment)",
                "MIG spot weld gun (panel joining at KMC scale)",
                "Wheel alignment / geometry rig",
                "Brake bleed and ABS test bench",
                "HVAC evacuation and charge station"
              ],
              skills: [
                "CKD Assembly Technician — panel alignment, fastener torque & sealant application",
                "Chassis Technician — suspension geometry, wheel bearing preload & alignment",
                "Brake Technician — hydraulic line routing, bleed & ABS diagnostic",
                "Paint Technician — cavity wax, underbody coating & cosmetic touch-up",
                "Quality Inspector — gap-and-flush, water-leak test & road test sign-off"
              ]
            }
          },
          {
            id: "au_ev_raw",
            stage: "Raw Materials",
            label: "EV Components & Materials",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Lithium-ion battery cells", detail: "Imported — HS 8507.60. No domestic cell production. All Li-ion cells for KMC EV imported from China/Korea. USD 34m EV battery imports." },
              { name: "Electric drive motor + inverter", detail: "Imported — HS 8501.32 / 8537. Electric traction motors and power electronics entirely imported; no domestic production." },
              { name: "Automotive steel (flat)", detail: "Imported — HS 7208. Wide-strip flat steel absent in Uganda (domestic: narrow-strip only). Panels mostly from CKD kits." },
              { name: "Wiring harness", detail: "Imported — HS 8544.30. All wiring harnesses imported; no domestic harness assembly (cable exists but sub-assembly absent)." },
              { name: "Semiconductors / ECUs", detail: "Imported — HS 8542. All electronics imported; no domestic chip or ECU production." }
            ]
          }
        ]
      }
    ]
  },

  "au_motorcycle": {
    id: "au_motorcycle",
    name: "Motorcycle (Boda-Boda)",
    category: "Assembled Vehicles",
    tier: "Phase III — CKD Assembly",
    color: "#047857",
    description: "Two-wheeler motorcycle (100–200cc) for the boda-boda market. Uganda's largest vehicle sub-sector by unit volume. CKD assembly from imported kits — engines, frames and tyres all imported. USD 157m annual motorcycle import opportunity.",
    legend: [
      { color: "#047857", label: "Motorcycle assembly chain" },
      { color: "#1e3a8a", label: "CKD components (imported)" },
    ],
    chains: [
      {
        title: "CKD Motorcycle Assembly",
        accent: "#047857",
        nodes: [
          {
            id: "au_moto_top",
            stage: "Finished Product",
            label: "Assembled Motorcycle",
            color: "#047857",
            textColor: "#ffffff",
            inputs: [
              "CKD engine assembly (100–125cc 4-stroke — imported from China/India)",
              "Frame + fork assembly (imported steel tube frame — CKD)",
              "Fuel tank + bodywork (imported plastic / steel panels)",
              "Tyres and tubes (imported — no domestic tyre mfg in Uganda)",
              "Wiring harness + instruments (imported)",
              "Battery (lead-acid — some locally assembled)"
            ],
            technology: [
              "Engine assembly station (torque-to-specification, crank case joining)",
              "Frame alignment jig (wheel & steering alignment)",
              "Electrical assembly station (harness routing, connector sealing)",
              "Fuel system assembly (carburettor / FI calibration, tank sealing)",
              "End-of-line test dyno (idle, throttle response, brake test)"
            ],
            skills: [
              "Motorcycle Assembly Technician — engine build, component fitment & torque checks",
              "Electrical Technician — wiring harness routing, earthing & instrument calibration",
              "QC Inspector — dimensional check, torque verification & road-test sign-off",
              "Workshop Manager — production throughput, CKD inventory & supplier liaison",
              "After-sales Technician — warranty repair, spare-parts sourcing & service manual compliance"
            ]
          },
          {
            id: "au_moto_raw",
            stage: "CKD Components (Imported)",
            label: "Motorcycle CKD Kit",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Engine assembly (CKD)", detail: "Imported — HS 8407. All motorcycle engines imported. No domestic engine production. China and India are dominant suppliers." },
              { name: "Steel frame + suspension forks", detail: "Imported — HS 8714. All frames and suspension assemblies imported; local weld-up of bus/truck bodies exists but not motorcycle frames." },
              { name: "Tyres and tubes", detail: "Imported — HS 4011. No tyre manufacturing in Uganda. All tyres imported." },
              { name: "Wiring harness", detail: "Imported — HS 8544.30. Complete wiring sub-systems imported with CKD kits." }
            ]
          }
        ]
      }
    ]
  },

  "au_trailer": {
    id: "au_trailer",
    name: "Trailer & Semi-Trailer",
    category: "Fabricated Vehicles",
    tier: "Phase III — Body Building (Strong)",
    color: "#1e3a8a",
    description: "Towed goods-carrying trailer and semi-trailer. Uganda's strongest vehicle manufacturing capability — Kampala and Jinja body builders actively produce trailers and truck bodies from domestic steel.",
    legend: [
      { color: "#1e3a8a", label: "Trailer fabrication chain" },
      { color: "#1e40af", label: "Sub-assembly" },
      { color: "#1d4ed8", label: "Steel and materials" },
    ],
    chains: [
      {
        title: "Trailer Fabrication Chain",
        accent: "#1e3a8a",
        nodes: [
          {
            id: "au_trailer_top",
            stage: "Finished Product",
            label: "Semi-Trailer / Trailer",
            color: "#1e3a8a",
            textColor: "#ffffff",
            inputs: [
              "Structural steel sections (I-beam, channel, tube — domestic supply from Steel & Tube, Roofings)",
              "Steel plate (6–10mm for floor and sides — domestic or imported)",
              "Axle assemblies (imported — no domestic axle production)",
              "Tyres and wheels (imported — no domestic tyre manufacturing)",
              "Air brake system (imported — Knorr-Bremse, Wabco)",
              "Electrics (LED lamps, ABS, trailer connector — partly imported)"
            ],
            technology: [
              "MIG/MAG structural welding (main chassis rail fabrication)",
              "CNC plasma / oxy-fuel cutter (plate and section cutting)",
              "Hydraulic press brake (panel bending)",
              "Sandblast chamber (surface preparation before priming)",
              "2-post vehicle lift (axle installation and geometry check)",
              "Prime + topcoat spray booth (corrosion protection)"
            ],
            skills: [
              "Structural Engineer — chassis beam design, payload capacity & ADR compliance (tare, GVM, GCVM)",
              "Coded Welder — structural MIG welding (AWS D1.1 or equivalent qualification)",
              "Fabricator / Fitter — assembly sequencing, jig use and dimensional check",
              "Auto-Electrician — trailer wiring, ABS wiring and 7-pin connector compliance",
              "Inspector — weld visual inspection, dimensional verification & brake test"
            ]
          },
          {
            id: "au_trailer_steel",
            stage: "Steel & Fabrication",
            label: "Steel Sub-Structures",
            color: "#1e40af",
            textColor: "#ffffff",
            inputs: [
              "Structural steel I-beam & channel (domestic supply — Steel & Tube Ltd, Jinja)",
              "Steel tube (RHS/SHS — domestic supply from Roofings, Steel & Tube)",
              "Steel plate (domestic narrow-gauge or imported wide plate)",
              "Welding consumables (MIG wire, electrodes — partly domestic)"
            ],
            technology: [
              "Angle iron / I-beam shear and saw (section cutting)",
              "MIG welding sets (sub-frame, cross-member and gusset fabrication)",
              "Drill press and tap (bolt holes for axle hangers)",
              "Grinding (weld dress and surface prep)"
            ],
            skills: [
              "Fabricator — steel marking, cutting, fitting and tack welding",
              "Welder — structural MIG — fillet and butt welds",
              "Quality Inspector — weld visual check and dimensional check against drawing"
            ]
          },
          {
            id: "au_trailer_raw",
            stage: "Materials",
            label: "Steel & Axle Inputs",
            color: "#1d4ed8",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Structural steel sections (I-beam, channel)", detail: "Domestic supply — HS 7216. Steel & Tube Ltd (Nakawa, Namanve) + Roofings produces structural sections. Uganda exported USD 6.6m HS 7216 in 2024." },
              { name: "Steel plate (6–10mm)", detail: "Partly domestic (narrow strip from Tembo Steel, Roofings), partly imported wide plate. HS 7208 imports USD 42m (2024)." },
              { name: "Axle assemblies", detail: "Imported — HS 8716.90. No domestic axle production. Imported from India, China, Germany (BPW, SAF-Holland)." },
              { name: "Tyres and wheels", detail: "Imported — HS 4011. All tyres imported; no tyre plant in Uganda." }
            ]
          }
        ]
      }
    ]
  },

  "au_bus": {
    id: "au_bus",
    name: "Bus & Coach",
    category: "Assembled Vehicles",
    tier: "Phase III — Body Building",
    color: "#059669",
    description: "Public passenger bus and intercity coach. KMC (Kayoola diesel/EV bus) + Kampala/Jinja body builders on imported chassis. Uganda builds bus bodies domestically on imported chassis frames.",
    legend: [
      { color: "#059669", label: "Bus assembly/body building" },
      { color: "#1e3a8a", label: "Chassis (imported)" },
    ],
    chains: [
      {
        title: "Bus Body Building Chain",
        accent: "#059669",
        nodes: [
          {
            id: "au_bus_top",
            stage: "Finished Product",
            label: "Bus / Coach",
            color: "#059669",
            textColor: "#ffffff",
            inputs: [
              "Bare chassis frame (imported — Yutong, Higer, Toyota Coaster, Ashok Leyland)",
              "Steel tube section (domestic — Roofings, Steel & Tube)",
              "Fibreglass / GRP body panels (locally moulded or imported)",
              "Seat sets and upholstery (partly domestic foam; imported fabric)",
              "Glazing (tempered safety glass — imported)",
              "Interior lining (melamine board, vinyl flooring)"
            ],
            technology: [
              "Chassis-mounted body frame jig (MIG/TIG welding of body structure onto chassis)",
              "CNC plasma cutter (floor/wall panel cutting)",
              "GRP hand lay-up / vacuum infusion (exterior body panels)",
              "Seat trim workshop (foam cutting, upholstery, seat rail installation)",
              "Spray paint booth (exterior finish)"
            ],
            skills: [
              "Body Builder Engineer — structural frame design, roll-over (ECE R66) & door load compliance",
              "MIG/TIG Welder — body frame structural welding",
              "GRP Laminator — body panel moulding and repair",
              "Trim Technician — seating, grab-rails, headliner and flooring",
              "Inspector — commissioning check, seatbelt anchor test & road test"
            ]
          },
          {
            id: "au_bus_raw",
            stage: "Chassis & Components (Imported)",
            label: "Chassis & Systems",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Bus chassis (bare or cowl)", detail: "Imported — HS 8706. All bus chassis imported (Yutong, Tata, Ashok Leyland, Toyota). KMC builds its own EV chassis." },
              { name: "Diesel or EV powertrain", detail: "Imported — HS 8408 / 8501.32. Engines and drive motors for buses all imported." },
              { name: "Safety glazing", detail: "Imported — HS 7007. All automotive safety glass imported; no float glass in Uganda." }
            ]
          }
        ]
      }
    ]
  },

  "au_parts": {
    id: "au_parts",
    name: "Auto Components & Spares",
    category: "Aftermarket & Parts",
    tier: "Phase V — Aftermarket (Strong)",
    color: "#7c3aed",
    description: "Automotive aftermarket components and spares. Uganda's most active vehicle-related sector — Ndeeba and Kisekka markets service a large fleet. Parts largely imported but reconditioning, welding repair and fabrication very active.",
    legend: [
      { color: "#7c3aed", label: "Aftermarket / reconditioning" },
      { color: "#1e3a8a", label: "Parts (imported)" },
    ],
    chains: [
      {
        title: "Aftermarket Parts Chain",
        accent: "#7c3aed",
        nodes: [
          {
            id: "au_parts_top",
            stage: "Aftermarket Service",
            label: "Parts & Reconditioning",
            color: "#7c3aed",
            textColor: "#ffffff",
            inputs: [
              "Imported replacement parts (engines, gearboxes, bearings, filters, seals)",
              "Reconditioned / rebuilt units (locally re-machined gearboxes, alternators, starters)",
              "Sheet metal repair materials (domestic mild steel plate, MIG wire)",
              "Paint (domestic production — Crown, Sadolin, Nile Paints)",
              "Rubber seals and gaskets (imported)"
            ],
            technology: [
              "Lathe and boring machine (cylinder re-boring, crankshaft re-grinding)",
              "Engine test stand (rebuilt engine run-in and diagnostic)",
              "MIG/TIG welding (crash repair and chassis straightening)",
              "Frame jig / body-straightening bench",
              "Wheel balancing and tyre fitting machine"
            ],
            skills: [
              "Auto Mechanic / Technician — engine overhaul, gearbox rebuild & driveline diagnosis",
              "Panel Beater — collision repair, metal shaping & spot weld repair",
              "Auto-Electrician — ECU diagnostic, wiring repair & sensor replacement",
              "CNC Machinist — cylinder boring, valve seat cutting & crankshaft grinding",
              "Parts Sourcing Specialist — fitment verification across makes/models & OEM vs. aftermarket quality assessment"
            ]
          },
          {
            id: "au_parts_raw",
            stage: "Parts Supply (Imported)",
            label: "Auto Parts Imports",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Auto parts & accessories (HS 8708)", detail: "Imported — HS 8708. USD 31.7m auto parts imports (2024). Ndeeba/Kisekka markets distribute imported parts across Uganda and EAC." },
              { name: "Tyres and tubes", detail: "Imported — HS 4011. No domestic tyre production. Large fleet creates enormous tyre demand." },
              { name: "Automotive batteries", detail: "Some lead-acid battery assembly locally; Li-ion all imported. HS 8507." }
            ]
          }
        ]
      }
    ]
  }
};

const CATEGORIES = [
  { name: "Assembled Vehicles", color: "#065f46", products: ["au_ev", "au_motorcycle", "au_bus"] },
  { name: "Fabricated Vehicles", color: "#1e3a8a", products: ["au_trailer"] },
  { name: "Aftermarket & Parts", color: "#7c3aed", products: ["au_parts"] }
];

const TRADE_HS4 = {
  "8703": {
    desc: "HS 8703 — motor cars and other vehicles for persons (incl. EVs)",
    year: 2024, imports: { uganda: 182000.0, eac: 8000.0 }, exports: { uganda: 1200.0, eac: 900.0 }
  },
  "8711": {
    desc: "HS 8711 — motorcycles",
    year: 2024, imports: { uganda: 157000.0, eac: 4000.0 }, exports: { uganda: 3200.0, eac: 2800.0 }
  },
  "8716": {
    desc: "HS 8716 — trailers and semi-trailers",
    year: 2024, imports: { uganda: 8400.0, eac: 1200.0 }, exports: { uganda: 2800.0, eac: 2600.0 }
  },
  "8702": {
    desc: "HS 8702 — motor vehicles for 10 or more persons (buses and coaches)",
    year: 2024, imports: { uganda: 18600.0, eac: 800.0 }, exports: { uganda: 400.0, eac: 350.0 }
  },
  "8708": {
    desc: "HS 8708 — parts and accessories of motor vehicles",
    year: 2024, imports: { uganda: 31700.0, eac: 2400.0 }, exports: { uganda: 800.0, eac: 700.0 }
  },
  "8507": {
    desc: "HS 8507 — electric accumulators (EV and starter batteries)",
    year: 2024, imports: { uganda: 22000.0, eac: 1400.0 }, exports: { uganda: 600.0, eac: 500.0 }
  }
};

const PRODUCT_HS4 = {
  "au_ev":         "8703",
  "au_motorcycle": "8711",
  "au_trailer":    "8716",
  "au_bus":        "8702",
  "au_parts":      "8708"
};

const RAW_MATERIAL_TRADE = {
  "Lithium-ion battery cells": {
    desc: "HS 8507.60 — lithium-ion accumulators. All cells for KMC EV imported from China/Korea.",
    year: 2024, imports: { uganda: 8400.0, eac: 200.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Automotive steel (flat)": {
    desc: "HS 7208 — flat-rolled steel (wide strip). Body panels all imported. No wide-strip mill in Uganda.",
    year: 2024, imports: { uganda: 42000.0, eac: 3000.0 }, exports: { uganda: 200.0, eac: 100.0 }
  },
  "Structural steel sections (I-beam, channel)": {
    desc: "HS 7216 — angles, shapes and sections of iron/steel. Domestic supply active (Steel & Tube, Roofings).",
    year: 2024, imports: { uganda: 3200.0, eac: 600.0 }, exports: { uganda: 6600.0, eac: 5800.0 }
  },
  "Tyres and tubes": {
    desc: "HS 4011 — new pneumatic tyres. No tyre manufacturing in Uganda. All imported.",
    year: 2024, imports: { uganda: 38000.0, eac: 2800.0 }, exports: { uganda: 1200.0, eac: 900.0 }
  }
};

const RAW_MATERIAL_PHASE = {};

const PHASE_PRODUCERS = {
  "au_III": {
    count: 3,
    label: "Phase III — Vehicle Assembly (EV bus, CKD motorcycle, body building)",
    examples: [
      "KMC (Kiira Motors Corporation) — Kayoola EV bus, Namanve",
      "Several CKD motorcycle assemblers (boda-boda market)",
      "Kampala & Jinja body builders (bus bodies, trailers, truck bodies)"
    ]
  },
  "au_V": {
    count: null,
    label: "Phase V — Aftermarket & Distribution (active)",
    examples: [
      "Ndeeba market (Kampala) — auto parts retail & reconditioning",
      "Kisekka market (Kampala) — second-hand parts distribution",
      "Numerous small auto garages and reconditioning workshops"
    ]
  }
};

const PHASE_SOURCE = "MTIC Diagnostic Study on Iron & Steel, Copper & Automotive (Report 1, 2026)";

const PRODUCT_FIRMS = {
  "au_ev": {
    status: "named",
    firms: ["Kiira Motors Corporation (KMC) — Kayoola EV bus, commissioned Sept 2025, ~2,500 veh/yr capacity"],
    note: "KEY GAP: Components (Phase II) absent — local content almost zero. USD 31.7m parts imports. 2040 target: KMC 10,000 veh/yr; regional EV-bus supplier."
  },
  "au_motorcycle": {
    status: "emerging",
    firms: ["Several CKD motorcycle assemblers (names not disclosed in MTIC source register)"],
    note: "CKD assembly active but components all imported. USD 157m motorcycle import opportunity. No domestic engine, frame or tyre production."
  },
  "au_trailer": {
    status: "named",
    firms: ["Multiple body builders in Kampala (Nalukolongo) and Jinja"],
    note: "Uganda's strongest vehicle manufacturing capability. Domestic steel from Steel & Tube and Roofings used in trailer fabrication."
  },
  "au_bus": {
    status: "named",
    firms: [
      "KMC (Kiira Motors Corporation) — Kayoola EV bus",
      "Kampala body builders — bus bodies on imported chassis"
    ],
    note: "Bus body building active on imported chassis. KMC the only manufacturer of a full vehicle including chassis (EV route)."
  },
  "au_parts": {
    status: "named",
    firms: ["Ndeeba market (Kampala)", "Kisekka market (Kampala)", "Numerous auto garages and reconditioning shops"],
    note: "Large import-based aftermarket. Reconditioning (engine rebuilding, panel repair) very active. USD 31.7m HS 8708 parts imports (2024)."
  }
};

const INPUT_KEYWORD_HS4 = [
  { pattern: /\bEV battery\b|\blithium.ion\b|\bBMS\b/i, hs4: "8507" },
  { pattern: /\bauto parts\b|\bspare parts\b|\breplacement parts\b/i, hs4: "8708" },
  { pattern: /\btyres?\b|\btires?\b|\btubes?\b.*\btyre\b/i, hs4: "4011" },
  { pattern: /\bwiring harness\b/i, hs4: "8544" },
  { pattern: /\bautomotive steel\b|\bflat steel\b.*\bcar\b|\bsteel plate\b|\bmild steel sheet\b/i, hs4: "7208" },
  { pattern: /\bstructural steel section\b|\bI-beam\b|\bsteel.*section\b|\bsteel tube.*section\b/i, hs4: "7216" },
  { pattern: /\bCKD engine\b|\bIC engine\b|\bpiston engine\b|\bspark.ignition engine\b/i, hs4: "8407" },
  { pattern: /\bchassis frame\b|\bbare chassis\b|\bCKD.*chassis\b/i, hs4: "8706" },
  { pattern: /\bframe.*fork\b|\bmotorcycle.*frame\b|\bframe.*motorcycle\b|\bCKD.*frame\b/i, hs4: "8714" },
  { pattern: /\bsafety glass\b|\btempered.*glass\b|\blaminated glass\b|\bglaz/i, hs4: "7007" },
  { pattern: /\bGRP panel\b|\bfibreglass.*panel\b|\bglass.*fibre\b|\bfibre.*glass\b/i, hs4: "7019" },
  { pattern: /\btraction motor\b|\belectric.*drive motor\b|\bEV.*motor\b/i, hs4: "8501" },
  { pattern: /\brubber seals?\b|\bgaskets?\b|\brubber.*gasket\b|\banti.vibration\b/i, hs4: "4016" },
  { pattern: /\bpaint\b|\bcoating\b.*\bvehicle\b|\bvehicle.*\bcoat/i, hs4: "3208" },
  { pattern: /\bwelding consumables?\b|\bMIG wire\b|\bweld.*electrode\b/i, hs4: "8311" },
];

const INPUT_KEYWORD_PHASE = [
  { pattern: /\bCKD engine\b|\bengine assembly.*imported\b/i, phase: "au_III" },
  { pattern: /\bKMC\b|\bKayoola\b/i, phase: "au_III" },
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
