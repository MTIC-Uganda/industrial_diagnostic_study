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

export async function getRoots() {
  return bundle().roots || [];
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
