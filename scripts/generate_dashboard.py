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

import csv, json, math, os, subprocess, sys, urllib.request, urllib.error
from pathlib import Path

ROOT   = Path(__file__).resolve().parent.parent
DATA   = ROOT / 'data' / 'dashboard'
TMPL   = ROOT / 'report' / 'sources-of-truth.template.html'
OUTPUT = ROOT / 'report' / 'sources-of-truth.html'

PB_URL      = os.environ.get('PB_URL', '').rstrip('/')
USE_POCKETBASE = bool(PB_URL)

# ── Data loading ──────────────────────────────────────────────────────────────

def pb_get(collection, sort=None, per_page=500):
    """Fetch all records from a PocketBase collection (public read)."""
    url = f'{PB_URL}/api/collections/{collection}/records?perPage={per_page}'
    if sort:
        url += f'&sort={sort}'
    try:
        with urllib.request.urlopen(url) as r:
            return json.loads(r.read()).get('items', [])
    except urllib.error.HTTPError as e:
        sys.exit(f'PocketBase error {e.code} fetching {collection}: {e.read().decode()[:200]}')
    except Exception as e:
        sys.exit(f'Cannot reach PocketBase at {PB_URL}: {e}')

def load_csv(name):
    with open(DATA / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

if USE_POCKETBASE:
    print(f'Data source: PocketBase ({PB_URL})')

    raw_chains    = pb_get('value_chains', sort='display_order')
    raw_kpis      = pb_get('kpi_indicators', sort='display_order')
    raw_facilities = pb_get('facilities', sort='chain_name,name')

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

    overview_kpis = [{
        'id':            r['slug'],
        'label':         r['label'],
        'current_value': r.get('current_value') or '',
        'sub_value':     r.get('sub_value') or '',
        'confidence':    r.get('confidence') or 'estimated',
        'source':        r.get('source') or '',
    } for r in raw_kpis]

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
    except SystemExit:
        print('  (no macro_trend collection in PocketBase yet — skipping Momentum panel)')
        macro_trend = []

else:
    print('Data source: local files (data/dashboard/)')
    chain_summary  = load_csv('chain_summary.csv')
    overview_kpis  = load_csv('overview_kpis.csv')
    chains         = json.loads((DATA / 'chains.json').read_text('utf-8'))
    chain_colors   = json.loads((DATA / 'chain_colors.json').read_text('utf-8'))
    raw_fac        = load_csv('factories.csv')
    factories_list = [{**f, 'loc': f.get('loc', '')} for f in raw_fac]

macro_trend_file = DATA / 'macro_trend.csv'
macro_trend = load_csv('macro_trend.csv') if macro_trend_file.exists() else []

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

# Unused since Jerome's 2026-06-20 rebrand (12 KPI cards + 9 Tenfold bars,
# hardcoded directly in the template like the progress bars always were).
# Kept for now in case the CSV-driven approach is revived for a future KPI set.
def kpi_cards_html():
    parts = []
    for r in overview_kpis:
        badge = confidence_badge_html(r.get('confidence', 'estimated'), r.get('source', ''))
        parts.append(
            f'<div class="card">'
            f'<h3>{esc(r["label"])} {badge}</h3>'
            f'<div class="value">{esc(r["current_value"])}</div>'
            f'<div class="sub-value">{r["sub_value"]}</div>'
            f'</div>'
        )
    return '\n    '.join(parts)

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
    sc_file = DATA / 'sector_comparison.csv'
    if not sc_file.exists():
        return ''
    rows = [r for r in load_csv('sector_comparison.csv') if r['chart'] == 'tax']
    if not rows:
        return ''
    rows.sort(key=lambda r: -float(r['pct']))
    slices = []
    palette_idx = 0
    for r in rows:
        if r.get('highlight') == '1':
            color = '#1565c0'
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
    sc_file = DATA / 'sector_comparison.csv'
    if not sc_file.exists():
        return '<div style="color:var(--muted);font-size:12px">No sector comparison data available.</div>'
    rows = [r for r in load_csv('sector_comparison.csv') if r['chart'] == chart_name]
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

def glossary_html():
    glossary_file = DATA / 'glossary.csv'
    if not glossary_file.exists():
        return '<div style="color:var(--muted);font-size:12px">No glossary available.</div>'
    rows = load_csv('glossary.csv')
    parts = []
    for r in sorted(rows, key=lambda r: r['term'].lower()):
        parts.append(
            f'<div class="glossary-item">'
            f'<div class="glossary-term">{esc(r["term"])}</div>'
            f'<div class="glossary-def">{esc(r["definition"])}</div>'
            f'</div>'
        )
    return '\n    '.join(parts)

SEVERITY_TAG = {'high': 'tag-red', 'medium': 'tag-yellow', 'low': 'tag-green'}

def risk_register_html():
    risk_file = DATA / 'risk_register.csv'
    if not risk_file.exists():
        return '<tr><td colspan="5" style="color:var(--muted)">No risk register available.</td></tr>'
    rows = load_csv('risk_register.csv')
    parts = []
    for r in rows:
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
    ms_file = DATA / 'milestones.csv'
    if not ms_file.exists():
        return ('', '<div style="color:var(--muted);font-size:12px">No milestone data available.</div>')
    rows = load_csv('milestones.csv')
    rows.sort(key=lambda r: int(r['year']))

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

def treemap_data_js():
    """Embeds the establishment-distribution datasets (region->district for
    Spatial Distribution, sector->subsector for Sector Distribution) extracted
    from Jerome's National Industries Register (Aug 2025) by
    scripts/extract_industries_register.py."""
    sector_file   = DATA / 'treemap_sector.json'
    district_file = DATA / 'treemap_district.json'
    sector_data   = json.loads(sector_file.read_text('utf-8')) if sector_file.exists() else {}
    district_data = json.loads(district_file.read_text('utf-8')) if district_file.exists() else {}
    return (
        'const TREEMAP_SECTOR_DATA = ' + json.dumps(sector_data, ensure_ascii=False) + ';\n'
        'const TREEMAP_DISTRICT_DATA = ' + json.dumps(district_data, ensure_ascii=False) + ';'
    )

def chains_js():
    return 'const chains = ' + json.dumps(chains, ensure_ascii=False, indent=2) + ';'

# ── Assemble ──────────────────────────────────────────────────────────────────

if not TMPL.exists():
    sys.exit(f'ERROR: template not found: {TMPL}\nRun scripts/create_template.py first.')

tmpl = TMPL.read_text('utf-8')

_ms_tabs, _ms_items = milestones_html()

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
    '<!--%%CREDIT_SECTOR_BARS%%-->':  sector_comparison_html('credit'),
    '/*%%CHAINS_DATA%%*/':            chains_js(),
    '/*%%CHAIN_COLORS_DATA%%*/':      chain_colors_js(),
    '/*%%FACTORIES_DATA%%*/':         factories_js(),
    '/*%%TREEMAP_DATA%%*/':           treemap_data_js(),
}

out = tmpl
for marker, content in replacements.items():
    if marker not in out:
        print(f'WARNING: marker not found: {marker}', file=sys.stderr)
    out = out.replace(marker, content, 1)

OUTPUT.write_text(out, 'utf-8')
print(f'Generated {OUTPUT}  ({len(out):,} bytes, {out.count(chr(10)):,} lines)')
