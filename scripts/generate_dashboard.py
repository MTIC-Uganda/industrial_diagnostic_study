#!/usr/bin/env python3
"""
Generate report/sources-of-truth.html from template + data.

Data source (auto-detected):
  • If PB_URL is set  →  fetch from PocketBase (CI / prod)
  • Otherwise         →  fall back to local CSV/JSON files in data/dashboard/

Usage:
    python scripts/generate_dashboard.py

Template:
    report/sources-of-truth.template.html   (5 placeholder markers)

Output:
    report/sources-of-truth.html
"""

import csv, json, math, os, re, subprocess, sys, urllib.request, urllib.error, urllib.parse
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
DATA   = ROOT / 'data' / 'dashboard'
TMPL   = ROOT / 'report' / 'sources-of-truth.template.html'
OUTPUT = ROOT / 'report' / 'sources-of-truth.html'

PB_URL      = os.environ.get('PB_URL', '').rstrip('/')
USE_POCKETBASE = bool(PB_URL)

# ── SINGLE SOURCE OF TRUTH (ADR-017) ──────────────────────────────────────────
# The dashboard is built ONLY from PocketBase. There is NO CSV/JSON fallback.
# If PB_URL is unset, or any required collection is empty, we FAIL LOUDLY rather
# than silently rendering stale committed-file data. This is enforced in code so
# no agent (Solomon's or Hillary's) can quietly reintroduce a file fallback.
if not USE_POCKETBASE:
    sys.exit('SINGLE SOURCE (ADR-017): PB_URL is required. The dashboard reads only '
             'from PocketBase; there is no file fallback. Set PB_URL and retry.')

# ── Data loading ──────────────────────────────────────────────────────────────

def pb_get(collection, sort=None, per_page=500, filter=None):
    """Fetch ALL records from a PocketBase collection (public read), paginating.
    PocketBase caps perPage at 500, so anything larger must page through."""
    items, page = [], 1
    while True:
        url = f'{PB_URL}/api/collections/{collection}/records?perPage={per_page}&page={page}'
        if sort:
            url += f'&sort={urllib.parse.quote(sort)}'
        if filter:
            url += f'&filter={urllib.parse.quote(filter)}'
        try:
            with urllib.request.urlopen(url) as r:
                payload = json.loads(r.read())
        except urllib.error.HTTPError as e:
            sys.exit(f'PocketBase error {e.code} fetching {collection}: {e.read().decode()[:200]}')
        except Exception as e:
            sys.exit(f'Cannot reach PocketBase at {PB_URL}: {e}')
        items.extend(payload.get('items', []))
        if page >= payload.get('totalPages', 1) or not payload.get('items'):
            break
        page += 1
    return items

def load_csv(name):
    # SINGLE SOURCE guard (ADR-017): reaching here means PocketBase was missing data
    # and something tried to fall back to a committed file — exactly the bypass we
    # forbid. Fail loudly; seed the collection in PocketBase instead.
    sys.exit(f'SINGLE SOURCE VIOLATION (ADR-017): tried to read {name} from disk. '
             f'All dashboard data must live in PocketBase; there is no file fallback.')

def pb_count(collection, filter=None):
    """Total record count via PocketBase's totalItems pagination field — one
    lightweight request (perPage=1), not a full fetch. Returns None if
    PocketBase is unreachable so the caller can fall back to a static figure."""
    url = f'{PB_URL}/api/collections/{collection}/records?perPage=1'
    if filter:
        url += f'&filter={urllib.parse.quote(filter)}'
    try:
        with urllib.request.urlopen(url) as r:
            return json.loads(r.read()).get('totalItems')
    except Exception:
        return None

if USE_POCKETBASE:
    print(f'Data source: PocketBase ({PB_URL})')

    raw_chains    = pb_get('value_chains', sort='display_order')
    # Locations map reads from the single `industries` table (ADR-011): every
    # establishment that has GPS, not a separate facilities table. Falls back to
    # the facilities collection if industries has no located rows yet.
    located = pb_get('industries', sort='chain_name,name',
                     filter='latitude != 0 || longitude != 0')
    if located:
        raw_facilities = [{
            'name': r.get('name') or r.get('name_products') or '',
            'chain_name': r.get('chain_name') or '',
            'lat': r.get('latitude') or 0, 'lng': r.get('longitude') or 0,
            'location': r.get('location') or r.get('district') or '',
            'products': r.get('products') or r.get('name_products') or '',
            'capacity_installed': r.get('capacity_installed') or '',
            'capacity_utilised': r.get('capacity_utilised') or '',
            'employees': r.get('employees') or '',
            'established': r.get('established') or '',
            'ownership': r.get('ownership') or '',
            'exports': r.get('exports') or '',
        } for r in located]
        print(f'  Locations map: {len(raw_facilities)} establishments from industries (GPS present)')
    else:
        raw_facilities = pb_get('facilities', sort='chain_name,name')
        print('  Locations map: industries has no GPS rows — facilities fallback')

    # Reshape for the generators below
    chain_summary = [{
        'chain':           r['name'],
        'key_import_2024': r.get('key_import_2024') or '',
        'key_export_2024': r.get('key_export_2024') or '',
        'position_tag':    r.get('position_tag') or '',
        'position_color':  r.get('position_color') or 'amber',
        'target_2040':     r.get('target_2040') or '',
        'priority_tag':    r.get('priority_tag') or '',
        'priority_color':  r.get('priority_color') or 'blue',
    } for r in raw_chains]

    chain_colors = {r['name']: r['color'] for r in raw_chains}

    chains = [{
        'id':   r['slug'],
        'name': r['name'],
        'map': {
            'title':  r.get('map_title') or '',
            'desc':   r.get('map_description') or '',
            'phases': r.get('map_phases') or [],
            'gap':    r.get('map_gap') or '',
        },
        'status': {
            'current':     r.get('status_current') or [],
            'companies':   r.get('status_companies') or [],
            'constraints': r.get('status_constraints') or [],
            'priorities':  r.get('status_priorities') or [],
            'proj':        r.get('status_proj') or {},
        },
    } for r in raw_chains]

    factories_list = [{
        'name':               f['name'],
        'chain':              f.get('chain_name') or '',
        'lat':                f.get('lat') or 0,
        'lng':                f.get('lng') or 0,
        'loc':                f.get('location') or '',
        'products':           f.get('products') or '',
        'capacity_installed': f.get('capacity_installed') or '',
        'capacity_utilised':  f.get('capacity_utilised') or '',
        'employees':          f.get('employees') or '',
        'est':                f.get('established') or '',
        'ownership':          f.get('ownership') or '',
        'exports':            f.get('exports') or '',
    } for f in raw_facilities]

    try:
        raw_macro = pb_get('macro_trend', sort='display_order')
        macro_trend = [{
            'id':           r['slug'],
            'label':        r['label'],
            'fy2021_value': r.get('fy2021_value') or '',
            'fy2025_value': r.get('fy2025_value') or '',
            'fy2021_pct':   r.get('fy2021_pct') or 0,
            'fy2025_pct':   r.get('fy2025_pct') or 0,
            'delta':        r.get('delta') or '',
            'direction':    r.get('direction') or 'up',
            'trajectory':   r.get('trajectory') or '',
            'trajectory_labels': r.get('trajectory_labels') or '',
            'confidence':   r.get('confidence') or 'estimated',
            'source':       r.get('source') or '',
        } for r in raw_macro]
        if not macro_trend:
            raise SystemExit
    except SystemExit:
        print('  (no macro_trend collection in PocketBase yet — using local CSV fallback)')
        _mt_file = DATA / 'macro_trend.csv'
        macro_trend = load_csv('macro_trend.csv') if _mt_file.exists() else []

else:
    print('Data source: local files (data/dashboard/)')
    chain_summary  = load_csv('chain_summary.csv')
    chains         = json.loads((DATA / 'chains.json').read_text('utf-8'))
    chain_colors   = json.loads((DATA / 'chain_colors.json').read_text('utf-8'))
    raw_fac        = load_csv('factories.csv')
    factories_list = [{**f, 'loc': f.get('loc', '')} for f in raw_fac]

# Total registered establishments — was a hand-typed "~7,011" both in the
# template and in key_indicators.csv's KPI-7 card; 2026-06-30 data-source
# audit flagged it as a number that will silently go stale as the register
# grows. industries is the canonical establishment table (ADR-011), so count
# it directly (excluding the curated FAC-* map-only rows, same exclusion
# treemap_data_js() already applies) — one lightweight request, not a full
# fetch. Falls back to the last-known figure if PocketBase is unreachable.
_pb_establishment_count = pb_count('industries', filter='reg_number !~ "FAC-"') if USE_POCKETBASE else None
ESTABLISHMENT_COUNT = _pb_establishment_count or 7011
ESTABLISHMENT_COUNT_LABEL = f'{ESTABLISHMENT_COUNT:,}'

if not USE_POCKETBASE:
    # Local-dev fallback only — when PocketBase is live, macro_trend was
    # already set above. (This file is committed for local runs, so without
    # this guard it would silently overwrite the PocketBase-sourced data
    # every time, regardless of whether PocketBase succeeded.)
    macro_trend_file = DATA / 'macro_trend.csv'
    macro_trend = load_csv('macro_trend.csv') if macro_trend_file.exists() else []

# Manufacturing Industry Key Indicators (the 12 cards) + their multi-category
# breakdowns (tax/hightech/credit donuts, region strip). PocketBase first
# (ADR-011, single source of truth); local CSV fallback both for local runs
# and for the first prod deploy after this code lands, before CI's
# seed-pocketbase job has populated the new collections.
def _pb_fetch_or_none(collection, sort=None):
    if not USE_POCKETBASE:
        return None
    try:
        return pb_get(collection, sort=sort)
    except SystemExit:
        return None

_raw_key_indicators  = _pb_fetch_or_none('key_indicators', sort='display_order')
if _raw_key_indicators:
    key_indicators = [{
        'slug': r['slug'], 'label': r['label'], 'kind': r['kind'],
        'value': r.get('value') or '', 'pct': r.get('pct') or '',
        'sub_value': r.get('sub_value') or '', 'icon': r.get('icon') or '',
        'color': r.get('color') or '', 'rest_color': r.get('rest_color') or '',
        'year': r.get('year') or '', 'source': r.get('source') or '',
        'confidence': r.get('confidence') or 'estimated',
    } for r in _raw_key_indicators]
else:
    if USE_POCKETBASE:
        print('  (no key_indicators collection in PocketBase yet — using local CSV fallback)')
    key_indicators = load_csv('key_indicators.csv')
KEY_INDICATORS = {r['slug']: r for r in key_indicators}
if 'establishments' in KEY_INDICATORS:
    KEY_INDICATORS['establishments']['value'] = ESTABLISHMENT_COUNT_LABEL

_raw_key_categories = _pb_fetch_or_none('key_indicator_categories', sort='indicator_slug,display_order')
if _raw_key_categories:
    key_indicator_categories = [{
        'indicator_slug': r['indicator_slug'], 'category': r['category'],
        'pct': r.get('pct') or 0, 'value_label': r.get('value_label') or '',
        'highlight': '1' if r.get('highlight') == '1' else '0',
    } for r in _raw_key_categories]
else:
    if USE_POCKETBASE:
        print('  (no key_indicator_categories collection in PocketBase yet — using local CSV fallback)')
    key_indicator_categories = load_csv('key_indicator_categories.csv')

def kpi_categories_for(slug):
    return [r for r in key_indicator_categories if r['indicator_slug'] == slug]

# Progress to Tenfold Growth panel — sourced from kpi_indicators (PocketBase,
# ADR-011), local CSV fallback at data/dashboard/overview_kpis.csv. This used
# to be hand-typed HTML in the template, which is exactly how it went stale
# and drifted from the 12-card KPI section above it (same underlying numbers,
# two disconnected sources). Now both read from the same table.
#
# PocketBase's seed-pocketbase CI job only runs on direct pushes to main
# (auto-merge pushes with the bot token don't trigger a new workflow run —
# a GitHub Actions anti-recursion rule), so there's always a window where a
# CSV gets a new row before PocketBase has it. Backfill any indicator slug
# this panel needs but PocketBase doesn't have yet from the CSV, instead of
# silently dropping that bar — PocketBase still wins for every slug it does
# have, so a real PocketBase correction always takes priority once seeded.
TENFOLD_PANEL_SLUGS = [
    'manufacturing_gdp', 'manufacturing_tax', 'mfg_exports', 'hightech_exports',
    'private_credit', 'industrial_parks', 'fdi_manufacturing',
    'manufacturing_employment', 'export_variety',
]

_raw_kpi_indicators = _pb_fetch_or_none('kpi_indicators', sort='display_order')
if _raw_kpi_indicators:
    kpi_indicators = [{
        'id': r['slug'], 'label': r['label'],
        'current_value': r.get('current_value') or '', 'current_pct': r.get('current_pct') or 0,
        'ndp_value': r.get('ndp_value') or '', 'ndp_pct': r.get('ndp_pct') or 0,
        'tenfold_value': r.get('tenfold_value') or '', 'tenfold_pct': r.get('tenfold_pct') or 0,
        'sub_value': r.get('sub_value') or '',
        'confidence': r.get('confidence') or 'estimated', 'source': r.get('source') or '',
    } for r in _raw_kpi_indicators]
else:
    if USE_POCKETBASE:
        print('  (no kpi_indicators collection in PocketBase yet — using local CSV fallback)')
    kpi_indicators = []
KPI_INDICATORS = {r['id']: r for r in kpi_indicators}

_missing_slugs = [s for s in TENFOLD_PANEL_SLUGS if s not in KPI_INDICATORS]
if _missing_slugs:
    if USE_POCKETBASE:
        print(f'  kpi_indicators missing from PocketBase (using CSV fallback for these): {", ".join(_missing_slugs)}')
    for r in load_csv('overview_kpis.csv'):
        if r['id'] in _missing_slugs:
            KPI_INDICATORS[r['id']] = r

# Tax/Credit-by-sector charts, Risk Register, Milestone Roadmap, Glossary —
# PocketBase first (ADR-011), local CSV fallback. 2026-06-30 data-source audit:
# these 4 had no PocketBase path at all (CSV-only), unlike everything else on
# the dashboard.
def _pb_or_csv(collection, csv_name, sort='display_order'):
    rows = _pb_fetch_or_none(collection, sort=sort)
    if rows:
        return rows
    if USE_POCKETBASE:
        print(f'  (no {collection} collection in PocketBase yet — using local CSV fallback)')
    csv_file = DATA / csv_name
    return load_csv(csv_name) if csv_file.exists() else []

sector_comparison = _pb_or_csv('sector_comparison', 'sector_comparison.csv')
risk_register     = _pb_or_csv('risk_register', 'risk_register.csv')
milestones        = _pb_or_csv('milestones', 'milestones.csv')
glossary          = _pb_or_csv('glossary', 'glossary.csv')
chain_synergies   = _pb_or_csv('chain_synergies', 'chain_synergies.csv')

# ── HTML generators ───────────────────────────────────────────────────────────

TAG_COLOR = {'green':'tag-green','amber':'tag-yellow','red':'tag-red','blue':'tag-blue'}

CONFIDENCE_BADGE = {
    'exact':       ('● exact',       'conf-exact'),
    'estimated':   ('≈ estimated',   'conf-estimated'),
    'indicative':  ('○ indicative',  'conf-indicative'),
    'not_available': ('— not available', 'conf-na'),
}

def esc(s):
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def confidence_badge_html(confidence, source):
    label, cls = CONFIDENCE_BADGE.get(confidence, CONFIDENCE_BADGE['estimated'])
    title = f' title="Source: {esc(source)}"' if source else ''
    return f'<span class="conf-badge {cls}"{title}>{label}</span>'

# Manufacturing Industry Key Indicators (the 12 cards) — text fields sourced
# from key_indicators (PocketBase, ADR-011). Chart markup (donut/pie/region
# strip) comes from kpi_simple_pie() etc. above; these cover the surrounding
# value/caption/source text so a correction to PocketBase updates both.
def kpi_value(slug):
    r = KEY_INDICATORS.get(slug)
    return esc(r['value']) if r and r.get('value') else ''

def kpi_subvalue(slug):
    r = KEY_INDICATORS.get(slug)
    return r['sub_value'] if r and r.get('sub_value') else ''

def kpi_icon(slug):
    r = KEY_INDICATORS.get(slug)
    return r.get('icon', '') if r else ''

def kpi_source_line(slug):
    r = KEY_INDICATORS.get(slug)
    if not r:
        return ''
    year, source = r.get('year', ''), r.get('source', '')
    return f'{esc(year)} &middot; Source: {esc(source)}'

def kpi_badge(slug):
    r = KEY_INDICATORS.get(slug)
    if not r:
        return ''
    sub = f"{r.get('source','')}, {r.get('year','')}".strip(', ')
    return confidence_badge_html(r.get('confidence', 'estimated'), sub)


def _usd_billions(s):
    m = re.search(r'USD\s*([\d.]+)\s*B', s or '')
    return float(m.group(1)) if m else None

def _fmt_pct(p):
    return f'{p:g}'

def tenfold_progress_panel_html():
    blocks = []
    for i, slug in enumerate(TENFOLD_PANEL_SLUGS, start=1):
        r = KPI_INDICATORS.get(slug)
        if not r:
            print(f'WARNING: kpi_indicators missing slug "{slug}" — Progress to Tenfold bar #{i} skipped', file=sys.stderr)
            continue
        cur_v, cur_p = r['current_value'], float(r['current_pct'] or 0)
        ndp_v, ndp_p = r['ndp_value'], float(r['ndp_pct'] or 0)
        ten_v, ten_p = r['tenfold_value'], float(r['tenfold_pct'] or 0)

        cur_w   = (cur_p / ten_p * 100) if ten_p else 0
        ndp_cum = (ndp_p / ten_p * 100) if ten_p else 0
        ndp_w   = max(ndp_cum - cur_w, 0)
        ten_w   = max(100 - ndp_cum, 0)

        cur_label = f'{esc(cur_v)} / {_fmt_pct(cur_p)}%' if cur_v else f'{_fmt_pct(cur_p)}%'
        ndp_label = f'{esc(ndp_v)} / {_fmt_pct(ndp_p)}%' if ndp_v else f'{_fmt_pct(ndp_p)}%'
        ten_label = f'{esc(ten_v)} / {_fmt_pct(ten_p)}%' if ten_v else f'{_fmt_pct(ten_p)}%'
        summary = f'{cur_label} → NDP IV {ndp_label} → Tenfold {ten_label}'

        margin = '' if i == 1 else ' style="margin-top:14px"'
        seg_cls_attr = ' class="tb-seg"' if slug == 'manufacturing_gdp' else ''

        extra_attrs = ''
        if slug == 'manufacturing_gdp':
            cur_usd, ndp_usd, ten_usd = _usd_billions(cur_v), _usd_billions(ndp_v), _usd_billions(ten_v)
            if cur_usd and ndp_usd and ten_usd:
                fig_cur_w   = cur_usd / ten_usd * 100
                fig_ndp_cum = ndp_usd / ten_usd * 100
                fig_ndp_w   = max(fig_ndp_cum - fig_cur_w, 0)
                fig_ten_w   = max(100 - fig_ndp_cum, 0)
                extra_attrs = (
                    f' id="tenfold-bar-1"'
                    f' data-pct-widths="{cur_w:.1f},{ndp_w:.1f},{ten_w:.1f}"'
                    f' data-fig-widths="{fig_cur_w:.1f},{fig_ndp_w:.1f},{fig_ten_w:.1f}"'
                    f' data-pct-labels="{esc(cur_v)} / {_fmt_pct(cur_p)}%|→ {esc(ndp_v)} / {_fmt_pct(ndp_p)}%|→ {esc(ten_v)} / {_fmt_pct(ten_p)}%"'
                    f' data-fig-labels="{esc(cur_v)}|→ {esc(ndp_v)}|→ {esc(ten_v)}"'
                )

        blocks.append(f'''
      <div class="progress-item"{margin}{extra_attrs}>
        <div class="progress-label"><span><strong>{i}. {esc(r["label"])}</strong></span><span style="font-size:11px">{summary}</span></div>
        <div style="position:relative;height:28px;background:#f5f5f5;border-radius:6px;overflow:hidden">
          <div{seg_cls_attr} style="position:absolute;left:0;top:0;height:100%;width:{cur_w:.1f}%;background:#1565c0;border-radius:6px 0 0 6px;display:flex;align-items:center;padding-left:8px;color:#fff;font-size:11px;font-weight:700">{cur_label}</div>
          <div{seg_cls_attr} style="position:absolute;left:{cur_w:.1f}%;top:0;height:100%;width:{ndp_w:.1f}%;background:#43a047;display:flex;align-items:center;padding-left:6px;color:#fff;font-size:11px;font-weight:700">→ {ndp_label}</div>
          <div{seg_cls_attr} style="position:absolute;left:{ndp_cum:.1f}%;top:0;height:100%;width:{ten_w:.1f}%;background:#f57f17;border-radius:0 6px 6px 0;display:flex;align-items:center;padding-left:6px;color:#fff;font-size:11px;font-weight:700">→ {ten_label} Tenfold</div>
        </div>
      </div>''')
    return ''.join(blocks)

def line_chart_svg(values, labels=None, width=320, chart_h=170, label_h=24,
                    y_axis_w=36, unit='trn', color='#2e7d32'):
    """Full-gridline line/area chart — diamond markers, a labelled y-axis tick
    at every whole unit, every value labelled above its point, x-axis category
    labels below. Modelled on a UBOS/URA/BoU economic-brief reference chart."""
    if not values or len(values) < 2:
        return ''
    n = len(values)
    lo_val, hi_val = min(values), max(values)

    axis_lo = math.floor(lo_val) - 1
    axis_hi = math.ceil(hi_val) + 1
    if axis_hi <= axis_lo:
        axis_hi = axis_lo + 1
    span = axis_hi - axis_lo

    top_pad = 14
    plot_h = chart_h - top_pad
    height = chart_h + label_h
    total_w = y_axis_w + width

    xs, ys = [], []
    for i, v in enumerate(values):
        x = y_axis_w + (i / (n - 1)) * (width - 16) + 8
        y = top_pad + plot_h - ((v - axis_lo) / span) * plot_h
        xs.append(x)
        ys.append(y)

    grid_parts = []
    for t in range(axis_lo, axis_hi + 1):
        gy = top_pad + plot_h - ((t - axis_lo) / span) * plot_h
        grid_parts.append(f'<line x1="{y_axis_w}" y1="{gy:.1f}" x2="{total_w-2}" y2="{gy:.1f}" stroke="#eee" stroke-width="1"/>')
        grid_parts.append(f'<text x="{y_axis_w-6}" y="{gy+3:.1f}" font-size="8" text-anchor="end" fill="#9e9e9e">{t}{unit}</text>')
    grid_html = ''.join(grid_parts)

    points = ' '.join(f'{x:.1f},{y:.1f}' for x, y in zip(xs, ys))
    base_y = top_pad + plot_h
    area = f'{xs[0]:.1f},{base_y:.1f} ' + points + f' {xs[-1]:.1f},{base_y:.1f}'

    hw = 4
    diamonds = ''.join(
        f'<polygon points="{x:.1f},{y-hw:.1f} {x+hw:.1f},{y:.1f} {x:.1f},{y+hw:.1f} {x-hw:.1f},{y:.1f}" fill="{color}"/>'
        for x, y in zip(xs, ys)
    )

    value_tags = []
    for i, (x, y) in enumerate(zip(xs, ys)):
        anchor = 'start' if i == 0 else 'end' if i == n - 1 else 'middle'
        ty = max(y - 9, top_pad - 3)
        value_tags.append(
            f'<text x="{x:.1f}" y="{ty:.1f}" font-size="8" text-anchor="{anchor}" '
            f'fill="{color}" font-weight="700">{values[i]:.1f}{unit}</text>'
        )
    value_tags = ''.join(value_tags)

    tick_labels = ''
    if labels and len(labels) == n:
        tick_labels = ''.join(
            f'<text x="{x:.1f}" y="{chart_h + 16}" font-size="8.5" text-anchor="middle" fill="#666" font-weight="600">{esc(lbl)}</text>'
            for x, lbl in zip(xs, labels)
        )

    return (
        f'<svg class="line-chart" width="{total_w}" height="{height}" viewBox="0 0 {total_w} {height}">'
        f'{grid_html}'
        f'<polygon points="{area}" fill="{color}" opacity="0.12"/>'
        f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
        f'{diamonds}{value_tags}{tick_labels}'
        f'</svg>'
    )

def _parse_num(value_str):
    """'3.5%' -> 3.5, 'USD 1.1bn' -> 1.1, 'Shs 19.6trn' -> 19.6"""
    import re
    m = re.search(r'([\d.]+)', value_str or '')
    return float(m.group(1)) if m else 0.0

_parse_bn = _parse_num

def grouped_bar_svg(categories, old_values, new_values, value_fmt=None,
                     colors=('#b0bec5', '#1565c0'), width=240, height=128):
    """Clustered vertical bar chart — one FY20/21 + one FY24/25 bar per category.

    Reserves top_pad above the tallest possible bar so its value label always
    has room to sit clear of the bar — otherwise the label for the max-value
    bar gets clamped to a position inside the bar itself, and since the label
    colour matches the bar fill, it becomes invisible.
    """
    n = len(categories)
    top_pad = 14
    chart_h = height - 26
    usable_h = chart_h - top_pad
    all_vals = [v for v in (old_values + new_values) if v is not None]
    max_v = max(all_vals) if all_vals else 1
    max_v = max_v or 1
    group_w = width / n
    bar_w = group_w * 0.30
    gap = group_w * 0.08
    fmt = value_fmt or (lambda v: f'{v:g}')
    parts = []
    for i, cat in enumerate(categories):
        gx = i * group_w
        ov, nv = old_values[i], new_values[i]
        oh = (ov / max_v) * usable_h
        nh = (nv / max_v) * usable_h
        ox = gx + group_w / 2 - bar_w - gap / 2
        nx = gx + group_w / 2 + gap / 2
        oy, ny = chart_h - oh, chart_h - nh
        parts.append(f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{bar_w:.1f}" height="{max(oh,0):.1f}" fill="{colors[0]}" rx="2"/>')
        parts.append(f'<rect x="{nx:.1f}" y="{ny:.1f}" width="{bar_w:.1f}" height="{max(nh,0):.1f}" fill="{colors[1]}" rx="2"/>')
        parts.append(f'<text x="{ox+bar_w/2:.1f}" y="{oy-4:.1f}" font-size="8" text-anchor="middle" fill="#888" font-weight="600">{esc(fmt(ov))}</text>')
        parts.append(f'<text x="{nx+bar_w/2:.1f}" y="{ny-4:.1f}" font-size="8" text-anchor="middle" fill="{colors[1]}" font-weight="700">{esc(fmt(nv))}</text>')
        parts.append(f'<text x="{gx+group_w/2:.1f}" y="{chart_h+15:.1f}" font-size="8.5" text-anchor="middle" fill="#666" font-weight="600">{esc(cat)}</text>')
    parts.append(f'<line x1="0" y1="{chart_h}" x2="{width}" y2="{chart_h}" stroke="#e0e0e0" stroke-width="1"/>')
    return f'<svg class="grouped-bar-chart" width="{width}" height="{height}" viewBox="0 0 {width} {height}">{"".join(parts)}</svg>'

def donut_svg(slices, size=110, stroke_width=7):
    """slices: list of (label, pct, color). Uses the r=15.9155 trick so pct maps 1:1 to dash units."""
    r = 15.91549430918954
    cx = cy = 21
    parts = [f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="#eee" stroke-width="{stroke_width}"/>']
    cum = 0
    for _, pct, color in slices:
        dashoffset = 25 - cum
        parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="transparent" stroke="{color}" '
            f'stroke-width="{stroke_width}" stroke-dasharray="{pct} {100-pct}" '
            f'stroke-dashoffset="{dashoffset}"/>'
        )
        cum += pct
    return f'<svg class="donut-chart" width="{size}" height="{size}" viewBox="0 0 42 42">{"".join(parts)}</svg>'

def donut_legend_html(slices):
    rows = []
    for label, pct, color in slices:
        rows.append(
            f'<div class="donut-legend-item"><span class="donut-swatch" style="background:{color}"></span>'
            f'<span class="donut-legend-label">{esc(label)}</span>'
            f'<span class="donut-legend-pct">{pct:g}%</span></div>'
        )
    return '\n'.join(rows)

def donut_card_html(title, slices, caption='', source=''):
    badge = confidence_badge_html('exact', source) if source else ''
    return f'''
    <div class="chart-card">
      <div class="chart-card-title">{esc(title)} {badge}</div>
      <div class="donut-wrap">
        {donut_svg(slices)}
        <div class="donut-legend">{donut_legend_html(slices)}</div>
      </div>
      {f'<div class="chart-card-caption">{caption}</div>' if caption else ''}
    </div>'''

def kpi_progress_bar(pct, color='#1565c0', width=120, height=8):
    """Simple horizontal fill bar for a KPI card's share-of-whole percentage —
    replaces the 2-slice donut (per feedback: donuts only make sense for the
    Tax Contribution card's real multi-sector breakdown, not a generic
    this-vs-rest split)."""
    try:
        pct = max(0, min(100, float(pct)))
    except (TypeError, ValueError):
        return ''
    fill_w = width * pct / 100
    return (
        f'<svg class="kpi-bar" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="{height/2}" fill="#e8eaf6"/>'
        f'<rect x="0" y="0" width="{fill_w:.1f}" height="{height}" rx="{height/2}" fill="{color}"/>'
        f'</svg>'
    )

UGX_PER_USD = 3700

def kpi_compact_donut(slug, size=72, stroke_width=8):
    """Compact category-breakdown donut for a KPI card — circle on top,
    legend below (per the 2026-06-23 dashboard review: 'I would prefer the
    circle is above and the key is below the circle'). The highlighted row
    renders in a standout colour and bold legend text. Sourced from
    key_indicator_categories (PocketBase, ADR-011) — slug is 'tax' or
    'hightech'; value_label is pre-formatted per-indicator (UGX for tax,
    USD for hightech) at the data layer, not computed here."""
    rows = kpi_categories_for(slug)
    if not rows:
        return ''
    rows = sorted(rows, key=lambda r: -float(r['pct']))
    slices, fig_labels = [], {}
    palette_idx = 0
    for r in rows:
        if r.get('highlight') == '1':
            color = '#e65100'  # vivid orange — the highlighted row must stand out
        else:
            color = DONUT_PALETTE[palette_idx % len(DONUT_PALETTE)]
            palette_idx += 1
        slices.append((r['category'], float(r['pct']), color))
        fig_labels[r['category']] = r.get('value_label', '')
    legend_rows = []
    for label, pct, color in slices:
        weight = '700' if color == '#e65100' else '400'
        fig = fig_labels.get(label, '')
        fig_html = f' &middot; {esc(fig)}' if fig else ''
        legend_rows.append(
            f'<div class="kpi-donut-legend-item" style="font-weight:{weight}">'
            f'<span class="donut-swatch" style="background:{color}"></span>'
            f'{esc(label)} <strong>{pct:g}%{fig_html}</strong></div>'
        )
    return (
        f'<div class="kpi-donut-col">'
        f'{donut_svg(slices, size=size, stroke_width=stroke_width)}'
        f'<div class="kpi-donut-legend">{"".join(legend_rows)}</div>'
        f'</div>'
    )

def kpi_simple_pie(slug, size=88, stroke_width=20):
    """Single-share pie for a KPI card where one figure IS the whole story —
    no legend needed ('a pie does not need a legend; it is self explanatory').
    A thicker ring than the multi-category donuts so it reads as a filled
    pie rather than a thin ring. The remaining/'rest' slice gets a visibly
    different colour per the FDI card's specific request. pct/color/rest_color
    come from the key_indicators record (PocketBase, ADR-011)."""
    r = KEY_INDICATORS.get(slug)
    if not r:
        return ''
    try:
        pct = max(0, min(100, float(r['pct'])))
    except (TypeError, ValueError, KeyError):
        return ''
    color = r.get('color') or '#1565c0'
    rest_color = r.get('rest_color') or '#e0e0e0'
    slices = [('', pct, color), ('', 100 - pct, rest_color)]
    return f'<div class="kpi-pie-wrap">{donut_svg(slices, size=size, stroke_width=stroke_width)}</div>'

def kpi_credit_donut(size=72, stroke_width=8):
    """Donut version of Private Sector Credit, for visual uniformity with the
    other indicator cards ('I would also like a donut there for uniformity').
    Sourced from key_indicator_categories (slug='credit'), where pct holds
    the Shs-trillions stock figure (not yet a %) — each sector's share is
    computed against the sum of just these 5, the only breakdown we have,
    not full economy-wide credit."""
    rows = kpi_categories_for('credit')
    if not rows:
        return ''
    total = sum(float(r['pct']) for r in rows) or 1
    rows_sorted = sorted(rows, key=lambda r: -float(r['pct']))
    slices, fig_labels = [], {}
    palette_idx = 0
    for r in rows_sorted:
        share = float(r['pct']) / total * 100
        if r.get('highlight') == '1':
            color = '#e65100'
        else:
            color = DONUT_PALETTE[palette_idx % len(DONUT_PALETTE)]
            palette_idx += 1
        slices.append((r['category'], share, color))
        fig_labels[r['category']] = r.get('value_label', '')
    legend_rows = []
    for label, share, color in slices:
        weight = '700' if color == '#e65100' else '400'
        legend_rows.append(
            f'<div class="kpi-donut-legend-item" style="font-weight:{weight}">'
            f'<span class="donut-swatch" style="background:{color}"></span>'
            f'{esc(label)} <strong>{share:.0f}% &middot; {esc(fig_labels[label])}</strong></div>'
        )
    return (
        f'<div class="kpi-donut-col">'
        f'{donut_svg(slices, size=size, stroke_width=stroke_width)}'
        f'<div class="kpi-donut-legend">{"".join(legend_rows)}</div>'
        f'</div>'
    )

REGION_STRIP_COLORS = {'Central': '#1565c0', 'Eastern': '#2e7d32', 'Western': '#6a1b9a', 'Northern': '#f57f17'}

def kpi_region_strip():
    """4-region proportional colour strip for the 'Distribution by Region'
    indicator card — Jerome explicitly didn't want a donut here, just a box
    subdivided by percentage with different colours per region, no popup.
    Sourced from key_indicator_categories (slug='region_dist'), PocketBase."""
    rows = kpi_categories_for('region_dist')
    if not rows:
        return ''
    segs, legend_items = [], []
    for r in rows:
        region = r['category']
        pct = float(r['pct'])
        color = REGION_STRIP_COLORS.get(region, '#90a4ae')
        segs.append(
            f'<div class="kpi-region-seg" style="width:{pct:.1f}%;background:{color}" '
            f'title="{esc(region)}: {pct:.1f}%"></div>'
        )
        legend_items.append(
            f'<span class="kpi-region-leg-item"><span class="sw" style="background:{color}"></span>'
            f'{esc(region)} {pct:.0f}%</span>'
        )
    return f'<div class="kpi-region-strip">{"".join(segs)}</div><div class="kpi-region-legend">{"".join(legend_items)}</div>'

def macro_trend_html():
    if not macro_trend:
        return '<div style="color:var(--muted);font-size:12px;padding:12px">No trend data available.</div>'
    mt = {r['id']: r for r in macro_trend}

    def badge_for(rid):
        r = mt.get(rid, {})
        return confidence_badge_html(r.get('confidence', 'estimated'), r.get('source', ''))

    def val(rid, key):
        return _parse_num(mt.get(rid, {}).get(key, ''))

    cards = []

    # Card 1 — Growth Rates (grouped bar)
    growth_svg = grouped_bar_svg(
        ['Industry', 'Manufacturing'],
        [val('industry_growth', 'fy2021_value'), val('mfg_growth', 'fy2021_value')],
        [val('industry_growth', 'fy2025_value'), val('mfg_growth', 'fy2025_value')],
        value_fmt=lambda v: f'{v:.1f}%',
    )
    cards.append(f'''
    <div class="chart-card">
      <div class="chart-card-title">Growth Rates {badge_for("industry_growth")}</div>
      {growth_svg}
      <div class="chart-card-caption">Both rose +3.4 pts — industrial growth is accelerating faster than the wider economy.</div>
    </div>''')

    # Card 2 — Manufacturing Value Added (line/area chart)
    vr = mt.get('mfg_value_added', {})
    traj_raw = (vr.get('trajectory') or '').strip()
    labels_raw = (vr.get('trajectory_labels') or '').strip()
    line_svg = ''
    if traj_raw:
        try:
            values = [float(v) for v in traj_raw.split(';') if v]
            labels = [l for l in labels_raw.split(';') if l] if labels_raw else None
            line_svg = line_chart_svg(values, labels=labels)
        except ValueError:
            line_svg = ''
    cards.append(f'''
    <div class="chart-card wide">
      <div class="chart-card-title">Mfg Value Added, real Shs trn {badge_for("mfg_value_added")}</div>
      <div class="line-chart-wrap">{line_svg}</div>
      <div class="chart-card-caption">{esc(vr.get("delta",""))} over 4 years — rising every single year, not just a one-off jump.</div>
    </div>''')

    # Card 3 — Share of GDP (declining, grouped bar — amber/red "new" bar)
    gdp_svg = grouped_bar_svg(
        ['Industry', 'Manufacturing'],
        [val('industry_gdp_share', 'fy2021_value'), val('mfg_gdp_share', 'fy2021_value')],
        [val('industry_gdp_share', 'fy2025_value'), val('mfg_gdp_share', 'fy2025_value')],
        value_fmt=lambda v: f'{v:.1f}%',
        colors=('#b0bec5', '#c62828'),
    )
    cards.append(f'''
    <div class="chart-card">
      <div class="chart-card-title">Share of GDP, current prices {badge_for("industry_gdp_share")}</div>
      {gdp_svg}
      <div class="chart-card-caption">Share of GDP fell even as real output grew — other sectors (services) are growing faster, not that industry shrank.</div>
    </div>''')

    # Card 4 — Manufactured Exports (simple before/after bar, real USD bn values)
    er = mt.get('mfg_exports', {})
    exp_old = _parse_bn(er.get('fy2021_value', ''))
    exp_new = _parse_bn(er.get('fy2025_value', ''))
    exp_svg = grouped_bar_svg(
        ['Exports'], [exp_old], [exp_new],
        value_fmt=lambda v: f'${v:g}bn', width=160,
    )
    cards.append(f'''
    <div class="chart-card">
      <div class="chart-card-title">Manufactured Exports, USD bn {badge_for("mfg_exports")}</div>
      {exp_svg}
      <div class="chart-card-caption">{esc(er.get("delta",""))} — exports more than doubled in four years.</div>
    </div>''')

    return '\n'.join(cards)

# Non-highlighted slices cycle through this palette; highlighted slices always
# get the brand blue, so the palette deliberately excludes it to avoid collisions.
DONUT_PALETTE = ['#b0bec5', '#2e7d32', '#f57f17', '#6a1b9a', '#789262', '#8d6e63']

def tax_donut_html():
    rows = [r for r in sector_comparison if r['chart'] == 'tax']
    if not rows:
        return ''
    rows.sort(key=lambda r: -float(r['pct']))
    slices = []
    palette_idx = 0
    for r in rows:
        if r.get('highlight') == '1':
            color = '#e65100'
        else:
            color = DONUT_PALETTE[palette_idx % len(DONUT_PALETTE)]
            palette_idx += 1
        slices.append((r['sector'], float(r['pct']), color))
    return donut_card_html(
        'Tax Contribution by Sector, FY24/25', slices,
        caption='Manufacturing holds the #2 line directly, behind Wholesale &amp; Retail (which is largely VAT on manufactured goods).',
        source='URA sector & revenue reports',
    )

def electricity_donut_html():
    mt = {r['id']: r for r in macro_trend}
    er = mt.get('industrial_electricity')
    if not er:
        return ''
    industrial = _parse_num(er.get('fy2025_value', ''))
    non_industrial = 100 - industrial
    slices = [
        ('Industrial customers', industrial, '#1565c0'),
        ('Non-industrial', non_industrial, '#b0bec5'),
    ]
    return donut_card_html(
        'Electricity Consumed by Customer Class, FY24/25', slices,
        caption=f'Up from ~{er.get("fy2021_value","60%")} industrial share in FY20/21 — industrial demand is absorbing a growing share of the grid.',
        source=er.get('source', 'Electricity Regulatory Authority'),
    )

def sector_comparison_html(chart_name):
    rows = [r for r in sector_comparison if r['chart'] == chart_name]
    if not rows:
        return '<div style="color:var(--muted);font-size:12px">No data for this chart.</div>'
    max_pct = max(float(r['pct']) for r in rows) or 1
    parts = []
    for r in rows:
        pct = float(r['pct'])
        width = (pct / max_pct) * 100
        highlight = r.get('highlight') == '1'
        bar_cls = 'sector-bar-fill highlight' if highlight else 'sector-bar-fill'
        label_cls = 'sector-bar-label highlight' if highlight else 'sector-bar-label'
        parts.append(f'''
    <div class="sector-bar-row">
      <span class="{label_cls}">{esc(r["sector"])}</span>
      <div class="sector-bar-track"><div class="{bar_cls}" style="width:{width}%"></div></div>
      <span class="sector-bar-val">{r["value_label"]}</span>
    </div>''')
    return '\n'.join(parts)

UPDATE_TAGS = {
    'data:':       ('📊', 'Data'),
    'ingest:':     ('📥', 'Ingest'),
    'synthesise:': ('✍️', 'Chapter'),
    'review:':     ('🔍', 'Review'),
    'gapfill:':    ('✅', 'Gap-fill'),
    'feat:':       ('🚀', 'Feature'),
    'fix:':        ('🛠️', 'Fix'),
    'publish:':    ('📖', 'Published'),
}

def recent_updates_html(limit=8):
    try:
        raw = subprocess.run(
            ['git', 'log', '-n', '40', '--pretty=format:%ad|||%s', '--date=short'],
            cwd=ROOT, capture_output=True, encoding='utf-8', timeout=20, check=True
        ).stdout
    except (subprocess.SubprocessError, FileNotFoundError):
        return '<div style="color:var(--muted);font-size:12px;padding:8px">No update history available.</div>'

    items = []
    for line in raw.splitlines():
        if '|||' not in line:
            continue
        date, msg = line.split('|||', 1)
        for prefix, (icon, tag) in UPDATE_TAGS.items():
            if msg.lower().startswith(prefix):
                clean_msg = msg[len(prefix):].strip()
                items.append((date, icon, tag, clean_msg))
                break
        if len(items) >= limit:
            break

    if not items:
        return '<div style="color:var(--muted);font-size:12px;padding:8px">No tagged updates yet — updates appear here once the pipeline starts committing data, chapters, and reviews.</div>'

    rows = []
    for date, icon, tag, msg in items:
        rows.append(
            f'<div class="update-item">'
            f'<span class="update-icon">{icon}</span>'
            f'<span class="update-tag">{esc(tag)}</span>'
            f'<span class="update-msg">{esc(msg)}</span>'
            f'<span class="update-date">{esc(date)}</span>'
            f'</div>'
        )
    return '\n    '.join(rows)

def chain_synergies_html():
    if not chain_synergies:
        return '<div style="color:rgba(255,255,255,.8);font-size:13px">No synergy data available.</div>'
    parts = []
    for r in chain_synergies:
        parts.append(
            f'<div style="background:rgba(255,255,255,.1);border-radius:8px;padding:12px">'
            f'<strong>{r["title"]}:</strong> {r["description"]}'
            f'</div>'
        )
    return '\n      '.join(parts)

def glossary_html():
    if not glossary:
        return '<div style="color:var(--muted);font-size:12px">No glossary available.</div>'
    parts = []
    for r in sorted(glossary, key=lambda r: r['term'].lower()):
        parts.append(
            f'<div class="glossary-item">'
            f'<div class="glossary-term">{esc(r["term"])}</div>'
            f'<div class="glossary-def">{esc(r["definition"])}</div>'
            f'</div>'
        )
    return '\n    '.join(parts)

SEVERITY_TAG = {'high': 'tag-red', 'medium': 'tag-yellow', 'low': 'tag-green'}

def risk_register_html():
    if not risk_register:
        return '<tr><td colspan="5" style="color:var(--muted)">No risk register available.</td></tr>'
    parts = []
    for r in risk_register:
        sev_cls = SEVERITY_TAG.get(r['severity'].lower(), 'tag-yellow')
        lik_cls = SEVERITY_TAG.get(r['likelihood'].lower(), 'tag-yellow')
        parts.append(
            f'<tr>'
            f'<td><strong>{esc(r["risk"])}</strong><div style="font-size:11px;color:var(--muted);margin-top:3px">{esc(r["category"])}</div></td>'
            f'<td><span class="tag {sev_cls}">{esc(r["severity"].title())}</span></td>'
            f'<td><span class="tag {lik_cls}">{esc(r["likelihood"].title())}</span></td>'
            f'<td>{esc(r["mitigation"])}</td>'
            f'<td>{esc(r["owner"])}</td>'
            f'</tr>'
        )
    return '\n        '.join(parts)

STATUS_LABEL = {
    'complete':   'tag-green',
    'in_progress':'tag-yellow',
    'planned':    'tag-blue',
    'proposed':   'tag-blue',
    'stalled':    'tag-red',
    'milestone':  'tag-red',
}
STATUS_TEXT = {
    'complete': 'Complete', 'in_progress': 'In Progress',
    'planned': 'Planned', 'proposed': 'Proposed (unconfirmed)',
    'stalled': 'Stalled', 'milestone': 'Policy Milestone',
}

VC_ORDER = ['Iron & Steel', 'Copper & Allied Metals', 'Automotive',
            'Textiles & Garments', 'Pharmaceuticals', 'Petrochemicals & Fertilizers',
            'Sugar & Confectionery', 'Plastics & Packaging', 'Cement & Building Materials']

def milestones_html():
    if not milestones:
        return ('', '<div style="color:var(--muted);font-size:12px">No milestone data available.</div>')
    rows = sorted(milestones, key=lambda r: int(r['year']))

    present_chains = [vc for vc in VC_ORDER if any(r['value_chain'] == vc for r in rows)]
    tab_parts = ['<button class="chain-btn active" data-chain="__all__" onclick="filterMilestones(this,\'__all__\')">All Chains</button>']
    for vc in present_chains:
        tab_parts.append(
            f'<button class="chain-btn" data-chain="{esc(vc)}" onclick="filterMilestones(this,\'{js_str(vc)}\')">{esc(vc)}</button>'
        )
    tabs_html = '\n    '.join(tab_parts)

    item_parts = []
    for r in rows:
        status = r['status'].lower()
        dot_cls = status if status in STATUS_LABEL else 'planned'
        tag_cls = STATUS_LABEL.get(status, 'tag-blue')
        tag_txt = STATUS_TEXT.get(status, status.title())
        is_universal = r['value_chain'] == 'All chains'
        data_chain = '__universal__' if is_universal else esc(r['value_chain'])
        item_parts.append(f'''
    <div class="milestone-item" data-chain="{data_chain}">
      <div class="milestone-dot {dot_cls}"></div>
      <div class="milestone-year">{esc(r["year_label"])} &middot; {esc(r["value_chain"])}</div>
      <div class="milestone-title">{esc(r["project"])}</div>
      <div class="milestone-meta"><span class="tag {tag_cls}">{esc(tag_txt)}</span><span class="tag tag-blue" style="background:#f5f5f5;color:#666">{esc(r["category"])}</span></div>
      <div class="milestone-note">{esc(r["note"])}</div>
    </div>''')
    items_html = '\n'.join(item_parts)

    return (tabs_html, items_html)

def chain_table_rows_html():
    rows = []
    for r in chain_summary:
        pc = TAG_COLOR.get(r['position_color'], 'tag-yellow')
        rc = TAG_COLOR.get(r['priority_color'], 'tag-blue')
        rows.append(
            f'<tr>'
            f'<td><strong>{esc(r["chain"])}</strong></td>'
            f'<td>{esc(r["key_import_2024"])}</td>'
            f'<td>{esc(r["key_export_2024"])}</td>'
            f'<td><span class="tag {pc}">{esc(r["position_tag"])}</span></td>'
            f'<td>{esc(r["target_2040"])}</td>'
            f'<td><span class="tag {rc}">{esc(r["priority_tag"])}</span></td>'
            f'</tr>'
        )
    return '\n        '.join(rows)

# ── JS generators ─────────────────────────────────────────────────────────────

def js_str(v):
    return str(v).replace('\\', '\\\\').replace("'", "\\'")

def factories_js():
    lines = ['const FACTORIES=[']
    for i, f in enumerate(factories_list):
        comma = '' if i == len(factories_list) - 1 else ','
        try:
            lat = float(f.get('lat') or 0)
            lng = float(f.get('lng') or 0)
        except (ValueError, TypeError):
            lat = lng = 0
        fields = ','.join(
            f"{k}:'{js_str(f.get(fk,''))}'"
            for k, fk in [
                ('loc','loc'),('products','products'),
                ('capacity_installed','capacity_installed'),
                ('capacity_utilised','capacity_utilised'),
                ('employees','employees'),('est','est'),
                ('ownership','ownership'),('exports','exports'),
            ]
        )
        lines.append(
            f"  {{name:'{js_str(f['name'])}',chain:'{js_str(f['chain'])}'"
            f",lat:{lat},lng:{lng},{fields}}}{comma}"
        )
    lines.append('];')
    return '\n'.join(lines)

def chain_colors_js():
    body = ',\n'.join(f"  '{js_str(k)}':'{v}'" for k, v in chain_colors.items())
    return f'const CHAIN_COLORS={{\n{body}\n}};'

def _treemaps_from_pocketbase():
    """Aggregate the six treemap views live from the PocketBase `industries`
    collection (the datastore). Returns None if PocketBase is unreachable or the
    collection is empty, so the caller falls back to static JSON."""
    from collections import defaultdict
    records, page = [], 1
    while True:
        url = f'{PB_URL}/api/collections/industries/records?perPage=500&page={page}'
        try:
            with urllib.request.urlopen(url) as r:
                payload = json.loads(r.read())
        except Exception:
            return None
        items = payload.get('items', [])
        records.extend(items)
        if page >= payload.get('totalPages', 1) or not items:
            break
        page += 1
    if not records:
        return None
    def nd(): return defaultdict(int)
    sector, district = defaultdict(nd), defaultdict(nd)
    rsec, dsec, rsub, dsub = defaultdict(nd), defaultdict(nd), defaultdict(nd), defaultdict(nd)
    for r in records:
        # The treemaps are the distribution of REGISTERED establishments (the
        # 7,011 register). The curated map factories merged in for the locations
        # map (reg_number FAC-*) are not register rows, so exclude them here so
        # the headline count and the sector/region mix stay accurate.
        if (r.get('reg_number') or '').startswith('FAC-'):
            continue
        reg  = r.get('region') or 'Unclassified'
        dist = r.get('district') or 'Unspecified'
        sec  = r.get('sector_name') or 'Unclassified'
        sub  = r.get('subsector_name') or 'Unspecified'
        sector[sec][sub] += 1
        district[reg][dist] += 1
        rsec[reg][sec] += 1
        dsec[dist][sec] += 1
        rsub[reg][sub] += 1
        dsub[dist][sub] += 1
    f = lambda d: {k: dict(v) for k, v in d.items()}
    return f(sector), f(district), f(rsec), f(dsec), f(rsub), f(dsub)

def treemap_data_js():
    """Embeds the establishment-distribution datasets. Preferred source is the
    PocketBase `industries` collection (the datastore); falls back to the static
    treemap_*.json committed in data/dashboard/ when PocketBase is off/empty.
    Original static files were produced by scripts/extract_industries_register.py:
      - region->district (Spatial Distribution)
      - sector->subsector (Sector Distribution)
      - region->sector and district->sector (cross-filtering: selecting a
        region/district updates Sector Distribution to that area's sector mix;
        selecting a sector updates Spatial Distribution to that sector's
        regional/district mix)
      - region->subsector and district->subsector (same cross-filter, one
        level deeper: selecting an individual product like "Bakery Products"
        updates Spatial Distribution to that specific product's mix)."""
    def _load(name):
        # SINGLE SOURCE guard (ADR-017): treemaps come from the PocketBase industries
        # collection, never a committed JSON. Reaching here = industries was empty.
        sys.exit(f'SINGLE SOURCE VIOLATION (ADR-017): tried to read {name} from disk. '
                 f'Treemaps must be computed from the PocketBase industries collection.')

    agg = _treemaps_from_pocketbase() if USE_POCKETBASE else None
    if agg:
        (sector_data, district_data, region_sector_data,
         district_sector_data, region_subsector_data, district_subsector_data) = agg
        print(f'  Treemaps: {sum(sum(v.values()) for v in district_data.values())} '
              f'establishments from PocketBase industries collection')
    else:
        sector_data             = _load('treemap_sector.json')
        district_data           = _load('treemap_district.json')
        region_sector_data      = _load('treemap_region.json')
        district_sector_data    = _load('treemap_district_sector.json')
        region_subsector_data   = _load('treemap_region_subsector.json')
        district_subsector_data = _load('treemap_district_subsector.json')
        if USE_POCKETBASE:
            print('  Treemaps: PocketBase industries empty — static JSON fallback')
    return (
        'const TREEMAP_SECTOR_DATA = ' + json.dumps(sector_data, ensure_ascii=False) + ';\n'
        'const TREEMAP_DISTRICT_DATA = ' + json.dumps(district_data, ensure_ascii=False) + ';\n'
        'const TREEMAP_REGION_SECTOR_DATA = ' + json.dumps(region_sector_data, ensure_ascii=False) + ';\n'
        'const TREEMAP_DISTRICT_SECTOR_DATA = ' + json.dumps(district_sector_data, ensure_ascii=False) + ';\n'
        'const TREEMAP_REGION_SUBSECTOR_DATA = ' + json.dumps(region_subsector_data, ensure_ascii=False) + ';\n'
        'const TREEMAP_DISTRICT_SUBSECTOR_DATA = ' + json.dumps(district_subsector_data, ensure_ascii=False) + ';'
    )

def chains_js():
    return 'const chains = ' + json.dumps(chains, ensure_ascii=False, indent=2) + ';'

# ── Assemble ──────────────────────────────────────────────────────────────────

if not TMPL.exists():
    sys.exit(f'ERROR: template not found: {TMPL}\nRun scripts/create_template.py first.')

tmpl = TMPL.read_text('utf-8')

_ms_tabs, _ms_items = milestones_html()

def tools_nav_html():
    """Team tool links for the header. Emitted ALWAYS but hidden by default; the
    bubble script reveals them only on the staging host (the workshop view), and the
    public prod dashboard shows the chat bubble instead. The split is decided at
    RUNTIME by hostname, not at build time — so CI's single build deployed to BOTH
    staging and prod renders correctly on each (ADR-016)."""
    up, ask = 'https://staging-upload.midd-ug.com', 'https://staging-ask.midd-ug.com'
    return ('<span id="midd-team-nav" style="display:none">'
            '<a href="' + up + '" class="tour-btn" target="_blank" rel="noopener" '
            'title="Upload a document (team)">&#128228; Upload</a>'
            '<a href="' + ask + '" class="tour-btn" target="_blank" rel="noopener" '
            'title="Ask the MIDD assistant (team)">&#128172; Ask MIDD</a></span>')


def is_prod_build():
    """Prod build = PocketBase points at the prod instance (:8090), not staging/local."""
    return bool(PB_URL) and '8091' not in PB_URL and 'staging' not in PB_URL

replacements = {
    '<!--%%CHAIN_SUMMARY_ROWS%%-->':  chain_table_rows_html(),
    '<!--%%MACRO_TREND_ITEMS%%-->':   macro_trend_html(),
    '<!--%%RECENT_UPDATES%%-->':      recent_updates_html(),
    '<!--%%GLOSSARY_ITEMS%%-->':      glossary_html(),
    '<!--%%RISK_REGISTER_ROWS%%-->':  risk_register_html(),
    '<!--%%MILESTONES_TABS%%-->':     _ms_tabs,
    '<!--%%MILESTONES_ITEMS%%-->':    _ms_items,
    '<!--%%TAX_DONUT%%-->':           tax_donut_html(),
    '<!--%%ELECTRICITY_DONUT%%-->':   electricity_donut_html(),
    # Manufacturing Industry Key Indicators (12 cards) — all sourced from
    # key_indicators / key_indicator_categories (PocketBase, ADR-011), with
    # data/dashboard/*.csv as the local-dev/first-deploy fallback.
    '<!--%%KPI1_DONUT%%-->':          kpi_simple_pie('value_added'),
    '<!--%%KPI1_VALUE%%-->':          kpi_value('value_added'),
    '<!--%%KPI1_SUBVALUE%%-->':       kpi_subvalue('value_added'),
    '<!--%%KPI1_SOURCE%%-->':         kpi_source_line('value_added'),
    '<!--%%KPI1_BADGE%%-->':          kpi_badge('value_added'),
    '<!--%%KPI2_ICON%%-->':           kpi_icon('growth'),
    '<!--%%KPI2_VALUE%%-->':          kpi_value('growth'),
    '<!--%%KPI2_SUBVALUE%%-->':       kpi_subvalue('growth'),
    '<!--%%KPI2_SOURCE%%-->':         kpi_source_line('growth'),
    '<!--%%KPI2_BADGE%%-->':          kpi_badge('growth'),
    '<!--%%KPI3_DONUT%%-->':          kpi_compact_donut('tax'),
    '<!--%%KPI3_SOURCE%%-->':         kpi_source_line('tax'),
    '<!--%%KPI3_BADGE%%-->':          kpi_badge('tax'),
    '<!--%%KPI4_ICON%%-->':           kpi_icon('exports'),
    '<!--%%KPI4_VALUE%%-->':          kpi_value('exports'),
    '<!--%%KPI4_SUBVALUE%%-->':       kpi_subvalue('exports'),
    '<!--%%KPI4_SOURCE%%-->':         kpi_source_line('exports'),
    '<!--%%KPI4_BADGE%%-->':          kpi_badge('exports'),
    '<!--%%KPI5_DONUT%%-->':          kpi_compact_donut('hightech', size=60, stroke_width=7),
    '<!--%%KPI5_SUBVALUE%%-->':       kpi_subvalue('hightech'),
    '<!--%%KPI5_SOURCE%%-->':         kpi_source_line('hightech'),
    '<!--%%KPI5_BADGE%%-->':          kpi_badge('hightech'),
    '<!--%%KPI6_DONUT%%-->':          kpi_credit_donut(),
    '<!--%%KPI6_SOURCE%%-->':         kpi_source_line('credit'),
    '<!--%%KPI6_BADGE%%-->':          kpi_badge('credit'),
    '<!--%%KPI7_ICON%%-->':           kpi_icon('establishments'),
    '<!--%%KPI7_VALUE%%-->':          kpi_value('establishments'),
    '<!--%%KPI7_SOURCE%%-->':         kpi_source_line('establishments'),
    '<!--%%KPI7_BADGE%%-->':          kpi_badge('establishments'),
    '<!--%%KPI8_REGION_STRIP%%-->':   kpi_region_strip(),
    '<!--%%KPI8_SOURCE%%-->':         kpi_source_line('region_dist'),
    '<!--%%KPI8_BADGE%%-->':          kpi_badge('region_dist'),
    '<!--%%KPI9_PIE%%-->':            kpi_simple_pie('parks'),
    '<!--%%KPI9_VALUE%%-->':          kpi_value('parks'),
    '<!--%%KPI9_SUBVALUE%%-->':       kpi_subvalue('parks'),
    '<!--%%KPI9_SOURCE%%-->':         kpi_source_line('parks'),
    '<!--%%KPI9_BADGE%%-->':          kpi_badge('parks'),
    '<!--%%KPI10_PIE%%-->':           kpi_simple_pie('fdi'),
    '<!--%%KPI10_VALUE%%-->':         kpi_value('fdi'),
    '<!--%%KPI10_SUBVALUE%%-->':      kpi_subvalue('fdi'),
    '<!--%%KPI10_SOURCE%%-->':        kpi_source_line('fdi'),
    '<!--%%KPI10_BADGE%%-->':         kpi_badge('fdi'),
    '<!--%%KPI11_PIE%%-->':           kpi_simple_pie('employment'),
    '<!--%%KPI11_VALUE%%-->':         kpi_value('employment'),
    '<!--%%KPI11_SUBVALUE%%-->':      kpi_subvalue('employment'),
    '<!--%%KPI11_SOURCE%%-->':        kpi_source_line('employment'),
    '<!--%%KPI11_BADGE%%-->':         kpi_badge('employment'),
    '<!--%%KPI12_ICON%%-->':          kpi_icon('variety'),
    '<!--%%KPI12_VALUE%%-->':         kpi_value('variety'),
    '<!--%%KPI12_SUBVALUE%%-->':      kpi_subvalue('variety'),
    '<!--%%KPI12_BAR%%-->':           kpi_progress_bar(float(KEY_INDICATORS.get('variety', {}).get('pct') or 0), color='#4527a0'),
    '<!--%%KPI12_SOURCE%%-->':        kpi_source_line('variety'),
    '<!--%%KPI12_BADGE%%-->':         kpi_badge('variety'),
    '<!--%%CREDIT_SECTOR_BARS%%-->':  sector_comparison_html('credit'),
    '<!--%%TENFOLD_PROGRESS_PANEL%%-->': tenfold_progress_panel_html(),
    '/*%%CHAINS_DATA%%*/':            chains_js(),
    '/*%%CHAIN_COLORS_DATA%%*/':      chain_colors_js(),
    '/*%%FACTORIES_DATA%%*/':         factories_js(),
    '/*%%TREEMAP_DATA%%*/':           treemap_data_js(),
    '<!--%%TOOLS_NAV%%-->':           tools_nav_html(),
    '<!--%%ESTABLISHMENT_COUNT%%-->': ESTABLISHMENT_COUNT_LABEL,
    '<!--%%CHAIN_SYNERGIES%%-->':     chain_synergies_html(),
}

out = tmpl
for marker, content in replacements.items():
    if marker not in out:
        print(f'WARNING: marker not found: {marker}', file=sys.stderr)
    out = out.replace(marker, content, 1)

# Public Ask MIDD chat bubble + team-nav: emitted ALWAYS. The bubble script picks
# what to show by hostname at runtime (bubble on prod, team links on staging), so a
# single build is correct on both origins — CI builds once and deploys to both
# (ADR-016). Just drop the marker comments.
out = out.replace('<!--CHAT_BUBBLE_START-->', '').replace('<!--CHAT_BUBBLE_END-->', '')
print('  Chat bubble + team-nav: included (hostname-aware at runtime)')

OUTPUT.write_text(out, 'utf-8')
print(f'Generated {OUTPUT}  ({len(out):,} bytes, {out.count(chr(10)):,} lines)')
