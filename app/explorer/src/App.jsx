import { useState } from "react";
import { PRODUCTS, CATEGORIES } from "./data/ironSteel.js";

function Arrow({ color }) {
  return (
    <div className="flex justify-center my-1">
      <svg width="20" height="18" viewBox="0 0 20 18">
        <line x1="10" y1="0" x2="10" y2="12" stroke={color} strokeWidth="2" />
        <polygon points="4,10 16,10 10,18" fill={color} />
      </svg>
    </div>
  );
}

const TABS = [
  { key: "inputs", label: "Inputs", icon: "📦" },
  { key: "technology", label: "Technology", icon: "⚙️" },
  { key: "skills", label: "Professionals", icon: "🎓" },
];

function TabBar({ tab, setTab, color }) {
  return (
    <div className="flex border-b border-slate-200">
      {TABS.map((t) => (
        <button key={t.key} onClick={() => setTab(t.key)}
          className="flex-1 py-1 text-xs font-semibold transition-all"
          style={{ backgroundColor: tab === t.key ? color : "transparent", color: tab === t.key ? "#fff" : "#475569" }}>
          {t.icon} {t.label}
        </button>
      ))}
    </div>
  );
}

function ItemList({ items, color }) {
  return (
    <ul className="space-y-1 pt-1">
      {(items || []).map((item, i) => (
        <li key={i} className="text-xs flex items-start gap-1.5 text-slate-700">
          <span className="mt-1 shrink-0 w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
          {item}
        </li>
      ))}
    </ul>
  );
}

function CardHeader({ stage, label, color, textColor }) {
  return (
    <div className="px-3 py-2 text-center" style={{ backgroundColor: color }}>
      <div className="text-xs font-semibold tracking-widest uppercase opacity-60" style={{ color: textColor }}>{stage}</div>
      <div className="text-xs font-bold mt-0.5 leading-tight" style={{ color: textColor }}>{label}</div>
    </div>
  );
}

function RouteLabel({ label, color, textColor }) {
  return (
    <div className="text-xs font-bold mb-1.5 text-center px-1 py-0.5 rounded"
      style={{ backgroundColor: color, color: textColor }}>{label}</div>
  );
}

function SimpleCard({ node }) {
  const [tab, setTab] = useState("inputs");
  return (
    <div className="rounded-lg overflow-hidden border border-slate-200 shadow-sm">
      <CardHeader stage={node.stage} label={node.label} color={node.color} textColor={node.textColor} />
      <div style={{ backgroundColor: node.color + "10" }}>
        <TabBar tab={tab} setTab={setTab} color={node.color} />
        <div className="px-3 py-2"><ItemList items={node[tab]} color={node.color} /></div>
      </div>
    </div>
  );
}

function DualCard({ node }) {
  const [tab, setTab] = useState("inputs");
  return (
    <div className="rounded-lg overflow-hidden border border-slate-200 shadow-sm">
      <CardHeader stage={node.stage} label={node.label} color={node.color} textColor={node.textColor} />
      <div style={{ backgroundColor: node.color + "10" }}>
        <TabBar tab={tab} setTab={setTab} color={node.color} />
        <div className="grid grid-cols-2 divide-x divide-slate-200">
          {[node.routeA, node.routeB].map((route, i) => (
            <div key={i} className="p-2">
              <RouteLabel label={route.label} color={node.color} textColor={node.textColor} />
              <ItemList items={route[tab]} color={node.color} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function TripleCard({ node }) {
  const [tab, setTab] = useState("inputs");
  const routes = [node.routeA, node.routeB, node.routeC];
  return (
    <div className="rounded-lg overflow-hidden border border-slate-200 shadow-sm">
      <CardHeader stage={node.stage} label={node.label} color={node.color} textColor={node.textColor} />
      <div style={{ backgroundColor: node.color + "10" }}>
        <TabBar tab={tab} setTab={setTab} color={node.color} />
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", borderTop: "1px solid #e2e8f0" }}>
          {routes.map((route, i) => (
            <div key={i} style={{ padding: "8px", borderRight: i < 2 ? "1px solid #e2e8f0" : "none" }}>
              <div style={{ fontSize: "9px", fontWeight: "700", textAlign: "center", padding: "3px 4px", borderRadius: "4px", marginBottom: "6px", backgroundColor: node.color, color: node.textColor, lineHeight: "1.3" }}>
                {route.label}
              </div>
              <ItemList items={route[tab]} color={node.color} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function GroupCard({ node }) {
  const [tab, setTab] = useState("inputs");
  return (
    <div className="rounded-lg overflow-hidden border border-slate-200 shadow-sm">
      <CardHeader stage={node.stage} label={node.label} color={node.color} textColor={node.textColor} />
      <div style={{ backgroundColor: node.color + "10" }}>
        <TabBar tab={tab} setTab={setTab} color={node.color} />
        <div className="grid grid-cols-2 divide-x divide-slate-200">
          {node.groups.map((g, i) => (
            <div key={i} className={`p-2 ${i < 2 ? "border-b border-slate-200" : ""}`}>
              <RouteLabel label={g.label} color={node.color} textColor={node.textColor} />
              <ItemList items={g[tab] || g.inputs} color={node.color} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function RawCard({ node }) {
  return (
    <div className="rounded-lg overflow-hidden border border-slate-200 shadow-sm">
      <CardHeader stage={node.stage} label={node.label} color={node.color} textColor={node.textColor} />
      <div className="divide-y divide-slate-200" style={{ backgroundColor: node.color + "10" }}>
        {node.items.map((item, i) => (
          <div key={i} className="px-3 py-2 flex items-start gap-2">
            <span className="mt-1 shrink-0 w-1.5 h-1.5 rounded-full" style={{ backgroundColor: node.color }} />
            <div>
              <div className="text-xs font-bold text-slate-800">{item.name}</div>
              <div className="text-xs text-slate-500">{item.detail}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function NodeCard({ node }) {
  if (node.triple) return <TripleCard node={node} />;
  if (node.dual) return <DualCard node={node} />;
  if (node.groups) return <GroupCard node={node} />;
  if (node.rawMaterials) return <RawCard node={node} />;
  return <SimpleCard node={node} />;
}

function Chain({ chain }) {
  return (
    <div className="flex flex-col min-w-0">
      <div className="text-center text-xs font-bold tracking-wider uppercase py-1.5 px-3 rounded-lg mb-2"
        style={{ backgroundColor: chain.accent, color: "#fff" }}>
        {chain.title}
      </div>
      {chain.nodes.map((node, i) => (
        <div key={node.id || i}>
          <NodeCard node={node} />
          {i < chain.nodes.length - 1 && <Arrow color={chain.accent} />}
        </div>
      ))}
    </div>
  );
}

export default function ValueChainExplorer() {
  const [selected, setSelected] = useState("galvanized");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const product = PRODUCTS[selected];

  return (
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#f8fafc", fontFamily: "system-ui, sans-serif", overflow: "hidden" }}>

      {/* Sidebar */}
      <div style={{ display: "flex", flexDirection: "column", backgroundColor: "#0f172a", width: sidebarOpen ? "200px" : "44px", flexShrink: 0, transition: "width 0.2s" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 12px", borderBottom: "1px solid #1e293b" }}>
          {sidebarOpen && <span style={{ color: "#94a3b8", fontSize: "10px", fontWeight: "700", letterSpacing: "0.1em", textTransform: "uppercase" }}>Products</span>}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ color: "#94a3b8", background: "none", border: "none", cursor: "pointer", fontSize: "14px", marginLeft: "auto" }}>
            {sidebarOpen ? "◂" : "▸"}
          </button>
        </div>
        <div style={{ overflowY: "auto", flex: 1, paddingTop: "8px" }}>
          {CATEGORIES.map((cat) => (
            <div key={cat.name} style={{ marginBottom: "12px" }}>
              {sidebarOpen && (
                <div style={{ padding: "2px 12px 4px", fontSize: "9px", fontWeight: "700", letterSpacing: "0.08em", textTransform: "uppercase", color: cat.color === "#1e4976" || cat.color === "#235991" || cat.color === "#1e3a8a" ? "#60a5fa" : cat.color === "#b45309" ? "#f59e0b" : cat.color === "#7c3aed" ? "#a78bfa" : "#94a3b8" }}>
                  {cat.name}
                </div>
              )}
              {cat.products.map((pid) => {
                const p = PRODUCTS[pid];
                return (
                  <button key={pid} onClick={() => setSelected(pid)}
                    title={p.name}
                    style={{ width: "100%", textAlign: "left", padding: sidebarOpen ? "5px 12px" : "8px", background: selected === pid ? "#1e293b" : "transparent", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ width: "6px", height: "6px", borderRadius: "50%", backgroundColor: p.color, flexShrink: 0 }} />
                    {sidebarOpen && <span style={{ fontSize: "11px", color: selected === pid ? "#f1f5f9" : "#94a3b8", fontWeight: selected === pid ? "600" : "400", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{p.name}</span>}
                  </button>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      {/* Main */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>

        {/* Header */}
        <div style={{ backgroundColor: "#fff", borderBottom: "1px solid #e2e8f0", padding: "12px 20px", flexShrink: 0 }}>
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
            <div>
              <div style={{ fontSize: "9px", fontWeight: "700", letterSpacing: "0.1em", textTransform: "uppercase", color: "#94a3b8" }}>
                Tier 2 — Finished Mill Products · {product.category}
              </div>
              <div style={{ fontSize: "18px", fontWeight: "900", color: "#0f172a", marginTop: "2px" }}>{product.name}</div>
              <div style={{ fontSize: "11px", color: "#64748b", marginTop: "2px", maxWidth: "600px" }}>{product.description}</div>
            </div>
            <div style={{ display: "flex", gap: "16px", fontSize: "11px", color: "#94a3b8", flexShrink: 0, marginLeft: "16px" }}>
              <span>📦 <strong>Inputs</strong></span>
              <span>⚙️ <strong>Technology</strong></span>
              <span>🎓 <strong>Professionals</strong></span>
            </div>
          </div>
        </div>

        {/* Chains */}
        <div style={{ flex: 1, overflowY: "auto", padding: "16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: product.chains.length === 1 ? "minmax(0,560px)" : `repeat(${product.chains.length}, minmax(0,1fr))`, gap: "20px", justifyContent: product.chains.length === 1 ? "center" : "stretch", margin: product.chains.length === 1 ? "0 auto" : "0" }}>
            {product.chains.map((chain, i) => (
              <Chain key={i} chain={chain} />
            ))}
          </div>
        </div>

        {/* Footer */}
        <div style={{ backgroundColor: "#fff", borderTop: "1px solid #e2e8f0", padding: "8px 20px", flexShrink: 0 }}>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "12px", justifyContent: "center" }}>
            {[
              { color: "#1a3a5c", label: "Steel — BOF / blast furnace" },
              { color: "#2b7ac5", label: "Steel — EAF / direct reduction" },
              { color: "#7b3f00", label: "Zinc chain" },
              { color: "#2d5a29", label: "Aluminum chain" },
              { color: "#374151", label: "Tin / chromium chain" },
              { color: "#7c3aed", label: "Paint & resin chain" },
            ].map((item, i) => (
              <span key={i} style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "10px", color: "#94a3b8" }}>
                <span style={{ width: "10px", height: "10px", borderRadius: "2px", backgroundColor: item.color, flexShrink: 0 }} />
                {item.label}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
