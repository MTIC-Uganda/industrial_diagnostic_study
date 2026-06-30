// One-off extraction script: imports the live ironSteel.js module and dumps
// every export to JSON, so the PocketBase migration is built from data the
// JS engine actually evaluated -- zero risk of hand-transcription error on
// data with real, carefully-checked citations.
import { PRODUCTS, CATEGORIES, TRADE_HS4, PRODUCT_HS4, RAW_MATERIAL_TRADE,
         PRODUCT_FIRMS, PHASE_PRODUCERS, PHASE_SOURCE, RAW_MATERIAL_PHASE }
  from './src/data/ironSteel.js';
import fs from 'fs';

// INPUT_KEYWORD_HS4 / INPUT_KEYWORD_PHASE and matchInputTrade/matchInputPhase
// aren't exported, so re-derive the keyword tables by reading the source file
// text directly (regex literals don't survive JSON.stringify, so capture
// .source/.flags instead of trying to import the RegExp objects themselves).
const src = fs.readFileSync('./src/data/ironSteel.js', 'utf-8');

function extractKeywordTable(constName, targetKey) {
  const re = new RegExp(`const ${constName} = \\[([\\s\\S]*?)\\n\\];`);
  const m = src.match(re);
  if (!m) throw new Error(`${constName} not found`);
  const body = m[1];
  const rowRe = /\{\s*pattern:\s*(\/(?:[^\/\\]|\\.)*\/[a-z]*),\s*(\w+):\s*"([^"]+)"\s*\}/g;
  const rows = [];
  let rm;
  while ((rm = rowRe.exec(body))) {
    const [, patternLit, , target] = rm;
    const lastSlash = patternLit.lastIndexOf('/');
    const source = patternLit.slice(1, lastSlash);
    const flags = patternLit.slice(lastSlash + 1);
    rows.push({ source, flags, [targetKey]: target });
  }
  return rows;
}

const INPUT_KEYWORD_HS4 = extractKeywordTable('INPUT_KEYWORD_HS4', 'hs4');
const INPUT_KEYWORD_PHASE = extractKeywordTable('INPUT_KEYWORD_PHASE', 'phase');

const out = {
  PRODUCTS, CATEGORIES, TRADE_HS4, PRODUCT_HS4, RAW_MATERIAL_TRADE,
  PRODUCT_FIRMS, PHASE_PRODUCERS, PHASE_SOURCE, RAW_MATERIAL_PHASE,
  INPUT_KEYWORD_HS4, INPUT_KEYWORD_PHASE,
};

fs.writeFileSync('./extracted_data.json', JSON.stringify(out, null, 2));
console.log('Extracted:');
console.log('  PRODUCTS:', Object.keys(PRODUCTS).length, 'products');
console.log('  CATEGORIES:', CATEGORIES.length);
console.log('  TRADE_HS4:', Object.keys(TRADE_HS4).length, 'codes');
console.log('  PRODUCT_HS4:', Object.keys(PRODUCT_HS4).length, 'mappings');
console.log('  RAW_MATERIAL_TRADE:', Object.keys(RAW_MATERIAL_TRADE).length, 'items');
console.log('  PRODUCT_FIRMS:', Object.keys(PRODUCT_FIRMS).length, 'products');
console.log('  PHASE_PRODUCERS:', Object.keys(PHASE_PRODUCERS).length, 'phases');
console.log('  RAW_MATERIAL_PHASE:', Object.keys(RAW_MATERIAL_PHASE).length, 'items');
console.log('  INPUT_KEYWORD_HS4:', INPUT_KEYWORD_HS4.length, 'rules');
console.log('  INPUT_KEYWORD_PHASE:', INPUT_KEYWORD_PHASE.length, 'rules');
