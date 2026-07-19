// Textiles & Garments — Value Chain Explorer data
// Source: MTIC Diagnostic Study (Report 2); ITC TradeMap 2024; seed_all_chains.py STRENGTH data

const PRODUCTS = {
  "tx_yarn": {
    id: "tx_yarn",
    name: "Cotton & Synthetic Yarn",
    category: "Yarn",
    tier: "Phase III — Spinning",
    color: "#4c1d95",
    description: "Spun yarn from cotton and synthetic fibres. Uganda's most developed textiles capability — Fine Spinners and Nytil operate spinning capacity. CRITICAL GAP: Wet processing (Phase V) absent means yarn cannot progress to export-quality fabric domestically.",
    legend: [
      { color: "#4c1d95", label: "Yarn spinning chain" },
      { color: "#6d28d9", label: "Fibre preparation" },
      { color: "#7c3aed", label: "Raw fibre" },
    ],
    chains: [
      {
        title: "Yarn Spinning Chain",
        accent: "#4c1d95",
        nodes: [
          {
            id: "tx_yarn_top",
            stage: "Finished Product",
            label: "Spun Yarn",
            color: "#4c1d95",
            textColor: "#ffffff",
            inputs: [
              "Ginned cotton lint (Uganda surplus — ~116,000 bales/yr; ~90% currently exported raw)",
              "Polyester staple fibre (imported — China/India dominant)",
              "Viscose / rayon staple (imported — cellulosic fibre for soft blends)",
              "Lubricant / spin finish (applied at ring frame for traveller lubrication)",
              "Energy (ring spinning frames, winding machines)"
            ],
            technology: [
              "Opening & cleaning line (bale opener, cleaner, blender — fibre preparation)",
              "Carding machine (web formation; removes neps and short fibres)",
              "Draw frame (doubling and drafting — sliver parallelisation)",
              "Speed frame / roving frame (preliminary twisting before ring frame)",
              "Ring spinning frame (twist insertion — most common in Uganda)",
              "Winding / autoconer (bobbin to cone; yarn clearing and splicing)"
            ],
            skills: [
              "Spinning Engineer — draft, twist factor and roving tension optimisation for target count (Ne)",
              "Fibre Technologist — fibre blend ratio, HVI testing (strength, uniformity, micronaire) & lot management",
              "Textile Technician — traveller selection, ring wear monitoring & yarn breakage root cause analysis",
              "Quality Engineer — yarn count, tenacity, elongation & Uster evenness testing per ISO 2060",
              "Maintenance Engineer — ring frame preventive maintenance (ring, traveller, spindle, apron)"
            ]
          },
          {
            id: "tx_fibre_prep",
            stage: "Fibre Preparation",
            label: "Fibre Blend & Opening",
            color: "#6d28d9",
            textColor: "#ffffff",
            inputs: [
              "Cotton lint (bales — from Uganda ginneries)",
              "Polyester staple fibre (100–150 mm cut length — imported)",
              "Viscose staple fibre (imported — 1.2–1.5 denier for fine blends)",
              "Bale-opening equipment lubrication and compressed air"
            ],
            technology: [
              "Bale plucker / opener (automatic multi-bale plucking)",
              "Cleaning / separating duct (gravity/impurity separation)",
              "Mixing chamber (intimate fibre blending across bale lots)",
              "Chute feed to card (pneumatic fibre transport)"
            ],
            skills: [
              "Fibre Blend Technologist — bale laydown, blend ratio management & HVI property matching",
              "Opening Area Operator — machine setting for gentle opening (minimise fibre damage)",
              "Quality Technician — trash content, fibre length and moisture measurement on incoming bales"
            ]
          },
          {
            id: "tx_cotton_raw",
            stage: "Raw Materials",
            label: "Cotton & Fibres",
            color: "#7c3aed",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Ginned cotton lint", detail: "Domestic — HS 5201. Uganda produces ~116,000 bales/yr; ~90% exported raw. Fine Spinners and Nytil consume some locally. Major surplus available for upstream spin investment." },
              { name: "Polyester staple fibre (PET)", detail: "Imported — HS 5503.20. All polyester fibre imported from China/India. No domestic polyester production." },
              { name: "Viscose / rayon staple", detail: "Imported — HS 5504.10. All viscose imported. Cellulosic fibre for soft-hand blends and baby clothing." }
            ]
          }
        ]
      }
    ]
  },

  "tx_fabric": {
    id: "tx_fabric",
    name: "Finished Fabric (Woven & Knit)",
    category: "Fabric",
    tier: "Phase V — Wet Processing (Critical Gap)",
    color: "#6d28d9",
    description: "Dyed and finished woven or knitted fabric ready for garment cutting. CRITICAL GAP: Wet processing and finishing (dyeing, printing, washing) is almost entirely absent in Uganda — without it, domestic yarn cannot become export-quality fabric or garment.",
    legend: [
      { color: "#6d28d9", label: "Finished fabric chain" },
      { color: "#7c3aed", label: "Grey fabric" },
      { color: "#4c1d95", label: "Yarn" },
      { color: "#1e3a8a", label: "Raw materials" },
    ],
    chains: [
      {
        title: "Fabric Production Chain",
        accent: "#6d28d9",
        nodes: [
          {
            id: "tx_fabric_top",
            stage: "Finished Product (Gap)",
            label: "Dyed & Finished Fabric",
            color: "#6d28d9",
            textColor: "#ffffff",
            inputs: [
              "Grey woven / knitted fabric (grey cloth from loom or knitting machine)",
              "Reactive / disperse dyes (CRITICAL — entirely imported; blocks chain if unavailable)",
              "Softeners, fixatives & optical brighteners (finishing chemicals — imported)",
              "Water (large volumes — 80–150 L/kg fabric for dyeing)",
              "Steam / process heat (fixation and drying)",
              "Energy (jigger, jet dyeing machine, stenter frame drives)"
            ],
            technology: [
              "Singeing machine (removes surface fuzz — gas flame or heated plate)",
              "Desizing / scouring machine (removes size and natural impurities)",
              "Mercerisation range (NaOH treatment — lustre and dye uptake improvement)",
              "Jet dyeing machine / jigger (dye application under pressure and heat)",
              "Continuous steamer (reactive dye fixation)",
              "Stenter frame (width control, heat setting, finishing chemical application)"
            ],
            skills: [
              "Dyeing Technician — recipe formulation, dye-bath management & colour matching (CMC/CIE tolerances)",
              "Wet Processing Engineer — process sequence optimisation, water and chemical consumption reduction",
              "Chemical Engineer — effluent treatment design (dye-bath decolourisation, pH neutralisation, BOD removal)",
              "Textile Chemist — dye selection (reactive for cotton, disperse for polyester) & fastness specification (ISO 105)",
              "Quality Engineer — colour fastness (wash, light, rub), shrinkage & hand-feel evaluation"
            ]
          },
          {
            id: "tx_grey_fabric",
            stage: "Grey Fabric (Gap)",
            label: "Grey Fabric",
            color: "#7c3aed",
            textColor: "#ffffff",
            dual: true,
            routeA: {
              label: "Woven Grey Fabric (Gap)",
              inputs: [
                "Warp yarn (sizing applied — starch or PVA for weaving strength)",
                "Weft yarn (sized or unsized depending on loom type)",
                "Loom heddles, reeds and rapiers (weaving consumables)",
                "Energy (rapier or projectile loom drives)"
              ],
              technology: [
                "Sizing machine (applies starch or PVA size to warp beam)",
                "Rapier loom (weft insertion by rapier carrier — most common industrial type)",
                "Air-jet loom (high-speed weft by compressed air — not in Uganda)",
                "Jacquard attachment (complex pattern weaving — very limited in Uganda)",
                "Cloth inspection and rolling frame"
              ],
              skills: [
                "Weaving Engineer — warp setting, pick density and beam preparation",
                "Loom Technician — rapier mechanism, shed formation and timing adjustment",
                "Sizing Technician — starch concentration, viscosity and add-on control",
                "Quality Inspector — pick count, width, reed marks and selvedge inspection",
                "Maintenance Engineer — loom preventive maintenance (loom speed, timing, beat-up)"
              ]
            },
            routeB: {
              label: "Knitted Fabric (Gap)",
              inputs: [
                "Yarn (combed cotton or polyester — finer count for knitting)",
                "Knitting machine oil (cylinder and dial lubrication)",
                "Energy (cylinder/flat-bed knitting machine drives)"
              ],
              technology: [
                "Circular weft knitting machine (jersey, interlock, rib — most common globally)",
                "Flat-bed knitting machine (fashion panels — limited in Uganda)",
                "Tumble dryer (moisture management pre-dyeing)",
                "Compacting machine (fabric length stabilisation)"
              ],
              skills: [
                "Knitting Engineer — gauge selection, stitch cam setting & fabric weight control",
                "Machine Technician — cylinder/dial needle replacement & sinker adjustment",
                "Quality Inspector — courses per cm, stitch length, cover factor & snag resistance"
              ]
            }
          },
          {
            id: "tx_yarn_input",
            stage: "Yarn",
            label: "Spun Yarn",
            color: "#4c1d95",
            textColor: "#ffffff",
            inputs: [
              "Cotton lint (Uganda domestic — Fine Spinners, Nytil)",
              "Polyester fibre (imported — for blends)",
              "Energy (ring spinning power)"
            ],
            technology: [
              "Ring spinning frame (Uganda — Fine Spinners + Nytil capacity)",
              "Open-end / rotor spinning (limited in Uganda)",
              "Winding (yarn from bobbin to cone)"
            ],
            skills: [
              "Spinning Engineer — count, twist and draft optimisation",
              "Quality Engineer — strength, evenness and hairiness tests"
            ]
          },
          {
            id: "tx_fab_raw",
            stage: "Raw Materials",
            label: "Dyes & Chemicals",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Reactive dyes (cotton)", detail: "Imported — HS 3204.16. CRITICAL: all synthetic dyes imported from India/China. Without dyes, no domestic fabric finishing is possible." },
              { name: "Disperse dyes (polyester)", detail: "Imported — HS 3204.11. All disperse dyes for polyester finishing imported." },
              { name: "Finishing chemicals (softeners, fixatives)", detail: "Imported — HS 3809.91. Textile auxiliaries entirely imported; no domestic production." }
            ]
          }
        ]
      }
    ]
  },

  "tx_tshirt": {
    id: "tx_tshirt",
    name: "T-Shirts & Knitwear",
    category: "Garments",
    tier: "Phase VI — Garment Manufacturing",
    color: "#7c3aed",
    description: "Mass-market knitted tops, polo shirts and knitwear. Some domestic production exists but fabric is largely imported — Uganda exports ~90% of its lint raw while importing finished garments.",
    legend: [
      { color: "#7c3aed", label: "Garment production chain" },
      { color: "#6d28d9", label: "Fabric & cut" },
      { color: "#1e3a8a", label: "Raw materials" },
    ],
    chains: [
      {
        title: "Knitwear Manufacturing Chain",
        accent: "#7c3aed",
        nodes: [
          {
            id: "tx_tshirt_top",
            stage: "Finished Product",
            label: "T-Shirt / Knitwear",
            color: "#7c3aed",
            textColor: "#ffffff",
            inputs: [
              "Knitted fabric (finished, dyed — imported or limited domestic)",
              "Thread (polyester or cotton sewing thread — imported spools)",
              "Labels (woven brand label + care label — imported)",
              "Buttons, zips, elastics (imported trims)",
              "Packaging (polyethylene bags, cartons)"
            ],
            technology: [
              "Automatic spreader and cutter (fabric spreading and die/blade cutting)",
              "Industrial lockstitch machine (Juki, Brother — body seaming)",
              "Overlock (serger) machine (edge finishing)",
              "Flatlock machine (sportswear flat seam)",
              "Buttonhole and button-attach machine",
              "Inspection table and manual folding / bagging line"
            ],
            skills: [
              "Garment Technician — stitch type selection, seam allowance, shrinkage allowance in pattern",
              "Sewing Machine Operator — lockstitch, overlock and flatlock seaming at production rates",
              "Pattern Maker / CAD Operator — pattern grading across sizes, marker planning for fabric efficiency",
              "Quality Controller — measurement check, seam strength & wash-test sample evaluation",
              "Production Planner — cut-to-ship lead time, bundle tracking & operator line balancing"
            ]
          },
          {
            id: "tx_cut_sew",
            stage: "Cut & Sew",
            label: "Cut, Sew & Trim",
            color: "#6d28d9",
            textColor: "#ffffff",
            inputs: [
              "Finished knitted fabric (laid on cutting table)",
              "Marker / pattern (CAD-generated cutting lay — optimised for yield)",
              "Fusible interlining (collar support — imported)",
              "Polyester thread (seaming thread — imported)"
            ],
            technology: [
              "Spreader (auto or manual multi-ply spreading)",
              "Straight knife / band knife cutter",
              "Bundling and ticketing (cut parts bundle for sewing floor)",
              "Collar pressing machine",
              "Steam iron (final pressing)"
            ],
            skills: [
              "Cutting Room Supervisor — lay planning, end loss minimisation & operator management",
              "Cutter — straight knife operation, pattern accuracy & fabric damage prevention",
              "Bundle Sorter — cut parts identification, lot segregation & work-in-progress tracking"
            ]
          },
          {
            id: "tx_garment_raw",
            stage: "Raw Materials",
            label: "Fabric & Trims",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Knitted fabric (jersey / interlock)", detail: "Largely imported — HS 6006. Only limited knitted fabric produced domestically. Without domestic dyeing/finishing, local yarn cannot feed this step." },
              { name: "Polyester sewing thread", detail: "Imported — HS 5402.20. All commercial sewing thread imported from India/China." },
              { name: "Woven labels and trims", detail: "Imported — HS 5807. Brand, size and care labels imported; some printing done locally." }
            ]
          }
        ]
      }
    ]
  },

  "tx_workwear": {
    id: "tx_workwear",
    name: "Uniforms & Workwear",
    category: "Garments",
    tier: "Phase VI — Garment Manufacturing",
    color: "#8b5cf6",
    description: "Industrial uniforms, school uniforms and corporate workwear. The most viable near-term garment opportunity in Uganda — large institutional procurement (government, schools, hospitals) can be served by domestic cut-and-sew using imported or limited domestic fabric.",
    legend: [
      { color: "#8b5cf6", label: "Workwear production chain" },
      { color: "#1e3a8a", label: "Fabric & materials (imported)" },
    ],
    chains: [
      {
        title: "Workwear Manufacturing Chain",
        accent: "#8b5cf6",
        nodes: [
          {
            id: "tx_work_top",
            stage: "Finished Product",
            label: "Uniforms / Workwear",
            color: "#8b5cf6",
            textColor: "#ffffff",
            inputs: [
              "Plain-weave fabric (poly-cotton 65/35 or 100% cotton — imported or limited domestic)",
              "Reflective tape (hi-vis workwear — imported)",
              "Zip fasteners, buttons & press studs (imported — HS 9607)",
              "Sewing thread (polyester core-spun — imported)",
              "Embroidery thread + backing (for logo/badge embroidery)"
            ],
            technology: [
              "Straight knife cutter (high-ply spread cutting)",
              "Industrial lockstitch sewing machine (multi-needle for pocket attachment)",
              "Overlock machine (French seam or safety stitch for durability)",
              "Bar-tack machine (stress point reinforcement at pocket corners, belt loops)",
              "Computerised embroidery machine (logo, company name, rank badges)",
              "Heat-press (badge transfer, reflective tape bonding)"
            ],
            skills: [
              "Garment Engineer — seam durability specification for laundering cycle requirements",
              "Embroidery Operator — hoop placement, colour sequence & stitch density programming",
              "Sewing Machine Operator — lockstitch, overlock and bar-tack operation at production rates",
              "Pattern Maker — grading across size range for institutional procurement",
              "QC Inspector — measurement audit, seam strength test & fabric pilling/abrasion assessment"
            ]
          },
          {
            id: "tx_work_raw",
            stage: "Fabric & Trims",
            label: "Materials",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Poly-cotton plain-weave fabric", detail: "Largely imported — HS 5513. Poly-cotton for workwear mostly imported. Some cotton fabric available from local spinning + external weaving (Nytil limited production)." },
              { name: "Reflective tape", detail: "Imported — HS 3926. All retroreflective tape for hi-vis workwear imported." },
              { name: "Zip fasteners", detail: "Imported — HS 9607. YKK and Chinese-brand zips imported." }
            ]
          }
        ]
      }
    ]
  },

  "tx_bags": {
    id: "tx_bags",
    name: "Woven PP Sacks & Bags",
    category: "Technical Textiles",
    tier: "Phase VI — Conversion (Emerging)",
    color: "#1d4ed8",
    description: "Woven polypropylene sacks for cement, grain, sugar and agricultural packaging. Some domestic production exists using imported PP resin/tape, making this the most active technical textile sub-sector in Uganda.",
    legend: [
      { color: "#1d4ed8", label: "PP sack production chain" },
      { color: "#1e3a8a", label: "PP resin (imported)" },
    ],
    chains: [
      {
        title: "Woven PP Sack Chain",
        accent: "#1d4ed8",
        nodes: [
          {
            id: "tx_bags_top",
            stage: "Finished Product",
            label: "Woven PP Sack",
            color: "#1d4ed8",
            textColor: "#ffffff",
            inputs: [
              "PP tape (extruded, stretched — from PP resin pellets imported)",
              "HDPE thread (sewing line — imported or PP monofilament)",
              "Printing inks (flexographic — for branding / client marking)",
              "Liner bag (LDPE inner liner for moisture-sensitive contents)",
              "Energy (extruder, loom and cutting drives)"
            ],
            technology: [
              "PP tape extrusion line (extruder + stretch orientation + winding)",
              "Circular loom (shuttle loom — weaves PP tape into tubular fabric)",
              "Laminator (optional LDPE lamination for moisture barrier)",
              "Flexographic printer (2–4 colour brand printing on fabric)",
              "Automatic bag cutter and sewer (bottom sew, hem + valve formation)"
            ],
            skills: [
              "Extrusion Engineer — tape denier, draw ratio and tenacity control (ASTM D5034)",
              "Weaving Technician — circular loom pick setting, selvedge tension & fabric weight specification",
              "Print Technician — ink viscosity, anilox roll pressure and colour density management",
              "Sewing Operator — automatic bag sewing machine operation and thread tension adjustment",
              "Quality Engineer — sack strength (drop test, puncture), print quality & weight per sack"
            ]
          },
          {
            id: "tx_bags_raw",
            stage: "Raw Materials (Imported)",
            label: "PP Resin & Inputs",
            color: "#1e3a8a",
            textColor: "#ffffff",
            rawMaterials: true,
            items: [
              { name: "Polypropylene (PP) resin pellets", detail: "Imported — HS 3902.10. All PP resin 100% imported. No domestic polymer production. Kabalega petrochemical park future (~2029)." },
              { name: "Printing inks (flexographic)", detail: "Imported — HS 3215.19. Water-based and solvent-based inks for bag printing imported." },
              { name: "LDPE liner film", detail: "Imported — HS 3920.10. LDPE film for moisture-barrier liner sacks imported." }
            ]
          }
        ]
      }
    ]
  }
};

const CATEGORIES = [
  { name: "Yarn", color: "#4c1d95", products: ["tx_yarn"] },
  { name: "Fabric", color: "#6d28d9", products: ["tx_fabric"] },
  { name: "Garments", color: "#7c3aed", products: ["tx_tshirt", "tx_workwear"] },
  { name: "Technical Textiles", color: "#1d4ed8", products: ["tx_bags"] }
];

const TRADE_HS4 = {
  "5201": {
    desc: "HS 5201 — cotton, not carded or combed. Uganda major exporter of raw lint.",
    year: 2024, imports: { uganda: 400.0, eac: 300.0 }, exports: { uganda: 42000.0, eac: 18000.0 }
  },
  "5205": {
    desc: "HS 5205 — cotton yarn (> 85% cotton). Fine Spinners and Nytil production.",
    year: 2024, imports: { uganda: 3200.0, eac: 600.0 }, exports: { uganda: 2100.0, eac: 1800.0 }
  },
  "6109": {
    desc: "HS 6109 — T-shirts, singlets and other vests, knitted.",
    year: 2024, imports: { uganda: 18000.0, eac: 1200.0 }, exports: { uganda: 800.0, eac: 600.0 }
  },
  "6211": {
    desc: "HS 6211 — track suits, ski suits and swimwear (incl. workwear).",
    year: 2024, imports: { uganda: 4200.0, eac: 300.0 }, exports: { uganda: 600.0, eac: 400.0 }
  },
  "6305": {
    desc: "HS 6305 — sacks and bags of textile materials (incl. woven PP sacks).",
    year: 2024, imports: { uganda: 8600.0, eac: 1200.0 }, exports: { uganda: 3400.0, eac: 3100.0 }
  },
  "3902": {
    desc: "HS 3902 — polymers of propylene (PP resin). All imported; no domestic PP resin.",
    year: 2024, imports: { uganda: 22000.0, eac: 400.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const PRODUCT_HS4 = {
  "tx_yarn":     "5205",
  "tx_fabric":   "5208",
  "tx_tshirt":   "6109",
  "tx_workwear": "6211",
  "tx_bags":     "6305"
};

const RAW_MATERIAL_TRADE = {
  "Ginned cotton lint": {
    desc: "HS 5201 — cotton, not carded or combed. Uganda produces ~116,000 bales/yr; ~90% exported raw.",
    year: 2024, imports: { uganda: 400.0, eac: 300.0 }, exports: { uganda: 42000.0, eac: 18000.0 }
  },
  "Polyester staple fibre (PET)": {
    desc: "HS 5503.20 — synthetic staple fibres, of polyesters. All imported from China/India.",
    year: 2024, imports: { uganda: 6200.0, eac: 400.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Reactive dyes (cotton)": {
    desc: "HS 3204.16 — reactive dyes. Entirely imported. CRITICAL gap — without dyes, no domestic fabric finishing.",
    year: 2024, imports: { uganda: 1800.0, eac: 200.0 }, exports: { uganda: 0.0, eac: 0.0 }
  },
  "Polypropylene (PP) resin pellets": {
    desc: "HS 3902.10 — polypropylene, primary forms. All PP resin imported; no domestic production.",
    year: 2024, imports: { uganda: 22000.0, eac: 400.0 }, exports: { uganda: 0.0, eac: 0.0 }
  }
};

const RAW_MATERIAL_PHASE = {
  "Ginned cotton lint": "tx_I"
};

const PHASE_PRODUCERS = {
  "tx_I": {
    count: 8,
    label: "Phase I — Cotton Growing (strong)",
    examples: ["Smallholder cotton farmers (~116,000 bales/yr)", "Cotton outgrowers supplying Fine Spinners"]
  },
  "tx_II": {
    count: 15,
    label: "Phase II — Cotton Ginning (strong)",
    examples: ["Fine Spinners ginneries", "Dunavant Uganda", "Olam Uganda", "Cargill Uganda"]
  },
  "tx_III": {
    count: 2,
    label: "Phase III — Spinning (emerging)",
    examples: ["Fine Spinners Uganda Ltd (Kampala)", "Nytil (Uganda Textile Industries)"]
  }
};

const PHASE_SOURCE = "MTIC Diagnostic Study on Textiles & Garments (Report 2, 2026)";

const PRODUCT_FIRMS = {
  "tx_yarn": {
    status: "named",
    firms: ["Fine Spinners Uganda Ltd", "Nytil (Uganda Textile Industries)"],
    note: "Spinning capacity exists but underutilised. CRITICAL GAP: Wet processing (Phase V) absent — without dyeing/finishing Uganda cannot produce export-quality fabric. 2040 target: ≥50% of lint processed domestically; ginnery utilisation 60%+"
  },
  "tx_fabric": {
    status: "absent",
    firms: [],
    note: "Finished fabric production ABSENT — wet processing and finishing critically missing. Grey woven fabric also largely absent (weaving capacity minimal). Critical bottleneck that blocks the entire textile value chain."
  },
  "tx_tshirt": {
    status: "emerging",
    firms: ["Several small garment makers in Kampala and Jinja"],
    note: "Some knitwear production; fabric largely imported. ~90% of Uganda's lint exported raw while finished T-shirts are imported."
  },
  "tx_workwear": {
    status: "emerging",
    firms: ["Several uniform manufacturers in Kampala (names in MTIC register)"],
    note: "Uniforms and workwear most viable near-term garment opportunity. Government and institutional procurement creates steady local demand."
  },
  "tx_bags": {
    status: "named",
    firms: ["Several woven PP sack producers (names in MTIC register)"],
    note: "Woven PP sacks most active technical textile sub-sector. Used for cement, sugar and grain packaging. PP resin 100% imported."
  }
};

const INPUT_KEYWORD_HS4 = [
  { pattern: /\bcotton lint\b|\bginned cotton\b/i, hs4: "5201" },
  { pattern: /\bpolyester.*fibre\b|\bPET.*staple\b|\bPSF\b/i, hs4: "5503" },
  { pattern: /\breactive dyes?\b|\bdisperse dyes?\b|\bdirect dyes?\b/i, hs4: "3204" },
  { pattern: /\bPP.*resin\b|\bpolypropylene.*pellets?\b/i, hs4: "3902" },
  { pattern: /\bcotton yarn\b/i, hs4: "5205" },
  { pattern: /\bviscose\b|\brayon staple\b|\bmodal\b|\blyocell\b/i, hs4: "5504" },
  { pattern: /\bsoftener\b|\bfixative\b|\boptical brightener\b|\btextile.*auxiliary\b|\bmordant\b/i, hs4: "3809" },
  { pattern: /\bsewing thread\b|\bpolyester thread\b|\boverlock thread\b/i, hs4: "5402" },
  { pattern: /\bzip fastener\b|\bslide fastener\b|\bzip\b.*garment/i, hs4: "9607" },
  { pattern: /\breflective tape\b|\bhi.vis.*tape\b|\bsafety tape\b/i, hs4: "3926" },
  { pattern: /\bprinting inks?\b|\bflexographic.*ink\b|\bgarment.*ink\b/i, hs4: "3215" },
  { pattern: /\bpoly.cotton.*fabric\b|\bworkwear.*fabric\b|\bsynthetic.*woven fabric\b/i, hs4: "5513" },
  { pattern: /\bwoven labels?\b|\bcare labels?\b|\bbrand.*labels?\b/i, hs4: "5807" },
  { pattern: /\bknitted fabric\b/i, hs4: "6006" },
];

const INPUT_KEYWORD_PHASE = [
  { pattern: /\bginned cotton\b|\bcotton lint\b/i, phase: "tx_I" },
  { pattern: /\bFine Spinners\b|\bNytil\b/i, phase: "tx_III" },
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
