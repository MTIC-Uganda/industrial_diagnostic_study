-- MTIC Value Chains — graph store in SQLite
-- Mirrors the valuechains.ai Neo4j model: nodes + directed weighted relationships.

PRAGMA foreign_keys = ON;

-- A node is a System, TechnologyType, Component, Material, LaborCost, etc.
CREATE TABLE IF NOT EXISTS nodes (
    id              TEXT PRIMARY KEY,          -- stable id, e.g. "iron-steel:rebar"
    value_chain_id  TEXT NOT NULL,             -- root id this node belongs to
    label           TEXT NOT NULL,             -- System | TechnologyType | Component | Material | LaborCost | MachineryCost | AdditionalInputCost
    name            TEXT NOT NULL,
    component_type  TEXT,                       -- material | component | other
    n_iteration     INTEGER DEFAULT 0,         -- layer depth from root (0 = root)

    function        TEXT,
    mechanism       TEXT,
    specifications  TEXT,
    prevalence      TEXT,
    price_range     TEXT,
    price_range_unit TEXT,

    synonyms        TEXT,                       -- JSON array
    core_components TEXT,                       -- JSON array
    hs_code         TEXT,                       -- JSON array of HS codes
    hs_code_description TEXT,                    -- JSON array
    hs_code_explanation TEXT,                    -- JSON array
    source_references   TEXT,                    -- JSON array

    -- MTIC-specific: live trade data pulled from ITC TradeMap
    trademap_data   TEXT                         -- JSON: {exports:[...], imports:[...], source}
);

-- A directed, weighted edge: start (upstream input) -> end (downstream product).
-- Traversing "incoming" = walking upstream from a product to its inputs.
CREATE TABLE IF NOT EXISTS relationships (
    id            TEXT PRIMARY KEY,
    type          TEXT NOT NULL DEFAULT 'GROUPED_PATH',
    start_node_id TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,  -- upstream
    end_node_id   TEXT NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,  -- downstream
    weight        REAL NOT NULL DEFAULT 0       -- cost share / prevalence, 0..1
);

CREATE INDEX IF NOT EXISTS idx_rel_end   ON relationships(end_node_id);
CREATE INDEX IF NOT EXISTS idx_rel_start ON relationships(start_node_id);
CREATE INDEX IF NOT EXISTS idx_nodes_vc  ON nodes(value_chain_id);

-- Roots view: a value chain is any node with no outgoing GROUPED_PATH
-- (i.e. it is never an upstream input to something else) AND label = System.
