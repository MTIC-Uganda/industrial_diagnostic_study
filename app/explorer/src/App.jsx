import { useState, useEffect } from "react";
import { PRODUCTS, CATEGORIES, TRADE_HS4, PRODUCT_HS4, RAW_MATERIAL_TRADE, matchInputTrade, matchInputPhase, getInputWeight, PRODUCT_FIRMS, PHASE_PRODUCERS, PHASE_SOURCE, RAW_MATERIAL_PHASE } from "./data/index.js";

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

// Structure cache: populated by live PocketBase fetch; null fields fall back to
// the bundled static imports (offline / before the fetch completes).
const _liveStructure = {
  products: null,          // map slug → product object
  categories: null,        // array of category objects
  productFirms: null,      // map product_slug → firms entry
  phaseProducers: null,    // map phase key → producers entry
  productHs4: null,        // map slug → hs4 string
  matchTrade: null,        // function(text) → trade object | null
  matchPhase: null,        // function(text) → phase entry | null
  getKeywordWeight: null,  // function(text) → { essentiality, scarcity, weight } | null
};

function _resolveProducts()      { return _liveStructure.products      || PRODUCTS; }
function _resolveCategories()    { return _liveStructure.categories    || CATEGORIES; }
function _resolveProductFirms()  { return _liveStructure.productFirms  || PRODUCT_FIRMS; }
function _resolvePhaseProducers(){ return _liveStructure.phaseProducers|| PHASE_PRODUCERS; }
function _resolveProductHs4(slug){ return (_liveStructure.productHs4   || PRODUCT_HS4)[slug] || null; }
function _resolveMatchPhase(text){ return _liveStructure.matchPhase ? _liveStructure.matchPhase(text) : matchInputPhase(text); }
function _resolveGetInputWeight(text){ return _liveStructure.getKeywordWeight ? _liveStructure.getKeywordWeight(text) : getInputWeight(text); }

// Product-as-input fallback: if the text exactly names a product (e.g. "Cold Rolled Coil"
// appearing as an input), resolve its trade data via that product's HS code.
// This makes trade data consistent whether an item appears as a finished product or as an
// upstream input — same HS code, same ITC TradeMap figures.
function _resolveMatchTrade(text) {
  const byKeyword = _liveStructure.matchTrade ? _liveStructure.matchTrade(text) : matchInputTrade(text);
  if (byKeyword) return byKeyword;
  const normText = text.trim().toLowerCase();
  const prods = _resolveProducts();
  for (const slug of Object.keys(prods)) {
    if ((prods[slug].name || '').toLowerCase() === normText) {
      const hs4 = _resolveProductHs4(slug);
      if (hs4) return resolveTrade(hs4);
    }
  }
  return null;
}

function formatUsd(thousands) {
  if (thousands == null) return "—";
  const usd = thousands * 1000;
  if (usd >= 1_000_000) return `$${(usd / 1_000_000).toFixed(1)}m`;
  if (usd >= 1_000) return `$${(usd / 1_000).toFixed(0)}k`;
  return `$${usd}`;
}

// Traffic-light availability status for each input item.
// green  = domestic production confirmed (phase count > 0)
// orange = item is traded (HS-code matched) but no domestic producer identified
// red    = traded commodity but no domestic production or trade data — capacity gap
// utility = process utility (no HS code, not trade-tracked, e.g. steam/electricity)
const STATUS_COLOR = { green: "#22c55e", orange: "#f97316", red: "#ef4444", utility: "#64748b" };
const STATUS_ORDER = { red: 0, orange: 1, green: 2, utility: 3 };

function inputStatus(text) {
  const trade = _resolveMatchTrade(text);
  const phase = _resolveMatchPhase(text);
  if (!trade && !phase) return "utility";
  if (phase && phase.count > 0) return "green";
  if (trade) return "orange";
  return "red";
}

function TradeBlock({ trade, noDataLabel }) {
  return (
    <>
      <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "10px" }}>📦 Trade ({trade ? trade.year : "—"}, USD)</div>
      {trade ? (
        <>
          <div style={{ color: "#cbd5e1" }}>
            Imports — Uganda: <strong>{formatUsd(trade.imports.uganda)}</strong> · EAC: <strong>{formatUsd(trade.imports.eac)}</strong> · Global: <strong>{formatUsd(trade.imports.global)}</strong>
          </div>
          <div style={{ color: "#cbd5e1" }}>
            Exports — Uganda: <strong>{formatUsd(trade.exports.uganda)}</strong> · EAC: <strong>{formatUsd(trade.exports.eac)}</strong> · Global: <strong>{formatUsd(trade.exports.global)}</strong>
          </div>
          <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "4px" }}>{trade.desc}</div>
        </>
      ) : (
        <div style={{ color: "#94a3b8" }}>{noDataLabel}</div>
      )}
    </>
  );
}

// Persistent right-hand detail panel — replaces the hover tooltip.
// Participates in the flex layout so the main content compresses left rather than being obscured.
function SidePanel({ title, onClose, children }) {
  return (
    <div style={{
      width: "320px", flexShrink: 0,
      backgroundColor: "#0f172a", color: "#e2e8f0",
      boxShadow: "-8px 0 32px rgba(0,0,0,0.55)",
      display: "flex", flexDirection: "column",
      fontSize: "11px", lineHeight: 1.5,
    }}>
      <div style={{
        display: "flex", alignItems: "flex-start", justifyContent: "space-between",
        padding: "14px 14px 10px", borderBottom: "1px solid #1e293b", flexShrink: 0,
      }}>
        <div style={{ fontWeight: 700, fontSize: "13px", color: "#fff", flex: 1, paddingRight: "8px", lineHeight: 1.35 }}>{title}</div>
        <button onClick={onClose} style={{
          color: "#64748b", background: "none", border: "none", cursor: "pointer",
          fontSize: "18px", lineHeight: 1, flexShrink: 0, padding: "0 2px",
        }}>✕</button>
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: "12px 14px" }}>
        {children}
      </div>
    </div>
  );
}

function PhaseCountBlock({ phase }) {
  const p = _resolvePhaseProducers()[phase];
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

function PhaseContextNote({ phaseContext }) {
  if (!phaseContext) return null;
  const p = _resolvePhaseProducers()[phaseContext.phase];
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

// ─── Detail panel content components ────────────────────────────────────────
// These render the inner body of the SidePanel — no anchorRect, no positioning.

function ProductDetailPanel({ product, hs4, onClose }) {
  const trade = resolveTrade(hs4);
  const producers = _resolveProductFirms()[product.id];
  return (
    <SidePanel title={product.name} onClose={onClose}>
      <TradeBlock trade={trade} noDataLabel="Trade data not yet fetched for this product's HS code." />

      <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "10px" }}>🏭 Known producers</div>
      <ProducerBlock entry={producers} />

      <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "10px" }}>⚡ Total installed capacity</div>
      {producers?.capacity ? (
        <div style={{ color: "#cbd5e1" }}>{producers.capacity}</div>
      ) : (
        <div style={{ color: "#64748b", fontSize: "11px" }}>
          Capacity data per product is being compiled from the MTIC National Industries Register.
          {producers?.phaseContext && " Phase-level capacity is referenced in the producers section above."}
        </div>
      )}

      {producers?.currentCapacity && producers?.targetCapacity && (
        <>
          <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "10px" }}>📊 Capacity vs target</div>
          <div style={{ color: "#cbd5e1" }}>Current: <strong>{producers.currentCapacity}</strong></div>
          <div style={{ color: "#cbd5e1" }}>Target: <strong>{producers.targetCapacity}</strong></div>
          {producers.capacityGapNote && (
            <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "4px" }}>{producers.capacityGapNote}</div>
          )}
        </>
      )}

      {hs4 && (
        <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "6px" }}>
          HS code: <strong>{hs4.replace(/_/g, " + ")}</strong>
        </div>
      )}

      <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "8px", borderTop: "1px solid #1e293b", paddingTop: "6px" }}>
        Sources: ITC TradeMap (Uganda bilateral trade 2024) · {PHASE_SOURCE}
      </div>
    </SidePanel>
  );
}

function RawMaterialDetailPanel({ item, onClose }) {
  const trade = resolveRawTrade(item.name);
  const phase = RAW_MATERIAL_PHASE[item.name];
  return (
    <SidePanel title={item.name} onClose={onClose}>
      {item.detail && (
        <div style={{ color: "#94a3b8", fontSize: "10.5px", marginBottom: "8px" }}>{item.detail}</div>
      )}

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
    </SidePanel>
  );
}

function InputDetailPanel({ text, onClose }) {
  const trade = _resolveMatchTrade(text);
  const phase = _resolveMatchPhase(text);
  const wt = _resolveGetInputWeight(text);
  const status = inputStatus(text);
  const hasData = trade || phase;
  return (
    <SidePanel title={text} onClose={onClose}>
      {/* Priority signal */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginTop: "6px", marginBottom: "4px" }}>
        <span style={{ width: "10px", height: "10px", borderRadius: "50%", backgroundColor: STATUS_COLOR[status], flexShrink: 0 }} />
        <span style={{ fontSize: "10px", color: STATUS_COLOR[status], fontWeight: 700 }}>
          {status === "green" ? "Domestic production confirmed" :
           status === "orange" ? "Traded — no domestic producer identified" :
           status === "red" ? "Capacity gap — must build domestically" :
           "Process utility (not HS-traded)"}
        </span>
      </div>
      {wt && (
        <div style={{ backgroundColor: "#1e293b", borderRadius: "6px", padding: "8px 10px", marginBottom: "6px", fontSize: "10.5px" }}>
          <div style={{ color: "#93c5fd", fontWeight: 700, marginBottom: "4px" }}>
            ⚖️ Priority score: <strong style={{ color: "#fff" }}>{wt.weight}/100</strong>
          </div>
          <div style={{ display: "flex", gap: "16px", color: "#94a3b8" }}>
            <span>Essentiality: <strong style={{ color: "#e2e8f0" }}>{wt.essentiality}/10</strong></span>
            <span>Domestic scarcity: <strong style={{ color: "#e2e8f0" }}>{wt.scarcity}/10</strong></span>
          </div>
          <div style={{ color: "#475569", fontSize: "9.5px", marginTop: "4px" }}>
            score = essentiality × scarcity — higher = address first
          </div>
        </div>
      )}
      {hasData ? (
        <>
          <div style={{ fontWeight: 700, color: "#93c5fd", marginTop: "8px" }}>🏭 Industries &amp; capacity</div>
          {phase ? (
            <div style={{ color: "#cbd5e1" }}><strong>{phase.count} plants</strong> — {phase.label}</div>
          ) : (
            <div style={{ color: "#94a3b8" }}>
              This input is traded as a commodity but producer-count data is not separately tracked at this level —
              see the finished-product card for named plant operators.
            </div>
          )}
          <TradeBlock trade={trade} noDataLabel="No HS-code-specific trade data available for this input." />
          <div style={{ color: "#64748b", fontSize: "9.5px", marginTop: "8px", borderTop: "1px solid #1e293b", paddingTop: "6px" }}>
            {phase ? `Sources: ITC TradeMap (Uganda bilateral trade 2024) · ${PHASE_SOURCE}` : "Source: ITC TradeMap (Uganda bilateral trade 2024)"}
          </div>
        </>
      ) : (
        <div style={{ marginTop: "8px" }}>
          <div style={{ fontWeight: 700, color: "#94a3b8", marginBottom: "6px" }}>⚙️ Process utility</div>
          <div style={{ color: "#94a3b8", lineHeight: "1.55", fontSize: "10.5px" }}>
            This input is consumed on-site — electricity, water, steam, cooling, inert gases, tooling, or other
            plant-operating consumables. It doesn&apos;t generate a separate line in Uganda&apos;s bilateral goods
            trade statistics; its cost is embedded in the plant&apos;s operating expenditure rather than appearing
            as a discrete HS-classified import.
          </div>
        </div>
      )}
    </SidePanel>
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

// Inputs tab: colored availability dots (red/orange/green/grey) sorted worst-first.
// Technology/Skills tabs: plain accent-color dots, original order.
function ItemList({ items, color, onItemClick }) {
  const isInputs = !!onItemClick;

  const displayItems = isInputs
    ? [...(items || [])].sort((a, b) => {
        const sa = STATUS_ORDER[inputStatus(a)], sb = STATUS_ORDER[inputStatus(b)];
        if (sa !== sb) return sa - sb;
        // Within same status: higher essentiality × scarcity weight first
        const wa = _resolveGetInputWeight(a)?.weight ?? 0;
        const wb = _resolveGetInputWeight(b)?.weight ?? 0;
        return wb - wa;
      })
    : (items || []);

  return (
    <ul className="space-y-1 pt-1">
      {displayItems.map((item, i) => {
        const status = isInputs ? inputStatus(item) : null;
        const dotColor = isInputs ? STATUS_COLOR[status] : color;
        return (
          <li key={i}
            className={`text-xs flex items-start gap-1.5 text-slate-700${isInputs ? " cursor-pointer hover:text-slate-900 hover:bg-slate-50 rounded px-1 -mx-1 py-0.5" : ""}`}
            onClick={isInputs ? () => onItemClick(item) : undefined}
            title={isInputs ? "Click for trade data and capacity details" : undefined}>
            <span className="mt-1 shrink-0 w-1.5 h-1.5 rounded-full" style={{ backgroundColor: dotColor }} />
            {item}
          </li>
        );
      })}
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

function SimpleCard({ node, onItemClick }) {
  const [tab, setTab] = useState("inputs");
  return (
    <div className="rounded-lg overflow-hidden border border-slate-200 shadow-sm">
      <CardHeader stage={node.stage} label={node.label} color={node.color} textColor={node.textColor} />
      <div style={{ backgroundColor: node.color + "10" }}>
        <TabBar tab={tab} setTab={setTab} color={node.color} />
        <div className="px-3 py-2">
          <ItemList items={node[tab]} color={node.color} onItemClick={tab === "inputs" ? onItemClick : undefined} />
        </div>
      </div>
    </div>
  );
}

function DualCard({ node, onItemClick }) {
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
              <ItemList items={route[tab]} color={node.color} onItemClick={tab === "inputs" ? onItemClick : undefined} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function TripleCard({ node, onItemClick }) {
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
              <ItemList items={route[tab]} color={node.color} onItemClick={tab === "inputs" ? onItemClick : undefined} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function GroupCard({ node, onItemClick }) {
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
              <ItemList items={g[tab] || g.inputs} color={node.color} onItemClick={tab === "inputs" ? onItemClick : undefined} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function RawCard({ node, onItemClick }) {
  return (
    <div className="rounded-lg overflow-hidden border border-slate-200 shadow-sm">
      <CardHeader stage={node.stage} label={node.label} color={node.color} textColor={node.textColor} />
      <div className="divide-y divide-slate-200" style={{ backgroundColor: node.color + "10" }}>
        {node.items.map((item, i) => (
          <div key={i} className="px-3 py-2 flex items-start gap-2 cursor-pointer hover:bg-slate-50"
            onClick={() => onItemClick && onItemClick(item)}
            title="Click for trade and capacity details">
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

function NodeCard({ node, onItemClick }) {
  if (node.triple) return <TripleCard node={node} onItemClick={onItemClick} />;
  if (node.dual) return <DualCard node={node} onItemClick={onItemClick} />;
  if (node.groups) return <GroupCard node={node} onItemClick={onItemClick} />;
  if (node.rawMaterials) return <RawCard node={node} onItemClick={onItemClick} />;
  return <SimpleCard node={node} onItemClick={onItemClick} />;
}

function Chain({ chain, onItemClick }) {
  return (
    <div className="flex flex-col min-w-0">
      <div className="text-center text-xs font-bold tracking-wider uppercase py-1.5 px-3 rounded-lg mb-2"
        style={{ backgroundColor: chain.accent, color: "#fff" }}>
        {chain.title}
      </div>
      {chain.nodes.map((node, i) => (
        <div key={node.id || i}>
          <NodeCard node={node} onItemClick={onItemClick} />
          {i < chain.nodes.length - 1 && <Arrow color={chain.accent} />}
        </div>
      ))}
    </div>
  );
}

const CHAINS = [
  { id: "iron",      label: "Iron & Steel" },
  { id: "copper",    label: "Copper & Allied Metals" },
  { id: "auto",      label: "Automotive" },
  { id: "textiles",  label: "Textiles & Garments" },
  { id: "pharma",    label: "Pharmaceuticals" },
  { id: "petrochem", label: "Petrochemicals & Fertilizers" },
  { id: "sugar",     label: "Sugar & Confectionery" },
  { id: "plastics",  label: "Plastics & Packaging" },
  { id: "cement",    label: "Cement & Building Materials" },
];

function productChain(slug) {
  if (slug.startsWith("cu_")) return "copper";
  if (slug.startsWith("au_")) return "auto";
  if (slug.startsWith("tx_")) return "textiles";
  if (slug.startsWith("ph_")) return "pharma";
  if (slug.startsWith("pc_")) return "petrochem";
  if (slug.startsWith("sg_")) return "sugar";
  if (slug.startsWith("pl_")) return "plastics";
  if (slug.startsWith("cm_")) return "cement";
  return "iron";
}

// detailPanel shape:
//   null                                         → panel closed
//   { type: 'product', product, hs4 }            → product detail (from sidebar click)
//   { type: 'input',   text }                    → chain input detail (from card click)
//   { type: 'raw',     item: { name, detail } }  → raw material detail (from RawCard click)

export default function ValueChainExplorer() {
  const [selected, setSelected] = useState("galvanized");
  const [selectedChain, setSelectedChain] = useState("iron");
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [detailPanel, setDetailPanel] = useState(null);
  const [, setLiveVersion] = useState(0); // incremented after any live PocketBase fetch to trigger re-render

  function handleChainChange(chainId) {
    setSelectedChain(chainId);
    const firstCat = _resolveCategories().find(cat => cat.products.some(pid => productChain(pid) === chainId));
    if (firstCat) {
      const firstPid = firstCat.products.find(pid => productChain(pid) === chainId);
      if (firstPid) setSelected(firstPid);
    }
    setDetailPanel(null);
  }

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
            imports: { uganda: parseFloat(row.imports_uganda), eac: parseFloat(row.imports_eac), global: row.imports_global ? parseFloat(row.imports_global) : null },
            exports: { uganda: parseFloat(row.exports_uganda), eac: parseFloat(row.exports_eac), global: row.exports_global ? parseFloat(row.exports_global) : null },
          };
        }
        setLiveVersion(v => v + 1);
      })
      .catch(() => {}); // static fallback stays active if PocketBase unreachable
  }, []);

  // Fetch the five structure collections in parallel so any PocketBase edit
  // (product description, firm list, phase count, keyword rule) shows on refresh.
  // Static bundle stays active as an offline fallback until the fetch resolves.
  useEffect(() => {
    const base = pbUrl();
    Promise.all([
      fetch(`${base}/api/collections/explorer_products/records?perPage=500&sort=display_order`).then(r => r.json()),
      fetch(`${base}/api/collections/explorer_categories/records?perPage=500&sort=display_order`).then(r => r.json()),
      fetch(`${base}/api/collections/explorer_phase_producers/records?perPage=500&sort=display_order`).then(r => r.json()),
      fetch(`${base}/api/collections/explorer_product_firms/records?perPage=500&sort=display_order`).then(r => r.json()),
      fetch(`${base}/api/collections/explorer_input_keywords/records?perPage=500&sort=display_order`).then(r => r.json()),
    ]).then(([prodData, catData, ppData, pfData, kwData]) => {
      const products = {}, productHs4 = {};
      for (const row of prodData.items || []) {
        products[row.slug] = {
          id: row.slug, name: row.name, category: row.category,
          color: row.color, description: row.description, chains: row.chains || [],
        };
        if (row.hs4_code) productHs4[row.slug] = row.hs4_code;
      }
      const categories = (catData.items || []).map(row => ({
        slug: row.slug, name: row.name, color: row.color, products: row.products || [],
      }));
      const phaseProducers = {};
      for (const row of ppData.items || []) {
        phaseProducers[row.phase] = { count: row.count, label: row.label, examples: row.examples || [], source: row.source };
      }
      const productFirms = {};
      for (const row of pfData.items || []) {
        productFirms[row.product_slug] = {
          status: row.status, firms: row.firms || [], note: row.note,
          phaseContext: row.phase_context || null,
          currentCapacity: row.current_capacity || null,
          targetCapacity: row.target_capacity || null,
          capacityGapNote: row.capacity_gap_note || null,
        };
      }
      // keyword rows arrive pre-sorted by display_order; first match wins
      const keywords = kwData.items || [];
      _liveStructure.matchTrade = function(text) {
        for (const kw of keywords) {
          if (kw.target_type !== 'hs4') continue;
          try { if (new RegExp(kw.pattern_source, kw.pattern_flags || '').test(text)) return resolveTrade(kw.target_value); } catch {}
        }
        return null;
      };
      _liveStructure.matchPhase = function(text) {
        for (const kw of keywords) {
          if (kw.target_type !== 'phase') continue;
          try { if (new RegExp(kw.pattern_source, kw.pattern_flags || '').test(text)) return phaseProducers[kw.target_value] || null; } catch {}
        }
        return null;
      };
      _liveStructure.getKeywordWeight = function(text) {
        for (const kw of keywords) {
          try {
            if (new RegExp(kw.pattern_source, kw.pattern_flags || '').test(text)) {
              if (kw.essentiality && kw.scarcity)
                return { essentiality: kw.essentiality, scarcity: kw.scarcity, weight: kw.essentiality * kw.scarcity };
              return null;
            }
          } catch {}
        }
        return null;
      };
      _liveStructure.products      = products;
      _liveStructure.productHs4    = productHs4;
      _liveStructure.categories    = categories;
      _liveStructure.phaseProducers= phaseProducers;
      _liveStructure.productFirms  = productFirms;
      setLiveVersion(v => v + 1);
    }).catch(() => {}); // static bundle fallback stays active if PocketBase unreachable
  }, []);

  const product = _resolveProducts()[selected];

  function openInputPanel(item) {
    // item is either a string (input text) or a raw-material object { name, detail }
    if (typeof item === "string") {
      setDetailPanel({ type: "input", text: item });
    } else {
      setDetailPanel({ type: "raw", item });
    }
  }

  return (
    <div style={{ display: "flex", height: "100vh", backgroundColor: "#f8fafc", fontFamily: "system-ui, sans-serif", overflow: "hidden" }}>

      {/* Sidebar */}
      <div style={{ display: "flex", flexDirection: "column", backgroundColor: "#0f172a", width: sidebarOpen ? "200px" : "44px", flexShrink: 0, transition: "width 0.2s" }}>
        <div style={{ borderBottom: "1px solid #1e293b" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "10px 12px 6px" }}>
            {sidebarOpen && <span style={{ color: "#94a3b8", fontSize: "10px", fontWeight: "700", letterSpacing: "0.1em", textTransform: "uppercase" }}>Value Chain</span>}
            <button onClick={() => setSidebarOpen(!sidebarOpen)} style={{ color: "#94a3b8", background: "none", border: "none", cursor: "pointer", fontSize: "14px", marginLeft: "auto" }}>
              {sidebarOpen ? "◂" : "▸"}
            </button>
          </div>
          {sidebarOpen && (
            <div style={{ padding: "0 10px 10px" }}>
              <select
                value={selectedChain}
                onChange={e => handleChainChange(e.target.value)}
                style={{ width: "100%", backgroundColor: "#1e293b", color: "#e2e8f0", border: "1px solid #334155", borderRadius: "5px", padding: "5px 8px", fontSize: "11px", cursor: "pointer", outline: "none" }}
              >
                {CHAINS.map(c => (
                  <option key={c.id} value={c.id} style={{ backgroundColor: "#0f172a" }}>{c.label}</option>
                ))}
              </select>
            </div>
          )}
        </div>
        <div style={{ overflowY: "auto", flex: 1, paddingTop: "8px" }}>
          {_resolveCategories().filter(cat => cat.products.some(pid => productChain(pid) === selectedChain)).map((cat) => (
            <div key={cat.name} style={{ marginBottom: "12px" }}>
              {sidebarOpen && (
                <div style={{ padding: "2px 12px 4px", fontSize: "9px", fontWeight: "700", letterSpacing: "0.08em", textTransform: "uppercase", color: cat.color === "#1e4976" || cat.color === "#235991" || cat.color === "#1e3a8a" ? "#60a5fa" : cat.color === "#b45309" ? "#f59e0b" : cat.color === "#7c3aed" ? "#a78bfa" : "#94a3b8" }}>
                  {cat.name}
                </div>
              )}
              {cat.products.map((pid) => {
                const p = _resolveProducts()[pid];
                const hs4 = _resolveProductHs4(pid);
                return (
                  <button key={pid}
                    title={p.name}
                    onClick={() => {
                      setSelected(pid);
                      setDetailPanel({ type: "product", product: p, hs4 });
                    }}
                    style={{ width: "100%", textAlign: "left", padding: sidebarOpen ? "5px 12px" : "8px", background: selected === pid ? "#1e293b" : "transparent", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: "8px" }}>
                    <span style={{ width: "6px", height: "6px", borderRadius: "50%", backgroundColor: p.color, flexShrink: 0 }} />
                    {sidebarOpen && (
                      <span style={{ overflow: "hidden" }}>
                        <span style={{ display: "block", fontSize: "11px", color: selected === pid ? "#f1f5f9" : "#94a3b8", fontWeight: selected === pid ? "600" : "400", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{p.name}</span>
                        {hs4 && (
                          <span style={{ display: "block", fontSize: "9px", color: "#475569", marginTop: "1px" }}>
                            HS {hs4.replace(/_/g, " + ")}
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
                {_resolveProductHs4(selected) && (
                  <div style={{ fontSize: "11px", fontWeight: "600", color: "#1565c0", background: "#e3f2fd", borderRadius: "4px", padding: "1px 7px", flexShrink: 0 }}>
                    HS {_resolveProductHs4(selected).replace(/_/g, " + ")}
                  </div>
                )}
              </div>
              <div style={{ fontSize: "11px", color: "#64748b", marginTop: "2px", maxWidth: "600px" }}>{product.description}</div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", fontSize: "10px", color: "#94a3b8", flexShrink: 0, marginLeft: "16px", textAlign: "right" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "4px", justifyContent: "flex-end" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: STATUS_COLOR.green, flexShrink: 0 }} />
                <span>Domestic production confirmed</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "4px", justifyContent: "flex-end" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: STATUS_COLOR.orange, flexShrink: 0 }} />
                <span>Imported; no domestic producer</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "4px", justifyContent: "flex-end" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: STATUS_COLOR.red, flexShrink: 0 }} />
                <span>Capacity gap — must build</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "4px", justifyContent: "flex-end" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: STATUS_COLOR.utility, flexShrink: 0 }} />
                <span>Process utility (on-site)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Chains */}
        <div style={{ flex: 1, overflowY: "auto", padding: "16px" }}>
          <div style={{ display: "grid", gridTemplateColumns: product.chains.length === 1 ? "minmax(0,560px)" : `repeat(${product.chains.length}, minmax(0,1fr))`, gap: "20px", justifyContent: product.chains.length === 1 ? "center" : "stretch", margin: product.chains.length === 1 ? "0 auto" : "0" }}>
            {product.chains.map((chain, i) => (
              <Chain key={i} chain={chain} onItemClick={openInputPanel} />
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

      {/* Detail panel — click-to-open, persistent, closable */}
      {detailPanel && detailPanel.type === "product" && (
        <ProductDetailPanel
          product={detailPanel.product}
          hs4={detailPanel.hs4}
          onClose={() => setDetailPanel(null)}
        />
      )}
      {detailPanel && detailPanel.type === "input" && (
        <InputDetailPanel
          text={detailPanel.text}
          onClose={() => setDetailPanel(null)}
        />
      )}
      {detailPanel && detailPanel.type === "raw" && (
        <RawMaterialDetailPanel
          item={detailPanel.item}
          onClose={() => setDetailPanel(null)}
        />
      )}
    </div>
  );
}
