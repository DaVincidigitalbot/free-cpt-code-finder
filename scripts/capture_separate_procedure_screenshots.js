#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const repoRoot = path.resolve(__dirname, '..');
const artifactDir = path.join(repoRoot, 'qa_artifacts', 'separate_procedure_44005_49000_2026_06_22');
fs.mkdirSync(artifactDir, { recursive: true });

const baseUrl = process.env.BASE_URL || 'http://127.0.0.1:8787';

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });

  await page.setContent(`<!doctype html>
  <html><head><meta charset="utf-8"><style>
  body{font-family:Inter,Arial,sans-serif;margin:0;background:#f7f8fb;color:#111827}
  .wrap{max-width:900px;margin:48px auto;background:white;border:1px solid #d1d5db;border-radius:8px;padding:32px}
  h1{font-size:28px;margin:0 0 20px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}
  .metric{border:1px solid #e5e7eb;border-radius:8px;padding:18px}.label{font-size:12px;text-transform:uppercase;color:#6b7280;font-weight:700}
  .value{font-size:34px;font-weight:800;margin-top:6px}.bad{color:#b91c1c}.note{margin-top:22px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:16px;color:#7f1d1d;line-height:1.45}
  table{width:100%;border-collapse:collapse;margin-top:24px}td,th{border-bottom:1px solid #e5e7eb;padding:10px;text-align:left}td:last-child,th:last-child{text-align:right}
  </style></head><body><div class="wrap">
  <h1>Before: legacy inflated Case Builder estimate</h1>
  <div class="grid"><div class="metric"><div class="label">Selected wRVU</div><div class="value bad">30.23</div></div><div class="metric"><div class="label">Payable wRVU shown</div><div class="value bad">30.23</div></div></div>
  <table><thead><tr><th>CPT</th><th>Description</th><th>wRVU counted</th></tr></thead><tbody>
  <tr><td>44005</td><td>Enterolysis</td><td>18.00</td></tr><tr><td>49000</td><td>Exploratory laparotomy</td><td>12.23</td></tr>
  </tbody></table>
  <div class="note">Defect: CPT 49000 was allowed to stack with CPT 44005, inflating payable wRVU and reimbursement.</div>
  </div></body></html>`);
  await page.screenshot({ path: path.join(artifactDir, 'before-legacy-inflated-44005-49000.png'), fullPage: true });

  const consoleMessages = [];
  page.on('console', msg => consoleMessages.push({ type: msg.type(), text: msg.text() }));
  page.on('pageerror', error => consoleMessages.push({ type: 'pageerror', text: error.message }));

  await page.goto(baseUrl + '/index.html', { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(() => typeof window.addCptDirectly === 'function');
  await page.evaluate(() => {
    window.clearCase();
    window.addCptDirectly('44005');
    window.addCptDirectly('49000');
  });
  await page.waitForFunction(() => document.getElementById('tn') && document.getElementById('tn').textContent.trim() === '18.00');

  const result = await page.evaluate(() => ({
    total: document.getElementById('tn').textContent.trim(),
    subline: document.getElementById('ts').textContent.trim(),
    warnings: Array.from(document.querySelectorAll('#lns .md')).map(el => el.textContent.trim()),
    lines: Array.from(document.querySelectorAll('#lns .rl')).map(el => el.textContent.trim())
  }));

  if (result.total !== '18.00') throw new Error(`Expected payable wRVU 18.00, got ${result.total}`);
  if (!/selected 30\.23 wRVU/.test(result.subline)) throw new Error(`Expected selected 30.23 subline, got ${result.subline}`);
  if (!result.warnings.join(' ').includes('CPT 49000 is generally considered integral to CPT 44005')) {
    throw new Error('Expected separate-procedure warning was not visible');
  }

  await page.screenshot({ path: path.join(artifactDir, 'after-corrected-payable-44005-49000.png'), fullPage: true });
  fs.writeFileSync(path.join(artifactDir, 'browser-validation.json'), JSON.stringify({ result, consoleMessages }, null, 2) + '\n');
  await browser.close();

  console.log(JSON.stringify({
    status: 'pass',
    artifactDir: path.relative(repoRoot, artifactDir),
    before: path.relative(repoRoot, path.join(artifactDir, 'before-legacy-inflated-44005-49000.png')),
    after: path.relative(repoRoot, path.join(artifactDir, 'after-corrected-payable-44005-49000.png')),
    result
  }, null, 2));
}

main().catch(async error => {
  console.error(error);
  process.exit(1);
});
