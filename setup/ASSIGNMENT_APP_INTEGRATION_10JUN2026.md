# Assignment: Integrate Jerome's Data into the Sankey App
**Date:** 10 June 2026
**From:** Hillary Arinda
**To:** Solomon Ariho

---

## Context (read the meeting transcript first)

Read `meeting_transcripts/industrial_diagnostic_study_10.7.2026.md` in full
before starting. Key quote from Jerome:

> "There is other data that we are currently not seeing that feeds into the
> report. Data like the current status of the iron and steel industry: how many
> industries, production figures, all those different things. I suspect that if
> you feed this discussion into Claude and ask it the different steps to take,
> it should be able to guide you on how to improve this to display all the
> different data we need."

And on integration vs combination:

> "Integrated. Because by integration it means that it could actually decompose
> what I give and put it in the right places."

---

## What Jerome built: `report/sources-of-truth.html`

Jerome has already synthesized the current-status data for all 9 chains into
an interactive HTML dashboard. Open it in your browser — it has:

1. **Value Chain Maps** — for each chain: phases (Phase I, II, III…) with a
   strength indicator per phase: green (strong/competitive), yellow (emerging/
   limited), red (gap/absent in Uganda).
2. **Chain Status + 2040 Projections** — for each chain: current imports, current
   exports, Uganda's position, the Tenfold 2040 target, and the priority rating.
3. **Key Indicators** — macro numbers: number of industries, employment, export
   value, key gaps.
4. **Critical Gap callout** — one-line summary of the single most critical gap
   per chain.

This is the data Jerome wants to see IN the Sankey app — not as a separate page.

---

## What the Sankey app currently shows

Open `app/frontend/public/graph-bundle.json` — the app shows:
- The upstream decomposition tree (Iron & Steel fully seeded; 8 others have
  estimated structure).
- Node detail panel: function, mechanism, HS codes, TradeMap trade figures.

What is MISSING from every node:
- Uganda's current production status (does Uganda have this capacity?)
- Strength indicator (strong / emerging / gap)
- Current production volume or capacity utilization
- The 2040 Tenfold target for this node

---

## Your task: integrate the two

### Step 1 — Add strength fields to the schema

Open `app/backend/schema.sql`. Add two fields to the `nodes` table:

```sql
strength        TEXT,   -- 'strong' | 'emerging' | 'gap' | NULL
strength_note   TEXT    -- short explanation of the strength rating
```

Run `python db.py` to recreate the database with the new schema (it is
idempotent — safe to run again).

### Step 2 — Update the seed scripts with strength data from Jerome's page

For each value chain, open `app/backend/seed_all_chains.py` and add
`strength` and `strength_note` to every node, matching what Jerome has in
`report/sources-of-truth.html`.

Example mapping — Iron & Steel:

| Jerome's phase (sources-of-truth) | Graph node | Strength |
|---|---|---|
| Phase I: Mining & Ore Prep | `p_ore`, `p_iron_ore` | gap |
| Phase II: Smelting/Reduction | `p_dri`, `p_sponge` | gap |
| Phase III: Steelmaking | `p_billet`, `p_bloom` | emerging |
| Phase IV: Rolling/Fabrication | `p_rebar`, `p_section` | strong |
| Phase V: Distribution | `p_trader` | strong |

Do the same mapping for all 9 chains. Use the colour coding in Jerome's HTML:
green = strong, yellow = emerging, red = gap.

### Step 3 — Add the critical gap and 2040 target to the root System node

Each root System node (e.g. `is:root` for Iron & Steel) should have:
- `strength_note` = Jerome's critical gap text (the orange warning box in his page)
- A `tenfold_target` field in `source_references` or `specifications` — the 2040
  target Jerome lists per chain.

### Step 4 — Expose strength in the Sankey visualization

Open `app/frontend/src/Sankey.jsx`. The `nodeColor()` function currently colors
by node label. Change it to also use `strength` when set:

```js
function nodeColor(n) {
  if (n.strength === 'strong')   return '#2e7d32';  // green
  if (n.strength === 'emerging') return '#f57f17';  // amber
  if (n.strength === 'gap')      return '#c62828';  // red
  return COLORS[n.label] || COLORS[n.componentType] || COLORS.other;
}
```

This means every Sankey node will be green / amber / red based on Uganda's
current position in the value chain — exactly what Jerome showed in his page,
but now inside the interactive decomposition tree.

### Step 5 — Show strength in the detail panel

Open `app/frontend/src/NodeDetail.jsx`. Add a status badge row near the top
of the panel that shows the strength indicator and the note. Mimic the style
from Jerome's page (green/yellow/red tag).

### Step 6 — Rebuild the bundle and push

```bash
cd app/backend
python db.py                # recreate schema + reseed
python wire_trademap.py     # inject live TradeMap figures
python export_bundle.py     # regenerate graph-bundle.json

cd ../frontend
npm run dev                 # verify it looks right locally
```

Push to a branch (`feat/integrate-strength-data`). CI will build, deploy to
staging, and if it looks good, auto-merge to main and push to prod.

---

## What Hillary will do in parallel

While you work on the strength integration, Hillary is:
- Setting up the deployment pipeline so the React app (not Jerome's HTML page)
  is what loads at the prod URL.
- Building Phase 2: ingestion agent (Jerome pushes data → graph.db updates
  automatically → no manual seeding required).

Your push to `feat/integrate-strength-data` will deploy automatically.
You do not need to touch the CI/CD or server configuration.

---

## Definition of done

When Jerome opens `https://tinyurl.com/28lxntmc`, he sees:
1. The Sankey diagram for each value chain
2. Nodes coloured green / amber / red by Uganda's current production status
3. Clicking any node shows the strength indicator, the gap note, and the
   TradeMap trade figures
4. The root node shows the critical gap callout and the 2040 Tenfold target

That is what Jerome described in the meeting. That is what we build.
