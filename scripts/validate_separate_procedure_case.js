#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const cptDb = JSON.parse(fs.readFileSync(path.join(repoRoot, 'cpt_database.json'), 'utf8'));
const ruleData = JSON.parse(fs.readFileSync(path.join(repoRoot, 'separate_procedure_rules.json'), 'utf8'));

function round2(value) {
  return Number(value.toFixed(2));
}

const rule = (ruleData.rules || []).find(item => item.primary === '44005' && item.secondary === '49000');
if (!rule) throw new Error('Missing separate-procedure rule for 44005 + 49000');

const primary = cptDb[rule.primary];
const secondary = cptDb[rule.secondary];
if (!primary || !secondary) throw new Error('Missing CPT database entries for validation case');

const selectedWrvu = round2(primary.work_rvu + secondary.work_rvu);
const payableWrvu = round2(primary.work_rvu);
const suppressedWrvu = round2(secondary.work_rvu);
const payablePayment = round2(primary.estimated_medicare_payment);

const expected = {
  selectedWrvu: 30.23,
  payableWrvu: 18,
  suppressedWrvu: 12.23
};

const actual = { selectedWrvu, payableWrvu, suppressedWrvu, payablePayment };
for (const key of Object.keys(expected)) {
  if (actual[key] !== expected[key]) {
    throw new Error(`${key} expected ${expected[key]} but got ${actual[key]}`);
  }
}

console.log(JSON.stringify({
  status: 'pass',
  case: '44005 + 49000',
  selected_procedures: ['44005', '49000'],
  selected_wrvus: selectedWrvu,
  payable_wrvus: payableWrvu,
  suppressed_wrvus: suppressedWrvu,
  payable_reimbursement: payablePayment,
  rule_applied: rule
}, null, 2));
