// Iron & Steel finished-product data: each stage carries inputs, technology
// and the professional skills required. To add the next value chain, create
// a sibling file (e.g. textiles.js) following this same PRODUCTS/CATEGORIES
// shape and merge it into App.jsx.

const SLAB_STAGE = {
  id: "slab", stage: "Continuous Casting", label: "Slab",
  color: "#2769ab", textColor: "#ffffff",
  inputs: ["Liquid steel (from ladle)", "Mold powder / flux (lubrication & heat transfer)", "Cooling water (primary & secondary)", "Argon gas (tundish sealing, SEN purging)", "Ferroalloy trim additions"],
  technology: ["Curved continuous slab caster (bow-type)", "Submerged entry nozzle (SEN) — controlled mold flow", "Electromagnetic stirring (EMS) — solidification quality", "Soft reduction system (centre segregation control)", "Tundish (intermediate vessel, multi-strand distribution)"],
  skills: ["Metallurgist — solidification modelling, segregation & inclusion cleanliness", "Process Engineer — mold level control & breakout prevention", "Refractory Engineer — tundish & mold flux design, SEN integrity", "Mechanical Engineer — secondary cooling design (spray patterns & water flow)", "Materials Engineer — slab surface quality specification"],
};
const BILLET_STAGE = {
  id: "billet", stage: "Continuous Casting", label: "Billet",
  color: "#2769ab", textColor: "#ffffff",
  inputs: ["Liquid steel (from ladle)", "Mold powder / flux", "Cooling water", "Argon gas (SEN purging)", "Ferroalloy trim additions"],
  technology: ["Vertical / curved billet caster (100–180mm square section)", "Electromagnetic stirring (EMS — mold & strand)", "Tundish with flow control & metering nozzle", "Mold level control (electromagnetic or radar)", "In-mold electromagnetic braking (EMBR)"],
  skills: ["Metallurgist — billet internal quality (macro, segregation, porosity control)", "Process Engineer — casting speed & superheat optimisation", "Refractory Engineer — SEN & tundish nozzle management", "Mechanical Engineer — strand guide & withdrawal roll alignment", "Quality Control Engineer — billet surface inspection & grading"],
};
const BLOOM_STAGE = {
  id: "bloom", stage: "Continuous Casting", label: "Bloom",
  color: "#2769ab", textColor: "#ffffff",
  inputs: ["Liquid steel (from ladle)", "Mold powder / flux", "Cooling water", "Argon gas", "Ferroalloy trim additions"],
  technology: ["Curved bloom caster (200–400mm section)", "Electromagnetic stirring (EMS — mold & strand)", "Soft reduction system (centre porosity control)", "Tundish with slide gate flow control", "Bloom surface inspection system"],
  skills: ["Metallurgist — bloom homogeneity, macro cleanliness & segregation control", "Process Engineer — casting speed, superheat & secondary cooling management", "Refractory Engineer — mold flux & tundish design for large sections", "Mechanical Engineer — bloom straightening & withdrawal equipment", "Quality Control Engineer — bloom surface quality & internal soundness testing"],
};
const BOF_EAF_STAGE = {
  id: "steel", stage: "Steelmaking", label: "Liquid Steel",
  color: "#2b7ac5", textColor: "#ffffff", dual: true,
  routeA: {
    label: "BOF Route",
    inputs: ["Hot metal (70–80%) from blast furnace", "Steel scrap (20–30%)", "Lime / dolomite (flux)", "Oxygen (blown at supersonic speed)", "Ferroalloys (Mn, Si, Al — deoxidation & chemistry)"],
    technology: ["Basic Oxygen Furnace (converter) — ~300t heat size", "Ladle furnace (LF) — secondary refining & alloying", "RH / VD degasser — ultra-low C & H2 removal (IF grades)", "KR desulphurisation (hot metal pretreatment)", "Argon purging station"],
    skills: ["Steelmaking Metallurgist — blowing model, endpoint carbon & slag basicity", "Process Engineer — heat balance, temperature & tap weight management", "Chemical Engineer — secondary metallurgy, alloy trim & inclusion shape control", "Refractory Engineer — converter lining management & gunning practice", "Materials Engineer — grade-specific chemistry development (IF, HSLA, AHSS)"],
  },
  routeB: {
    label: "EAF Route",
    inputs: ["Scrap / DRI / HBI (metallic charge)", "Electricity (arc melting)", "Lime / dolomite (flux)", "Ferroalloys", "Graphite electrodes", "Carbon / oxygen injection"],
    technology: ["Electric Arc Furnace (AC or DC) — scrap or DRI melting", "Ladle furnace (LF) — refining & alloying", "VD / VOD degasser (stainless & specialty grades)", "Scrap preheating (Consteel / shaft furnace)", "Fume extraction & offgas treatment system"],
    skills: ["Steelmaking Metallurgist — foamy slag practice & power-on time optimisation", "Electrical Engineer — arc furnace power systems & electrode regulation", "Process Engineer — charge mix optimisation (scrap grades, DRI ratio)", "Chemical Engineer — refining to tight chemistry windows & degassing", "Materials Engineer — residual element (Cu, Sn, Ni) management from scrap"],
  },
};
const BF_DR_STAGE = {
  id: "iron", stage: "Ironmaking", label: "Metallic Inputs",
  color: "#2f8bdf", textColor: "#ffffff", triple: true,
  routeA: {
    label: "Blast Furnace → Hot Metal",
    inputs: ["Sinter + pellets + lump ore (iron burden)", "Metallurgical coke (reductant + fuel + burden support)", "Limestone / dolomite flux", "Hot blast air (1,100-1,200 C)", "Pulverized coal injection (PCI)"],
    technology: ["Blast furnace (BF) — shaft furnace, 3,000-5,000 m3 working volume", "Hot blast stoves (Cowper stoves — blast preheating)", "PCI system — coke substitution", "Casthouse equipment (taphole drilling, mud guns, torpedo ladles)", "Top gas recovery turbine (TRT) — energy recovery"],
    skills: ["Ironmaking Metallurgist — burden distribution, gas flow & raceway management", "Chemical Engineer — slag basicity, viscosity & hot metal chemistry control", "Refractory Engineer — furnace lining wear monitoring & campaign life management", "Mechanical Engineer — casthouse equipment, stove & tuyere maintenance", "Process Engineer — PCI rate optimisation & coke rate reduction programmes"],
  },
  routeB: {
    label: "Direct Reduction → DRI/HBI",
    inputs: ["Iron ore pellets (high grade, >67% Fe)", "Natural gas (reformed to H2 + CO reducing gas)", "or Green hydrogen (H2 — emerging route)", "Electricity (for H2 via electrolysis)"],
    technology: ["MIDREX shaft furnace (dominant DR technology globally)", "HYL / Energiron pressurized DR reactor", "Coal-based rotary kiln (SL/RN process)", "H2-based DRI shaft furnace (HYBRIT — emerging)", "Hot briquetting press (HBI for safe transport & storage)"],
    skills: ["Process Metallurgist — reducing gas chemistry (H2/CO ratio) & metallisation control", "Chemical Engineer — pellet reducibility assessment & DR reactor design", "Hydrogen Engineer — H2 integration, safety management & electrolyser operation", "Materials Engineer — DRI/HBI handling, passivation & pyrophoric risk management", "Process Engineer — energy efficiency optimisation across DR circuit"],
  },
  routeC: {
    label: "Electric Smelting Furnace → Pig Iron",
    inputs: ["Iron ore fines / pellets / pre-reduced DRI (ore feed)", "Electricity (primary energy source — arc or resistive heating)", "Coal / char (reductant — reducing agent in bath)", "Fluxes — limestone / dolomite (slag chemistry)", "Oxygen (optional — post-combustion for energy efficiency)"],
    technology: ["Electric Smelting Furnace (ESF) — submerged arc furnace variant for ironmaking", "HIsarna smelting reduction reactor (Tata Steel — cyclone converter furnace + bath smelter)", "Finex / COREX smelting reduction furnace (fluidized bed pre-reduction + melter gasifier)", "Boston Metal Molten Oxide Electrolysis (MOE) — electrolytic iron production (emerging)", "Helios ESF project (commercial-scale ESF — early deployment stage)"],
    skills: ["Pyrometallurgical Engineer — ESF electrode management, bath temperature & slag chemistry control", "Electrical Engineer — high-power AC/DC furnace power systems & electrode regulation", "Process Metallurgist — smelting reduction chemistry, pre-reduction degree & pig iron quality control", "Refractory Engineer — ESF hearth & sidewall lining design for liquid iron & slag conditions", "Process Engineer — energy efficiency optimisation & CO2 intensity benchmarking vs. blast furnace route"],
  },
};
const FEEDSTOCK_STAGE = {
  id: "feedstock", stage: "Feedstock Preparation", label: "Prepared Feedstock",
  color: "#3396e8", textColor: "#ffffff",
  groups: [
    { label: "Sinter", inputs: ["Iron ore fines", "Coke breeze", "Limestone / dolomite", "Return fines"], technology: ["Dwight-Lloyd sintering strand", "Ignition hood (coke breeze combustion)", "Sinter cooler & screening"], skills: ["Minerals Engineer — sinter blend & basicity optimisation", "Process Engineer — strand productivity & permeability management", "Metallurgist — tumble index, reducibility & RDI targets"] },
    { label: "Pellets", inputs: ["Iron ore concentrate", "Bentonite binder", "Flux additives"], technology: ["Balling disc / drum", "Travelling grate / grate-kiln induration furnace", "Pellet screening & cooling"], skills: ["Minerals Engineer — green ball formation, sizing & binder optimisation", "Process Engineer — induration temperature profile & fuel efficiency", "Metallurgist — cold crush strength, porosity & reducibility specification"] },
    { label: "Coke", inputs: ["Metallurgical coal blend", "Coke oven battery (1,100 C carbonisation)"], technology: ["By-product coke oven battery", "Heat recovery coke oven (SCOPE21)", "Coke dry quenching (CDQ — energy recovery)"], skills: ["Coal Technologist — blend design (vitrinite reflectance, CRI/CSR targeting)", "Chemical Engineer — carbonisation time, temperature & by-product recovery", "Metallurgist — coke quality (CSR, CRI, M40/M10) specification & testing"] },
    { label: "Reducing Gas", inputs: ["Natural gas — SMR reforming", "or Electrolysis — green H2"], technology: ["Steam methane reformer (SMR)", "Pressure swing adsorption (PSA — H2 purification)", "Alkaline / PEM electrolyzer (green H2)"], skills: ["Chemical Engineer — reformer catalyst management & H2/CO ratio control", "Hydrogen Engineer — electrolyser stack efficiency & H2 purity specification", "Process Engineer — PSA cycle optimisation & gas compression management"] },
  ],
};
const STEEL_RAW = {
  id: "rawsteel", stage: "Raw Materials — Steel Chain", label: "Steel Raw Materials",
  color: "#1a3a5c", textColor: "#e8f4ff", rawMaterials: true,
  items: [
    { name: "Iron Ore", detail: "Hematite / magnetite — mined, crushed, beneficiated to concentrate" },
    { name: "Metallurgical Coal", detail: "Low-sulfur coking grades — carbonized into coke in battery ovens" },
    { name: "Limestone / Dolomite", detail: "Quarried — flux for ironmaking slag and steelmaking refining" },
    { name: "Water", detail: "Cooling and process water throughout chain" },
    { name: "Energy / Electricity", detail: "EAF arc melting, DRI reduction, rolling mills, coating lines" },
  ],
};

const ZINC_CHAIN = [
  { id: "zn-bath", stage: "Coating Input", label: "Zinc in Galvanizing Bath", color: "#7b3f00", textColor: "#ffffff", inputs: ["SHG zinc ingots (99.995% pure)", "Aluminum additions (0.15-0.25% — inhibition layer)", "Flux chemicals (ammonium chloride pre-flux)", "Lead (trace — for spangle, largely phased out)"], technology: ["Zinc pot (ceramic-lined, 450-460 C)", "Induction / gas-fired bath heating", "Air knife / gas wiping system (coating weight control)", "Pot roll system (sink roll, stabilizer rolls)", "Dross removal equipment"], skills: ["Coating Technologist — bath temperature, Al/Fe balance & dross management", "Materials Engineer — Fe2Al5 inhibition layer formation & coating adhesion", "Metallurgist — spangle control (zero spangle for automotive)", "Quality Control Engineer — coating weight, bend test & salt spray testing", "Process Engineer — zinc consumption efficiency & bath contamination control"] },
  { id: "zn-refine", stage: "Zinc Refining", label: "Zinc Refining", color: "#9c5200", textColor: "#ffffff", inputs: ["Crude zinc from smelting (98-99% Zn)", "Energy (distillation or electrolytic refining)"], technology: ["Fractional distillation (New Jersey / Reflux column)", "Electrolytic refining (ultra-high purity)", "Liquation (iron removal — preliminary step)"], skills: ["Hydrometallurgical Engineer — distillation column temperature profiling & impurity separation", "Chemical Engineer — impurity distribution modelling (Pb, Cd, Fe, Cu removal)", "Metallurgist — SHG purity verification (ASTM B6 / EN 1179)", "Process Engineer — energy efficiency & by-product recovery (Cd, Pb)", "Quality Control Engineer — trace element analysis & product certification"] },
  { id: "zn-smelt", stage: "Zinc Smelting", label: "Zinc Smelting", color: "#b56300", textColor: "#ffffff", dual: true,
    routeA: { label: "Hydrometallurgical (dominant ~85%)", inputs: ["Zinc concentrate (roasted calcine)", "Sulfuric acid (leach medium)", "Electricity (electrowinning)", "Reagents (MnO2, Sb, Cu — purification)"], technology: ["Fluidized bed roaster (ZnS to ZnO + SO2)", "Sulfuric acid plant (SO2 to H2SO4 by-product)", "Leach tanks (ZnO dissolution in H2SO4)", "Purification circuit (cementation, solvent extraction)", "Electrowinning tankhouse (Zn2+ to Zn metal on Al cathodes)"], skills: ["Hydrometallurgical Engineer — leach efficiency, pH & temperature optimisation", "Electrochemical Engineer — current efficiency & specific energy in electrowinning", "Chemical Engineer — purification circuit (Co, Ni, Cu, Cd impurity removal)", "Process Engineer — roaster feed management & SO2 emission control", "Environmental Engineer — effluent treatment & acid plant compliance"] },
    routeB: { label: "Pyrometallurgical (~15%)", inputs: ["Zinc concentrate (sintered)", "Coke / coal (reductant)", "Sinter feed (flux additions)"], technology: ["Imperial Smelting Furnace (ISF) — simultaneous Zn + Pb", "Retort distillation (horizontal / vertical)", "Lead splash condenser (zinc vapor capture)", "Sinter plant (feed preparation)"], skills: ["Pyrometallurgical Engineer — ISF tuyere zone, blast rate & coke rate management", "Metallurgist — zinc vapor condensation efficiency & lead splash condenser operation", "Refractory Engineer — high-temperature furnace lining & campaign management", "Process Engineer — simultaneous Zn/Pb separation & sinter bed management", "Mechanical Engineer — sinter plant, furnace & condenser equipment maintenance"] },
  },
  { id: "zn-conc", stage: "Mining & Concentration", label: "Zinc Ore Processing", color: "#cf7400", textColor: "#ffffff", inputs: ["Run-of-mine zinc ore (sphalerite — ZnS)", "Water (process)", "Reagents (collectors, frothers, depressants)", "Energy (crushing, grinding, pumping)"], technology: ["Underground / open-pit mining (drill + blast or TBM)", "Crushing & grinding circuit (SAG mill, ball mill)", "Froth flotation cells (selective ZnS concentration)", "Thickeners & filter press (concentrate dewatering)", "Tailings management facility"], skills: ["Mining Engineer — ore body characterisation, mine planning & drill-blast design", "Mineral Processing Engineer — grinding circuit optimisation & liberation size control", "Flotation Metallurgist — reagent suite design, pH control & grade/recovery trade-off", "Geologist — ore reserve estimation, resource classification & grade control", "Environmental Engineer — tailings disposal design & regulatory compliance"] },
  { id: "zn-raw", stage: "Raw Materials — Zinc Chain", label: "Zinc Raw Materials", color: "#7b3f00", textColor: "#ffe8cc", rawMaterials: true, items: [{ name: "Zinc Ore (Sphalerite, ZnS)", detail: "Underground / open-pit mines — often polymetallic (Zn, Pb, Ag, Cd)" }, { name: "Sulfuric Acid", detail: "Self-generated by-product of ZnS roasting — used in leaching" }, { name: "Electricity", detail: "Energy-intensive electrowinning — dominant operating cost" }, { name: "Coke / Coal", detail: "Pyrometallurgical route reductant (ISF and retort processes)" }, { name: "Process Water", detail: "Flotation, leaching, cooling — significant volume required" }] },
];

const ALZN_CHAIN = [
  { id: "alzn-bath", stage: "Coating Input", label: "Al-Zn Alloy Bath (Galvalume)", color: "#4a6741", textColor: "#ffffff", inputs: ["Aluminum (55% of bath by weight)", "Zinc (43.4% of bath)", "Silicon (1.6% — prevents alloy layer cracking)", "Energy (heat for molten alloy bath ~600 C)"], technology: ["Alloy pot (600 C — higher temp than galvanizing)", "Air knife / gas wiping (coating weight control)", "Pot roll system (sink roll, stabilizer rolls)", "In-line passivation / chemical treatment system", "Dross management system (Al-Fe intermetallics)"], skills: ["Coating Technologist — Al-Zn bath chemistry control (Al:Zn:Si ratio)", "Materials Engineer — alloy layer microstructure & corrosion barrier design", "Metallurgist — silicon distribution control & dross formation minimisation", "Process Engineer — bath temperature stability at elevated operating point", "Quality Control Engineer — coating weight, adhesion & accelerated corrosion testing"] },
  { id: "al-supply", stage: "Aluminum Supply", label: "Aluminum (Primary)", color: "#5a8055", textColor: "#ffffff", inputs: ["Alumina (Al2O3) — from Bayer process", "Carbon anodes (petroleum coke + pitch)", "Electricity (electrolysis — Hall-Heroult process)", "Cryolite bath (Na3AlF6 — molten electrolyte)", "Alloying additions (Si, Mg, Fe)"], technology: ["Hall-Heroult electrolytic reduction cell (smelting pot)", "Anode baking furnace (carbon anode production)", "Metal casting & alloying furnace", "Gas treatment centre (HF & dust capture)", "Rodding shop (anode assembly)"], skills: ["Electrochemical Engineer — cell voltage, current efficiency & bath chemistry control", "Materials Engineer — anode quality (density, reactivity) specification & management", "Metallurgist — aluminium alloy composition & casting practice", "Process Engineer — pot line energy efficiency & thermal balance optimisation", "Environmental Engineer — HF & perfluorocarbon (PFC) emission management"] },
  { id: "alumina", stage: "Alumina Refining", label: "Alumina (Bayer Process)", color: "#6b9966", textColor: "#ffffff", inputs: ["Bauxite ore (Al-hydroxide minerals)", "Caustic soda (NaOH — digestion medium)", "Steam / energy (digestion at 140-240 C)", "Lime (CaO — impurity removal)", "Flocculants (red mud settling)"], technology: ["Digestion circuit (high-pressure vessels)", "Red mud separation (thickeners & filtration)", "Precipitation tanks (Al hydroxide crystallisation)", "Calcination kiln (Al(OH)3 to Al2O3 at 1,000 C)", "Red mud storage & disposal facility"], skills: ["Chemical Engineer — Bayer circuit chemistry, caustic recovery & yield optimisation", "Process Engineer — digestion temperature, pressure & residence time management", "Minerals Engineer — bauxite characterisation & blend optimisation", "Environmental Engineer — red mud (bauxite residue) management & disposal", "Materials Engineer — alumina particle size, surface area & purity specification"] },
  { id: "bauxite", stage: "Raw Materials — Aluminum Chain", label: "Aluminum Raw Materials", color: "#2d5a29", textColor: "#e8ffe6", rawMaterials: true, items: [{ name: "Bauxite Ore", detail: "Gibbsite / boehmite / diaspore — open-pit mined in tropical laterite deposits" }, { name: "Caustic Soda (NaOH)", detail: "Chemical input for Bayer digestion — largely recycled in circuit" }, { name: "Electricity", detail: "Dominant cost in Hall-Heroult smelting — 13-15 MWh per tonne Al" }, { name: "Petroleum Coke", detail: "Carbon anode raw material — from oil refinery by-product streams" }, { name: "Coal Tar Pitch", detail: "Anode binder — coal distillation by-product" }] },
];

const TIN_CHAIN = [
  { id: "tin-coat", stage: "Coating Input", label: "Tin / Chromium Coating", color: "#374151", textColor: "#ffffff", inputs: ["Tin anodes or tin salts (tinplate — electrolytic deposition)", "Chromic acid / chromium salts (ECCS — electrolytic Cr/CrOx)", "Sulfuric acid / MSA electrolyte solution", "Passivation chemicals (sodium dichromate)", "Food-grade lacquer (applied post-tinning)"], technology: ["Electrolytic tinning line (high-speed, up to 600 m/min)", "Tin melting / flow-brightening unit (reflowing for bright finish)", "Chromate passivation unit", "Differential coating weight system (DS tinplate)", "ECCS electrolytic chromium coating line"], skills: ["Coating Technologist — tin coating weight uniformity & electrolyte bath management", "Electrochemical Engineer — current density, electrolyte composition & tin distribution", "Materials Engineer — FeSn2 alloy layer specification & porosity control", "Food Packaging Engineer — food-contact compliance & lacquer adhesion testing", "Quality Control Engineer — porosity (Enamel Rater), lacquer adhesion & corrosion testing"] },
  { id: "tin-refine", stage: "Tin Refining", label: "Tin Refining", color: "#4b5563", textColor: "#ffffff", inputs: ["Crude tin from smelting (97-99% Sn)", "Energy (electrolytic refining or fire refining)", "Reagents (Cl2, S — removing Pb, As, Cu, Fe)"], technology: ["Fire refining (liquation, boiling, tossing — removes Pb, As, Cu)", "Electrolytic refining (high-purity tin on stainless steel cathodes)", "Centrifugal casting (tin anode production for electrolytic lines)"], skills: ["Pyrometallurgical Engineer — fire refining operations & impurity removal sequencing", "Electrochemical Engineer — electrolytic refining cell design & current efficiency", "Metallurgist — tin purity specification (BS EN ISO 9453 / ASTM B339)", "Chemical Engineer — electrolyte management & slime (by-product) processing", "Quality Control Engineer — trace impurity analysis (Pb, As, Bi, Sb limits)"] },
  { id: "tin-smelt", stage: "Tin Smelting", label: "Tin Smelting", color: "#6b7280", textColor: "#ffffff", inputs: ["Tin concentrate (cassiterite — SnO2)", "Coal / coke (reductant)", "Limestone flux", "Iron scrap (slag fuming — recovery)"], technology: ["Reverberatory furnace or electric furnace (primary smelting)", "Slag fuming furnace (tin recovery from slag)", "Converter (impurity removal — Pb, As)", "Dross treatment system"], skills: ["Pyrometallurgical Engineer — furnace temperature, slag chemistry & tin recovery", "Metallurgist — concentrate blend optimisation & impurity management", "Refractory Engineer — furnace lining design for tin smelting conditions", "Chemical Engineer — slag fuming operations & tin recovery maximisation", "Process Engineer — energy efficiency & by-product (Pb, slag) management"] },
  { id: "tin-mine", stage: "Mining & Concentration", label: "Tin Ore Processing", color: "#9ca3af", textColor: "#1f2937", inputs: ["Cassiterite ore (SnO2 — primary tin mineral)", "Water (alluvial / hydraulic mining)", "Energy (crushing, gravity separation)", "Reagents (flotation — sulphide tin ores)"], technology: ["Alluvial dredging / hydraulic mining (primary tin source)", "Hard rock underground / open-pit mining (primary cassiterite)", "Gravity separation (jigs, spirals, shaking tables)", "Flotation (sulphide tin ores — stannite)", "Magnetic separation (removal of iron minerals)"], skills: ["Mining Engineer — alluvial dredge operation or hard rock mine planning", "Mineral Processing Engineer — gravity circuit optimisation (high SG of cassiterite)", "Flotation Metallurgist — sulphide tin ore beneficiation", "Geologist — placer deposit evaluation & alluvial reserve estimation", "Environmental Engineer — tailings management & land rehabilitation"] },
  { id: "tin-raw", stage: "Raw Materials — Tin Chain", label: "Tin Raw Materials", color: "#374151", textColor: "#f3f4f6", rawMaterials: true, items: [{ name: "Cassiterite Ore (SnO2)", detail: "Primary tin mineral — alluvial placers & hard rock pegmatites (Indonesia, China, Myanmar, Bolivia)" }, { name: "Coal / Coke", detail: "Reductant for cassiterite smelting in reverberatory / electric furnaces" }, { name: "Electricity", detail: "Electric furnace smelting & electrolytic refining" }, { name: "Limestone", detail: "Flux for slag formation in primary tin smelting" }, { name: "Water", detail: "Hydraulic mining & gravity separation — alluvial operations" }] },
];

const PAINT_CHAIN = [
  { id: "paint-app", stage: "Coating Input", label: "Organic Paint / Coating System", color: "#7c3aed", textColor: "#ffffff", inputs: ["Primer coat (polyester / epoxy base)", "Topcoat (polyester, PVDF, polyurethane resins)", "Pigments (TiO2 for white, organic pigments for colour)", "Cross-linking agents (melamine, isocyanate)", "Solvents (aromatic hydrocarbons — largely replaced by waterborne)", "Pre-treatment chemicals (chromate-free conversion coating)"], technology: ["Coil coating line (roll coat application — up to 200 m/min)", "Curing oven (convection + induction — PMT 215-232 C)", "Pre-treatment section (alkaline clean, rinse, conversion coat)", "Cooling section (quench water or forced air after oven)", "In-line spectrometer (colour & gloss measurement)"], skills: ["Coating Technologist — paint formulation, viscosity control & film weight uniformity", "Chemical Engineer — curing oven temperature profile & PMT management", "Materials Engineer — paint adhesion, flexibility (T-bend) & weatherability specification", "Colour Technologist — colour matching, gloss measurement & metamerism control", "Quality Control Engineer — cross-cut adhesion, reverse impact, salt spray & UV weathering tests"] },
  { id: "resin", stage: "Resin / Polymer Production", label: "Coating Resins", color: "#8b5cf6", textColor: "#ffffff", inputs: ["Purified terephthalic acid (PTA) — polyester base", "Ethylene glycol (polyester monomer)", "Vinylidene fluoride monomer (PVDF resins)", "Isocyanate compounds (polyurethane)", "Melamine (cross-linking agent)"], technology: ["Polyester condensation reactor (PTA + ethylene glycol)", "PVDF polymerisation reactor (emulsion / suspension)", "Resin blending & quality testing facility", "Solvent recovery & recycling system", "Pigment dispersion mill (bead mill / roll mill)"], skills: ["Polymer Chemist — resin polymerisation, molecular weight & viscosity control", "Chemical Engineer — reactor design, monomer conversion & by-product management", "Materials Engineer — resin weatherability, UV resistance & flexibility specification", "Process Engineer — solvent recovery efficiency & VOC emission management", "Quality Control Engineer — resin viscosity, acid value & colour specification"] },
  { id: "petrochem", stage: "Petrochemical Feedstocks", label: "Petrochemical Inputs", color: "#a78bfa", textColor: "#1f2937", inputs: ["Paraxylene (PX) — oxidised to PTA (polyester feedstock)", "Ethylene — to ethylene glycol (EG)", "Fluorite (CaF2) + HF — vinylidene fluoride (PVDF precursor)", "Toluene diisocyanate (TDI) — polyurethane feedstock", "Titanium dioxide (TiO2) — white pigment (from ilmenite / rutile)"], technology: ["Paraxylene extraction (aromatics complex — naphtha reforming)", "PTA oxidation reactor (PX to PTA via CoBr catalyst)", "Ethylene glycol plant (EO hydration)", "Fluorochemical plant (HF + monomer to VDF)", "TiO2 plant (sulphate or chloride process)"], skills: ["Petrochemical Engineer — aromatics complex operation & paraxylene separation", "Chemical Engineer — oxidation reactor design, catalyst management & yield optimisation", "Process Engineer — fluorochemical plant HF safety & containment management", "Materials Engineer — TiO2 pigment particle size, opacity & durability specification", "Environmental Engineer — VOC, HF & process emission compliance management"] },
  { id: "paint-raw", stage: "Raw Materials — Paint Chain", label: "Paint & Resin Raw Materials", color: "#5b21b6", textColor: "#ede9fe", rawMaterials: true, items: [{ name: "Crude Oil / Naphtha", detail: "Petrochemical feedstock base — aromatics complex for paraxylene production" }, { name: "Natural Gas / Ethylene", detail: "Ethylene glycol monomer for polyester resin synthesis" }, { name: "Fluorite (CaF2)", detail: "Mineral feedstock for PVDF fluoropolymer resin production" }, { name: "Ilmenite / Rutile", detail: "Titanium ore — source of TiO2 white pigment (sulphate or chloride process)" }, { name: "Solvents", detail: "Aromatic & aliphatic solvents — largely transitioning to waterborne systems" }] },
];
const HRC_NODE = (id) => ({ id, stage: "Hot Rolling", label: "Hot-Rolled Coil", color: "#235991", textColor: "#ffffff", inputs: ["Slab (reheated to ~1,200-1,250 C)", "Energy (natural gas for reheating furnaces)", "Work rolls & backup rolls", "High-pressure descaling water", "Coiling lubricants"], technology: ["Walking beam / pusher-type slab reheating furnace", "Roughing mill (breakdown passes)", "Finishing mill (5-7 tandem stands)", "Runout table laminar cooling system", "Downcoiler (coiling at 550-750 C)"], skills: ["Rolling Mill Process Engineer — pass schedule, reduction & temperature sequencing", "Metallurgist — FDT & CT control for target microstructure", "Mechanical Engineer — roll crown & flatness control (CVC, roll bending)", "Thermal Engineer — reheating furnace combustion optimisation & scale control", "Materials Engineer — mechanical property targeting across steel grades"] });
const CRC_NODE = (id) => ({ id, stage: "Cold Rolling", label: "Cold-Rolled Coil", color: "#1e4976", textColor: "#ffffff", inputs: ["Hot-rolled coil (pickled & oiled)", "Rolling lubricants / emulsions", "Pickling acids (HCl — remove mill scale)", "Electricity", "Nitrogen / inert gas (annealing atmosphere)"], technology: ["Tandem cold mill (TCM) — 4 or 6-hi rolling stands in series", "Reversing cold mill (single stand, multiple passes)", "Continuous annealing line (CAL) — rapid cycle", "Batch annealing furnace (BAF) — deep drawing grades", "Temper / skin-pass mill (surface finish & flatness)"], skills: ["Metallurgist — recrystallization & grain growth control during annealing", "Rolling Mill Process Engineer — gauge, flatness & inter-stand tension control", "Materials Engineer — mechanical property specification (YS, TS, elongation)", "Surface Quality Engineer — roughness Ra, cleanliness & defect classification", "Electrical & Automation Engineer — mill drive systems & process control loops"] });

const PRODUCTS = {
  galvanized: {
    id: "galvanized", name: "Galvanized Sheet", category: "Coated Flat", color: "#1a3a5c",
    description: "Cold-rolled steel with zinc coating applied by hot-dip or electrolytic process. Primary use: construction, automotive, appliances.",
    chains: [
      { title: "Steel Base Chain", accent: "#1a3a5c", nodes: [
        { id: "galv-top", stage: "Finished Mill Product", label: "Galvanized Sheet", color: "#1a3a5c", textColor: "#ffffff", inputs: ["Cold-rolled coil (base substrate)", "Zinc ingots — SHG grade (99.995%)", "Aluminum additive (0.2% in bath)", "Flux / pickling acids (HCl, H2SO4)", "Energy (heat for bath / electricity for electrolytic line)"], technology: ["Continuous hot-dip galvanizing line (Sendzimir process)", "Electrogalvanizing line (electrolytic deposition)", "Air-knife wiping system (controls coating weight g/m2)", "Tension levelling & skin-pass mill (flatness/surface)", "In-line annealing furnace (recrystallization before coating)"], skills: ["Coating Technologist — bath chemistry, coating weight & uniformity control", "Materials Engineer — substrate-coating compatibility & intermetallic layer design", "Metallurgist — spangle morphology control & surface quality specification", "Quality Control Engineer — adhesion, bend & corrosion resistance testing", "Process Engineer — line speed optimisation & annealing cycle management"] },
        CRC_NODE("galv-crc"), HRC_NODE("galv-hrc"), SLAB_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
      { title: "Zinc Coating Chain", accent: "#7b3f00", nodes: ZINC_CHAIN },
    ],
  },
  galvalume: {
    id: "galvalume", name: "Galvalume / Aluzinc", category: "Coated Flat", color: "#2d5a29",
    description: "Cold-rolled steel coated with aluminum-zinc-silicon alloy (55% Al / 43.4% Zn / 1.6% Si). Superior corrosion resistance. Primary use: roofing, cladding, appliance panels.",
    chains: [
      { title: "Steel Base Chain", accent: "#1a3a5c", nodes: [
        { id: "gv-top", stage: "Finished Mill Product", label: "Galvalume / Aluzinc Sheet", color: "#2d5a29", textColor: "#ffffff", inputs: ["Cold-rolled coil (base substrate)", "Aluminum (55% of bath by weight)", "Zinc (43.4% of bath)", "Silicon (1.6% — prevents alloy layer cracking)", "Energy (heat for molten alloy bath ~600 C)"], technology: ["Continuous hot-dip Al-Zn coating line (higher bath temp than galvanizing)", "Air knife / gas wiping system (coating weight control)", "In-line passivation / chemical treatment system", "Tension levelling & skin-pass mill", "Dross management system (Al-Fe intermetallics)"], skills: ["Coating Technologist — Al-Zn-Si bath chemistry & temperature control", "Materials Engineer — alloy layer microstructure, corrosion barrier & adhesion design", "Metallurgist — silicon distribution control & dross formation minimisation", "Process Engineer — bath temperature stability at elevated operating point (~600 C)", "Quality Control Engineer — coating weight, adhesion & accelerated corrosion testing"] },
        CRC_NODE("gv-crc"), HRC_NODE("gv-hrc"), SLAB_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
      { title: "Aluminum-Zinc Chain", accent: "#2d5a29", nodes: ALZN_CHAIN },
    ],
  },
  prepainted: {
    id: "prepainted", name: "Pre-painted / Color-Coated Coil", category: "Coated Flat", color: "#7c3aed",
    description: "Galvanized or Galvalume base coil with organic paint system applied on a coil coating line. Primary use: roofing, cladding, domestic appliances, automotive interiors.",
    chains: [
      { title: "Steel Base Chain", accent: "#1a3a5c", nodes: [
        { id: "pp-top", stage: "Finished Mill Product", label: "Pre-painted / Color-Coated Coil", color: "#7c3aed", textColor: "#ffffff", inputs: ["Galvanized or Galvalume base coil", "Primer coat (polyester / epoxy)", "Topcoat (polyester, PVDF, polyurethane)", "Pre-treatment chemicals (chromate-free conversion coating)", "Solvents, pigments & cross-linking agents"], technology: ["Coil coating line (roll coat application — up to 200 m/min)", "Curing oven (convection + induction — PMT 215-232 C)", "Pre-treatment section (alkaline clean, rinse, conversion coat)", "Cooling section (quench water or forced air)", "In-line spectrometer (colour & gloss measurement)"], skills: ["Coating Technologist — paint formulation, viscosity control & film weight uniformity", "Chemical Engineer — curing oven temperature profile & PMT management", "Materials Engineer — paint adhesion, flexibility (T-bend) & weatherability specification", "Colour Technologist — colour matching, gloss measurement & metamerism control", "Quality Control Engineer — cross-cut adhesion, reverse impact, salt spray & UV weathering"] },
        { id: "pp-base", stage: "Metallic Base Coil", label: "Galvanized / Galvalume Base", color: "#1a3a5c", textColor: "#ffffff", inputs: ["Cold-rolled coil (substrate)", "Zinc or Al-Zn coating (as per galvanized / galvalume route)", "See Galvanized or Galvalume decomposition for full inputs"], technology: ["Hot-dip galvanizing line or Al-Zn coating line", "Full decomposition: see Galvanized / Galvalume product in selector"], skills: ["Coating Technologist — metallic base coat quality specification", "Materials Engineer — base coating compatibility with organic topcoat system", "See Galvanized / Galvalume product for full professional chain"] },
        CRC_NODE("pp-crc"), HRC_NODE("pp-hrc"), SLAB_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
      { title: "Paint & Resin Chain", accent: "#7c3aed", nodes: PAINT_CHAIN },
    ],
  },
  tinplate: {
    id: "tinplate", name: "Tinplate / Tin-Free Steel (ECCS)", category: "Coated Flat", color: "#374151",
    description: "Cold-rolled steel with electrolytic tin (tinplate) or electrolytic chromium/oxide coating (ECCS/TFS). Primary use: food & beverage cans, aerosols, closures.",
    chains: [
      { title: "Steel Base Chain", accent: "#1a3a5c", nodes: [
        { id: "tp-top", stage: "Finished Mill Product", label: "Tinplate / ECCS", color: "#374151", textColor: "#ffffff", inputs: ["Cold-rolled blackplate (thin gauge, 0.10-0.49mm)", "Tin anodes or tin salts (tinplate)", "Chromic acid / chromium salts (ECCS / TFS)", "Sulfuric acid / MSA electrolyte", "Passivation chemicals (sodium dichromate)", "Food-grade lacquer (applied post-tinning)"], technology: ["Electrolytic tinning line (high-speed, up to 600 m/min)", "Tin melting / flow-brightening (reflowing — bright finish)", "Chromate passivation unit", "Differential coating weight system (DS tinplate)", "ECCS electrolytic chromium coating line"], skills: ["Coating Technologist — tin coating weight uniformity & electrolyte bath management", "Electrochemical Engineer — current density, electrolyte composition & tin distribution", "Materials Engineer — FeSn2 alloy layer specification & porosity control", "Food Packaging Engineer — food-contact compliance & lacquer adhesion testing", "Quality Control Engineer — porosity (Enamel Rater), lacquer adhesion & corrosion testing"] },
        { id: "tp-bp", stage: "Cold Rolling (Blackplate)", label: "Blackplate (Cold-Rolled)", color: "#1e4976", textColor: "#ffffff", inputs: ["Hot-rolled coil (pickled & oiled)", "Rolling lubricants / emulsions", "Pickling acids (HCl)", "Electricity", "Inert gas (annealing atmosphere)"], technology: ["Tandem cold mill (TCM — thin gauge)", "Double reduction mill (DR — 2nd cold reduction for ultra-thin)", "Continuous annealing line (CAL)", "Batch annealing furnace (BAF)", "Temper mill (controlled elongation)"], skills: ["Metallurgist — ultra-thin gauge recrystallization & earing control", "Rolling Mill Process Engineer — gauge uniformity to +/-2 micron tolerances", "Materials Engineer — hardness (HR30T), earing & mechanical property specification", "Surface Quality Engineer — tin mill product surface defect classification", "Process Engineer — double reduction schedule for DR tinplate grades"] },
        HRC_NODE("tp-hrc"), SLAB_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
      { title: "Tin / Chromium Chain", accent: "#374151", nodes: TIN_CHAIN },
    ],
  },
  coldrolled: {
    id: "coldrolled", name: "Cold-Rolled Coil / Sheet", category: "Cold-Rolled Flat", color: "#1e4976",
    description: "Hot-rolled coil cold-reduced at room temperature for thinner gauge, tighter tolerances and smoother surface. Primary use: automotive body panels, appliances, electrical steel.",
    chains: [
      { title: "Steel Chain", accent: "#1a3a5c", nodes: [
        { id: "crc-top", stage: "Finished Mill Product", label: "Cold-Rolled Coil / Sheet", color: "#1e4976", textColor: "#ffffff", inputs: ["Hot-rolled coil (pickled & oiled — scale-free surface)", "Rolling lubricants / emulsions", "Pickling acids (HCl — scale removal before cold reduction)", "Electricity (rolling mill drives & annealing)", "Nitrogen / hydrogen / inert gas (annealing atmosphere)"], technology: ["Pickling line & tandem cold mill (PL-TCM — combined unit)", "Tandem cold mill (TCM) — 4 or 6-hi rolling stands in series", "Reversing cold mill (RCM — smaller volumes, specialty grades)", "Continuous annealing line (CAL) — tight mechanical property control", "Batch annealing furnace (BAF) — deep drawing & extra-deep drawing grades", "Temper / skin-pass mill — final surface finish, flatness & yield point elimination"], skills: ["Metallurgist — recrystallization, grain growth & texture control during annealing", "Rolling Mill Process Engineer — gauge, flatness, shape & inter-stand tension control", "Materials Engineer — mechanical property specification (YS, TS, elongation, n-value, r-value)", "Surface Quality Engineer — roughness Ra specification, cleanliness & defect classification", "Electrical & Automation Engineer — mill drive systems, AGC & flatness measurement systems"] },
        HRC_NODE("crc-hrc"), SLAB_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  hotrolled: {
    id: "hotrolled", name: "Hot-Rolled Coil / Sheet / Strip", category: "Hot-Rolled Flat", color: "#235991",
    description: "Steel slab rolled at high temperature into coil, sheet or strip. Primary use: automotive structural, general fabrication, pipe-making strip, welded tube.",
    chains: [
      { title: "Steel Chain", accent: "#1a3a5c", nodes: [
        { id: "hrc-top", stage: "Finished Mill Product", label: "Hot-Rolled Coil / Sheet / Strip", color: "#235991", textColor: "#ffffff", inputs: ["Slab (reheated to ~1,200-1,250 C)", "Energy (natural gas for reheating furnaces)", "Work rolls & backup rolls (HSS, ICDP grades)", "High-pressure descaling water (remove oxide scale)", "Coiling lubricants / coolants"], technology: ["Walking beam / pusher-type slab reheating furnace", "Edger & vertical scale breaker", "Roughing mill (2-hi or 4-hi — 5-8 breakdown passes)", "Finishing mill (5-7 tandem 4-hi / 6-hi stands)", "Runout table laminar cooling system (controlled microstructure)", "Downcoiler / carrousel coiler (coiling at 550-750 C)", "Steckel mill (reversing — for specialty alloys & stainless)"], skills: ["Rolling Mill Process Engineer — pass schedule design, reduction per pass & interpass temperature control", "Metallurgist — FDT & CT control for target microstructure (ferritic, bainitic, multiphase)", "Mechanical Engineer — roll crown, flatness control (CVC, roll bending, shifting)", "Thermal Engineer — reheating furnace combustion optimisation, scale formation control & energy efficiency", "Materials Engineer — steel grade portfolio management (HSLA, API, structural, dual-phase)"] },
        SLAB_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  plate: {
    id: "plate", name: "Plate", category: "Hot-Rolled Flat", color: "#1d4e8f",
    description: "Heavy gauge flat steel (>6mm) rolled from slab on a plate mill. Primary use: shipbuilding, pressure vessels, bridges, offshore structures, heavy machinery.",
    chains: [
      { title: "Steel Chain", accent: "#1a3a5c", nodes: [
        { id: "plate-top", stage: "Finished Mill Product", label: "Plate", color: "#1d4e8f", textColor: "#ffffff", inputs: ["Slab (thicker section vs. strip slab — up to 350mm)", "Energy (natural gas for reheating furnaces)", "Work rolls & backup rolls", "Descaling water (high-pressure)", "Quench water (for TMCP / quench & temper grades)"], technology: ["Reversing plate mill (4-hi — single slab, reversing passes)", "Controlled rolling system (TMCP — thermomechanical controlled processing)", "Accelerated cooling system (ACS — water spray after rolling)", "Quench & temper furnace (Q&T grades — offshore, pressure vessel)", "Flatness correction press (roller leveller — heavy plate)", "Ultrasonic testing system (UT — lamination & internal flaw detection)"], skills: ["Metallurgist — TMCP schedule design (controlled rolling + accelerated cooling for high toughness)", "Rolling Mill Process Engineer — pass schedule, reduction & inter-pass temperature in reversing mill", "Materials Engineer — plate toughness (CTOD, Charpy) & weldability specification for structural / offshore grades", "NDT Engineer — ultrasonic testing, TOFD & phased array inspection of plate internal quality", "Heat Treatment Engineer — quench & temper cycle design for high-strength grades (S690, S890)"] },
        SLAB_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  rebar: {
    id: "rebar", name: "Rebar (Reinforcing Bar)", category: "Long Products", color: "#92400e",
    description: "Deformed steel bar rolled from billet. Primary use: concrete reinforcement in buildings, bridges, tunnels and infrastructure.",
    chains: [
      { title: "Steel Chain", accent: "#92400e", nodes: [
        { id: "rb-top", stage: "Finished Mill Product", label: "Rebar", color: "#92400e", textColor: "#ffffff", inputs: ["Billet (reheated to ~1,100-1,150 C)", "Energy (natural gas for reheating furnace)", "Work rolls (with deformation grooves for ribs & lugs)", "Water quench (for QST / Tempcore self-tempering process)", "Roll rings & guides"], technology: ["Walking beam billet reheating furnace", "Roughing, intermediate & finishing rolling mill stands (long product)", "Water quench box (Tempcore / QST — quench & self-temper for high yield strength)", "Flying shear (cut to length)", "Cold bed (cooling & straightening)", "Bar counting & bundling system"], skills: ["Rolling Mill Process Engineer — billet rolling schedule, pass design & speed sequencing", "Metallurgist — QST process control (quench intensity, self-tempering temperature for 500 MPa+ yield)", "Materials Engineer — rebar grade specification (BS 4449, ASTM A615/A706, ISO 6935-2)", "Quality Control Engineer — yield strength, TS, elongation, bend & rebend testing", "Structural Engineer (product application) — seismic-grade rebar specification (B500C / A706)"] },
        BILLET_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  wirerod: {
    id: "wirerod", name: "Wire Rod", category: "Long Products", color: "#b45309",
    description: "Small-diameter rod (5-20mm) coiled at high speed from billet. Primary use: downstream drawing into wire, welding wire, fasteners, spring wire, PC strand.",
    chains: [
      { title: "Steel Chain", accent: "#b45309", nodes: [
        { id: "wr-top", stage: "Finished Mill Product", label: "Wire Rod", color: "#b45309", textColor: "#ffffff", inputs: ["Billet (reheated to ~1,050-1,100 C)", "Energy (natural gas for reheating furnace)", "High-speed rolling rolls (carbide / HSS)", "Water cooling (inter-block controlled cooling)", "Stelmor air cooling conveyor"], technology: ["Walking beam billet reheating furnace", "Roughing & intermediate mill (high-speed long product mill)", "Pre-finishing & finishing block (10-stand no-twist finishing block — up to 120 m/s)", "Laying head (coil formation at high speed)", "Stelmor controlled cooling conveyor (air & fan cooling for microstructure control)", "Coil handling & compaction system"], skills: ["Rolling Mill Process Engineer — high-speed rolling schedule, pass design & no-twist block management", "Metallurgist — Stelmor cooling curve control (pearlite, bainite or martensite for downstream application)", "Materials Engineer — wire rod grade portfolio (SAE 1008 general, SAE 1080 PC strand, SBQ grades)", "Quality Control Engineer — mechanical properties (UTS, reduction of area), surface quality & scale weight", "Wire Drawing Engineer — rod surface quality & decarburisation depth specification for downstream drawing"] },
        BILLET_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  merchantbar: {
    id: "merchantbar", name: "Merchant Bar", category: "Long Products", color: "#78350f",
    description: "Standard bar sections (rounds, flats, squares, angles, hexagons) rolled from billet. Primary use: general engineering, fabrication, machining, construction.",
    chains: [
      { title: "Steel Chain", accent: "#78350f", nodes: [
        { id: "mb-top", stage: "Finished Mill Product", label: "Merchant Bar", color: "#78350f", textColor: "#ffffff", inputs: ["Billet (reheated to ~1,100-1,150 C)", "Energy (natural gas for reheating furnace)", "Work rolls (shaped grooves for section profiles)", "Cooling water", "Cutting & bundling consumables"], technology: ["Walking beam billet reheating furnace", "Roughing, intermediate & finishing mill stands", "Universal rolling stand (for flat & angle sections)", "Cooling bed (gravity or mechanical walking beam type)", "Cold saw / flying shear (cut to bar length)", "Bar straightening machine", "Bundling & weighing system"], skills: ["Rolling Mill Process Engineer — bar rolling pass sequence & profile tolerance management", "Metallurgist — controlled cooling for mechanical property targeting (normalised vs. as-rolled)", "Materials Engineer — multi-section grade portfolio specification (S235, S355, bright drawn tolerances)", "Quality Control Engineer — dimensional inspection, surface quality & mechanical property testing", "Technical Sales Engineer — customer section selection, tolerance & surface finish specification"] },
        BILLET_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  structural: {
    id: "structural", name: "Structural Sections (I/H-beam, Channel, Angle)", category: "Long Products", color: "#1e3a5f",
    description: "Heavy structural profiles rolled from bloom. Primary use: building frames, bridges, industrial structures, crane rails.",
    chains: [
      { title: "Steel Chain", accent: "#1e3a5f", nodes: [
        { id: "str-top", stage: "Finished Mill Product", label: "Structural Sections", color: "#1e3a5f", textColor: "#ffffff", inputs: ["Bloom (reheated to ~1,200-1,250 C)", "Energy (natural gas for reheating furnace)", "Universal rolling rolls (horizontal & vertical stands)", "Cooling water", "Cutting & stacking consumables"], technology: ["Walking beam bloom reheating furnace", "Breakdown rolling mill (reducing bloom to dog-bone shape)", "Universal mill (H/V stands — simultaneous web & flange rolling)", "Edger stands (flange width control)", "Cooling bed (gravity or mechanical)", "Cold saw (cut to beam length)", "Roller straightener", "Cambering press (optional — pre-camber for bridge beams)"], skills: ["Rolling Mill Process Engineer — universal mill pass schedule, web/flange reduction & dog-bone design", "Metallurgist — controlled cooling for structural grade properties (S355, S420, S460)", "Materials Engineer — section modulus, toughness (Charpy) & weldability specification for structural use", "NDT Engineer — ultrasonic testing of flanges & web for lamination & surface crack detection", "Structural Engineer (product application) — section selection & connection design for steel frame structures"] },
        BLOOM_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  rail: {
    id: "rail", name: "Rail", category: "Long Products", color: "#374151",
    description: "Heavy section rolled from bloom to precise rail profile (head, web, foot). Primary use: railway track (main line, metro, tram, crane rail).",
    chains: [
      { title: "Steel Chain", accent: "#374151", nodes: [
        { id: "rl-top", stage: "Finished Mill Product", label: "Rail", color: "#374151", textColor: "#ffffff", inputs: ["Bloom (reheated to ~1,200-1,250 C — clean steel essential)", "Energy (natural gas for reheating furnace)", "Profiling rolls (rail head, web & foot)", "Head hardening quench water (for premium head-hardened rail)", "Straightening consumables"], technology: ["Walking beam bloom reheating furnace", "Breakdown, intermediate & finishing rolling mill (rail profile)", "Accelerated cooling / head hardening unit (for pearlitic head hardened rail — 370-400 HBW)", "Roller straightener (vertical & horizontal — rail straightness to 1mm/m spec)", "Rail end finishing (drilling, sawing, grinding)", "Ultrasonic & eddy current testing (full-length automated NDT)", "Length measurement & marking system"], skills: ["Rolling Mill Process Engineer — rail rolling pass schedule, profile tolerance & finishing temperature control", "Metallurgist — head hardening process control (pearlite interlamellar spacing for wear & RCF resistance)", "Materials Engineer — rail grade specification (EN 13674: 260, 320, 350HT, 400UHC — wear & fatigue)", "NDT Engineer — automated UT, eddy current & profile measurement for 100% rail length inspection", "Track Engineer (product application) — rail selection, weld specification & maintenance regime"] },
        BLOOM_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  sheetpiling: {
    id: "sheetpiling", name: "Sheet Piling", category: "Long Products", color: "#065f46",
    description: "Hot-rolled interlocking steel sections (Z, U or flat profile) driven into ground to form retaining walls, cofferdams and flood defences.",
    chains: [
      { title: "Steel Chain", accent: "#065f46", nodes: [
        { id: "spil-top", stage: "Finished Mill Product", label: "Sheet Piling", color: "#065f46", textColor: "#ffffff", inputs: ["Bloom (reheated to ~1,200-1,250 C)", "Energy (natural gas for reheating furnace)", "Profiling rolls (Z, U or flat section with interlock geometry)", "Cooling water", "Cutting & stacking consumables"], technology: ["Walking beam bloom reheating furnace", "Breakdown rolling mill (initial section reduction)", "Universal mill / dedicated sheet pile mill (profile with integral interlock rolling)", "Cooling bed", "Cold saw (cut to pile length)", "Roller straightener", "Shot blasting & painting line (corrosion protection for permanent works)"], skills: ["Rolling Mill Process Engineer — sheet pile rolling pass schedule & interlock geometry tolerance control", "Metallurgist — section cooling control for structural grade properties (S270GP, S355GP, S430GP)", "Materials Engineer — section modulus, interlock strength & corrosion resistance specification", "Geotechnical Engineer (product application) — pile section selection, driving resistance & wall design", "NDT Engineer — dimensional inspection of interlock geometry & surface quality assessment"] },
        BLOOM_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  weldedpipe: {
    id: "weldedpipe", name: "Welded Pipe / Tube", category: "Tubular Products", color: "#1e3a8a",
    description: "Pipe formed by rolling flat strip / coil into a cylinder and welding the seam (ERW, LSAW or HSAW). Primary use: line pipe (oil & gas), structural hollow sections, water & gas distribution.",
    chains: [
      { title: "Steel Chain", accent: "#1a3a5c", nodes: [
        { id: "wp-top", stage: "Finished Mill Product", label: "Welded Pipe / Tube", color: "#1e3a8a", textColor: "#ffffff", inputs: ["Hot-rolled coil / strip or plate (skelp)", "Welding consumables (submerged arc flux & wire for LSAW/HSAW)", "Electricity (ERW — high-frequency induction or contact welding)", "Coating materials (FBE, 3LPE — for buried line pipe)", "Non-destructive testing consumables"], technology: ["ERW pipe mill (high-frequency welding — structural & small OD line pipe)", "LSAW mill (longitudinal submerged arc weld — large diameter, thick wall)", "HSAW / SSAW mill (helical submerged arc weld — large diameter, thinner wall)", "Seam annealing unit (ERW — post-weld heat treatment of weld seam)", "Hydrostatic test press (pressure test to API / EN standards)", "FBE / 3LPE coating line (external corrosion protection)", "Ultrasonic & X-ray weld inspection system"], skills: ["Welding Engineer — weld procedure qualification (WPS/PQR), heat input & HAZ property control", "Rolling Mill Process Engineer — strip forming, sizing & ovality control in pipe mill", "Materials Engineer — line pipe grade specification (API 5L X52-X80, sour service HIC-resistant)", "NDT Engineer — automated UT, X-ray & eddy current inspection of weld seam & pipe body", "Coating Engineer — FBE / 3LPE application, adhesion & holiday testing for buried service"] },
        HRC_NODE("wp-hrc"), SLAB_STAGE, BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
  seamlesspipe: {
    id: "seamlesspipe", name: "Seamless Pipe", category: "Tubular Products", color: "#1e40af",
    description: "Pipe formed without a weld seam by piercing and rolling a solid round billet. Primary use: OCTG (oil country tubular goods), high-pressure boiler tubes, process plant piping.",
    chains: [
      { title: "Steel Chain", accent: "#1a3a5c", nodes: [
        { id: "sp2-top", stage: "Finished Mill Product", label: "Seamless Pipe", color: "#1e40af", textColor: "#ffffff", inputs: ["Round billet (reheated to ~1,200-1,250 C)", "Energy (natural gas for reheating furnace)", "Piercing mill tooling (piercing plug & rolls)", "Mandrel bar (plug mill / mandrel mill)", "Sizing / stretch-reducing mill rolls"], technology: ["Rotary hearth / walking beam billet reheating furnace", "Rotary piercer (Mannesmann process — cross-roll piercing of billet)", "Plug mill or mandrel mill (elongation & wall thickness reduction)", "Stretch-reducing mill (final OD & WT control — no mandrel)", "Normalising / quench & temper furnace (heat treatment for OCTG grades)", "Hydrostatic test press (API / EN pressure test)", "Ultrasonic & electromagnetic inspection system (full body & ends)"], skills: ["Rolling Mill Process Engineer — piercing & elongation mill setup, pass design & wall thickness uniformity", "Metallurgist — heat treatment cycle design (N, Q&T) for OCTG grade mechanical properties & SSC resistance", "Materials Engineer — OCTG grade specification (API 5CT: J55, L80, P110, Q125 — burst, collapse, tension)", "NDT Engineer — UT, EMI & hydrostatic inspection for API PSL-2 & PSL-3 requirements", "Petroleum Engineer (product application) — casing & tubing design for downhole pressure, temperature & corrosion"] },
        { id: "sp2-billet", stage: "Round Billet Casting", label: "Round Billet", color: "#2769ab", textColor: "#ffffff", inputs: ["Liquid steel (from ladle)", "Mold powder / flux", "Cooling water", "Argon gas (SEN purging)"], technology: ["Continuous round billet caster (circular section — 150-400mm diameter)", "Electromagnetic stirring (EMS — centre quality)", "Tundish with metering nozzle", "Mold level control system"], skills: ["Metallurgist — billet centre porosity & segregation minimisation (critical for seamless piercing)", "Process Engineer — casting speed, superheat & cooling management", "Refractory Engineer — SEN & tundish nozzle management", "Quality Control Engineer — macro etch & UT of billet internal quality (centre porosity spec)", "Materials Engineer — hydrogen & cleanliness specification (flake-sensitive OCTG grades)"] },
        BOF_EAF_STAGE, BF_DR_STAGE, FEEDSTOCK_STAGE, STEEL_RAW,
      ]},
    ],
  },
};

const CATEGORIES = [
  { name: "Coated Flat", color: "#7c3aed", products: ["galvanized", "galvalume", "prepainted", "tinplate"] },
  { name: "Cold-Rolled Flat", color: "#1e4976", products: ["coldrolled"] },
  { name: "Hot-Rolled Flat", color: "#235991", products: ["hotrolled", "plate"] },
  { name: "Long Products", color: "#b45309", products: ["rebar", "wirerod", "merchantbar", "structural", "rail", "sheetpiling"] },
  { name: "Tubular Products", color: "#1e3a8a", products: ["weldedpipe", "seamlesspipe"] },
];

// ── Trade & capacity reference data ─────────────────────────────────────────
// Sourced from data/trademap/UGA_*.csv (ITC TradeMap, Uganda's bilateral
// trade, 2024, USD '000) and report/chapters/report1-04-iron-steel.md
// (NPA/UDC 2025 plant register). TradeMap was only fetched at HS-4-digit
// level, which groups several finished products together — figures are
// labelled by that real granularity rather than attributed to one product.
// EAC = sum of Uganda's 2024 trade with Kenya, Tanzania, Rwanda, Burundi,
// South Sudan and DR Congo from the same bilateral CSVs. "Global" (world
// total trade flow, not just Uganda's) has not been sourced yet.
const TRADE_HS4 = {
  "7208": {
    desc: "HS 7208 — flat-rolled, hot-rolled, ≥600mm (shared by Hot-Rolled Coil and Plate)",
    year: 2024,
    imports: { uganda: 219496, eac: 117 },
    exports: { uganda: 2876, eac: 2802 },
  },
  "7209": {
    desc: "HS 7209 — flat-rolled, cold-rolled, ≥600mm",
    year: 2024,
    imports: { uganda: 4213, eac: 1923 },
    exports: { uganda: 256, eac: 255 },
  },
  "7213": {
    desc: "HS 7213 — bars and rods in coils (wire rod)",
    year: 2024,
    imports: { uganda: 34054, eac: 0 },
    exports: { uganda: 503, eac: 503 },
  },
  "7214": {
    desc: "HS 7214 — other bars and rods, iron/non-alloy steel (shared by Rebar and Merchant Bar)",
    year: 2024,
    imports: { uganda: 2725, eac: 768 },
    exports: { uganda: 55849, eac: 55633 },
  },
  "7204": {
    desc: "HS 7204 — ferrous waste and scrap (EAF charge input)",
    year: 2024,
    imports: { uganda: 72847, eac: 50228 },
    exports: { uganda: 36, eac: 0 },
  },
  "7207": {
    desc: "HS 7207 — semi-finished products of iron/non-alloy steel (slab, billet, bloom)",
    year: 2024,
    imports: { uganda: 78549, eac: 0 },
    exports: { uganda: 2516, eac: 2516 },
  },
  // Refined metals fed directly into the coating baths (zinc ingots, the
  // Al-Zn alloy bath, tin anodes) — fetched from ITC TradeMap 2026-06-29.
  // Uganda has no zinc/aluminium/tin smelting industry, so it imports the
  // finished metal for these coating lines, not the raw ore.
  "7901": {
    desc: "HS 7901 — unwrought zinc (zinc ingots for galvanizing baths)",
    year: 2024,
    imports: { uganda: 12483, eac: 0 },
    exports: { uganda: 0, eac: 0 },
  },
  "7601": {
    desc: "HS 7601 — unwrought aluminium (Al-Zn alloy bath input)",
    year: 2024,
    imports: { uganda: 12995, eac: 0 },
    exports: { uganda: 0, eac: 0 },
  },
  "8001": {
    desc: "HS 8001 — unwrought tin (tin anodes for electrolytic tinning)",
    year: 2024,
    imports: { uganda: 222, eac: 0 },
    exports: { uganda: 2625, eac: 0 },
  },
};

// Keyword -> HS-4 group, for matching free-text "Inputs" tab line items
// (e.g. "Steel scrap (20-30%)" or "Billet (reheated to ~1,100-1,150 C)")
// to the same trade data used for raw materials and products above.
const INPUT_KEYWORD_HS4 = [
  { pattern: /\bscrap\b/i, hs4: "7204" },
  { pattern: /\b(slab|billet|bloom|semi-finished)\b/i, hs4: "7207" },
  { pattern: /\bzinc ingots?\b/i, hs4: "7901" },
  { pattern: /\baluminum \(55% of bath/i, hs4: "7601" },
  { pattern: /\btin anodes?\b/i, hs4: "8001" },
];

function matchInputTrade(text) {
  const hit = INPUT_KEYWORD_HS4.find((k) => k.pattern.test(text));
  return hit ? TRADE_HS4[hit.hs4] : null;
}

// Keyword -> verified Phase, for the same free-text "Inputs" line items —
// only for phases the NPA/UDC register actually distinguishes (II/III/IV).
// Deliberately excludes hot/cold-rolled coil mentions: those are imported
// inputs, not domestically produced, so no Uganda phase count applies.
const INPUT_KEYWORD_PHASE = [
  { pattern: /\bsponge iron\b|\bpig iron\b|\bDRI\b|\bHBI\b/i, phase: "II" },
  { pattern: /\bscrap\b|\bliquid steel\b/i, phase: "III" },
  { pattern: /\b(slab|billet|bloom)\b/i, phase: "IV" },
];

function matchInputPhase(text) {
  const hit = INPUT_KEYWORD_PHASE.find((k) => k.pattern.test(text));
  return hit ? PHASE_PRODUCERS[hit.phase] : null;
}

// Which HS-4 trade group each product falls under (omitted = not fetched yet).
const PRODUCT_HS4 = {
  hotrolled: "7208",
  plate: "7208",
  coldrolled: "7209",
  wirerod: "7213",
  rebar: "7214",
  merchantbar: "7214",
};

// Verified plant-by-phase participation, extracted from the NPA/UDC source
// register itself (Table 7: "Value Chain mapping for Iron and Steel players
// in Uganda") once it was converted from legacy .doc to .docx. Each plant is
// colour-coded there by % operation in each value-chain phase; counts below
// are plants marked active (100%, <50%, or small-scale) in that phase —
// "out of business" marks are excluded (e.g. BM Steel Ltd, International
// Mining Company of Uganda and WCH are all marked fully out of business,
// despite BM Steel being named as an active producer in the report chapter's
// prose summary — the matrix is the more granular, more current source).
//
// Phase V is split into V(a) primary steel rolling (billets -> long
// products: rebar, wire rod, bars, sections) and V(b) finishing/coating
// (e.g. PPGI/galvanizing) — this split is explicit in the source document's
// own text (Section 3.3.6: "the small players in Phase V(b) source their
// raw materials locally from those in Phase V(a)"). This is the most
// granular real breakdown available — the register does not go further to
// separate, say, rebar-only plants from wire-rod-only plants within V(a).
const PHASE_PRODUCERS = {
  I: { count: 3, label: "Phase I — exploration & mining", examples: ["SINO Minerals Ltd (300,000 tpa installed, Kabale)", "GLISCO Ltd (small-scale, Kisoro)", "Kamuntu Investments (small-scale)"] },
  II: { count: 2, label: "Phase II — ironmaking (sponge iron/DRI)", examples: ["Tembo Steel — Iganga", "Abyssinia Iron & Steel (U) Ltd — Jinja"] },
  III: { count: 5, label: "Phase III — steelmaking", examples: ["Tembo Steel", "Abyssinia Iron & Steel", "Pramukh Steel", "Yogi Steel", "Tembo Steel — Lugazi"] },
  IV: { count: 9, label: "Phase IV — continuous casting (slabs/blooms/billets)", examples: ["Tembo Steel", "Abyssinia Iron & Steel", "Steel & Tube Ltd (Nakawa & Namanve)", "Roofings Ltd — Lubowa", "Tian Tang Steel"] },
  Va: { count: 16, label: "Phase V(a) — primary steel rolling (billets → long products)", examples: ["Roofings Ltd (Lubowa & Namanve)", "Steel & Tube Ltd (Nakawa & Namanve)", "Tembo Steel (Iganga & Lugazi)", "Pramukh Steel", "Yogi Steel", "Tian Tang Steel", "Madhvani Steel", "and 9 others"] },
  Vb: { count: 32, label: "Phase V(b) — finishing/coating (e.g. PPGI, galvanizing)", examples: ["Uganda Baati", "Tororo Cement — Steel Division", "Nile Roofings Ltd", "East African Roofing Systems Ltd", "Mayuge Sugar — Steel Division", "plus the 16 Phase V(a) plants, and 11 others"] },
};
const PHASE_SOURCE = "NPA/UDC, Mapping and Value Chain Analysis for Uganda's Iron and Steel Industry (Oct 2025), Table 7";

// Per-product producer attribution. The PHASE_PRODUCERS counts above answer
// "how many plants operate at this rolling/finishing stage" — they do NOT
// answer "how many plants make THIS specific product," because the source
// register doesn't split rolling output by product. Conflating the two
// (attaching the same phase count to five different products) was wrong —
// it looks precise but answers a different question than the one asked.
//
// So: the headline here is always the most product-specific answer we
// actually have (named firms from the report chapter's prose, where it
// attributes a firm to a specific product) or an explicit "not available
// per-product" when we don't. `phaseContext` is shown only as secondary,
// clearly-labelled background — never as if it were the per-product count.
// status: "named" = specific firms attributed to this product; "absent" =
// the report explicitly states no/negligible domestic production;
// "unknown" = neither confirmed — don't imply a number either way.
const PRODUCT_FIRMS = {
  galvanized: { status: "named", firms: ["Uganda Baati (named for \"roofing, coated sheet\")", "Roofings Rolling Mills (named for \"coated coil\", among other products)"], phaseContext: { phase: "Vb", sharedWith: "Galvalume, Pre-painted Coil and all other Phase V(b) finishing output" } },
  galvalume: { status: "unknown", note: "Not named separately from Galvanized Sheet/PPGI anywhere in the source documents — no specific producer or absence confirmed for this alloy specifically." },
  prepainted: { status: "named", firms: ["Roofings Rolling Mills (named for \"coated coil\")"], note: "The source register's Phase V(b) economic analysis is specifically about PPGI (pre-painted galvanised iron) production economics, but still doesn't name which plants make PPGI vs plain galvanized.", phaseContext: { phase: "Vb", sharedWith: "Galvanized Sheet, Galvalume and all other Phase V(b) finishing output" } },
  tinplate: { status: "absent", note: "Explicitly deprioritized — \"low\" on every prioritisation criterion (report Section 4.F); no producer named or marked active." },
  coldrolled: { status: "absent", note: "Flat-rolling is explicitly described as absent in Uganda — Phase V(a)/(b) plants finish imported coil, none cast and roll flat coil domestically." },
  hotrolled: { status: "absent", note: "Flat-rolling is explicitly described as absent in Uganda — Phase V(a)/(b) plants finish imported coil, none cast and roll flat coil domestically." },
  plate: { status: "absent", note: "Flat-rolling is explicitly described as absent in Uganda — Phase V(a)/(b) plants finish imported coil, none cast and roll flat coil domestically." },
  rebar: { status: "named", firms: ["Roofings Rolling Mills (named for \"rebar, wire, coated coil\")", "Tororo Cement — Steel Division (named for \"long products\")", "Pramukh, Yogi, Madhvani, Tian Tang, Diamond and others (named for \"re-rolling, sections, wire, nails\")"], note: "Uganda's strongest finished product — net exporter (USD 55.8m, 2024).", phaseContext: { phase: "Va", sharedWith: "Wire Rod, Merchant Bar, Structural Sections and Welded Pipe" } },
  wirerod: { status: "named", firms: ["Roofings Rolling Mills (named for \"wire\")", "Pramukh, Yogi, Madhvani, Tian Tang, Diamond and others (named for \"wire, nails\")"], phaseContext: { phase: "Va", sharedWith: "Rebar, Merchant Bar, Structural Sections and Welded Pipe" } },
  merchantbar: { status: "named", firms: ["Steel & Tube Ltd (named for \"bars, tubes, sections\")", "Pramukh, Yogi, Madhvani, Tian Tang, Diamond and others (named for \"sections\")"], phaseContext: { phase: "Va", sharedWith: "Rebar, Wire Rod, Structural Sections and Welded Pipe" } },
  structural: { status: "named", firms: ["Steel & Tube Ltd (named for \"bars, tubes, sections\")"], phaseContext: { phase: "Va", sharedWith: "Rebar, Wire Rod, Merchant Bar and Welded Pipe" } },
  rail: { status: "unknown", note: "Not discussed in the source report — neither confirmed present nor absent." },
  sheetpiling: { status: "unknown", note: "Not discussed in the source report — neither confirmed present nor absent." },
  weldedpipe: { status: "named", firms: ["Roofings Ltd (named for \"pipes\")", "Steel & Tube Ltd (named for \"tubes\")"], phaseContext: { phase: "Va", sharedWith: "Rebar, Wire Rod, Merchant Bar and Structural Sections" } },
  seamlesspipe: { status: "absent", note: "Explicitly named as a product Uganda should NOT pursue at this stage (report Section 4.F)." },
};

// Verified Phase I (mining) producer count for raw materials shown in the
// "Raw Materials" cards, where the NPA/UDC register covers that material.
const RAW_MATERIAL_PHASE = {
  "Iron Ore": "I",
};

// Trade data for named raw-material commodities shown in the "Raw Materials"
// cards (RawCard items). Keyed by the exact item name string used in those
// cards. Fetched from ITC TradeMap 2026-06-29 — only Water, Electricity and
// Process Water are intentionally left out (not goods tracked by HS code in
// the conventional bilateral-trade sense).
//
// Deliberately NOT included despite being fetched: "Crude Oil / Naphtha"
// (HS 2710, refined petroleum) and "Natural Gas / Ethylene" (HS 2711,
// petroleum gases) — Uganda's HS 2710 imports (~$2.09bn, 2024) are almost
// entirely motor fuel, and HS 2711 is almost entirely LPG cylinders; Uganda
// has no petrochemical cracking industry, so neither figure is actually
// representative of "feedstock for resin production." Attaching either
// would repeat the same mistake this data effort started by fixing —
// a number that looks specific but answers a different question.
const RAW_MATERIAL_TRADE = {
  "Iron Ore": {
    desc: "HS 2601 — iron ores and concentrates",
    year: 2024,
    imports: { uganda: 0, eac: 0 },
    exports: { uganda: 35841, eac: 35841 },
  },
  "Metallurgical Coal": {
    desc: "HS 2701 — coal and briquettes (not metallurgical-grade specific)",
    year: 2024,
    imports: { uganda: 9639, eac: 8295 },
    exports: { uganda: 0, eac: 0 },
  },
  "Limestone / Dolomite": {
    desc: "HS 2521 — limestone flux",
    year: 2024,
    imports: { uganda: 165, eac: 165 },
    exports: { uganda: 12, eac: 12 },
  },
  "Zinc Ore (Sphalerite, ZnS)": {
    desc: "HS 2608 — zinc ores and concentrates",
    year: 2024,
    imports: { uganda: 440, eac: 0 },
    exports: { uganda: 0, eac: 0 },
  },
  "Sulfuric Acid": {
    desc: "HS 2807 — sulphuric acid",
    year: 2024,
    imports: { uganda: 1306, eac: 1219 },
    exports: { uganda: 5, eac: 5 },
  },
  "Coke / Coal": {
    desc: "HS 2704 — coke and semi-coke",
    year: 2024,
    imports: { uganda: 0, eac: 0 },
    exports: { uganda: 2184, eac: 2184 },
  },
  "Bauxite Ore": {
    desc: "HS 2606 — aluminium ores and concentrates",
    year: 2024,
    imports: { uganda: 203, eac: 203 },
    exports: { uganda: 0, eac: 0 },
  },
  "Caustic Soda (NaOH)": {
    desc: "HS 2815 — sodium hydroxide",
    year: 2024,
    imports: { uganda: 15137, eac: 201 },
    exports: { uganda: 3148, eac: 3116 },
  },
  "Petroleum Coke": {
    desc: "HS 2713 — petroleum coke, bitumen and other petroleum-oil residues",
    year: 2024,
    imports: { uganda: 9578, eac: 86 },
    exports: { uganda: 464, eac: 464 },
  },
  "Coal Tar Pitch": {
    desc: "HS 2706 — tar from coal/lignite",
    year: 2024,
    imports: { uganda: 0, eac: 0 },
    exports: { uganda: 0, eac: 0 },
  },
  "Cassiterite Ore (SnO2)": {
    desc: "HS 2609 — tin ores and concentrates",
    year: 2024,
    imports: { uganda: 0, eac: 0 },
    exports: { uganda: 0, eac: 0 },
  },
  "Coal / Coke": {
    desc: "HS 2704 — coke and semi-coke",
    year: 2024,
    imports: { uganda: 0, eac: 0 },
    exports: { uganda: 2184, eac: 2184 },
  },
  "Fluorite (CaF2)": {
    desc: "HS 2529 — feldspar, leucite, nepheline, fluorspar (not fluorite-specific)",
    year: 2024,
    imports: { uganda: 37, eac: 0 },
    exports: { uganda: 0, eac: 0 },
  },
  "Ilmenite / Rutile": {
    desc: "HS 2614 — titanium and zirconium ores and concentrates",
    year: 2024,
    imports: { uganda: 0, eac: 0 },
    exports: { uganda: 0, eac: 0 },
  },
};

export { PRODUCTS, CATEGORIES, TRADE_HS4, PRODUCT_HS4, RAW_MATERIAL_TRADE, matchInputTrade, matchInputPhase, PRODUCT_FIRMS, PHASE_PRODUCERS, PHASE_SOURCE, RAW_MATERIAL_PHASE };
