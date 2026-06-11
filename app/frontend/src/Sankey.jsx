import React, { useMemo, useState, useRef, useEffect } from "react";
import { sankey, sankeyLinkHorizontal, sankeyLeft } from "d3-sankey";

const LABEL_MARGIN = 170; // room on the right for the last column's labels

// Structural levels are coloured by label; components/inputs by their category
// (component_type). Keys are split so a component's label ("Material",
// "Component", ...) falls through to its lowercase category colour.
const COLORS = {
  System: "#002b5b",
  Stage: "#00695c",
  Route: "#5c6bc0",
  TechnologyType: "#26a69a",
  material: "#2e7d32",
  component: "#1565c0",
  energy: "#f9a825",
  labor: "#8e24aa",
  machinery: "#6d4c41",
  additive: "#9e9e9e",
  other: "#8e8e8e",
};

function nodeColor(n) {
  return COLORS[n.label] || COLORS[n.componentType] || COLORS.other;
}

// Focus-adjacency: from a node, keep only its immediately connected links —
// its direct inputs and direct outputs — plus the nodes on the other end.
// Everything else is dimmed. (Immediate neighbours only, not the full path.)
function adjacency(nodeId, links) {
  if (!nodeId) return null;
  const nodeIds = new Set([nodeId]);
  const linkSet = new Set();
  for (const l of links) {
    if (l.source.id === nodeId) {        // a direct input of this node
      linkSet.add(l);
      nodeIds.add(l.target.id);
    } else if (l.target.id === nodeId) { // a direct output (this node feeds it)
      linkSet.add(l);
      nodeIds.add(l.source.id);
    }
  }
  return { nodeIds, linkSet };
}

export default function SankeyView({ graph, onNodeClick, selectedId }) {
  const [hovered, setHovered] = useState(null);

  // Fill the available container width; each product's decomposition is a small
  // tree, so it fits without horizontal scrolling.
  const wrapRef = useRef(null);
  const [width, setWidth] = useState(1200);
  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const w = Math.floor(entries[0].contentRect.width);
      if (w > 0) setWidth(Math.max(720, w));
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  // Height scales with the busiest column so its nodes don't get crushed into
  // an unreadable vertical stack (n_iteration = the node's column/depth).
  const height = useMemo(() => {
    if (!graph || !graph.nodes.length) return 560;
    const perCol = {};
    for (const n of graph.nodes) {
      const c = n.properties.n_iteration ?? 0;
      perCol[c] = (perCol[c] || 0) + 1;
    }
    const maxCol = Math.max(...Object.values(perCol));
    return Math.min(2200, Math.max(560, maxCol * 18 + 24));
  }, [graph]);

  const { nodes, links } = useMemo(() => {
    if (!graph || !graph.nodes.length) return { nodes: [], links: [] };

    const nodeList = graph.nodes.map((n) => ({
      id: n.id,
      name: n.properties.name,
      label: n.labels[0],
      componentType: n.properties.component_type,
      strength: n.properties.strength,
      raw: n,
    }));
    const idIndex = new Map(nodeList.map((n, i) => [n.id, i]));

    // Edge direction: start = upstream input, end = downstream product.
    // For a left→right "final product → inputs" Sankey we draw root on the
    // left, so source = downstream (end), target = upstream (start).
    const linkList = graph.relationships
      .filter((r) => idIndex.has(r.start_node_id) && idIndex.has(r.end_node_id))
      .map((r) => ({
        source: idIndex.get(r.end_node_id),
        target: idIndex.get(r.start_node_id),
        value: Math.max(r.properties.weight || 0.001, 0.001),
      }));

    if (!linkList.length) return { nodes: [], links: [] };

    // Reserve room on the right for the deepest column's labels.
    const sk = sankey()
      .nodeWidth(14)
      .nodePadding(9)
      .nodeAlign(sankeyLeft)
      .extent([[8, 8], [width - LABEL_MARGIN, height - 8]]);

    try {
      return sk({
        nodes: nodeList.map((d) => ({ ...d })),
        links: linkList.map((d) => ({ ...d })),
      });
    } catch (e) {
      return { nodes: [], links: [] };
    }
  }, [graph, width, height]);

  // Hovering a node highlights only its immediate inputs and outputs and dims
  // the rest; leaving restores the full view. The selected node keeps its
  // outline (below) but no longer dims the chart, so a drilled-in view stays
  // fully visible.
  const focus = useMemo(() => adjacency(hovered, links), [hovered, links]);

  // One representative drillable node (a direct input of the root) — used as the
  // onboarding tour's "click a block" highlight target (#tour-node).
  const demoNodeId = useMemo(() => {
    const rootId = graph?.root_node_id;
    const fromRoot = links.find((l) => l.source.id === rootId);
    return fromRoot ? fromRoot.target.id : (nodes[1]?.id ?? nodes[0]?.id);
  }, [links, nodes, graph]);

  if (!nodes.length) {
    return <div style={{ padding: 40, color: "#888" }}>No flows to display.</div>;
  }

  // The selected node (its details are in the side panel) never dims.
  const nodeOpacity = (n) =>
    n.id === selectedId || !focus ? 1 : focus.nodeIds.has(n.id) ? 1 : 0.18;
  const linkOpacity = (l) => (!focus ? 0.35 : focus.linkSet.has(l) ? 0.72 : 0.06);
  const TRANS = "opacity 0.3s ease";

  const contentRight = width - LABEL_MARGIN;

  return (
    <div ref={wrapRef} style={{ width: "100%" }}>
      {/* Click on empty canvas clears the selection (and un-dims the chart). */}
      <svg
        width={width}
        height={height}
        style={{ background: "#fff", display: "block" }}
        onClick={() => onNodeClick?.(null)}
      >
      <g>
        {links.map((l, i) => (
          <path
            key={i}
            d={sankeyLinkHorizontal()(l)}
            fill="none"
            stroke={nodeColor(l.target)}
            strokeOpacity={linkOpacity(l)}
            strokeWidth={Math.max(1, l.width)}
            style={{ transition: `stroke-opacity 0.3s ease` }}
          >
            <title>
              {l.source.name} → {l.target.name}: {(l.value * 100).toFixed(1)}%
            </title>
          </path>
        ))}
      </g>
      <g>
        {nodes.map((n, i) => {
          const isSelected = n.id === selectedId;
          const isHovered = n.id === hovered;
          // Outline marks the node: a bold orange ring for the selected one
          // (whose details are in the panel), a thin grey ring on hover.
          const stroke = isSelected ? "#ff6f00" : isHovered ? "#333" : "none";
          const strokeWidth = isSelected ? 5 : isHovered ? 2 : 0;
          const right = n.x1 >= contentRight - 2 || n.x0 < 40;
          return (
            <g
              key={i}
              id={n.id === demoNodeId ? "tour-node" : undefined}
              style={{ cursor: "pointer", transition: TRANS, opacity: nodeOpacity(n) }}
              onClick={(e) => { e.stopPropagation(); onNodeClick?.(n.raw); }}
              onMouseEnter={() => setHovered(n.id)}
              onMouseLeave={() => setHovered(null)}
            >
              <rect
                x={n.x0}
                y={n.y0}
                width={n.x1 - n.x0}
                height={Math.max(1, n.y1 - n.y0)}
                fill={nodeColor(n)}
                stroke={stroke}
                strokeWidth={strokeWidth}
                style={{ transition: "stroke-width 0.12s ease" }}
              >
                <title>{n.name} ({n.label})</title>
              </rect>
              <text
                x={right ? n.x1 + 6 : n.x0 - 6}
                y={(n.y0 + n.y1) / 2}
                dy="0.35em"
                textAnchor={right ? "start" : "end"}
                fontSize={10.5}
                fontWeight={isSelected || isHovered ? 700 : 400}
                fill={isSelected ? "#b34700" : "#222"}
              >
                {n.name}
              </text>
            </g>
          );
        })}
        ))}
      </g>
      </svg>
    </div>
  );
}
