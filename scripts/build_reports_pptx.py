"""
Build PowerPoint decks for the two full diagnostic reports.

Reuses the slide helpers in make_presentations.py for a consistent house style.
For each report: a title slide, then per value-chain a section divider plus
key content slides (findings, prioritized products, and the trade table where
present). Trade figures keep their inline ITC TradeMap citation.

Usage:
    python scripts/build_reports_pptx.py
Outputs:
    report/Report-1-Iron-Steel-Copper-Automotive.pptx
    report/Report-2-Textiles-Pharma-Petrochem-Sugar-Plastics-Cement.pptx
"""
import re
from pathlib import Path

import make_presentations as mp   # slide helpers + palette

BASE = Path(__file__).parent.parent
CH   = BASE / "report" / "chapters"


def strip_md(s):
    """Remove markdown emphasis/code markers for slide text."""
    s = re.sub(r'\*\*([^*]+)\*\*', r'\1', s)
    s = re.sub(r'\*([^*]+)\*', r'\1', s)
    s = re.sub(r'`([^`]+)`', r'\1', s)
    return s.strip()


def parse_chapter(path):
    """Return {title, sections:[{head, paras:[], bullets:[], tables:[[rows]]}]}."""
    lines = path.read_text(encoding="utf-8").split("\n")
    title = "Chapter"
    sections, cur = [], None
    tbuf = []

    def flush_table():
        nonlocal tbuf
        if cur is not None and tbuf:
            rows = [r for r in tbuf if not re.match(r'^\|[\s:|-]+\|?$', r.strip())]
            cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
            if len(cells) >= 2:
                cur["tables"].append(cells)
        tbuf = []

    for ln in lines:
        s = ln.rstrip("\n")
        if s.lstrip().startswith("|"):
            tbuf.append(s); continue
        flush_table()
        st = s.strip()
        if st.startswith("# "):
            title = strip_md(st[2:])
        elif st.startswith("## "):
            cur = {"head": strip_md(st[3:]), "paras": [], "bullets": [], "tables": []}
            sections.append(cur)
        elif st.startswith("### ") and cur is not None:
            cur["bullets"].append("▸ " + strip_md(st[4:]))
        elif (st.startswith("- ") or st.startswith("* ")) and cur is not None:
            cur["bullets"].append("•  " + strip_md(st[2:]))
        elif re.match(r'^\d+\.\s', st) and cur is not None:
            cur["bullets"].append(strip_md(st))
        elif st and not st.startswith(">") and st != "---" and cur is not None:
            if not st.startswith("**Report") and not st.startswith("**Status") \
               and not st.startswith("**Client") and not st.startswith("**Programme") \
               and not st.startswith("**Primary") and not st.startswith("**ToR"):
                cur["paras"].append(strip_md(st))
    flush_table()
    return {"title": title, "sections": sections}


def chunk(items, n):
    for i in range(0, len(items), n):
        yield items[i:i + n]


def add_chapter_slides(prs, ch, section_no):
    """One section divider + a few content/table slides per chapter."""
    mp.section_divider(prs, section_no, ch["title"])

    for sec in ch["sections"]:
        head = sec["head"]
        low = head.lower()

        # Tables (trade tables, scoring, action matrix) → table slides
        for tbl in sec["tables"]:
            headers = tbl[0]
            rows = tbl[1:]
            if not rows:
                continue
            # cap rows per slide for legibility
            for part in chunk(rows, 10):
                mp.table_slide(prs, f"{ch['title'].split(':')[0]} — {head}"[:70],
                               headers, part)

        # Narrative / bullets → content slides (cap lines per slide)
        body = []
        for p in sec["paras"]:
            # wrap long paragraphs into readable bullet lines
            body.append("•  " + p if not p.startswith(("•", "▸")) else p)
        body += sec["bullets"]
        body = [b for b in body if b.strip()]
        if body:
            for part in chunk(body, 8):
                mp.content_slide(prs, f"{ch['title'].split(':')[0]} — {head}"[:70], part)


def build(report_no, title, subtitle, chains, glob, out_name):
    prs = mp.new_prs()
    mp.title_slide(prs, title, subtitle, chains)
    files = sorted(CH.glob(glob))
    for i, f in enumerate(files, start=1):
        ch = parse_chapter(f)
        add_chapter_slides(prs, ch, i)
    out = BASE / "report" / out_name
    prs.save(out)
    return out, len(files), len(prs.slides._sldIdLst)


if __name__ == "__main__":
    out1, n1, s1 = build(
        1, "Industrial Diagnostic Study — Report 1",
        "Iron & Steel · Copper & Allied Metals · Automotive",
        ["Iron & Steel", "Copper & Allied Metals", "Automotive"],
        "report1-*.md",
        "Report-1-Iron-Steel-Copper-Automotive.pptx")
    print(f"Built {out1.name}: {n1} chapters, {s1} slides")

    out2, n2, s2 = build(
        2, "Industrial Diagnostic Study — Report 2",
        "Textiles · Pharma · Petrochemicals & Fertilizers · Sugar · Plastics · Cement",
        ["Textiles & Garments", "Pharmaceuticals", "Petrochemicals & Fertilizers",
         "Sugar & Confectionery", "Plastics & Packaging", "Cement & Building Materials"],
        "report2-*.md",
        "Report-2-Textiles-Pharma-Petrochem-Sugar-Plastics-Cement.pptx")
    print(f"Built {out2.name}: {n2} chapters, {s2} slides")
    print("Done.")
