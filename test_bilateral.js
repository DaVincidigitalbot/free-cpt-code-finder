// Test script for bilateral/laterality logic
const fs = require('fs');

// Load data
const cptDb = JSON.parse(fs.readFileSync('./cpt_database.json', 'utf8'));
const modifierRules = JSON.parse(fs.readFileSync('./modifier_rules.json', 'utf8'));
const ncciBundles = JSON.parse(fs.readFileSync('./ncci_bundles.json', 'utf8'));

// Simplified ModifierEngine for testing
class TestEngine {
  constructor() {
    this.modifierRules = modifierRules;
    this.ncciBundles = ncciBundles;
  }

  analyze(procedures, context) {
    const results = procedures.map((proc, idx) => {
      const rules = this.modifierRules[proc.code] || {};
      const baseWRVU = proc.work_rvu || 0;
      let adjustedWRVU = baseWRVU;
      const modifiers = [];
      const explanations = [];
      let rank = idx === 0 ? 'primary' : 'secondary';

      // Check bilateral
      const isBilateral = proc.bilateral || (context.bilateral && context.bilateral[proc.code]);
      if (isBilateral && rules.bilateral_eligible) {
        modifiers.push('-50');
        adjustedWRVU = baseWRVU * 1.5;
        explanations.push('Bilateral 150% (modifier -50)');
      }

      // Check laterality
      const lat = proc.laterality || (context.laterality && context.laterality[proc.code]);
      if (lat === 'left') modifiers.push('-LT');
      if (lat === 'right') modifiers.push('-RT');

      // MPPR for secondary (if not bilateral, not addon)
      if (rank === 'secondary' && !modifiers.includes('-50') && !rules.addon_code) {
        modifiers.push('-51');
        adjustedWRVU = baseWRVU * 0.5;
        explanations.push('MPPR 50% secondary');
      }

      return {
        id: proc.id,
        code: proc.code,
        description: proc.description,
        laterality: proc.laterality || 'none',
        bilateral: isBilateral,
        modifiers,
        baseWRVU,
        adjustedWRVU,
        rank,
        explanations
      };
    });

    return { procedures: results, confidence: { score: 95 } };
  }
}

// Test cases
const engine = new TestEngine();

console.log('═══════════════════════════════════════════════════════════');
console.log('TEST 1: CPT 15734 UNILATERAL');
console.log('═══════════════════════════════════════════════════════════');
const test1 = engine.analyze([
  { id: 1, code: '15734', description: 'Component separation', work_rvu: 20.22, laterality: 'none', bilateral: false }
], {});
test1.procedures.forEach(p => {
  console.log(`CPT: ${p.code}`);
  console.log(`Modifiers: ${p.modifiers.join(', ') || 'none'}`);
  console.log(`Base wRVU: ${p.baseWRVU.toFixed(2)}`);
  console.log(`Adjusted wRVU: ${p.adjustedWRVU.toFixed(2)}`);
  console.log(`Explanations: ${p.explanations.join('; ') || 'Primary procedure'}`);
});

console.log('\n═══════════════════════════════════════════════════════════');
console.log('TEST 2: CPT 15734 BILATERAL (modifier -50)');
console.log('═══════════════════════════════════════════════════════════');
const test2 = engine.analyze([
  { id: 1, code: '15734', description: 'Component separation', work_rvu: 20.22, laterality: 'bilateral', bilateral: true }
], { bilateral: { '15734': true } });
test2.procedures.forEach(p => {
  console.log(`CPT: ${p.code}`);
  console.log(`Modifiers: ${p.modifiers.join(', ') || 'none'}`);
  console.log(`Base wRVU: ${p.baseWRVU.toFixed(2)}`);
  console.log(`Adjusted wRVU: ${p.adjustedWRVU.toFixed(2)} (expected: 30.33 = 20.22 * 1.5)`);
  console.log(`Explanations: ${p.explanations.join('; ')}`);
});

console.log('\n═══════════════════════════════════════════════════════════');
console.log('TEST 3: CPT 15734 ENTERED TWICE (L + R separate)');
console.log('═══════════════════════════════════════════════════════════');
const test3 = engine.analyze([
  { id: 1, code: '15734', description: 'Component separation LEFT', work_rvu: 20.22, laterality: 'left', bilateral: false },
  { id: 2, code: '15734', description: 'Component separation RIGHT', work_rvu: 20.22, laterality: 'right', bilateral: false }
], { laterality: { '15734': 'left' } });
test3.procedures.forEach(p => {
  console.log(`CPT: ${p.code} [${p.laterality.toUpperCase()}]`);
  console.log(`Modifiers: ${p.modifiers.join(', ') || 'none'}`);
  console.log(`Base wRVU: ${p.baseWRVU.toFixed(2)}`);
  console.log(`Adjusted wRVU: ${p.adjustedWRVU.toFixed(2)}`);
  console.log(`Rank: ${p.rank}`);
  console.log('---');
});
console.log(`Total wRVU: ${test3.procedures.reduce((s,p) => s + p.adjustedWRVU, 0).toFixed(2)}`);

console.log('\n═══════════════════════════════════════════════════════════');
console.log('TEST 4: MULTI-PROCEDURE (15734 bilateral + 49595 hernia)');
console.log('═══════════════════════════════════════════════════════════');
const test4 = engine.analyze([
  { id: 1, code: '15734', description: 'Component separation', work_rvu: 20.22, laterality: 'bilateral', bilateral: true },
  { id: 2, code: '49595', description: 'Ventral hernia repair >10cm', work_rvu: 18.31, laterality: 'none', bilateral: false }
], { bilateral: { '15734': true } });
test4.procedures.forEach(p => {
  console.log(`CPT: ${p.code}${p.bilateral ? ' [BILATERAL]' : ''}`);
  console.log(`Modifiers: ${p.modifiers.join(', ') || 'none'}`);
  console.log(`Base wRVU: ${p.baseWRVU.toFixed(2)}`);
  console.log(`Adjusted wRVU: ${p.adjustedWRVU.toFixed(2)}`);
  console.log(`Rank: ${p.rank}`);
  console.log('---');
});
console.log(`Total wRVU: ${test4.procedures.reduce((s,p) => s + p.adjustedWRVU, 0).toFixed(2)}`);
console.log('Expected: 15734 bilateral = 30.33, 49595 secondary = 9.16 (50%), Total = 39.49');

console.log('\n═══════════════════════════════════════════════════════════');
console.log('ALL TESTS COMPLETE');
console.log('═══════════════════════════════════════════════════════════');
