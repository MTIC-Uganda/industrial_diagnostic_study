"""
brief_lib — pure builder for the public Ask MIDD data brief (ADR-017/018).

Kept separate from app.py (no FastAPI import) so it is unit-testable. The brief is
the ONLY context the public chatbot gets: sanitized aggregates from PocketBase —
numbers + labels only, never people, company-level rows, or internal notes. That is
what stops the public bubble leaking names while still letting it answer data.
"""


# Friendly titles for the key_indicator_categories breakdown groups (the donut/strip cards).
CATEGORY_LABELS = {
    "tax": "Manufacturing tax contribution by sector",
    "credit": "Private sector credit by sector",
    "hightech": "High-tech / manufactured exports by category",
    "region_dist": "Manufacturing establishments by region",
}


def format_public_brief(chains, kpis, sector_counts, region_counts,
                        categories=None, macro=None):
    """PocketBase aggregates -> sanitized public brief text.

    chains:  list of {name, key_export_2024?, key_import_2024?, target_2040?}
    kpis:    list of {label, value, year?, source?/source_detail?}
    sector_counts / region_counts: {name: count}
    categories: list of {indicator_slug, category, pct, value_label?} — the dashboard's
                breakdown cards (tax/credit/hightech/region), grouped by indicator_slug.
    macro:      list of {label, fy2021_value?, fy2025_value?, delta?} — the momentum/trend cards.
    """
    lines = ["Scope: Uganda's priority manufacturing value chains covered by this dashboard."]
    for c in chains:
        parts = [c.get("name", "")]
        if c.get("key_export_2024"):
            parts.append(f"exports {c['key_export_2024']}")
        if c.get("key_import_2024"):
            parts.append(f"imports {c['key_import_2024']}")
        if c.get("target_2040"):
            parts.append(f"2040 target {c['target_2040']}")
        joined = ", ".join(p for p in parts if p)
        if joined:
            lines.append("- " + joined)

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
        if v21 and v25:
            body = f"{v21} (FY20/21) to {v25} (FY24/25)"
        else:
            body = v25 or v21
        if delta:
            body += f", change {delta}"
        lines.append(f"{label}: {body}.")

    return "\n".join(lines)
