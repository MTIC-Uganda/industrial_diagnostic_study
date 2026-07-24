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

# Strength data from Jerome's sources-of-truth.html (Value Chain Maps tab).
# Phase I Mining→gap, II Ironmaking→emerging, III Steelmaking→emerging,
# IV Casting→emerging, V Rolling/Finishing→strong, VI Market→strong.
# Flat steel (slab/HRC/CRC) is absent → gap.  Long products competitive → strong.
IS_STRENGTH = {
    # Raw materials
    "m_ore_fines":   ("emerging", "Iron ore mining limited — 1 commercial miner (SINO Minerals, ~300k tpa); fines exported as-is, no sintering or pelletising capacity"),
    "m_ore_pellets": ("gap",      "Ore pelletising absent — fines not commercially pelletised in Uganda"),
    "m_coke":        ("gap",      "Metallurgical coke absent — no coking coal in Uganda; all imported"),
    "m_limestone":   ("strong",   "Limestone abundant — same deposits supplying the cement sector"),
    "m_ferroalloys": ("gap",      "Ferroalloys all imported from South Africa and China"),
    "m_scrap_hms":   ("emerging", "HMS scrap collection growing; informal market; infrastructure limited"),
    "m_scrap_shred": ("emerging", "Shredded scrap available from local collection; limited scale"),
    "m_zinc":        ("gap",      "No domestic zinc production; all imported"),
    "m_nickel":      ("gap",      "Nickel absent — all imported"),
    "m_chromium":    ("gap",      "Ferrochrome absent — all imported"),
    "m_nbvti":       ("gap",      "Micro-alloys absent — all imported"),
    "m_electrodes":  ("gap",      "Graphite electrodes absent — all imported"),
    "m_natgas":      ("emerging", "Natural gas from Albertine basin; pre-commercial production"),
    "m_tin":         ("gap",      "Tin absent — all imported"),
    "m_paint":       ("emerging", "Some coating/paint systems produced locally (Crown, Sadolin)"),
    "m_aluminium":   ("gap",      "Aluminium absent — all imported"),
    # Energy, labour, plant
    "e_electricity": ("emerging", "Hydro grid available; 8–10¢/kWh vs Kenya 5–7¢ — cost disadvantage"),
    "e_heat":        ("emerging", "Rolling/reheating furnaces operational at Roofings, Steel & Tube"),
    "l_labour":      ("emerging", "~2,500 direct workers; 68% of firms report technical skill shortage"),
    "k_furnace":     ("emerging", "Induction furnaces and some EAF at Tembo, Abyssinia, Roofings"),
    "k_mill":        ("strong",   "Rolling mills at Roofings Rolling Mills, Steel & Tube, Uganda Baati — operational"),
    "k_press":       ("gap",      "Forging presses absent — no forging industry in Uganda"),
    # Iron-making intermediates
    "c_sinter":      ("gap",      "Sinter plant absent — no sintering of ore fines in Uganda"),
    "c_pig":         ("gap",      "Pig iron absent — no blast furnace in Uganda"),
    "c_dri":         ("emerging", "DRI/HBI — Tembo Steels ~350k tpa (Iganga/Lugazi) + Abyssinia ~30k tpa (Jinja)"),
    # Steel-making + casting intermediates
    "c_crude":       ("emerging", "Crude steel from induction/EAF; scrap + DRI based; ~513k tpa utilised"),
    "c_slab":        ("gap",      "Steel slab absent — no flat steel casting in Uganda; USD 219.5m flat imports"),
    "c_bloom":       ("emerging", "Blooms cast at some facilities; limited scale"),
    "c_billet":      ("emerging", "Billets cast domestically at Tembo, Abyssinia and others; Phase IV emerging"),
    "c_hrc":         ("gap",      "Hot-rolled coil absent — CRITICAL GAP; USD 219.5m flat steel imports (HS 7208)"),
    "c_crc":         ("gap",      "Cold-rolled coil absent — all imported; flat steel entirely missing"),
    "c_wire":        ("strong",   "Drawn wire produced domestically; feeds rebar, mesh and wire-rod products"),
    # Technologies
    "t_bf":          ("gap",      "Blast furnace absent — no hot-metal/pig-iron production in Uganda"),
    "t_shaft":       ("emerging", "DRI shaft furnace — Tembo (MIDREX-style) and Abyssinia operational"),
    "t_bof":         ("gap",      "BOF absent — all steelmaking from EAF/induction in Uganda"),
    "t_eaf":         ("emerging", "EAF/induction — scrap + DRI; ~37 plants; Phase III emerging"),
    "t_caster":      ("emerging", "Continuous casting — billet and bloom; partial domestic capacity"),
    # Finished products (Phase V Rolling/Finishing) — aligned with Explorer product list
    "p_rebar":       ("strong",   "Rebar — Uganda's strongest product; net exporter USD 55.8m (2024); ~70% capacity used."),
    "p_wirerod":     ("strong",   "Wire rod — produced and exported regionally; strong domestic rolling capacity"),
    "p_sections":    ("strong",   "Structural sections — active at Roofings Rolling Mills and Steel & Tube"),
    "p_rails":       ("gap",      "Rails absent — no rail production in Uganda; all imported"),
    "p_plate":       ("gap",      "Hot-rolled plate absent — flat steel entirely missing in Uganda"),
    "p_galv":        ("emerging", "Galvanised sheet — Roofings Ltd and Uganda Baati active; imported coil coated locally"),
    "p_erw":         ("gap",      "Welded pipe absent — no pipe welding from domestic HRC"),
    "p_seamless":    ("gap",      "Seamless pipe absent — far upstream of current capability"),
    "p_crc":         ("gap",      "Cold-rolled coil absent — all imported"),
    "p_tinplate":    ("gap",      "Tinplate absent — no tin-coated flat steel in Uganda"),
    "p_prepaint":    ("emerging", "Pre-painted (PPGI) — Uganda Baati and Roofings active; imported coated coil processed"),
    "p_merchant":    ("strong",   "Merchant bar — domestic long-product rolling active"),
    "p_piling":      ("gap",      "Sheet piling absent — all imported"),
    "p_hrc":         ("gap",      "HRC absent — CRITICAL flat-steel gap; all imported"),
    "p_alzinc":      ("gap",      "Al-Zn coated sheet absent — all imported"),
    "p_eccs":        ("gap",      "ECCS/tin-free steel absent — all imported"),
}


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
    # Finished products — names match the Explorer (PocketBase explorer_products) exactly
    # Long products
    "p_rebar":     ("Rebar (Reinforcing Bar)", "7214.20", "Bars and rods, iron/non-alloy steel", "Concrete reinforcement; the largest long product."),
    "p_wirerod":   ("Wire Rod", "7213.10", "Bars and rods in coils", "Feed for wire drawing, mesh and rope."),
    "p_sections":  ("Structural Sections (I/H-beam, Channel, Angle)", "7216.33", "Angles, shapes and sections", "Columns and beams for steel-frame buildings."),
    "p_rails":     ("Rail", "7302.10", "Railway track construction material", "Head-hardened track for rail networks."),
    "p_merchant":  ("Merchant Bar", "7214.99", "Other bars and rods, iron/non-alloy steel, not further worked", "General-purpose hot-rolled bars for fabrication."),
    "p_piling":    ("Sheet Piling", "7301.10", "Sheet piling of iron or steel", "Interlocking sections for retaining walls and foundations."),
    # Flat products
    "p_hrc":       ("Hot-Rolled Coil / Sheet / Strip", "7208.39", "Flat-rolled, hot-rolled, in coils", "General flat steel feedstock and finished sheet."),
    "p_plate":     ("Plate", "7208.51", "Flat-rolled, hot-rolled, heavy plate", "Heavy plate for ships, vessels and bridges."),
    "p_crc":       ("Cold-Rolled Coil / Sheet", "7209.17", "Flat-rolled, cold-rolled", "Surface-critical flat steel for auto and appliances."),
    "p_galv":      ("Galvanized Sheet", "7210.49", "Flat-rolled, clad/plated/coated", "Corrosion-resistant sheet; construction & auto."),
    "p_alzinc":    ("Galvalume / Aluzinc", "7210.61", "Flat-rolled, plated/coated with Al-Zn alloys", "Durable coated sheet for roofing and appliances."),
    "p_prepaint":  ("Pre-painted / Color-Coated Coil", "7210.70", "Flat-rolled, painted/coated", "Colour-coated sheet for roofing and cladding."),
    "p_tinplate":  ("Tinplate / Tin-Free Steel (ECCS)", "7210.12", "Flat-rolled, tin-coated or chromium-coated", "Tin-coated and chromium-coated sheet for packaging."),
    "p_eccs":      ("Tin-Free Steel (ECCS)", "7210.50", "Flat-rolled, coated with chromium/chromium oxides", "Chromium-coated packaging steel for lacquered cans."),
    # Tubular products
    "p_erw":       ("Welded Pipe / Tube", "7306.30", "Other tubes and pipes, welded", "Pipe formed by rolling flat strip into a cylinder and welding the seam."),
    "p_seamless":  ("Seamless Pipe", "7304.29", "Tubes, pipes, seamless", "Pipe formed without a weld seam for high-pressure applications."),
}

# Edges: downstream -> list of (upstream_input, weight)  [weight = cost share]
EDGES = {
    # Long products
    "p_rebar":     [("c_billet", .72), ("e_heat", .12), ("k_mill", .08), ("l_labour", .08)],
    "p_wirerod":   [("c_billet", .70), ("k_mill", .12), ("e_heat", .10), ("l_labour", .08)],
    "p_sections":  [("c_bloom", .72), ("k_mill", .10), ("e_heat", .10), ("l_labour", .08)],
    "p_rails":     [("c_bloom", .74), ("e_heat", .12), ("l_labour", .08), ("k_mill", .06)],
    "p_merchant":  [("c_billet", .74), ("e_heat", .12), ("k_mill", .08), ("l_labour", .06)],
    "p_piling":    [("c_bloom", .74), ("e_heat", .12), ("k_mill", .08), ("l_labour", .06)],
    # Flat products
    "p_hrc":       [("c_hrc", .86), ("e_heat", .06), ("k_mill", .04), ("l_labour", .04)],
    "p_plate":     [("c_slab", .76), ("e_heat", .12), ("l_labour", .06), ("k_mill", .06)],
    "p_crc":       [("c_crc", .86), ("e_electricity", .06), ("k_mill", .04), ("l_labour", .04)],
    "p_galv":      [("c_crc", .68), ("m_zinc", .16), ("e_heat", .08), ("l_labour", .08)],
    "p_alzinc":    [("c_crc", .62), ("m_aluminium", .10), ("m_zinc", .14), ("e_heat", .08), ("l_labour", .06)],
    "p_prepaint":  [("c_crc", .64), ("m_zinc", .14), ("m_paint", .12), ("e_heat", .05), ("l_labour", .05)],
    "p_tinplate":  [("c_crc", .70), ("m_tin", .16), ("e_electricity", .06), ("k_mill", .04), ("l_labour", .04)],
    "p_eccs":      [("c_crc", .66), ("m_chromium", .12), ("e_electricity", .14), ("l_labour", .08)],
    # Tubular products
    "p_erw":       [("c_hrc", .76), ("e_electricity", .10), ("k_mill", .08), ("l_labour", .06)],
    "p_seamless":  [("c_billet", .72), ("e_heat", .12), ("k_mill", .10), ("l_labour", .06)],

    # Rolled flat intermediates
    "c_hrc":   [("c_slab", .74), ("e_heat", .14), ("k_mill", .07), ("l_labour", .05)],
    "c_crc":   [("c_hrc", .78), ("e_heat", .08), ("e_electricity", .08), ("l_labour", .06)],

    # Semi-finished shapes produced by continuous casting
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
        s, sn = IS_STRENGTH.get(nid, (None, None))
        db.upsert_node(conn, id=nid, value_chain_id=VC, label=label, name=name,
                       component_type=ctype, function=fn,
                       hs_code=[hs] if hs else None,
                       hs_code_description=[hsd] if hsd else None,
                       source_references=SRC,
                       strength=s, strength_note=sn)

    # Finished-product roots
    for pid, (name, hs, hsd, fn) in PRODUCTS.items():
        s, sn = IS_STRENGTH.get(pid, (None, None))
        db.upsert_node(conn, id=pid, value_chain_id=VC, label="System", name=name,
                       component_type="other", function=fn,
                       hs_code=[hs] if hs else None,
                       hs_code_description=[hsd] if hsd else None,
                       source_references=SRC,
                       strength=s, strength_note=sn)

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
