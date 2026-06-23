#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function arg(name, fallback) {
  const idx = process.argv.indexOf('--' + name);
  return idx >= 0 ? process.argv[idx + 1] : fallback;
}

const sourceDir = arg('source-dir', process.env.CMS_NCCI_SOURCE_DIR || '');
const version = arg('version', '2026-Q3');
const limit = Number(arg('limit', '500'));
const mode = arg('mode', 'modifier0');
const outDir = arg('out-dir', path.join('data', 'ncci', 'versions', version));
const activeDir = arg('active-dir', path.join('data', 'ncci', 'active'));
const forcedRegressionPairs = new Set([
  '44055|49000',
  '44140|44005',
  '44120|44005',
  '44310|44005',
  '44620|44005',
  '44625|44005',
  '47562|49000',
  '60240|60512'
]);

if (!sourceDir || !fs.existsSync(sourceDir)) {
  console.error('Missing --source-dir pointing to CMS Practitioner PTP zip files');
  process.exit(2);
}

const db = JSON.parse(fs.readFileSync('cpt_database.json', 'utf8'));
const existing = JSON.parse(fs.readFileSync('ncci_bundles.json', 'utf8'));
const existingPairs = new Set();
Object.entries(existing.bundles || {}).forEach(([column1, bundle]) => {
  (bundle.column2_codes || []).forEach(column2 => existingPairs.add(String(column1) + '|' + String(column2)));
});

const targetTerms = [
  'general', 'trauma', 'acute care', 'colorectal', 'colon', 'rectal', 'hernia',
  'foregut', 'esoph', 'stomach', 'gastric', 'endocrine', 'thyroid', 'parathyroid',
  'adrenal', 'hpb', 'hepato', 'liver', 'bile', 'biliary', 'gallbladder', 'pancreas',
  'small bowel', 'enter', 'append', 'breast', 'skin', 'soft tissue', 'vascular',
  'bowel', 'ostomy', 'splen'
];

function textFor(entry) {
  return [
    entry.specialty,
    entry.category,
    entry.subcategory,
    entry.code_family,
    entry.description,
    ...(entry.search_terms || [])
  ].filter(Boolean).join(' ').toLowerCase();
}

function inScope(code) {
  const entry = db[String(code)];
  if (!entry) return false;
  if (entry.category !== 'Surgery') return false;
  const haystack = textFor(entry);
  return targetTerms.some(term => haystack.includes(term));
}

function frequencyScore(entry) {
  const text = textFor(entry);
  let score = 10;
  if (/colect|colon|rect|bowel|enter|ostomy|hernia|append|chole|laparotomy|splen|thyroid|vascular/.test(text)) score += 35;
  if (/exploratory|enterolysis|adhesion|separate procedure|diagnostic laparoscopy/.test(text)) score += 35;
  if (/trauma|acute|emerg|append|small bowel|colect|hernia/.test(text)) score += 15;
  return Math.min(score, 100);
}

function parseZip(zipFile) {
  const list = spawnSync('unzip', ['-Z1', zipFile], { encoding: 'utf8' });
  if (list.status !== 0) throw new Error('Unable to list ' + zipFile + ': ' + list.stderr);
  const txtName = list.stdout.split(/\r?\n/).find(name => /\.txt$/i.test(name));
  if (!txtName) return [];
  const result = spawnSync('unzip', ['-p', zipFile, txtName], { encoding: 'utf8', maxBuffer: 256 * 1024 * 1024 });
  if (result.status !== 0) throw new Error('Unable to read ' + zipFile + ': ' + result.stderr);
  return result.stdout.split(/\r?\n/).slice(6).map(line => {
    const cols = line.split('\t');
    if (cols.length < 7) return null;
    const column1 = String(cols[0] || '').trim();
    const column2 = String(cols[1] || '').trim();
    if (!/^\d{4,5}[A-Z]?$/.test(column1) || !/^\d{4,5}[A-Z]?$/.test(column2)) return null;
    return {
      column1,
      column2,
      effective: String(cols[3] || '').trim(),
      deletion: String(cols[4] || '').trim(),
      modifier_indicator: String(cols[5] || '').trim(),
      rationale: String(cols.slice(6).join(' ') || '').trim(),
      sourceFile: txtName
    };
  }).filter(Boolean);
}

const zipFiles = fs.readdirSync(sourceDir)
  .filter(name => /\.zip$/i.test(name))
  .map(name => path.join(sourceDir, name))
  .sort();

const allPairs = zipFiles.flatMap(parseZip)
  .filter(pair => pair.deletion === '*')
  .filter(pair => mode === 'modifier0' ? pair.modifier_indicator === '0' : true)
  .filter(pair => inScope(pair.column1) && inScope(pair.column2))
  .filter(pair => !existingPairs.has(pair.column1 + '|' + pair.column2));

const ranked = allPairs.map(pair => {
  const c1 = db[pair.column1];
  const c2 = db[pair.column2];
  const selectedWrvuImpact = Number(c2.work_rvu || 0);
  const selectedPaymentImpact = Number(c2.estimated_medicare_payment || 0);
  const frequency = Math.max(frequencyScore(c1), frequencyScore(c2));
  const riskScore = Math.round((frequency * 3) + (selectedWrvuImpact * 6) + (selectedPaymentImpact / 30));
  return {
    category: 'phase1_surgical_modifier0_activation',
    column1: pair.column1,
    column1Description: c1.description,
    column2: pair.column2,
    column2Description: c2.description,
    modifier_indicator: pair.modifier_indicator,
    effective: pair.effective,
    rationale: pair.rationale || 'CMS NCCI PTP edit',
    sourceFile: pair.sourceFile,
    previousBehavior: 'No active CMS NCCI hard stop in FreeCPTCodeFinder; both selected CPT lines could contribute payable wRVU if entered together.',
    newBehavior: 'CMS NCCI modifier-0 hard stop; Column 2 remains visible as selected/performed but contributes 0.00 payable wRVU and cannot be bypassed with modifier 59/X modifiers.',
    selectedWrvuImpact: Number((Number(c1.work_rvu || 0) + Number(c2.work_rvu || 0)).toFixed(2)),
    payableWrvuImpact: Number(Number(c2.work_rvu || 0).toFixed(2)),
    selectedRevenueImpact: Number((Number(c1.estimated_medicare_payment || 0) + Number(c2.estimated_medicare_payment || 0)).toFixed(2)),
    payableRevenueImpact: Number(Number(c2.estimated_medicare_payment || 0).toFixed(2)),
    frequencyScore: frequency,
    riskScore
  };
}).sort((a, b) => b.riskScore - a.riskScore || b.payableWrvuImpact - a.payableWrvuImpact);

const selected = [];
const seenSelected = new Set();
for (const item of ranked) {
  const key = item.column1 + '|' + item.column2;
  if (forcedRegressionPairs.has(key) && !seenSelected.has(key)) {
    selected.push(item);
    seenSelected.add(key);
  }
}
for (const item of ranked) {
  if (selected.length >= limit) break;
  const key = item.column1 + '|' + item.column2;
  if (!seenSelected.has(key)) {
    selected.push(item);
    seenSelected.add(key);
  }
}

const generatedAt = new Date().toISOString();
const dataset = {
  schema: 'freecpt.ncci.ptp.v1',
  source: 'CMS NCCI Practitioner PTP',
  version,
  generatedAt,
  activationMode: 'phase1_surgical_modifier0_only',
  modifier1Activated: false,
  pairCount: selected.length,
  ptp_pairs: selected.map(item => ({
    column1: item.column1,
    column2: item.column2,
    modifier_indicator: item.modifier_indicator,
    effective: item.effective,
    rationale: item.rationale,
    description: item.column1Description + ' / ' + item.column2Description,
    sourceFile: item.sourceFile,
    risk_score: item.riskScore,
    potential_wrvu_impact: item.payableWrvuImpact,
    potential_revenue_impact: item.payableRevenueImpact
  }))
};

const audit = {
  generatedAt,
  version,
  sourceDir,
  sourceFiles: zipFiles.map(file => path.basename(file)),
  mode,
  requestedLimit: limit,
  eligibleMissingPairs: allPairs.length,
  activatedPairs: selected.length,
  modifier1Activated: false
};

fs.mkdirSync(outDir, { recursive: true });
fs.mkdirSync(activeDir, { recursive: true });
fs.writeFileSync(path.join(outDir, 'surgical-modifier0-activation-pack.json'), JSON.stringify(dataset, null, 2));
fs.writeFileSync(path.join(outDir, 'surgical-modifier0-behavior-change-list.json'), JSON.stringify({
  generatedAt,
  version,
  behaviorChangeCount: selected.length,
  forcedRegressionPairs: Array.from(forcedRegressionPairs).filter(key => seenSelected.has(key)),
  pairs: selected
}, null, 2));
fs.writeFileSync(path.join(outDir, 'import-audit.json'), JSON.stringify(audit, null, 2));
fs.writeFileSync(path.join(activeDir, 'cms_ncci_ptp_active.json'), JSON.stringify(dataset, null, 2));
fs.writeFileSync(path.join(activeDir, 'manifest.json'), JSON.stringify({
  activeVersion: version,
  activeDataset: 'cms_ncci_ptp_active.json',
  activatedAt: generatedAt,
  activationMode: dataset.activationMode,
  pairCount: selected.length,
  rollback: 'Replace data/ncci/active/cms_ncci_ptp_active.json with an empty ptp_pairs dataset or revert this branch commit, then redeploy.'
}, null, 2));

console.log(JSON.stringify({
  version,
  sourceFiles: audit.sourceFiles,
  eligibleMissingPairs: audit.eligibleMissingPairs,
  activatedPairs: selected.length,
  output: outDir
}, null, 2));
