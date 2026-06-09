"""
SQLite graph store + recursive upstream traversal.

The traversal mirrors valuechains.ai's /graph/incoming: starting from a root
product node, walk UPSTREAM along GROUPED_PATH edges (end_node = product,
start_node = input) up to `max_iterations` layers, keeping only edges whose
weight >= min_threshold.
"""
import sqlite3
import json
from pathlib import Path

DB_PATH     = Path(__file__).parent / "graph.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

JSON_FIELDS = ["synonyms", "core_components", "hs_code", "hs_code_description",
               "hs_code_explanation", "source_references", "trademap_data"]


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create tables from schema.sql (idempotent)."""
    conn = connect()
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.commit()
    conn.close()


def _row_to_node(row):
    d = dict(row)
    for f in JSON_FIELDS:
        if d.get(f):
            try:
                d[f] = json.loads(d[f])
            except (json.JSONDecodeError, TypeError):
                pass
    return d


def get_node(node_id):
    conn = connect()
    row = conn.execute("SELECT * FROM nodes WHERE id = ?", (node_id,)).fetchone()
    conn.close()
    return _row_to_node(row) if row else None


def get_roots():
    """Root systems = System nodes that are never an upstream input
    (no relationship where they are the start_node)."""
    conn = connect()
    rows = conn.execute(
        """
        SELECT n.* FROM nodes n
        WHERE n.label = 'System'
          AND n.id NOT IN (SELECT start_node_id FROM relationships)
        ORDER BY n.name
        """
    ).fetchall()
    conn.close()
    return [_row_to_node(r) for r in rows]


def get_incoming(root_id, max_iterations=4, min_threshold=0.003):
    """
    Breadth-first upstream walk from root_id.
    Returns {nodes, relationships, root_node_id, total_nodes, total_relationships}.
    """
    conn = connect()
    collected_nodes = {}
    collected_rels  = {}

    root = conn.execute("SELECT * FROM nodes WHERE id = ?", (root_id,)).fetchone()
    if not root:
        conn.close()
        return None
    collected_nodes[root_id] = _row_to_node(root)

    frontier = [root_id]
    for _ in range(max_iterations):
        if not frontier:
            break
        placeholders = ",".join("?" * len(frontier))
        rels = conn.execute(
            f"""
            SELECT * FROM relationships
            WHERE end_node_id IN ({placeholders})
              AND weight >= ?
            """,
            (*frontier, min_threshold),
        ).fetchall()

        next_frontier = []
        for r in rels:
            collected_rels[r["id"]] = {
                "id": r["id"],
                "type": r["type"],
                "start_node_id": r["start_node_id"],
                "end_node_id": r["end_node_id"],
                "properties": {"weight": r["weight"], "path_weight": r["weight"]},
            }
            sid = r["start_node_id"]
            if sid not in collected_nodes:
                nrow = conn.execute("SELECT * FROM nodes WHERE id = ?", (sid,)).fetchone()
                if nrow:
                    collected_nodes[sid] = _row_to_node(nrow)
                    next_frontier.append(sid)
        frontier = next_frontier

    conn.close()
    nodes = list(collected_nodes.values())
    rels  = list(collected_rels.values())
    return {
        "nodes": nodes,
        "relationships": rels,
        "root_node_id": root_id,
        "total_nodes": len(nodes),
        "total_relationships": len(rels),
    }


# ── Write helpers (used by seed scripts) ────────────────────────────────────

def upsert_node(conn, **kw):
    for f in JSON_FIELDS:
        if f in kw and not isinstance(kw[f], (str, type(None))):
            kw[f] = json.dumps(kw[f], ensure_ascii=False)
    cols = ", ".join(kw.keys())
    placeholders = ", ".join("?" * len(kw))
    updates = ", ".join(f"{k}=excluded.{k}" for k in kw if k != "id")
    conn.execute(
        f"INSERT INTO nodes ({cols}) VALUES ({placeholders}) "
        f"ON CONFLICT(id) DO UPDATE SET {updates}",
        tuple(kw.values()),
    )


def upsert_rel(conn, rid, start_id, end_id, weight, rtype="GROUPED_PATH"):
    conn.execute(
        "INSERT INTO relationships (id, type, start_node_id, end_node_id, weight) "
        "VALUES (?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET weight=excluded.weight",
        (rid, rtype, start_id, end_id, weight),
    )


if __name__ == "__main__":
    init_db()
    print(f"Initialised {DB_PATH}")
    # Seed the per-product Iron & Steel decomposition graph.
    try:
        import seed_products
        n, r = seed_products.run()
        print(f"Seeded Iron & Steel: {n} nodes, {r} relationships.")
    except ImportError:
        print("No Iron & Steel seed script found.")
    try:
        import seed_all_chains
        nn, np, nr = seed_all_chains.run()
        print(f"Seeded {len(seed_all_chains.CHAINS)} other value chains: "
              f"{nn} nodes, {np} product roots, {nr} relationships.")
    except ImportError:
        print("No multi-chain seed script found.")
