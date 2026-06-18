#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const vm = require("vm");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..");
const BASE_URL = "https://freecptcodefinder.com";
const OUT_DIR = path.join(ROOT, "audit_reports", "category_cleanup_postdeploy_2026-06-18");
const CACHE_BUST = Date.now();

const SEARCH_CHECKS = {
  colectomy: "44140",
  CABG: "33533",
  "component separation": "15734",
  fasciotomy: "27600",
  nephrectomy: "50545",
  Whipple: "48150",
  "hernia repair": "49505",
  "exploratory laparotomy": "49000",
  tonsillectomy: "42825",
  debridement: "11044",
  "sinus endoscopy": "31231",
  splenectomy: "38100",
  BMP: "80048"
};

const REMOVED_SPECIALTIES = new Set([
  "bowel_resection",
  "cabg",
  "component_separation",
  "fasciotomy",
  "kidney",
  "liver",
  "pancreas",
  "hernia_repair",
  "exploratory",
  "ent_tonsil_adenoid",
  "debridement",
  "sinus_endoscopy",
  "splenectomy",
  "pathology",
  "Otolaryngology (ENT)",
  "Otolaryngology (Ent)"
]);

async function fetchText(url) {
  const controller = new AbortController();
  const timer = setTimeout(function () { controller.abort(); }, 15000);
  try {
    const response = await fetch(url, { signal: controller.signal });
    if (!response.ok) throw new Error(url + " returned " + response.status);
    return await response.text();
  } finally {
    clearTimeout(timer);
  }
}

async function checkUrl(url) {
  const controller = new AbortController();
  const timer = setTimeout(function () { controller.abort(); }, 15000);
  try {
    let response = await fetch(url, { method: "HEAD", redirect: "follow", signal: controller.signal });
    if (response.status === 405 || response.status === 403) {
      response = await fetch(url, { method: "GET", redirect: "follow", signal: controller.signal });
    }
    return { url: url, status: response.status, ok: response.status < 400 };
  } catch (error) {
    return { url: url, status: null, ok: false, error: String(error.message || error) };
  } finally {
    clearTimeout(timer);
  }
}

function parseSpecs(html) {
  const match = html.match(/const SPECS=(\{[\s\S]*?\});\n\n\/\/ ===== STATE =====/);
  if (!match) throw new Error("Could not locate live SPECS object");
  const context = {};
  vm.createContext(context);
  vm.runInContext("SPECS=" + match[1], context);
  return context.SPECS;
}

function collectInternalLinks(html) {
  const links = new Set();
  for (const match of html.matchAll(/href=["']([^"']+)["']/gi)) {
    const href = match[1].trim();
    if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:") || href.startsWith("javascript:")) continue;
    const url = new URL(href, BASE_URL);
    if (url.origin !== BASE_URL) continue;
    url.hash = "";
    links.add(url.toString());
  }
  return Array.from(links).sort();
}

function validateDb(db) {
  const errors = [];
  const badSpecialtyValues = {};
  for (const entryPair of Object.entries(db)) {
    const code = entryPair[0];
    const entry = entryPair[1];
    if (entry.code !== code) errors.push(code + ": code field mismatch");
    if (!entry.description) errors.push(code + ": missing description");
    if (!entry.specialty) errors.push(code + ": missing specialty");
    if (REMOVED_SPECIALTIES.has(String(entry.specialty))) {
      badSpecialtyValues[entry.specialty] = (badSpecialtyValues[entry.specialty] || 0) + 1;
    }
  }
  return { errors: errors, badSpecialtyValues: badSpecialtyValues };
}

function validateSearch(db) {
  const rows = Object.values(db).map(function (entry) {
    return {
      code: String(entry.code),
      haystack: [
        entry.code,
        entry.description,
        entry.specialty,
        entry.category,
        entry.subcategory,
        entry.code_family
      ].concat(entry.search_terms || []).filter(Boolean).join(" ").toLowerCase()
    };
  });
  return Object.fromEntries(Object.entries(SEARCH_CHECKS).map(function (entry) {
    const query = entry[0];
    const expected = entry[1];
    const tokens = query.toLowerCase().split(/\s+/);
    const found = rows.some(function (row) {
      return row.code === expected && tokens.every(function (token) { return row.haystack.includes(token); });
    });
    return [query, { expected: expected, found: found }];
  }));
}

async function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const errors = [];
  const html = await fetchText(BASE_URL + "/?postdeploy=" + CACHE_BUST);
  const specs = parseSpecs(html);
  const db = JSON.parse(await fetchText(BASE_URL + "/cpt_database.json?postdeploy=" + CACHE_BUST));

  const categoryCount = Object.keys(specs).length;
  if (categoryCount !== 41) errors.push("Expected 41 categories, found " + categoryCount);

  const dbValidation = validateDb(db);
  errors.push.apply(errors, dbValidation.errors);
  if (Object.keys(dbValidation.badSpecialtyValues).length) {
    errors.push("Removed standalone specialty values remain: " + JSON.stringify(dbValidation.badSpecialtyValues));
  }

  const searchResults = validateSearch(db);
  for (const entry of Object.entries(searchResults)) {
    if (!entry[1].found) errors.push("Search check failed: " + entry[0] + " -> " + entry[1].expected);
  }

  const internalLinks = collectInternalLinks(html);
  const linkResults = [];
  for (const link of internalLinks) linkResults.push(await checkUrl(link));
  const brokenLinks = linkResults.filter(function (result) { return !result.ok; });
  if (brokenLinks.length) errors.push(brokenLinks.length + " broken internal links found");

  const browser = await chromium.launch({ channel: "chrome", headless: true });
  const desktop = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
  await desktop.route(/free-cpt-code-finder\.onrender\.com/, function (route) { return route.abort(); });
  const page = await desktop.newPage();
  const consoleErrors = [];
  page.on("console", function (message) {
    if (message.type() === "error" && !/Failed to load resource|ERR_FAILED/.test(message.text())) consoleErrors.push(message.text());
  });
  page.on("pageerror", function (error) { consoleErrors.push(error.message); });
  await page.goto(BASE_URL + "/?postdeploy-browser=" + CACHE_BUST, { waitUntil: "domcontentloaded" });
  await page.waitForSelector(".spec-n");
  await page.evaluate(function () { addProc("44140", "Colectomy, partial; with anastomosis", 18.43, "", 0); });
  await page.waitForSelector(".rcpt");
  const caseBuilderText = await page.locator("#lns").textContent();
  if (!caseBuilderText.includes("44140")) errors.push("Case Builder smoke failed for 44140");
  await page.screenshot({ path: path.join(OUT_DIR, "desktop-postdeploy-home-casebuilder.png"), fullPage: false });

  const mobile = await browser.newContext({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2 });
  const mobilePage = await mobile.newPage();
  await mobilePage.goto(BASE_URL + "/?postdeploy-mobile=" + CACHE_BUST, { waitUntil: "domcontentloaded" });
  await mobilePage.waitForSelector(".spec-n");
  const mobileOverflow = await mobilePage.evaluate(function () {
    return {
      innerWidth: window.innerWidth,
      bodyScrollWidth: document.body.scrollWidth,
      docScrollWidth: document.documentElement.scrollWidth,
      hasHorizontalOverflow: Math.max(document.body.scrollWidth, document.documentElement.scrollWidth) > window.innerWidth + 1
    };
  });
  if (mobileOverflow.hasHorizontalOverflow) errors.push("Mobile horizontal overflow detected: " + JSON.stringify(mobileOverflow));
  await mobilePage.screenshot({ path: path.join(OUT_DIR, "mobile-postdeploy-layout.png"), fullPage: false });
  await browser.close();

  errors.push.apply(errors, consoleErrors.map(function (error) { return "Console error: " + error; }));

  const report = {
    generatedAt: new Date().toISOString(),
    productionUrl: BASE_URL,
    homepageLoaded: true,
    categoryCount: categoryCount,
    cptRecordCount: Object.keys(db).length,
    orphanedCptRecordErrors: dbValidation.errors,
    badSpecialtyValues: dbValidation.badSpecialtyValues,
    searchResults: searchResults,
    internalLinkCount: internalLinks.length,
    brokenLinks: brokenLinks,
    caseBuilderHas44140: caseBuilderText.includes("44140"),
    mobileOverflow: mobileOverflow,
    screenshots: [
      path.join(OUT_DIR, "desktop-postdeploy-home-casebuilder.png"),
      path.join(OUT_DIR, "mobile-postdeploy-layout.png")
    ],
    errors: errors
  };
  fs.writeFileSync(path.join(OUT_DIR, "postdeploy-crawl.json"), JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
  if (errors.length) process.exit(1);
}

main().catch(function (error) {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  fs.writeFileSync(path.join(OUT_DIR, "postdeploy-crawl-error.log"), String(error.stack || error) + "\n");
  console.error(error.stack || error);
  process.exit(1);
});
