import React from "react";

// Detail panel mirroring valuechains.ai: function, mechanism, core components,
// HS codes, prevalence/price, sources.
function Section({ title, children }) {
  if (!children || (Array.isArray(children) && !children.length)) return null;
  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ fontWeight: 700, fontSize: 12, color: "#005ca8", textTransform: "uppercase", marginBottom: 4 }}>
        {title}
      </div>
      <div style={{ fontSize: 13, color: "#222", lineHeight: 1.5 }}>{children}</div>
    </div>
  );
}

function Flow({ label, f }) {
  if (!f) return null;
  const money = (v) =>
    v == null ? "n/a" : v >= 1000 ? `US$${(v / 1000).toFixed(1)}m` : `US$${Math.round(v)}k`;
  return (
    <div style={{ marginBottom: 6 }}>
      <b>{label} {f.latest_year}:</b> {money(f.world)} (world)
      {f.top_partners?.length ? (
        <ul style={{ margin: "2px 0 0", paddingLeft: 18 }}>
          {f.top_partners.map(([n, v], i) => (
            <li key={i}>{n}: {money(v)}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

function TradeMap({ data }) {
  const detail = data.detail || {};
  return (
    <div style={{ fontSize: 12.5 }}>
      {Object.entries(detail).map(([hs, d]) => (
        <div key={hs} style={{ marginBottom: 10, paddingBottom: 8, borderBottom: "1px solid #eee" }}>
          <div style={{ fontWeight: 600, marginBottom: 3 }}>HS {hs}</div>
          <Flow label="Imports" f={d.imports} />
          <Flow label="Exports" f={d.exports} />
        </div>
      ))}
      <div style={{ fontSize: 10.5, color: "#888", marginTop: 4 }}>
        Source: ITC TradeMap (Uganda), latest available year.
      </div>
    </div>
  );
}

export default function NodeDetail({ node, onClose }) {
  if (!node) return null;
  const p = node.properties;
  const hs = p.hs_code || [];
  const hsDesc = p.hs_code_description || [];

  return (
    <div style={{
      width: 360, borderLeft: "1px solid #e0e0e0", padding: 18,
      overflowY: "auto", height: "100%", background: "#fafbfc",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start" }}>
        <h2 style={{ fontSize: 18, margin: 0, color: "#002b5b" }}>{p.name}</h2>
        <button onClick={onClose} style={{ border: "none", background: "none", fontSize: 18, cursor: "pointer" }}>✕</button>
      </div>
      <div style={{ fontSize: 11, color: "#888", marginBottom: 14 }}>
        {node.labels.join(", ")}{p.component_type ? ` · ${p.component_type}` : ""}
      </div>

      <Section title="Synonyms">{(p.synonyms || []).join("; ")}</Section>
      <Section title="Function">{p.function}</Section>
      <Section title="Mechanism">{p.mechanism}</Section>
      <Section title="Specifications">{p.specifications}</Section>
      <Section title="Core components">
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          {(p.core_components || []).map((c, i) => <li key={i}>{c}</li>)}
        </ul>
      </Section>
      <Section title="Prevalence">{p.prevalence}</Section>
      <Section title="Price range">
        {p.price_range ? `${p.price_range} ${p.price_range_unit || ""}` : null}
      </Section>
      <Section title="HS codes">
        {hs.length ? (
          <ul style={{ margin: 0, paddingLeft: 18 }}>
            {hs.map((c, i) => <li key={i}><b>{c}</b>{hsDesc[i] ? ` — ${hsDesc[i]}` : ""}</li>)}
          </ul>
        ) : null}
      </Section>
      <Section title="Trade data (ITC TradeMap)">
        {p.trademap_data ? <TradeMap data={p.trademap_data} /> : <span style={{ color: "#aaa" }}>Trade data not yet available for this node.</span>}
      </Section>
      <Section title="Sources">
        <ul style={{ margin: 0, paddingLeft: 18 }}>
          {(p.source_references || []).slice(0, 6).map((s, i) => (
            <li key={i} style={{ wordBreak: "break-all" }}>
              {s.startsWith("http") ? <a href={s} target="_blank" rel="noreferrer">{s}</a> : s}
            </li>
          ))}
        </ul>
      </Section>
    </div>
  );
}
