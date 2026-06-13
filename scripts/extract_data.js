/**
 * One-time extraction: pull FACTORIES, chains, CHAIN_COLORS from the HTML
 * and write them as clean JSON files into data/dashboard/.
 *
 *   node scripts/extract_data.js
 */
const fs   = require('fs');
const path = require('path');

const html = fs.readFileSync('report/sources-of-truth.html', 'utf8');

// ── Helpers ───────────────────────────────────────────────────────────────────
function extract(varName, html) {
  // Find "const <varName> = <value>;" where value starts with [ or {
  const re = new RegExp(`const ${varName}\\s*=\\s*([\\[\\{])`, 's');
  const m  = re.exec(html);
  if (!m) throw new Error(`${varName} not found`);

  const start = m.index + m[0].length - 1;  // position of opening bracket
  const open  = html[start];
  const close = open === '[' ? ']' : '}';
  let depth = 0, i = start;

  for (; i < html.length; i++) {
    if (html[i] === open)  depth++;
    if (html[i] === close) { depth--; if (depth === 0) break; }
  }

  const jsSource = html.slice(start, i + 1);

  // Evaluate in a sandboxed scope
  const fn = new Function(`return ${jsSource};`);
  return fn();
}

const outDir = path.join('data', 'dashboard');
fs.mkdirSync(outDir, { recursive: true });

// ── 1. FACTORIES ──────────────────────────────────────────────────────────────
const FACTORIES = extract('FACTORIES', html);
console.log(`Extracted ${FACTORIES.length} factories`);

// Write JSON (raw backup)
fs.writeFileSync(path.join(outDir, 'factories.json'),
  JSON.stringify(FACTORIES, null, 2), 'utf8');

// Write CSV
const fields = ['name','chain','lat','lng','loc','products',
                'capacity_installed','capacity_utilised','employees',
                'est','ownership','exports'];

function csvRow(obj) {
  return fields.map(f => {
    const v = String(obj[f] ?? '—');
    // Wrap in quotes if it contains comma, newline, or quote
    return /[,"\n]/.test(v) ? `"${v.replace(/"/g, '""')}"` : v;
  }).join(',');
}

const csvLines = [fields.join(','), ...FACTORIES.map(csvRow)];
fs.writeFileSync(path.join(outDir, 'factories.csv'),
  csvLines.join('\n'), 'utf8');
console.log(`Written data/dashboard/factories.csv`);

// ── 2. CHAIN_COLORS ───────────────────────────────────────────────────────────
const CHAIN_COLORS = extract('CHAIN_COLORS', html);
fs.writeFileSync(path.join(outDir, 'chain_colors.json'),
  JSON.stringify(CHAIN_COLORS, null, 2), 'utf8');
console.log(`Written data/dashboard/chain_colors.json  (${Object.keys(CHAIN_COLORS).length} chains)`);

// ── 3. chains (status + map data) ─────────────────────────────────────────────
const chains = extract('chains', html);
console.log(`Extracted ${chains.length} chain status objects`);
fs.writeFileSync(path.join(outDir, 'chains.json'),
  JSON.stringify(chains, null, 2), 'utf8');
console.log(`Written data/dashboard/chains.json`);

console.log('\nExtraction complete. Files in data/dashboard/');
