"""
Wire ITC TradeMap CSVs into the graph nodes.

Reads the CSVs produced by industrial_diagnostic_study/scripts/trademap_fetch.py
(data/trademap/UGA_<hs>_<flow>_<date>.csv), summarises each, and stores the
result on every graph node whose hs_code matches.

After running, each node's detail panel shows live trade figures, cited to
ITC TradeMap (per the project rule that TradeMap data is cited at point of use).

Usage:
    python wire_trademap.py
"""
import csv
import glob
import json
import re
from pathlib import Path
from collections import defaultdict

import db

# CSVs live in the report repo's data folder
TRADEMAP_DIR = Path(__file__).parents[2] / "data" / "trademap"


def _num(s):
    s = (s or "").replace(",", "").strip()
    try:
        return float(s)
    except ValueError:
        return None


def parse_csv(path):
    """Return {'latest_year', 'world', 'top_partners':[(name,val)...]} in US$ thousand."""
    with open(path, encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        return None
    header = rows[0]
    # year columns: those containing a 4-digit year (20xx)
    year_cols = [(i, re.search(r"(20\d\d)", h).group(1))
                 for i, h in enumerate(header) if re.search(r"20\d\d", h)]
    if not year_cols:
        return None
    # pick the most recent year column by value, not position
    last_i, last_year = max(year_cols, key=lambda t: t[1])

    world = None
    partners = []
    for r in rows[1:]:
        if len(r) <= last_i:
            continue
        name = r[1].strip()
        val = _num(r[last_i])
        if not name:
            continue
        if name.lower() == "world":
            world = val
        elif val:
            partners.append((name, val))
    partners.sort(key=lambda x: -x[1])
    return {"latest_year": last_year, "world": world, "top_partners": partners[:3]}


def collect_by_hs():
    """Map hs_code -> {imports:..., exports:...} summaries."""
    out = defaultdict(dict)
    if not TRADEMAP_DIR.exists():
        print(f"No TradeMap dir at {TRADEMAP_DIR}")
        return out
    for path in glob.glob(str(TRADEMAP_DIR / "UGA_*_*.csv")):
        m = re.search(r"UGA_(\w+?)_(imports|exports)_", Path(path).name)
        if not m:
            continue
        hs, flow = m.group(1), m.group(2)
        parsed = parse_csv(path)
        if parsed:
            out[hs][flow] = parsed
    return out


def fmt_money(v):
    if v is None:
        return "n/a"
    if v >= 1000:
        return f"US${v/1000:.1f}m"
    return f"US${v:.0f}k"


def summarise(hs, data):
    parts = []
    imp, exp = data.get("imports"), data.get("exports")
    if imp:
        tp = ", ".join(n for n, _ in imp["top_partners"]) or "n/a"
        parts.append(f"Imports {fmt_money(imp['world'])} ({imp['latest_year']}), mainly {tp}")
    if exp:
        tp = ", ".join(n for n, _ in exp["top_partners"]) or "n/a"
        parts.append(f"Exports {fmt_money(exp['world'])} ({exp['latest_year']})"
                     + (f", to {tp}" if tp != "n/a" else ""))
    summary = "; ".join(parts)
    if summary:
        summary += f"  (Source: ITC TradeMap, HS {hs})"
    return summary


def run():
    by_hs = collect_by_hs()
    print(f"Parsed TradeMap data for HS codes: {sorted(by_hs.keys())}")

    conn = db.connect()
    nodes = conn.execute("SELECT id, hs_code FROM nodes").fetchall()
    updated = 0
    for n in nodes:
        if not n["hs_code"]:
            continue
        hs_list = json.loads(n["hs_code"])
        # CSVs are keyed by 4-digit HS heading; dataset codes may be 6-digit
        # subheadings (e.g. "7208.37"), so match on the 4-digit prefix.
        matched = {}
        for h in hs_list:
            key = re.sub(r"\D", "", str(h))[:4]
            if key in by_hs:
                matched[str(h)] = by_hs[key]
        if not matched:
            continue
        payload = {
            "source": "ITC TradeMap",
            "hs_codes": list(matched.keys()),
            "detail": matched,
            "summary": " | ".join(summarise(hs, d) for hs, d in matched.items()),
        }
        conn.execute("UPDATE nodes SET trademap_data = ? WHERE id = ?",
                     (json.dumps(payload, ensure_ascii=False), n["id"]))
        updated += 1
        print(f"  wired {n['id']}: {payload['summary'][:90]}")
    conn.commit()
    conn.close()
    print(f"Done. {updated} nodes updated with live TradeMap data.")


if __name__ == "__main__":
    run()
