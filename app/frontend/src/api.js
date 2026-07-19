// Static client for the MTIC Value Chains data. Runs entirely off a bundled
// JSON snapshot (public/graph-bundle.json) — no backend required. getRoots() and
// getIncoming() reproduce the live API (backend/main.py + db.py) in-memory, so
// the UI behaves identically whether served statically or from FastAPI.
//
// The JSON is imported statically so Vite bundles it into the JS chunk at build
// time — this makes the output a single self-contained HTML file with no runtime
// network dependency.

import rawBundle from "../public/graph-bundle.json";

let _bundle = null;

function bundle() {
  if (!_bundle) {
    // Shallow-clone so we can attach the Map without mutating the imported object
    const b = Object.assign({}, rawBundle);
    b._nodeById = new Map(b.nodes.map((n) => [n.id, n]));
    _bundle = b;
  }
  return _bundle;
}

// The Explorer is the primary product list. The map shows only products that
// have an Explorer entry — one product per Explorer card, matched by element_id.
// To add a new product to the map: add it to the Explorer first, then add its
// map element_id here.
const EXPLORER_PRODUCTS = new Set([
  // Iron & Steel (15)
  "p_galv", "p_alzinc", "p_prepaint", "p_tinplate",
  "p_crc", "p_hrc", "p_plate",
  "p_rebar", "p_wirerod", "p_merchant", "p_sections", "p_rails", "p_piling",
  "p_erw", "p_seamless",
  // Copper & Allied Metals (5)
  "cu_p_cable", "cu_p_wire", "cu_p_alu_cond", "cu_p_alu_prof", "cu_p_brass",
  // Automotive (5)
  "au_p_ev", "au_p_motorcycle", "au_p_trailer", "au_p_bus", "au_p_parts",
  // Textiles & Garments (5)
  "tx_p_yarn", "tx_p_fabric", "tx_p_tshirt", "tx_p_workwear", "tx_p_bags",
  // Pharmaceuticals (5)
  "ph_p_arv", "ph_p_antimal", "ph_p_tablets", "ph_p_inject", "ph_p_vaccine",
  // Petrochemicals & Fertilizers (4)
  "pc_p_npk", "pc_p_urea", "pc_p_pe", "pc_p_dap",
  // Sugar & Confectionery (5)
  "sg_p_white", "sg_p_brown", "sg_p_ethanol", "sg_p_hardcandy", "sg_p_softdrink",
  // Plastics & Packaging (5)
  "pl_p_bottles", "pl_p_pipes", "pl_p_bags", "pl_p_house", "pl_p_flexible",
  // Cement & Building Materials (5)
  "cm_p_opc", "cm_p_ppc", "cm_p_blocks", "cm_p_rmc", "cm_p_tiles",
]);

export async function getRoots() {
  return (bundle().roots || []).filter(r => EXPLORER_PRODUCTS.has(r.element_id));
}

// Breadth-first upstream walk from nodeId, keeping edges with weight >= threshold,
// up to `layers` iterations — mirrors db.get_incoming().
export async function getIncoming(nodeId, layers = 4, minThreshold = 0.003) {
  const b = bundle();
  const root = b._nodeById.get(nodeId);
  if (!root) return null;

  const nodes = new Map([[nodeId, root]]);
  const rels = new Map();
  let frontier = [nodeId];

  for (let i = 0; i < layers && frontier.length; i++) {
    const ends = new Set(frontier);
    const next = [];
    for (const r of b.relationships) {
      if (!ends.has(r.end_node_id) || r.properties.weight < minThreshold) continue;
      rels.set(r.id, r);
      const sid = r.start_node_id;
      if (!nodes.has(sid)) {
        const n = b._nodeById.get(sid);
        if (n) { nodes.set(sid, n); next.push(sid); }
      }
    }
    frontier = next;
  }

  const nodeList = [...nodes.values()];
  const relList = [...rels.values()];
  return {
    nodes: nodeList,
    relationships: relList,
    root_node_id: nodeId,
    total_nodes: nodeList.length,
    total_relationships: relList.length,
  };
}
