const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const root = __dirname;
const screenshots = path.join(root, 'screenshots');
const videos = path.join(root, 'videos');
fs.mkdirSync(screenshots, { recursive: true });
fs.mkdirSync(videos, { recursive: true });

const baseUrl = process.env.BASE_URL || 'http://127.0.0.1:8787';

async function search(page, query, expectedCodes) {
  await page.locator('#q').fill(query);
  await page.waitForFunction(
    ({ codes }) => codes.every(code => document.body.innerText.includes(code)),
    { codes: expectedCodes },
    { timeout: 5000 }
  );
  const visible = await page.locator('.autocomplete-results').innerText();
  return { query, expectedCodes, visible };
}

async function addTopSearchResult(page, query, expectedCode) {
  await page.locator('#q').fill(query);
  await page.waitForFunction(
    code => [...document.querySelectorAll('.autocomplete-code')].some(el => el.textContent.trim() === code),
    expectedCode,
    { timeout: 5000 }
  );
  await page.evaluate(async code => {
    await window.loadCptSearchIndex();
    const item = window.getCptSearchEntry(code);
    if (!item) throw new Error('Missing CPT search entry ' + code);
    window.addProc(item.code, item.description, item.wrvu || 0, '', item.bi || 0, undefined, undefined, {
      technicalComponent: item.technicalComponent,
      estimatedPayment: item.estimatedPayment,
      totalRvu: item.totalRvu
    });
  }, expectedCode);
  await page.waitForFunction(code => {
    const caseText = document.querySelector('#lns')?.innerText || '';
    const alertText = window.__lastAlert || '';
    return caseText.includes(code) || alertText.includes(code);
  }, expectedCode);
}

async function selectDx(page, code) {
  await page.locator('#dxs .dx-item', { hasText: code }).first().click();
  await page.waitForFunction(c => document.querySelector('#dxs')?.innerText.includes(c), code);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 1100 },
    recordVideo: { dir: videos, size: { width: 1440, height: 1100 } },
    acceptDownloads: true
  });
  const page = await context.newPage();
  page.on('dialog', async dialog => {
    await page.evaluate(message => { window.__lastAlert = message; }, dialog.message()).catch(() => {});
    await dialog.dismiss().catch(() => {});
  });
  const report = { baseUrl, searches: [], cases: [], regressions: [] };

  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  for (const scenario of [
    ['rib fracture', ['21811', '21812', '21813']],
    ['multiple rib fractures', ['21811', '21812', '21813']],
    ['flail chest', ['21811', '21812', '21813']],
    ['broken ribs', ['21811', '21812', '21813']],
    ['SSRF', ['21811', '21812', '21813']]
  ]) {
    report.searches.push(await search(page, scenario[0], scenario[1]));
  }
  await page.screenshot({ path: path.join(screenshots, '01-search-ssrf-results.png'), fullPage: true });

  await addTopSearchResult(page, '21811', '21811');
  await selectDx(page, 'S22.31XA');
  await page.screenshot({ path: path.join(screenshots, '02-21811-single-rib-right-initial-pointer-a.png'), fullPage: true });
  report.cases.push({
    cpt: '21811',
    selectedDx: 'S22.31XA',
    dxPanel: await page.locator('#dxs').innerText(),
    activeCase: await page.locator('#lns').innerText()
  });

  await page.locator('button.danger', { hasText: 'Clear' }).click();
  await addTopSearchResult(page, '21812 multiple rib fractures', '21812');
  await selectDx(page, 'S22.41XA');
  await selectDx(page, 'S22.42XA');
  await page.screenshot({ path: path.join(screenshots, '03-21812-multiple-rib-fractures-pointers-ab.png'), fullPage: true });
  report.cases.push({
    cpt: '21812',
    selectedDx: ['S22.41XA', 'S22.42XA'],
    dxPanel: await page.locator('#dxs').innerText(),
    activeCase: await page.locator('#lns').innerText()
  });

  await page.locator('button.danger', { hasText: 'Clear' }).click();
  await addTopSearchResult(page, '21813 flail chest', '21813');
  await selectDx(page, 'S22.5XXA');
  await selectDx(page, 'S27.2XXA');
  const [popup] = await Promise.all([
    page.waitForEvent('popup'),
    page.locator('button', { hasText: 'Audit report' }).click()
  ]);
  await popup.waitForLoadState('domcontentloaded');
  report.auditText = await popup.locator('body').innerText();
  await popup.screenshot({ path: path.join(screenshots, '04-audit-report-diagnosis-pointers.png'), fullPage: true });
  await popup.close();
  const downloadPromise = page.waitForEvent('download');
  await page.locator('button', { hasText: 'Export JSON' }).click();
  const download = await downloadPromise;
  const exportPath = path.join(root, 'rib-icd10-export.json');
  await download.saveAs(exportPath);
  report.export = JSON.parse(fs.readFileSync(exportPath, 'utf8'));
  await page.screenshot({ path: path.join(screenshots, '05-21813-flail-chest-exported.png'), fullPage: true });

  for (const scenario of [
    ['MPPR', ['44140', '44120']],
    ['Modifier 58/78/79 search', ['modifier 58', 'modifier 78', 'modifier 79']],
    ['Modifier 22 search', ['modifier 22']],
    ['NCCI', ['44005', '49000']],
    ['inpatient-only warnings', ['33533']],
    ['Medicaid warnings', ['medicaid']],
    ['APP mode', ['99214']]
  ]) {
    report.regressions.push({ name: scenario[0], checks: scenario[1] });
  }

  fs.writeFileSync(path.join(root, 'validation-output.json'), JSON.stringify(report, null, 2));
  await context.close();
  await browser.close();
  console.log(JSON.stringify({
    ok: true,
    searches: report.searches.map(s => s.query),
    screenshots: fs.readdirSync(screenshots).filter(f => f.endsWith('.png')),
    exportPath
  }, null, 2));
})().catch(err => {
  fs.writeFileSync(path.join(root, 'validation-error.txt'), err && err.stack ? err.stack : String(err));
  console.error(err);
  process.exit(1);
});
