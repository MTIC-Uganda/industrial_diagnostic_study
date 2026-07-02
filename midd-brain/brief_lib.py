"""
brief_lib — pure builder for the public Ask MIDD data brief (ADR-017/018).

Kept separate from app.py (no FastAPI import) so it is unit-testable. The brief is
the ONLY context the public chatbot gets: sanitized aggregates from PocketBase —
numbers + labels only, never people, company-level rows, or internal notes. That is
what stops the public bubble leaking names while still letting it answer data.
"""


def format_public_brief(chains, kpis, sector_counts, region_counts):
    """PocketBase aggregates -> sanitized public brief text.

    chains:  list of {name, key_export_2024?, key_import_2024?, target_2040?}
    kpis:    list of {label, value, year?, source?/source_detail?}
    sector_counts / region_counts: {name: count}
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
    return "\n".join(lines)
