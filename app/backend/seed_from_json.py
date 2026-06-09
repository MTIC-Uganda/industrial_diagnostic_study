"""
Load a structured value-chain dataset (valuechains.ai-style JSON) into the graph.

The dataset nests five levels:

    System (root)
      -> Stage              (e.g. Raw materials, Iron-making, ...)
        -> Production route (with prevalence %)
          -> Technology type
            -> Component / material   (hs_code, category, cost_share_pct, CO2)
              -> upstream inputs      (category, weight_pct)

Each level becomes a node; each parent/child pair becomes a directed edge whose
start_node is the upstream input (child) and end_node is the downstream product
(parent) — matching the app's "incoming" traversal, which walks from the System
root outward to raw inputs. Edge weight is the child's share of its parent:

    stage   -> root   : 1.0 (equal bands)
    route   -> stage  : prevalence_pct / 100
    type    -> route  : equal share among sibling types
    comp    -> type   : cost_share_pct / 100
    input   -> comp   : weight_pct / 100

Run via db.py (which calls run()) or directly:  python seed_from_json.py
"""
import json
from pathlib import Path

import db

DATA_FILE = Path(__file__).parent / "iron_steel_value_chain.json"
ROOT_ID = "is:root"

# JSON category -> (node label, component_type used for colour/detail)
CATEGORY = {
    "material":  ("Material", "material"),
    "component": ("Component", "component"),
    "energy":    ("Energy", "energy"),
    "labor":     ("LaborCost", "labor"),
    "machinery": ("MachineryCost", "machinery"),
    "additive":  ("Additive", "additive"),
}


def _specs(*parts):
    """Join non-empty specification fragments into one sentence."""
    return "  ".join(p for p in parts if p) or None


def run():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    vc = "iron_steel_global"

    db.init_db()
    conn = db.connect()

    nodes = []   # collected (kwargs) — upserted below
    rels = []    # (id, start=child, end=parent, weight)

    def add_node(**kw):
        nodes.append(kw)

    def add_rel(child_id, parent_id, weight):
        rels.append((f"e:{child_id}->{parent_id}", child_id, parent_id,
                     round(max(weight, 0.001), 4)))

    # ── Interleaved, process-order value chain ────────────────────────────────
    # Left to right: Iron & Steel Value Chain (root) -> Raw materials & inputs +
    # its full breakdown -> Iron-making + breakdown -> Steel-making -> Casting &
    # rolling -> Finished steel products + breakdown.
    #
    # Each stage opens up to its routes -> technology types -> components ->
    # upstream inputs, and a stage's component-level products feed the next
    # stage, threading the stages so they sit after the previous stage's
    # breakdown (a true left-to-right material flow). n_iteration is the node's
    # column: stage i sits at 1 + 4*i, its routes/types/components/inputs at the
    # next four columns.
    add_node(id=ROOT_ID, value_chain_id=vc, label="System",
             name=data.get("title", "Iron & Steel Value Chain"),
             component_type="other", n_iteration=0,
             function=data.get("description"),
             source_references=["valuechains.ai-style structured dataset"])

    stages = data["stages"]            # process order: s1 raw ... s5 finished
    prev_components = None              # component ids of the previous stage
    for i, stage in enumerate(stages):
        sd = 1 + 4 * i                 # this stage's column
        sid = stage["id"]
        add_node(id=sid, value_chain_id=vc, label="Stage", name=stage["label"],
                 n_iteration=sd, function=stage.get("sub"),
                 source_references=["valuechains.ai-style structured dataset"])
        if prev_components is None:     # first stage feeds the root
            add_rel(sid, ROOT_ID, 1.0)
        else:                           # previous stage's products feed this one
            for pcid in prev_components:
                add_rel(sid, pcid, 0.08)

        stage_components = []
        for route in stage["routes"]:
            rid = route["id"]
            prev = route.get("prevalence_pct")
            add_node(id=rid, value_chain_id=vc, label="Route", name=route["label"],
                     n_iteration=sd + 1,
                     prevalence=(f"{prev}% of the {stage['label']} stage"
                                 if prev is not None else None),
                     source_references=["valuechains.ai-style structured dataset"])
            add_rel(rid, sid, (prev or 100) / 100.0)

            types = route.get("types", [])
            type_share = 1.0 / max(len(types), 1)
            for typ in types:
                tid = typ["id"]
                add_node(id=tid, value_chain_id=vc, label="TechnologyType",
                         name=typ["label"], n_iteration=sd + 2,
                         source_references=["valuechains.ai-style structured dataset"])
                add_rel(tid, rid, type_share)

                for ci, comp in enumerate(typ.get("components", [])):
                    cid = f"{tid}_c{ci}"
                    label, ctype = CATEGORY.get(comp.get("category", ""),
                                                ("Component", "component"))
                    hs = comp.get("hs_code")
                    # Keep the upstream inputs as detail on the component (shown
                    # in the panel) rather than as their own flow nodes, which
                    # would create a ~200-node fan-out that drowns later stages.
                    inputs = comp.get("upstream_inputs", [])
                    add_node(
                        id=cid, value_chain_id=vc, label=label, name=comp["name"],
                        component_type=ctype, n_iteration=sd + 3,
                        function=comp.get("function"),
                        mechanism=comp.get("mechanism"),
                        specifications=_specs(
                            f"Category: {comp.get('category')}." if comp.get("category") else "",
                            f"Cost share within type: {comp['cost_share_pct']}%." if comp.get("cost_share_pct") is not None else "",
                            f"CO2 intensity: {comp['co2_intensity']}." if comp.get("co2_intensity") else "",
                        ),
                        core_components=[
                            f"{inp['name']}"
                            + (f" ({inp['weight_pct']}%)" if inp.get("weight_pct") else "")
                            + (f" — {inp['category']}" if inp.get("category") else "")
                            for inp in inputs
                        ] or None,
                        hs_code=[hs] if hs else None,
                        source_references=["valuechains.ai-style structured dataset"],
                    )
                    add_rel(cid, tid, (comp.get("cost_share_pct") or 0) / 100.0)
                    stage_components.append(cid)

        prev_components = stage_components

    for kw in nodes:
        db.upsert_node(conn, **kw)
    for rid, s, e, w in rels:
        db.upsert_rel(conn, rid, s, e, w)

    conn.commit()
    conn.close()
    return len(nodes), len(rels)


if __name__ == "__main__":
    n, r = run()
    print(f"Loaded value chain from {DATA_FILE.name}: {n} nodes, {r} relationships.")
