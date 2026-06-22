#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const cptDb = JSON.parse(fs.readFileSync(path.join(repoRoot, 'cpt_database.json'), 'utf8'));
const ruleData = JSON.parse(fs.readFileSync(path.join(repoRoot, 'separate_procedure_rules.json'), 'utf8'));

const rules = (ruleData.rules || []).filter(rule => ['38100', '38101'].includes(String(rule.secondary)));
if (rules.length !== 2) throw new Error('Expected two iatrogenic splenectomy rules, found ' + rules.length);

function round2(value) {
  return Number(value.toFixed(2));
}

function code(codeValue) {
  const row = cptDb[String(codeValue)];
  if (!row) throw new Error('Missing CPT ' + codeValue);
  return row;
}

function ruleFor(secondary) {
  const rule = rules.find(item => String(item.secondary) === String(secondary));
  if (!rule) throw new Error('Missing rule for ' + secondary);
  return rule;
}

function shouldSuppress(primary, secondary, context = {}) {
  const rule = ruleFor(secondary);
  const primaryMatches = (rule.primary_codes || []).map(String).includes(String(primary));
  if (!primaryMatches) return false;
  return context.splenicIndication === 'iatrogenic_splenic_injury';
}

function evaluateCase(name, selected, contextByCode = {}) {
  const selectedRows = selected.map(code);
  const selectedWrvu = round2(selectedRows.reduce((sum, row) => sum + row.work_rvu, 0));
  const payable = [];
  const suppressed = [];

  selectedRows.forEach(row => {
    const secondary = String(row.code);
    const splenicRule = rules.find(rule => String(rule.secondary) === secondary);
    if (!splenicRule) {
      payable.push(row);
      return;
    }

    const suppressedBy = selectedRows.find(candidate => shouldSuppress(candidate.code, secondary, contextByCode[secondary] || {}));
    if (suppressedBy) {
      suppressed.push({ code: secondary, by: String(suppressedBy.code), work_rvu: row.work_rvu });
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
    name: 'positive_colectomy_total_splenectomy_iatrogenic',
    selected: ['44140', '38100'],
    contextByCode: { '38100': { splenicIndication: 'iatrogenic_splenic_injury' } },
    expectPayable: ['44140'],
    expectSuppressed: ['38100']
  },
  {
    name: 'positive_gastrectomy_total_splenectomy_iatrogenic',
    selected: ['43620', '38100'],
    contextByCode: { '38100': { splenicIndication: 'iatrogenic_splenic_injury' } },
    expectPayable: ['43620'],
    expectSuppressed: ['38100']
  },
  {
    name: 'positive_distal_pancreatectomy_total_splenectomy_iatrogenic',
    selected: ['48140', '38100'],
    contextByCode: { '38100': { splenicIndication: 'iatrogenic_splenic_injury' } },
    expectPayable: ['48140'],
    expectSuppressed: ['38100']
  },
  {
    name: 'negative_trauma_laparotomy_splenic_rupture',
    selected: ['49000', '38100'],
    contextByCode: { '38100': { splenicIndication: 'traumatic_splenic_injury' } },
    expectPayable: ['49000', '38100'],
    expectSuppressed: []
  },
  {
    name: 'negative_splenectomy_alone',
    selected: ['38100'],
    contextByCode: { '38100': { splenicIndication: 'splenic_mass' } },
    expectPayable: ['38100'],
    expectSuppressed: []
  },
  {
    name: 'negative_colectomy_pre_existing_splenic_pathology',
    selected: ['44140', '38100'],
    contextByCode: { '38100': { splenicIndication: 'pre_existing_splenic_pathology' } },
    expectPayable: ['44140', '38100'],
    expectSuppressed: []
  },
  {
    name: 'negative_separate_encounter_splenectomy',
    selected: ['44140', '38100'],
    contextByCode: { '38100': { splenicIndication: 'separate_encounter' } },
    expectPayable: ['44140', '38100'],
    expectSuppressed: []
  },
  {
    name: 'review_required_colectomy_unknown_splenic_context',
    selected: ['44140', '38100'],
    contextByCode: {},
    expectPayable: ['44140', '38100'],
    expectSuppressed: []
  },
  {
    name: 'positive_colectomy_partial_splenectomy_iatrogenic',
    selected: ['44140', '38101'],
    contextByCode: { '38101': { splenicIndication: 'iatrogenic_splenic_injury' } },
    expectPayable: ['44140'],
    expectSuppressed: ['38101']
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
  colectomy_38100_before_context: evaluateCase('before_or_unknown_context', ['44140', '38100'], {}),
  colectomy_38100_after_iatrogenic_context: evaluateCase('after_iatrogenic_context', ['44140', '38100'], {
    '38100': { splenicIndication: 'iatrogenic_splenic_injury' }
  }),
  gastrectomy_38100_after_iatrogenic_context: evaluateCase('gastrectomy_after_iatrogenic_context', ['43620', '38100'], {
    '38100': { splenicIndication: 'iatrogenic_splenic_injury' }
  }),
  distal_pancreatectomy_38100_after_iatrogenic_context: evaluateCase('distal_pancreatectomy_after_iatrogenic_context', ['48140', '38100'], {
    '38100': { splenicIndication: 'iatrogenic_splenic_injury' }
  })
};

console.log(JSON.stringify({
  status: 'pass',
  rule_count: rules.length,
  abdominal_parent_cpt_families_included: {
    gastric: ['43620', '43621', '43622', '43631', '43632', '43633', '43634', '43635', '43840'],
    small_bowel_colorectal: ['44120', '44121', '44140', '44143', '44155', '44202', '44203', '44204', '44205', '44206', '44207', '44208', '44210', '44212'],
    pancreas: ['48140', '48150', '48153'],
    exploratory_abdominal_access: ['49000']
  },
  excluded_distinct_splenic_indications: rules[0].do_not_suppress_when,
  positive_and_negative_tests: results,
  before_after_payable_wrvu_examples: examples
}, null, 2));
