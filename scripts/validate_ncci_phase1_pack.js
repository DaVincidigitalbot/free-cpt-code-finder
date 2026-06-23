#!/usr/bin/env node
const fs = require('fs');

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

const active = readJson('data/ncci/active/cms_ncci_ptp_active.json');
const manifest = readJson('data/ncci/active/manifest.json');
const audit = readJson('data/ncci/versions/2026-Q3/import-audit.json');
const behavior = readJson('data/ncci/versions/2026-Q3/surgical-modifier0-behavior-change-list.json');

const requiredPairs = [
  '44055|49000',
  '44140|44005',
  '44120|44005',
  '44310|44005',
  '44620|44005',
  '44625|44005'
];

const failures = [];
const activePairs = new Set((active.ptp_pairs || []).map(pair => pair.column1 + '|' + pair.column2));

if (active.schema !== 'freecpt.ncci.ptp.v1') failures.push('Unexpected active schema');
if (active.version !== '2026-Q3') failures.push('Unexpected active CMS version');
if (active.modifier1Activated !== false) failures.push('Phase 1 must not activate modifier-1 edits');
if ((active.ptp_pairs || []).some(pair => String(pair.modifier_indicator) !== '0')) failures.push('Active dataset contains a non-modifier-0 pair');
if (active.pairCount !== 500 || (active.ptp_pairs || []).length !== 500) failures.push('Active dataset must contain exactly 500 Phase 1 pairs');
if (manifest.activeVersion !== active.version) failures.push('Manifest activeVersion does not match active dataset');
if (manifest.pairCount !== active.pairCount) failures.push('Manifest pairCount does not match active dataset');
if (audit.activatedPairs !== active.pairCount) failures.push('Import audit activatedPairs does not match active dataset');
if (behavior.behaviorChangeCount !== active.pairCount) failures.push('Behavior-change count does not match active dataset');

for (const key of requiredPairs) {
  if (!activePairs.has(key)) failures.push('Missing required Phase 1 regression pair ' + key);
}

for (const pair of behavior.pairs || []) {
  if (!pair.previousBehavior || !pair.newBehavior) failures.push('Missing behavior explanation for ' + pair.column1 + '|' + pair.column2);
  if (typeof pair.selectedWrvuImpact !== 'number' || typeof pair.payableWrvuImpact !== 'number') failures.push('Missing wRVU impact for ' + pair.column1 + '|' + pair.column2);
}

const report = {
  checkedAt: new Date().toISOString(),
  activeVersion: active.version,
  pairCount: active.pairCount,
  modifier1Activated: active.modifier1Activated,
  requiredPairsPresent: requiredPairs.filter(key => activePairs.has(key)),
  failures
};

fs.mkdirSync('qa_artifacts/ncci_phase1_surgical_pack_2026_06_23', { recursive: true });
fs.writeFileSync('qa_artifacts/ncci_phase1_surgical_pack_2026_06_23/regression-validation.json', JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));

if (failures.length) process.exit(1);
