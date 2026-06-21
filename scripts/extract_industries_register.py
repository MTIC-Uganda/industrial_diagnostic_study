#!/usr/bin/env python3
"""
One-off extraction script: parses data/manufacturing-overview/industries-register-aug2025.pdf
into structured JSON datasets for the Manufacturing Industry Distribution treemaps
(per Jerome's spec: "Spatial Distribution by region and district" + "Sector
Distribution by 2-digit/4-digit ISIC classification"):

  data/dashboard/treemap_district.json — Region -> District -> count (Spatial Distribution, used)
  data/dashboard/treemap_sector.json   — Sector -> Sub-sector -> count (Sector Distribution, used)
  data/dashboard/treemap_region.json   — Region -> Sector -> count (supplementary cross-tab, not
                                          currently rendered by the dashboard — kept since it's
                                          free to compute from the same pass and may be useful
                                          for future analysis)

Approach:
  1. The summary table (PDF pages 4-5) gives each sub-sector's starting "Ref Number"
     (the sequential row number where that sub-sector begins). Sub-sector boundaries
     are therefore [ref_number, next_sub-sector's ref_number - 1].
  2. The establishment listing (PDF pages 6-149) gives each establishment's sequential
     row number and District. Looking up which sub-sector range a row number falls
     into gives every establishment's Sector + Sub-sector.
  3. District is mapped to one of Uganda's 4 statistical regions (Central/Eastern/
     Northern/Western) via a hand-compiled lookup table.

Run once; output is committed to data/dashboard/ and the PDF is not re-parsed at
dashboard-generation time.
"""

import json
import re
from pathlib import Path

import pypdf

ROOT = Path(__file__).resolve().parent.parent
PDF  = ROOT / 'data' / 'manufacturing-overview' / 'industries-register-aug2025.pdf'
OUT  = ROOT / 'data' / 'dashboard'

# ── 1. Sub-sector boundaries (from the summary table, PDF pages 4-5) ──────────
# (sub_sector_no, sub_sector_name, ref_number_start, sector_no, sector_name)
SUBSECTORS = [
    (1,  "Meat", 1,    1, "Food Products"),
    (2,  "Fish", 87,   1, "Food Products"),
    (3,  "Fruits and Vegetables", 121, 1, "Food Products"),
    (4,  "Vegetable Oil, Animal Oil and Fats", 426, 1, "Food Products"),
    (5,  "Dairy products", 591, 1, "Food Products"),
    (6,  "Grain mill products", 794, 1, "Food Products"),
    (7,  "Starch and starch products", 1152, 1, "Food Products"),
    (8,  "Bakery Products", 1184, 1, "Food Products"),
    (9,  "Sugar", 1588, 1, "Food Products"),
    (10, "Cocoa, Chocolate and Sugar Confectionary", 1604, 1, "Food Products"),
    (11, "Macaroni and Noodles", 1653, 1, "Food Products"),
    (12, "Prepared meals and dishes", 1659, 1, "Food Products"),
    (13, "Other food products", 1664, 1, "Food Products"),
    (14, "Animal Feeds", 1835, 1, "Food Products"),
    (15, "Tea", 1865, 1, "Food Products"),
    (16, "Distilled and Blended spirits", 1953, 2, "Beverages"),
    (17, "Wines", 2313, 2, "Beverages"),
    (18, "Malt Liquors and Malt", 2510, 2, "Beverages"),
    (19, "Soft Drinks, Mineral Water and other waters", 2546, 2, "Beverages"),
    (20, "Tobacco Products", 3118, 3, "Tobacco"),
    (21, "Textiles", 3126, 4, "Textiles"),
    (22, "Tanning", 3147, 5, "Leather and Leather Products"),
    (23, "Luggage, Handbags, Saddlery And Harness", 3170, 5, "Leather and Leather Products"),
    (24, "Footwear", 3211, 5, "Leather and Leather Products"),
    (25, "Sawmilling", 3323, 6, "Wood and Wood Products"),
    (26, "Veneer", 3351, 6, "Wood and Wood Products"),
    (27, "Carpentry", 3356, 6, "Wood and Wood Products"),
    (28, "Wooden Containers", 3435, 6, "Wood and Wood Products"),
    (29, "Other wood products", 3440, 6, "Wood and Wood Products"),
    (30, "Furniture", 3537, 6, "Wood and Wood Products"),
    (31, "Pulp, Paper and Paperboard", 3594, 7, "Paper and Paper Products"),
    (32, "Corrugated paper and Paperboard", 3671, 7, "Paper and Paper Products"),
    (33, "Other articles of Paper", 3695, 7, "Paper and Paper Products"),
    (34, "Printing", 3817, 8, "Printing and Reproduction of Recorded Media"),
    (35, "Services related to Printing", 4460, 8, "Printing and Reproduction of Recorded Media"),
    (36, "Reproduction of recorded media", 4621, 8, "Printing and Reproduction of Recorded Media"),
    (37, "Refined Petroleum Products", 4625, 9, "Coke and Petroleum Products"),
    (38, "Fertilizers", 4718, 10, "Chemical and Chemical Products"),
    (39, "Pesticides and Agro chemicals", 4721, 10, "Chemical and Chemical Products"),
    (40, "Paints & Vanishes", 4747, 10, "Chemical and Chemical Products"),
    (41, "Soap & Detergents", 4864, 10, "Chemical and Chemical Products"),
    (42, "Other Chemical Products", 5369, 10, "Chemical and Chemical Products"),
    (43, "Man made Fibres", 5464, 10, "Chemical and Chemical Products"),
    (44, "Pharmaceuticals, Medicinal Chemical and Botanical Products", 5466, 11, "Pharmaceutical, Medical Chemicals and Botanical Products"),
    (45, "Tyres", 5564, 12, "Rubber and Plastic Products"),
    (46, "Other Rubber products", 5573, 12, "Rubber and Plastic Products"),
    (47, "Plastics", 5594, 12, "Rubber and Plastic Products"),
    (48, "Glass", 5930, 13, "Other Non-Metallic Mineral Products"),
    (49, "Refractory Products", 5950, 13, "Other Non-Metallic Mineral Products"),
    (50, "Clay building materials", 5952, 13, "Other Non-Metallic Mineral Products"),
    (51, "Porcelain & Ceramic", 6004, 13, "Other Non-Metallic Mineral Products"),
    (52, "Cement", 6010, 13, "Other Non-Metallic Mineral Products"),
    (53, "Concrete & Cement Products", 6031, 13, "Other Non-Metallic Mineral Products"),
    (54, "Stone", 6130, 13, "Other Non-Metallic Mineral Products"),
    (55, "Other non-metallic mineral products n.e.c.", 6138, 13, "Other Non-Metallic Mineral Products"),
    (56, "Iron & Steel", 6202, 14, "Basic Metals"),
    (57, "Basic precious and other non-ferrous metals", 6363, 14, "Basic Metals"),
    (58, "Iron & Steel Casting", 6375, 14, "Basic Metals"),
    (59, "Non Ferrous metals casting", 6393, 14, "Basic Metals"),
    (60, "Structural metal fabrication", 6396, 15, "Fabricated Metal Products Except Machinery and Equipment"),
    (61, "Tanks, reservoirs and containers of metal", 6527, 15, "Fabricated Metal Products Except Machinery and Equipment"),
    (62, "Steam generators, except central heating hot water boilers", 6534, 15, "Fabricated Metal Products Except Machinery and Equipment"),
    (63, "Forging, pressing, stamping and roll-forming of metal; powder metallurgy", 6536, 15, "Fabricated Metal Products Except Machinery and Equipment"),
    (64, "Treatment and coating of metals; machining", 6544, 15, "Fabricated Metal Products Except Machinery and Equipment"),
    (65, "Cutlery, hand tools and general hardware", 6550, 15, "Fabricated Metal Products Except Machinery and Equipment"),
    (66, "Other fabricated metal products", 6560, 15, "Fabricated Metal Products Except Machinery and Equipment"),
    (67, "Communication equipment", 6845, 16, "Computer, Electronic and Optical Products"),
    (68, "Electric motors, generators, transformers and electricity distribution and control apparatus", 6847, 17, "Electrical Equipment"),
    (69, "Batteries and accumulators", 6848, 17, "Electrical Equipment"),
    (70, "Fibre optical cables", 6859, 17, "Electrical Equipment"),
    (71, "Other electronic and electric wires and cables", 6861, 17, "Electrical Equipment"),
    (72, "Electric lighting equipment", 6876, 17, "Electrical Equipment"),
    (73, "Domestic Home Appliances", 6885, 17, "Electrical Equipment"),
    (74, "Other electrical equipment", 6892, 17, "Electrical Equipment"),
    (75, "Agricultural and forestry machinery", 6939, 18, "Machinery and Equipment"),
    (76, "Food, beverage and tobacco processing machinery", 6943, 18, "Machinery and Equipment"),
    (77, "Other special-purpose machinery", 6944, 18, "Machinery and Equipment"),
    (78, "Passenger motor vehicles (buses, coaches, trolleybuses)", 6947, 19, "Motor Vehicles, Trailers and Semi-Trailers"),
    (79, "Bodies (Coach Work) For Motor vehicles, Manufacture Of Trailers And Semi-Trailers", 6951, 19, "Motor Vehicles, Trailers and Semi-Trailers"),
    (80, "Parts and accessories for motor vehicles", 6957, 19, "Motor Vehicles, Trailers and Semi-Trailers"),
    (81, "Ships & floating structures", 6966, 20, "Other Transport Equipment"),
    (82, "Pleasure & sporting boats", 6967, 20, "Other Transport Equipment"),
    (83, "Air & Spacecraft", 6968, 20, "Other Transport Equipment"),
    (84, "Motorcycles", 6978, 20, "Other Transport Equipment"),
    (85, "Bicycles", 6988, 20, "Other Transport Equipment"),
    (86, "Other transport equipment", 6990, 20, "Other Transport Equipment"),
    (87, "Jewellery", 6995, 21, "Other Manufacturing"),
    (88, "Games & Toys", 6997, 21, "Other Manufacturing"),
    (89, "Medical & Dental instruments", 6999, 21, "Other Manufacturing"),
    (90, "Other Manufacturing", 7005, 21, "Other Manufacturing"),
]
TOTAL_EXPECTED = 7011

def subsector_for_row(row_no: int):
    """Binary-search-free linear scan (only 90 entries) for which sub-sector a row falls in."""
    match = SUBSECTORS[0]
    for s in SUBSECTORS:
        if s[2] <= row_no:
            match = s
        else:
            break
    return match  # (subsector_no, subsector_name, ref_start, sector_no, sector_name)

# ── 2. District -> Region lookup (Uganda's 4 statistical regions) ─────────────
REGION_MAP = {
    # Central
    'Kampala':'Central','Wakiso':'Central','Mukono':'Central','Mpigi':'Central',
    'Buikwe':'Central','Luwero':'Central','Nakaseke':'Central','Nakasongola':'Central',
    'Mityana':'Central','Mubende':'Central','Kiboga':'Central','Kyankwanzi':'Central',
    'Kayunga':'Central','Lyantonde':'Central','Rakai':'Central','Sembabule':'Central',
    'Ssembabule':'Central','Kalungu':'Central','Bukomansimbi':'Central','Gomba':'Central',
    'Butambala':'Central','Kalangala':'Central','Masaka':'Central','Mawokota':'Central',
    'Lwengo':'Central','Kassanda':'Central','Buvuma':'Central','Kiryandongo':'Central',
    # Eastern
    'Jinja':'Eastern','Mbale':'Eastern','Tororo':'Eastern','Busia':'Eastern',
    'Soroti':'Eastern','Iganga':'Eastern','Kamuli':'Eastern','Bugiri':'Eastern',
    'Pallisa':'Eastern','Kapchorwa':'Eastern','Kumi':'Eastern','Sironko':'Eastern',
    'Budaka':'Eastern','Butaleja':'Eastern','Manafwa':'Eastern','Namutumba':'Eastern',
    'Bukedea':'Eastern','Bukwo':'Eastern','Kaberamaido':'Eastern','Kaliro':'Eastern',
    'Mayuge':'Eastern','Namayingo':'Eastern','Serere':'Eastern','Amuria':'Eastern',
    'Ngora':'Eastern','Bulambuli':'Eastern','Kibuku':'Eastern','Luuka':'Eastern',
    'Buyende':'Eastern','Namisindwa':'Eastern','Katakwi':'Eastern','Soroti City':'Eastern',
    'Jinja City':'Eastern','Mbale City':'Eastern',
    # Northern
    'Gulu':'Northern','Lira':'Northern','Arua':'Northern','Kitgum':'Northern',
    'Pader':'Northern','Apac':'Northern','Nebbi':'Northern','Moyo':'Northern',
    'Adjumani':'Northern','Yumbe':'Northern','Kotido':'Northern','Moroto':'Northern',
    'Nakapiripirit':'Northern','Amuru':'Northern','Oyam':'Northern','Kole':'Northern',
    'Lamwo':'Northern','Agago':'Northern','Amolatar':'Northern','Dokolo':'Northern',
    'Otuke':'Northern','Alebtong':'Northern','Abim':'Northern','Kaabong':'Northern',
    'Amudat':'Northern','Napak':'Northern','Koboko':'Northern','Maracha':'Northern',
    'Zombo':'Northern','Pakwach':'Northern','Nwoya':'Northern','Omoro':'Northern',
    'Gulu City':'Northern','Lira City':'Northern','Arua City':'Northern','Terego':'Northern',
    'Madi-Okollo':'Northern','Obongi':'Northern','Karenga':'Northern','Kwania':'Northern',
    'Nabilatuk':'Northern','Karenga ':'Northern',
    # Western
    'Mbarara':'Western','Kabale':'Western','Kasese':'Western','Hoima':'Western',
    'Masindi':'Western','Bushenyi':'Western','Ntungamo':'Western','Rukungiri':'Western',
    'Kanungu':'Western','Kisoro':'Western','Kabarole':'Western','Kyenjojo':'Western',
    'Kibaale':'Western','Bundibugyo':'Western','Buliisa':'Western','Kiruhura':'Western',
    'Ibanda':'Western','Isingiro':'Western','Kamwenge':'Western','Kyegegwa':'Western',
    'Mitooma':'Western','Ntoroko':'Western','Rubirizi':'Western','Sheema':'Western',
    'Buhweju':'Western','Rukiga':'Western','Bunyangabu':'Western','Kagadi':'Western',
    'Kakumiro':'Western','Rubanda':'Western','Kazo':'Western','Kikuube':'Western',
    'Mbarara City':'Western','Fort Portal City':'Western','Kitagwenda':'Western',
    'Kagadi ':'Western', 'Rwampara':'Western','Mubende City':'Central',
    # Common alternate spellings / districts missing from the first pass —
    # found by checking unmatched rows against a phone-number-adjacency heuristic.
    'Luweero':'Central',       # alt spelling of Luwero (40 occurrences in source)
    'Kasanda':'Central',       # alt spelling of Kassanda
    'Kyotera':'Central',       # carved from Rakai
    'Bududa':'Eastern',
    'Kween':'Eastern',         # carved from Kapchorwa
}

ROW_RE = re.compile(r'^(\d+)\s+(.+)$')

def parse_pages(reader):
    """Yield (row_no, rest_of_line_text) for every establishment-listing row."""
    for page_idx in range(5, 149):  # PDF pages 6-149 (0-indexed 5-148)
        text = reader.pages[page_idx].extract_text()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            m = ROW_RE.match(line)
            if not m:
                continue
            row_no = int(m.group(1))
            if row_no < 1 or row_no > TOTAL_EXPECTED:
                continue
            yield row_no, m.group(2)

# Known multi-word districts that must be matched before single-word ones to
# avoid partial matches (e.g. "Fort Portal City" containing "Fort").
DISTRICT_NAMES_SORTED = sorted(REGION_MAP.keys(), key=len, reverse=True)

# Collapse alternate spellings to one canonical display name for the district
# treemap, so "Luweero" and "Luwero" don't show up as two separate cells.
CANONICAL_DISTRICT = {
    'Luweero': 'Luwero',
    'Kasanda': 'Kassanda',
}

def find_district(rest_text: str):
    for name in DISTRICT_NAMES_SORTED:
        if name.strip() and name in rest_text:
            return name.strip()
    return None

def main():
    reader = pypdf.PdfReader(PDF)

    sector_subsector_counts = {}   # sector_name -> {subsector_name: count}
    region_sector_counts = {}      # region -> {sector_name: count}  (kept for reference)
    region_district_counts = {}    # region -> {district_name: count}  (spatial treemap)
    unmatched_district_rows = 0
    seen_rows = set()

    for row_no, rest in parse_pages(reader):
        if row_no in seen_rows:
            continue  # duplicate extraction (shouldn't happen, but be safe)
        seen_rows.add(row_no)

        _, subsector_name, _, _, sector_name = subsector_for_row(row_no)

        sector_subsector_counts.setdefault(sector_name, {})
        sector_subsector_counts[sector_name][subsector_name] = \
            sector_subsector_counts[sector_name].get(subsector_name, 0) + 1

        district = find_district(rest)
        region = REGION_MAP.get(district) if district else None
        if not region:
            unmatched_district_rows += 1
            region = 'Unclassified'
            district_display = 'Unspecified'
        else:
            district_display = CANONICAL_DISTRICT.get(district, district)

        region_sector_counts.setdefault(region, {})
        region_sector_counts[region][sector_name] = \
            region_sector_counts[region].get(sector_name, 0) + 1

        region_district_counts.setdefault(region, {})
        region_district_counts[region][district_display] = \
            region_district_counts[region].get(district_display, 0) + 1

    total_rows = len(seen_rows)
    print(f'Parsed {total_rows} / {TOTAL_EXPECTED} expected establishment rows')
    print(f'Rows with unmatched district: {unmatched_district_rows} '
          f'({unmatched_district_rows/total_rows*100:.1f}%)')

    sector_total_check = sum(sum(v.values()) for v in sector_subsector_counts.values())
    region_total_check = sum(sum(v.values()) for v in region_sector_counts.values())
    print(f'Sector-tree total: {sector_total_check}, Region-tree total: {region_total_check}')

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'treemap_sector.json').write_text(
        json.dumps(sector_subsector_counts, indent=2, ensure_ascii=False), encoding='utf-8')
    (OUT / 'treemap_region.json').write_text(
        json.dumps(region_sector_counts, indent=2, ensure_ascii=False), encoding='utf-8')
    (OUT / 'treemap_district.json').write_text(
        json.dumps(region_district_counts, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Wrote treemap_sector.json, treemap_region.json, treemap_district.json to {OUT}')

if __name__ == '__main__':
    main()
