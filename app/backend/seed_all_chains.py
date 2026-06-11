"""
Per-product decomposition graphs for the remaining MTIC report value chains.

Same model as seed_products.py (Iron & Steel): every finished good is a System
ROOT; the app walks UPSTREAM through intermediates -> processing technologies ->
raw materials, energy, labour and plant. Upstream nodes are shared within a
chain so each chain is one directed "made-from" network, not many separate trees.

Node ids are namespaced per chain (cu_ copper, au_ automotive, tx_ textiles,
ph_ pharma, pc_ petrochem/fertilizer, sg_ sugar, pl_ plastics, cm_ cement) so
they never collide with Iron & Steel (p_/c_/m_) or each other.

Edge convention: start_node = upstream input, end_node = downstream product;
weight = that input's cost share of the parent (0..1, indicative estimates).
HS codes follow chapters most associated with each finished good; cost shares
are engineering estimates to be refined with NPA/UDC and ITC TradeMap data.
"""
import db

SRC = ["MTIC value-chain taxonomy; standard industrial process routes (estimated weights)"]

# Strength data from Jerome's sources-of-truth.html (Value Chain Maps tab).
# green=strong, yellow=emerging, red=gap.  node_id → (strength, note)
STRENGTH = {
    # ══════════════════════════════════════════════════════
    # COPPER & ALLIED METALS
    # Phases: I Mining→gap  II Smelting→gap  III Refining→gap
    #         IV Semi-fab→gap  V Fabrication→strong  VI Market→strong
    # Critical gap: Phases I–IV entirely absent. USD 57.7m cable imports.
    # 2040 target: USD 300–500m cable market; Kilembe revival.
    # ══════════════════════════════════════════════════════
    "cu_m_ore":      ("gap",      "Kilembe mine dormant since 1980s; PSA signed March 2025 — not yet operational"),
    "cu_m_scrap":    ("emerging", "Secondary copper from recycling; limited scale in Uganda"),
    "cu_m_zinc":     ("gap",      "No domestic zinc production; all imported"),
    "cu_m_tin":      ("gap",      "No domestic tin; all imported"),
    "cu_m_lead":     ("gap",      "No domestic lead; all imported"),
    "cu_m_alu":      ("gap",      "Aluminium absent — all imported"),
    "cu_m_pvc":      ("gap",      "PVC insulation imported; domestic resin awaits Kabalega park (~2029)"),
    "cu_e_elec":     ("emerging", "Grid access 25.3%; reliability constraints for electro-refining"),
    "cu_e_heat":     ("gap",      "Process heat from imported fuels; no domestic alternative"),
    "cu_l_labour":   ("gap",      "Mining/metallurgical skills scarce after decades of Kilembe dormancy"),
    "cu_k_smelt":    ("gap",      "No smelter in Uganda; all blister copper absent or imported"),
    "cu_k_cast":     ("strong",   "Cable Corporation Ltd casting and rolling plant operational"),
    "cu_k_draw":     ("strong",   "Wire-drawing and extrusion at Cable Corporation Ltd"),
    "cu_t_smelt":    ("gap",      "Flash smelting absent — no smelter in Uganda"),
    "cu_t_refine":   ("gap",      "Electrorefining absent — all cathode imported from DRC/China"),
    "cu_t_sxew":     ("gap",      "SX-EW absent — Kilembe oxide ore untapped"),
    "cu_c_conc":     ("gap",      "Copper concentrate absent — Kilembe dormant since 1980s"),
    "cu_c_blister":  ("gap",      "Blister copper absent — no smelter in Uganda"),
    "cu_c_cathode":  ("gap",      "Refined cathode entirely imported; USD 6.9m (HS 7403, 2024)"),
    "cu_c_wirerod":  ("gap",      "Wire rod imported — Phase IV semi-fabrication absent"),
    "cu_c_billet":   ("gap",      "Copper billet imported — no local semi-fabrication"),
    "cu_c_brass":    ("gap",      "Brass production absent — alloy imported"),
    "cu_c_bronze":   ("gap",      "Bronze production absent — alloy imported"),
    "cu_p_cathode":  ("gap",      "Refined cathode entirely imported from DRC and China"),
    "cu_p_wirerod":  ("gap",      "Wire rod imported — no domestic semi-fabrication"),
    "cu_p_wire":     ("strong",   "Cable Corporation Ltd produces copper wire; domestic + regional market"),
    "cu_p_cable":    ("strong",   "Cable Corporation Ltd ~65% domestic market share; electrification-driven demand. CRITICAL GAP: Phases I–IV entirely absent — USD 57.7m cable imports + USD 6.9m cathode imports. 2040 target: USD 300–500m cable market; Kilembe copper cathode + cobalt production."),
    "cu_p_tube":     ("gap",      "Copper tube production absent in Uganda"),
    "cu_p_sheet":    ("gap",      "Copper sheet absent — no local semi-fabrication"),
    "cu_p_busbar":   ("gap",      "Busbar absent — imported from DRC/China"),
    "cu_p_brass":    ("gap",      "Brass rod/fittings absent — all imported"),
    "cu_p_bronze":   ("gap",      "Bronze absent — no local alloy production"),
    "cu_p_fittings": ("gap",      "Copper fittings absent — all imported"),
    "cu_p_alu_prof": ("gap",      "Aluminium extrusions absent — all imported"),
    "cu_p_alu_sheet":("gap",      "Aluminium sheet absent — all imported"),
    "cu_p_alu_cond": ("gap",      "ACSR conductor absent — all imported"),
    "cu_p_zinc":     ("gap",      "Zinc sheet/anodes absent — all imported"),
    "cu_p_lead":     ("gap",      "Lead products absent — all imported"),
    "cu_p_solder":   ("gap",      "Solder absent — all imported"),

    # ══════════════════════════════════════════════════════
    # AUTOMOTIVE
    # Phases: I Raw Materials→emerging  II Components→gap
    #         III Assembly→emerging  IV Distribution→strong  V After-Market→strong
    # Key gap: Components (Phase II) — local content almost zero. USD 31.7m parts imports.
    # 2040 target: KMC 10,000 veh/yr; e-boda assembly at scale.
    # ══════════════════════════════════════════════════════
    "au_m_steel":    ("emerging", "Domestic long steel (rebar/sections) exists; flat steel for body panels absent"),
    "au_m_alu":      ("gap",      "Aluminium alloy absent — all imported"),
    "au_m_plastic":  ("emerging", "Domestic polymer converters active; resin 100% imported"),
    "au_m_rubber":   ("gap",      "No synthetic rubber production in Uganda"),
    "au_m_glass":    ("gap",      "Automotive glass absent — all imported"),
    "au_m_copper":   ("emerging", "Cable Corporation wire available; wiring harness assembly absent"),
    "au_m_chips":    ("gap",      "Semiconductors/ECUs entirely imported; no domestic production"),
    "au_m_textile":  ("emerging", "Some upholstery textile available; foam locally produced"),
    "au_m_paint":    ("emerging", "Some paint manufacturing in Uganda (Crown, Sadolin)"),
    "au_m_cells":    ("gap",      "Li-ion battery cells entirely imported"),
    "au_m_lead":     ("emerging", "Some lead-acid battery assembly locally"),
    "au_e_elec":     ("emerging", "Grid power available; reliability constraints"),
    "au_l_labour":   ("emerging", "Assembly skills at KMC; EV/mechatronics engineering skills scarce"),
    "au_k_stamp":    ("gap",      "Stamping presses absent — body panels all CKD/imported"),
    "au_k_robot":    ("gap",      "Robotic welding absent — CKD assembly is manual"),
    "au_k_mould":    ("emerging", "Injection moulding exists in plastics sector; limited automotive use"),
    "au_k_machine":  ("gap",      "CNC machining for automotive components absent"),
    "au_c_biw":      ("gap",      "Body-in-white absent — all CKD/SKD; no panel stamping in Uganda"),
    "au_c_engine":   ("gap",      "ICE engine production absent — all engines imported"),
    "au_c_emotor":   ("gap",      "Electric drive motors absent — KMC sources motors externally"),
    "au_c_trans":    ("gap",      "Transmissions absent — all imported"),
    "au_c_chassis":  ("emerging", "Some chassis/frame fabrication for buses (Kampala/Jinja body builders)"),
    "au_c_battery":  ("gap",      "EV battery packs absent — all sourced externally by KMC"),
    "au_c_interior": ("emerging", "Some interior/upholstery local content; trim largely imported"),
    "au_c_harness":  ("gap",      "Wiring harness assembly absent — all imported"),
    "au_c_tyres":    ("gap",      "No tyre manufacturing in Uganda — all imported"),
    "au_p_car":      ("gap",      "No domestic ICE passenger car production"),
    "au_p_ev":       ("emerging", "KMC Kayoola EV bus — plant commissioned Sept 2025; ~2,500 vehicles/yr capacity. KEY GAP: Components (Phase II) absent — local content almost zero; USD 31.7m parts imports (HS 8708). 2040 target: KMC 10,000 veh/yr; regional EV-bus supplier."),
    "au_p_hybrid":   ("gap",      "No hybrid vehicle production in Uganda"),
    "au_p_pickup":   ("gap",      "No domestic pickup production"),
    "au_p_truck":    ("gap",      "No domestic truck production"),
    "au_p_bus":      ("emerging", "KMC bus production; Kampala/Jinja body builders on imported chassis"),
    "au_p_motorcycle":("emerging","CKD motorcycle assembly (boda-boda market); USD 157m import opportunity"),
    "au_p_threewheel":("gap",     "No three-wheeler production in Uganda"),
    "au_p_tractor":  ("gap",      "No domestic tractor production"),
    "au_p_trailer":  ("strong",   "Trailer/body fabrication active in Kampala and Jinja"),
    "au_p_engine":   ("gap",      "Engines all imported — no domestic engine manufacturing"),
    "au_p_parts":    ("strong",   "Large aftermarket — Ndeeba/Kisekka market; import-based but very active"),
    "au_p_battery":  ("emerging", "Some lead-acid battery assembly; Li-ion all imported"),
    "au_p_tyres":    ("gap",      "No tyre manufacturing in Uganda — all imported"),

    # ══════════════════════════════════════════════════════
    # TEXTILES & GARMENTS
    # Phases: I Cotton Growing→strong  II Ginning→strong  III Spinning→emerging
    #         IV Weaving/Knitting→gap  V Wet Processing & Finishing→gap  VI Garment Mfg→emerging
    # Critical gap: Wet processing/finishing (Phase V) — blocks entire chain.
    # 2040 target: Process ≥50% of lint domestically; ginnery utilisation 60%+.
    # ══════════════════════════════════════════════════════
    "tx_m_cotton":   ("strong",   "~116,000 bales (2023); smallholder base; surplus in good years"),
    "tx_m_poly":     ("gap",      "Polyester fibre entirely imported"),
    "tx_m_visc":     ("gap",      "Viscose/rayon entirely imported"),
    "tx_m_wool":     ("gap",      "Wool not produced commercially in Uganda"),
    "tx_m_dye":      ("gap",      "Synthetic dyes entirely imported — CRITICAL; blocks finishing step"),
    "tx_m_trim":     ("gap",      "Trims, zips and buttons mostly imported"),
    "tx_e_elec":     ("emerging", "Grid power available; reliability constraints for continuous mills"),
    "tx_e_heat":     ("emerging", "Process steam/heat available at integrated mills"),
    "tx_l_labour":   ("strong",   "~18,000 employment (Fine Spinners + outgrowers); skilled pool established"),
    "tx_k_spin":     ("emerging", "Spinning capacity at Fine Spinners and Nytil; underutilised"),
    "tx_k_loom":     ("gap",      "Weaving looms largely absent; fabric not produced domestically at scale"),
    "tx_k_knit":     ("gap",      "Knitting machines largely absent"),
    "tx_k_dye":      ("gap",      "Dyeing/finishing plant CRITICALLY ABSENT — single biggest gap in chain"),
    "tx_k_sew":      ("emerging", "Sewing/cutting capacity at some Kampala garment makers"),
    "tx_c_yarn":     ("emerging", "Fine Spinners + Nytil (limited); yarn produced at low volumes"),
    "tx_c_woven":    ("gap",      "Grey woven fabric largely absent — weaving capacity missing"),
    "tx_c_knit":     ("gap",      "Knitted fabric largely absent — knitting capacity minimal"),
    "tx_c_finfab":   ("gap",      "Dyed & finished fabric ABSENT — wet processing/finishing missing; blocks garment chain"),
    "tx_c_nonwoven": ("gap",      "Nonwoven fabric absent — all imported"),
    "tx_p_yarn":     ("emerging", "Yarn produced at Fine Spinners + Nytil; limited volume. CRITICAL GAP: Wet processing & finishing absent — without dyeing/finishing Uganda cannot produce export-quality fabric or garments. 2040 target: ≥50% of lint processed domestically; ginnery utilisation 60%+."),
    "tx_p_fabric":   ("gap",      "Finished fabric absent — wet processing/finishing critically missing"),
    "tx_p_tshirt":   ("emerging", "Limited knitwear; ~90% of Uganda's lint exported raw"),
    "tx_p_shirts":   ("emerging", "Some woven shirt production; fabric largely imported"),
    "tx_p_trousers": ("emerging", "Limited trouser/denim production"),
    "tx_p_dresses":  ("emerging", "Limited women's apparel"),
    "tx_p_underwear":("emerging", "Some underwear/hosiery production"),
    "tx_p_workwear": ("emerging", "Uniforms/workwear — some institutional demand served locally"),
    "tx_p_home":     ("gap",      "Home textiles (linen, towels) largely absent"),
    "tx_p_carpet":   ("gap",      "Carpets and rugs absent"),
    "tx_p_technical":("gap",      "Technical textiles absent — all imported"),
    "tx_p_bags":     ("emerging", "Woven PP sacks produced locally for cement/grain packaging"),
    "tx_p_medical":  ("emerging", "Some medical/hygiene textiles produced locally"),

    # ══════════════════════════════════════════════════════
    # PHARMACEUTICALS
    # Phases: I API & Excipients→gap  II Formulation & Mfg→strong
    #         III Packaging→strong  IV Distribution→strong  V Dispensing→strong
    # Key gap: API & excipients (Phase I) — near-total import dependence; India 58%.
    # 2040 target: USD 0.9–1.2B market; import dependence <50%.
    # ══════════════════════════════════════════════════════
    "ph_m_inter":    ("gap",      "Chemical intermediates for API synthesis entirely imported"),
    "ph_m_solvent":  ("gap",      "Pharma-grade solvents imported; India and China dominant"),
    "ph_m_excip":    ("gap",      "Excipients (fillers, binders) mostly imported"),
    "ph_m_bio":      ("gap",      "Biological substrates imported — no local cell-culture capacity"),
    "ph_m_pack":     ("strong",   "Primary packaging linked to plastics chain; active domestic production"),
    "ph_m_glass":    ("emerging", "Some glass vials available; most imported"),
    "ph_e_elec":     ("emerging", "Clean-room HVAC needs consistent power; constraints at some facilities"),
    "ph_l_labour":   ("strong",   "6 WHO-GMP facilities; +42% employment growth 2017–19 (UNIDO)"),
    "ph_k_reactor":  ("gap",      "API synthesis reactors absent — no local API manufacturing"),
    "ph_k_tablet":   ("strong",   "Tablet presses at QCIL and others; 1.2bn tabs/caps/yr"),
    "ph_k_fill":     ("strong",   "Aseptic filling lines at QCIL; WHO-GMP prequalified"),
    "ph_k_qc":       ("strong",   "QC lab instruments at 6 WHO-GMP aligned manufacturers"),
    "ph_c_api":      ("gap",      "APIs near-totally imported — deepest structural risk; India 58% of medicine imports"),
    "ph_c_form":     ("strong",   "Formulated blends made at QCIL, KPI, Rene and others; WHO-GMP capable"),
    "ph_p_tablets":  ("strong",   "QCIL 1.2bn tabs/caps/yr; KPI, Rene and others active. KEY GAP: API & excipients (Phase I) — near-total import dependence is the deepest structural and supply-security risk. 2040 target: USD 0.9–1.2B market; cut import dependence to <50%."),
    "ph_p_inject":   ("strong",   "Aseptic injectables at QCIL; WHO-GMP prequalified"),
    "ph_p_syrups":   ("strong",   "Oral liquids produced at multiple manufacturers"),
    "ph_p_ointment": ("strong",   "Topical preparations produced locally"),
    "ph_p_iv":       ("emerging", "IV fluids at some manufacturers; limited volume"),
    "ph_p_vaccine":  ("gap",      "No vaccine/biologics production in Uganda"),
    "ph_p_antibiotic":("strong",  "Antibiotics produced at QCIL and others; WHO-GMP"),
    "ph_p_antimal":  ("strong",   "Antimalarials — QCIL flagship (ACT); WHO-GMP prequalified"),
    "ph_p_arv":      ("strong",   "ARVs — QCIL's core product; WHO/PEPFAR procurement; UGX 267bn revenue"),
    "ph_p_otc":      ("strong",   "OTC analgesics produced locally by multiple manufacturers"),
    "ph_p_supp":     ("emerging", "Some vitamins/supplements produced; limited range"),
    "ph_p_vet":      ("emerging", "Some veterinary medicines produced locally"),
    "ph_p_api":      ("gap",      "Bulk API production near zero — near-total import dependence"),
    "ph_p_devices":  ("emerging", "Some medical consumables produced; syringes largely imported"),
    "ph_p_diag":     ("gap",      "Diagnostic kits/reagents absent — all imported"),

    # ══════════════════════════════════════════════════════
    # PETROCHEMICALS & FERTILIZERS
    # Phases: I Upstream Extraction→emerging  II Refining/Processing→gap
    #         III Petrochemical Processing→gap  IV Blending & Formulation→gap  V Market→strong
    # Critical gaps: Refinery not operational until ~2029; Sukulu phosphate stalled.
    # 2040 target: 1.5–2m tonnes fertiliser demand; Kabalega park operational.
    # ══════════════════════════════════════════════════════
    "pc_m_crude":    ("emerging", "Crude oil reserves identified (Lake Albert); production pre-FID"),
    "pc_m_gas":      ("emerging", "Associated gas from oil fields; pre-commercial production"),
    "pc_m_naphtha":  ("gap",      "Naphtha absent — no refinery yet; Kabaale expected ~2029"),
    "pc_m_phos":     ("gap",      "Sukulu phosphate plant stalled (2021); 100,000 tpa design unused"),
    "pc_m_potash":   ("gap",      "No potash deposits in Uganda; all imported"),
    "pc_m_sulphur":  ("gap",      "No domestic sulphur production; all imported"),
    "pc_e_elec":     ("emerging", "Grid power available; reliability constraints for chemical plants"),
    "pc_e_steam":    ("gap",      "Industrial process steam absent at commercial scale"),
    "pc_l_labour":   ("gap",      "Chemical/process engineering skills scarce"),
    "pc_k_crack":    ("gap",      "Steam cracker absent — no refinery/petrochemical complex yet"),
    "pc_k_reform":   ("gap",      "Ammonia plant/reformer absent — green ammonia option planned"),
    "pc_k_poly":     ("gap",      "Polymerisation reactors absent — Kabalega park future (~2029)"),
    "pc_c_ethylene": ("gap",      "Ethylene absent — no domestic petrochemical processing"),
    "pc_c_propylene":("gap",      "Propylene absent — no domestic petrochemical processing"),
    "pc_c_btx":      ("gap",      "Aromatics (BTX) absent — no domestic petrochemical processing"),
    "pc_c_ammonia":  ("gap",      "Ammonia absent — no domestic production; all imported"),
    "pc_c_methanol": ("gap",      "Methanol absent — no domestic production"),
    "pc_c_nitric":   ("gap",      "Nitric acid absent — no domestic production"),
    "pc_c_sulphuric":("gap",      "Sulphuric acid absent — no domestic production"),
    "pc_c_phosacid": ("gap",      "Phosphoric acid absent — Sukulu phosphate stalled"),
    "pc_p_pe":       ("gap",      "PE resin absent — 100% imported; Kabalega park future (~2029). CRITICAL GAP: Refinery not operational until ~2029; Sukulu phosphate stalled. Uganda imports ~50,000 t of fertiliser vs ~1m t needed — a 950,000 t annual gap. 2040 target: 1.5–2m tonnes fertiliser/yr; Kabalega park operational supplying domestic resin."),
    "pc_p_pp":       ("gap",      "PP resin absent — all imported"),
    "pc_p_pvc":      ("gap",      "PVC absent — all imported"),
    "pc_p_pet":      ("gap",      "PET absent — all imported"),
    "pc_p_ps":       ("gap",      "PS/EPS absent — all imported"),
    "pc_p_rubber":   ("gap",      "Synthetic rubber absent — all imported"),
    "pc_p_solvent":  ("gap",      "Industrial solvents absent — all imported"),
    "pc_p_methanol": ("gap",      "Methanol absent — all imported"),
    "pc_p_urea":     ("gap",      "Urea absent — all imported; part of USD 32.1m fertiliser imports"),
    "pc_p_can":      ("gap",      "CAN/ammonium nitrate absent — all imported"),
    "pc_p_dap":      ("gap",      "DAP absent — imported from Saudi Arabia/Kenya"),
    "pc_p_ssp":      ("gap",      "SSP absent — Sukulu phosphate stalled"),
    "pc_p_npk":      ("gap",      "NPK compound fertilizer absent — all imported; 950,000 tonne annual supply gap"),
    "pc_p_mop":      ("gap",      "Potassium fertilizer absent — all imported"),
    "pc_p_ammonia":  ("gap",      "Merchant ammonia absent — all imported"),

    # ══════════════════════════════════════════════════════
    # SUGAR & CONFECTIONERY
    # Phases: I Cane Growing→strong  II Milling→strong  III Refining→emerging
    #         IV Downstream→gap  V Market→strong
    # Key gap: Industrial sugar refining (Phase III) + downstream ethanol/co-gen (Phase IV).
    # 2040 target: Downstream-dominated chain; domestic industrial sugar + ethanol + co-gen.
    # ══════════════════════════════════════════════════════
    "sg_m_cane":     ("strong",   "Structural surplus — ~822,000 t/yr; Kakira ~50% of national output"),
    "sg_m_cocoa":    ("gap",      "Cocoa beans not produced commercially in Uganda — all imported"),
    "sg_m_milk":     ("emerging", "Some milk solids/powder production; most imported"),
    "sg_m_flav":     ("gap",      "Flavours, colours and additives mostly imported"),
    "sg_m_pectin":   ("gap",      "Gelatin/pectin imported; no domestic production"),
    "sg_m_fruit":    ("emerging", "Fruit pulp available from Uganda's agricultural base"),
    "sg_e_elec":     ("emerging", "Bagasse co-generation potential largely unexploited"),
    "sg_e_steam":    ("strong",   "Bagasse steam at sugar mills — abundant by-product of milling"),
    "sg_l_labour":   ("strong",   "Large agricultural and mill labour force established at major mills"),
    "sg_k_mill":     ("strong",   "Cane mills at Kakira, Kinyara, SCOUL, Mayuge — operational"),
    "sg_k_centri":   ("strong",   "Centrifuges operational at all major mills"),
    "sg_k_pack":     ("emerging", "Processing/packaging for confectionery emerging but limited"),
    "sg_c_juice":    ("strong",   "Cane juice extraction operational at all major mills"),
    "sg_c_raw":      ("strong",   "Raw/brown sugar — ~822,000 tpa; Uganda is net regional exporter"),
    "sg_c_refined":  ("emerging", "Refined white sugar — Kinyara ~75,000 t industrial; gap for food/pharma-grade"),
    "sg_c_molasses": ("strong",   "Molasses abundant by-product — largely exported raw or fed to animals"),
    "sg_c_syrup":    ("emerging", "Glucose/sugar syrup produced but limited capacity"),
    "sg_c_cocoa":    ("gap",      "Cocoa liquor/butter absent — no cocoa processing in Uganda"),
    "sg_p_white":    ("emerging", "Industrial white sugar — some (Kinyara); USD 38.1m still imported despite surplus. KEY GAP: Industrial sugar refining + downstream ethanol/co-gen (Phase IV) under-exploited. 2040 target: Downstream-dominated; industrial sugar, ethanol, co-gen, confectionery."),
    "sg_p_brown":    ("strong",   "Brown/raw sugar surplus — Uganda is net regional exporter"),
    "sg_p_icing":    ("emerging", "Icing/specialty sugars — limited production"),
    "sg_p_molasses": ("strong",   "Molasses abundant; largely exported raw or used as animal feed"),
    "sg_p_ethanol":  ("gap",      "Ethanol from molasses largely unexploited — KEY downstream gap"),
    "sg_p_hardcandy":("emerging", "Some hard-boiled sweets produced locally"),
    "sg_p_toffee":   ("emerging", "Toffees/caramels produced at some confectioners"),
    "sg_p_chocolate":("gap",      "Chocolate production minimal — no cocoa processing in Uganda"),
    "sg_p_gums":     ("emerging", "Gums/jellies produced by some local confectioners"),
    "sg_p_chewing":  ("emerging", "Some chewing gum production"),
    "sg_p_biscuits": ("emerging", "Biscuits and cookies — some local manufacturers"),
    "sg_p_bakery":   ("emerging", "Bakery confectionery — numerous local producers"),
    "sg_p_softdrink":("strong",   "Sweetened beverages — significant domestic production (Coca-Cola, Pepsi, Century)"),
    "sg_p_jam":      ("emerging", "Some jams/preserves produced locally"),

    # ══════════════════════════════════════════════════════
    # PLASTICS & PACKAGING
    # Phases: I Resin/Feedstock→gap  II Conversion→strong  III Packaging & Products→strong
    #         IV Use→strong  V Recycling→emerging
    # Key gap: Resin feedstock (Phase I) — 100% imported; recycling under-scaled.
    # 2040 target: Kabalega park → domestic resin; circularity strategy.
    # ══════════════════════════════════════════════════════
    "pl_m_pe":       ("gap",      "PE resin 100% imported; Kabalega petrochemical park future (~2029)"),
    "pl_m_pp":       ("gap",      "PP resin 100% imported — no domestic polymer production"),
    "pl_m_pvc":      ("gap",      "PVC resin 100% imported"),
    "pl_m_pet":      ("gap",      "PET resin 100% imported"),
    "pl_m_ps":       ("gap",      "PS/EPS resin 100% imported"),
    "pl_m_paper":    ("emerging", "Some paper/paperboard locally produced; significant imports"),
    "pl_m_foil":     ("gap",      "Aluminium foil absent — all imported"),
    "pl_m_add":      ("gap",      "Masterbatch/additives mostly imported; limited local compounding"),
    "pl_m_recyc":    ("emerging", "Recycled plastic — ~600 t/day waste; <40% collected; under-scaled"),
    "pl_e_elec":     ("emerging", "Grid power for moulding/extrusion; reliability constraints"),
    "pl_l_labour":   ("strong",   "Plastics manufacturing workforce established; 41 UNBS-certified firms"),
    "pl_k_inj":      ("strong",   "Injection moulding operational — Nice House of Plastics, Nile Plastic, others"),
    "pl_k_ext":      ("strong",   "Extruders operational — film, pipe, sheet production established"),
    "pl_k_blow":     ("strong",   "Blow moulding for bottles and jerrycans — active domestic production"),
    "pl_k_print":    ("emerging", "Flexographic printing/lamination — limited capacity"),
    "pl_c_film":     ("strong",   "Plastic film/sheet produced domestically — established converters"),
    "pl_c_preform":  ("strong",   "PET preforms produced domestically — bottle blowing active"),
    "pl_p_bottles":  ("strong",   "PET bottles — significant domestic production for beverages. KEY GAP: Resin feedstock (Phase I) — 100% imported; ~150,000 t/yr all imported. Recycling severely under-scaled. 2040 target: Kabalega park domestic resin; circularity strategy — 37% plastic pollution cut by 2040."),
    "pl_p_jerry":    ("strong",   "Jerrycans and drums — active domestic production"),
    "pl_p_bags":     ("strong",   "Plastic bags/sacks — 41 UNBS-certified manufacturers"),
    "pl_p_film":     ("strong",   "Packaging film — established domestic production"),
    "pl_p_rigid":    ("strong",   "Rigid containers/tubs — active domestic production"),
    "pl_p_caps":     ("strong",   "Caps and closures — domestic production active"),
    "pl_p_pipes":    ("strong",   "PVC pipes and fittings — domestic production (Roofings, others)"),
    "pl_p_house":    ("strong",   "Household plasticware — significant domestic production"),
    "pl_p_crates":   ("strong",   "Crates and pallets — domestic production for logistics"),
    "pl_p_woven":    ("strong",   "Woven PP sacks — domestic production for cement, sugar and grain packaging"),
    "pl_p_foam":     ("emerging", "EPS foam — limited domestic production"),
    "pl_p_corrug":   ("strong",   "Corrugated boxes — active domestic production for FMCG"),
    "pl_p_flexible": ("strong",   "Flexible laminates/pouches — domestic production established"),
    "pl_p_labels":   ("strong",   "Labels and printed packaging — domestic production active"),
    "pl_p_furniture":("emerging", "Plastic furniture — some domestic production"),

    # ══════════════════════════════════════════════════════
    # CEMENT & BUILDING MATERIALS
    # Phases: I Limestone Quarrying→strong  II Clinker Production→emerging
    #         III Cement Grinding→strong  IV Building Materials→emerging  V Construction Market→strong
    # Key gap: Clinker (Phase II) — >50% imported; USD 162.2m import bill (2024).
    # 2040 target: >90% clinker self-sufficiency; dominant regional cement supplier.
    # ══════════════════════════════════════════════════════
    "cm_m_lime":     ("strong",   "Limestone quarries at Dura (Kamwenge), Tororo, Karamoja — established"),
    "cm_m_clay":     ("strong",   "Clay/shale abundant; quarried alongside limestone deposits"),
    "cm_m_gypsum":   ("emerging", "Gypsum deposits exist in Uganda; partly imported"),
    "cm_m_sand":     ("strong",   "Sand and aggregates abundant — quarried across Uganda"),
    "cm_m_pozz":     ("emerging", "Pozzolana available; slag from steel sector limited but growing"),
    "cm_m_steel":    ("strong",   "Reinforcing steel (rebar) — domestic production strong; see Iron & Steel chain"),
    "cm_m_fuel":     ("gap",      "Kiln fuel (coal) largely imported; alt-fuel opportunity (waste, biomass)"),
    "cm_e_elec":     ("emerging", "Grid power for grinding; reliability constraints; 8–10¢/kWh"),
    "cm_e_heat":     ("gap",      "Kiln thermal energy from imported coal — high cost constraint"),
    "cm_l_labour":   ("strong",   "Quarry and cement plant workforce established at major operators"),
    "cm_k_kiln":     ("emerging", ">50% clinker imported; domestic kilns at Tororo/Hima; 2 new plants under construction (USD 500m)"),
    "cm_k_mill":     ("strong",   "Grinding mills at Tororo (3 Mtpa), Hima (2 Mtpa), Simba (1 Mtpa), Kampala (1 Mtpa)"),
    "cm_k_crush":    ("strong",   "Crushers at established limestone quarries — operational"),
    "cm_k_mix":      ("emerging", "Batching/moulding plant growing but largely artisanal scale"),
    "cm_c_meal":     ("strong",   "Raw meal — ground at established limestone quarries"),
    "cm_c_clinker":  ("emerging", ">50% imported (USD 162.2m, 2024); 2 new plants under construction (USD 500m total)"),
    "cm_c_cement":   ("strong",   "Portland cement grinding — 7 Mtpa installed; Uganda is net cement exporter"),
    "cm_c_agg":      ("strong",   "Crushed aggregate — abundant; active quarrying across Uganda"),
    "cm_p_opc":      ("strong",   "OPC — Uganda grinds and exports; Tororo, Hima, Simba, Kampala active. KEY GAP: Clinker >50% imported — USD 162.2m (2024). Two new plants (USD 500m) under construction. 2040 target: >90% clinker self-sufficiency; Uganda as dominant regional cement supplier."),
    "cm_p_ppc":      ("strong",   "Pozzolana/blended cement — strong; lower-carbon option growing"),
    "cm_p_clinker":  ("emerging", "Clinker still >50% imported; new domestic plants under construction"),
    "cm_p_white":    ("gap",      "White cement absent — all imported"),
    "cm_p_rmc":      ("emerging", "Ready-mix concrete — growing but served by few operators"),
    "cm_p_blocks":   ("emerging", "Concrete blocks and bricks — growing; mostly small-scale"),
    "cm_p_pavers":   ("emerging", "Paving blocks/kerbs — growing urban demand; local producers"),
    "cm_p_pipes":    ("emerging", "Concrete pipes — some production for drainage/sewerage"),
    "cm_p_precast":  ("emerging", "Precast elements — limited; growing for infrastructure"),
    "cm_p_rooftile": ("emerging", "Roofing tiles — some local production"),
    "cm_p_fibre":    ("gap",      "Fibre-cement sheets absent — all imported"),
    "cm_p_lime":     ("strong",   "Building lime — produced domestically alongside clinker"),
    "cm_p_gypboard": ("gap",      "Gypsum plasterboard absent — all imported"),
    "cm_p_mortar":   ("emerging", "Dry mortar/plaster — limited local production"),
    "cm_p_tiles":    ("gap",      "Ceramic tiles absent — all imported; significant market opportunity"),
    "cm_p_bricks":   ("emerging", "Clay bricks — traditional brick kilns; artisanal scale"),
    "cm_p_glass":    ("gap",      "Flat glass absent — no float glass production in Uganda; all imported"),
}

# Each chain: {vc, nodes:{id:(label,ctype,name,hs,hsd,fn)}, products:{id:(name,hs,hsd,fn)}, edges:{id:[(up,w)]}}
CHAINS = []

# ════════════════════════════════════════════════════════════════════════════
# 1. COPPER & ALLIED METALS
# ════════════════════════════════════════════════════════════════════════════
CHAINS.append({
  "vc": "Copper & Allied Metals",
  "nodes": {
    "cu_m_ore":     ("Material","material","Copper ore (chalcopyrite)","2603.00","Copper ores and concentrates","Mined sulphide/oxide ore; <1% Cu."),
    "cu_m_scrap":   ("Material","material","Copper scrap","7404.00","Copper waste and scrap","Recycled copper feed for secondary smelting."),
    "cu_m_zinc":    ("Material","material","Zinc","7901.00","Unwrought zinc","Alloying metal for brass."),
    "cu_m_tin":     ("Material","material","Tin","8001.00","Unwrought tin","Alloying metal for bronze and solder."),
    "cu_m_lead":    ("Material","material","Lead","7801.00","Unwrought lead","Battery plate and solder metal."),
    "cu_m_alu":     ("Material","material","Aluminium ingot","7601.00","Unwrought aluminium","Light conductor and structural metal."),
    "cu_m_pvc":     ("Material","material","PVC / XLPE insulation","3904.10","Polymers of vinyl chloride","Insulation and sheathing for cables."),
    "cu_e_elec":    ("Energy","energy","Electricity","3500.00","Electrical energy","Electrowinning, refining and melting power."),
    "cu_e_heat":    ("Energy","energy","Process heat / fuel",None,None,"Smelting and reheating energy."),
    "cu_l_labour":  ("LaborCost","labor","Labour",None,None,"Skilled smelting and fabrication labour."),
    "cu_k_smelt":   ("MachineryCost","machinery","Smelter & converter","8454.10","Converters and ladles","Flash smelting and converting furnaces."),
    "cu_k_cast":    ("MachineryCost","machinery","Casting & rolling plant","8455.00","Metal-rolling mills","Continuous casting and rolling equipment."),
    "cu_k_draw":    ("MachineryCost","machinery","Wire drawing / extrusion","8463.00","Metal drawing/extrusion machines","Wire drawing, tube and profile extrusion."),
    # Process technologies
    "cu_t_smelt":   ("TechnologyType",None,"Flash smelting","8454.10","Smelting furnace","Smelts concentrate to matte then blister copper."),
    "cu_t_refine":  ("TechnologyType",None,"Electrorefining","8543.30","Electrolytic refining plant","Refines anode copper to 99.99% cathode."),
    "cu_t_sxew":    ("TechnologyType",None,"Leach–SX–EW (hydromet)","8421.29","Solvent-extraction / electrowinning","Leaches oxide ore to cathode without smelting."),
    # Intermediates
    "cu_c_conc":    ("Component","component","Copper concentrate","2603.00","Copper concentrate","Flotation concentrate, ~30% Cu."),
    "cu_c_blister": ("Component","component","Blister copper","7401.00","Copper mattes; cement copper","Crude ~98% copper from converting."),
    "cu_c_cathode": ("Component","component","Refined copper cathode","7403.11","Refined copper, cathodes","99.99% Cu electrolytic cathode."),
    "cu_c_wirerod": ("Component","component","Copper wire rod","7408.11","Copper wire, >6mm","Cast & rolled rod feed for wire drawing."),
    "cu_c_billet":  ("Component","component","Copper billet / cake","7403.21","Copper alloy, unwrought","Cast semi for tube, sheet and profiles."),
    "cu_c_brass":   ("Component","component","Brass (Cu-Zn alloy)","7403.21","Copper-zinc base alloys","Machinable corrosion-resistant alloy."),
    "cu_c_bronze":  ("Component","component","Bronze (Cu-Sn alloy)","7403.22","Copper-tin base alloys","Wear-resistant bearing alloy."),
  },
  "products": {
    "cu_p_cathode": ("Refined copper cathode","7403.11","Refined copper, cathodes","Exchange-grade copper; feed for all semis."),
    "cu_p_wirerod": ("Copper wire rod","7408.11","Copper wire, >6mm cross-section","Rod for drawing into wire and conductors."),
    "cu_p_wire":    ("Copper wire & winding wire","7408.19","Copper wire","Magnet and conductor wire for motors."),
    "cu_p_cable":   ("Insulated power & data cable","8544.49","Insulated electric conductors","Power, building and communication cable."),
    "cu_p_tube":    ("Copper tube & pipe","7411.10","Copper tubes and pipes","Plumbing, HVAC and refrigeration tube."),
    "cu_p_sheet":   ("Copper sheet, strip & foil","7409.11","Copper plates, sheets, strip","Roofing, electronics and gaskets."),
    "cu_p_busbar":  ("Copper busbar & profiles","7407.10","Copper bars, rods, profiles","Switchgear and distribution conductors."),
    "cu_p_brass":   ("Brass rod, fittings & valves","7407.21","Copper-zinc bars and profiles","Plumbing fittings, valves and hardware."),
    "cu_p_bronze":  ("Bronze bearings & castings","7419.80","Other articles of copper","Bushings, bearings and marine fittings."),
    "cu_p_fittings":("Copper pipe fittings","7412.20","Copper alloy tube/pipe fittings","Elbows, tees and couplings."),
    "cu_p_alu_prof":("Aluminium extrusions & profiles","7604.21","Aluminium profiles","Window frames and structural sections."),
    "cu_p_alu_sheet":("Aluminium sheet & foil","7606.11","Aluminium plates/sheets","Roofing, packaging foil and panels."),
    "cu_p_alu_cond":("Aluminium conductor (ACSR)","7614.10","Stranded aluminium conductor","Overhead power transmission lines."),
    "cu_p_zinc":    ("Zinc sheet & anodes","7905.00","Zinc plates, sheets, strip","Roofing, die-cast and galvanising anodes."),
    "cu_p_lead":    ("Lead products (sheet, battery plate)","7804.11","Lead plates, sheets","Radiation shielding and battery plates."),
    "cu_p_solder":  ("Solder (Sn-Pb / lead-free)","8311.30","Wire/rods for soldering","Joining alloy for electronics and plumbing."),
  },
  "edges": {
    "cu_p_cathode": [("cu_c_cathode",.92),("cu_l_labour",.05),("cu_e_elec",.03)],
    "cu_p_wirerod": [("cu_c_wirerod",.90),("cu_e_elec",.05),("cu_l_labour",.05)],
    "cu_p_wire":    [("cu_c_wirerod",.78),("cu_k_draw",.10),("cu_e_elec",.07),("cu_l_labour",.05)],
    "cu_p_cable":   [("cu_c_wirerod",.62),("cu_m_pvc",.20),("cu_k_draw",.08),("cu_e_elec",.05),("cu_l_labour",.05)],
    "cu_p_tube":    [("cu_c_billet",.72),("cu_k_draw",.12),("cu_e_heat",.08),("cu_l_labour",.08)],
    "cu_p_sheet":   [("cu_c_billet",.72),("cu_k_cast",.12),("cu_e_heat",.08),("cu_l_labour",.08)],
    "cu_p_busbar":  [("cu_c_billet",.74),("cu_k_draw",.10),("cu_e_heat",.08),("cu_l_labour",.08)],
    "cu_p_brass":   [("cu_c_brass",.80),("cu_k_draw",.08),("cu_e_heat",.06),("cu_l_labour",.06)],
    "cu_p_bronze":  [("cu_c_bronze",.80),("cu_k_cast",.08),("cu_e_heat",.06),("cu_l_labour",.06)],
    "cu_p_fittings":[("cu_c_billet",.66),("cu_c_brass",.16),("cu_k_draw",.08),("cu_l_labour",.10)],
    "cu_p_alu_prof":[("cu_m_alu",.74),("cu_k_draw",.12),("cu_e_heat",.08),("cu_l_labour",.06)],
    "cu_p_alu_sheet":[("cu_m_alu",.74),("cu_k_cast",.12),("cu_e_heat",.08),("cu_l_labour",.06)],
    "cu_p_alu_cond":[("cu_m_alu",.78),("cu_k_draw",.10),("cu_e_elec",.06),("cu_l_labour",.06)],
    "cu_p_zinc":    [("cu_m_zinc",.80),("cu_k_cast",.08),("cu_e_heat",.06),("cu_l_labour",.06)],
    "cu_p_lead":    [("cu_m_lead",.80),("cu_k_cast",.08),("cu_e_heat",.06),("cu_l_labour",.06)],
    "cu_p_solder":  [("cu_m_tin",.56),("cu_m_lead",.30),("cu_e_heat",.08),("cu_l_labour",.06)],
    # Intermediates
    "cu_c_wirerod": [("cu_c_cathode",.88),("cu_k_cast",.06),("cu_l_labour",.06)],
    "cu_c_billet":  [("cu_c_cathode",.86),("cu_k_cast",.08),("cu_l_labour",.06)],
    "cu_c_brass":   [("cu_c_cathode",.62),("cu_m_zinc",.30),("cu_e_heat",.04),("cu_l_labour",.04)],
    "cu_c_bronze":  [("cu_c_cathode",.66),("cu_m_tin",.26),("cu_e_heat",.04),("cu_l_labour",.04)],
    "cu_c_cathode": [("cu_t_refine",.55),("cu_t_sxew",.30),("cu_m_scrap",.10),("cu_l_labour",.05)],
    "cu_t_refine":  [("cu_c_blister",.82),("cu_e_elec",.10),("cu_k_smelt",.04),("cu_l_labour",.04)],
    "cu_t_sxew":    [("cu_c_conc",.55),("cu_e_elec",.30),("cu_k_smelt",.08),("cu_l_labour",.07)],
    "cu_c_blister": [("cu_t_smelt",1.0)],
    "cu_t_smelt":   [("cu_c_conc",.70),("cu_e_heat",.16),("cu_k_smelt",.08),("cu_l_labour",.06)],
    "cu_c_conc":    [("cu_m_ore",.82),("cu_e_elec",.08),("cu_l_labour",.10)],
  },
})

# ════════════════════════════════════════════════════════════════════════════
# 2. AUTOMOTIVE
# ════════════════════════════════════════════════════════════════════════════
CHAINS.append({
  "vc": "Automotive",
  "nodes": {
    "au_m_steel":   ("Material","material","Automotive steel (sheet/HSLA)","7208.39","Flat-rolled steel","Body panels, chassis and structural parts."),
    "au_m_alu":     ("Material","material","Aluminium alloy","7601.20","Aluminium alloys","Lightweight body, engine and wheel castings."),
    "au_m_plastic": ("Material","material","Polymer resins","3901.10","Polymers, primary forms","Bumpers, trim and interior mouldings."),
    "au_m_rubber":  ("Material","material","Rubber","4002.19","Synthetic rubber","Tyres, seals and hoses."),
    "au_m_glass":   ("Material","material","Automotive glass","7007.21","Laminated safety glass","Windscreens and windows."),
    "au_m_copper":  ("Material","material","Copper wire","7408.19","Copper wire","Wiring harness and motor windings."),
    "au_m_chips":   ("Material","material","Semiconductors & ECUs","8542.31","Electronic integrated circuits","Engine, safety and infotainment control."),
    "au_m_textile": ("Material","material","Upholstery textile & foam","5903.90","Coated/laminated textile","Seating, headliner and trim."),
    "au_m_paint":   ("Material","material","Coatings & paint","3208.90","Paints and varnishes","Corrosion protection and finish."),
    "au_m_cells":   ("Material","material","Li-ion battery cells","8507.60","Lithium-ion accumulators","Energy storage for EVs and hybrids."),
    "au_m_lead":    ("Material","material","Lead-acid battery","8507.10","Lead-acid accumulators","Starter battery for ICE vehicles."),
    "au_e_elec":    ("Energy","energy","Electricity",None,None,"Stamping, welding and assembly power."),
    "au_l_labour":  ("LaborCost","labor","Labour",None,None,"Assembly, welding and QA labour."),
    "au_k_stamp":   ("MachineryCost","machinery","Stamping press","8462.10","Forging/stamping machines","Presses body panels from steel coil."),
    "au_k_robot":   ("MachineryCost","machinery","Robotic weld & assembly line","8479.50","Industrial robots","Welds body-in-white and assembles units."),
    "au_k_mould":   ("MachineryCost","machinery","Injection moulding","8477.10","Injection-moulding machines","Moulds plastic interior and trim parts."),
    "au_k_machine": ("MachineryCost","machinery","CNC machining & casting","8458.11","Machine tools","Machines engine, transmission and parts."),
    # Intermediate assemblies
    "au_c_biw":     ("Component","component","Body-in-white (welded shell)","8707.10","Bodies for vehicles","Stamped and welded structural body shell."),
    "au_c_engine":  ("Component","component","Internal-combustion engine","8407.34","Spark-ignition engines","Petrol/diesel powertrain."),
    "au_c_emotor":  ("Component","component","Electric drive motor","8501.32","Electric motors","Traction motor for EV/hybrid."),
    "au_c_trans":   ("Component","component","Transmission & driveline","8708.40","Gear boxes for vehicles","Gearbox, axles and driveshafts."),
    "au_c_chassis": ("Component","component","Chassis & suspension","8708.99","Parts and accessories","Frame, suspension and steering."),
    "au_c_battery": ("Component","component","EV battery pack","8507.60","Lithium-ion accumulators","Modules, BMS and housing."),
    "au_c_interior":("Component","component","Interior & seating","9401.20","Seats for motor vehicles","Seats, dashboard and trim."),
    "au_c_harness": ("Component","component","Wiring harness & electronics","8544.30","Ignition wiring sets","Power and signal distribution."),
    "au_c_tyres":   ("Component","component","Tyres & wheels","4011.10","New pneumatic tyres","Road contact and load support."),
  },
  "products": {
    "au_p_car":     ("Passenger car (ICE)","8703.23","Motor cars, spark-ignition","Mainstream petrol/diesel passenger vehicle."),
    "au_p_ev":      ("Battery electric vehicle (BEV)","8703.80","Motor cars, electric","Fully electric passenger vehicle."),
    "au_p_hybrid":  ("Hybrid vehicle (HEV/PHEV)","8703.60","Motor cars, hybrid","Combined ICE + electric drive vehicle."),
    "au_p_pickup":  ("Pickup / light commercial","8704.21","Motor vehicles for goods, <5t","Light goods and utility vehicle."),
    "au_p_truck":   ("Truck / heavy lorry","8704.23","Motor vehicles for goods, >20t","Heavy goods transport vehicle."),
    "au_p_bus":     ("Bus & coach","8702.10","Motor vehicles, >10 persons","Public and intercity passenger transport."),
    "au_p_motorcycle":("Motorcycle","8711.20","Motorcycles, 50-250cc","Two-wheeler personal transport."),
    "au_p_threewheel":("Three-wheeler (auto-rickshaw)","8703.21","Motor cars, <1000cc","Low-cost passenger/goods three-wheeler."),
    "au_p_tractor": ("Agricultural tractor","8701.92","Tractors, 18-37kW","Farm traction and PTO power."),
    "au_p_trailer": ("Trailer & semi-trailer","8716.39","Trailers for goods transport","Towed goods-carrying unit."),
    "au_p_engine":  ("Engines (standalone)","8407.90","Spark-ignition engines","Replacement and OEM engine units."),
    "au_p_parts":   ("Auto components & spares","8708.99","Parts and accessories","Aftermarket and OEM components."),
    "au_p_battery": ("Automotive batteries","8507.10","Electric accumulators","Starter and traction batteries."),
    "au_p_tyres":   ("Tyres & tubes","4011.10","New pneumatic tyres","Replacement and OEM tyres."),
  },
  "edges": {
    "au_p_car":     [("au_c_biw",.26),("au_c_engine",.22),("au_c_trans",.12),("au_c_chassis",.12),("au_c_interior",.10),("au_c_harness",.06),("au_c_tyres",.06),("au_l_labour",.06)],
    "au_p_ev":      [("au_c_biw",.22),("au_c_battery",.34),("au_c_emotor",.14),("au_c_chassis",.10),("au_c_interior",.08),("au_c_harness",.06),("au_c_tyres",.06)],
    "au_p_hybrid":  [("au_c_biw",.22),("au_c_engine",.18),("au_c_emotor",.12),("au_c_battery",.16),("au_c_trans",.10),("au_c_interior",.08),("au_c_tyres",.06),("au_l_labour",.08)],
    "au_p_pickup":  [("au_c_biw",.28),("au_c_engine",.22),("au_c_trans",.12),("au_c_chassis",.16),("au_c_interior",.08),("au_c_tyres",.08),("au_l_labour",.06)],
    "au_p_truck":   [("au_c_chassis",.30),("au_c_engine",.26),("au_c_trans",.16),("au_c_biw",.10),("au_c_tyres",.10),("au_l_labour",.08)],
    "au_p_bus":     [("au_c_biw",.30),("au_c_engine",.22),("au_c_chassis",.18),("au_c_interior",.14),("au_c_tyres",.08),("au_l_labour",.08)],
    "au_p_motorcycle":[("au_m_steel",.30),("au_c_engine",.34),("au_c_tyres",.12),("au_c_harness",.08),("au_l_labour",.16)],
    "au_p_threewheel":[("au_m_steel",.30),("au_c_engine",.30),("au_c_tyres",.14),("au_c_interior",.10),("au_l_labour",.16)],
    "au_p_tractor": [("au_c_engine",.32),("au_c_trans",.22),("au_c_chassis",.22),("au_c_tyres",.12),("au_l_labour",.12)],
    "au_p_trailer": [("au_m_steel",.56),("au_c_chassis",.20),("au_c_tyres",.14),("au_l_labour",.10)],
    "au_p_engine":  [("au_c_engine",.92),("au_l_labour",.08)],
    "au_p_parts":   [("au_c_chassis",.34),("au_c_trans",.30),("au_m_steel",.16),("au_l_labour",.20)],
    "au_p_battery": [("au_m_lead",.46),("au_m_cells",.34),("au_m_plastic",.10),("au_l_labour",.10)],
    "au_p_tyres":   [("au_c_tyres",.92),("au_l_labour",.08)],
    # Intermediate assemblies
    "au_c_biw":     [("au_m_steel",.58),("au_m_alu",.16),("au_k_stamp",.10),("au_k_robot",.08),("au_m_paint",.04),("au_l_labour",.04)],
    "au_c_engine":  [("au_m_alu",.30),("au_m_steel",.30),("au_k_machine",.20),("au_m_chips",.08),("au_l_labour",.12)],
    "au_c_emotor":  [("au_m_copper",.42),("au_m_steel",.26),("au_m_chips",.14),("au_k_machine",.10),("au_l_labour",.08)],
    "au_c_trans":   [("au_m_steel",.52),("au_k_machine",.26),("au_e_elec",.08),("au_l_labour",.14)],
    "au_c_chassis": [("au_m_steel",.62),("au_k_stamp",.14),("au_m_rubber",.08),("au_l_labour",.16)],
    "au_c_battery": [("au_m_cells",.70),("au_m_chips",.12),("au_m_alu",.08),("au_l_labour",.10)],
    "au_c_interior":[("au_m_plastic",.40),("au_m_textile",.34),("au_k_mould",.12),("au_l_labour",.14)],
    "au_c_harness": [("au_m_copper",.46),("au_m_plastic",.24),("au_m_chips",.16),("au_l_labour",.14)],
    "au_c_tyres":   [("au_m_rubber",.62),("au_m_steel",.12),("au_e_elec",.10),("au_l_labour",.16)],
  },
})

# ════════════════════════════════════════════════════════════════════════════
# 3. TEXTILES & GARMENTS
# ════════════════════════════════════════════════════════════════════════════
CHAINS.append({
  "vc": "Textiles & Garments",
  "nodes": {
    "tx_m_cotton":  ("Material","material","Raw cotton","5201.00","Cotton, not carded/combed","Natural staple fibre; ginned lint."),
    "tx_m_poly":    ("Material","material","Polyester fibre (PET)","5503.20","Synthetic staple fibres","Synthetic staple and filament fibre."),
    "tx_m_visc":    ("Material","material","Viscose / rayon fibre","5504.10","Artificial staple fibres","Cellulosic fibre for soft fabrics."),
    "tx_m_wool":    ("Material","material","Wool","5101.11","Wool, greasy","Animal protein fibre."),
    "tx_m_dye":     ("Material","material","Dyes & finishing chemicals","3204.17","Synthetic organic dyes","Colour and functional finishing."),
    "tx_m_trim":    ("Material","material","Trims, zips & buttons","9607.11","Slide fasteners","Garment closures and accessories."),
    "tx_e_elec":    ("Energy","energy","Electricity",None,None,"Spinning, weaving and machine power."),
    "tx_e_heat":    ("Energy","energy","Process steam / heat",None,None,"Dyeing, drying and finishing heat."),
    "tx_l_labour":  ("LaborCost","labor","Labour",None,None,"Spinning, stitching and finishing labour."),
    "tx_k_spin":    ("MachineryCost","machinery","Spinning frame","8445.20","Textile spinning machines","Spins fibre into yarn."),
    "tx_k_loom":    ("MachineryCost","machinery","Weaving loom","8446.21","Weaving machines (looms)","Interlaces yarn into woven fabric."),
    "tx_k_knit":    ("MachineryCost","machinery","Knitting machine","8447.11","Knitting machines","Forms knitted fabric from yarn."),
    "tx_k_dye":     ("MachineryCost","machinery","Dyeing & finishing plant","8451.40","Washing/dyeing machines","Dyes, prints and finishes fabric."),
    "tx_k_sew":     ("MachineryCost","machinery","Sewing & cutting line","8452.21","Sewing machines, automatic","Cuts and stitches garments."),
    # Intermediates
    "tx_c_yarn":    ("Component","component","Yarn (cotton/synthetic)","5205.12","Cotton yarn","Spun yarn for weaving and knitting."),
    "tx_c_woven":   ("Component","component","Grey woven fabric","5208.11","Woven cotton fabric","Loom-state unfinished woven cloth."),
    "tx_c_knit":    ("Component","component","Knitted fabric","6006.21","Knitted/crocheted fabrics","Stretch fabric for jersey wear."),
    "tx_c_finfab":  ("Component","component","Dyed & finished fabric","5208.31","Woven cotton, dyed","Coloured, finished cloth ready to cut."),
    "tx_c_nonwoven":("Component","component","Nonwoven fabric","5603.11","Nonwovens","Bonded web for technical and hygiene use."),
  },
  "products": {
    "tx_p_yarn":    ("Yarn (cotton & synthetic)","5205.12","Cotton/synthetic yarn","Industrial yarn for weaving and knitting."),
    "tx_p_fabric":  ("Finished fabric (woven & knit)","5208.31","Finished woven/knit fabric","Dyed cloth for garment and home use."),
    "tx_p_tshirt":  ("T-shirts & knitwear","6109.10","T-shirts, knitted","Mass-market knit tops."),
    "tx_p_shirts":  ("Shirts & blouses (woven)","6205.20","Men's shirts, cotton","Formal and casual woven shirts."),
    "tx_p_trousers":("Trousers, jeans & denim","6203.42","Men's trousers, cotton","Denim and casual bottoms."),
    "tx_p_dresses": ("Dresses & womenswear","6204.42","Women's dresses, cotton","Fashion and occasion wear."),
    "tx_p_underwear":("Underwear & hosiery","6107.11","Underpants, knitted","Innerwear, socks and hosiery."),
    "tx_p_workwear":("Uniforms & workwear","6211.33","Track suits / workwear","Industrial, school and corporate uniforms."),
    "tx_p_home":    ("Home textiles (linen, towels)","6302.31","Bed linen, cotton","Bedsheets, towels and curtains."),
    "tx_p_carpet":  ("Carpets & rugs","5703.31","Tufted carpets","Floor coverings and mats."),
    "tx_p_technical":("Technical & industrial textiles","5911.90","Textiles for technical use","Filtration, geotextiles and belting."),
    "tx_p_bags":    ("Bags & sacks (woven)","6305.33","Sacks/bags, polyethylene strip","Packaging and shopping bags."),
    "tx_p_medical": ("Medical & hygiene textiles","5603.11","Nonwoven hygiene textiles","Masks, gowns and sanitary products."),
  },
  "edges": {
    "tx_p_yarn":    [("tx_c_yarn",.92),("tx_l_labour",.05),("tx_e_elec",.03)],
    "tx_p_fabric":  [("tx_c_finfab",.90),("tx_l_labour",.06),("tx_e_elec",.04)],
    "tx_p_tshirt":  [("tx_c_knit",.58),("tx_k_sew",.10),("tx_m_trim",.06),("tx_e_elec",.04),("tx_l_labour",.22)],
    "tx_p_shirts":  [("tx_c_finfab",.56),("tx_k_sew",.10),("tx_m_trim",.08),("tx_l_labour",.26)],
    "tx_p_trousers":[("tx_c_finfab",.58),("tx_k_sew",.10),("tx_m_trim",.08),("tx_l_labour",.24)],
    "tx_p_dresses": [("tx_c_finfab",.54),("tx_k_sew",.10),("tx_m_trim",.08),("tx_l_labour",.28)],
    "tx_p_underwear":[("tx_c_knit",.54),("tx_k_sew",.10),("tx_m_trim",.06),("tx_l_labour",.30)],
    "tx_p_workwear":[("tx_c_finfab",.58),("tx_k_sew",.10),("tx_m_trim",.08),("tx_l_labour",.24)],
    "tx_p_home":    [("tx_c_finfab",.66),("tx_k_sew",.08),("tx_e_heat",.06),("tx_l_labour",.20)],
    "tx_p_carpet":  [("tx_c_yarn",.60),("tx_k_knit",.12),("tx_e_heat",.08),("tx_l_labour",.20)],
    "tx_p_technical":[("tx_c_nonwoven",.62),("tx_k_dye",.10),("tx_e_heat",.10),("tx_l_labour",.18)],
    "tx_p_bags":    [("tx_c_woven",.66),("tx_k_sew",.10),("tx_e_elec",.06),("tx_l_labour",.18)],
    "tx_p_medical": [("tx_c_nonwoven",.66),("tx_k_sew",.08),("tx_e_elec",.06),("tx_l_labour",.20)],
    # Intermediates
    "tx_c_yarn":    [("tx_m_cotton",.46),("tx_m_poly",.24),("tx_m_visc",.08),("tx_k_spin",.08),("tx_e_elec",.06),("tx_l_labour",.08)],
    "tx_c_woven":   [("tx_c_yarn",.70),("tx_k_loom",.12),("tx_e_elec",.08),("tx_l_labour",.10)],
    "tx_c_knit":    [("tx_c_yarn",.70),("tx_k_knit",.12),("tx_e_elec",.08),("tx_l_labour",.10)],
    "tx_c_finfab":  [("tx_c_woven",.62),("tx_m_dye",.14),("tx_k_dye",.10),("tx_e_heat",.08),("tx_l_labour",.06)],
    "tx_c_nonwoven":[("tx_m_poly",.62),("tx_e_heat",.14),("tx_e_elec",.10),("tx_l_labour",.14)],
  },
})

# ════════════════════════════════════════════════════════════════════════════
# 4. PHARMACEUTICALS
# ════════════════════════════════════════════════════════════════════════════
CHAINS.append({
  "vc": "Pharmaceuticals",
  "nodes": {
    "ph_m_inter":   ("Material","material","Chemical intermediates","2933.39","Heterocyclic compounds","Building blocks for API synthesis."),
    "ph_m_solvent": ("Material","material","Solvents & reagents","2902.00","Cyclic hydrocarbons","Reaction and purification media."),
    "ph_m_excip":   ("Material","material","Excipients","3912.12","Cellulose and derivatives","Fillers, binders and coatings."),
    "ph_m_bio":     ("Material","material","Biological substrates","3002.90","Human/animal substances","Cell cultures and antigens."),
    "ph_m_pack":    ("Material","material","Primary packaging","3923.90","Plastic packaging","Blisters, bottles and closures."),
    "ph_m_glass":   ("Material","material","Glass vials & ampoules","7010.10","Glass ampoules","Sterile primary containers."),
    "ph_e_elec":    ("Energy","energy","Electricity / utilities",None,None,"Clean-room HVAC and process power."),
    "ph_l_labour":  ("LaborCost","labor","Skilled labour & QA",None,None,"Pharmacists, technicians and QA staff."),
    "ph_k_reactor": ("MachineryCost","machinery","Synthesis reactor","8419.89","Chemical reaction vessels","API synthesis and purification."),
    "ph_k_tablet":  ("MachineryCost","machinery","Tablet press & coater","8479.82","Mixing/processing machines","Compresses and coats tablets."),
    "ph_k_fill":    ("MachineryCost","machinery","Aseptic filling line","8422.30","Filling/sealing machines","Sterile filling of vials and ampoules."),
    "ph_k_qc":      ("MachineryCost","machinery","QC & lab instruments","9027.80","Physical/chemical analysis","Assay, purity and release testing."),
    # Intermediates
    "ph_c_api":     ("Component","component","Active ingredient (API)","2941.90","Antibiotics; active compounds","Synthesised therapeutic molecule."),
    "ph_c_form":    ("Component","component","Formulated blend","3003.90","Medicaments, bulk","API + excipients ready to dose."),
  },
  "products": {
    "ph_p_tablets": ("Tablets & capsules","3004.90","Medicaments, dosed","Solid oral dosage forms."),
    "ph_p_inject":  ("Injectables & vials","3004.90","Medicaments, dosed","Sterile parenteral medicines."),
    "ph_p_syrups":  ("Syrups & oral liquids","3004.90","Medicaments, dosed","Liquid oral suspensions and elixirs."),
    "ph_p_ointment":("Ointments & creams","3004.90","Medicaments, dosed","Topical semi-solid preparations."),
    "ph_p_iv":      ("IV fluids & infusions","3004.90","Medicaments, dosed","Large-volume parenteral fluids."),
    "ph_p_vaccine": ("Vaccines & biologics","3002.41","Vaccines for human medicine","Immunological and biologic products."),
    "ph_p_antibiotic":("Antibiotics","3004.10","Medicaments w/ penicillins","Anti-bacterial therapeutics."),
    "ph_p_antimal": ("Antimalarials","3004.90","Antimalarial medicaments","Malaria treatment (ACT and others)."),
    "ph_p_arv":     ("Antiretrovirals (ARVs)","3004.90","Antiretroviral medicaments","HIV/AIDS treatment regimens."),
    "ph_p_otc":     ("OTC & analgesics","3004.90","Medicaments, dosed","Pain, cold and over-the-counter lines."),
    "ph_p_supp":    ("Vitamins & supplements","3004.50","Medicaments w/ vitamins","Nutritional and mineral supplements."),
    "ph_p_vet":     ("Veterinary medicines","3004.90","Veterinary medicaments","Livestock and companion-animal drugs."),
    "ph_p_api":     ("Bulk APIs","2941.90","Active pharmaceutical ingredients","Active ingredients sold to formulators."),
    "ph_p_devices": ("Medical devices & consumables","9018.31","Syringes, needles","Syringes, IV sets and disposables."),
    "ph_p_diag":    ("Diagnostic reagents & kits","3822.00","Diagnostic reagents","Lab and rapid test kits."),
  },
  "edges": {
    "ph_p_tablets": [("ph_c_form",.58),("ph_k_tablet",.12),("ph_m_pack",.14),("ph_l_labour",.12),("ph_k_qc",.04)],
    "ph_p_inject":  [("ph_c_api",.40),("ph_k_fill",.18),("ph_m_glass",.18),("ph_l_labour",.16),("ph_k_qc",.08)],
    "ph_p_syrups":  [("ph_c_form",.52),("ph_m_solvent",.12),("ph_m_pack",.18),("ph_l_labour",.14),("ph_k_qc",.04)],
    "ph_p_ointment":[("ph_c_form",.54),("ph_m_excip",.14),("ph_m_pack",.16),("ph_l_labour",.12),("ph_k_qc",.04)],
    "ph_p_iv":      [("ph_m_solvent",.30),("ph_c_form",.24),("ph_k_fill",.18),("ph_m_pack",.16),("ph_l_labour",.12)],
    "ph_p_vaccine": [("ph_m_bio",.42),("ph_k_fill",.18),("ph_m_glass",.16),("ph_l_labour",.14),("ph_k_qc",.10)],
    "ph_p_antibiotic":[("ph_c_api",.50),("ph_m_excip",.14),("ph_k_tablet",.10),("ph_m_pack",.12),("ph_l_labour",.14)],
    "ph_p_antimal": [("ph_c_api",.50),("ph_m_excip",.14),("ph_k_tablet",.10),("ph_m_pack",.12),("ph_l_labour",.14)],
    "ph_p_arv":     [("ph_c_api",.54),("ph_m_excip",.12),("ph_k_tablet",.10),("ph_m_pack",.12),("ph_l_labour",.12)],
    "ph_p_otc":     [("ph_c_form",.56),("ph_k_tablet",.12),("ph_m_pack",.16),("ph_l_labour",.12),("ph_k_qc",.04)],
    "ph_p_supp":    [("ph_c_form",.50),("ph_m_excip",.20),("ph_m_pack",.16),("ph_l_labour",.14)],
    "ph_p_vet":     [("ph_c_form",.54),("ph_m_excip",.14),("ph_m_pack",.16),("ph_l_labour",.16)],
    "ph_p_api":     [("ph_c_api",.90),("ph_k_qc",.06),("ph_l_labour",.04)],
    "ph_p_devices": [("ph_m_pack",.50),("ph_k_fill",.16),("ph_e_elec",.10),("ph_l_labour",.24)],
    "ph_p_diag":    [("ph_m_bio",.40),("ph_m_solvent",.18),("ph_k_qc",.16),("ph_l_labour",.18),("ph_m_pack",.08)],
    # Intermediates
    "ph_c_api":     [("ph_m_inter",.46),("ph_m_solvent",.18),("ph_k_reactor",.16),("ph_e_elec",.08),("ph_l_labour",.12)],
    "ph_c_form":    [("ph_c_api",.60),("ph_m_excip",.24),("ph_l_labour",.10),("ph_k_qc",.06)],
  },
})

# ════════════════════════════════════════════════════════════════════════════
# 5. PETROCHEMICALS & FERTILIZERS
# ════════════════════════════════════════════════════════════════════════════
CHAINS.append({
  "vc": "Petrochemicals & Fertilizers",
  "nodes": {
    "pc_m_crude":   ("Material","material","Crude oil","2709.00","Petroleum oils, crude","Feedstock for refining and naphtha."),
    "pc_m_gas":     ("Material","material","Natural gas","2711.21","Natural gas, gaseous","Feedstock for ammonia and methanol."),
    "pc_m_naphtha": ("Material","material","Naphtha","2710.12","Light petroleum distillates","Steam-cracker feedstock."),
    "pc_m_phos":    ("Material","material","Phosphate rock","2510.10","Natural calcium phosphates","Source of P for phosphate fertilizers."),
    "pc_m_potash":  ("Material","material","Potash (MOP)","3104.20","Potassium chloride","Source of K for fertilizers."),
    "pc_m_sulphur": ("Material","material","Sulphur","2503.00","Sulphur of all kinds","Feed for sulphuric acid."),
    "pc_e_elec":    ("Energy","energy","Electricity",None,None,"Compression and plant power."),
    "pc_e_steam":   ("Energy","energy","Process steam / heat",None,None,"Cracking, reforming and reaction heat."),
    "pc_l_labour":  ("LaborCost","labor","Labour",None,None,"Process operators and engineers."),
    "pc_k_crack":   ("MachineryCost","machinery","Steam cracker","8419.40","Distilling/cracking plant","Cracks naphtha/gas to olefins."),
    "pc_k_reform":  ("MachineryCost","machinery","Reformer / ammonia plant","8419.89","Reaction plant","Reforms gas to syngas and ammonia."),
    "pc_k_poly":    ("MachineryCost","machinery","Polymerisation reactor","8477.80","Polymer processing plant","Polymerises monomers to resin."),
    # Intermediates
    "pc_c_ethylene":("Component","component","Ethylene","2901.21","Ethylene","Olefin building block for PE/PVC/PET."),
    "pc_c_propylene":("Component","component","Propylene","2901.22","Propene (propylene)","Olefin building block for PP."),
    "pc_c_btx":     ("Component","component","Aromatics (BTX)","2902.20","Benzene","Benzene/toluene/xylene for PS and solvents."),
    "pc_c_ammonia": ("Component","component","Ammonia","2814.10","Anhydrous ammonia","Base for nitrogen fertilizers."),
    "pc_c_methanol":("Component","component","Methanol","2905.11","Methanol","Solvent and chemical feedstock."),
    "pc_c_nitric":  ("Component","component","Nitric acid","2808.00","Nitric acid","Oxidiser for nitrate fertilizers."),
    "pc_c_sulphuric":("Component","component","Sulphuric acid","2807.00","Sulphuric acid","Acidulant for phosphate fertilizers."),
    "pc_c_phosacid":("Component","component","Phosphoric acid","2809.20","Phosphoric acid","Feed for DAP/MAP and SSP."),
  },
  "products": {
    "pc_p_pe":      ("Polyethylene (PE) resin","3901.10","Polyethylene, primary","Film, bottle and pipe polymer."),
    "pc_p_pp":      ("Polypropylene (PP) resin","3902.10","Polypropylene, primary","Moulding and fibre polymer."),
    "pc_p_pvc":     ("PVC resin","3904.10","Poly(vinyl chloride)","Pipe, profile and cable polymer."),
    "pc_p_pet":     ("PET resin","3907.61","Poly(ethylene terephthalate)","Bottle and fibre polymer."),
    "pc_p_ps":      ("Polystyrene (PS/EPS)","3903.11","Polystyrene, expansible","Packaging and insulation polymer."),
    "pc_p_rubber":  ("Synthetic rubber","4002.19","Styrene-butadiene rubber","Tyre and seal elastomer."),
    "pc_p_solvent": ("Industrial solvents","2902.30","Toluene","Paints, coatings and process solvents."),
    "pc_p_methanol":("Methanol","2905.11","Methanol","Chemical and fuel-grade methanol."),
    "pc_p_urea":    ("Urea","3102.10","Urea","High-analysis nitrogen fertilizer."),
    "pc_p_can":     ("Ammonium nitrate / CAN","3102.30","Ammonium nitrate","Nitrogen fertilizer and blasting grade."),
    "pc_p_dap":     ("DAP / MAP","3105.30","Diammonium phosphate","Nitrogen-phosphorus fertilizer."),
    "pc_p_ssp":     ("Single superphosphate (SSP)","3103.11","Superphosphates","Phosphate fertilizer."),
    "pc_p_npk":     ("NPK compound fertilizer","3105.20","Mineral fertilizers N-P-K","Balanced multi-nutrient fertilizer."),
    "pc_p_mop":     ("Potassium fertilizer (MOP)","3104.20","Potassium chloride","Potash fertilizer."),
    "pc_p_ammonia": ("Ammonia","2814.10","Anhydrous ammonia","Merchant ammonia for industry."),
  },
  "edges": {
    "pc_p_pe":      [("pc_c_ethylene",.70),("pc_k_poly",.14),("pc_e_elec",.08),("pc_l_labour",.08)],
    "pc_p_pp":      [("pc_c_propylene",.70),("pc_k_poly",.14),("pc_e_elec",.08),("pc_l_labour",.08)],
    "pc_p_pvc":     [("pc_c_ethylene",.60),("pc_k_poly",.16),("pc_e_elec",.14),("pc_l_labour",.10)],
    "pc_p_pet":     [("pc_c_ethylene",.40),("pc_c_btx",.34),("pc_k_poly",.12),("pc_e_elec",.06),("pc_l_labour",.08)],
    "pc_p_ps":      [("pc_c_btx",.46),("pc_c_ethylene",.26),("pc_k_poly",.12),("pc_e_elec",.08),("pc_l_labour",.08)],
    "pc_p_rubber":  [("pc_c_btx",.40),("pc_c_propylene",.30),("pc_k_poly",.12),("pc_e_steam",.10),("pc_l_labour",.08)],
    "pc_p_solvent": [("pc_c_btx",.78),("pc_e_steam",.08),("pc_e_elec",.06),("pc_l_labour",.08)],
    "pc_p_methanol":[("pc_c_methanol",.90),("pc_e_elec",.05),("pc_l_labour",.05)],
    "pc_p_urea":    [("pc_c_ammonia",.66),("pc_e_steam",.16),("pc_k_reform",.08),("pc_l_labour",.10)],
    "pc_p_can":     [("pc_c_ammonia",.46),("pc_c_nitric",.34),("pc_e_steam",.08),("pc_l_labour",.12)],
    "pc_p_dap":     [("pc_c_ammonia",.34),("pc_c_phosacid",.46),("pc_e_steam",.08),("pc_l_labour",.12)],
    "pc_p_ssp":     [("pc_m_phos",.46),("pc_c_sulphuric",.38),("pc_e_steam",.06),("pc_l_labour",.10)],
    "pc_p_npk":     [("pc_c_ammonia",.20),("pc_c_phosacid",.24),("pc_m_potash",.26),("pc_e_steam",.12),("pc_l_labour",.18)],
    "pc_p_mop":     [("pc_m_potash",.86),("pc_e_elec",.06),("pc_l_labour",.08)],
    "pc_p_ammonia": [("pc_c_ammonia",.92),("pc_e_steam",.04),("pc_l_labour",.04)],
    # Intermediates
    "pc_c_ethylene":[("pc_m_naphtha",.58),("pc_m_gas",.16),("pc_k_crack",.12),("pc_e_steam",.08),("pc_l_labour",.06)],
    "pc_c_propylene":[("pc_m_naphtha",.62),("pc_k_crack",.14),("pc_e_steam",.10),("pc_l_labour",.06),("pc_e_elec",.08)],
    "pc_c_btx":     [("pc_m_naphtha",.66),("pc_k_crack",.12),("pc_e_steam",.10),("pc_l_labour",.06),("pc_e_elec",.06)],
    "pc_c_ammonia": [("pc_m_gas",.58),("pc_k_reform",.16),("pc_e_steam",.16),("pc_l_labour",.10)],
    "pc_c_methanol":[("pc_m_gas",.66),("pc_k_reform",.14),("pc_e_steam",.12),("pc_l_labour",.08)],
    "pc_c_nitric":  [("pc_c_ammonia",.72),("pc_e_steam",.12),("pc_l_labour",.08),("pc_e_elec",.08)],
    "pc_c_sulphuric":[("pc_m_sulphur",.70),("pc_e_steam",.12),("pc_l_labour",.08),("pc_e_elec",.10)],
    "pc_c_phosacid":[("pc_m_phos",.50),("pc_c_sulphuric",.34),("pc_e_steam",.06),("pc_l_labour",.10)],
  },
})

# ════════════════════════════════════════════════════════════════════════════
# 6. SUGAR & CONFECTIONERY
# ════════════════════════════════════════════════════════════════════════════
CHAINS.append({
  "vc": "Sugar & Confectionery",
  "nodes": {
    "sg_m_cane":    ("Material","material","Sugarcane","1212.93","Sugar cane","Harvested cane; sucrose feedstock."),
    "sg_m_cocoa":   ("Material","material","Cocoa beans","1801.00","Cocoa beans","Feedstock for chocolate products."),
    "sg_m_milk":    ("Material","material","Milk solids","0402.21","Milk powder","Dairy base for toffee and chocolate."),
    "sg_m_flav":    ("Material","material","Flavours, colours & additives","3302.10","Flavouring mixtures","Taste, colour and preservation."),
    "sg_m_pectin":  ("Material","material","Gelatin / pectin","3503.00","Gelatin","Gelling agent for jellies and gums."),
    "sg_m_fruit":   ("Material","material","Fruit pulp","2008.99","Prepared fruit","Base for jams and preserves."),
    "sg_e_elec":    ("Energy","energy","Electricity",None,None,"Mill, packaging and plant power."),
    "sg_e_steam":   ("Energy","energy","Process steam (bagasse)",None,None,"Evaporation and crystallisation heat."),
    "sg_l_labour":  ("LaborCost","labor","Labour",None,None,"Milling, processing and packing labour."),
    "sg_k_mill":    ("MachineryCost","machinery","Cane mill & crusher","8438.30","Sugar manufacturing machinery","Crushes cane and extracts juice."),
    "sg_k_centri":  ("MachineryCost","machinery","Centrifuge & crystalliser","8421.19","Centrifuges","Separates sugar crystals from molasses."),
    "sg_k_pack":    ("MachineryCost","machinery","Processing & packaging line","8422.30","Packing machinery","Cooks, forms and packs confectionery."),
    # Intermediates
    "sg_c_juice":   ("Component","component","Cane juice","1212.93","Extracted cane juice","Raw sucrose-bearing juice."),
    "sg_c_raw":     ("Component","component","Raw sugar","1701.13","Cane sugar, raw","Crystallised unrefined sugar."),
    "sg_c_refined": ("Component","component","Refined white sugar","1701.99","Refined sugar","Purified white sucrose."),
    "sg_c_molasses":("Component","component","Molasses","1703.10","Cane molasses","Syrup by-product; fermentation feed."),
    "sg_c_syrup":   ("Component","component","Sugar / glucose syrup","1702.30","Glucose and syrup","Liquid sugar for confectionery."),
    "sg_c_cocoa":   ("Component","component","Cocoa liquor & butter","1803.10","Cocoa paste","Ground roasted cocoa mass."),
  },
  "products": {
    "sg_p_white":   ("Refined white sugar","1701.99","Refined cane sugar","Table and industrial white sugar."),
    "sg_p_brown":   ("Brown / raw sugar","1701.13","Raw cane sugar","Mill-white and brown sugar."),
    "sg_p_icing":   ("Icing & specialty sugars","1701.91","Sugar with flavouring","Icing, caster and cube sugar."),
    "sg_p_molasses":("Molasses","1703.10","Cane molasses","Animal feed and distillery feedstock."),
    "sg_p_ethanol": ("Ethanol & spirits","2207.10","Undenatured ethanol","Potable and industrial alcohol."),
    "sg_p_hardcandy":("Hard-boiled sweets","1704.90","Sugar confectionery","Boiled sugar candies and lollipops."),
    "sg_p_toffee":  ("Toffees & caramels","1704.90","Sugar confectionery","Milk-based chewy confectionery."),
    "sg_p_chocolate":("Chocolate & cocoa confectionery","1806.31","Chocolate, filled","Bars, pralines and coatings."),
    "sg_p_gums":    ("Gums & jellies","1704.90","Sugar confectionery","Gummies, pastilles and jellies."),
    "sg_p_chewing": ("Chewing gum","1704.10","Chewing gum","Gum base confectionery."),
    "sg_p_biscuits":("Biscuits & cookies","1905.31","Sweet biscuits","Baked sweet snacks."),
    "sg_p_bakery":  ("Cakes & bakery confectionery","1905.90","Bakery products","Cakes, pastries and confections."),
    "sg_p_softdrink":("Sweetened beverages","2202.10","Sweetened waters","Soft drinks and squashes."),
    "sg_p_jam":     ("Jams & preserves","2007.99","Jams and jellies","Fruit preserves and marmalades."),
  },
  "edges": {
    "sg_p_white":   [("sg_c_refined",.90),("sg_e_elec",.04),("sg_l_labour",.06)],
    "sg_p_brown":   [("sg_c_raw",.90),("sg_e_elec",.04),("sg_l_labour",.06)],
    "sg_p_icing":   [("sg_c_refined",.78),("sg_m_flav",.08),("sg_k_pack",.06),("sg_l_labour",.08)],
    "sg_p_molasses":[("sg_c_molasses",.92),("sg_l_labour",.08)],
    "sg_p_ethanol": [("sg_c_molasses",.66),("sg_e_steam",.16),("sg_k_centri",.08),("sg_l_labour",.10)],
    "sg_p_hardcandy":[("sg_c_syrup",.58),("sg_m_flav",.14),("sg_k_pack",.12),("sg_e_steam",.06),("sg_l_labour",.10)],
    "sg_p_toffee":  [("sg_c_syrup",.46),("sg_m_milk",.24),("sg_m_flav",.10),("sg_k_pack",.10),("sg_l_labour",.10)],
    "sg_p_chocolate":[("sg_c_cocoa",.40),("sg_c_refined",.26),("sg_m_milk",.18),("sg_k_pack",.08),("sg_l_labour",.08)],
    "sg_p_gums":    [("sg_c_syrup",.50),("sg_m_pectin",.18),("sg_m_flav",.12),("sg_k_pack",.10),("sg_l_labour",.10)],
    "sg_p_chewing": [("sg_c_syrup",.46),("sg_m_flav",.22),("sg_k_pack",.12),("sg_l_labour",.20)],
    "sg_p_biscuits":[("sg_c_refined",.34),("sg_m_flav",.16),("sg_k_pack",.14),("sg_e_steam",.12),("sg_l_labour",.24)],
    "sg_p_bakery":  [("sg_c_refined",.32),("sg_m_flav",.16),("sg_m_milk",.12),("sg_k_pack",.12),("sg_l_labour",.28)],
    "sg_p_softdrink":[("sg_c_syrup",.40),("sg_m_flav",.20),("sg_k_pack",.16),("sg_e_elec",.08),("sg_l_labour",.16)],
    "sg_p_jam":     [("sg_c_refined",.38),("sg_m_fruit",.34),("sg_k_pack",.10),("sg_e_steam",.08),("sg_l_labour",.10)],
    # Intermediates
    "sg_c_juice":   [("sg_m_cane",.78),("sg_k_mill",.10),("sg_e_elec",.06),("sg_l_labour",.06)],
    "sg_c_raw":     [("sg_c_juice",.66),("sg_e_steam",.16),("sg_k_centri",.10),("sg_l_labour",.08)],
    "sg_c_refined": [("sg_c_raw",.80),("sg_e_steam",.08),("sg_k_centri",.06),("sg_l_labour",.06)],
    "sg_c_molasses":[("sg_c_juice",.86),("sg_k_centri",.08),("sg_l_labour",.06)],
    "sg_c_syrup":   [("sg_c_refined",.84),("sg_e_steam",.08),("sg_l_labour",.08)],
    "sg_c_cocoa":   [("sg_m_cocoa",.80),("sg_e_steam",.08),("sg_k_pack",.06),("sg_l_labour",.06)],
  },
})

# ════════════════════════════════════════════════════════════════════════════
# 7. PLASTICS & PACKAGING
# ════════════════════════════════════════════════════════════════════════════
CHAINS.append({
  "vc": "Plastics & Packaging",
  "nodes": {
    "pl_m_pe":      ("Material","material","Polyethylene resin","3901.10","Polyethylene, primary","HDPE/LDPE for film, bottles and pipe."),
    "pl_m_pp":      ("Material","material","Polypropylene resin","3902.10","Polypropylene, primary","Moulding and woven-sack polymer."),
    "pl_m_pvc":     ("Material","material","PVC resin","3904.10","Poly(vinyl chloride)","Pipe and profile polymer."),
    "pl_m_pet":     ("Material","material","PET resin","3907.61","Poly(ethylene terephthalate)","Bottle-grade polymer."),
    "pl_m_ps":      ("Material","material","Polystyrene resin","3903.11","Polystyrene","Foam and rigid packaging polymer."),
    "pl_m_paper":   ("Material","material","Paper & paperboard","4805.11","Paper and paperboard","Corrugated and carton stock."),
    "pl_m_foil":    ("Material","material","Aluminium foil","7607.11","Aluminium foil","Barrier layer for laminates."),
    "pl_m_add":     ("Material","material","Masterbatch & additives","3206.49","Colouring matter","Colour, UV and process additives."),
    "pl_m_recyc":   ("Material","material","Recycled plastic","3915.10","Plastic waste/scrap","Reprocessed polymer feedstock."),
    "pl_e_elec":    ("Energy","energy","Electricity",None,None,"Moulding and extrusion power."),
    "pl_l_labour":  ("LaborCost","labor","Labour",None,None,"Machine operation and finishing labour."),
    "pl_k_inj":     ("MachineryCost","machinery","Injection moulding","8477.10","Injection-moulding machines","Moulds rigid containers and parts."),
    "pl_k_ext":     ("MachineryCost","machinery","Extruder","8477.20","Extruders","Extrudes film, sheet, pipe and profile."),
    "pl_k_blow":    ("MachineryCost","machinery","Blow moulding","8477.30","Blow-moulding machines","Blows bottles, jerrycans and drums."),
    "pl_k_print":   ("MachineryCost","machinery","Printing & lamination","8443.16","Flexographic printing","Prints and laminates packaging."),
    # Intermediates
    "pl_c_film":    ("Component","component","Plastic film & sheet","3920.10","Plastic plates/sheet","Extruded film for bags and laminates."),
    "pl_c_preform": ("Component","component","PET preform","3923.30","Carboys, bottles (preform)","Injection preform for bottle blowing."),
  },
  "products": {
    "pl_p_bottles": ("PET bottles & containers","3923.30","Carboys, bottles, flasks","Beverage and liquid packaging."),
    "pl_p_jerry":   ("Jerrycans & drums","3923.90","Articles for conveyance/packing","Bulk liquid and chemical containers."),
    "pl_p_bags":    ("Plastic bags & sacks","3923.21","Sacks/bags of polyethylene","Carrier and packaging bags."),
    "pl_p_film":    ("Packaging film & wrap","3920.10","Plastic film","Shrink, stretch and lamination film."),
    "pl_p_rigid":   ("Rigid containers & tubs","3923.10","Boxes, cases, crates","Food and industrial tubs."),
    "pl_p_caps":    ("Caps & closures","3923.50","Stoppers, lids, caps","Bottle and container closures."),
    "pl_p_pipes":   ("Plastic pipes & fittings","3917.23","Tubes/pipes of PVC","Water, drainage and conduit pipe."),
    "pl_p_house":   ("Household plasticware","3924.10","Tableware/kitchenware","Buckets, basins and utensils."),
    "pl_p_crates":  ("Crates & pallets","3923.10","Boxes, cases, crates","Returnable transport packaging."),
    "pl_p_woven":   ("Woven PP sacks","6305.33","Sacks/bags of PP strip","Grain, sugar and cement sacks."),
    "pl_p_foam":    ("EPS foam packaging","3921.11","Cellular polystyrene","Protective and insulation packaging."),
    "pl_p_corrug":  ("Corrugated boxes & cartons","4819.10","Cartons of corrugated paper","Shipping and retail boxes."),
    "pl_p_flexible":("Flexible laminates & pouches","3921.90","Plastic laminates","Food and sachet pouches."),
    "pl_p_labels":  ("Labels & printed packaging","4821.10","Printed paper labels","Product labelling and wraps."),
    "pl_p_furniture":("Plastic furniture","9403.70","Furniture of plastics","Chairs, tables and storage."),
  },
  "edges": {
    "pl_p_bottles": [("pl_c_preform",.62),("pl_k_blow",.16),("pl_e_elec",.10),("pl_l_labour",.12)],
    "pl_p_jerry":   [("pl_m_pe",.62),("pl_k_blow",.16),("pl_e_elec",.10),("pl_l_labour",.12)],
    "pl_p_bags":    [("pl_c_film",.66),("pl_m_add",.08),("pl_e_elec",.10),("pl_l_labour",.16)],
    "pl_p_film":    [("pl_c_film",.84),("pl_m_add",.06),("pl_l_labour",.10)],
    "pl_p_rigid":   [("pl_m_pp",.58),("pl_k_inj",.16),("pl_e_elec",.12),("pl_l_labour",.14)],
    "pl_p_caps":    [("pl_m_pp",.56),("pl_k_inj",.18),("pl_e_elec",.12),("pl_l_labour",.14)],
    "pl_p_pipes":   [("pl_m_pvc",.58),("pl_k_ext",.16),("pl_e_elec",.12),("pl_l_labour",.14)],
    "pl_p_house":   [("pl_m_pp",.54),("pl_m_recyc",.10),("pl_k_inj",.14),("pl_e_elec",.10),("pl_l_labour",.12)],
    "pl_p_crates":  [("pl_m_pp",.60),("pl_k_inj",.16),("pl_e_elec",.10),("pl_l_labour",.14)],
    "pl_p_woven":   [("pl_m_pp",.56),("pl_k_ext",.16),("pl_k_print",.06),("pl_e_elec",.08),("pl_l_labour",.14)],
    "pl_p_foam":    [("pl_m_ps",.62),("pl_k_ext",.14),("pl_e_elec",.12),("pl_l_labour",.12)],
    "pl_p_corrug":  [("pl_m_paper",.62),("pl_k_print",.14),("pl_e_elec",.08),("pl_l_labour",.16)],
    "pl_p_flexible":[("pl_c_film",.50),("pl_m_foil",.18),("pl_k_print",.16),("pl_l_labour",.16)],
    "pl_p_labels":  [("pl_m_paper",.52),("pl_k_print",.22),("pl_m_add",.08),("pl_l_labour",.18)],
    "pl_p_furniture":[("pl_m_pp",.58),("pl_k_inj",.16),("pl_e_elec",.12),("pl_l_labour",.14)],
    # Intermediates
    "pl_c_film":    [("pl_m_pe",.54),("pl_m_pp",.18),("pl_m_recyc",.10),("pl_k_ext",.08),("pl_e_elec",.06),("pl_l_labour",.04)],
    "pl_c_preform": [("pl_m_pet",.74),("pl_k_inj",.12),("pl_e_elec",.08),("pl_l_labour",.06)],
  },
})

# ════════════════════════════════════════════════════════════════════════════
# 8. CEMENT & BUILDING MATERIALS
# ════════════════════════════════════════════════════════════════════════════
CHAINS.append({
  "vc": "Cement & Building Materials",
  "nodes": {
    "cm_m_lime":    ("Material","material","Limestone","2521.00","Limestone flux","Primary calcium source for clinker."),
    "cm_m_clay":    ("Material","material","Clay / shale","2508.40","Other clays","Silica-alumina source for clinker."),
    "cm_m_gypsum":  ("Material","material","Gypsum","2520.10","Gypsum; anhydrite","Set retarder and plasterboard base."),
    "cm_m_sand":    ("Material","material","Sand & aggregates","2505.10","Silica sands","Concrete and mortar filler; glass feed."),
    "cm_m_pozz":    ("Material","material","Pozzolana / fly ash","2621.90","Slag, ash and residues","Supplementary cementitious material."),
    "cm_m_steel":   ("Material","material","Reinforcing steel","7214.20","Bars/rods, deformed","Reinforcement for concrete products."),
    "cm_m_fuel":    ("Material","material","Coal / kiln fuel","2701.12","Coal","Thermal energy for the kiln."),
    "cm_e_elec":    ("Energy","energy","Electricity",None,None,"Grinding, crushing and plant power."),
    "cm_e_heat":    ("Energy","energy","Kiln thermal energy",None,None,"Clinkerisation and curing heat."),
    "cm_l_labour":  ("LaborCost","labor","Labour",None,None,"Quarry, kiln and finishing labour."),
    "cm_k_kiln":    ("MachineryCost","machinery","Rotary kiln","8417.80","Industrial furnaces (non-electric)","Burns raw meal to clinker at 1450C."),
    "cm_k_mill":    ("MachineryCost","machinery","Grinding mill","8474.20","Crushing/grinding machines","Grinds raw meal and finished cement."),
    "cm_k_crush":   ("MachineryCost","machinery","Crusher","8474.10","Sorting/crushing machines","Crushes quarried limestone and clay."),
    "cm_k_mix":     ("MachineryCost","machinery","Batching & moulding plant","8474.31","Concrete/mortar mixers","Mixes and forms concrete products."),
    # Intermediates
    "cm_c_meal":    ("Component","component","Raw meal","2523.10","Cement raw mix","Ground limestone-clay kiln feed."),
    "cm_c_clinker": ("Component","component","Cement clinker","2523.10","Cement clinker","Nodular intermediate from the kiln."),
    "cm_c_cement":  ("Component","component","Portland cement (ground)","2523.29","Portland cement","Ground clinker + gypsum binder."),
    "cm_c_agg":     ("Component","component","Crushed aggregate","2517.10","Pebbles, gravel, crushed stone","Graded stone for concrete."),
  },
  "products": {
    "cm_p_opc":     ("Ordinary Portland cement (OPC)","2523.29","Portland cement","General-purpose construction cement."),
    "cm_p_ppc":     ("Pozzolana / blended cement (PPC)","2523.90","Other hydraulic cements","Lower-carbon blended cement."),
    "cm_p_clinker": ("Cement clinker","2523.10","Cement clinker","Traded intermediate for grinding plants."),
    "cm_p_white":   ("White cement","2523.21","White Portland cement","Architectural and decorative cement."),
    "cm_p_rmc":     ("Ready-mix concrete","3824.50","Non-refractory mortars/concretes","Site-delivered fresh concrete."),
    "cm_p_blocks":  ("Concrete blocks & bricks","6810.11","Building blocks and bricks","Masonry units for walling."),
    "cm_p_pavers":  ("Paving blocks & kerbs","6810.19","Tiles, flagstones, paving","Interlocking pavers and kerbstones."),
    "cm_p_pipes":   ("Concrete pipes & culverts","6810.99","Articles of cement/concrete","Drainage and sewerage pipe."),
    "cm_p_precast": ("Precast & prestressed elements","6810.91","Prefabricated structural components","Beams, slabs and panels."),
    "cm_p_rooftile":("Roofing tiles","6810.19","Tiles, flagstones","Concrete roofing tiles."),
    "cm_p_fibre":   ("Fibre-cement sheets","6811.40","Articles of asbestos-cement etc.","Roofing and cladding sheets."),
    "cm_p_lime":    ("Building lime","2522.20","Slaked lime","Mortar, plaster and stabilisation."),
    "cm_p_gypboard":("Gypsum plasterboard","6809.11","Boards/sheets of plaster","Drywall and ceiling boards."),
    "cm_p_mortar":  ("Dry mortar & plaster","3824.50","Mortars and concretes","Bagged tile adhesive and plaster."),
    "cm_p_tiles":   ("Ceramic tiles","6907.21","Ceramic flags and tiles","Floor and wall tiles."),
    "cm_p_bricks":  ("Clay bricks","6904.10","Building bricks","Fired clay masonry units."),
    "cm_p_glass":   ("Flat glass","7005.29","Float glass, non-wired","Window and facade glazing."),
  },
  "edges": {
    "cm_p_opc":     [("cm_c_cement",.92),("cm_e_elec",.04),("cm_l_labour",.04)],
    "cm_p_ppc":     [("cm_c_clinker",.52),("cm_m_pozz",.26),("cm_m_gypsum",.06),("cm_k_mill",.06),("cm_e_elec",.06),("cm_l_labour",.04)],
    "cm_p_clinker": [("cm_c_clinker",.92),("cm_l_labour",.08)],
    "cm_p_white":   [("cm_c_clinker",.64),("cm_m_gypsum",.08),("cm_e_heat",.14),("cm_k_mill",.06),("cm_l_labour",.08)],
    "cm_p_rmc":     [("cm_c_cement",.40),("cm_c_agg",.34),("cm_k_mix",.10),("cm_e_elec",.06),("cm_l_labour",.10)],
    "cm_p_blocks":  [("cm_c_cement",.42),("cm_c_agg",.34),("cm_k_mix",.10),("cm_e_elec",.04),("cm_l_labour",.10)],
    "cm_p_pavers":  [("cm_c_cement",.44),("cm_c_agg",.32),("cm_k_mix",.10),("cm_e_elec",.04),("cm_l_labour",.10)],
    "cm_p_pipes":   [("cm_c_cement",.40),("cm_c_agg",.28),("cm_m_steel",.16),("cm_k_mix",.08),("cm_l_labour",.08)],
    "cm_p_precast": [("cm_c_cement",.36),("cm_c_agg",.26),("cm_m_steel",.22),("cm_k_mix",.08),("cm_l_labour",.08)],
    "cm_p_rooftile":[("cm_c_cement",.44),("cm_m_sand",.30),("cm_k_mix",.10),("cm_e_elec",.06),("cm_l_labour",.10)],
    "cm_p_fibre":   [("cm_c_cement",.50),("cm_m_pozz",.18),("cm_k_mix",.10),("cm_e_elec",.08),("cm_l_labour",.14)],
    "cm_p_lime":    [("cm_m_lime",.56),("cm_k_kiln",.12),("cm_e_heat",.18),("cm_l_labour",.14)],
    "cm_p_gypboard":[("cm_m_gypsum",.58),("cm_k_kiln",.08),("cm_e_heat",.16),("cm_l_labour",.18)],
    "cm_p_mortar":  [("cm_c_cement",.46),("cm_m_sand",.34),("cm_k_mix",.08),("cm_l_labour",.12)],
    "cm_p_tiles":   [("cm_m_clay",.40),("cm_k_kiln",.16),("cm_e_heat",.22),("cm_e_elec",.08),("cm_l_labour",.14)],
    "cm_p_bricks":  [("cm_m_clay",.50),("cm_k_kiln",.12),("cm_e_heat",.22),("cm_l_labour",.16)],
    "cm_p_glass":   [("cm_m_sand",.42),("cm_k_kiln",.12),("cm_e_heat",.28),("cm_e_elec",.08),("cm_l_labour",.10)],
    # Intermediates
    "cm_c_meal":    [("cm_m_lime",.54),("cm_m_clay",.20),("cm_k_crush",.10),("cm_k_mill",.08),("cm_l_labour",.08)],
    "cm_c_clinker": [("cm_c_meal",.46),("cm_m_fuel",.20),("cm_e_heat",.18),("cm_k_kiln",.10),("cm_l_labour",.06)],
    "cm_c_cement":  [("cm_c_clinker",.74),("cm_m_gypsum",.08),("cm_k_mill",.08),("cm_e_elec",.06),("cm_l_labour",.04)],
    "cm_c_agg":     [("cm_m_sand",.62),("cm_k_crush",.20),("cm_e_elec",.08),("cm_l_labour",.10)],
  },
})


def run():
    db.init_db()
    conn = db.connect()
    n_nodes = n_products = n_edges = 0
    for chain in CHAINS:
        vc = chain["vc"]
        for nid, (label, ctype, name, hs, hsd, fn) in chain["nodes"].items():
            s, sn = STRENGTH.get(nid, (None, None))
            db.upsert_node(conn, id=nid, value_chain_id=vc, label=label, name=name,
                           component_type=ctype, function=fn,
                           hs_code=[hs] if hs else None,
                           hs_code_description=[hsd] if hsd else None,
                           source_references=SRC,
                           strength=s, strength_note=sn)
            n_nodes += 1
        for pid, (name, hs, hsd, fn) in chain["products"].items():
            s, sn = STRENGTH.get(pid, (None, None))
            db.upsert_node(conn, id=pid, value_chain_id=vc, label="System", name=name,
                           component_type="other", function=fn,
                           hs_code=[hs] if hs else None,
                           hs_code_description=[hsd] if hsd else None,
                           source_references=SRC,
                           strength=s, strength_note=sn)
            n_products += 1
        for downstream, inputs in chain["edges"].items():
            for upstream, weight in inputs:
                db.upsert_rel(conn, f"e:{upstream}->{downstream}", upstream, downstream, weight)
                n_edges += 1
    conn.commit()
    conn.close()
    return n_nodes, n_products, n_edges


if __name__ == "__main__":
    nodes, products, edges = run()
    print(f"Seeded {len(CHAINS)} value chains: {nodes} shared nodes, "
          f"{products} product roots, {edges} relationships.")
