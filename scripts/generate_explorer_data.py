#!/usr/bin/env python3
"""
Generate app/explorer/src/data/ironSteel.js from PocketBase (ADR-017).

PocketBase is the ONLY source (explorer_products, explorer_categories,
explorer_trade_hs4, explorer_raw_material_trade, explorer_phase_producers,
explorer_product_firms, explorer_input_keywords — see db/pb_setup_explorer.py).
There is no file fallback. This script regenerates the JS data file the Explorer's
vite build bundles, the same way scripts/generate_dashboard.py regenerates the main
dashboard from PocketBase.

Structured for testability (ADR-018): all logic is in pure/importable functions;
the only side effects (PocketBase fetch, file write) run under main().

Usage:  PB_URL=... python scripts/generate_explorer_data.py
Output: app/explorer/src/data/ironSteel.js
"""

import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'app' / 'explorer' / 'src' / 'data' / 'ironSteel.js'

# logical key -> (PocketBase collection, sort)
COLLECTIONS = {
    'products':        ('explorer_products', 'display_order'),
    'categories':      ('explorer_categories', 'display_order'),
    'trade_hs4':       ('explorer_trade_hs4', 'display_order'),
    'raw_material':    ('explorer_raw_material_trade', 'display_order'),
    'phase_producers': ('explorer_phase_producers', 'display_order'),
    'product_firms':   ('explorer_product_firms', 'display_order'),
    'input_keywords':  ('explorer_input_keywords', 'display_order'),
    'trade_trend':     ('explorer_trade_trend',    'hs4_code,year'),
    'trade_partners':  ('explorer_trade_partners', 'hs4_code,rank'),
}


# ── SINGLE SOURCE guards (ADR-017): no file fallback ──────────────────────────
def load_csv(name):
    sys.exit(f'SINGLE SOURCE VIOLATION (ADR-017): tried to read {name} from disk. '
             f'Explorer data must live in PocketBase; there is no file fallback.')


def load_json(name):
    sys.exit(f'SINGLE SOURCE VIOLATION (ADR-017): tried to read {name} from disk. '
             f'Explorer data must live in PocketBase; there is no file fallback.')


# ── PocketBase fetch ──────────────────────────────────────────────────────────
def pb_get(pb_url, collection, sort=None):
    """Fetch all records from a PocketBase collection, paginating. None on error."""
    items, page = [], 1
    while True:
        url = f'{pb_url}/api/collections/{collection}/records?perPage=500&page={page}'
        if sort:
            url += f'&sort={urllib.parse.quote(sort)}'
        try:
            with urllib.request.urlopen(url) as r:
                payload = json.loads(r.read())
        except Exception as e:
            print(f'  Cannot reach PocketBase for {collection}: {e}')
            return None
        items.extend(payload.get('items', []))
        if page >= payload.get('totalPages', 1) or not payload.get('items'):
            break
        page += 1
    return items


def fetch_all(pb_url):
    """Fetch every explorer collection -> {logical_key: [rows] | None}."""
    return {key: pb_get(pb_url, coll, sort) for key, (coll, sort) in COLLECTIONS.items()}


# ── Pure reshape (unit-tested) ────────────────────────────────────────────────
def _maybe_json(value, default=None):
    """A PocketBase json field arrives as a python value or a JSON string; normalise."""
    if isinstance(value, str):
        return json.loads(value) if value else default
    return value


def build_products(rows):
    out = {}
    for r in rows or []:
        out[r['slug']] = {
            'id': r['slug'], 'name': r['name'], 'category': r['category'],
            'color': r['color'], 'description': r['description'],
            'chains': _maybe_json(r['chains']),
        }
    return out


def build_categories(rows):
    return [
        {'name': r['name'], 'color': r['color'], 'products': _maybe_json(r['products'])}
        for r in rows or []
    ]


def _trade_block(r):
    def _g(key): return float(r[key]) if r.get(key) not in (None, '', 0) else None
    return {
        'desc': r['desc'], 'year': int(float(r['year'])),
        'imports': {'uganda': float(r['imports_uganda']), 'eac': float(r['imports_eac']), 'global': _g('imports_global')},
        'exports': {'uganda': float(r['exports_uganda']), 'eac': float(r['exports_eac']), 'global': _g('exports_global')},
    }


def build_trade_hs4(rows):
    return {r['hs4_code']: _trade_block(r) for r in rows or []}


def build_product_hs4(product_rows):
    return {r['slug']: r['hs4_code'] for r in product_rows or [] if r.get('hs4_code')}


def build_raw_material(rows):
    trade, phase = {}, {}
    for r in rows or []:
        trade[r['item_name']] = _trade_block(r)
        if r.get('phase'):
            phase[r['item_name']] = r['phase']
    return trade, phase


def build_phase_producers(rows):
    producers, source = {}, ''
    for r in rows or []:
        producers[r['phase']] = {
            'count': int(float(r['count'])), 'label': r['label'],
            'examples': _maybe_json(r['examples']),
        }
        source = r.get('source') or source
    return producers, source


def build_product_firms(rows):
    out = {}
    for r in rows or []:
        firms = _maybe_json(r['firms'], []) or []
        phase_context = _maybe_json(r.get('phase_context'), None)
        entry = {'status': r['status'], 'firms': firms, 'note': r.get('note') or ''}
        if phase_context:
            entry['phaseContext'] = phase_context
        out[r['product_slug']] = entry
    return out


def build_input_keywords(rows):
    hs4, phase = [], []
    for r in rows or []:
        row = {'source': r['pattern_source'], 'flags': r['pattern_flags'], 'value': r['target_value']}
        (hs4 if r['target_type'] == 'hs4' else phase).append(row)
    return hs4, phase


def build_trade_trend(rows):
    """Group trend rows by hs4_code → sorted list of {year, imports_uganda, unit_value_usd_t}."""
    out = {}
    for r in rows or []:
        code = r['hs4_code']
        if code not in out:
            out[code] = []
        uv = float(r['unit_value_usd_t']) if r.get('unit_value_usd_t') not in (None, '', 0, '0') else None
        out[code].append({
            'year': int(float(r['year'])),
            'imports_uganda': float(r['imports_uganda']),
            'unit_value_usd_t': uv,
        })
    for code in out:
        out[code].sort(key=lambda x: x['year'])
    return out


def build_trade_partners(rows):
    """Group partner rows by hs4_code → ranked list of {rank, name, code, value}."""
    out = {}
    for r in rows or []:
        code = r['hs4_code']
        if code not in out:
            out[code] = []
        out[code].append({
            'rank': int(float(r['rank'])),
            'name': r['partner_name'],
            'code': int(float(r.get('partner_code', 0))),
            'value': float(r['imports_value_usd_k']),
        })
    for code in out:
        out[code].sort(key=lambda x: x['rank'])
    return out


def build_priority_scores(trade_hs4, trend, partners):
    """
    Compute a 0–100 opportunity score per HS4 code for import-substitution ranking.

    Components (sum = 100 max):
      import_score (0-40): log-scaled Uganda import value — large market = big opportunity
      cagr_score   (0-25): CAGR from trend — rising imports = growing urgency
      gap_score    (0-25): (imports − exports) / imports — no domestic output = clear gap
      conc_score   (0-10): top-supplier share — single source = strategic risk / urgency

    Only codes with Uganda imports ≥ 500 USD thousands ($500k) are scored.
    """
    import math
    MAX_LOG = math.log10(500_000)  # ~$500M — log scale ceiling
    scores = {}
    for hs4, trade in (trade_hs4 or {}).items():
        imp = trade['imports']['uganda']
        exp = trade['exports']['uganda']
        if imp < 500:
            continue

        # 1. Import scale (0-40)
        import_score = min(40.0, (math.log10(max(imp, 1)) / MAX_LOG) * 40)

        # 2. CAGR (0-25): 20%+ CAGR → full 25 pts
        cagr_score = 0.0
        trend_rows = (trend or {}).get(hs4, [])
        if len(trend_rows) >= 2:
            oldest = trend_rows[0]['imports_uganda']
            newest = trend_rows[-1]['imports_uganda']
            years = trend_rows[-1]['year'] - trend_rows[0]['year']
            if oldest > 0 and years > 0:
                cagr = (newest / oldest) ** (1 / years) - 1
                cagr_score = min(25.0, max(0.0, cagr * 125))

        # 3. Production gap (0-25)
        gap_score = max(0.0, (imp - exp) / imp) * 25 if imp > 0 else 0.0

        # 4. Supply concentration risk (0-10)
        conc_score = 0.0
        partner_rows = (partners or {}).get(hs4, [])
        if partner_rows:
            total_val = sum(p['value'] for p in partner_rows) or 1
            conc_score = (partner_rows[0]['value'] / total_val) * 10

        total = round(import_score + cagr_score + gap_score + conc_score)
        scores[hs4] = {
            'score': min(100, total),
            'components': {
                'import': round(import_score),
                'cagr':   round(cagr_score),
                'gap':    round(gap_score),
                'conc':   round(conc_score),
            },
        }
    return scores


def build_all(raw):
    """Turn raw PocketBase rows into every shape the JS module needs."""
    rm_trade, rm_phase = build_raw_material(raw['raw_material'])
    phase_producers, phase_source = build_phase_producers(raw['phase_producers'])
    kw_hs4, kw_phase = build_input_keywords(raw['input_keywords'])
    trade_hs4 = build_trade_hs4(raw['trade_hs4'])
    trend     = build_trade_trend(raw.get('trade_trend'))
    partners  = build_trade_partners(raw.get('trade_partners'))
    return {
        'PRODUCTS': build_products(raw['products']),
        'CATEGORIES': build_categories(raw['categories']),
        'TRADE_HS4': trade_hs4,
        'PRODUCT_HS4': build_product_hs4(raw['products']),
        'RAW_MATERIAL_TRADE': rm_trade,
        'RAW_MATERIAL_PHASE': rm_phase,
        'PHASE_PRODUCERS': phase_producers,
        'PHASE_SOURCE': phase_source,
        'PRODUCT_FIRMS': build_product_firms(raw['product_firms']),
        'INPUT_KEYWORD_HS4': kw_hs4,
        'INPUT_KEYWORD_PHASE': kw_phase,
        'TRADE_TREND': trend,
        'TRADE_PARTNERS': partners,
        'OPPORTUNITY_SCORES': build_priority_scores(trade_hs4, trend, partners),
    }


# ── JS emit ───────────────────────────────────────────────────────────────────
def js_obj(value):
    """json.dumps output is valid JS object/array literal syntax."""
    return json.dumps(value, indent=2, ensure_ascii=False)


def js_regex_array(rows, target_key):
    lines = ['[']
    for r in rows:
        lines.append(f'  {{ pattern: /{r["source"]}/{r["flags"]}, {target_key}: {json.dumps(r["value"])} }},')
    lines.append(']')
    return '\n'.join(lines)


def render_js(d):
    """Render the whole ironSteel.js module from the built data dict."""
    return f'''// GENERATED FILE — do not hand-edit. Regenerate with:
//   python scripts/generate_explorer_data.py
// Source of truth: PocketBase (explorer_* collections — see db/pb_setup_explorer.py).

const PRODUCTS = {js_obj(d['PRODUCTS'])};

const CATEGORIES = {js_obj(d['CATEGORIES'])};

const TRADE_HS4 = {js_obj(d['TRADE_HS4'])};

const PRODUCT_HS4 = {js_obj(d['PRODUCT_HS4'])};

const RAW_MATERIAL_TRADE = {js_obj(d['RAW_MATERIAL_TRADE'])};

const RAW_MATERIAL_PHASE = {js_obj(d['RAW_MATERIAL_PHASE'])};

const PHASE_PRODUCERS = {js_obj(d['PHASE_PRODUCERS'])};

const PHASE_SOURCE = {json.dumps(d['PHASE_SOURCE'])};

const PRODUCT_FIRMS = {js_obj(d['PRODUCT_FIRMS'])};

// 6-year Uganda import trend per HS4 code (2019-2024). Keys are HS4 codes;
// values are arrays sorted by year: {{ year, imports_uganda (USD thousands), unit_value_usd_t }}.
// Populated by scripts/fetch_strategic_data.py + db/pb_setup_explorer.py.
const TRADE_TREND = {js_obj(d['TRADE_TREND'])};

// Top import source countries per HS4 code (UN Comtrade 2024).
// Keys are HS4 codes; values are arrays sorted by rank: {{ rank, name, code, value (USD thousands) }}.
const TRADE_PARTNERS = {js_obj(d['TRADE_PARTNERS'])};

// 0–100 import-substitution opportunity score per HS4 code.
// score    = import_scale(0-40) + cagr(0-25) + production_gap(0-25) + supply_concentration(0-10)
// components: {{ import, cagr, gap, conc }} — each sub-score for transparency in the UI.
const OPPORTUNITY_SCORES = {js_obj(d['OPPORTUNITY_SCORES'])};

// Keyword -> HS-4 group, for matching free-text "Inputs" tab line items
// to the same trade data used for raw materials and products above.
const INPUT_KEYWORD_HS4 = {js_regex_array(d['INPUT_KEYWORD_HS4'], 'hs4')};

function matchInputTrade(text) {{
  const hit = INPUT_KEYWORD_HS4.find((k) => k.pattern.test(text));
  return hit ? TRADE_HS4[hit.hs4] : null;
}}

function matchInputHs4(text) {{
  const hit = INPUT_KEYWORD_HS4.find((k) => k.pattern.test(text));
  return hit ? hit.hs4 : null;
}}

// Keyword -> verified Phase, for the same free-text "Inputs" line items.
const INPUT_KEYWORD_PHASE = {js_regex_array(d['INPUT_KEYWORD_PHASE'], 'phase')};

function matchInputPhase(text) {{
  const hit = INPUT_KEYWORD_PHASE.find((k) => k.pattern.test(text));
  return hit ? PHASE_PRODUCERS[hit.phase] : null;
}}

// Returns {{ essentiality, scarcity, weight }} for the first matching keyword.
function getInputWeight(text) {{
  const h4 = INPUT_KEYWORD_HS4.find(k => k.pattern.test(text));
  if (h4 && h4.essentiality) return {{ essentiality: h4.essentiality, scarcity: h4.scarcity, weight: h4.essentiality * h4.scarcity }};
  const hp = INPUT_KEYWORD_PHASE.find(k => k.pattern.test(text));
  if (hp && hp.essentiality) return {{ essentiality: hp.essentiality, scarcity: hp.scarcity, weight: hp.essentiality * hp.scarcity }};
  return null;
}}

export {{ PRODUCTS, CATEGORIES, TRADE_HS4, PRODUCT_HS4, RAW_MATERIAL_TRADE, matchInputTrade, matchInputHs4, matchInputPhase, getInputWeight, PRODUCT_FIRMS, PHASE_PRODUCERS, PHASE_SOURCE, RAW_MATERIAL_PHASE, TRADE_TREND, TRADE_PARTNERS, OPPORTUNITY_SCORES }};
'''


# ── main (the only side effects) ──────────────────────────────────────────────
def main(pb_url=None, out=OUTPUT, fetcher=fetch_all):
    pb_url = pb_url if pb_url is not None else os.environ.get('PB_URL', '').rstrip('/')
    if not pb_url:
        sys.exit('SINGLE SOURCE (ADR-017): PB_URL is required — explorer data comes only '
                 'from PocketBase; there is no file fallback.')
    raw = fetcher(pb_url)
    if not raw.get('products'):
        sys.exit('ERROR: no explorer_products data in PocketBase (empty or unreachable).')
    built = build_all(raw)
    js = render_js(built)
    Path(out).write_text(js, 'utf-8')
    print(f'Data source: PocketBase ({pb_url})')
    print(f'Generated {out}  ({len(js):,} bytes, {len(built["PRODUCTS"])} products)')
    return js


if __name__ == '__main__':
    main()
