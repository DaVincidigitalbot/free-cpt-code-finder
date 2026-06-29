const assert = require('assert');
const engine = require('./global_modifier_engine');

function test(name, fn) {
  try {
    fn();
    console.log('PASS ' + name);
  } catch (err) {
    console.error('FAIL ' + name);
    throw err;
  }
}

test('modifier 58 for planned staged procedure', () => {
  const result = engine.evaluateGlobalPeriod({ inGlobalPeriod: true, planned: 'yes' });
  assert.strictEqual(result.modifier, '58');
  assert.strictEqual(result.education.newGlobalPeriod, true);
});

test('modifier 58 for more extensive procedure', () => {
  const result = engine.evaluateGlobalPeriod({ inGlobalPeriod: true, planned: 'no', moreExtensive: 'yes' });
  assert.strictEqual(result.modifier, '58');
});

test('modifier 58 for therapy after diagnostic procedure', () => {
  const result = engine.evaluateGlobalPeriod({ inGlobalPeriod: true, therapyAfterDiagnostic: true });
  assert.strictEqual(result.modifier, '58');
});

test('modifier 78 for complication return to OR', () => {
  const result = engine.evaluateGlobalPeriod({ inGlobalPeriod: true, complicationReturnToOR: 'yes' });
  assert.strictEqual(result.modifier, '78');
  assert.strictEqual(result.education.newGlobalPeriod, false);
});

test('modifier 79 for unrelated procedure', () => {
  const result = engine.evaluateGlobalPeriod({ inGlobalPeriod: true, unrelated: 'yes' });
  assert.strictEqual(result.modifier, '79');
  assert.strictEqual(result.education.newGlobalPeriod, true);
});

test('warn when no postoperative modifier criteria fit', () => {
  const result = engine.evaluateGlobalPeriod({
    inGlobalPeriod: true,
    planned: 'no',
    moreExtensive: 'no',
    therapyAfterDiagnostic: 'no',
    complicationReturnToOR: 'no',
    unrelated: 'no'
  });
  assert.strictEqual(result.modifier, null);
  assert.match(result.warning, /may not support/);
});

test('modifier 22 candidate from objective time and hostile abdomen facts', () => {
  const result = engine.analyzeModifier22({
    expectedMinutes: 90,
    actualMinutes: 180,
    adhesiolysisMinutes: 129,
    totalOperativeMinutes: 200,
    operativeReport: 'Hostile reoperative abdomen with diffuse feculent peritonitis and mesh explantation.'
  });
  assert.strictEqual(result.candidate, true);
  assert(result.reasons.some(reason => reason.includes('129 minutes')));
  assert(result.reasons.some(reason => reason.includes('65%')));
  assert(result.reasons.some(reason => reason.includes('Feculent peritonitis')));
  assert(result.reasons.some(reason => reason.includes('Mesh explantation')));
});

test('modifier 22 justification uses objective findings only', () => {
  const analysis = engine.analyzeModifier22({
    expectedMinutes: 100,
    actualMinutes: 170,
    adhesiolysisMinutes: 70,
    totalOperativeMinutes: 170,
    objectiveFindings: ['dense vascular adhesions', 'reoperative field']
  });
  const text = engine.generateModifier22Justification({ cptCode: '44140', analysis });
  assert.match(text, /CPT 44140/);
  assert.match(text, /170 minutes/);
  assert.match(text, /70 minutes/);
  assert(!/AI|algorithm|buzzword/i.test(text));
});

test('payment impact is educational estimate', () => {
  const result = engine.estimateModifier22Impact(1000, 20);
  assert.strictEqual(result.withoutModifier22, 1000);
  assert.strictEqual(result.successfulAppealEstimate, 1200);
  assert.strictEqual(result.estimatedIncrease, 200);
  assert.match(result.label, /Educational estimate/);
});

console.log('Global modifier engine unit tests complete.');
