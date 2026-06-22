#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const cptDb = JSON.parse(fs.readFileSync(path.join(repoRoot, 'cpt_database.json'), 'utf8'));
const ruleData = JSON.parse(fs.readFileSync(path.join(repoRoot, 'separate_procedure_rules.json'), 'utf8'));

const rule = (ruleData.rules || []).find(item => item.id === 'diagnostic-knee-arthroscopy-same-knee-surgical-arthroscopy');
if (!rule) throw new Error('Missing 29870 same-knee surgical arthroscopy rule');
if (String(rule.secondary) !== '29870') throw new Error('Expected secondary CPT 29870');

function round2(value) {
  return Number(value.toFixed(2));
}

function code(codeValue) {
  const row = cptDb[String(codeValue)];
  if (!row) throw new Error('Missing CPT ' + codeValue);
  return row;
}

function truthyContext(value) {
  return value === true || value === 'true' || value === 'yes' || value === 'same' || value === 1 || value === '1';
}

function distinctContext(context = {}) {
  if (
    context.sameKnee === false ||
    context.same_knee === false ||
    context.sameAnatomicSite === false ||
    context.same_anatomic_site === false
  ) return true;
  const values = [
    context.relationship,
    context.kneeRelationship,
    context.knee_relationship,
    context.indication,
    context.diagnosticIndication,
    context.diagnostic_indication,
    context.encounter,
    context.session
  ].map(value => String(value || '').trim()).filter(Boolean);
  return values.some(value => (rule.do_not_suppress_when || []).includes(value));
}

function sameKnee(primaryCode, contextByCode = {}) {
  const secondaryContext = contextByCode['29870'] || {};
  const primaryContext = contextByCode[String(primaryCode)] || {};
  if (
    truthyContext(secondaryContext.sameKnee) ||
    truthyContext(secondaryContext.same_knee) ||
    truthyContext(secondaryContext.sameAnatomicSite) ||
    truthyContext(secondaryContext.same_anatomic_site)
  ) return true;
  const secondarySide = String(secondaryContext.side || secondaryContext.kneeSide || secondaryContext.knee_side || '').toUpperCase();
  const primarySide = String(primaryContext.side || primaryContext.kneeSide || primaryContext.knee_side || '').toUpperCase();
  return !!primarySide && primarySide === secondarySide && (primarySide === 'RT' || primarySide === 'LT');
}

function shouldSuppress(primaryCode, contextByCode = {}) {
  if (!(rule.primary_codes || []).map(String).includes(String(primaryCode))) return false;
  const secondaryContext = contextByCode['29870'] || {};
  if (distinctContext(secondaryContext)) return false;
  return sameKnee(primaryCode, contextByCode);
}

function evaluateCase(name, selected, contextByCode = {}) {
  const selectedRows = selected.map(code);
  const selectedWrvu = round2(selectedRows.reduce((sum, row) => sum + row.work_rvu, 0));
  const payable = [];
  const suppressed = [];

  selectedRows.forEach(row => {
    if (String(row.code) !== '29870') {
      payable.push(row);
      return;
    }
    const suppressedBy = selectedRows.find(candidate => shouldSuppress(candidate.code, contextByCode));
    if (suppressedBy) {
      suppressed.push({ code: '29870', by: String(suppressedBy.code), work_rvu: row.work_rvu });
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
    name: 'positive_meniscectomy_same_knee_explicit_context',
    selected: ['29881', '29870'],
    contextByCode: { '29870': { sameKnee: true } },
    expectPayable: ['29881'],
    expectSuppressed: ['29870']
  },
  {
    name: 'positive_acl_same_knee_matching_laterality_context',
    selected: ['29888', '29870'],
    contextByCode: { '29888': { side: 'RT' }, '29870': { side: 'RT' } },
    expectPayable: ['29888'],
    expectSuppressed: ['29870']
  },
  {
    name: 'positive_lavage_same_knee_same_anatomic_site',
    selected: ['29871', '29870'],
    contextByCode: { '29870': { same_anatomic_site: true } },
    expectPayable: ['29871'],
    expectSuppressed: ['29870']
  },
  {
    name: 'negative_contralateral_knee',
    selected: ['29881', '29870'],
    contextByCode: { '29881': { side: 'RT' }, '29870': { side: 'LT', kneeRelationship: 'contralateral_knee' } },
    expectPayable: ['29881', '29870'],
    expectSuppressed: []
  },
  {
    name: 'negative_separate_encounter',
    selected: ['29881', '29870'],
    contextByCode: { '29870': { encounter: 'separate_encounter' } },
    expectPayable: ['29881', '29870'],
    expectSuppressed: []
  },
  {
    name: 'negative_diagnostic_arthroscopy_alone',
    selected: ['29870'],
    contextByCode: { '29870': { indication: 'diagnostic_arthroscopy_alone' } },
    expectPayable: ['29870'],
    expectSuppressed: []
  },
  {
    name: 'review_required_unknown_same_knee_context',
    selected: ['29881', '29870'],
    contextByCode: {},
    expectPayable: ['29881', '29870'],
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
  meniscectomy_29870_unknown_context: evaluateCase('before_or_unknown_context', ['29881', '29870'], {}),
  meniscectomy_29870_same_knee_context: evaluateCase('after_same_knee_context', ['29881', '29870'], {
    '29870': { sameKnee: true }
  }),
  acl_29870_same_knee_context: evaluateCase('acl_same_knee_context', ['29888', '29870'], {
    '29888': { side: 'RT' },
    '29870': { side: 'RT' }
  })
};

console.log(JSON.stringify({
  status: 'pass',
  rule_id: rule.id,
  rule_status: rule.status,
  parent_cpt_count: rule.primary_codes.length,
  parent_cpt_codes: rule.primary_codes,
  escape_hatch_contexts: rule.do_not_suppress_when,
  positive_and_negative_tests: results,
  before_after_payable_wrvu_examples: examples
}, null, 2));
