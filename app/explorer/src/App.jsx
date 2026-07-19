import { useState, useRef, useLayoutEffect, useEffect } from "react";
import { PRODUCTS, CATEGORIES, TRADE_HS4, PRODUCT_HS4, RAW_MATERIAL_TRADE, matchInputTrade, matchInputPhase, PRODUCT_FIRMS, PHASE_PRODUCERS, PHASE_SOURCE, RAW_MATERIAL_PHASE } from "./data/index.js";

// Resolve PocketBase URL from the page host so the same HTML works on staging and prod.
function pbUrl() {
  try {
    const h = window.location.hostname;
    if (h.includes("staging")) return "https://staging-db.midd-ug.com";
    if (h.includes("midd-ug.com")) return "https://db.midd-ug.com";
    return "http://89.167.121.193:8090"; // direct IP fallback for local dev
  } catch { return "http://89.167.121.193:8090"; }
}

// Module-level cache that gets populated after the first live fetch.
// Keyed by hs4_code; values override the static TRADE_HS4 from the JS bundle.
const _liveTradeCache = {};

function resolveTrade(hs4) {
  if (!hs4) return null;
  return _liveTradeCache[hs4] || TRADE_HS4[hs4] || null;
}

function resolveRawTrade(name) {
  return RAW_MATERIAL_TRADE[name] || null;
}

function formatUsd(thousands) {
  if (thousands == null) return "—";
  const usd = thousands * 1000;
  if (usd >= 1_000_000) return `$${(usd / 1_000_000).toFixed(1)}m`;
  if (usd >= 1_000) return `$${(usd / 1_000).toFixed(0)}k`;
  return `$${usd}`;
}

function TradeBlock({ trade, noDataLabel }) {
  return (
    <>
      <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "10px" }}>📦 Trade ({trade ? trade.year : "—"}, USD)</div>
      {trade ? (
        <>
          <div style={{ color: "#cbd5e1" }}>
            Imports — Uganda: <strong>{formatUsd(trade.imports.uganda)}</strong> · EAC: <strong>{formatUsd(trade.imports.eac)}</strong> · Global: <span style={{ color: "#64748b" }}>not yet sourced</span>
          </div>
          <div style={{ color: "#cbd5e1" }}>
            Exports — Uganda: <strong>{formatUsd(trade.exports.uganda)}</strong> · EAC: <strong>{formatUsd(trade.exports.eac)}</strong>
          </div>
          <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "4px" }}>{trade.desc}</div>
        </>
      ) : (
        <div style={{ color: "#94a3b8" }}>{noDataLabel}</div>
      )}
    </>
  );
}

// This app is normally embedded in an <iframe> on the live dashboard. A
// popup that stays within the iframe's OWN window.innerHeight can still run
// off the bottom of what the user actually sees, if the iframe itself is
// taller than the remaining space below the fold of the outer page (i.e.
// the iframe is only partially scrolled into view). Same-origin iframes can
// read window.frameElement to find their own position within the parent
// page, so use that — when available — as the real clamp boundary instead
// of just this document's own viewport.
function getVisibleViewport() {
  let top = 0, left = 0, height = window.innerHeight, width = window.innerWidth;
  try {
    if (window.frameElement && window.parent && window.parent !== window) {
      const r = window.frameElement.getBoundingClientRect();
      const pH = window.parent.innerHeight;
      const pW = window.parent.innerWidth;
      top = Math.max(0, -r.top);
      left = Math.max(0, -r.left);
      height = Math.max(0, Math.min(r.bottom, pH) - Math.max(r.top, 0));
      width = Math.max(0, Math.min(r.right, pW) - Math.max(r.left, 0));
    }
  } catch (e) {
    // Cross-origin or no parent access — fall back to this document's own viewport.
  }
  return { top, left, height, width };
}

// Renders the popup, measures its own size once mounted, and clamps/flips
// it so it always stays fully within the visible viewport relative to the
// hovered element's rect — regardless of where on the page that element is,
// and regardless of how much of the embedding iframe is actually visible.
function StatsPopupShell({ title, anchorRect, children }) {
  const ref = useRef(null);
  const [pos, setPos] = useState(null);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el || !anchorRect) return;
    const margin = 8;
    const vp = getVisibleViewport();
    const w = el.offsetWidth;
    const h = el.offsetHeight;
    const maxW = Math.max(50, vp.width - 2 * margin);
    const maxH = Math.max(50, vp.height - 2 * margin);

    let left = anchorRect.right + margin;
    if (left + Math.min(w, maxW) > vp.left + vp.width - margin) {
      left = anchorRect.left - Math.min(w, maxW) - margin; // flip to the left of the anchor
    }
    left = Math.max(vp.left + margin, Math.min(left, vp.left + vp.width - Math.min(w, maxW) - margin));

    let top = anchorRect.top;
    top = Math.max(vp.top + margin, Math.min(top, vp.top + vp.height - Math.min(h, maxH) - margin));

    setPos({ top, left, maxW, maxH });
  }, [anchorRect]);

  return (
    <div
      ref={ref}
      style={{
        position: "fixed", zIndex: 50,
        top: pos ? pos.top : anchorRect.top, left: pos ? pos.left : anchorRect.right + 8,
        visibility: pos ? "visible" : "hidden", width: "300px",
        // Repositioning alone can't keep the popup on-screen if its content
        // is taller than the visible viewport — cap its own size to fit,
        // and let it scroll internally if needed.
        maxWidth: pos ? `${pos.maxW}px` : "calc(100vw - 16px)",
        maxHeight: pos ? `${pos.maxH}px` : "calc(100vh - 16px)",
        overflowY: "auto",
        backgroundColor: "#0f172a", color: "#e2e8f0", borderRadius: "8px",
        padding: "12px 14px", boxShadow: "0 8px 24px rgba(0,0,0,0.4)",
        fontSize: "11px", lineHeight: 1.5, pointerEvents: "none",
      }}
    >
      <div style={{ fontWeight: 700, fontSize: "12px", color: "#fff" }}>{title}</div>
      {children}
    </div>
  );
}

function PhaseCountBlock({ phase }) {
  const p = PHASE_PRODUCERS[phase];
  if (!p) return null;
  return (
    <>
      <div style={{ color: "#cbd5e1" }}><strong>{p.count} plants</strong> — {p.label}</div>
      <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "2px" }}>
        e.g. {p.examples.join(", ")}.
      </div>
    </>
  );
}

// Phase-level context is shown only as secondary background, never as the
// answer to "how many plants make this product" — it's the same number for
// every product sharing that phase, so presenting it as the headline would
// repeat the exact mistake this was built to fix.
function PhaseContextNote({ phaseContext }) {
  if (!phaseContext) return null;
  const p = PHASE_PRODUCERS[phaseContext.phase];
  if (!p) return null;
  return (
    <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "6px", borderTop: "1px solid #1e293b", paddingTop: "4px" }}>
      Broader context, NOT specific to this product: {p.count} plants are marked active in {p.label} overall — a
      total shared with {phaseContext.sharedWith}. The register doesn't break this down by which specific product
      each plant makes.
    </div>
  );
}

function ProducerBlock({ entry }) {
  if (!entry || entry.status === "unknown") {
    return (
      <>
        <div style={{ color: "#94a3b8" }}>Not identified per-product in source documents — neither confirmed present nor absent.</div>
        {entry?.note && <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "2px" }}>{entry.note}</div>}
        <PhaseContextNote phaseContext={entry?.phaseContext} />
      </>
    );
  }
  if (entry.status === "absent") {
    return (
      <>
        <div style={{ color: "#fca5a5" }}>No domestic producer identified — explicitly described as absent/deprioritized in the source report.</div>
        {entry.note && <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "2px" }}>{entry.note}</div>}
        <PhaseContextNote phaseContext={entry.phaseContext} />
      </>
    );
  }
  // status === "named": firms the report chapter specifically attributes to
  // THIS product — the most specific answer available, not a shared count.
  return (
    <>
      <div style={{ color: "#cbd5e1" }}>{entry.firms.join(" · ")}</div>
      <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "2px" }}>
        Named firms only, from the report's plant-register excerpt — not a verified complete count.
        {entry.note ? ` ${entry.note}` : ""}
      </div>
      <PhaseContextNote phaseContext={entry.phaseContext} />
    </>
  );
}

function ProductStatsPopup({ product, hs4, anchorRect }) {
  const trade = resolveTrade(hs4);
  const producers = PRODUCT_FIRMS[product.id];
  return (
    <StatsPopupShell title={product.name} anchorRect={anchorRect}>

      {/* ── Uganda trade (minister question: how much imported / exported) ── */}
      <TradeBlock trade={trade} noDataLabel="Trade data not yet fetched for this product's HS code." />

      {/* ── Known producers + industry count ───────────────────────────── */}
      <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "10px" }}>🏭 Known producers</div>
      <ProducerBlock entry={producers} />

      {/* ── Installed capacity (minister question) — populated from MTIC   */}
      {/* ── National Industries Register; left blank until register data   */}
      {/* ── is linked per product (interim: see phase count above).       */}
      <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "10px" }}>⚡ Total installed capacity</div>
      {producers?.capacity ? (
        <div style={{ color: "#cbd5e1" }}>{producers.capacity}</div>
      ) : (
        <div style={{ color: "#64748b", fontSize: "11px" }}>
          Capacity data per product is being compiled from the MTIC National Industries Register.
          {producers?.phaseContext &&
            " Phase-level capacity is referenced in the producers section above."}
        </div>
      )}

      {/* ── HS code(s) for traceability ───────────────────────────────── */}
      {hs4 && (
        <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "6px" }}>
          HS code: <strong>{hs4.replace(/_/g, " + ")}</strong>
        </div>
      )}

      <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "8px", borderTop: "1px solid #1e293b", paddingTop: "6px" }}>
        Sources: ITC TradeMap (Uganda bilateral trade 2024) · {PHASE_SOURCE}
      </div>
    </StatsPopupShell>
  );
}

function RawMaterialPopup({ item, anchorRect }) {
  const trade = resolveRawTrade(item.name);
  const phase = RAW_MATERIAL_PHASE[item.name];
  return (
    <StatsPopupShell title={item.name} anchorRect={anchorRect}>
      <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "8px" }}>🏭 Industries &amp; capacity</div>
      {phase ? (
        <PhaseCountBlock phase={phase} />
      ) : (
        <div style={{ color: "#94a3b8" }}>Not yet sourced for this raw material (mining/production data is not in the source documents at this granularity).</div>
      )}

      <TradeBlock trade={trade} noDataLabel="No HS-code-specific trade data fetched yet for this raw material." />

      <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "8px", borderTop: "1px solid #1e293b", paddingTop: "6px" }}>
        {phase ? `Sources: ITC TradeMap (Uganda bilateral trade) · ${PHASE_SOURCE}` : "Source: ITC TradeMap (Uganda bilateral trade)"}
      </div>
    </StatsPopupShell>
  );
}

function InputStatsPopup({ text, anchorRect }) {
  const trade = matchInputTrade(text);
  const phase = matchInputPhase(text);
  return (
    <StatsPopupShell title={text} anchorRect={anchorRect}>
      <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "8px" }}>🏭 Industries &amp; capacity</div>
      {phase ? (
        <div style={{ color: "#cbd5e1" }}><strong>{phase.count} plants</strong> — {phase.label}</div>
      ) : (
        <div style={{ color: "#94a3b8" }}>
          No count exists for this intermediate stream specifically — it's produced inside whichever finished-product
          plants use this process step. See that product's card for named producers, where known.
        </div>
      )}

      <TradeBlock trade={trade} noDataLabel="No HS-code-specific trade data fetched yet for this input." />

      <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "8px", borderTop: "1px solid #1e293b", paddingTop: "6px" }}>
        {phase ? `Sources: ITC TradeMap (Uganda bilateral trade) · ${PHASE_SOURCE}` : "Source: ITC TradeMap (Uganda bilateral trade)"}
      </div>
    </StatsPopupShell>
  );
}

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

function ItemList({ items, color, showTrade }) {
  const [hover, setHover] = useState(null);
  return (
    <ul className="space-y-1 pt-1">
      {(items || []).map((item, i) => (
        <li key={i} className="text-xs flex items-start gap-1.5 text-slate-700"
          onMouseEnter={showTrade ? (e) => {
            const r = e.currentTarget.getBoundingClientRect();
            setHover({ text: item, rect: r });
          } : undefined}
          onMouseLeave={showTrade ? () => setHover(null) : undefined}>
          <span className="mt-1 shrink-0 w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
          {item}
        </li>
      ))}
      {hover && <InputStatsPopup text={hover.text} anchorRect={hover.rect} />}
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
        <div className="px-3 py-2"><ItemList items={node[tab]} color={node.color} showTrade={tab === "inputs"} /></div>
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
              <ItemList items={route[tab]} color={node.color} showTrade={tab === "inputs"} />
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
              <ItemList items={route[tab]} color={node.color} showTrade={tab === "inputs"} />
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
              <ItemList items={g[tab] || g.inputs} color={node.color} showTrade={tab === "inputs"} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function RawCard({ node }) {
  const [hover, setHover] = useState(null);
  return (
    <div className="rounded-lg overflow-hidden border border-slate-200 shadow-sm">
      <CardHeader stage={node.stage} label={node.label} color={node.color} textColor={node.textColor} />
      <div className="divide-y divide-slate-200" style={{ backgroundColor: node.color + "10" }}>
        {node.items.map((item, i) => (
          <div key={i} className="px-3 py-2 flex items-start gap-2"
            onMouseEnter={(e) => {
              const r = e.currentTarget.getBoundingClientRect();
              setHover({ item, rect: r });
            }}
            onMouseLeave={() => setHover(null)}>
            <span className="mt-1 shrink-0 w-1.5 h-1.5 rounded-full" style={{ backgroundColor: node.color }} />
            <div>
              <div className="text-xs font-bold text-slate-800">{item.name}</div>
              <div className="text-xs text-slate-500">{item.detail}</div>
            </div>
          </div>
        ))}
      </div>
      {hover && <RawMaterialPopup item={hover.item} anchorRect={hover.rect} />}
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
  const [hoverInfo, setHoverInfo] = useState(null);
  const [, setLiveTradeVersion] = useState(0); // incremented after PocketBase fetch to trigger re-render

  // Fetch trade data live from PocketBase on every page load so a refresh picks
  // up the latest values without a new deploy. Silently falls back to the
  // bundled static data if PocketBase is unreachable.
  useEffect(() => {
    const base = pbUrl();
    fetch(`${base}/api/collections/explorer_trade_hs4/records?perPage=500&sort=hs4_code`)
      .then(r => r.json())
      .then(data => {
        for (const row of data.items || []) {
          _liveTradeCache[row.hs4_code] = {
            desc: row.desc,
            year: parseInt(row.year, 10),
            imports: { uganda: parseFloat(row.imports_uganda), eac: parseFloat(row.imports_eac) },
            exports: { uganda: parseFloat(row.exports_uganda), eac: parseFloat(row.exports_eac) },
          };
        }
        setLiveTradeVersion(v => v + 1);
      })
      .catch(() => {}); // static fallback stays active if PocketBase unreachable
  }, []);

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
                    onMouseEnter={(e) => setHoverInfo({ pid, rect: e.currentTarget.getBoundingClientRect() })}
                    onMouseLeave={() => setHoverInfo(null)}
                    style={{ width: "100%", textAlign: "left", padding: sidebarOpen ? "5px 12px" : "8px", background: selected === pid ? "#1e293b" : "transparent", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ width: "6px", height: "6px", borderRadius: "50%", backgroundColor: p.color, flexShrink: 0 }} />
                    {sidebarOpen && (
                      <span style={{ overflow: "hidden" }}>
                        <span style={{ display: "block", fontSize: "11px", color: selected === pid ? "#f1f5f9" : "#94a3b8", fontWeight: selected === pid ? "600" : "400", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{p.name}</span>
                        {PRODUCT_HS4[pid] && (
                          <span style={{ display: "block", fontSize: "9px", color: "#475569", marginTop: "1px" }}>
                            HS {PRODUCT_HS4[pid].replace(/_/g, " + ")}
                          </span>
                        )}
                      </span>
                    )}
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
                {product.tier || "Value Chain"} · {product.category}
              </div>
              <div style={{ display: "flex", alignItems: "baseline", gap: "10px", marginTop: "2px" }}>
                <div style={{ fontSize: "18px", fontWeight: "900", color: "#0f172a" }}>{product.name}</div>
                {PRODUCT_HS4[selected] && (
                  <div style={{ fontSize: "11px", fontWeight: "600", color: "#1565c0", background: "#e3f2fd", borderRadius: "4px", padding: "1px 7px", flexShrink: 0 }}>
                    HS {PRODUCT_HS4[selected].replace(/_/g, " + ")}
                  </div>
                )}
              </div>
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
            {(product.legend || []).map((item, i) => (
              <span key={i} style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "10px", color: "#94a3b8" }}>
                <span style={{ width: "10px", height: "10px", borderRadius: "2px", backgroundColor: item.color, flexShrink: 0 }} />
                {item.label}
              </span>
            ))}
          </div>
        </div>
      </div>

      {hoverInfo && (
        <ProductStatsPopup product={PRODUCTS[hoverInfo.pid]} hs4={PRODUCT_HS4[hoverInfo.pid]} anchorRect={hoverInfo.rect} />
      )}
    </div>
  );
}
