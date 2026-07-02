import React, { useMemo, useState } from "react";
import { sankey, sankeyLinkHorizontal, sankeyLeft } from "d3-sankey";

// Labels now shown only on hover/selection, so we reserve less margin.
// A small buffer still leaves room for the hovered label to render without clipping.
const LABEL_MARGIN = 80;

// Structural levels are coloured by label; components/inputs by their category
// (component_type). Keys are split so a component's label ("Material",
// "Component", ...) falls through to its lowercase category colour.
// Vivid, saturated palette (2026-07-01 minister feedback: "current blue too dull").
// Reference: OEC (Observatory of Economic Complexity) colour conventions — bold,
// high-contrast, each node type immediately recognisable by colour alone.
const COLORS = {
  System:         "#0050c8",  // deep cobalt — top-level system nodes
  Stage:          "#00897b",  // vivid teal — production stages
  Route:          "#6200ea",  // vivid purple — route/pathway nodes
  TechnologyType: "#00acc1",  // vivid cyan — technology groupings
  material:       "#2e7d32",  // vivid forest green — raw materials
  component:      "#c62828",  // vivid red — finished/intermediate components
  energy:         "#f57f17",  // vivid amber — energy inputs
  labor:          "#ad1457",  // vivid magenta — labour / skills
  machinery:      "#4e342e",  // warm dark brown — machinery / capital equipment
  additive:       "#546e7a",  // slate — additives / processing aids
  other:          "#616161",  // mid-grey — uncategorised
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

// Overhead (px) consumed by breadcrumb, tip, legend, and flag band above/below the SVG.
// With the detail panel open the tip is hidden, saving ~66px; use 200 as a safe ceiling.
const OVERHEAD = 200;

export default function SankeyView({ graph, onNodeClick, selectedId, containerW = 1200, containerH = 640, hasPanel = false }) {
  const [hovered, setHovered] = useState(null);

  // Width = full content width of the scroll container (already excludes padding).
  const width = Math.max(320, containerW);

  // Height: fill the scroll container vertically so the chart uses the screen.
  // The node-count formula gives the minimum legible height; the container height
  // (minus overhead for controls above/below) gives the fill target on large screens.
  const height = useMemo(() => {
    const overhead = hasPanel ? OVERHEAD - 60 : OVERHEAD; // tip is hidden when panel is open
    const fillH = Math.max(0, containerH - overhead);
    if (!graph || !graph.nodes.length) return Math.max(fillH, 400);
    const perCol = {};
    for (const n of graph.nodes) {
      const c = n.properties.n_iteration ?? 0;
      perCol[c] = (perCol[c] || 0) + 1;
    }
    const maxCol = Math.max(...Object.values(perCol));
    const contentH = maxCol * 20 + 24; // 20px per node, slight increase for breathing room
    return Math.min(2400, Math.max(fillH, contentH));
  }, [graph, containerH, hasPanel]);

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
      .nodeWidth(18)       // slightly wider bars for visual weight
      .nodePadding(18)     // wider group spacing (was 9) — minister feedback
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
    <>
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
              {/* Labels shown only on hover or selection — keeps the diagram
                  clean at a glance (OEC-style icon/block-first), full
                  text always accessible by hovering or clicking. */}
              {(isHovered || isSelected) && (
                <text
                  x={right ? n.x1 + 6 : n.x0 - 6}
                  y={(n.y0 + n.y1) / 2}
                  dy="0.35em"
                  textAnchor={right ? "start" : "end"}
                  fontSize={10.5}
                  fontWeight={700}
                  fill={isSelected ? "#b34700" : "#111"}
                  style={{ pointerEvents: "none" }}
                >
                  {n.name}
                </text>
              )}
            </g>
          );
        })}
      </g>
      </svg>
    </>
  );
}
