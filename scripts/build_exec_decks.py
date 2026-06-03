"""
Build SHORT executive PowerPoint decks (~15-20 slides) for each report —
boardroom/Commissioner version, following Jerome's coaching: open with a
table of contents, lead with the core finding, one priorities table per chain,
cross-cutting actions, investment portfolio, and close with a clear ask.

Pulls the prioritized-products tables straight from the chapter markdown so
the numbers and inline citations stay consistent with the full report.

Usage:
    python scripts/build_exec_decks.py
Outputs:
    report/Report-1-Executive-Deck.pptx
    report/Report-2-Executive-Deck.pptx
"""
import re
from pathlib import Path

import make_presentations as mp

BASE = Path(__file__).parent.parent
CH   = BASE / "report" / "chapters"


def strip_md(s):
    s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
    s = re.sub(r'\*([^*]+)\*', r'\1', s)
    s = re.sub(r'`([^`]+)`', r'\1', s)
    return s.strip()


def first_priorities_table(path):
    """Return (headers, rows) of the first markdown table under a '.E' /
    'Prioritized Products' section, else None."""
    lines = path.read_text(encoding="utf-8").split("\n")
    in_prio = False
    tbuf = []
    for ln in lines:
        st = ln.strip()
        if st.startswith("## "):
            in_prio = ("prioritiz" in st.lower() or ".e " in st.lower()
                       or st.lower().endswith(".e"))
            if not in_prio and tbuf:
                break
        if in_prio and st.startswith("|"):
            tbuf.append(st)
        elif in_prio and tbuf and not st.startswith("|"):
            break
    rows = [r for r in tbuf if not re.match(r'^\|[\s:|-]+\|?$', r.strip())]
    cells = [[strip_md(c.strip()) for c in r.strip().strip("|").split("|")] for r in rows]
    if len(cells) >= 2:
        return cells[0], cells[1:]
    return None


def priorities_summary(path):
    """Pull the bolded 'priorities for X' list lines from a chapter, if any."""
    out = []
    for ln in path.read_text(encoding="utf-8").split("\n"):
        m = re.match(r'^\d+\.\s+\*\*([^*]+)\*\*\s*(.*)$', ln.strip())
        if m:
            tail = strip_md(m.group(2))
            tail = tail[:90] + ("…" if len(tail) > 90 else "")
            out.append(f"{len(out)+1}.  {m.group(1)} — {tail}" if tail else f"{len(out)+1}.  {m.group(1)}")
        if len(out) >= 4:
            break
    return out


def build(title, subtitle, chains, chapter_specs, toc, core_finding,
          cross_cutting, investment, ask, out_name):
    prs = mp.new_prs()
    mp.title_slide(prs, title, subtitle, chains)

    # 1. Table of contents (Jerome: always open with one)
    mp.content_slide(prs, "What this deck covers", toc)

    # 2. The core finding
    mp.content_slide(prs, "The core finding", core_finding)

    # 3. One priorities slide per chain
    for label, fname in chapter_specs:
        path = CH / fname
        if not path.exists():
            continue
        tbl = first_priorities_table(path)
        if tbl:
            headers, rows = tbl
            mp.table_slide(prs, f"{label} — Prioritized products", headers, rows[:8])
        else:
            summ = priorities_summary(path) or ["See full report chapter."]
            mp.content_slide(prs, f"{label} — Priorities", summ)

    # 4. Cross-cutting actions
    mp.content_slide(prs, "Cross-cutting priority actions", cross_cutting)

    # 5. Investment portfolio
    mp.content_slide(prs, "Investment portfolio", investment)

    # 6. The ask (Jerome: close with a clear ask)
    mp.section_divider(prs, "", "The Ask", ask)

    out = BASE / "report" / out_name
    prs.save(out)
    return out, len(prs.slides._sldIdLst)


# ── Report 1 ────────────────────────────────────────────────────────────────
R1 = build(
    "Industrial Diagnostic Study — Report 1",
    "Iron & Steel · Copper & Allied Metals · Automotive",
    ["Iron & Steel", "Copper & Allied Metals", "Automotive"],
    [("Iron & Steel", "report1-04-iron-steel.md"),
     ("Copper & Allied Metals", "report1-05-copper-allied-metals.md"),
     ("Automotive", "report1-06-automotive.md")],
    toc=[
        "•  The core finding across the three metal value chains",
        "•  Prioritized products: Iron & Steel, Copper, Automotive",
        "•  Cross-cutting priority actions",
        "•  Investment portfolio and roadmap",
        "•  The ask",
    ],
    core_finding=[
        "Uganda exports raw and imports finished — the value leaks out at every stage.",
        "",
        "•  Iron ore exported raw (USD 35.8m, 2024) while flat steel is imported (USD 219.5m).  (ITC TradeMap)",
        "•  Copper: Kilembe dormant; insulated cable imported (USD 57.7m, 2024).  (ITC TradeMap)",
        "•  Vehicles: ~48,700 used vehicles imported a year; Kiira plant now commissioned (Sept 2025).",
        "",
        "The opportunity in every chain: move upstream, substitute imports, add value.",
    ],
    cross_cutting=[
        "1.  Enforce UNBS standards against substandard metal imports (quick win).",
        "2.  Retain feedstock — tax/limit raw iron-ore and scrap leakage.",
        "3.  Power agreements for heavy industrial loads (steel, smelting).",
        "4.  Long-term industrial finance facility.",
        "5.  Metallurgy & process-engineering skills compact (68% of manufacturers report skills gaps).",
        "6.  Sequence the integrated ore → DRI → steel → product pathway.",
    ],
    investment=[
        "Indicative portfolio (figures indicative, pending feasibility):",
        "",
        "•  Integrated steel (ore→DRI→flat/long): ~USD 0.5–1.0bn — Devki/Tembo anchors.",
        "•  Flat-rolling mill to substitute HS 7208 imports.",
        "•  Kilembe copper cathode + cobalt (production-sharing, Mar 2025).",
        "•  Cable & conductor expansion.",
        "•  Automotive assembly scale-up (Kiira) + parts localisation.",
    ],
    ask=("Endorse the prioritized products, approve the cross-cutting actions, "
         "and mandate the investment roadmap for partner mobilization."),
    out_name="Report-1-Executive-Deck.pptx",
)
print(f"Built {R1[0].name}: {R1[1]} slides")

# ── Report 2 ────────────────────────────────────────────────────────────────
R2 = build(
    "Industrial Diagnostic Study — Report 2",
    "Textiles · Pharma · Petrochemicals & Fertilizers · Sugar · Plastics · Cement",
    ["Textiles & Garments", "Pharmaceuticals", "Petrochemicals & Fertilizers",
     "Sugar & Confectionery", "Plastics & Packaging", "Cement & Building Materials"],
    [("Textiles & Garments", "report2-04-textiles-garments.md"),
     ("Pharmaceuticals", "report2-05-pharmaceuticals.md"),
     ("Petrochemicals & Fertilizers", "report2-06-petrochemicals-fertilizers.md"),
     ("Sugar & Confectionery", "report2-07-sugar-confectionery.md"),
     ("Plastics & Packaging", "report2-08-plastics-packaging.md"),
     ("Cement & Building Materials", "report2-09-cement-building-materials.md")],
    toc=[
        "•  The core finding across the six value chains",
        "•  Prioritized products for each of the six chains",
        "•  Cross-cutting priority actions",
        "•  Investment portfolio and roadmap",
        "•  The ask",
    ],
    core_finding=[
        "Uganda under-processes raw inputs and imports the finished product.",
        "",
        "•  Textiles: ~90% of cotton lint exported raw; only two integrated mills.",
        "•  Pharma: ~90% of medicines imported (USD 263.4m) — but a proven GMP base.",
        "•  Fertilizer: Sukulu plant stalled; ~1m t needed, ~50,000 t imported.",
        "•  Sugar: structural surplus — the value is downstream (industrial sugar, ethanol).",
        "•  Plastics & cement: net importer of packaging and clinker (USD 162m).  (ITC TradeMap)",
    ],
    cross_cutting=[
        "1.  Favour domestic value addition over raw export / finished import.",
        "2.  Enforce UNBS & NDA standards (highest-leverage quick win).",
        "3.  Anchor demand via public procurement (medicines, uniforms, cement, fertilizer).",
        "4.  Parks, utilities, effluent & circular-economy infrastructure.",
        "5.  Long-term industrial-finance facility.",
        "6.  Cross-sector skills compact.",
        "7.  Sequence the petrochemical park and its downstream linkages.",
    ],
    investment=[
        "Indicative portfolio (figures indicative, pending feasibility):",
        "",
        "•  ~USD 0.6–1.3bn over five years (excl. the ~USD 4bn investor-led refinery).",
        "•  Highest-certainty: sugar downstream, plastics recycling, cement clinker, GMP generics.",
        "•  Refinery + Kabalega petrochemical park = medium-term feedstock anchor (~2029–30).",
        "•  Majority private-led; public/PPP support in standards, skills, finance, procurement.",
    ],
    ask=("Endorse the prioritized products, approve the seven cross-cutting "
         "actions, and mandate the investment roadmap for partner mobilization."),
    out_name="Report-2-Executive-Deck.pptx",
)
print(f"Built {R2[0].name}: {R2[1]} slides")
print("Done.")
