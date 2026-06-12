import React, { useEffect, useMemo, useRef, useState } from "react";
import { getRoots, getIncoming } from "./api.js";
import SankeyView from "./Sankey.jsx";
import NodeDetail from "./NodeDetail.jsx";
import { useTour } from "./useTour.js";
import coatOfArms from "../public/uganda_coat_of_arms.png";

export default function App() {
  const [roots, setRoots] = useState([]);       // every product root, all chains
  const [valueChain, setValueChain] = useState(null); // selected value chain (source_db)
  const [path, setPath] = useState([]);          // drill-down breadcrumb; last entry = current root
  const [graph, setGraph] = useState(null);
  const [layers, setLayers] = useState(11);
  const [minPct, setMinPct] = useState(0.3); // percent
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tourActive, setTourActive] = useState(false); // true while the tour is running
  const { startTour } = useTour(setTourActive); // onboarding tour (auto-launches on first visit)

  // Track the scroll container's dimensions so the Sankey always fills available space.
  // Observing the container (not the SVG itself) means NodeDetail opening/closing
  // immediately gives the Sankey its new correct width + height.
  const scrollRef = useRef(null);
  const [scrollDims, setScrollDims] = useState({ w: 1200, h: 640 });
  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const ro = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      if (width > 0 && height > 0)
        setScrollDims({ w: Math.floor(width), h: Math.floor(height) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, []);

  useEffect(() => {
    getRoots().then((rs) => {
      setRoots(rs);
      if (rs.length) {
        setValueChain(rs[0].source_db);
        setPath([{ id: rs[0].element_id, name: rs[0].name }]);
      }
    });
  }, []);

  // Distinct value chains (report sectors) and the products within the selected one.
  const valueChains = useMemo(
    () => [...new Set(roots.map((r) => r.source_db))],
    [roots]
  );
  const products = useMemo(
    () => roots.filter((r) => r.source_db === valueChain),
    [roots, valueChain]
  );

  const currentRoot = path[path.length - 1] || null; // node currently at the chart root
  const currentId = currentRoot?.id || null;

  // A real input node of the current root — used during the tour to render a
  // sample breadcrumb trail so step 5 can actually demonstrate "where you are".
  const demoCrumb = useMemo(() => {
    if (!graph) return null;
    const rel = graph.relationships.find((r) => r.end_node_id === graph.root_node_id);
    const node = rel && graph.nodes.find((n) => n.id === rel.start_node_id);
    return node?.properties?.name || null;
  }, [graph]);

  const onValueChain = (vc) => {
    setValueChain(vc);
    const first = roots.find((r) => r.source_db === vc);
    setPath(first ? [{ id: first.element_id, name: first.name }] : []);
    setSelected(null);
  };

  const onProduct = (id) => {
    const r = products.find((x) => x.element_id === id);
    setPath([{ id, name: r ? r.name : id }]);
    setSelected(null);
  };

  // Hybrid click: open the detail panel AND drill into the node (re-root the
  // chart), unless it is already the root or a leaf with no upstream inputs.
  const handleNodeClick = (node) => {
    if (!node) { setSelected(null); return; }        // background click → close panel
    setSelected(node);
    if (node.id === currentId) return;                // already the root → details only
    const hasUpstream = graph?.relationships?.some((r) => r.end_node_id === node.id);
    if (!hasUpstream) return;                          // raw-material leaf → details only
    setPath((p) => [...p, { id: node.id, name: node.properties.name }]);
  };

  const goToCrumb = (i) => { setPath((p) => p.slice(0, i + 1)); setSelected(null); };
  const goBack = () => { setPath((p) => (p.length > 1 ? p.slice(0, -1) : p)); setSelected(null); };
  const resetRoot = () => { setPath((p) => p.slice(0, 1)); setSelected(null); };

  useEffect(() => {
    if (!currentId) return;
    setLoading(true);
    getIncoming(currentId, layers, minPct / 100)
      .then((g) => setGraph(g))
      .finally(() => setLoading(false));
  }, [currentId, layers, minPct]);

  return (
    <div style={{ fontFamily: "Segoe UI, system-ui, sans-serif", height: "100vh", display: "flex", flexDirection: "column" }}>
      <header style={{ background: "#002b5b", color: "#fff", padding: "14px 22px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
          <img
            src={coatOfArms}
            alt="Coat of arms of Uganda"
            style={{ height: 46, width: "auto", display: "block" }}
          />
          <div>
            <div style={{ fontSize: 19, fontWeight: 700 }}>MTIC Value Chains</div>
            <div style={{ fontSize: 12, opacity: 0.8 }}>
              Systems and their Types — interactive value-chain decomposition
            </div>
          </div>
        </div>
        <button
          id="tour-button"
          onClick={startTour}
          style={{ background: "#1565c0", color: "#fff", border: "none", borderRadius: 4, padding: "7px 14px", fontSize: 13, cursor: "pointer", fontWeight: 600 }}
        >
          Take a Tour
        </button>
      </header>

      <div style={{ display: "flex", gap: 24, alignItems: "flex-start", padding: "12px 22px", borderBottom: "1px solid #eee", flexWrap: "wrap" }}>
        <Control id="tour-valuechain" label="Value chain" hint="Pick which report value chain to explore">
          <select value={valueChain || ""} onChange={(e) => onValueChain(e.target.value)}>
            {valueChains.map((vc) => <option key={vc} value={vc}>{vc}</option>)}
          </select>
        </Control>
        <Control id="tour-product" label="Finished product" hint="Pick a product to trace back to raw materials">
          <select value={path[0]?.id || ""} onChange={(e) => onProduct(e.target.value)}>
            {products.map((r) => <option key={r.element_id} value={r.element_id}>{r.name}</option>)}
          </select>
        </Control>
        <Control id="tour-layers" label={`Layers: ${layers}`} hint="How many steps upstream to show">
          <input type="range" min={1} max={11} value={layers} onChange={(e) => setLayers(+e.target.value)} />
        </Control>
        <Control id="tour-minflow" label={`Min flow: ${minPct.toFixed(1)}%`} hint="Hide flows smaller than this">
          <input type="range" min={0} max={10} step={0.1} value={minPct} onChange={(e) => setMinPct(+e.target.value)} />
        </Control>
        <div style={{ marginLeft: "auto", fontSize: 12, color: "#666", alignSelf: "center" }}>
          {graph && <span>{graph.total_nodes} nodes · {graph.total_relationships} flows</span>}
          {loading && <span style={{ color: "#888" }}>&nbsp;loading…</span>}
        </div>
      </div>

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <div id="tour-scroll" ref={scrollRef} style={{ flex: 1, overflow: "auto", padding: 12, minWidth: 0 }}>
          <div id="tour-breadcrumb" style={{ marginBottom: 10 }}>
            <div style={{ fontSize: 17, fontWeight: 700, color: "#002b5b" }}>
              {currentRoot ? currentRoot.name : "—"}
              <span style={{ fontWeight: 400, color: "#777" }}> · Value Chain</span>
            </div>
            <Breadcrumb path={path} onCrumb={goToCrumb} onBack={goBack} onReset={resetRoot} demo={tourActive} demoCrumb={demoCrumb} />
          </div>
          {!selected && (
            <div id="tour-tip" style={{ fontSize: 13, color: "#1565c0", background: "#eef4fb", border: "1px solid #cfe0f2", borderRadius: 6, padding: "8px 12px", marginBottom: 10 }}>
              💡 <strong>Tip:</strong> Click any block to <strong>drill into it</strong> — the chart re-roots to its breakdown and a details panel opens. Use the breadcrumb above to step back. Flow width shows each input's cost share.
            </div>
          )}
          <div id="tour-diagram">
            <SankeyView
              graph={graph}
              onNodeClick={handleNodeClick}
              selectedId={selected?.id}
              containerW={scrollDims.w}
              containerH={scrollDims.h}
              hasPanel={!!selected}
            />
          </div>
          <Legend />
        </div>
        {selected && <NodeDetail node={selected} onClose={() => setSelected(null)} />}
      </div>
    </div>
  );
}

// Uganda national flag colours: six equal horizontal stripes (black, yellow, red ×2)
function UgandaBand() {
  return (
    <div
      role="presentation"
      title="Uganda"
      style={{
        height: 18,
        marginTop: 10,
        background:
          "linear-gradient(to bottom," +
          "#000000 0 16.667%," +
          "#FCDC04 16.667% 33.333%," +
          "#D90000 33.333% 50%," +
          "#000000 50% 66.667%," +
          "#FCDC04 66.667% 83.333%," +
          "#D90000 83.333% 100%)",
      }}
    />
  );
}

function Breadcrumb({ path, onCrumb, onBack, onReset, demo, demoCrumb }) {
  if (!path.length) return null;

  // Normally the trail + back/reset buttons only appear once the user has
  // drilled in (path > 1). During the tour we render a *sample* trail
  // (product → a real input node) and the buttons even on a fresh, un-drilled
  // view, so step 5 can actually demonstrate "where you are". This demo state is
  // shown only while the tour runs (`demo`) and clears the moment it ends. The
  // sample crumb and buttons are harmless no-ops if clicked here.
  const isDemo = demo && path.length === 1 && !!demoCrumb;
  const crumbs = isDemo ? [...path, { id: "__demo__", name: demoCrumb }] : path;
  const showNav = path.length > 1 || demo;

  const btn = { border: "1px solid #cfe0f2", background: "#eef4fb", color: "#1565c0", borderRadius: 4, cursor: "pointer", fontSize: 11, padding: "1px 7px" };
  return (
    <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 4, marginTop: 5, fontSize: 12.5 }}>
      {crumbs.map((c, i) => {
        const last = i === crumbs.length - 1;
        return (
          <React.Fragment key={c.id + ":" + i}>
            {i > 0 && <span style={{ color: "#bbb" }}>›</span>}
            <button
              onClick={() => !last && onCrumb(i)}
              disabled={last}
              title={last ? "Current view" : `Back to ${c.name}`}
              style={{
                border: "none", background: "none", padding: 0,
                cursor: last ? "default" : "pointer",
                color: last ? "#002b5b" : "#1565c0",
                fontWeight: last ? 700 : 400, fontSize: 12.5,
              }}
            >
              {c.name}
            </button>
          </React.Fragment>
        );
      })}
      {showNav && (
        <button onClick={onBack} title="Back one level" style={{ ...btn, marginLeft: 8 }}>
          ‹ back
        </button>
      )}
      {showNav && (
        <button onClick={onReset} title="Reset to the original product" style={btn}>
          ✕ reset
        </button>
      )}
    </div>
  );
}

function Control({ label, hint, children, id }) {
  return (
    <div id={id} style={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <label style={{ fontSize: 13, fontWeight: 600 }}>{label}</label>
      {children}
      <span style={{ fontSize: 11, color: "#999" }}>{hint}</span>
    </div>
  );
}

function Legend() {
  const items = [
    ["System (finished product)", "#002b5b"],
    ["Technology type", "#26a69a"],
    ["Component", "#1565c0"],
    ["Material", "#2e7d32"],
    ["Energy", "#f9a825"],
    ["Labour", "#8e24aa"],
    ["Machinery", "#6d4c41"],
  ];
  return (
    <div id="tour-legend" style={{ display: "flex", gap: 16, marginTop: 12, fontSize: 12, color: "#555" }}>
      {items.map(([label, c]) => (
        <span key={label} style={{ display: "flex", alignItems: "center", gap: 5 }}>
          <span style={{ width: 12, height: 12, background: c, display: "inline-block", borderRadius: 2 }} />
          {label}
        </span>
      ))}
    </div>
  );
}
