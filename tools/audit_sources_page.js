#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const root = path.resolve(process.argv[2] || '.');
const htmlFiles = [];

function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    if (['.git', 'node_modules', 'qa_artifacts', '.pytest_cache', '__pycache__'].includes(name)) continue;
    const file = path.join(dir, name);
    const stat = fs.statSync(file);
    if (stat.isDirectory()) walk(file);
    else if (file.endsWith('.html')) htmlFiles.push(file);
  }
}

function resolveSitePath(fromFile, href) {
  const clean = href.split('#')[0].split('?')[0];
  if (!clean) return null;
  return clean.startsWith('/') ? path.join(root, clean) : path.join(path.dirname(fromFile), clean);
}

function existsSiteTarget(target) {
  return fs.existsSync(target) || fs.existsSync(`${target}.html`) || fs.existsSync(path.join(target, 'index.html'));
}

walk(root);

const rootSources = path.join(root, 'sources.html');
const missingInternalLinks = [];
const missingSourceLinks = [];
const nonRootSourceLinks = [];

for (const file of htmlFiles) {
  const html = fs.readFileSync(file, 'utf8');
  for (const match of html.matchAll(/\b(?:href|src)=["']([^"']+)["']/g)) {
    const href = match[1];
    if (!href || href.startsWith('#') || /^[a-z]+:/i.test(href) || href.startsWith('//') || href.startsWith('mailto:') || href.startsWith('tel:')) continue;
    const target = resolveSitePath(file, href);
    if (!target) continue;
    if (!existsSiteTarget(target)) {
      missingInternalLinks.push({ file: path.relative(root, file), link: href, target: path.relative(root, target) });
    }
    if (/sources?\.html|references?\.html|sources\//i.test(href)) {
      if (href.split('#')[0].split('?')[0] !== '/sources.html') {
        nonRootSourceLinks.push({ file: path.relative(root, file), link: href });
      }
      if (!fs.existsSync(rootSources)) {
        missingSourceLinks.push({ file: path.relative(root, file), link: href });
      }
    }
  }
}

const sourceHtml = fs.existsSync(rootSources) ? fs.readFileSync(rootSources, 'utf8') : '';
const requiredReferences = [
  /CMS Physician Fee Schedule/i,
  /National Physician Fee Schedule Relative Value File/i,
  /Medicare Claims Processing Manual/i,
  /NCCI Policy Manual/i,
  /Physician Fee Schedule Database|MPFS/i,
  /AMA CPT/i
];
const missingReferenceText = requiredReferences.map(r => r.source).filter((_, i) => !requiredReferences[i].test(sourceHtml));

const result = {
  root,
  htmlFiles: htmlFiles.length,
  rootSourcesExists: fs.existsSync(rootSources),
  rootSourcesStatus: fs.existsSync(rootSources) ? 200 : 404,
  missingInternalLinks: missingInternalLinks.length,
  missingSourceLinks: missingSourceLinks.length,
  nonRootSourceLinks: nonRootSourceLinks.length,
  missingReferenceText,
  sampleMissingInternalLinks: missingInternalLinks.slice(0, 25),
  sampleNonRootSourceLinks: nonRootSourceLinks.slice(0, 25)
};

console.log(JSON.stringify(result, null, 2));

if (!result.rootSourcesExists || result.rootSourcesStatus !== 200 || result.missingInternalLinks || result.missingSourceLinks || result.nonRootSourceLinks || result.missingReferenceText.length) {
  process.exit(1);
}
