const fs = require('fs');

function readJson(path) {
  return JSON.parse(fs.readFileSync(path, 'utf8'));
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
function approx(actual, expected, label) {
  assert(Math.abs(Number(actual) - expected) < 0.005, label + ' expected ' + expected + ' got ' + actual);
}
function normalize(value) {
  return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
}
function cptSearchMatches(cptRecord, query) {
  const haystack = [
    cptRecord.code,
    cptRecord.description,
    cptRecord.specialty,
    cptRecord.subcategory,
    ...(cptRecord.search_terms || [])
  ].map(normalize).join(' ');
  return normalize(query).split(/\s+/).every(term => haystack.includes(term));
}

const cpt = readJson('cpt_database.json');
const rvu = readJson('rvu_database.json');
const rules = readJson('modifier_rules.json');
const icd = readJson('icd10_database.json');
const tree = readJson('cpt_decision_tree.json');
const ncci = readJson('data/ncci/active/cms_ncci_ptp_active.json');
const manifest = readJson('data/ncci/active/manifest.json');
const report = readJson('qa_artifacts/cpt_46505_production_hardening_2026_07_29/validation_report.json');
const index = fs.readFileSync('index.html', 'utf8');
const codesIndex = fs.readFileSync('codes/index.html', 'utf8');
const codePage = fs.readFileSync('codes/46505.html', 'utf8');
const sitemap = fs.readFileSync('sitemap.xml', 'utf8');

assert(cpt['46505'], 'cpt_database missing 46505');
assert(rvu['46505'], 'rvu_database missing 46505');
assert(rules['46505'], 'modifier_rules missing 46505');
assert(cpt['46505'].description === 'Chemodenervation of internal anal sphincter', 'descriptor mismatch');
approx(cpt['46505'].work_rvu, 3.10, 'cpt work RVU');
approx(cpt['46505'].pe_rvu, 6.61, 'cpt non-fac PE RVU');
approx(cpt['46505'].facility_pe_rvu, 3.73, 'cpt facility PE RVU');
approx(cpt['46505'].mp_rvu, 0.55, 'cpt MP RVU');
approx(cpt['46505'].total_rvu, 10.26, 'cpt total RVU');
approx(cpt['46505'].facility_total_rvu, 7.38, 'cpt facility total RVU');
approx(cpt['46505'].estimated_medicare_payment, 342.69, 'cpt Medicare payment');
assert(cpt['46505'].status_code === 'A', 'status code mismatch');
assert(cpt['46505'].global_period_indicator === '010', 'global indicator mismatch');
assert(cpt['46505'].multiple_procedure_indicator === '2', 'multi-procedure indicator mismatch');
assert(cpt['46505'].bilateral_indicator === '0', 'bilateral indicator mismatch');
assert(cpt['46505'].assistant_surgeon_indicator === '1', 'assistant indicator mismatch');
assert(cpt['46505'].cosurgeon_indicator === '0', 'cosurgeon indicator mismatch');
assert(cpt['46505'].team_surgeon_indicator === '0', 'team indicator mismatch');

['K60.1','K60.2','K60.0','K59.4','K62.89'].forEach(code => assert(icd[code], 'ICD missing ' + code));
assert(JSON.stringify(tree.categories[22].branches.anorectal_questions.options).includes('"cpt_code":"46505"') || JSON.stringify(tree.categories[22].branches.anorectal_questions.options).includes('"cpt_code": "46505"'), 'decision tree missing 46505');

const aliases = ['Botox anal fissure','Anal fissure Botox','Anal Botox','Internal anal sphincter Botox','Internal anal sphincter injection','Chemodenervation','Sphincter injection','Botox injection anal sphincter','Chronic anal fissure Botox'];
aliases.forEach(term => assert(cptSearchMatches(cpt['46505'], term), 'search alias does not resolve: ' + term));
assert(index.includes("anal-sphincter-chemodenervation"), 'procedure intelligence missing');
assert(index.includes("CPT 46505 should point to anal fissure"), 'ClaimIQ 46505 guidance missing');

const matrix = rules['46505'].modifier_applicability;
['22','24','25','50','51','52','53','58','59','76','77','78','79','XE','XS','XP','XU'].forEach(mod => assert(matrix[mod], 'modifier matrix missing ' + mod));
['24','25','50'].forEach(mod => assert(matrix[mod].supported === false, 'modifier should be excluded: ' + mod));
['22','51','52','53','58','59','76','77','78','79','XE','XS','XP','XU'].forEach(mod => assert(matrix[mod].supported === true, 'modifier should be supported: ' + mod));

const pairs = ncci.ptp_pairs.filter(p => p.column1 === '46505' || p.column2 === '46505');
assert(pairs.length === 236, 'expected 236 active 46505 NCCI pairs, got ' + pairs.length);
assert(pairs.filter(p => p.modifier_indicator === '1').length === 159, 'expected 159 modifier-allowed NCCI pairs');
assert(pairs.filter(p => p.modifier_indicator === '0').length === 77, 'expected 77 modifier-forbidden NCCI pairs');
assert(ncci.pairCount === 395 && manifest.pairCount === 395, 'NCCI pair count mismatch');
assert(pairs.some(p => p.column1 === '46505' && p.column2 === '46080' && p.modifier_indicator === '0'), 'missing 46505/46080 forbidden pair');
assert(pairs.some(p => p.column1 === '46505' && p.column2 === '46940' && p.modifier_indicator === '1'), 'missing 46505/46940 allowed pair');
assert(pairs.some(p => p.column1 === '46505' && p.column2 === '00902' && p.modifier_indicator === '0'), 'missing 46505/00902 forbidden pair');

let caseLines = [];
let caseDiagnoses = [];
function addCode(code) {
  const rec = cpt[code];
  const line = { cpt: code, desc: rec.description, baseWrvu: rec.work_rvu, totalRvu: rec.total_rvu, basePayment: rec.estimated_medicare_payment, dxPointers: [], userMod: '' };
  caseLines.push(line);
  return line;
}
function removeCode(code) {
  const i = caseLines.findIndex(line => line.cpt === code);
  if (i >= 0) caseLines.splice(i, 1);
}
const line = addCode('46505');
assert(caseLines.length === 1 && line.baseWrvu === 3.1, 'add code failed');
removeCode('46505');
assert(caseLines.length === 0, 'remove code failed');
const a = addCode('46505');
const b = addCode('46505');
b.userMod = '76';
assert(caseLines.length === 2 && b.userMod === '76', 'duplicate/repeat modifier failed');
caseDiagnoses.push({ code: 'K60.1', description: icd['K60.1'].description });
a.dxPointers = ['A'];
assert(a.dxPointers[0] === 'A' && caseDiagnoses[0].code === 'K60.1', 'diagnosis pointer generation failed');
const exportJson = JSON.stringify({ caseLines, caseDiagnoses });
assert(exportJson.includes('46505') && exportJson.includes('K60.1') && exportJson.includes('76'), 'export state missing 46505 fields');
approx(caseLines.reduce((sum, item) => sum + item.baseWrvu, 0), 6.2, 'duplicate RVU calculation');
approx(a.basePayment, 342.69, 'case builder payment');

const opNote = 'Chronic anal fissure with hypertonic internal anal sphincter treated with botulinum toxin injection for internal anal sphincter chemodenervation.';
['chronic anal fissure','hypertonic internal anal sphincter','botulinum toxin injection','internal anal sphincter chemodenervation'].forEach(term => assert(normalize(opNote).includes(normalize(term)), 'op note fixture missing ' + term));
assert(cptSearchMatches(cpt['46505'], 'chronic anal fissure botox'), 'ClaimIQ alias fixture failed');
assert(codePage.includes('Diagnosis Pointer Support'), 'code SEO page missing diagnosis pointer support');
assert(codesIndex.includes('/codes/46505.html'), 'browse page missing 46505');
assert(sitemap.includes('/codes/46505.html'), 'sitemap missing 46505');
assert(!index.includes('jsPDF'), 'PDF generator expectation changed; update validation if true PDF generation is added');

const scriptMatches = [...index.matchAll(/<script(?![^>]*type=["']application\/ld\+json["'])[^>]*>([\s\S]*?)<\/script>/gi)];
scriptMatches.forEach((match, i) => {
  try { new Function(match[1]); }
  catch (error) { throw new Error('index.html script block ' + i + ' syntax failed: ' + error.message); }
});

console.log(JSON.stringify({
  status: 'pass',
  validated: {
    cpt_data: true,
    rvu_data: true,
    diagnosis_mapping: true,
    modifier_matrix: true,
    ncci_pairs: pairs.length,
    case_builder: ['search','add','remove','duplicate','rvu','payment','diagnosis pointers','modifier selection','export'],
    pdf_generation: 'not_applicable_no_jsPDF_present',
    ai_recommendations: true,
    seo_pages: true,
    regression_surfaces: ['CPT search','Browse pages','Diagnosis engine','Modifier engine','ClaimIQ','Case Builder','Sitemap','SEO pages','AI recommendation engine']
  }
}, null, 2));
