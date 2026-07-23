"""
Full graph rebuild — run this instead of individual seed/wire/export scripts.

Order is mandatory:
  1. seed_products   — Iron & Steel nodes + edges
  2. seed_all_chains — other 8 chains
  3. wire_trademap   — inject ITC TradeMap trade figures into every node
  4. export_bundle   — write graph-bundle.json for the Sankey frontend

Always run wire_trademap after any reseed; skipping it leaves NodeDetail
panels showing "Trade data not yet available."
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import db
import seed_products
import seed_all_chains
import wire_trademap
import export_bundle


def main():
    print("── Step 1: seed Iron & Steel ──────────────────────────────────────")
    db.init_db()
    nodes, rels = seed_products.run()
    print(f"   {nodes} nodes, {rels} relationships, {len(seed_products.PRODUCTS)} product roots\n")

    print("── Step 2: seed all other chains ──────────────────────────────────")
    seed_all_chains.run()
    print()

    print("── Step 3: wire ITC TradeMap data ─────────────────────────────────")
    wire_trademap.run()
    print()

    print("── Step 4: export graph-bundle.json ───────────────────────────────")
    export_bundle.main()
    print("\nDone. graph.db and graph-bundle.json are up to date.")


if __name__ == "__main__":
    main()
