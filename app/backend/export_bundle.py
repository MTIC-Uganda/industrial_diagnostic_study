"""
Export the whole graph (roots + nodes + relationships) to a single static JSON
bundle the frontend can run off directly — no backend required. The shapes match
the live API (main.py) exactly, so api.js can serve getRoots()/getIncoming()
in-memory with identical results.

Run:  python export_bundle.py
Out:  ../frontend/public/graph-bundle.json
"""
import json
from pathlib import Path

import db

OUT = Path(__file__).parent.parent / "frontend" / "public" / "graph-bundle.json"


def node_to_graphnode(n: dict) -> dict:
    props = {k: v for k, v in n.items() if k not in ("id", "label")}
    return {"id": n["id"], "labels": [n["label"]], "properties": props}


def main():
    conn = db.connect()
    node_rows = [db._row_to_node(r) for r in conn.execute("SELECT * FROM nodes").fetchall()]
    rel_rows = conn.execute("SELECT * FROM relationships").fetchall()
    conn.close()

    roots = [
        {
            "element_id": r["id"],
            "name": r["name"],
            "is_public": True,
            "requires_auth": False,
            "source_db": r["value_chain_id"],
        }
        for r in db.get_roots()
    ]

    bundle = {
        "roots": roots,
        "nodes": [node_to_graphnode(n) for n in node_rows],
        "relationships": [
            {
                "id": r["id"],
                "type": r["type"],
                "start_node_id": r["start_node_id"],
                "end_node_id": r["end_node_id"],
                "properties": {"weight": r["weight"], "path_weight": r["weight"]},
            }
            for r in rel_rows
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")
    kb = OUT.stat().st_size / 1024
    print(f"Wrote {OUT} — {len(bundle['roots'])} roots, "
          f"{len(bundle['nodes'])} nodes, {len(bundle['relationships'])} rels, {kb:.0f} KB")


if __name__ == "__main__":
    main()
