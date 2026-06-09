# MTIC Value Chains App (`app/`)

An interactive value-chain decomposition explorer for the MTIC Industrial
Diagnostic Study — modelled on the structure of valuechains.ai (Productive
Capabilities Data Lab), adapted for Uganda's 9 NDP IV priority value chains.

> **Note — repo migration (2026-06-10):** This code previously lived in a
> separate repo (`MTIC-Uganda/valuechains-app`, now archived). It was merged
> here so the app and data share one repo and one CI/CD pipeline. The code is
> identical; only paths changed.

## What it does

Renders each value chain as an interactive **Sankey diagram**: a final
product/system on the left, decomposed upstream into technology types and
then into components, materials, labour, and machinery — with flow widths
weighted by cost share. Click any node to drill upstream and open a detail
panel (function, mechanism, HS codes, TradeMap trade data, sources).

## Architecture

```
app/                         (this directory, inside industrial_diagnostic_study/)
  backend/
    schema.sql               nodes + relationships tables (Neo4j-style graph in SQLite)
    db.py                    DB helpers + recursive upstream traversal
    models.py                Pydantic response models
    main.py                  REST API (mirrors valuechains.ai /api/v1 shape)
    wire_trademap.py         Reads ../data/trademap/*.csv → injects trade data into nodes
    generate_chapter.py      Reads graph.db → writes ../report/chapters/*.md
    export_bundle.py         Dumps graph.db → frontend/public/graph-bundle.json
    seed_products.py         Iron & Steel full seed
    seed_all_chains.py       All 8 remaining chains (full node taxonomy)
    requirements.txt
  frontend/                  React + d3-sankey visualization
    src/
      App.jsx                Chain/product selector, breadcrumb navigation
      Sankey.jsx             D3-sankey component with focus/hover/drill
      NodeDetail.jsx         Node detail side panel
      api.js                 Static bundle client (no backend needed)
    public/
      graph-bundle.json      Pre-built data snapshot — regenerate with export_bundle.py
  netlify.toml               Netlify build config (base = app/frontend)
```

## The single source of truth

`backend/graph.db` powers both the app and the report chapters:

```
data/trademap/*.csv  →  wire_trademap.py  →  graph nodes (live trade figures)
graph.db             →  export_bundle.py  →  frontend/public/graph-bundle.json  →  Sankey app
graph.db             →  generate_chapter.py  →  ../report/chapters/*.md
```

**Never edit `graph-bundle.json` by hand** — always regenerate with `export_bundle.py`.

## Data model

Mirrors the reverse-engineered valuechains.ai model:

- **Node** — labels: `System`, `TechnologyType`, `Component`, `Material`,
  `LaborCost`, `MachineryCost`, `AdditionalInputCost`. Properties: name,
  synonyms, function, mechanism, specifications, core_components,
  component_type (material/component/other), prevalence, price_range,
  hs_code(+description, explanation), source_references, n_iteration.
- **Relationship** — type `GROUPED_PATH`, directed upstream→downstream,
  property `weight` (cost share / prevalence, 0-1).

## Run locally

```bash
# Set up the graph database
cd app/backend
pip install -r requirements.txt
python db.py                    # creates graph.db, seeds Iron & Steel

# Wire in TradeMap data
python wire_trademap.py         # reads ../../data/trademap/*.csv

# Export static bundle for the frontend
python export_bundle.py         # writes ../frontend/public/graph-bundle.json

# Run the backend API (optional — frontend works without it via bundle)
uvicorn main:app --reload --port 8000

# Run the frontend (separate terminal)
cd ../frontend
npm install
npm run dev                     # http://localhost:5173
```

## Static build + Netlify deploy

```bash
cd app/backend
python export_bundle.py         # refresh data snapshot

cd ../frontend
npm run build                   # static site → frontend/dist/
```

`netlify.toml` at the repo root sets `base = "app/frontend"`. Connecting the
`industrial_diagnostic_study` repo to a Netlify site gives automatic deploys
on every push to `main`.

## Current data state

| Chain | Status |
|---|---|
| Iron & Steel | Fully seeded (real node data, scaffold proven) |
| Copper & Allied Metals | Full taxonomy, estimated weights — needs real figures |
| Automotive | Full taxonomy, estimated weights — needs real figures |
| Textiles & Garments | Full taxonomy, estimated weights — needs real figures |
| Pharmaceuticals | Full taxonomy, estimated weights — needs real figures |
| Petrochemicals & Fertilizers | Full taxonomy, estimated weights — needs real figures |
| Sugar & Confectionery | Full taxonomy, estimated weights — needs real figures |
| Plastics & Packaging | Full taxonomy, estimated weights — needs real figures |
| Cement & Building Materials | Full taxonomy, estimated weights — needs real figures |

Solomon's current task: replace estimated weights with real figures from
Jerome's documents in `../../data/`. See `seed_all_chains.py`.
