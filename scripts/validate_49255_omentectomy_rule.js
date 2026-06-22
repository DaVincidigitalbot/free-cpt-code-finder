#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const cptDb = JSON.parse(fs.readFileSync(path.join(repoRoot, 'cpt_database.json'), 'utf8'));
const ruleData = JSON.parse(fs.readFileSync(path.join(repoRoot, 'separate_procedure_rules.json'), 'utf8'));

const rule = (ruleData.rules || []).find(item => item.id === 'omentectomy-integral-to-abdominal-oncologic-debulking');
if (!rule) throw new Error('Missing 49255 omentectomy/debulking rule');
if (String(rule.secondary) !== '49255') throw new Error('Expected secondary CPT 49255');

function round2(value) {
  return Number(value.toFixed(2));
}

function code(codeValue) {
  const row = cptDb[String(codeValue)];
  if (!row) throw new Error('Missing CPT ' + codeValue);
  return row;
}

function contextValue(context = {}) {
  return String(
    context.omentectomyContext ||
    context.omentectomy_context ||
    context.omentalIndication ||
    context.omental_indication ||
    context.indication ||
    ''
  ).trim();
}

function shouldSuppress(primary, secondary, contextByCode = {}) {
  if (String(secondary) !== '49255') return false;
  if (!(rule.primary_codes || []).map(String).includes(String(primary))) return false;
  const context = contextByCode['49255'] || {};
  const value = contextValue(context);
  if ((rule.do_not_suppress_when || []).includes(value)) return false;
  return ((rule.suppress_when && rule.suppress_when.omentectomy_context) || []).includes(value);
}

function evaluateCase(name, selected, contextByCode = {}) {
  const selectedRows = selected.map(code);
  const selectedWrvu = round2(selectedRows.reduce((sum, row) => sum + row.work_rvu, 0));
  const payable = [];
  const suppressed = [];

  selectedRows.forEach(row => {
    if (String(row.code) !== '49255') {
      payable.push(row);
      return;
    }
    const suppressedBy = selectedRows.find(candidate => shouldSuppress(candidate.code, row.code, contextByCode));
    if (suppressedBy) {
      suppressed.push({ code: '49255', by: String(suppressedBy.code), work_rvu: row.work_rvu });
    } else {
      payable.push(row);
    }
  });

  return {
    name,
    selected,
    contextByCode,
    selected_wrvus: selectedWrvu,
    payable_procedures: payable.map(row => String(row.code)),
    payable_wrvus: round2(payable.reduce((sum, row) => sum + row.work_rvu, 0)),
    suppressed_procedures: suppressed,
    suppressed_wrvus: round2(suppressed.reduce((sum, row) => sum + row.work_rvu, 0))
  };
}

const cases = [
  {
    name: 'positive_bso_hysterectomy_omentectomy_debulking',
    selected: ['58952', '49255'],
    contextByCode: { '49255': { omentectomyContext: 'cytoreduction_debulking' } },
    expectPayable: ['58952'],
    expectSuppressed: ['49255']
  },
  {
    name: 'positive_bso_total_omentectomy_included_parent',
    selected: ['58956', '49255'],
    contextByCode: { '49255': { omentectomyContext: 'included_in_parent_operation' } },
    expectPayable: ['58956'],
    expectSuppressed: ['49255']
  },
  {
    name: 'positive_intra_abdominal_tumor_resection_integral_omentectomy',
    selected: ['49203', '49255'],
    contextByCode: { '49255': { omentectomyContext: 'incidental_integral_same_abdominal_operation' } },
    expectPayable: ['49203'],
    expectSuppressed: ['49255']
  },
  {
    name: 'negative_omentectomy_alone',
    selected: ['49255'],
    contextByCode: { '49255': { omentalIndication: 'omental_mass' } },
    expectPayable: ['49255'],
    expectSuppressed: []
  },
  {
    name: 'negative_unknown_context_review_required',
    selected: ['58952', '49255'],
    contextByCode: {},
    expectPayable: ['58952', '49255'],
    expectSuppressed: []
  },
  {
    name: 'negative_distinct_omental_mass',
    selected: ['58952', '49255'],
    contextByCode: { '49255': { omentalIndication: 'omental_mass' } },
    expectPayable: ['58952', '49255'],
    expectSuppressed: []
  },
  {
    name: 'negative_separate_encounter',
    selected: ['58952', '49255'],
    contextByCode: { '49255': { encounter: 'separate_encounter' } },
    expectPayable: ['58952', '49255'],
    expectSuppressed: []
  }
];

const results = cases.map(test => {
  const actual = evaluateCase(test.name, test.selected, test.contextByCode);
  const payableOk = JSON.stringify(actual.payable_procedures) === JSON.stringify(test.expectPayable);
  const suppressedOk = JSON.stringify(actual.suppressed_procedures.map(item => item.code)) === JSON.stringify(test.expectSuppressed);
  if (!payableOk || !suppressedOk) {
    throw new Error(test.name + ' failed: ' + JSON.stringify({ actual, expected: test }, null, 2));
  }
  return actual;
});

const examples = {
  unknown_context: evaluateCase('unknown_context', ['58952', '49255'], {}),
  debulking_context: evaluateCase('debulking_context', ['58952', '49255'], {
    '49255': { omentectomyContext: 'cytoreduction_debulking' }
  }),
  distinct_omental_mass: evaluateCase('distinct_omental_mass', ['58952', '49255'], {
    '49255': { omentalIndication: 'omental_mass' }
  })
};

console.log(JSON.stringify({
  status: 'pass',
  rule_id: rule.id,
  rule_status: rule.status,
  parent_cpt_count: rule.primary_codes.length,
  parent_cpt_codes: rule.primary_codes,
  escape_hatch_contexts: rule.do_not_suppress_when,
  suppressible_contexts: rule.suppress_when.omentectomy_context,
  positive_and_negative_tests: results,
  before_after_payable_wrvu_examples: examples
}, null, 2));
