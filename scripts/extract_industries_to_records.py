#!/usr/bin/env python3
"""
Extract individual industry records from the Uganda Industries Register PDF.

Outputs:  data/dashboard/industries.json  — one JSON object per establishment (7,011 total)

This file feeds db/seed_industries.py, which loads records into PocketBase.
PocketBase is the SINGLE SOURCE OF TRUTH for all manufacturing establishment data;
the dashboard reads from there, never from this JSON directly.

Usage:
    pip install pypdf
    python scripts/extract_industries_to_records.py
"""

import json
import re
from pathlib import Path

import pypdf

ROOT = Path(__file__).resolve().parent.parent
PDF  = ROOT / 'data' / 'manufacturing-overview' / 'industries-register-aug2025.pdf'
OUT  = ROOT / 'data' / 'dashboard' / 'industries.json'

# ── Sub-sector → Sector classification (from PDF summary table, pages 4-5) ────
# (subsector_no, subsector_name, ref_start, sector_no, sector_name)
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
    match = SUBSECTORS[0]
    for s in SUBSECTORS:
        if s[2] <= row_no:
            match = s
        else:
            break
    return match  # (subsector_no, name, ref_start, sector_no, sector_name)


# ── District → Region ─────────────────────────────────────────────────────────
REGION_MAP = {
    # Central
    'Kampala': 'Central', 'Wakiso': 'Central', 'Mukono': 'Central', 'Mpigi': 'Central',
    'Buikwe': 'Central', 'Luwero': 'Central', 'Nakaseke': 'Central', 'Nakasongola': 'Central',
    'Mityana': 'Central', 'Mubende': 'Central', 'Kiboga': 'Central', 'Kyankwanzi': 'Central',
    'Kayunga': 'Central', 'Lyantonde': 'Central', 'Rakai': 'Central', 'Sembabule': 'Central',
    'Ssembabule': 'Central', 'Kalungu': 'Central', 'Bukomansimbi': 'Central', 'Gomba': 'Central',
    'Butambala': 'Central', 'Kalangala': 'Central', 'Masaka': 'Central', 'Mawokota': 'Central',
    'Lwengo': 'Central', 'Kassanda': 'Central', 'Buvuma': 'Central', 'Kiryandongo': 'Central',
    'Mubende City': 'Central',
    # Eastern
    'Jinja': 'Eastern', 'Mbale': 'Eastern', 'Tororo': 'Eastern', 'Busia': 'Eastern',
    'Soroti': 'Eastern', 'Iganga': 'Eastern', 'Kamuli': 'Eastern', 'Bugiri': 'Eastern',
    'Pallisa': 'Eastern', 'Kapchorwa': 'Eastern', 'Kumi': 'Eastern', 'Sironko': 'Eastern',
    'Budaka': 'Eastern', 'Butaleja': 'Eastern', 'Manafwa': 'Eastern', 'Namutumba': 'Eastern',
    'Bukedea': 'Eastern', 'Bukwo': 'Eastern', 'Kaberamaido': 'Eastern', 'Kaliro': 'Eastern',
    'Mayuge': 'Eastern', 'Namayingo': 'Eastern', 'Serere': 'Eastern', 'Amuria': 'Eastern',
    'Ngora': 'Eastern', 'Bulambuli': 'Eastern', 'Kibuku': 'Eastern', 'Luuka': 'Eastern',
    'Buyende': 'Eastern', 'Namisindwa': 'Eastern', 'Katakwi': 'Eastern',
    'Soroti City': 'Eastern', 'Jinja City': 'Eastern', 'Mbale City': 'Eastern',
    'Bududa': 'Eastern', 'Kween': 'Eastern',
    # Northern
    'Gulu': 'Northern', 'Lira': 'Northern', 'Arua': 'Northern', 'Kitgum': 'Northern',
    'Pader': 'Northern', 'Apac': 'Northern', 'Nebbi': 'Northern', 'Moyo': 'Northern',
    'Adjumani': 'Northern', 'Yumbe': 'Northern', 'Kotido': 'Northern', 'Moroto': 'Northern',
    'Nakapiripirit': 'Northern', 'Amuru': 'Northern', 'Oyam': 'Northern', 'Kole': 'Northern',
    'Lamwo': 'Northern', 'Agago': 'Northern', 'Amolatar': 'Northern', 'Dokolo': 'Northern',
    'Otuke': 'Northern', 'Alebtong': 'Northern', 'Abim': 'Northern', 'Kaabong': 'Northern',
    'Amudat': 'Northern', 'Napak': 'Northern', 'Koboko': 'Northern', 'Maracha': 'Northern',
    'Zombo': 'Northern', 'Pakwach': 'Northern', 'Nwoya': 'Northern', 'Omoro': 'Northern',
    'Gulu City': 'Northern', 'Lira City': 'Northern', 'Arua City': 'Northern',
    'Terego': 'Northern', 'Madi-Okollo': 'Northern', 'Obongi': 'Northern',
    'Karenga': 'Northern', 'Kwania': 'Northern', 'Nabilatuk': 'Northern',
    # Western
    'Mbarara': 'Western', 'Kabale': 'Western', 'Kasese': 'Western', 'Hoima': 'Western',
    'Masindi': 'Western', 'Bushenyi': 'Western', 'Ntungamo': 'Western', 'Rukungiri': 'Western',
    'Kanungu': 'Western', 'Kisoro': 'Western', 'Kabarole': 'Western', 'Kyenjojo': 'Western',
    'Kibaale': 'Western', 'Bundibugyo': 'Western', 'Buliisa': 'Western', 'Kiruhura': 'Western',
    'Ibanda': 'Western', 'Isingiro': 'Western', 'Kamwenge': 'Western', 'Kyegegwa': 'Western',
    'Mitooma': 'Western', 'Ntoroko': 'Western', 'Rubirizi': 'Western', 'Sheema': 'Western',
    'Buhweju': 'Western', 'Rukiga': 'Western', 'Bunyangabu': 'Western', 'Kagadi': 'Western',
    'Kakumiro': 'Western', 'Rubanda': 'Western', 'Kazo': 'Western', 'Kikuube': 'Western',
    'Mbarara City': 'Western', 'Fort Portal City': 'Western', 'Kitagwenda': 'Western',
    'Rwampara': 'Western',
    # Alternate spellings
    'Luweero': 'Central', 'Kasanda': 'Central', 'Kyotera': 'Central',
}

CANONICAL_DISTRICT = {
    'Luweero': 'Luwero',
    'Kasanda': 'Kassanda',
}

# ── ISIC Rev. 4 two-digit division descriptions ───────────────────────────────
ISIC_2DIGIT_DESC = {
    '10': 'Manufacture of food products',
    '11': 'Manufacture of beverages',
    '12': 'Manufacture of tobacco products',
    '13': 'Manufacture of textiles',
    '14': 'Manufacture of wearing apparel',
    '15': 'Manufacture of leather and related products',
    '16': 'Manufacture of wood and products of wood and cork, except furniture',
    '17': 'Manufacture of paper and paper products',
    '18': 'Printing and reproduction of recorded media',
    '19': 'Manufacture of coke and refined petroleum products',
    '20': 'Manufacture of chemicals and chemical products',
    '21': 'Manufacture of basic pharmaceutical products and pharmaceutical preparations',
    '22': 'Manufacture of rubber and plastics products',
    '23': 'Manufacture of other non-metallic mineral products',
    '24': 'Manufacture of basic metals',
    '25': 'Manufacture of fabricated metal products, except machinery and equipment',
    '26': 'Manufacture of computer, electronic and optical products',
    '27': 'Manufacture of electrical equipment',
    '28': 'Manufacture of machinery and equipment n.e.c.',
    '29': 'Manufacture of motor vehicles, trailers and semi-trailers',
    '30': 'Manufacture of other transport equipment',
    '31': 'Manufacture of furniture',
    '32': 'Other manufacturing',
    '33': 'Repair and installation of machinery and equipment',
}

# Fallback: sector_no → ISIC 2-digit (used when PDF embeds no 4-digit header before a row)
SECTOR_TO_ISIC2 = {
    1: '10', 2: '11', 3: '12', 4: '13', 5: '15', 6: '16', 7: '17',
    8: '18', 9: '19', 10: '20', 11: '21', 12: '22', 13: '23', 14: '24',
    15: '25', 16: '26', 17: '27', 18: '28', 19: '29', 20: '30', 21: '32',
}

# ── Regexes ───────────────────────────────────────────────────────────────────
# Establishment row: row-number + 1+ spaces + rest of text
ROW_RE = re.compile(r'^(\d+)\s+(.+)$')

# ISIC 4-digit section header: exactly 4 digits immediately followed by dash/en-dash
# e.g. "1010-Processing and Preserving of Meat and Meat Products"
ISIC_HEAD_RE = re.compile(r'^(\d{4})[–\-]\s*(.+)')

# GPS decimal degrees: two floats matching Uganda's bounding box (lat -2..5, lng 29..36)
GPS_RE = re.compile(r'(-?\d{1,2}\.\d{4,})\s*[,/\s]+\s*(\d{2,3}\.\d{4,})')

# Phone numbers (Uganda: +256xxx, 07xx, 03xx, or plain 10-12 digit runs)
PHONE_RE = re.compile(r'(\+?256[\s\-]?\d[\d\s\-]{7,}|\+?0[37][\d\s\-]{7,}|\b\d{10,12}\b)')

# Longest-first so multi-word district names (e.g. "Fort Portal City") match before "Fort"
DISTRICT_NAMES_SORTED = sorted(
    (k for k in REGION_MAP if k.strip()),
    key=len, reverse=True,
)


def find_district(text: str):
    for name in DISTRICT_NAMES_SORTED:
        if name in text:
            return name
    return None


def extract_gps(text: str):
    """Return (lat, lng, text_with_gps_removed). Validates Uganda bounding box."""
    m = GPS_RE.search(text)
    if not m:
        return None, None, text
    try:
        lat = float(m.group(1))
        lng = float(m.group(2))
        if not (-2.0 <= lat <= 5.0) or not (29.0 <= lng <= 36.0):
            return None, None, text
        cleaned = (text[:m.start()] + ' ' + text[m.end():]).strip()
        return lat, lng, cleaned
    except (ValueError, IndexError):
        return None, None, text


def extract_phone(text: str):
    """Return (normalised_phone, text_with_phone_removed)."""
    m = PHONE_RE.search(text)
    if not m:
        return None, text
    phone = re.sub(r'[\s\-]', '', m.group(1))
    cleaned = (text[:m.start()] + ' ' + text[m.end():]).strip()
    return phone, cleaned


def main():
    reader  = pypdf.PdfReader(PDF)
    records: dict[int, dict] = {}

    cur_isic4      = None
    cur_isic4_desc = None

    # Pages 6-149 in PDF (0-indexed: 5-148) contain the establishment listing
    for page_idx in range(5, 149):
        page_text = reader.pages[page_idx].extract_text() or ''
        for line in page_text.splitlines():
            line = line.strip()
            if not line:
                continue

            # ── ISIC 4-digit header (check before ROW_RE) ──────────────────
            hm = ISIC_HEAD_RE.match(line)
            if hm:
                cur_isic4      = hm.group(1)
                cur_isic4_desc = hm.group(2).strip()
                # Strip parenthetical ISIC notes like "(ISIC 1010)"
                cur_isic4_desc = re.sub(r'\s*\(.*?\)\s*$', '', cur_isic4_desc).strip()
                continue

            # ── Establishment row ──────────────────────────────────────────
            rm = ROW_RE.match(line)
            if not rm:
                continue

            row_no = int(rm.group(1))
            if not (1 <= row_no <= TOTAL_EXPECTED):
                continue
            if row_no in records:
                continue  # deduplicate (PDF sometimes repeats header rows across page breaks)

            rest = rm.group(2).strip()

            # Extract structured fields from the flattened row text
            lat, lng, rest   = extract_gps(rest)
            contact, rest    = extract_phone(rest)
            district_raw     = find_district(rest)

            if district_raw:
                district = CANONICAL_DISTRICT.get(district_raw, district_raw).strip()
                region   = REGION_MAP.get(district_raw.strip(), 'Unclassified')
                rest     = rest.replace(district_raw, '', 1).strip()
            else:
                district = ''
                region   = 'Unclassified'

            name_products = re.sub(r'\s+', ' ', rest).strip()

            # Classification
            ss_no, ss_name, _, sector_no, sector_name = subsector_for_row(row_no)

            # ISIC codes — use PDF header if available; fall back to sector lookup
            isic_4      = cur_isic4 or ''
            isic_4_desc = cur_isic4_desc or ''
            isic_2      = isic_4[:2] if isic_4 else (SECTOR_TO_ISIC2.get(sector_no) or '')
            isic_2_desc = ISIC_2DIGIT_DESC.get(isic_2, '')

            records[row_no] = {
                'reg_number':       f'NIR-2025-{row_no:06d}',
                'row_no':           row_no,
                'name_products':    name_products,   # raw combined text; split manually in PocketBase
                'name':             '',              # editable: industry name (split from name_products)
                'products':         '',              # editable: specific products
                'district':         district,
                'region':           region,
                'contact':          contact or '',
                'latitude':         lat,
                'longitude':        lng,
                'isic_4digit':      isic_4,
                'isic_4digit_desc': isic_4_desc,
                'isic_2digit':      isic_2,
                'isic_2digit_desc': isic_2_desc,
                'subsector_num':    ss_no,
                'subsector_name':   ss_name,
                'sector_num':       sector_no,
                'sector_name':      sector_name,
                'status':           'active',
                'source':           'Uganda Industries Register Aug 2025',
                'notes':            '',
            }

    out_list = [records[k] for k in sorted(records.keys())]
    total    = len(out_list)

    no_district = sum(1 for r in out_list if not r['district'])
    no_isic4    = sum(1 for r in out_list if not r['isic_4digit'])
    no_gps      = sum(1 for r in out_list if r['latitude'] is None)
    missing_nos = sorted(set(range(1, TOTAL_EXPECTED + 1)) - set(records.keys()))

    print(f'Extracted  {total} / {TOTAL_EXPECTED} records')
    print(f'  No district  : {no_district:5d}  ({no_district / total * 100:.1f}%)')
    print(f'  No ISIC-4    : {no_isic4:5d}  ({no_isic4 / total * 100:.1f}%)')
    print(f'  No GPS       : {no_gps:5d}  ({no_gps / total * 100:.1f}%)')
    if missing_nos:
        print(f'  Missing rows : {len(missing_nos)} (first 10: {missing_nos[:10]})')

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out_list, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'\nWrote {OUT}')


if __name__ == '__main__':
    main()
