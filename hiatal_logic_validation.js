global.window = {};
global.document = { addEventListener: () => {} };
global.fetch = async () => ({ ok: true, json: async () => ({}) });

require('./modifier_engine.js');

const engine = window.ModifierEngine;
engine.modifierRules = require('./modifier_rules.json');
engine.ncciBundles = require('./ncci_bundles.json');

const scenarios = [
  { name: '1. Lap sliding Type I, Nissen', items: [{ code: '43280', description: 'Lap Nissen fundoplication', work_rvu: 14.85 }], expectPresent: ['43280'] },
  { name: '2. Lap sliding Type I, Toupet', items: [{ code: '43280', description: 'Lap Toupet fundoplication', work_rvu: 14.85 }], expectPresent: ['43280'] },
  { name: '3. Lap sliding Type I, Dor', items: [{ code: '43280', description: 'Lap Dor fundoplication', work_rvu: 14.85 }], expectPresent: ['43280'] },
  { name: '4. Open sliding Type I, Nissen', items: [{ code: '43324', description: 'Open fundoplasty', work_rvu: 18.85 }], expectPresent: ['43324'] },
  { name: '5. Lap PEH no mesh, no fundo', items: [{ code: '43281', description: 'Lap PEH repair', work_rvu: 16.25 }], expectPresent: ['43281'] },
  { name: '6. Lap PEH no mesh + Nissen bundled', items: [{ code: '43281', description: 'Lap PEH repair', work_rvu: 16.25 }, { code: '43280', description: 'Lap Nissen', work_rvu: 14.85 }], expectPresent: ['43281'], expectBundled: [{ code: '43280', into: '43281' }] },
  { name: '7. Lap PEH no mesh + Toupet bundled', items: [{ code: '43281', description: 'Lap PEH repair', work_rvu: 16.25 }, { code: '43280', description: 'Lap Toupet', work_rvu: 14.85 }], expectPresent: ['43281'], expectBundled: [{ code: '43280', into: '43281' }] },
  { name: '8. Giant paraesophageal hernia + Toupet + mesh', items: [{ code: '43281', description: 'Lap PEH repair', work_rvu: 16.25 }, { code: '43280', description: 'Lap Toupet', work_rvu: 14.85 }], context: { hiatalMesh: true }, expectPresent: ['43282'], expectAbsent: ['43281'], expectBundled: [{ code: '43280', into: '43282' }] },
  { name: '9. Lap PEH mesh without fundo', items: [{ code: '43282', description: 'Lap PEH repair with mesh', work_rvu: 16.25 }], expectPresent: ['43282'] },
  { name: '10. Recurrent hiatal hernia redo PEH + Nissen', items: [{ code: '43281', description: 'Redo lap PEH repair', work_rvu: 16.25 }, { code: '43280', description: 'Redo Nissen', work_rvu: 14.85 }], expectPresent: ['43281'], expectBundled: [{ code: '43280', into: '43281' }] },
  { name: '11. Open PEH laparotomy no mesh', items: [{ code: '43332', description: 'Open PEH laparotomy', work_rvu: 18.85 }], expectPresent: ['43332'] },
  { name: '12. Open PEH laparotomy + fundoplasty bundled', items: [{ code: '43332', description: 'Open PEH laparotomy', work_rvu: 18.85 }, { code: '43324', description: 'Open fundoplasty', work_rvu: 18.85 }], expectPresent: ['43332'], expectBundled: [{ code: '43324', into: '43332' }] },
  { name: '13. Open PEH laparotomy with mesh', items: [{ code: '43333', description: 'Open PEH laparotomy with mesh', work_rvu: 18.85 }], expectPresent: ['43333'] },
  { name: '14. Open PEH thoracotomy no mesh', items: [{ code: '43334', description: 'Open PEH thoracotomy', work_rvu: 18.85 }], expectPresent: ['43334'] },
  { name: '15. Open PEH thoracotomy with mesh', items: [{ code: '43335', description: 'Open PEH thoracotomy mesh', work_rvu: 18.85 }], expectPresent: ['43335'] },
  { name: '16. Open PEH thoracoabdominal no mesh', items: [{ code: '43336', description: 'Open PEH thoracoabdominal', work_rvu: 18.85 }], expectPresent: ['43336'] },
  { name: '17. Open PEH thoracoabdominal with mesh', items: [{ code: '43337', description: 'Open PEH thoracoabdominal mesh', work_rvu: 18.85 }], expectPresent: ['43337'] },
  { name: '18. PEH + Collis gastroplasty advanced branch', items: [{ code: '43281', description: 'Lap PEH repair', work_rvu: 16.25 }, { code: '43499', description: 'Collis gastroplasty unlisted esophagus', work_rvu: 0 }], expectPresent: ['43281', '43499'] },
  { name: '19. Gastropexy added to PEH repair stays bundled', items: [{ code: '43281', description: 'Lap PEH repair with gastropexy', work_rvu: 16.25 }, { code: '43280', description: 'Fundoplasty separately entered in error', work_rvu: 14.85 }], expectPresent: ['43281'], expectBundled: [{ code: '43280', into: '43281' }] },
  { name: '20. Diagnostic lap converted to sliding repair', items: [{ code: '49320', description: 'Diagnostic laparoscopy', work_rvu: 5.2 }, { code: '43280', description: 'Lap Nissen', work_rvu: 14.85 }], expectAbsent: ['49320'], expectPresent: ['43280'] },
  { name: '21. Diagnostic lap converted to PEH repair', items: [{ code: '49320', description: 'Diagnostic laparoscopy', work_rvu: 5.2 }, { code: '43281', description: 'Lap PEH repair', work_rvu: 16.25 }], expectAbsent: ['49320'], expectPresent: ['43281'] },
  { name: '22. Diagnostic lap converted to open PEH repair', items: [{ code: '49320', description: 'Diagnostic laparoscopy', work_rvu: 5.2 }, { code: '43332', description: 'Open PEH laparotomy', work_rvu: 18.85 }], expectAbsent: ['49320'], expectPresent: ['43332'] },
  { name: '23. Diagnostic lap only remains when no definitive procedure', items: [{ code: '49320', description: 'Diagnostic laparoscopy', work_rvu: 5.2 }], expectPresent: ['49320'] },
  { name: '24. Diagnostic lap + unrelated definitive intra-abdominal procedure suppressed', items: [{ code: '49320', description: 'Diagnostic laparoscopy', work_rvu: 5.2 }, { code: '47562', description: 'Lap cholecystectomy', work_rvu: 11.0 }], expectAbsent: ['49320'], expectPresent: ['47562'] },
  { name: '25. Explicit 43282 + erroneous 43280 entry stays single-code', items: [{ code: '43282', description: 'Lap PEH repair with mesh', work_rvu: 16.25 }, { code: '43280', description: 'Lap Nissen', work_rvu: 14.85 }], expectPresent: ['43282'], expectBundled: [{ code: '43280', into: '43282' }] }
];

function analyzeScenario(scenario) {
  return engine.analyze(scenario.items.map(item => ({ ...item })), scenario.context || {});
}

let failures = 0;
for (const scenario of scenarios) {
  const analysis = analyzeScenario(scenario);
  const codes = analysis.procedures.filter(proc => proc.allowed !== false).map(proc => String(proc.code));
  const all = analysis.procedures.map(proc => ({
    code: String(proc.code),
    allowed: proc.allowed !== false,
    bundledInto: proc.bundledInto || null,
    exclusionReason: proc.exclusionReason || null,
    internalNote: proc.internalNote || null
  }));

  const expectPresent = scenario.expectPresent || [];
  const expectAbsent = scenario.expectAbsent || [];
  const expectBundled = scenario.expectBundled || [];

  const localFailures = [];
  for (const code of expectPresent) if (!codes.includes(code)) localFailures.push(`missing expected code ${code}`);
  for (const code of expectAbsent) if (codes.includes(code)) localFailures.push(`unexpected surviving code ${code}`);
  for (const bundle of expectBundled) {
    const match = all.find(proc => proc.code === bundle.code && proc.bundledInto === bundle.into && !proc.allowed);
    if (!match) localFailures.push(`expected ${bundle.code} to bundle into ${bundle.into}`);
  }

  if (localFailures.length) failures += 1;
  console.log(`\n=== ${scenario.name} ===`);
  console.log(JSON.stringify({ survivingCodes: codes, procedures: all, failures: localFailures }, null, 2));
}

if (failures > 0) {
  console.error(`\n${failures} scenario(s) failed.`);
  process.exit(1);
}

console.log(`\nAll ${scenarios.length} hiatal/fundoplication validation scenarios passed.`);
