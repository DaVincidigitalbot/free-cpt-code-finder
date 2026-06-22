#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const repoRoot = path.resolve(__dirname, '..');
const artifactDir = process.env.ARTIFACT_DIR
  ? path.resolve(process.env.ARTIFACT_DIR)
  : path.join(repoRoot, 'qa_artifacts', 'separate_procedure_49255_omentectomy_2026_06_22');
fs.mkdirSync(artifactDir, { recursive: true });

const baseUrl = (process.env.BASE_URL || 'http://127.0.0.1:8795').replace(/\/$/, '');
const pageUrl = baseUrl + '/index.html?review_49255_check=' + Date.now();

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
    {
      name: 'bso_hysterectomy_49255_debulking_suppressed',
      codes: ['58952', '49255'],
      contextByCode: { '49255': { omentectomyContext: 'cytoreduction_debulking' } },
      expectedTotal: '26.61',
      expectedSelected: '38.86',
      expect49255Suppressed: true,
      expectWarning: true
    },
    {
      name: 'bso_total_omentectomy_49255_included_parent_suppressed',
      codes: ['58956', '49255'],
      contextByCode: { '49255': { omentectomyContext: 'included_in_parent_operation' } },
      expectedTotal: '22.23',
      expectedSelected: '34.48',
      expect49255Suppressed: true,
      expectWarning: true
    },
    {
      name: 'tumor_resection_49255_integral_suppressed',
      codes: ['49203', '49255'],
      contextByCode: { '49255': { omentectomyContext: 'incidental_integral_same_abdominal_operation' } },
      expectedTotal: '16.76',
      expectedSelected: '29.01',
      expect49255Suppressed: true,
      expectWarning: true
    },
    {
      name: 'bso_hysterectomy_49255_unknown_context_review_required',
      codes: ['58952', '49255'],
      contextByCode: {},
      expectedTotal: '38.86',
      expectedSelected: null,
      expect49255Suppressed: false,
      expectWarning: true
    },
    {
      name: 'bso_hysterectomy_49255_distinct_omental_mass_not_suppressed',
      codes: ['58952', '49255'],
      contextByCode: { '49255': { omentalIndication: 'omental_mass' } },
      expectedTotal: '38.86',
      expectedSelected: null,
      expect49255Suppressed: false,
      expectWarning: false
    },
    {
      name: 'omentectomy_alone_not_suppressed',
      codes: ['49255'],
      contextByCode: { '49255': { omentalIndication: 'omental_mass' } },
      expectedTotal: '12.25',
      expectedSelected: null,
      expect49255Suppressed: false,
      expectWarning: false
    }
  ];

  const results = [];
  for (const testCase of cases) {
    const result = await runCase(page, testCase);
    assert(result.total === testCase.expectedTotal, testCase.name + ' payable total mismatch', result);
    if (testCase.expectedSelected) assert(result.subline.includes('selected ' + testCase.expectedSelected + ' wRVU'), testCase.name + ' selected wRVU mismatch', result);
    const omentectomyLine = result.lines.find(line => line.includes('49255')) || '';
    const suppressed = /Payable wRVU 0\.00/.test(omentectomyLine);
    assert(suppressed === testCase.expect49255Suppressed, testCase.name + ' 49255 suppression mismatch', result);
    const warningVisible = result.cards.some(card => card.title === 'Separate Procedure' && card.warningClass === 'separate' && /49255|omentectomy/.test(card.text));
    assert(warningVisible === testCase.expectWarning, testCase.name + ' warning state mismatch', result);
    assert(result.overflow.length === 0, testCase.name + ' overflow detected', result.overflow);
    results.push({ name: testCase.name, result });
    if (testCase.name === 'bso_hysterectomy_49255_debulking_suppressed') {
      await page.screenshot({ path: path.join(artifactDir, 'bso-hysterectomy-49255-debulking-suppressed.png'), fullPage: true });
    }
    if (testCase.name === 'bso_hysterectomy_49255_unknown_context_review_required') {
      await page.screenshot({ path: path.join(artifactDir, 'bso-hysterectomy-49255-review-required.png'), fullPage: true });
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
      path.relative(repoRoot, path.join(artifactDir, 'bso-hysterectomy-49255-debulking-suppressed.png')),
      path.relative(repoRoot, path.join(artifactDir, 'bso-hysterectomy-49255-review-required.png'))
    ],
    consoleMessages
  }, null, 2));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
