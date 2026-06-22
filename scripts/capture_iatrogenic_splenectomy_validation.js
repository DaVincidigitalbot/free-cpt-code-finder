#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const repoRoot = path.resolve(__dirname, '..');
const artifactDir = process.env.ARTIFACT_DIR
  ? path.resolve(process.env.ARTIFACT_DIR)
  : path.join(repoRoot, 'qa_artifacts', 'iatrogenic_splenectomy_2026_06_22');
fs.mkdirSync(artifactDir, { recursive: true });

const baseUrl = (process.env.BASE_URL || 'http://127.0.0.1:8789').replace(/\/$/, '');
const pageUrl = baseUrl + '/index.html?iatrogenic_splenectomy_check=' + Date.now();

async function runCase(page, testCase) {
  await page.evaluate(({ codes, contextByCode }) => {
    window.clearCase();
    codes.forEach(code => window.addCptDirectly(code));
    Object.entries(contextByCode || {}).forEach(([code, context]) => {
      window.setCaseBuilderClinicalContext(code, context);
    });
  }, testCase);
  await page.waitForTimeout(250);
  return page.evaluate(() => {
    const lines = Array.from(document.querySelectorAll('#lns .rl')).map(el => el.textContent.trim());
    const cards = Array.from(document.querySelectorAll('.warning-card')).map(card => ({
      className: card.className,
      warningClass: card.getAttribute('data-warning-class'),
      title: card.querySelector('.warning-card__title')?.textContent.trim(),
      summary: card.querySelector('.warning-card__summary')?.textContent.trim(),
      text: card.textContent.trim()
    }));
    const overflow = Array.from(document.querySelectorAll('#lns .rl, .warning-card, .warning-card__summary')).filter(el => el.scrollWidth > el.clientWidth + 1).map(el => ({
      className: el.className,
      text: el.textContent.trim().slice(0, 160),
      scrollWidth: el.scrollWidth,
      clientWidth: el.clientWidth
    }));
    return {
      total: document.getElementById('tn')?.textContent.trim(),
      subline: document.getElementById('ts')?.textContent.trim(),
      cards,
      lines,
      overflow
    };
  });
}

function assert(condition, message, detail) {
  if (!condition) throw new Error(message + (detail ? ': ' + JSON.stringify(detail, null, 2) : ''));
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
  const consoleMessages = [];
  page.on('console', msg => consoleMessages.push({ type: msg.type(), text: msg.text() }));
  page.on('pageerror', error => consoleMessages.push({ type: 'pageerror', text: error.message }));

  await page.goto(pageUrl, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => typeof window.addCptDirectly === 'function' && typeof window.setCaseBuilderClinicalContext === 'function');

  const cases = [
    { name: 'colectomy_38100_iatrogenic', codes: ['44140', '38100'], contextByCode: { '38100': { splenicIndication: 'iatrogenic_splenic_injury' } }, expectedTotal: '22.03', expectedSelected: '41.09', splenectomyCode: '38100', expectSplenectomySuppressed: true, expectWarning: true },
    { name: 'gastrectomy_38100_iatrogenic', codes: ['43620', '38100'], contextByCode: { '38100': { splenicIndication: 'iatrogenic_splenic_injury' } }, expectedTotal: '33.19', expectedSelected: '52.25', splenectomyCode: '38100', expectSplenectomySuppressed: true, expectWarning: true },
    { name: 'distal_pancreatectomy_38100_iatrogenic', codes: ['48140', '38100'], contextByCode: { '38100': { splenicIndication: 'iatrogenic_splenic_injury' } }, expectedTotal: '25.66', expectedSelected: '44.72', splenectomyCode: '38100', expectSplenectomySuppressed: true, expectWarning: true },
    { name: 'trauma_laparotomy_38100_splenic_rupture', codes: ['49000', '38100'], contextByCode: { '38100': { splenicIndication: 'traumatic_splenic_injury' } }, expectedTotal: '19.06', expectedSelected: '31.29', splenectomyCode: '38100', expectSplenectomySuppressed: false, expectWarning: false },
    { name: 'splenectomy_alone', codes: ['38100'], contextByCode: { '38100': { splenicIndication: 'splenic_mass' } }, expectedTotal: '19.06', expectedSelected: null, splenectomyCode: '38100', expectSplenectomySuppressed: false, expectWarning: false },
    { name: 'colectomy_38100_pre_existing_pathology', codes: ['44140', '38100'], contextByCode: { '38100': { splenicIndication: 'pre_existing_splenic_pathology' } }, expectedTotal: '41.09', expectedSelected: null, splenectomyCode: '38100', expectSplenectomySuppressed: false, expectWarning: false },
    { name: 'colectomy_38100_unknown_context_review_required', codes: ['44140', '38100'], contextByCode: {}, expectedTotal: '41.09', expectedSelected: null, splenectomyCode: '38100', expectSplenectomySuppressed: false, expectWarning: true },
    { name: 'colectomy_38101_iatrogenic', codes: ['44140', '38101'], contextByCode: { '38101': { splenicIndication: 'iatrogenic_splenic_injury' } }, expectedTotal: '22.03', expectedSelected: '41.09', splenectomyCode: '38101', expectSplenectomySuppressed: true, expectWarning: true }
  ];

  const results = [];
  for (const testCase of cases) {
    const result = await runCase(page, testCase);
    assert(result.total === testCase.expectedTotal, testCase.name + ' payable total mismatch', result);
    if (testCase.expectedSelected) assert(result.subline.includes('selected ' + testCase.expectedSelected + ' wRVU'), testCase.name + ' selected wRVU mismatch', result);
    const splenectomyLine = result.lines.find(line => line.includes(testCase.splenectomyCode)) || '';
    const splenectomySuppressed = /Payable wRVU 0\.00/.test(splenectomyLine);
    assert(splenectomySuppressed === testCase.expectSplenectomySuppressed, testCase.name + ' splenectomy suppression state mismatch', result);
    const warningVisible = result.cards.some(card => card.title === 'Separate Procedure' && card.warningClass === 'separate' && /separate-procedure splenectomy code|Review required/.test(card.text));
    assert(warningVisible === testCase.expectWarning, testCase.name + ' warning state mismatch', result);
    assert(result.overflow.length === 0, testCase.name + ' overflow detected', result.overflow);
    results.push({ name: testCase.name, result });
    if (testCase.name === 'colectomy_38100_iatrogenic') {
      await page.screenshot({ path: path.join(artifactDir, 'colectomy-38100-iatrogenic-suppressed.png'), fullPage: true });
    }
    if (testCase.name === 'colectomy_38100_unknown_context_review_required') {
      await page.screenshot({ path: path.join(artifactDir, 'colectomy-38100-review-required.png'), fullPage: true });
    }
  }

  const validation = {
    status: 'pass',
    baseUrl,
    pageUrl,
    checkedAt: new Date().toISOString(),
    results,
    consoleMessages
  };
  fs.writeFileSync(path.join(artifactDir, 'browser-validation.json'), JSON.stringify(validation, null, 2) + '\n');
  await browser.close();

  console.log(JSON.stringify({
    status: 'pass',
    artifactDir: path.relative(repoRoot, artifactDir),
    validationJson: path.relative(repoRoot, path.join(artifactDir, 'browser-validation.json')),
    screenshots: [
      path.relative(repoRoot, path.join(artifactDir, 'colectomy-38100-iatrogenic-suppressed.png')),
      path.relative(repoRoot, path.join(artifactDir, 'colectomy-38100-review-required.png'))
    ],
    consoleMessages
  }, null, 2));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
