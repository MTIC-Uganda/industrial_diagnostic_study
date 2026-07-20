"""
query_tool — the security boundary for the public chatbot's database tool (ADR-017/018).

A public LLM must NEVER be able to run an arbitrary PocketBase query. So the model only
*proposes* a query spec (JSON); this module VALIDATES it against a strict whitelist
(allowed collections, filterable fields, operators, capped limit) and builds a safe,
read-only PocketBase filter. Anything off-whitelist or malformed -> None (the caller
falls back to the brief). Pure + unit-tested; no I/O here.
"""

# Whitelisted read-only surface. filter_fields: what the model may filter on.
# return_fields: the only fields ever returned for a "list" (excludes contact/owner/notes).
QUERYABLE = {
    "industries": {
        "filter_fields": {"region", "district", "sector_name", "subsector_name",
                          "chain_name", "status", "isic_2digit_desc"},
        "return_fields": ["name", "district", "region", "sector_name", "products",
                          "capacity_installed", "employees", "status"],
    },
    "value_chains": {
        "filter_fields": {"slug", "name"},
        "return_fields": ["name", "key_export_2024", "key_import_2024", "target_2040",
                          "status_current"],
    },
    "key_indicators": {
        "filter_fields": {"slug"},
        "return_fields": ["label", "value", "year", "source_detail"],
    },
}

ALLOWED_OPS = {"=", "~"}   # PocketBase: exact-match, contains. Nothing else.
MAX_LIMIT = 50
MAX_FILTERS = 4
MAX_VALUE_LEN = 80

# Fields the model may GROUP BY (aggregate counts over), per collection. This is the
# security boundary for the "group" mode: only these dimensions can be broken down, so
# the public bot can answer "which sectors / by region / rank districts" (ADR-025) without
# code execution and without exposing anything outside the whitelist above.
GROUPABLE = {
    "industries": {"region", "district", "sector_name", "subsector_name",
                   "chain_name", "status", "isic_2digit_desc"},
    "value_chains": {"status_current", "position_tag", "priority_tag"},
}


def validate_spec(spec):
    """Validate a model-proposed query spec against the whitelist.

    spec = {"collection", "filters":[{"field","op","value"}], "mode":"count"|"list", "limit"?}
    Returns a sanitized spec dict, or None if anything is off-whitelist/unsafe.
    """
    if not isinstance(spec, dict):
        return None
    coll = spec.get("collection")
    if coll not in QUERYABLE:
        return None
    conf = QUERYABLE[coll]

    filters = spec.get("filters") or []
    if not isinstance(filters, list) or len(filters) > MAX_FILTERS:
        return None
    clean = []
    for f in filters:
        if not isinstance(f, dict):
            return None
        field = f.get("field")
        op = f.get("op", "=")
        val = f.get("value")
        if field not in conf["filter_fields"]:
            return None
        if op not in ALLOWED_OPS:
            return None
        if not isinstance(val, (str, int, float)) or isinstance(val, bool):
            return None
        sval = str(val)
        if not sval or len(sval) > MAX_VALUE_LEN or '"' in sval or "\\" in sval:
            return None
        clean.append({"field": field, "op": op, "value": sval})

    mode = spec.get("mode", "count")
    if mode not in ("count", "list", "group"):
        return None
    try:
        limit = int(spec.get("limit", 20))
    except (TypeError, ValueError):
        limit = 20
    limit = max(1, min(limit, MAX_LIMIT))
    out = {"collection": coll, "filters": clean, "mode": mode, "limit": limit}
    if mode == "group":
        group_by = spec.get("group_by")
        if group_by not in GROUPABLE.get(coll, set()):
            return None
        out["group_by"] = group_by
    return out


def aggregate_rows(rows, group_by, limit=15):
    """Count rows per distinct group_by value, highest first, top `limit`. Pure.

    Feed it the ALREADY-projected rows from a validated 'group' query. Missing or blank
    values are skipped (they are not a category). Ties break alphabetically so the output
    is deterministic. Returns [{"value": <label>, "count": <n>}, ...].
    """
    counts = {}
    for r in rows:
        if not isinstance(r, dict):
            continue
        raw = r.get(group_by)
        if raw is None:
            continue
        key = str(raw).strip()
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:max(1, limit)]
    return [{"value": k, "count": c} for k, c in top]


def build_filter(filters):
    """Build a PocketBase filter expression from ALREADY-VALIDATED filters.

    Values are validated to contain no quotes/backslashes, so wrapping in double
    quotes is safe. Returns "" when there are no filters (match all).
    """
    return "&&".join(f'{f["field"]}{f["op"]}"{f["value"]}"' for f in filters)


def return_fields(collection):
    """The safe field list to request for a 'list' query on this collection."""
    return QUERYABLE[collection]["return_fields"]
