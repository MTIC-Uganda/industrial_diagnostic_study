# Value Chain Explorer

Interactive drill-down through a value chain's finished products and their full upstream
chains — every stage (raw material -> ironmaking -> steelmaking -> casting -> rolling ->
finishing/coating) shown as a card with three tabs: **Inputs**, **Technology**, **Professionals**.

Sibling app to `app/frontend` (the Sankey value-chain map), but a different interaction model
(sidebar product picker + linear chain-of-cards rather than a network diagram) and a different
styling approach (Tailwind utility classes here; `app/frontend` is plain CSS) — kept separate
rather than merged into `app/frontend`.

v1 covers **Iron & Steel only** (12 finished products: galvanized sheet, Galvalume, pre-painted
coil, tinplate/ECCS, cold-rolled, hot-rolled, plate, rebar, wire rod, merchant bar, structural
sections, rail, sheet piling, welded pipe, seamless pipe).

## Run locally

```bash
npm install
npm run dev        # http://localhost:3001
```

## Build

```bash
npm run build
```

Outputs a single self-contained `index.html` to `../../report/explorer-dist/`, then copies it to
`../../report/explorer.html` — the file `report/sources-of-truth.template.html` iframes under the
"Value Chain Explorer" tab. Same single-file pattern as `app/frontend` -> `report/sankey.html`.

## Adding the next value chain

1. Create `src/data/<chain>.js` following the shape in `src/data/ironSteel.js`: stage objects
   (`{ id, stage, label, color, textColor, inputs, technology, skills }`, plus the `dual`/`triple`/
   `groups`/`rawMaterials` variants for branching routes or raw-material lists), a `PRODUCTS` map
   keyed by product id, and a `CATEGORIES` array grouping those product ids.
2. In `src/App.jsx`, import the new file's `PRODUCTS`/`CATEGORIES` and merge them into the
   existing ones (or extend `App.jsx` to accept multiple chain modules if/when there's more than
   one chain — not needed yet for a single additional chain).
3. `npm run build`, then regenerate the dashboard (`python ../../scripts/generate_dashboard.py`
   from the repo root) and check the new chain's products appear under the Explorer tab.

## Deployment

No manual deploy step. Push to a branch — `.github/workflows/deploy.yml` builds this app
alongside `app/frontend`, deploys to `staging.midd-ug.com`, health-checks, and auto-promotes to
`midd-ug.com` once staging is healthy (same pipeline the Sankey app already uses).
