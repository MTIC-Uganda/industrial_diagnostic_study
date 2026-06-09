"""
Generate a report chapter from the SAME graph that powers the web app.

This is the bridge that keeps the report and the app in lockstep: one graph
per value chain is the single source of truth. Populating it fills the app
(Sankey + node details) AND produces the chapter below.

The chapter follows the Commissioner-approved 6-part value-chain template:
  A. Value Chain Map          <- generated directly from the graph structure
  B. Current State            <- node HS codes + TradeMap trade figures
  C. Binding Constraints      <- template (analyst fills, per node)
  D. Market Assessment        <- node HS codes + TradeMap figures
  E. Prioritized Products     <- template (scoring framework)
  F. Priority Action Matrix   <- template

TradeMap figures are cited inline wherever they appear (per project rule).

Usage:
    python generate_chapter.py is:root --number 4 --out ../../industrial_diagnostic_study/report/chapters/report1-04-iron-steel.md
"""
import sys
import argparse
from pathlib import Path

import db


def _children(graph, parent_id):
    """Upstream inputs of parent_id, with weights, sorted by weight desc."""
    kids = []
    for r in graph["relationships"]:
        if r["end_node_id"] == parent_id:
            child = next((n for n in graph["nodes"] if n["id"] == r["start_node_id"]), None)
            if child:
                kids.append((child, r["properties"]["weight"]))
    return sorted(kids, key=lambda x: -x[1])


def _tree_lines(graph, node_id, depth=0, seen=None):
    """Render the value-chain map as an indented tree (mirrors the Sankey)."""
    seen = seen or set()
    if node_id in seen:
        return []
    seen.add(node_id)
    lines = []
    for child, w in _children(graph, node_id):
        bullet = "  " * depth + f"- **{child['name']}** "
        meta = f"_({child['label']}"
        if child.get("component_type"):
            meta += f", {child['component_type']}"
        meta += f", weight {w:.0%})_"
        hs = child.get("hs_code") or []
        if hs:
            meta += f" — HS {', '.join(map(str, hs))}"
        lines.append(bullet + meta)
        lines += _tree_lines(graph, child["id"], depth + 1, seen)
    return lines


def _trade_rows(graph):
    """Collect nodes that carry HS codes / TradeMap data for Part B & D."""
    rows = []
    for n in graph["nodes"]:
        hs = n.get("hs_code") or []
        if hs:
            tm = n.get("trademap_data")
            rows.append((n["name"], hs, n.get("hs_code_description") or [], tm))
    return rows


def generate(root_id, number=4, layers=6):
    root = db.get_node(root_id)
    if not root:
        raise SystemExit(f"No node {root_id}")
    graph = db.get_incoming(root_id, max_iterations=layers, min_threshold=0)

    name = root["name"].replace(" System", "")
    L = []
    L.append(f"# Chapter {number}: {name} Value Chain")
    L.append("")
    L.append("> This chapter is generated from the value-chain graph that also "
             "powers the interactive dashboard. The structure here mirrors the "
             "app node-for-node; updating one updates the other.")
    L.append("")

    # ── Part A: Value Chain Map (from the graph) ──────────────────
    L.append(f"## {number}.A  Value Chain Map")
    L.append("")
    if root.get("function"):
        L.append(root["function"])
        L.append("")
    if root.get("mechanism"):
        L.append(f"**How it works:** {root['mechanism']}")
        L.append("")
    L.append(f"**{root['name']}** decomposes upstream as follows "
             "(weights = share of the parent's cost/prevalence):")
    L.append("")
    L += _tree_lines(graph, root_id)
    L.append("")

    # ── Part B: Current State ─────────────────────────────────────
    L.append(f"## {number}.B  Current State Assessment")
    L.append("")
    rows = _trade_rows(graph)
    if rows:
        L.append("| Node | HS code(s) | Trade position |")
        L.append("|---|---|---|")
        for nm, hs, desc, tm in rows:
            if tm:
                # summary already carries inline "(Source: ITC TradeMap, HS …)"
                # citations; replace the " | " HS separator with <br> so the
                # markdown table cell renders correctly.
                pos = tm.get("summary", "see TradeMap pull").replace(" | ", "<br>")
            else:
                pos = "_DATA NEEDED — run TradeMap fetch for these HS codes_"
            L.append(f"| {nm} | {', '.join(map(str, hs))} | {pos} |")
        L.append("")
    L.append("_Production volumes, active firms, employment, and capacity "
             "utilization to be completed from Jerome's NPA/UDC sources._")
    L.append("")

    # ── Part C: Binding Constraints ───────────────────────────────
    L.append(f"## {number}.C  Binding Constraints Analysis")
    L.append("")
    for dim in ["Inputs and raw materials", "Technology and productivity",
                "Energy", "Water", "Logistics and transport",
                "Waste and effluent management", "Finance and investment",
                "Skills and workforce", "Standards and quality compliance",
                "Policy and regulatory environment"]:
        L.append(f"- **{dim}:** _…_")
    L.append("")

    # ── Part D: Market Assessment ─────────────────────────────────
    L.append(f"## {number}.D  Market Assessment")
    L.append("")
    L.append("Domestic, regional (EAC/COMESA), and global markets per node, "
             "using ITC TradeMap import/export series for the HS codes above. "
             "_All trade figures cited inline to TradeMap at point of use._")
    L.append("")

    # ── Part E: Prioritized Products ──────────────────────────────
    L.append(f"## {number}.E  Prioritized Products")
    L.append("")
    L.append("Apply the five-criterion scoring framework (accessible market 25%, "
             "comparative advantage 25%, feasibility 20%, jobs 15%, import "
             "substitution 15%) to the technology types above to select 3–4 "
             "priority products, with explicit deprioritization rationale.")
    L.append("")

    # ── Part F: Priority Action Matrix ────────────────────────────
    L.append(f"## {number}.F  Priority Action Matrix")
    L.append("")
    L.append("| Timeframe | Action | Responsible | Indicative cost |")
    L.append("|---|---|---|---|")
    L.append("| Quick win (0–12m) | _…_ | | |")
    L.append("| Reform (1–3y) | _…_ | | |")
    L.append("| Investment (3–5y) | _…_ | | |")
    L.append("")

    return "\n".join(L)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root_id")
    ap.add_argument("--number", type=int, default=4)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    md = generate(args.root_id, args.number)
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"Wrote {args.out}")
    else:
        print(md)
