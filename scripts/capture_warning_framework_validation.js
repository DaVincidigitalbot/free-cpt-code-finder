#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const repoRoot = path.resolve(__dirname, '..');
const artifactDir = path.join(repoRoot, 'qa_artifacts', 'warning_framework_2026_06_22');
fs.mkdirSync(artifactDir, { recursive: true });
const baseUrl = process.env.BASE_URL || 'http://127.0.0.1:8790';

function assert(condition, message, detail) {
  if (!condition) throw new Error(message + (detail ? ': ' + JSON.stringify(detail, null, 2) : ''));
}

async function snapshot(page, name) {
  const data = await page.evaluate(() => {
    const cards = Array.from(document.querySelectorAll('.warning-card')).map(card => ({
      className: card.className,
      warningClass: card.getAttribute('data-warning-class'),
      title: card.querySelector('.warning-card__title')?.textContent.trim(),
      summary: card.querySelector('.warning-card__summary')?.textContent.trim(),
      text: card.textContent.trim()
    }));
    const lines = Array.from(document.querySelectorAll('#lns .rl')).map(line => line.textContent.trim());
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
      overflow,
      duplicateTexts: cards.reduce((acc, card) => { acc[card.summary] = (acc[card.summary] || 0) + 1; return acc; }, {})
    };
  });
  await page.screenshot({ path: path.join(artifactDir, name + '.png'), fullPage: true });
  return data;
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
  const consoleMessages = [];
  page.on('console', msg => consoleMessages.push({ type: msg.type(), text: msg.text() }));
  page.on('pageerror', error => consoleMessages.push({ type: 'pageerror', text: error.message }));
  await page.goto(baseUrl + '/index.html', { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => typeof window.addCptDirectly === 'function' && typeof window.setCaseBuilderClinicalContext === 'function');

  await page.evaluate(() => { window.clearCase(); window.addCptDirectly('44207'); window.addCptDirectly('44180'); });
  await page.waitForTimeout(300);
  const ncci = await snapshot(page, 'desktop-ncci-hard-stop-44207-44180');
  assert(ncci.cards.length === 1, 'NCCI case should show one warning card only', ncci);
  assert(ncci.cards[0].title === 'NCCI Hard Stop', 'NCCI warning class mismatch', ncci);
  assert(ncci.cards[0].warningClass === 'ncci', 'NCCI card data class mismatch', ncci);
  assert(!/Bundled \/ not separately payable/.test(ncci.lines.join(' ')), 'Old bundled paragraph should not render', ncci);
  assert(ncci.overflow.length === 0, 'Desktop NCCI overflow detected', ncci.overflow);

  await page.evaluate(() => { window.clearCase(); window.addCptDirectly('44005'); window.addCptDirectly('49000'); });
  await page.waitForTimeout(300);
  const separate = await snapshot(page, 'desktop-separate-procedure-44005-49000');
  assert(separate.cards.length === 1, 'Separate-procedure case should show one warning card only', separate);
  assert(separate.cards[0].title === 'Separate Procedure', 'Separate-procedure class mismatch', separate);
  assert(separate.cards[0].warningClass === 'separate', 'Separate-procedure data class mismatch', separate);
  const warningNeedle = 'CPT 49000 is generally considered integral to CPT 44005';
  assert((separate.lines.join(' ').match(new RegExp(warningNeedle, 'g')) || []).length === 1, 'Separate-procedure warning duplicated', separate);

  await page.evaluate(() => {
    window.clearCase();
    window.addCptDirectly('44140');
    window.addCptDirectly('38100');
    window.setCaseBuilderClinicalContext('38100', { splenicIndication: 'iatrogenic_splenic_injury' });
  });
  await page.waitForTimeout(300);
  const splenic = await snapshot(page, 'desktop-separate-procedure-38100-iatrogenic');
  assert(splenic.cards.length === 1, 'Iatrogenic splenectomy should show one warning card only', splenic);
  assert(splenic.cards[0].title === 'Separate Procedure', 'Iatrogenic splenectomy warning class mismatch', splenic);
  assert((splenic.lines.join(' ').match(/separate-procedure splenectomy code/g) || []).length === 1, 'Splenectomy warning duplicated', splenic);

  await page.evaluate(() => {
    window.clearCase();
    window.addEM('99214', 'Est pt, mod', 1.92);
    window.addCptDirectly('44140');
    window.setCaseBuilderUserModifier('99214', '25');
  });
  await page.waitForTimeout(300);
  const doc = await snapshot(page, 'desktop-documentation-opportunity-99214-44140');
  assert(doc.cards.length === 1, 'Documentation opportunity should show one warning card only', doc);
  assert(doc.cards[0].title === 'Documentation Opportunity', 'Documentation opportunity class mismatch', doc);
  assert(doc.cards[0].warningClass === 'doc', 'Documentation opportunity data class mismatch', doc);

  await page.setViewportSize({ width: 390, height: 900 });
  await page.evaluate(() => { window.clearCase(); window.addCptDirectly('44005'); window.addCptDirectly('49000'); });
  await page.waitForTimeout(300);
  const mobile = await snapshot(page, 'mobile-separate-procedure-44005-49000');
  assert(mobile.cards.length === 1, 'Mobile separate-procedure should show one warning card only', mobile);
  assert(mobile.overflow.length === 0, 'Mobile overflow detected', mobile.overflow);

  const validation = {
    status: 'pass',
    checkedAt: new Date().toISOString(),
    baseUrl,
    consoleMessages,
    cases: { ncci, separate, splenic, doc, mobile },
    noDuplicateWarningValidation: {
      ncciCards: ncci.cards.length,
      separateCards: separate.cards.length,
      splenicCards: splenic.cards.length,
      docCards: doc.cards.length,
      mobileCards: mobile.cards.length
    },
    overflowValidation: {
      desktopNcciOverflow: ncci.overflow,
      mobileOverflow: mobile.overflow
    }
  };
  fs.writeFileSync(path.join(artifactDir, 'warning-framework-browser-validation.json'), JSON.stringify(validation, null, 2) + '\n');
  await browser.close();
  console.log(JSON.stringify({
    status: 'pass',
    artifactDir: path.relative(repoRoot, artifactDir),
    validationJson: path.relative(repoRoot, path.join(artifactDir, 'warning-framework-browser-validation.json')),
    consoleMessages
  }, null, 2));
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
