"""
Per-product Iron & Steel decomposition graph.

Each finished steel product is its own value-chain ROOT (a System node). From a
product, the app walks upstream through its semi-finished form -> crude steel ->
iron-making -> raw materials, so every product gets its own clean Sankey showing
how it is made, all the way back to ores, coke, fluxes and scrap.

Upstream nodes (crude steel, pig iron, slab, billet, iron ore, …) are SHARED:
they are inserted once and reused by every product that draws on them, so the
graph is a directed acyclic "made-from" network rather than 11 separate trees.

Edge convention matches the app: start_node = upstream input, end_node = the
downstream product; weight = that input's cost share of the parent (0..1).

The product set, HS codes and CO2 figures come from the structured dataset in
iron_steel_value_chain.json; the inter-stage process links are standard primary
steelmaking routes (BF-BOF and scrap/DRI-EAF), to be refined with NPA/UDC data.
"""
import db

# Value-chain group this product set belongs to (shown in the "Value chain"
# dropdown). Other report chains (Copper, Automotives, …) seed their own VC.
VC = "Iron & Steel"
SRC = ["valuechains.ai-style structured dataset; standard primary-steel process"]


# ── Shared upstream nodes (materials, intermediates, energy, labour, plant) ───
# id: (label, component_type, name, hs_code, hs_desc, function)
NODES = {
    # Raw materials (chain endpoints)
    "m_ore_fines":  ("Material", "material", "Iron ore fines", "2601.11", "Iron ores and concentrates", "Sintered before furnace use; >60% Fe."),
    "m_ore_pellets":("Material", "material", "Iron ore pellets", "2601.12", "Iron ore agglomerated", "High-Fe feed for DRI and blast furnace."),
    "m_coke":       ("Material", "material", "Metallurgical coke", "2704.00", "Coke and semi-coke", "Reductant and structural support in the blast furnace."),
    "m_limestone":  ("Material", "material", "Limestone (flux)", "2521.00", "Limestone flux", "Flux that removes impurities as slag."),
    "m_ferroalloys":("Material", "material", "Ferroalloys (Mn, Si)", "7202.11", "Ferro-alloys", "Alloying elements that set steel grade."),
    "m_scrap_hms":  ("Material", "material", "Heavy melting scrap (HMS)", "7204.10", "Ferrous waste and scrap", "Primary furnace charge; recycled steel."),
    "m_scrap_shred":("Material", "material", "Shredded scrap", "7204.41", "Ferrous waste and scrap", "Consistent-chemistry recycled steel."),
    "m_zinc":       ("Material", "material", "Zinc", "7901", "Unwrought zinc", "Corrosion-protection coating metal."),
    "m_nickel":     ("Material", "material", "Nickel", "7502", "Unwrought nickel", "Austenite stabiliser for stainless grades."),
    "m_chromium":   ("Material", "material", "Ferrochrome (Cr)", "7202.41", "Ferro-chromium", "Corrosion resistance for stainless grades."),
    "m_nbvti":      ("Material", "material", "Nb / V / Ti micro-alloys", "7202", "Ferro-alloys", "Micro-alloying for high-strength low-alloy steel."),
    "m_electrodes": ("Material", "material", "Graphite electrodes", "8545.11", "Carbon/graphite electrodes", "Carry the arc current in the electric arc furnace."),
    "m_natgas":     ("Energy",   "energy",   "Natural gas / H2", None, None, "Reductant and energy for direct reduction."),
    "m_tin":        ("Material", "material", "Tin", "8001", "Unwrought tin", "Electrolytic coating metal for tinplate."),
    "m_paint":      ("Material", "material", "Coating / paint system", "3208", "Paints and varnishes", "Organic colour-coat for pre-painted steel."),
    "m_aluminium":  ("Material", "material", "Aluminium", "7601", "Unwrought aluminium", "Coating metal for Al-Zn and aluminised steel."),

    # Energy, labour, plant (shared, reused everywhere)
    "e_electricity":("Energy",   "energy",   "Electricity", None, None, "Power for melting, casting and finishing."),
    "e_heat":       ("Energy",   "energy",   "Process / rolling heat", None, None, "Reheating and rolling furnace energy."),
    "l_labour":     ("LaborCost","labor",    "Labour", None, None, "Skilled and semi-skilled operating labour."),
    "k_furnace":    ("MachineryCost","machinery","Furnace & casting plant", "8454", "Converters, ladles, casting machines", "Melting and continuous-casting equipment."),
    "k_mill":       ("MachineryCost","machinery","Rolling / forming mill", "8455", "Metal-rolling mills", "Hot/cold rolling and forming equipment."),
    "k_press":      ("MachineryCost","machinery","Forging press / hammer", "8462", "Forging/stamping machine tools", "Shapes heated billets/blooms by compressive force."),

    # Iron-making intermediates
    "c_sinter":     ("Component","component", "Sinter", None, None, "Agglomerated ore burden for the blast furnace."),
    "c_pig":        ("Component","component", "Pig iron (hot metal)", "7201.10", "Pig iron and spiegeleisen", "Liquid blast-furnace iron; main BOF input."),
    "c_dri":        ("Component","component", "Direct reduced iron (DRI/HBI)", "7203.10", "Ferrous products, direct reduction", "Gas-reduced sponge iron; EAF feed."),

    # Steel-making + casting intermediates
    "c_crude":      ("Component","component", "Crude / liquid steel", "7206", "Iron and non-alloy steel, primary forms", "Refined liquid steel from BOF or EAF."),
    "c_slab":       ("Component","component", "Steel slab", "7207", "Semi-finished iron/steel", "Cast flat semi-finished steel."),
    "c_bloom":      ("Component","component", "Steel bloom", "7207", "Semi-finished iron/steel", "Cast heavy-section semi-finished steel."),
    "c_billet":     ("Component","component", "Steel billet", "7207", "Semi-finished iron/steel", "Cast square-section semi-finished steel."),
    "c_hrc":        ("Component","component", "Hot rolled coil (HRC)", "7208.37", "Flat-rolled, hot-rolled", "Hot-rolled flat semi-product."),
    "c_crc":        ("Component","component", "Cold rolled coil (CRC)", "7209.16", "Flat-rolled, cold-rolled", "Cold-rolled flat for surface-critical use."),
    "c_wire":       ("Component","component", "Drawn steel wire", "7217", "Wire of iron or non-alloy steel", "Cold-drawn wire feed for fasteners, rope, mesh and nails."),

    # Production technologies (TechnologyType) — the methods that transform
    # inputs into the intermediate above them. Shared across all products.
    "t_bf":     ("TechnologyType", None, "Blast furnace (BF)", "8454.10", "Blast furnace plant", "Smelts the ore burden into liquid pig iron with coke."),
    "t_shaft":  ("TechnologyType", None, "DRI shaft furnace (MIDREX/HYL)", "8454.90", "Direct-reduction shaft furnace", "Reduces ore pellets to sponge iron using gas or H2."),
    "t_bof":    ("TechnologyType", None, "Basic oxygen furnace (BOF)", "8454.20", "Basic oxygen converter", "Refines hot metal plus scrap into crude steel."),
    "t_eaf":    ("TechnologyType", None, "Electric arc furnace (EAF)", "8514.10", "Electric arc furnace", "Melts scrap and DRI into crude steel."),
    "t_caster": ("TechnologyType", None, "Continuous casting", "8454.30", "Continuous casting machine", "Casts liquid steel into slabs, blooms and billets."),
}

# Finished products = roots (label System). id: (name, hs, hs_desc, function)
PRODUCTS = {
    "p_rebar":     ("Reinforcing bar (rebar)", "7214.20", "Bars and rods, iron/non-alloy steel", "Concrete reinforcement; the largest long product."),
    "p_wirerod":   ("Wire rod & drawn wire", "7213.10", "Bars and rods in coils", "Feed for wire, mesh, fasteners and rope."),
    "p_sections":  ("Structural sections (I, H beams)", "7216.33", "Angles, shapes and sections", "Columns and beams for steel-frame buildings."),
    "p_rails":     ("Rails", "7302.10", "Railway track construction material", "Head-hardened track for rail networks."),
    "p_plate":     ("Hot rolled plate", "7208.51", "Flat-rolled, hot-rolled, heavy plate", "Heavy plate for ships, vessels and bridges."),
    "p_galv":      ("Galvanised sheet (GI/GA)", "7210.49", "Flat-rolled, clad/plated/coated", "Corrosion-resistant sheet; construction & auto."),
    "p_electrical":("Electrical steel (GOES/NOES)", "7225.11", "Flat-rolled silicon-electrical steel", "Transformer cores and motor laminations."),
    "p_erw":       ("Electric resistance welded (ERW) pipe", "7306.30", "Other tubes and pipes, welded", "Line pipe and structural hollow sections."),
    "p_seamless":  ("Seamless oil country tubular goods (OCTG)", "7304.29", "Tubes, pipes, seamless", "Oil-country tubular goods for drilling."),
    "p_stainless": ("Stainless steel (304 / 316)", "7219.12", "Flat-rolled stainless steel", "Corrosion-resistant; food, chemical, medical."),
    "p_hsla":      ("High-strength low-alloy (HSLA)", "7225.50", "Flat-rolled other alloy steel", "Lightweight structural steel; auto & bridges."),
    "p_crc":       ("Cold rolled coil/sheet (CRC)", "7209.17", "Flat-rolled, cold-rolled", "Surface-critical flat steel for auto and appliances."),
    "p_tinplate":  ("Tinplate (ETP)", "7210.12", "Flat-rolled, tin-coated", "Tin-coated sheet for food and beverage cans."),
    "p_prepaint":  ("Pre-painted / colour-coated (PPGI)", "7210.70", "Flat-rolled, painted/coated", "Colour-coated sheet for roofing and cladding."),
    "p_mesh":      ("Welded wire mesh / fabric", "7314.20", "Grill, netting and fencing, welded", "Reinforcing mesh and fencing from drawn wire."),
    "p_forgings":  ("Forged steel components", "7326.19", "Articles of iron/steel, forged", "Shafts, flanges and fittings shaped by forging."),
    "p_castings":  ("Steel / iron castings", "7325.99", "Cast articles of iron/steel", "Cast parts for machinery, valves and fittings."),
    "p_grinding":  ("Grinding media (balls)", "7325.91", "Grinding balls, cast/forged", "Wear-resistant media for mining and cement mills."),

    # ── Full HS 72-73 taxonomy: additional finished products ──────────────────
    # Long products
    "p_merchant":  ("Merchant bar (rounds, squares, flats)", "7214.99", "Other bars and rods, iron/non-alloy steel, not further worked", "General-purpose hot-rolled bars for fabrication."),
    "p_lightsec":  ("Light sections (angles & channels)", "7216.10", "U, I or H sections, height < 80 mm", "Small structural shapes for light fabrication."),
    "p_sbq":       ("Cold-drawn / bright bar (SBQ)", "7215.50", "Other bars and rods, cold-formed/cold-finished", "Precision engineering steel bar for machining."),
    "p_piling":    ("Sheet piling", "7301.10", "Sheet piling of iron or steel", "Interlocking sections for retaining walls and foundations."),
    "p_railfit":   ("Railway track fittings (fishplates, sole plates)", "7302.40", "Fish-plates and sole plates", "Jointing and fastening components for rail track."),
    # Flat products
    "p_hrc":       ("Hot rolled coil/sheet (HRC)", "7208.39", "Flat-rolled, hot-rolled, in coils", "General flat steel feedstock and finished sheet."),
    "p_alzinc":    ("Aluminium-zinc coated sheet (Galvalume)", "7210.61", "Flat-rolled, plated/coated with Al-Zn alloys", "Durable coated sheet for roofing and appliances."),
    "p_alusteel":  ("Aluminised steel sheet", "7210.69", "Flat-rolled, otherwise plated/coated with aluminium", "Heat-resistant coated sheet for exhausts and ovens."),
    "p_egalv":     ("Electro-galvanised sheet", "7210.30", "Flat-rolled, electrolytically zinc-coated", "Thin even zinc coating for automotive body panels."),
    "p_eccs":      ("Tin-free steel / ECCS", "7210.50", "Flat-rolled, coated with chromium/chromium oxides", "Chromium-coated packaging steel for lacquered cans."),
    # Tubular products
    "p_saw":       ("SAW line pipe (LSAW/HSAW)", "7305.11", "Line pipe, longitudinally submerged-arc welded", "Large-diameter oil & gas transmission pipe."),
    "p_hss":       ("Hollow structural sections (HSS)", "7306.61", "Welded tubes, square/rectangular section", "Structural hollow sections for steel frames."),
    "p_precision": ("Cold-drawn seamless precision tube", "7304.31", "Tubes, seamless, cold-drawn/cold-rolled", "Tight-tolerance tube for hydraulics and machinery."),
    # Stainless & special steels
    "p_ss_long":   ("Stainless steel bar & wire rod", "7222.11", "Bars and rods of stainless steel, hot-rolled", "Corrosion-resistant long products for shafts and fasteners."),
    "p_ss_tube":   ("Stainless steel tube/pipe", "7306.40", "Welded tubes of stainless steel", "Hygienic, corrosion-resistant piping."),
    "p_tool":      ("Tool steel", "7228.30", "Other bars/rods of alloy steel, hot-rolled", "High-hardness steel for dies, cutters and moulds."),
    "p_spring":    ("Spring steel", "7226.91", "Flat-rolled other alloy steel, hot-rolled", "High-fatigue steel for springs and blades."),
    "p_bearing":   ("Bearing steel", "7228.50", "Other bars/rods of alloy steel, cold-finished", "Clean high-carbon-chromium steel for bearings."),
    # Wire & fabricated products
    "p_wire":      ("Steel wire (drawn & galvanised)", "7217.20", "Wire of iron/non-alloy steel, zinc-coated", "Drawn wire for ropes, mesh, springs and fencing."),
    "p_nails":     ("Nails, tacks & staples", "7317.00", "Nails, tacks, staples of iron or steel", "Fastening hardware drawn and headed from wire."),
    "p_fasteners": ("Bolts, nuts & fasteners", "7318.15", "Threaded screws and bolts", "Threaded fasteners cold-forged from wire/bar."),
    "p_rope":      ("Wire rope & cable", "7312.10", "Stranded wire, ropes and cables", "Load-bearing rope for cranes, lifts and rigging."),
    "p_fencing":   ("Fencing & chain-link", "7314.31", "Grill, netting and fencing, zinc-coated", "Galvanised fencing and chain-link mesh."),
    # Cast iron branch
    "p_diron":     ("Ductile / grey iron pipe & fittings", "7303.00", "Tubes, pipes and hollow profiles of cast iron", "Cast-iron pressure pipe for water and sewerage."),
}

# Edges: downstream -> list of (upstream_input, weight)  [weight = cost share]
EDGES = {
    # Finished products
    "p_rebar":     [("c_billet", .72), ("e_heat", .12), ("k_mill", .08), ("l_labour", .08)],
    "p_wirerod":   [("c_billet", .70), ("k_mill", .12), ("e_heat", .10), ("l_labour", .08)],
    "p_sections":  [("c_bloom", .72), ("k_mill", .10), ("e_heat", .10), ("l_labour", .08)],
    "p_rails":     [("c_bloom", .74), ("e_heat", .12), ("l_labour", .08), ("k_mill", .06)],
    "p_plate":     [("c_slab", .76), ("e_heat", .12), ("l_labour", .06), ("k_mill", .06)],
    "p_galv":      [("c_crc", .68), ("m_zinc", .16), ("e_heat", .08), ("l_labour", .08)],
    "p_electrical":[("c_crc", .68), ("m_ferroalloys", .12), ("e_heat", .12), ("l_labour", .08)],
    "p_erw":       [("c_hrc", .76), ("e_electricity", .10), ("k_mill", .08), ("l_labour", .06)],
    "p_seamless":  [("c_billet", .72), ("e_heat", .12), ("k_mill", .10), ("l_labour", .06)],
    "p_stainless": [("c_crude", .50), ("m_nickel", .14), ("m_chromium", .14), ("m_scrap_hms", .10), ("e_electricity", .07), ("l_labour", .05)],
    "p_hsla":      [("c_slab", .76), ("m_nbvti", .08), ("e_heat", .10), ("l_labour", .06)],
    "p_crc":       [("c_crc", .86), ("e_electricity", .06), ("k_mill", .04), ("l_labour", .04)],
    "p_tinplate":  [("c_crc", .70), ("m_tin", .16), ("e_electricity", .06), ("k_mill", .04), ("l_labour", .04)],
    "p_prepaint":  [("c_crc", .64), ("m_zinc", .14), ("m_paint", .12), ("e_heat", .05), ("l_labour", .05)],
    "p_mesh":      [("c_wire", .60), ("m_zinc", .16), ("k_mill", .12), ("e_heat", .06), ("l_labour", .06)],
    "p_forgings":  [("c_bloom", .68), ("e_heat", .14), ("k_press", .10), ("l_labour", .08)],
    "p_castings":  [("c_crude", .60), ("k_furnace", .14), ("e_electricity", .12), ("m_ferroalloys", .06), ("l_labour", .08)],
    "p_grinding":  [("c_billet", .70), ("e_heat", .14), ("k_mill", .08), ("l_labour", .08)],

    # Full HS 72-73 taxonomy — long products
    "p_merchant":  [("c_billet", .74), ("e_heat", .12), ("k_mill", .08), ("l_labour", .06)],
    "p_lightsec":  [("c_billet", .72), ("e_heat", .12), ("k_mill", .09), ("l_labour", .07)],
    "p_sbq":       [("c_billet", .70), ("k_mill", .14), ("e_heat", .08), ("l_labour", .08)],
    "p_piling":    [("c_bloom", .74), ("e_heat", .12), ("k_mill", .08), ("l_labour", .06)],
    "p_railfit":   [("c_bloom", .70), ("e_heat", .12), ("k_mill", .10), ("l_labour", .08)],
    # Flat products
    "p_hrc":       [("c_hrc", .86), ("e_heat", .06), ("k_mill", .04), ("l_labour", .04)],
    "p_alzinc":    [("c_crc", .62), ("m_aluminium", .10), ("m_zinc", .14), ("e_heat", .08), ("l_labour", .06)],
    "p_alusteel":  [("c_crc", .66), ("m_aluminium", .16), ("e_heat", .10), ("l_labour", .08)],
    "p_egalv":     [("c_crc", .66), ("m_zinc", .14), ("e_electricity", .12), ("l_labour", .08)],
    "p_eccs":      [("c_crc", .66), ("m_chromium", .12), ("e_electricity", .14), ("l_labour", .08)],
    # Tubular products
    "p_saw":       [("c_hrc", .74), ("e_electricity", .12), ("k_mill", .08), ("l_labour", .06)],
    "p_hss":       [("c_hrc", .76), ("e_heat", .08), ("k_mill", .10), ("l_labour", .06)],
    "p_precision": [("c_billet", .70), ("k_mill", .14), ("e_heat", .08), ("l_labour", .08)],
    # Stainless & special steels
    "p_ss_long":   [("c_crude", .52), ("m_chromium", .16), ("m_nickel", .12), ("e_heat", .10), ("l_labour", .10)],
    "p_ss_tube":   [("c_crude", .48), ("m_chromium", .16), ("m_nickel", .12), ("k_mill", .12), ("e_electricity", .06), ("l_labour", .06)],
    "p_tool":      [("c_crude", .58), ("m_ferroalloys", .18), ("e_heat", .12), ("l_labour", .12)],
    "p_spring":    [("c_hrc", .70), ("m_ferroalloys", .12), ("e_heat", .10), ("l_labour", .08)],
    "p_bearing":   [("c_crude", .56), ("m_ferroalloys", .14), ("m_chromium", .12), ("e_heat", .10), ("l_labour", .08)],
    # Wire & fabricated products (drawn from the shared wire intermediate)
    "p_wire":      [("c_wire", .74), ("m_zinc", .14), ("k_mill", .06), ("l_labour", .06)],
    "p_nails":     [("c_wire", .74), ("k_mill", .14), ("l_labour", .12)],
    "p_fasteners": [("c_wire", .70), ("k_mill", .16), ("l_labour", .14)],
    "p_rope":      [("c_wire", .72), ("m_zinc", .14), ("k_mill", .08), ("l_labour", .06)],
    "p_fencing":   [("c_wire", .70), ("m_zinc", .16), ("k_mill", .08), ("l_labour", .06)],
    # Cast iron branch (made directly from blast-furnace pig iron in a foundry)
    "p_diron":     [("c_pig", .58), ("k_furnace", .14), ("m_ferroalloys", .08), ("e_heat", .12), ("l_labour", .08)],

    # Rolled flat intermediates
    "c_hrc":   [("c_slab", .74), ("e_heat", .14), ("k_mill", .07), ("l_labour", .05)],
    "c_crc":   [("c_hrc", .78), ("e_heat", .08), ("e_electricity", .08), ("l_labour", .06)],

    # Drawn wire intermediate (wire rod -> cold-drawn wire) feeding fabricated products
    "c_wire":  [("c_billet", .78), ("k_mill", .10), ("e_heat", .06), ("l_labour", .06)],

    # Semi-finished shapes are produced by the continuous-casting technology
    "c_slab":   [("t_caster", 1.0)],
    "c_bloom":  [("t_caster", 1.0)],
    "c_billet": [("t_caster", 1.0)],
    "t_caster": [("c_crude", .86), ("e_electricity", .06), ("k_furnace", .05), ("l_labour", .03)],

    # Crude steel via two steelmaking technologies: BOF (hot metal) and EAF (scrap/DRI)
    "c_crude": [("t_bof", .55), ("t_eaf", .38), ("m_ferroalloys", .05), ("l_labour", .02)],
    "t_bof":   [("c_pig", .62), ("m_scrap_hms", .22), ("e_electricity", .06), ("k_furnace", .06), ("l_labour", .04)],
    "t_eaf":   [("m_scrap_hms", .38), ("m_scrap_shred", .25), ("c_dri", .18), ("e_electricity", .10),
                ("m_electrodes", .03), ("k_furnace", .03), ("l_labour", .03)],

    # Iron via blast furnace; sponge iron via DRI shaft furnace
    "c_pig":   [("t_bf", 1.0)],
    "t_bf":    [("c_sinter", .50), ("m_coke", .28), ("m_limestone", .10), ("e_heat", .08), ("l_labour", .04)],
    "c_dri":   [("t_shaft", 1.0)],
    "t_shaft": [("m_ore_pellets", .55), ("m_natgas", .30), ("e_electricity", .10), ("l_labour", .05)],
    "c_sinter":[("m_ore_fines", .72), ("m_coke", .12), ("m_limestone", .10), ("e_heat", .06)],
}


def run():
    db.init_db()
    conn = db.connect()

    # Shared upstream nodes
    for nid, (label, ctype, name, hs, hsd, fn) in NODES.items():
        db.upsert_node(conn, id=nid, value_chain_id=VC, label=label, name=name,
                       component_type=ctype, function=fn,
                       hs_code=[hs] if hs else None,
                       hs_code_description=[hsd] if hsd else None,
                       source_references=SRC)

    # Finished-product roots
    for pid, (name, hs, hsd, fn) in PRODUCTS.items():
        db.upsert_node(conn, id=pid, value_chain_id=VC, label="System", name=name,
                       component_type="other", function=fn,
                       hs_code=[hs] if hs else None,
                       hs_code_description=[hsd] if hsd else None,
                       source_references=SRC)

    # Edges (start = upstream input, end = downstream product)
    n = 0
    for downstream, inputs in EDGES.items():
        for upstream, weight in inputs:
            db.upsert_rel(conn, f"e:{upstream}->{downstream}", upstream, downstream, weight)
            n += 1

    conn.commit()
    conn.close()
    return len(NODES) + len(PRODUCTS), n


if __name__ == "__main__":
    nodes, rels = run()
    print(f"Seeded per-product decomposition: {nodes} nodes, {rels} relationships, "
          f"{len(PRODUCTS)} product roots.")
