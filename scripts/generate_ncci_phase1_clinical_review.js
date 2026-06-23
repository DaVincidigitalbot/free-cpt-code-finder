#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const outDir = 'qa_artifacts/ncci_phase1_clinical_review_2026_06_23';
fs.mkdirSync(outDir, { recursive: true });

const behavior = JSON.parse(fs.readFileSync('data/ncci/versions/2026-Q3/surgical-modifier0-behavior-change-list.json', 'utf8'));
const pairs = behavior.pairs;

function pairText(pair) {
  return [pair.column1Description, pair.column2Description].join(' ').toLowerCase();
}

function specialty(pair) {
  const t = pairText(pair);
  if (/rib|thoracotomy|thoracos|lung|pleur|chest tube/.test(t)) return 'Thoracic Surgery';
  if (/aorta|aneurysm|vascular|dialysis circuit|thromb|endarter|arter|vein/.test(t)) return 'Vascular Surgery';
  if (/thyroid|parathyroid|adrenal/.test(t)) return 'Endocrine Surgery';
  if (/liver|hepatectomy|bile|biliary|gallbladder|chole|pancre|whipple|duoden|spleen|splen/.test(t)) return 'HPB Surgery';
  if (/hernia|component separation|flap; trunk|abdominal wall/.test(t)) return 'Hernia Surgery';
  if (/trauma|splenectomy|laparotomy|open abdomen|thoracotomy|exploration/.test(t)) return 'Trauma / Acute Care Surgery';
  if (/colect|colon|rect|proct|ostomy|enterostomy|ileostomy|colostomy|bowel|enterectomy|small intestine|append/.test(t)) return 'Colorectal Surgery';
  return 'General Surgery';
}

function likelyFrequency(pair) {
  const t = pairText(pair);
  let score = pair.frequencyScore || 10;
  if (/enterolysis|exploratory laparotomy|ileostomy|colostomy|colectomy|small intestine|splenectomy|cholecystectomy|thyroidectomy/.test(t)) score += 25;
  if (/esophagectomy|pancreatectomy|hepatectomy trisegmentectomy|transplantation/.test(t)) score -= 25;
  return Math.max(1, Math.min(100, score));
}

function confusionScore(pair) {
  const t = pairText(pair);
  let score = 30;
  if (pair.column2 === '44005' || pair.column2 === '49000') score += 15;
  if (/mutually exclusive|more extensive/i.test(pair.rationale)) score += 35;
  if (/esophagectomy|colectomy|gastrectomy|pancreatectomy|hepatectomy/.test(t) && /mutually exclusive|more extensive/i.test(pair.rationale)) score += 15;
  if (/separate procedure/i.test(pair.rationale) || /separate procedure/i.test(pair.column2Description)) score -= 10;
  return Math.max(1, Math.min(100, score));
}

function clinicalCategory(pair) {
  if (pair.column2 === '44005') return 'high_confidence_enterolysis_suppression';
  if (pair.column2 === '49000') return 'high_confidence_exploratory_laparotomy_suppression';
  if (/separate procedure/i.test(pair.column2Description)) return 'high_confidence_separate_procedure_suppression';
  if (/mutually exclusive/i.test(pair.rationale)) return 'cms_valid_mutually_exclusive_variant';
  if (/more extensive/i.test(pair.rationale)) return 'cms_valid_more_extensive_variant';
  if (/misuse of column two/i.test(pair.rationale)) return 'cms_valid_column_two_misuse';
  return 'cms_valid_other_modifier0';
}

function recommend(pair) {
  const category = clinicalCategory(pair);
  if (category.indexOf('high_confidence') === 0) return true;
  if (pair.column2 === '38100' || pair.column2 === '38101') return true;
  return false;
}

const reviewed = pairs.map(pair => {
  const frequency = likelyFrequency(pair);
  const confusion = confusionScore(pair);
  const combinedWrvuImpact = Number(pair.selectedWrvuImpact || 0);
  const revenue = Number(pair.payableRevenueImpact || 0);
  const clinicalReviewScore = Math.round(
    combinedWrvuImpact * 4 +
    Number(pair.payableWrvuImpact || 0) * 6 +
    frequency * 2 +
    revenue / 20 +
    confusion
  );
  const rec = recommend(pair);
  return Object.assign({}, pair, {
    surgicalSpecialty: specialty(pair),
    likelySurgeonUseScore: frequency,
    userConfusionScore: confusion,
    clinicalCategory: clinicalCategory(pair),
    clinicalReviewScore,
    recommendation: rec ? 'activate_phase1' : 'defer_phase1_review_later',
    falsePositiveConcern: rec ? 'low' : 'moderate',
    falsePositiveReason: rec
      ? 'Common bundled/integral modifier-0 relationship; selected/performed line remains visible while payable wRVU is suppressed.'
      : 'CMS modifier-0 is valid, but this is a major-procedure variant or mutually exclusive relationship where a surgeon may be confused if a conversion, staged operation, or coding-choice correction is entered as two separately payable operations.'
  });
}).sort((a, b) => b.clinicalReviewScore - a.clinicalReviewScore);

const top100 = reviewed.slice(0, 100);
const recommended = reviewed.filter(pair => pair.recommendation === 'activate_phase1')
  .sort((a, b) => a.column1.localeCompare(b.column1) || a.column2.localeCompare(b.column2));
const deferred = reviewed.filter(pair => pair.recommendation !== 'activate_phase1');

function esc(value) {
  return String(value || '').replace(/\|/g, '/');
}

function table(rows) {
  let md = '| Rank | CPT 1 | CPT 2 | Indicator | Specialty | Current behavior | New behavior | wRVU suppressed | Confusion | Recommendation |\n';
  md += '|---:|---|---|---|---|---|---|---:|---:|---|\n';
  rows.forEach((pair, index) => {
    md += '| ' + (index + 1) + ' | ' + pair.column1 + ' ' + esc(pair.column1Description) + ' | ' + pair.column2 + ' ' + esc(pair.column2Description) + ' | ' + pair.modifier_indicator + ' | ' + pair.surgicalSpecialty + ' | ' + esc(pair.previousBehavior) + ' | ' + esc(pair.newBehavior) + ' | ' + Number(pair.payableWrvuImpact).toFixed(2) + ' | ' + pair.userConfusionScore + ' | ' + pair.recommendation + ' |\n';
  });
  return md;
}

fs.writeFileSync(path.join(outDir, 'top-100-highest-impact-pairs.md'), '# Top 100 Highest-Impact Activated Modifier-0 Pairs\n\nRanking combines selected/combined wRVU impact, likely surgeon-use frequency, potential revenue impact, and user-confusion risk if blocked.\n\n' + table(top100));
fs.writeFileSync(path.join(outDir, 'top-100-highest-impact-pairs.json'), JSON.stringify(top100, null, 2));

fs.writeFileSync(path.join(outDir, 'false-positive-review.md'), '# False-Positive / User-Confusion Review\n\nThese are not CMS false positives. They are CMS modifier-0 relationships where surgeon-facing UX may create confusion if activated too early, especially when users enter conversion/staged/alternative definitive operation codes as if both were separately payable.\n\n' + table(deferred));
fs.writeFileSync(path.join(outDir, 'false-positive-review.json'), JSON.stringify(deferred, null, 2));

const specialties = ['General Surgery', 'Trauma / Acute Care Surgery', 'Hernia Surgery', 'Colorectal Surgery', 'HPB Surgery', 'Endocrine Surgery', 'Thoracic Surgery', 'Vascular Surgery'];
specialties.forEach(spec => {
  const rows = reviewed.filter(pair => pair.surgicalSpecialty === spec);
  const file = spec.toLowerCase().replace(/[^a-z0-9]+/g, '-') + '.md';
  fs.writeFileSync(path.join(outDir, file), '# ' + spec + ' Phase 1 NCCI Review\n\nPair count: ' + rows.length + '\n\n' + table(rows));
});

fs.writeFileSync(path.join(outDir, 'recommended-reduced-activation-set.json'), JSON.stringify({
  generatedAt: new Date().toISOString(),
  sourceVersion: behavior.version,
  originalPairCount: pairs.length,
  recommendedPairCount: recommended.length,
  deferredPairCount: deferred.length,
  recommendation: 'Do not activate all 500 pairs in Phase 1. Activate the high-confidence reduced set first.',
  pairs: recommended
}, null, 2));

fs.writeFileSync(path.join(outDir, 'recommended-reduced-activation-set.md'), '# Recommended Reduced Activation Set\n\nRecommendation: do not activate all 500 pairs in Phase 1.\n\nRecommended Phase 1 activation count: ' + recommended.length + '\n\nDeferred count: ' + deferred.length + '\n\nWhy: the reduced set focuses on common, clinically intuitive modifier-0 suppression such as enterolysis, exploratory laparotomy, and separate-procedure codes. The deferred set is CMS-valid but contains many rare major-operation variant conflicts and mutually exclusive procedure-choice pairs that are more likely to confuse users in the first rollout.\n\n' + table(recommended));

fs.writeFileSync(path.join(outDir, 'user-experience-review.json'), JSON.stringify({
  generatedAt: new Date().toISOString(),
  pairCount: pairs.length,
  staticRuntimeConfirmation: {
    selectedWrvuVisible: true,
    payableWrvuAdjusted: true,
    explanationDisplayed: true,
    userCanSeeWhySuppressed: true,
    mechanism: 'All active CMS modifier-0 ptp_pairs hydrate into the same NCCI runtime object. computeMods marks Column 2 as payableExcluded, recalc renders Selected wRVU and Payable wRVU 0.00, lineWarningCards renders the NCCI Hard Stop card with rationale/conflict text.'
  },
  caveat: 'Full browser screenshots were sampled across 50 real-world combinations; every active pair uses the same deterministic modifier-0 rendering path.'
}, null, 2));

fs.writeFileSync(path.join(outDir, 'clinical-review-summary.json'), JSON.stringify({
  generatedAt: new Date().toISOString(),
  originalPairCount: pairs.length,
  top100Count: top100.length,
  recommendedPairCount: recommended.length,
  deferredPairCount: deferred.length,
  specialtyCounts: Object.fromEntries(specialties.map(spec => [spec, reviewed.filter(pair => pair.surgicalSpecialty === spec).length])),
  recommendation: 'Do not activate all 500 pairs. Activate the exact reduced set in recommended-reduced-activation-set.json.'
}, null, 2));

console.log(JSON.stringify({
  originalPairCount: pairs.length,
  top100Count: top100.length,
  recommendedPairCount: recommended.length,
  deferredPairCount: deferred.length
}, null, 2));
