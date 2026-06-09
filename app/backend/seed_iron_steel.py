"""
Iron & Steel value-chain graph for Uganda — full product map.

Models the complete iron & steel value chain as set out in the NPA/UDC
"Report on the Mapping and Value Chain Analysis for Uganda's Iron and Steel
Industry" (June 2025). The report frames the chain in five phases:

  Phase I   Exploration & Mining   -> beneficiated/graded iron ore
  Phase II  Ironmaking             -> sponge iron (DRI) / pig iron
  Phase III Steelmaking            -> crude steel (BOF/EAF/induction)
  Phase IV  Continuous casting     -> semi-finished: billets, blooms, slabs
  Phase V   Steel rolling & finishing -> long & flat products, wire products,
            hollow sections (tubes/pipes), structural steel, roofing, hardware

The Sankey reads left (finished System) to right (raw materials upstream).
Edge direction: start_node = upstream input, end_node = downstream product;
weight = that input's share of the parent's cost / prevalence (0..1, summing
to ~1 within each parent). Value-addition bands per phase are from Table 1 of
the report; cost shares are indicative pending firm-level KII data.

HS codes follow the Harmonized System: chapter 72 (iron & steel), chapter 73
(articles of iron or steel), plus upstream raw materials (26/27/25) and
machinery (84). Nodes whose HS codes have a matching ITC TradeMap CSV get live
trade figures wired in by wire_trademap.py.
"""
import db

VC = "iron_steel_mtic"
SRC = ["NPA/UDC Report on the Mapping and Value Chain Analysis for Uganda's "
       "Iron and Steel Industry (June 2025)"]


# ── Node definitions ────────────────────────────────────────────────────────
# Each entry: dict of kwargs for db.upsert_node. Grouped by phase for clarity.

NODES = [
    # ── Root system ──────────────────────────────────────────────────────────
    dict(id="is:root", label="System", name="Iron & Steel System",
         component_type="other", n_iteration=0,
         function="Produces iron and steel products for construction, "
                  "manufacturing, and infrastructure in Uganda. Installed "
                  "capacity ~1.68m tpa, ~30% utilised (NPA/UDC 2025).",
         mechanism="Iron ore or scrap is reduced/melted into crude steel, cast "
                   "into semi-finished forms (billets, blooms, slabs), then "
                   "rolled and finished into long, flat, tubular, wire, "
                   "structural and hardware products.",
         core_components=["Mining & beneficiation", "Ironmaking (DRI/BF)",
                          "Steelmaking (EAF/induction)", "Continuous casting",
                          "Rolling & finishing"],
         synonyms=["Steel industry", "Ferrous metals value chain"],
         hs_code=["72", "73"],
         hs_code_description=["Iron and steel", "Articles of iron or steel"],
         source_references=SRC),

    # ── Phase V: finished products (TechnologyType, n_iteration=1) ─────────────
    dict(id="is:long", label="TechnologyType", name="Long products (bars & rods)",
         component_type="component", n_iteration=1,
         function="Reinforcement bar (rebar), wire rod, and merchant bar used "
                  "mainly in construction — the largest segment of Ugandan demand.",
         mechanism="Billets are hot-rolled into bars, rods and rounds.",
         prevalence="Largest domestic segment; most installed rolling capacity.",
         price_range="600-900", price_range_unit="USD per tonne",
         hs_code=["7213", "7214", "7215"],
         hs_code_description=["Bars and rods, hot-rolled, in coils",
                              "Other bars and rods of iron/non-alloy steel",
                              "Other bars and rods of iron/non-alloy steel"],
         source_references=SRC),
    dict(id="is:flat", label="TechnologyType", name="Flat products (sheet, coil, plate)",
         component_type="component", n_iteration=1,
         function="Hot- and cold-rolled sheet, coil and plate for manufacturing, "
                  "fabrication and downstream roofing.",
         mechanism="Slabs are hot- and cold-rolled into flat sheet, coil and plate.",
         prevalence="Largely imported; limited domestic flat-rolling capacity.",
         price_range="700-1100", price_range_unit="USD per tonne",
         hs_code=["7208", "7209", "7211", "7225"],
         hs_code_description=["Flat-rolled, hot-rolled, >=600mm",
                              "Flat-rolled, cold-rolled, >=600mm",
                              "Flat-rolled, <600mm",
                              "Flat-rolled of other alloy steel, >=600mm"],
         source_references=SRC),
    dict(id="is:roofing", label="TechnologyType", name="Roofing & coated sheet",
         component_type="component", n_iteration=1,
         function="Galvanised, pre-painted and corrugated roofing sheet — a major "
                  "domestic product (Uganda Baati, Roofings).",
         mechanism="Flat coil is galvanised/coated with zinc or aluminium-zinc, "
                   "then corrugated or profiled.",
         prevalence="Strong domestic production and regional export base.",
         price_range="800-1300", price_range_unit="USD per tonne",
         hs_code=["7210", "7212"],
         hs_code_description=["Flat-rolled, clad/plated/coated, >=600mm",
                              "Flat-rolled, clad/plated/coated, <600mm"],
         source_references=SRC),
    dict(id="is:tubes", label="TechnologyType", name="Tubes, pipes & hollow sections",
         component_type="component", n_iteration=1,
         function="Welded and seamless tubes, pipes and hollow structural "
                  "sections for water, construction and mechanical use.",
         mechanism="Strip/coil is formed and welded into tube, or billet is "
                   "pierced into seamless pipe.",
         prevalence="Growing domestic capacity for welded tube and hollow section.",
         price_range="750-1200", price_range_unit="USD per tonne",
         hs_code=["7304", "7305", "7306"],
         hs_code_description=["Seamless tubes and pipes",
                              "Other tubes/pipes (welded, >406mm)",
                              "Other tubes, pipes and hollow profiles"],
         source_references=SRC),
    dict(id="is:wire", label="TechnologyType", name="Wire & wire products",
         component_type="component", n_iteration=1,
         function="Drawn wire, wire nails, barbed wire, mesh and fencing.",
         mechanism="Wire rod is cold-drawn into wire, then formed into nails, "
                   "barbed wire, woven/welded mesh and fencing.",
         prevalence="Established domestic wire-drawing and nail production.",
         price_range="700-1100", price_range_unit="USD per tonne",
         hs_code=["7217", "7313", "7314", "7317"],
         hs_code_description=["Wire of iron or non-alloy steel",
                              "Barbed wire and fencing wire",
                              "Cloth, grill, netting and fencing of wire",
                              "Nails, tacks, staples and similar"],
         source_references=SRC),
    dict(id="is:structural", label="TechnologyType", name="Structural steel & fabrication",
         component_type="component", n_iteration=1,
         function="Angles, shapes, sections and fabricated structures (trusses, "
                  "frames, towers, bridges).",
         mechanism="Blooms/billets are rolled into sections, then cut, welded "
                   "and fabricated into structures.",
         prevalence="Project-driven; fabrication is labour-intensive.",
         price_range="700-1100", price_range_unit="USD per tonne",
         hs_code=["7216", "7301", "7308"],
         hs_code_description=["Angles, shapes and sections",
                              "Sheet piling; welded angles/shapes/sections",
                              "Structures and parts of structures of iron/steel"],
         source_references=SRC),
    dict(id="is:hardware", label="TechnologyType", name="Hardware & other articles",
         component_type="component", n_iteration=1,
         function="Screws, bolts, nuts, chains, household and other articles of "
                  "iron or steel.",
         mechanism="Bar, wire and sheet are machined, formed and assembled into "
                   "fasteners, fittings and finished articles.",
         prevalence="Mostly imported; some domestic fastener and houseware output.",
         price_range="900-1800", price_range_unit="USD per tonne",
         hs_code=["7318", "7315", "7323", "7326"],
         hs_code_description=["Screws, bolts, nuts and similar",
                              "Chain and parts thereof",
                              "Table, kitchen and household articles",
                              "Other articles of iron or steel"],
         source_references=SRC),

    # ── Phase IV: semi-finished / continuous casting (n_iteration=2) ───────────
    dict(id="is:billet", label="Component", name="Steel billet",
         component_type="component", n_iteration=2,
         function="Semi-finished square-section cast steel; feedstock for long, "
                  "wire and section rolling.",
         mechanism="Crude steel is continuously cast into billets.",
         hs_code=["7207"], hs_code_description=["Semi-finished products of iron/non-alloy steel"],
         source_references=SRC),
    dict(id="is:bloom", label="Component", name="Steel bloom",
         component_type="component", n_iteration=2,
         function="Semi-finished large-section cast steel for heavy structural sections.",
         mechanism="Crude steel is continuously cast into blooms.",
         hs_code=["7207"], hs_code_description=["Semi-finished products of iron/non-alloy steel"],
         source_references=SRC),
    dict(id="is:slab", label="Component", name="Steel slab",
         component_type="component", n_iteration=2,
         function="Semi-finished flat-section cast steel; feedstock for flat, "
                  "roofing and tube production.",
         mechanism="Crude steel is continuously cast into slabs.",
         hs_code=["7207"], hs_code_description=["Semi-finished products of iron/non-alloy steel"],
         source_references=SRC),

    # ── Phase III: steelmaking (n_iteration=3) ─────────────────────────────────
    dict(id="is:crude", label="Component", name="Crude steel (EAF/induction)",
         component_type="component", n_iteration=3,
         function="Liquid steel (<2% C) refined from scrap, sponge and/or pig iron.",
         mechanism="Electric arc / induction furnaces melt scrap and DRI; the "
                   "melt is refined to grade, then sent to casting.",
         prevalence="Uganda's steelmaking is dominated by induction/EAF on scrap.",
         hs_code=["7206"], hs_code_description=["Iron and non-alloy steel in ingots/primary forms"],
         source_references=SRC),
    dict(id="is:scrap", label="Material", name="Ferrous scrap",
         component_type="material", n_iteration=4,
         function="Recycled ferrous feedstock — the dominant charge for Ugandan "
                  "induction/EAF steelmaking.",
         hs_code=["7204"], hs_code_description=["Ferrous waste and scrap"],
         source_references=SRC),
    dict(id="is:ferro", label="Material", name="Ferroalloys & refining chemicals",
         component_type="material", n_iteration=4,
         function="Ferro-manganese, ferro-silicon and fluxes that adjust steel "
                  "chemistry and grade.",
         hs_code=["7202"], hs_code_description=["Ferro-alloys"],
         source_references=SRC),

    # ── Phase II: ironmaking (n_iteration=4) ───────────────────────────────────
    dict(id="is:sponge", label="Component", name="Sponge iron / DRI",
         component_type="component", n_iteration=4,
         function="Directly-reduced iron from ore; primary virgin iron unit for "
                  "the steel furnace.",
         mechanism="Iron ore is reduced below melting point using coal/gas "
                   "(Midrex/HYL/SL-RN) to sponge iron.",
         hs_code=["7203"], hs_code_description=["Ferrous products obtained by direct reduction of iron ore"],
         source_references=SRC),
    dict(id="is:pig", label="Component", name="Pig iron",
         component_type="component", n_iteration=4,
         function="High-carbon iron from the blast furnace; alternative virgin "
                  "iron unit.",
         mechanism="Iron ore, coke and limestone are smelted in a blast furnace "
                   "to molten pig iron.",
         hs_code=["7201"], hs_code_description=["Pig iron and spiegeleisen"],
         source_references=SRC),

    # ── Phase I: mining & raw materials (n_iteration=5) ─────────────────────────
    dict(id="is:ore", label="Material", name="Iron ore (beneficiated)",
         component_type="material", n_iteration=5,
         function="Beneficiated and graded hematite ore — south-western Uganda "
                  "holds high-grade deposits.",
         mechanism="Mined ore is crushed, ground, magnetically separated and "
                   "concentrated, then pelletised/sintered.",
         hs_code=["2601"], hs_code_description=["Iron ores and concentrates"],
         source_references=SRC),
    dict(id="is:coal", label="Material", name="Coal / coke",
         component_type="material", n_iteration=5,
         function="Reductant and energy source for iron reduction (coke for blast "
                  "furnace, coal for DRI).",
         hs_code=["2701", "2704"],
         hs_code_description=["Coal", "Coke and semi-coke"],
         source_references=SRC),
    dict(id="is:flux", label="Material", name="Limestone & dolomite (flux)",
         component_type="material", n_iteration=5,
         function="Fluxes that remove impurities as slag during iron- and steelmaking.",
         hs_code=["2521", "2518"],
         hs_code_description=["Limestone flux", "Dolomite"],
         source_references=SRC),
    dict(id="is:zinc", label="Material", name="Zinc & coating metals",
         component_type="material", n_iteration=2,
         function="Zinc / aluminium-zinc and paint used to galvanise and coat "
                  "roofing and flat product.",
         hs_code=["7901"], hs_code_description=["Unwrought zinc"],
         source_references=SRC),

    # ── Cross-cutting costs ────────────────────────────────────────────────────
    dict(id="is:energy", label="AdditionalInputCost", name="Electricity & energy",
         component_type="other", n_iteration=3,
         function="Power for melting, rolling and finishing. Unreliable supply "
                  "and pricing are the industry's most-cited constraint (NPA/UDC 2025).",
         source_references=SRC),
    dict(id="is:mill", label="MachineryCost", name="Rolling mill",
         component_type="other", n_iteration=2,
         function="Capital equipment for hot/cold rolling of long and flat product.",
         hs_code=["8455"], hs_code_description=["Metal-rolling mills and rolls therefor"],
         source_references=SRC),
    dict(id="is:furnace", label="MachineryCost", name="Furnace & casting plant",
         component_type="other", n_iteration=3,
         function="Electric arc/induction furnaces and continuous casting machines.",
         hs_code=["8454"], hs_code_description=["Converters, ladles, ingot moulds and casting machines"],
         source_references=SRC),
    dict(id="is:labour", label="LaborCost", name="Labour",
         component_type="other", n_iteration=2,
         function="Skilled and semi-skilled labour across melting, rolling, "
                  "fabrication and finishing.",
         source_references=SRC),
]


# ── Relationships: (id, start=upstream input, end=downstream product, weight) ──
# Weight = input's share of the parent's cost / prevalence (sums ~1 per parent).
RELS = [
    # Finished products -> System (prevalence / share of demand)
    ("r_long",   "is:long",       "is:root", 0.28),
    ("r_flat",   "is:flat",       "is:root", 0.20),
    ("r_roof",   "is:roofing",    "is:root", 0.16),
    ("r_tubes",  "is:tubes",      "is:root", 0.12),
    ("r_wire",   "is:wire",       "is:root", 0.10),
    ("r_struct", "is:structural", "is:root", 0.08),
    ("r_hard",   "is:hardware",   "is:root", 0.06),

    # Long products <- billet + rolling
    ("r_long_billet", "is:billet", "is:long", 0.65),
    ("r_long_mill",   "is:mill",   "is:long", 0.12),
    ("r_long_energy", "is:energy", "is:long", 0.15),
    ("r_long_labour", "is:labour", "is:long", 0.08),

    # Flat products <- slab + rolling
    ("r_flat_slab",   "is:slab",   "is:flat", 0.63),
    ("r_flat_mill",   "is:mill",   "is:flat", 0.15),
    ("r_flat_energy", "is:energy", "is:flat", 0.14),
    ("r_flat_labour", "is:labour", "is:flat", 0.08),

    # Roofing & coated sheet <- slab + zinc/coating + rolling
    ("r_roof_slab",   "is:slab",   "is:roofing", 0.52),
    ("r_roof_zinc",   "is:zinc",   "is:roofing", 0.14),
    ("r_roof_mill",   "is:mill",   "is:roofing", 0.12),
    ("r_roof_energy", "is:energy", "is:roofing", 0.14),
    ("r_roof_labour", "is:labour", "is:roofing", 0.08),

    # Tubes & hollow sections <- slab (strip) + billet (seamless) + forming
    ("r_tubes_slab",   "is:slab",   "is:tubes", 0.50),
    ("r_tubes_billet", "is:billet", "is:tubes", 0.15),
    ("r_tubes_mill",   "is:mill",   "is:tubes", 0.13),
    ("r_tubes_energy", "is:energy", "is:tubes", 0.14),
    ("r_tubes_labour", "is:labour", "is:tubes", 0.08),

    # Wire & wire products <- billet (wire rod) + drawing
    ("r_wire_billet", "is:billet", "is:wire", 0.62),
    ("r_wire_mill",   "is:mill",   "is:wire", 0.12),
    ("r_wire_energy", "is:energy", "is:wire", 0.14),
    ("r_wire_labour", "is:labour", "is:wire", 0.12),

    # Structural steel & fabrication <- bloom + billet + heavy labour
    ("r_struct_bloom",  "is:bloom",  "is:structural", 0.50),
    ("r_struct_billet", "is:billet", "is:structural", 0.12),
    ("r_struct_mill",   "is:mill",   "is:structural", 0.08),
    ("r_struct_energy", "is:energy", "is:structural", 0.10),
    ("r_struct_labour", "is:labour", "is:structural", 0.20),

    # Hardware & other articles <- billet/wire feedstock + fabrication labour
    ("r_hard_billet", "is:billet", "is:hardware", 0.45),
    ("r_hard_wire",   "is:wire",   "is:hardware", 0.18),
    ("r_hard_energy", "is:energy", "is:hardware", 0.10),
    ("r_hard_labour", "is:labour", "is:hardware", 0.27),

    # Semi-finished (Phase IV) <- crude steel + casting
    ("r_billet_crude",   "is:crude",   "is:billet", 0.86),
    ("r_billet_energy",  "is:energy",  "is:billet", 0.10),
    ("r_billet_furnace", "is:furnace", "is:billet", 0.04),
    ("r_bloom_crude",    "is:crude",   "is:bloom",  0.86),
    ("r_bloom_energy",   "is:energy",  "is:bloom",  0.10),
    ("r_bloom_furnace",  "is:furnace", "is:bloom",  0.04),
    ("r_slab_crude",     "is:crude",   "is:slab",   0.86),
    ("r_slab_energy",    "is:energy",  "is:slab",   0.10),
    ("r_slab_furnace",   "is:furnace", "is:slab",   0.04),

    # Crude steel (Phase III) <- scrap + sponge + pig + ferroalloys + furnace + energy
    ("r_crude_scrap",   "is:scrap",   "is:crude", 0.48),
    ("r_crude_sponge",  "is:sponge",  "is:crude", 0.18),
    ("r_crude_pig",     "is:pig",     "is:crude", 0.08),
    ("r_crude_ferro",   "is:ferro",   "is:crude", 0.05),
    ("r_crude_furnace", "is:furnace", "is:crude", 0.06),
    ("r_crude_energy",  "is:energy",  "is:crude", 0.12),
    ("r_crude_labour",  "is:labour",  "is:crude", 0.03),

    # Sponge iron / DRI (Phase II) <- ore + coal + flux + energy
    ("r_sponge_ore",    "is:ore",    "is:sponge", 0.55),
    ("r_sponge_coal",   "is:coal",   "is:sponge", 0.22),
    ("r_sponge_flux",   "is:flux",   "is:sponge", 0.06),
    ("r_sponge_energy", "is:energy", "is:sponge", 0.12),
    ("r_sponge_labour", "is:labour", "is:sponge", 0.05),

    # Pig iron (Phase II, blast furnace) <- ore + coke + flux
    ("r_pig_ore",    "is:ore",    "is:pig", 0.50),
    ("r_pig_coal",   "is:coal",   "is:pig", 0.30),
    ("r_pig_flux",   "is:flux",   "is:pig", 0.10),
    ("r_pig_energy", "is:energy", "is:pig", 0.06),
    ("r_pig_labour", "is:labour", "is:pig", 0.04),
]


def run():
    db.init_db()
    conn = db.connect()
    for n in NODES:
        db.upsert_node(conn, value_chain_id=VC, **n)
    for rid, s, e, w in RELS:
        db.upsert_rel(conn, rid, s, e, w)
    conn.commit()
    conn.close()


if __name__ == "__main__":
    run()
    print(f"Iron & Steel value-chain graph seeded: "
          f"{len(NODES)} nodes, {len(RELS)} relationships.")
