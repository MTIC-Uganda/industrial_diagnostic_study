"""
midd_lib — pure, importable helpers for the MIDD pipeline (ADR-018).

The generators and seeders (generate_dashboard.py, generate_explorer_data.py,
db/pb_setup.py) run PocketBase side effects at import time, so their logic can't
be unit-tested directly. This module is the home for the PURE pieces of that logic:
no I/O, no module-level side effects, deterministic. Those scripts import from here
(incrementally), which both de-duplicates and makes the logic covered by real unit
tests instead of subprocess behaviour checks.

Pure functions only. If a function needs the network or the filesystem, it does not
belong here.
"""
import urllib.parse

FAC_PREFIX = "FAC-"


def pb_filter(expr: str) -> str:
    """URL-encode a PocketBase records-query filter expression.

    A raw filter containing spaces or '&' (e.g. a category value like
    "Wholesale & Retail") otherwise makes urllib raise InvalidURL — a real
    CI-breaking bug (ADR-017 / Issue #70). Always route filters through here.
    """
    return urllib.parse.quote(expr)


def slug_filter(slug: str) -> str:
    """Encoded filter matching a single `slug` field."""
    return pb_filter(f'(slug="{slug}")')


def two_field_filter(field_a: str, val_a: str, field_b: str, val_b: str) -> str:
    """Encoded AND filter over two fields (e.g. indicator_slug + category)."""
    return pb_filter(f'({field_a}="{val_a}"&&{field_b}="{val_b}")')


def is_real_establishment(record: dict) -> bool:
    """True for a genuine registered establishment, False for a curated FAC-* map pin.

    The dashboard's establishment count and treemaps exclude the curated FAC-*
    map-only rows so the headline figure reflects the real register.
    """
    return not str(record.get("reg_number", "")).startswith(FAC_PREFIX)


CONFIDENCE_BADGE = {
    "exact":         ("● exact",         "conf-exact"),
    "estimated":     ("≈ estimated",     "conf-estimated"),
    "indicative":    ("○ indicative",    "conf-indicative"),
    "not_available": ("— not available", "conf-na"),
}


def confidence_badge(confidence: str):
    """Map a confidence level to its (label, css-class). Unknown -> estimated."""
    return CONFIDENCE_BADGE.get(confidence, CONFIDENCE_BADGE["estimated"])


def aggregate_counts(records, *keys):
    """Nested count aggregation (the treemap shape), computed from PocketBase rows.

    Groups records by the given record keys, counting leaves:
        aggregate_counts(rows, "region", "sector") -> {region: {sector: count}}
    A record missing any of the keys (None or "") is skipped, so partial rows never
    create blank buckets.
    """
    out = {}
    for r in records:
        vals = [r.get(k) for k in keys]
        if any(v in (None, "") for v in vals):
            continue
        node = out
        for v in vals[:-1]:
            node = node.setdefault(v, {})
        leaf = vals[-1]
        node[leaf] = node.get(leaf, 0) + 1
    return out
