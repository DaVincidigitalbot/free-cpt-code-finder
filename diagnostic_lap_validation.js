global.window = {};
global.document = { addEventListener: () => {} };
global.fetch = async () => ({ json: async () => ({}) });
require('./modifier_engine.js');

const engine = window.ModifierEngine;
engine.modifierRules = require('./modifier_rules.json');
engine.ncciBundles = require('./ncci_bundles.json');

function printScenario(label, items, context = {}) {
  const analysis = engine.analyze(items.map(i => ({ ...i })), context);
  console.log(`\n=== ${label} ===`);
  analysis.procedures.forEach(proc => {
    console.log(JSON.stringify({
      code: proc.code,
      description: proc.description,
      rank: proc.rank,
      adjustedWRVU: proc.adjustedWRVU,
      exclusionReason: proc.exclusionReason || null,
      builderNote: proc.builderNote || proc.internalNote || null,
      bundledInto: proc.bundledInto || null
    }, null, 2));
  });
}

printScenario('A. Diagnostic lap only', [
  { code: '49320', description: 'Diagnostic laparoscopy of abdomen/peritoneum', wRVU: 6.0 }
]);

printScenario('B. Diagnostic lap + lysis', [
  { code: '49320', description: 'Diagnostic laparoscopy of abdomen/peritoneum', wRVU: 6.0 },
  { code: '44005', description: 'Lysis of adhesions', wRVU: 15.0 }
]);

printScenario('C. Robotic diagnostic lap', [
  { code: '49320', description: 'Robotic diagnostic laparoscopy of abdomen/peritoneum', wRVU: 6.0, builderNote: 'Robotic approach does not change CPT code' }
]);

printScenario('D. Open exploration', [
  { code: '49000', description: 'Exploratory laparotomy', wRVU: 11.25 }
]);
