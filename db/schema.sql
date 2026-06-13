-- ═══════════════════════════════════════════════════════════════════════════
-- MTIC Industrial Diagnostic Study — Supabase schema
--
-- Run this once in the Supabase SQL editor:
--   Dashboard → SQL Editor → paste and run
-- ═══════════════════════════════════════════════════════════════════════════

-- ── Value chains ─────────────────────────────────────────────────────────────
-- One row per value chain (9 now; grows as more chains are added).
-- Simple columns for the data entry person to fill in a table editor.
-- Complex nested data (phases, constraints) stored as JSONB.

CREATE TABLE IF NOT EXISTS value_chains (
  id              text PRIMARY KEY,                  -- slug: 'iron-steel', 'copper'
  name            text NOT NULL UNIQUE,
  color           text NOT NULL DEFAULT '#1565c0',   -- hex colour for map dots + UI
  display_order   int  NOT NULL DEFAULT 0,

  -- Overview tab: chain summary table
  key_import_2024 text,
  key_export_2024 text,
  position_tag    text,
  position_color  text CHECK (position_color  IN ('green','amber','red')),
  target_2040     text,
  priority_tag    text,
  priority_color  text CHECK (priority_color  IN ('red','blue','green','amber')),

  -- Value chain map tab
  map_title       text,
  map_description text,
  map_gap         text,
  map_phases      jsonb NOT NULL DEFAULT '[]',
  -- Each phase object: {name, label, detail, strength, stat}
  -- strength values: 'gap' | 'emerging' | 'moderate' | 'strong'

  -- Chain status tab (these are complex; edited as JSON in Supabase table editor)
  status_current      jsonb NOT NULL DEFAULT '[]',
  -- Each item: {label, value, color}  — color: 'blue'|'green'|'amber'|'red'

  status_companies    text[] NOT NULL DEFAULT '{}',

  status_constraints  jsonb NOT NULL DEFAULT '[]',
  -- Each item: {label, w}  — w: 'w5' (critical) … 'w1' (minor)

  status_priorities   text[] NOT NULL DEFAULT '{}',
  -- Ordered list of priority action strings

  status_proj         jsonb NOT NULL DEFAULT '{}',
  -- Object: {title, rows: [{label, current, target}]}

  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);

-- ── Facilities (factories) ────────────────────────────────────────────────────
-- One row per manufacturing facility.
-- chain_id links to value_chains — edit chain name once, all facilities follow.

CREATE TABLE IF NOT EXISTS facilities (
  id                  uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  chain_id            text NOT NULL REFERENCES value_chains(id) ON DELETE RESTRICT,
  name                text NOT NULL,
  lat                 numeric(9,6),
  lng                 numeric(9,6),
  location            text,
  products            text,
  capacity_installed  text,
  capacity_utilised   text,
  employees           text,
  established         text,
  ownership           text,
  exports             text,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS facilities_chain_idx ON facilities (chain_id);

-- ── KPI indicators ────────────────────────────────────────────────────────────
-- Six top-level KPI cards on the Overview tab.
-- Jerome updates current_value, ndp_value, tenfold_value as figures change.

CREATE TABLE IF NOT EXISTS kpi_indicators (
  id              text PRIMARY KEY,   -- slug: 'manufacturing_gdp'
  label           text NOT NULL,
  current_value   text,
  current_pct     int,                -- bar width in 0-100 scale (relative to tenfold)
  ndp_value       text,
  ndp_pct         int,
  tenfold_value   text,
  tenfold_pct     int,
  sub_value       text,               -- HTML string shown below the big number
  display_order   int NOT NULL DEFAULT 0
);

-- ── Row Level Security ────────────────────────────────────────────────────────
-- The anon key (safe to expose in CI) can only SELECT.
-- INSERT/UPDATE/DELETE requires the service role key (admin only).

ALTER TABLE value_chains   ENABLE ROW LEVEL SECURITY;
ALTER TABLE facilities      ENABLE ROW LEVEL SECURITY;
ALTER TABLE kpi_indicators  ENABLE ROW LEVEL SECURITY;

CREATE POLICY "public read value_chains"
  ON value_chains FOR SELECT USING (true);

CREATE POLICY "public read facilities"
  ON facilities FOR SELECT USING (true);

CREATE POLICY "public read kpi_indicators"
  ON kpi_indicators FOR SELECT USING (true);

-- ── Auto-update updated_at ────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER value_chains_updated_at
  BEFORE UPDATE ON value_chains
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER facilities_updated_at
  BEFORE UPDATE ON facilities
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
