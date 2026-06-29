const assert = require('assert');
const fs = require('fs');
const engine = require('./global_modifier_engine');
const cases = JSON.parse(fs.readFileSync('./qa_artifacts/global_modifier_intelligence_v1/sample-global-modifier-cases.json', 'utf8'));
const cptDb = JSON.parse(fs.readFileSync('./cpt_database.json', 'utf8'));

let count = 0;
for (const [specialty, specialtyCases] of Object.entries(cases)) {
  for (const scenario of specialtyCases) {
    const previous = scenario.previousOperation || {};
    const metadata = cptDb[String(previous.cpt)] || {};
    const globalStatus = engine.determineGlobalPeriod({
      previousCode: previous.cpt,
      previousDate: previous.date,
      currentDate: scenario.todayDate || '2026-06-29',
      metadata
    });
    const result = engine.evaluateGlobalPeriod({
      ...scenario.answers,
      globalStatus,
      sameSurgeon: scenario.sameSurgeon || 'yes',
      sameGroup: scenario.sameGroup || 'yes',
      complicationType: scenario.complicationType || '',
      unrelatedReason: scenario.unrelatedReason || 'Separate diagnosis/site documented in sample case.'
    });
    assert.strictEqual(result.modifier, scenario.expectedModifier, specialty + ': ' + scenario.name);
    assert(['High', 'Moderate', 'Low'].includes(result.confidence), specialty + ': confidence missing');
    assert(Array.isArray(result.facts), specialty + ': facts missing');
    if (scenario.modifier22Facts) {
      const mod22 = engine.analyzeModifier22(scenario.modifier22Facts);
      assert.strictEqual(mod22.candidate, true, specialty + ': modifier 22 candidate expected');
      assert(['High', 'Moderate'].includes(mod22.confidence), specialty + ': modifier 22 confidence expected');
    }
    console.log('PASS ' + specialty + ': ' + scenario.name + ' -> -' + result.modifier + ' (' + result.confidence + ') POD ' + globalStatus.postoperativeDay + '/' + globalStatus.globalPeriodDays);
    count++;
  }
}
console.log('Validated ' + count + ' global modifier specialty cases.');
