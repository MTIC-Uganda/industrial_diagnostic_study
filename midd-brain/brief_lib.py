"""
brief_lib — pure builder for the public Ask MIDD data brief (ADR-017/018).

Kept separate from app.py (no FastAPI import) so it is unit-testable. The brief is
the ONLY context the public chatbot gets: sanitized aggregates from PocketBase —
numbers + labels only, never people (owners/team), company-level rows, or internal
notes. That is what stops the public bubble leaking names while still letting it
answer about every card on the dashboard.
"""
import json

# Friendly titles for the key_indicator_categories breakdown groups (the donut/strip cards).
CATEGORY_LABELS = {
    "tax": "Manufacturing tax contribution by sector",
    "credit": "Private sector credit by sector",
    "hightech": "High-tech / manufactured exports by category",
    "region_dist": "Manufacturing establishments by region",
}


def _as_list(v):
    """A PocketBase multi-value field arrives as a list, a JSON string, or plain text."""
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x).strip() for x in v if str(x).strip()]
    if isinstance(v, str):
        s = v.strip()
        if s.startswith("["):
            try:
                p = json.loads(s)
                if isinstance(p, list):
                    return [str(x).strip() for x in p if str(x).strip()]
            except ValueError:
                pass
        return [s] if s else []
    return [str(v)]


def format_public_brief(chains, kpis, sector_counts, region_counts,
                        categories=None, macro=None, targets=None,
                        glossary=None, risks=None, milestones=None, synergies=None):
    """PocketBase aggregates -> sanitized public brief text (every dashboard card).

    chains:     list of value-chain dicts (name, trade, target, position/priority tags,
                and diagnostic lists: current/constraints/priorities + gap).
    kpis:       the 12 headline indicator cards {label, value, year?, source?}.
    sector_counts / region_counts: {name: count} establishment counts.
    categories: key_indicator_categories breakdown rows, grouped by indicator_slug.
    macro:      macro_trend momentum cards.
    targets:    kpi_indicators (the Tenfold-growth target bars).
    glossary / risks / milestones / synergies: the remaining reference cards. `risks`
                is rendered WITHOUT the owner field (no people).
    """
    lines = ["Scope: Uganda's priority manufacturing value chains covered by this dashboard."]

    for c in chains:
        head = [c.get("name", "")]
        if c.get("position_tag"):
            head.append(f"position: {c['position_tag']}")
        if c.get("priority_tag"):
            head.append(f"priority: {c['priority_tag']}")
        if c.get("key_export_2024"):
            head.append(f"exports {c['key_export_2024']}")
        if c.get("key_import_2024"):
            head.append(f"imports {c['key_import_2024']}")
        if c.get("target_2040"):
            head.append(f"2040 target {c['target_2040']}")
        joined = ", ".join(p for p in head if p)
        if joined:
            lines.append("- " + joined)
        for key, lbl in (("current", "current state"), ("constraints", "constraints"),
                         ("priorities", "priorities")):
            vals = _as_list(c.get(key))
            if vals:
                lines.append(f"  {lbl}: " + "; ".join(vals))
        if c.get("gap"):
            lines.append(f"  gap/opportunity: {c['gap']}")

    total = sum(sector_counts.values())
    if total:
        lines.append(f"Registered manufacturing establishments: {total:,}.")
    if region_counts:
        lines.append("By region: "
                     + "; ".join(f"{k}: {v:,}" for k, v in sorted(region_counts.items())) + ".")
    if sector_counts:
        top = sorted(sector_counts.items(), key=lambda kv: -kv[1])[:15]
        lines.append("By sector: " + "; ".join(f"{k}: {v:,}" for k, v in top) + ".")

    for r in kpis:
        label, val = r.get("label"), r.get("value")
        if label and val:
            src = r.get("source_detail") or r.get("source") or ""
            yr = f", {r['year']}" if r.get("year") else ""
            lines.append(f"{label}: {val}{yr}" + (f" (source: {src})" if src else "") + ".")

    # Breakdown cards (tax/credit/hightech/region), grouped by indicator.
    groups = {}
    for r in categories or []:
        groups.setdefault(r.get("indicator_slug"), []).append(r)
    for slug, rows in groups.items():
        segs = []
        for r in rows:
            cat, pct, vl = r.get("category"), r.get("pct"), r.get("value_label")
            if not cat:
                continue
            seg = f"{cat} {pct}%" if pct not in (None, "") else str(cat)
            if vl:
                seg += f" ({vl})"
            segs.append(seg)
        if segs:
            lines.append(f"{CATEGORY_LABELS.get(slug, slug)}: " + "; ".join(segs) + ".")

    # Momentum / trend cards.
    for r in macro or []:
        label = r.get("label")
        v21, v25, delta = r.get("fy2021_value"), r.get("fy2025_value"), r.get("delta")
        if not label or not (v21 or v25):
            continue
        body = f"{v21} (FY20/21) to {v25} (FY24/25)" if (v21 and v25) else (v25 or v21)
        if delta:
            body += f", change {delta}"
        lines.append(f"{label}: {body}.")

    # Tenfold-growth target bars.
    trows = [t for t in (targets or []) if t.get("label") and t.get("current_value")]
    if trows:
        lines.append("Tenfold growth targets (current -> NDP IV -> 2040):")
        for t in trows:
            path = " -> ".join(x for x in (t.get("current_value"), t.get("ndp_value"),
                                           t.get("tenfold_value")) if x)
            lines.append(f"- {t['label']}: {path}")

    # Reference cards.
    gterms = [g for g in (glossary or []) if g.get("term") and g.get("definition")]
    if gterms:
        lines.append("Glossary: " + "; ".join(f"{g['term']} = {g['definition']}" for g in gterms))

    rrows = [r for r in (risks or []) if r.get("risk")]
    if rrows:
        lines.append("Key risks:")
        for r in rrows:
            seg = f"- {r['risk']}"
            if r.get("severity"):
                seg += f" (severity {r['severity']})"
            if r.get("mitigation"):
                seg += f"; mitigation: {r['mitigation']}"
            lines.append(seg)

    mrows = [m for m in (milestones or []) if m.get("project")]
    if mrows:
        lines.append("Roadmap milestones:")
        for m in mrows:
            meta = " ".join(x for x in (m.get("year_label"), m.get("value_chain")) if x)
            status = f" ({m['status']})" if m.get("status") else ""
            lines.append(f"- {meta}: {m['project']}{status}".strip())

    srows = [s for s in (synergies or []) if s.get("title")]
    if srows:
        lines.append("Cross-chain synergies: "
                     + "; ".join(f"{s['title']}: {s.get('description', '')}" for s in srows))

    return "\n".join(lines)
