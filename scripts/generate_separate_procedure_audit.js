#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const cptDb = JSON.parse(fs.readFileSync(path.join(repoRoot, 'cpt_database.json'), 'utf8'));
const ruleData = JSON.parse(fs.readFileSync(path.join(repoRoot, 'separate_procedure_rules.json'), 'utf8'));
const outputPath = path.join(repoRoot, 'separate-procedure-audit.json');
const existingReport = fs.existsSync(outputPath)
  ? JSON.parse(fs.readFileSync(outputPath, 'utf8'))
  : null;
const conversionFactor = 32.3465;

function money(value) {
  return Number(value.toFixed(2));
}

function wrvu(value) {
  return Number(value.toFixed(2));
}

const separateProcedureCodes = Object.values(cptDb)
  .filter(entry => /\bseparate procedure\b/i.test(entry.description || ''))
  .map(entry => ({
    code: entry.code,
    description: entry.description,
    work_rvu: entry.work_rvu || 0,
    estimated_medicare_payment: money(entry.estimated_medicare_payment || ((entry.total_rvu || 0) * conversionFactor))
  }))
  .sort((a, b) => String(a.code).localeCompare(String(b.code)));

const affectedRelationships = (ruleData.rules || []).map(rule => {
  const primary = cptDb[rule.primary];
  const secondary = cptDb[rule.secondary];
  if (!primary || !secondary) {
    throw new Error(`Rule references unloaded CPT code: ${rule.primary} / ${rule.secondary}`);
  }

  const selectedWrvu = wrvu((primary.work_rvu || 0) + (secondary.work_rvu || 0));
  const payableWrvu = wrvu(primary.work_rvu || 0);
  const selectedPayment = money((primary.estimated_medicare_payment || 0) + (secondary.estimated_medicare_payment || 0));
  const payablePayment = money(primary.estimated_medicare_payment || ((primary.total_rvu || 0) * conversionFactor));

  return {
    cpt_pair: [rule.primary, rule.secondary],
    primary: {
      code: rule.primary,
      description: primary.description,
      work_rvu: wrvu(primary.work_rvu || 0)
    },
    secondary: {
      code: rule.secondary,
      description: secondary.description,
      work_rvu: wrvu(secondary.work_rvu || 0)
    },
    selected_wrvus: selectedWrvu,
    correct_payable_wrvus: payableWrvu,
    suppressed_wrvus: wrvu(selectedWrvu - payableWrvu),
    selected_reimbursement: selectedPayment,
    correct_payable_reimbursement: payablePayment,
    suppressed_reimbursement: money(selectedPayment - payablePayment),
    rule_applied: rule
  };
});

const report = {
  generated_at: process.env.AUDIT_GENERATED_AT || existingReport?.generated_at || new Date().toISOString(),
  rule_file: 'separate_procedure_rules.json',
  loaded_cpt_count: Object.keys(cptDb).length,
  separate_procedure_code_count: separateProcedureCodes.length,
  affected_relationship_count: affectedRelationships.length,
  separate_procedure_codes: separateProcedureCodes,
  affected_relationships: affectedRelationships
};

fs.writeFileSync(outputPath, JSON.stringify(report, null, 2) + '\n');

console.log(JSON.stringify({
  output: 'separate-procedure-audit.json',
  loaded_cpt_count: report.loaded_cpt_count,
  separate_procedure_code_count: report.separate_procedure_code_count,
  affected_relationship_count: report.affected_relationship_count,
  affected_relationships: affectedRelationships.map(item => ({
    cpt_pair: item.cpt_pair,
    selected_wrvus: item.selected_wrvus,
    correct_payable_wrvus: item.correct_payable_wrvus,
    suppressed_wrvus: item.suppressed_wrvus
  }))
}, null, 2));
