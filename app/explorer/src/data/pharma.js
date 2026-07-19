// Pharmaceuticals — Value Chain Explorer data
// Source: MTIC Diagnostic Study (Report 2); ITC TradeMap 2024; seed_all_chains.py STRENGTH data

const PRODUCTS = {
  "ph_arv": {
    id: "ph_arv",
    name: "Antiretrovirals (ARVs)",
    category: "Essential Medicines",
    tier: "Phase II — Formulation (Strong)",
    color: "#134e4a",
    description: "HIV/AIDS treatment regimens (tenofovir, lamivudine, efavirenz combinations). Uganda's pharmaceutical flagship — QCIL (Quality Chemicals Industries Ltd) is sub-Saharan Africa's largest ARV manufacturer; WHO/PEPFAR prequalified. Revenue: UGX 267bn. KEY GAP: APIs (Phase I) near-totally imported from India.",
    legend: [
      { color: "#134e4a", label: "ARV / formulation chain" },
      { color: "#0d9488", label: "Formulated blend" },
      { color: "#14b8a6", label: "API & intermediates" },
      { color: "#1e3a8a", label: "Raw materials (imported)" },
    ],
    chains: [
      {
        title: "ARV Manufacturing Chain",
        accent: "#134e4a",
        nodes: [
          {
            id: "ph_arv_top",
            stage: "Finished Product",
            label: "ARV Tablets / Capsules",
            color: "#134e4a",
            textColor: "#ffffff",
            inputs: [
              "Tenofovir disoproxil fumarate API (TDF — imported from India; core ARV)",
              "Lamivudine API (3TC — imported from India)",
              "Efavirenz API (EFV — imported from India; NNRTI component)",
              "Excipients (microcrystalline cellulose, croscarmellose sodium, magnesium stearate — imported)",
              "Film coat (polyvinyl alcohol, titanium dioxide, talc — for film-coated tablets)",
              "Primary packaging (blister foil + PVC, HDPE bottles — partly domestic)"
            ],
            technology: [
              "High-shear granulator (wet granulation — API + binder blending)",
              "Fluid bed dryer (granule moisture removal to specification)",
              "Tablet press (multi-station rotary compressor — ~200,000 tablets/hr)",
              "Film coating pan (aqueous polymer coat application)",
              "Blister packing machine (foil-foil or foil-PVC)",
              "In-process controls: hardness, friability, dissolution testing (USP/BP)"
            ],
            skills: [
              "Pharmaceutical Formulation Scientist — blend uniformity, tablet hardness/friability and dissolution profile",
              "QA/Validation Specialist — process validation (IQ/OQ/PQ), batch record review & CAPA management",
              "Regulatory Affairs Officer — WHO-GMP dossier (PQ submission), donor/tender compliance",
              "Production Pharmacist — batch release testing, specification deviation management",
              "API Procurement Specialist — supplier qualification (DMF filing), quality agreement & cold chain management"
            ]
          },
          {
            id: "ph_formulation",
            stage: "Formulation",
            label: "Formulated Blend",
            color: "#0d9488",
            textColor: "#ffffff",
            inputs: [
              "APIs (TDF, 3TC, EFV — weighed and dispensed in containment)",
              "Intra-granular excipients (binder: PVP K30; filler: MCC)",
              "Extra-granular excipients (disintegrant: croscarmellose; lubricant: Mg stearate)",
              "Purified water (granulation solvent — removed in drying)",
              "Energy (granulator, dryer, tablet press power)"
            ],
            technology: [
              "Dispensing booth (containment — Class D cleanroom minimum)",
              "Sifter (powder de-lumping before blending)",
              "V-blender / IBC blender (powder blend — lubrication step)",
              "In-process blend uniformity sampler (UV spectroscopy or HPLC method)",
              "Bin-to-press transfer (gravity or vacuum)"
            ],
            skills: [
              "Production Technician — blend operation, cleanroom gowning & batch record completion",
              "In-process QC Analyst — hardness, weight variation, disintegration tests per USP/BP",
              "Cleaning Validation Specialist — equipment cleaning procedure qualification",
              "Environmental Monitoring Officer — cleanroom particulate and microbial sampling"
            ]
          },
          {
            id: "ph_api_input",
            stage: "API (Imported)",
            label: "Active Pharmaceutical Ingredients",
            color: "#14b8a6",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Tenofovir disoproxil fumarate (TDF)", detail: "Imported — HS 2934.99. India dominant (58% of Uganda medicine imports). No API synthesis in Uganda; near-total import dependence is the deepest structural risk." },
              { name: "Lamivudine (3TC)", detail: "Imported — HS 2933.59. All HIV/AIDS APIs imported; QCIL and others solely formulators, not API manufacturers." },
              { name: "Efavirenz (EFV)", detail: "Imported — HS 2934.99. All ARV APIs from India and China; supply disruption risk." },
              { name: "Artemether + lumefantrine (ACT)", detail: "Imported — HS 2941.90. QCIL flagship antimalarial also uses entirely imported APIs." }
            ]
          }
        ]
      }
    ]
  },

  "ph_antimal": {
    id: "ph_antimal",
    name: "Antimalarials (ACT)",
    category: "Essential Medicines",
    tier: "Phase II — Formulation (Strong)",
    color: "#0d9488",
    description: "Artemisinin-combination therapy (ACT) — artemether/lumefantrine. QCIL produces ACTs for Uganda, EAC and PEPFAR/GFATM markets. WHO-GMP prequalified, PEPFAR-approved supply. APIs entirely imported from India/China.",
    legend: [
      { color: "#0d9488", label: "Antimalarial chain" },
      { color: "#1e3a8a", label: "APIs (imported)" },
    ],
    chains: [
      {
        title: "ACT Manufacturing Chain",
        accent: "#0d9488",
        nodes: [
          {
            id: "ph_acm_top",
            stage: "Finished Product",
            label: "ACT Tablets (Artemether/Lumefantrine)",
            color: "#0d9488",
            textColor: "#ffffff",
            inputs: [
              "Artemether API (semi-synthetic from artemisinin — imported from China/India)",
              "Lumefantrine API (imported from India or China)",
              "Excipients (castor oil, polysorbate 80, hypromellose)",
              "Film coat (opaque — light protection for photosensitive APIs)",
              "PVC/PVDC blister foil (imported packaging)"
            ],
            technology: [
              "High-shear granulator (lipid-based granulation for lumefantrine solubility enhancement)",
              "Rotary tablet press (bi-layer or standard compression)",
              "Film coating pan (HPMC-based opaque coat)",
              "Blister sealer (foil heat-seal)",
              "Dissolution tester (USP Apparatus 2 — critical for bioavailability compliance)"
            ],
            skills: [
              "Formulation Scientist — lipid dispersion for lumefantrine (BCS Class II bioavailability challenge)",
              "QA Pharmacist — batch release, specification setting & impurity control",
              "Regulatory Affairs — WHO prequalification maintenance & PEPFAR/GFATM dossier",
              "Analyst (HPLC) — API assay, related substances & dissolution per WHO/PQ methodology",
              "Cold Chain Manager — temperature excursion control for product stability (25°C/60% RH ICH Z1b)"
            ]
          },
          {
            id: "ph_acm_raw",
            stage: "APIs (Imported)",
            label: "Antimalarial APIs & Excipients",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Artemether API", detail: "Imported — HS 2941.90 / 2932.90. Semi-synthetic from artemisinin (Artemisia annua extract). China dominant supplier. Uganda could grow Artemisia — unexplored opportunity." },
              { name: "Lumefantrine API", detail: "Imported — HS 2934.99. Synthetic API; India and China are the global sources. No API synthesis in Uganda." },
              { name: "Castor oil (excipient)", detail: "Imported — HS 1515.30. Vegetable oil excipient for lumefantrine dispersion; Uganda grows castor but not pharma-grade processing." }
            ]
          }
        ]
      }
    ]
  },

  "ph_tablets": {
    id: "ph_tablets",
    name: "General Tablets & Capsules",
    category: "Solid Oral Dosage",
    tier: "Phase II — Formulation (Strong)",
    color: "#14b8a6",
    description: "Broad-spectrum tablets and capsules including antibiotics, analgesics and OTC medicines. QCIL capacity: 1.2 billion tablets/capsules/year. Multiple WHO-GMP aligned facilities (KPI, Rene and others). APIs 100% imported.",
    legend: [
      { color: "#14b8a6", label: "Tablet manufacturing chain" },
      { color: "#0d9488", label: "API blend" },
      { color: "#1e3a8a", label: "APIs (imported)" },
    ],
    chains: [
      {
        title: "Tablet Manufacturing Chain",
        accent: "#14b8a6",
        nodes: [
          {
            id: "ph_tab_top",
            stage: "Finished Product",
            label: "Tablets / Capsules",
            color: "#14b8a6",
            textColor: "#ffffff",
            inputs: [
              "Active Pharmaceutical Ingredient (API — imported from India/China)",
              "Microcrystalline cellulose (MCC — filler/binder; imported)",
              "Croscarmellose sodium (disintegrant; imported)",
              "Magnesium stearate (lubricant; imported)",
              "Film coating system (HPMC, TiO2, PEG — imported)",
              "Hard gelatin / HPMC capsule shells (imported)"
            ],
            technology: [
              "High-shear wet granulator (API blend + binder solution)",
              "Fluid bed dryer / coater (granule drying & pellet coating)",
              "Rotary tablet press (10–51 station — 100k–300k tablets/hr)",
              "Film coater (side-vented pan — aqueous coat)",
              "Capsule filling machine (hard gelatin / HPMC — plug or pellet fill)",
              "Strip and blister packing (PVC-foil or alu-alu blister sealing)"
            ],
            skills: [
              "Pharmaceutical Technologist — granulation end-point, tablet hardness & dissolution optimisation",
              "QA Manager — batch record review, non-conformance management & GMP audit readiness",
              "HPLC Analyst — API assay, dissolution testing & degradation product identification",
              "Validation Specialist — process, cleaning and analytical method validation per ICH Q2",
              "Packaging Engineer — blister sealing integrity, child-resistant closure & stability chamber management"
            ]
          },
          {
            id: "ph_blend",
            stage: "Formulated Blend",
            label: "API Blend",
            color: "#0d9488",
            textColor: "#ffffff",
            inputs: [
              "API (dispensed under containment — OEL <10 µg/m3 for potent compounds)",
              "Excipients (sieved and weighed — MCC, croscarmellose, Mg stearate)",
              "Purified water (WFI for aseptic processes or granulation water)"
            ],
            technology: [
              "Dispensing booth (Class D cleanroom — OEL-rated for potent API)",
              "IBC / V-blender (final blend — uniformity ≤ 3% CV)",
              "On-line NIR blend monitor (real-time blend uniformity endpoint)"
            ],
            skills: [
              "Production Operator — GMP gowning, batch record execution & environmental monitoring",
              "QC In-process Analyst — hardness, weight, disintegration and uniformity checks",
              "Containment Engineer — downflow booth maintenance, safe change filters & air-lock discipline"
            ]
          },
          {
            id: "ph_tab_raw",
            stage: "Raw Materials (Imported)",
            label: "APIs & Excipients",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Active Pharmaceutical Ingredient (API)", detail: "Imported — HS 2941.xx / 2933.xx / 2934.xx. Near-total import dependence; India 58% of Uganda medicine imports. No API synthesis in Uganda." },
              { name: "Microcrystalline cellulose (MCC)", detail: "Imported — HS 3912.12. Pharmaceutical-grade filler/binder. All imported from India/China (Avicel, Comcel)." },
              { name: "Film coat system (HPMC)", detail: "Imported — HS 3912.31. Complete film coat systems (Opadry) imported. No local pharma excipient production." },
              { name: "Primary packaging (blister foil, PVC)", detail: "Partly domestic — HS 7607 / 3920. PVC film partly domestic (plastics chain); aluminium foil imported." }
            ]
          }
        ]
      }
    ]
  },

  "ph_inject": {
    id: "ph_inject",
    name: "Injectables & Vials",
    category: "Sterile Medicines",
    tier: "Phase II — Formulation (Strong)",
    color: "#0f766e",
    description: "Sterile injectable medicines in vials and ampoules. QCIL aseptic filling line is WHO-GMP prequalified — one of the few aseptic fill facilities in East Africa. Fills imported API solutions into imported glass vials.",
    legend: [
      { color: "#0f766e", label: "Injectable manufacturing chain" },
      { color: "#1e3a8a", label: "APIs & vials (imported)" },
    ],
    chains: [
      {
        title: "Aseptic Injectable Chain",
        accent: "#0f766e",
        nodes: [
          {
            id: "ph_inj_top",
            stage: "Finished Product",
            label: "Sterile Injectable",
            color: "#0f766e",
            textColor: "#ffffff",
            inputs: [
              "Sterile API solution / bulk (imported or prepared in-house under aseptic conditions)",
              "Water for Injection (WFI — produced on-site by multi-effect distillation)",
              "Glass vials / ampoules (type I borosilicate glass — imported from Europe/India)",
              "Rubber stoppers + aluminium crimp seals (imported — siliconised stoppers)",
              "Nitrogen / inert gas (vial head-space purge — oxidation prevention)"
            ],
            technology: [
              "Multi-effect distiller / WFI generator (on-site ultrapure water production)",
              "Sterile filtration (0.22 µm membrane sterilisation of bulk solution)",
              "Aseptic filling machine (RABS or isolator-based — Class A in Class B background)",
              "Lyophiliser (freeze-dryer — for lyo products requiring reconstitution)",
              "Vial washer, tunnel steriliser (depyrogenation at 250°C / 30 min)",
              "Crimping machine + visual inspection station (AQL sampling)"
            ],
            skills: [
              "Aseptic Processing Engineer — RABS/isolator integrity, line clearance & media fill validation",
              "Sterility Assurance Specialist — environmental monitoring, bio-burden testing & sterility test",
              "WFI Systems Engineer — distiller operation, TOC and endotoxin monitoring",
              "QA Pharmacist — batch release, parametric release approval (if sterilisation data used)",
              "Regulatory Affairs Officer — WHO PQ maintenance for injectables, lyophilised dossier"
            ]
          },
          {
            id: "ph_inj_raw",
            stage: "Raw Materials (Imported)",
            label: "APIs, Vials & Excipients",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Sterile API bulk", detail: "Imported — HS 2941.xx. All APIs for injectables imported. No API synthesis or sterile API manufacturing in Uganda." },
              { name: "Type I borosilicate vials", detail: "Imported — HS 7010.10. All pharma-grade glass vials imported from India, Europe. Some glass locally available but not pharma grade." },
              { name: "Rubber closures (stoppers)", detail: "Imported — HS 4015. Siliconised chlorobutyl stoppers imported. No rubber closure manufacturing in Uganda." },
              { name: "Water for Injection (WFI)", detail: "On-site production — multi-effect distillation from municipal supply. QCIL and others produce own WFI." }
            ]
          }
        ]
      }
    ]
  },

  "ph_vaccine": {
    id: "ph_vaccine",
    name: "Vaccines & Biologics",
    category: "Biologics",
    tier: "Phase I — Production (Gap)",
    color: "#be185d",
    description: "Vaccines, biologics and immunological products. No vaccine production in Uganda — entirely imported. Long-term aspiration: mRNA or protein-subunit manufacturing with African CDC/CEPI support. Requires biosafety, cell culture and cold chain investment.",
    legend: [
      { color: "#be185d", label: "Vaccine manufacturing chain (gap)" },
      { color: "#1e3a8a", label: "All inputs (imported)" },
    ],
    chains: [
      {
        title: "Vaccine Manufacturing Chain",
        accent: "#be185d",
        nodes: [
          {
            id: "ph_vax_top",
            stage: "Finished Product (Gap)",
            label: "Vaccine / Biologic",
            color: "#be185d",
            textColor: "#ffffff",
            inputs: [
              "Drug substance (antigen / mRNA — produced in upstream bioprocess; all imported currently)",
              "Adjuvant system (alum, AS01, AS03 — imported)",
              "Stabilisers (sucrose, trehalose, glycine — excipients for lyophilisation)",
              "Multi-dose glass vials (type I — imported)",
              "Cold chain equipment (2–8°C refrigerators; −60/−80°C freezers for mRNA)"
            ],
            technology: [
              "Bioreactor (fed-batch or perfusion — cell culture or fermentation)",
              "Downstream purification (chromatography, UF/DF, depth filtration)",
              "Formulation / fill-finish (aseptic filling under RABS/isolator)",
              "Lyophiliser (freeze-drying for stability at ambient — future for Uganda)",
              "Cold chain monitoring system (temperature loggers, controlled temp facility)"
            ],
            skills: [
              "Bioprocess Engineer — cell culture optimisation, bioreactor control, yield and titre maximisation",
              "Downstream Process Scientist — protein purification, chromatography method development",
              "Regulatory Affairs (Biologics) — WHO PQ for vaccines, BLA equivalent submission",
              "Cold Chain Manager — temperature monitoring, excursion SOP, controlled temp room management",
              "Quality Control Scientist — potency assay, sterility, endotoxin, identity and stability testing"
            ]
          },
          {
            id: "ph_vax_raw",
            stage: "All Inputs (Imported / Gap)",
            label: "Vaccine Inputs",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Vaccine drug substance (antigen)", detail: "Imported — HS 3002.49. No vaccine antigen manufacturing in Uganda. Imported ready-to-fill or finished doses." },
              { name: "Cell culture media", detail: "Imported — HS 3821.00. All GMP-grade cell culture media imported from Thermo Fisher, Merck." },
              { name: "Single-use bioprocess consumables", detail: "Imported — HS 9018. Bags, tubing, filters for bioreactor and filling all imported." }
            ]
          }
        ]
      }
    ]
  }
};

const CATEGORIES = [
  { name: "Essential Medicines", color: "#134e4a", products: ["ph_arv", "ph_antimal"] },
  { name: "Solid Oral Dosage", color: "#14b8a6", products: ["ph_tablets"] },
  { name: "Sterile Medicines", color: "#0f766e", products: ["ph_inject"] },
  { name: "Biologics", color: "#be185d", products: ["ph_vaccine"] }
];

const TRADE_HS4 = {
  "3004": {
    desc: "HS 3004 — medicaments (mixed or unmixed products for therapeutic use), dosed. Uganda imports + exports both.",
    year: 2024, imports: { uganda: 188000.0, eac: 14000.0 }, exports: { uganda: 42000.0, eac: 36000.0 }
  },
  "2941": {
    desc: "HS 2941 — antibiotics. Key API class; QCIL produces antibiotics locally using imported APIs.",
    year: 2024, imports: { uganda: 8200.0, eac: 600.0 }, exports: { uganda: 400.0, eac: 300.0 }
  },
  "3002": {
    desc: "HS 3002 — human blood, vaccines, toxins (biological products). All vaccines imported.",
    year: 2024, imports: { uganda: 28000.0, eac: 2000.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "7010": {
    desc: "HS 7010 — glass vials, ampoules, bottles for pharma. All pharma glass imported.",
    year: 2024, imports: { uganda: 3200.0, eac: 400.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "9018": {
    desc: "HS 9018 — instruments and apparatus for medical/surgical use (incl. syringes).",
    year: 2024, imports: { uganda: 14000.0, eac: 1200.0 }, exports: { uganda: 2400.0, eac: 2100.0 }
  }
};

const PRODUCT_HS4 = {
  "ph_arv":     "3004",
  "ph_antimal": "3004",
  "ph_tablets": "3004",
  "ph_inject":  "3004",
  "ph_vaccine": "3002"
};

const RAW_MATERIAL_TRADE = {
  "Tenofovir disoproxil fumarate (TDF)": {
    desc: "HS 2934.99 — heterocyclic compounds (ARV APIs). India 58% of Uganda medicine imports.",
    year: 2024, imports: { uganda: 22000.0, eac: 0.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Active Pharmaceutical Ingredient (API)": {
    desc: "HS 2941.xx / 2934.xx — APIs (various chapters). Near-total import dependence.",
    year: 2024, imports: { uganda: 38000.0, eac: 1000.0 }, exports: { uganda: 200.0, eac: 100.0 }
  },
  "Type I borosilicate vials": {
    desc: "HS 7010.10 — glass ampoules and vials. All pharma glass imported from India and Europe.",
    year: 2024, imports: { uganda: 3200.0, eac: 400.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const RAW_MATERIAL_PHASE = {};

const PHASE_PRODUCERS = {
  "ph_II": {
    count: 6,
    label: "Phase II — Formulation & Manufacturing (WHO-GMP aligned)",
    examples: [
      "QCIL (Quality Chemicals Industries Ltd) — 1.2bn tabs/caps/yr; WHO-GMP PQ",
      "KPI (Kampala Pharmaceutical Industries)",
      "Rene Industries",
      "Uganda Ltd / Medipharm",
      "Others (3 additional WHO-GMP aligned facilities)"
    ]
  },
  "ph_III": {
    count: 6,
    label: "Phase III — Packaging (active — linked to plastics chain)",
    examples: [
      "QCIL (in-house blister and bottle packaging)",
      "Other manufacturers with in-house packaging lines"
    ]
  }
};

const PHASE_SOURCE = "MTIC Diagnostic Study on Pharmaceuticals (Report 2, 2026); UNIDO Uganda pharma sector report";

const PRODUCT_FIRMS = {
  "ph_arv": {
    status: "named",
    firms: ["QCIL (Quality Chemicals Industries Ltd) — sub-Saharan Africa's largest ARV manufacturer"],
    note: "UGX 267bn revenue. WHO/PEPFAR prequalified. KEY GAP: APIs (Phase I) near-total import dependence from India. 2040 target: USD 0.9–1.2B market; cut import dependence to <50%."
  },
  "ph_antimal": {
    status: "named",
    firms: ["QCIL — ACT (artemether/lumefantrine) flagship; WHO-GMP, PEPFAR/GFATM procurement"],
    note: "ACT produced locally using entirely imported APIs. QCIL is a formulator, not an API synthesiser."
  },
  "ph_tablets": {
    status: "named",
    firms: [
      "QCIL (1.2bn tabs/caps/yr)",
      "KPI (Kampala Pharmaceutical Industries)",
      "Rene Industries",
      "And 3 other WHO-GMP aligned facilities"
    ],
    note: "Strong solid dosage manufacturing base. 6 WHO-GMP facilities. All APIs imported."
  },
  "ph_inject": {
    status: "named",
    firms: ["QCIL — aseptic injectables; WHO-GMP PQ for sterile products"],
    note: "One of few aseptic fill capabilities in East Africa. All glass vials and APIs imported."
  },
  "ph_vaccine": {
    status: "absent",
    firms: [],
    note: "No vaccine or biologic production in Uganda. All vaccines imported. 2040 aspiration: mRNA/protein-subunit manufacturing with AfCDC/CEPI support."
  }
};

const INPUT_KEYWORD_HS4 = [
  { pattern: /\bAPI\b|\bactive pharmaceutical\b/i, hs4: "2941" },
  { pattern: /\bglass vials?\b|\bborosilicate vials?\b/i, hs4: "7010" },
  { pattern: /\bvaccine\b|\bantigen\b/i, hs4: "3002" },
  { pattern: /\bsyringe\b|\bIV set\b/i, hs4: "9018" },
];

const INPUT_KEYWORD_PHASE = [
  { pattern: /\bQCIL\b|\bformulat/i, phase: "ph_II" },
  { pattern: /\bblister\b|\bpackaging.*pharma\b/i, phase: "ph_III" },
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
