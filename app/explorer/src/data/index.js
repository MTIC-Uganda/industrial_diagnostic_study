// Value Chain Explorer — combined data index
// Merges all 9 chain data files into a single set of exports for App.jsx
// Source files: ironSteel.js, copper.js, automotive.js, textiles.js, pharma.js,
//               petrochem.js, sugar.js, plastics.js, cement.js

import * as ironSteel from "./ironSteel.js";
import * as copper    from "./copper.js";
import * as automotive from "./automotive.js";
import * as textiles  from "./textiles.js";
import * as pharma    from "./pharma.js";
import * as petrochem from "./petrochem.js";
import * as sugar     from "./sugar.js";
import * as plastics  from "./plastics.js";
import * as cement    from "./cement.js";

const ALL_CHAINS = [
  ironSteel,
  copper,
  automotive,
  textiles,
  pharma,
  petrochem,
  sugar,
  plastics,
  cement,
];

// Merge all PRODUCTS objects (keyed by slug — no collisions expected)
const PRODUCTS = Object.assign({}, ...ALL_CHAINS.map(c => c.PRODUCTS));

// Merge all CATEGORIES arrays (each chain contributes its own category groups)
const CATEGORIES = ALL_CHAINS.flatMap(c => c.CATEGORIES);

// Merge all TRADE_HS4 objects (keyed by HS4 string)
const TRADE_HS4 = Object.assign({}, ...ALL_CHAINS.map(c => c.TRADE_HS4));

// Merge all PRODUCT_HS4 maps (product slug → HS4 string)
const PRODUCT_HS4 = Object.assign({}, ...ALL_CHAINS.map(c => c.PRODUCT_HS4));

// Merge all RAW_MATERIAL_TRADE maps (material name → trade object)
const RAW_MATERIAL_TRADE = Object.assign({}, ...ALL_CHAINS.map(c => c.RAW_MATERIAL_TRADE));

// Merge all RAW_MATERIAL_PHASE maps (material name → phase key)
const RAW_MATERIAL_PHASE = Object.assign({}, ...ALL_CHAINS.map(c => c.RAW_MATERIAL_PHASE));

// Merge all PRODUCT_FIRMS maps (product slug → firm info)
const PRODUCT_FIRMS = Object.assign({}, ...ALL_CHAINS.map(c => c.PRODUCT_FIRMS));

// Merge all PHASE_PRODUCERS maps (chain-prefixed phase key → producer info)
// Keys are namespaced per chain (is_I, cu_V, au_III, tx_I, ph_II, pc_IV, sg_I, pl_II, cm_I …)
// so no collisions occur across chains.
const PHASE_PRODUCERS = Object.assign({}, ...ALL_CHAINS.map(c => c.PHASE_PRODUCERS));

// PHASE_SOURCE: multi-chain combined citation
const PHASE_SOURCE = ALL_CHAINS
  .map(c => c.PHASE_SOURCE)
  .filter(Boolean)
  .join(" · ");

// INPUT_KEYWORD_HS4/PHASE are not exported by chain files (they're internal).
// Delegate to each chain's own matcher functions instead, which use their
// own keyword arrays and TRADE_HS4/PHASE_PRODUCERS correctly.
function matchInputTrade(text) {
  for (const chain of ALL_CHAINS) {
    const result = chain.matchInputTrade?.(text);
    if (result) return result;
  }
  return null;
}

function matchInputPhase(text) {
  for (const chain of ALL_CHAINS) {
    const result = chain.matchInputPhase?.(text);
    if (result) return result;
  }
  return null;
}

export {
  PRODUCTS,
  CATEGORIES,
  TRADE_HS4,
  PRODUCT_HS4,
  RAW_MATERIAL_TRADE,
  matchInputTrade,
  matchInputPhase,
  PRODUCT_FIRMS,
  PHASE_PRODUCERS,
  PHASE_SOURCE,
  RAW_MATERIAL_PHASE,
};
