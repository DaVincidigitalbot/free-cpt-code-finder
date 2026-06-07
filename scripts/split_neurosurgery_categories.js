const fs = require('fs');
const path = require('path');
const vm = require('vm');

const root = path.resolve(__dirname, '..');
const today = '2026-06-07';
const artifactDir = path.join(root, 'qa_artifacts', 'neurosurgery_split_2026_06_07');
fs.mkdirSync(artifactDir, { recursive: true });

const cranialName = 'Skull Base / Cranial Neurosurgery';
const spineName = 'Spine Neurosurgery';
const cranialSlug = 'skull-base-cranial-neurosurgery';
const spineSlug = 'spine-neurosurgery';

const spineCodes = new Set([
  '22551','22552','22554','22558','22600','22610','22612','22614','22630',
  '62270','62322','62323','63001','63003','63005','63012','63030','63042','63045',
  '63047','63048','63075','63081','63267','63650','63655','63685','64561',
  '61782','61783'
]);

const specialtyMoves = {
  '60100': 'Endocrine',
  '60200': 'Endocrine',
  '60210': 'Endocrine',
  '60212': 'Endocrine',
  '60220': 'Endocrine',
  '60225': 'Endocrine',
  '60260': 'Endocrine',
  '60270': 'Endocrine',
  '60271': 'Endocrine',
  '60280': 'Endocrine',
  '60281': 'Endocrine',
  '60500': 'Endocrine',
  '60502': 'Endocrine',
  '60505': 'Endocrine',
  '60540': 'Endocrine',
  '60545': 'Endocrine',
  '60650': 'Endocrine',
  '64718': 'Orthopedic Hand Surgery',
  '64721': 'Orthopedic Hand Surgery',
  '29848': 'Orthopedic Hand Surgery',
  '69210': 'Otolaryngology (ENT)',
  '69433': 'Otolaryngology (ENT)',
  '69436': 'Otolaryngology (ENT)',
  '69501': 'Otolaryngology (ENT)'
};

const legacyNeurosurgeryExtraCodes = {
  '22552': spineName,
  '22558': spineName,
  '22600': spineName,
  '22630': spineName,
  '63048': spineName,
  '61700': cranialName,
  '61680': cranialName,
  '29848': 'Orthopedic Hand Surgery'
};

const manualReviewNotes = {
  '29848': 'Peripheral median nerve / carpal tunnel code. Currently in Neurosurgery, but more commonly Hand/Orthopedic Hand than cranial or spine.',
  '64718': 'Peripheral ulnar nerve at elbow. Currently in Neurosurgery, but overlaps Hand/Upper Extremity more than cranial or spine.',
  '64721': 'Peripheral median nerve at carpal tunnel. Currently in Neurosurgery, but overlaps Hand/Upper Extremity more than cranial or spine.',
  '60100': 'Thyroid biopsy. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60200': 'Thyroid cyst aspiration. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60210': 'Partial thyroid lobectomy. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60212': 'Partial thyroid lobectomy with contralateral subtotal lobectomy. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60220': 'Total thyroid lobectomy. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60225': 'Total thyroid lobectomy with contralateral subtotal lobectomy. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60260': 'Completion thyroidectomy. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60270': 'Thyroidectomy, including substernal thyroid. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60271': 'Cervical approach substernal thyroidectomy. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60280': 'Thyroglossal duct cyst excision. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60281': 'Recurrent thyroglossal duct cyst excision. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60500': 'Parathyroid exploration. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60502': 'Parathyroid re-exploration. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60505': 'Parathyroid autotransplantation/additional exploration. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60540': 'Adrenalectomy. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60545': 'Adrenalectomy with adjacent organ work. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '60650': 'Laparoscopic adrenalectomy. Existing Neurosurgery row appears miscategorized; not cranial or spine.',
  '69210': 'Impacted cerumen removal. Existing Neurosurgery row appears miscategorized; ENT rather than cranial/spine neurosurgery.',
  '69433': 'Tympanostomy tube, local/topical anesthesia. Existing Neurosurgery row appears miscategorized; ENT rather than cranial/spine neurosurgery.',
  '69436': 'Tympanostomy tube, general anesthesia. Existing Neurosurgery row appears miscategorized; ENT rather than cranial/spine neurosurgery.',
  '69501': 'Simple mastoidectomy. Existing Neurosurgery row overlaps cranial region but is commonly ENT/otology.'
};

function uniqueRows(rows) {
  const seen = new Set();
  const out = [];
  for (const row of rows) {
    const code = String(row[0]);
    if (seen.has(code)) continue;
    seen.add(code);
    out.push(row);
  }
  return out;
}

function classifyRow(row) {
  const code = String(row[0]);
  if (specialtyMoves[code]) return specialtyMoves[code];
  return spineCodes.has(code) ? spineName : cranialName;
}

function specialtyIdFor(name) {
  return name.toLowerCase().replace(/&/g, 'and').replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
}

function extractSpecs(html) {
  const match = html.match(/const SPECS=(\{[\s\S]*?\});\n\n\/\/ ===== STATE =====/);
  if (!match) throw new Error('Could not locate const SPECS in index.html');
  const context = {};
  vm.createContext(context);
  vm.runInContext('SPECS=' + match[1], context);
  return { specs: context.SPECS, literal: match[1], full: match[0] };
}

function rowFromDatabase(code) {
  const dbPath = path.join(root, 'cpt_database.json');
  if (!fs.existsSync(dbPath)) return null;
  const db = JSON.parse(fs.readFileSync(dbPath, 'utf8'));
  const entry = Array.isArray(db.codes)
    ? db.codes.find(row => String(row.code) === String(code))
    : db[String(code)];
  if (!entry) return null;
  return [String(code), entry.description || ('CPT ' + code), Number(entry.work_rvu || 0), Number(entry.global_period_days || 0)];
}

function optionFromDatabase(code, label, icd10 = []) {
  const row = rowFromDatabase(code) || [String(code), 'CPT ' + code, 0, 0];
  return {
    cpt_code: String(code),
    description: row[1],
    icd10,
    label: label || row[1],
    modifiers: [],
    work_rvu: row[2]
  };
}

function writeJson(file, data) {
  fs.writeFileSync(file, JSON.stringify(data, null, 2) + '\n');
}

function writeObjectJsonPreserveKeyOrder(file, data, preferredText, changedKeys = new Set()) {
  const matches = [...preferredText.matchAll(/^  "([^"\\]+)": \{/gm)];
  const preferredOrder = matches.map(match => match[1]);
  const rawBlocks = {};
  for (let i = 0; i < matches.length; i++) {
    const key = matches[i][1];
    const start = matches[i].index;
    const end = i + 1 < matches.length ? matches[i + 1].index - 2 : preferredText.lastIndexOf('\n}');
    rawBlocks[key] = preferredText.slice(start, end);
  }
  const keys = [...new Set([...preferredOrder, ...Object.keys(data)])].filter(key => Object.prototype.hasOwnProperty.call(data, key));
  const body = keys.map(key => {
    if (!changedKeys.has(key) && rawBlocks[key]) return rawBlocks[key];
    const json = JSON.stringify(data[key], null, 2).split('\n').map(line => '  ' + line).join('\n');
    return '  ' + JSON.stringify(key) + ': ' + json.trimStart();
  }).join(',\n');
  fs.writeFileSync(file, '{\n' + body + '\n}\n');
}

function renderCategoryPage(name, slug, rows, blurb) {
  const title = name + ' CPT Codes';
  const description = title + ' with CPT descriptors, physician work RVUs, global periods, and direct links into FreeCPTCodeFinder code pages.';
  const cards = rows.map(([code, desc, wrvu, global]) => {
    const safeDesc = String(desc).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return '      <a class="code-card neuro-code-card" href="/codes/' + code + '.html"><div class="code-top"><span class="cpt">' + code + '</span><span class="wrvu-pill">' + Number(wrvu || 0).toFixed(2) + ' wRVU</span></div><p>' + safeDesc + '</p><span class="global">Global: ' + global + ' days</span></a>';
  }).join('\n');
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title} | FreeCPTCodeFinder.com</title>
  <meta name="description" content="${description}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://freecptcodefinder.com/categories/${slug}.html">
  <link rel="icon" type="image/png" href="/favicon.png">
  <link rel="apple-touch-icon" href="/logo-192.png">
  <link rel="stylesheet" href="/styles/site-theme.css">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-NPFGH437ZS"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag('js',new Date());gtag('config','G-NPFGH437ZS');</script>
  <script defer src="/js/site-chrome.js"></script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3385830962144023" crossorigin="anonymous"></script>
  <meta property="og:title" content="${title} | FreeCPTCodeFinder.com">
  <meta property="og:description" content="${description}">
  <meta property="og:url" content="https://freecptcodefinder.com/categories/${slug}.html">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Free CPT Code Finder">
  <meta property="og:image" content="https://freecptcodefinder.com/og-image.png">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="${title} | FreeCPTCodeFinder.com">
  <meta name="twitter:description" content="${description}">
  <meta name="twitter:image" content="https://freecptcodefinder.com/og-image.png">
  <script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"CollectionPage","name":"${title}","url":"https://freecptcodefinder.com/categories/${slug}.html","description":"${description}","isPartOf":{"@type":"WebSite","name":"FreeCPTCodeFinder.com","url":"https://freecptcodefinder.com/"}},{"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://freecptcodefinder.com/"},{"@type":"ListItem","position":2,"name":"Neurosurgery","item":"https://freecptcodefinder.com/#case-builder"},{"@type":"ListItem","position":3,"name":"${name}","item":"https://freecptcodefinder.com/categories/${slug}.html"}]}]}</script>
  <style>
    .code-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px;margin-top:18px}
    .code-card.neuro-code-card{display:block!important;border:1px solid var(--line);border-radius:8px;padding:14px;background:var(--white);text-decoration:none;min-width:0}
    .code-top{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}
    .code-card.neuro-code-card .cpt{font-size:20px;font-weight:800;color:var(--ox);min-width:auto}
    .wrvu-pill,.global{font-size:12px;font-weight:700;border:1px solid var(--line2);border-radius:999px;padding:4px 8px;color:var(--ink2);white-space:nowrap}
    .code-card.neuro-code-card p{margin:0 0 12px;color:var(--ink2);line-height:1.45;overflow-wrap:break-word}
    .subnav{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0 20px}
    .subnav a{border:1px solid var(--line);border-radius:999px;padding:7px 11px;text-decoration:none;font-weight:700;font-size:14px}
    @media(max-width:700px){.code-grid{grid-template-columns:1fr}.code-top{align-items:flex-start;flex-direction:column}}
  </style>
</head>
<body>
<div class="site-shell">
<div class="site-page" data-site-header></div>
<main class="site-content-wrap site-richtext">
  <div class="wrap">
    <div class="breadcrumb"><a href="/">Home</a> / Neurosurgery / ${name}</div>
    <h1>${title}</h1>
    <p class="last-updated">Last reviewed: June 7, 2026</p>
    <p>${blurb}</p>
    <div class="subnav">
      <a href="/categories/${cranialSlug}.html">Skull Base / Cranial Neurosurgery</a>
      <a href="/categories/${spineSlug}.html">Spine Neurosurgery</a>
      <a href="/#case-builder">Open case builder</a>
    </div>
    <div class="quick-answer">
      <h2>Category Count</h2>
      <p>This category contains ${rows.length} CPT codes moved from the prior broad Neurosurgery section. CPT descriptors and RVU values were preserved from the existing site data.</p>
    </div>
    <h2>${name} CPT Codes</h2>
    <div class="code-grid">
${cards}
    </div>
  </div>
</main>
<div class="site-page" data-site-footer></div>
</div>
</body>
</html>
`;
}

const indexPath = path.join(root, 'index.html');
const indexHtml = fs.readFileSync(indexPath, 'utf8');
const { specs, literal, full } = extractSpecs(indexHtml);
const extraRows = Object.keys(legacyNeurosurgeryExtraCodes).flatMap(code => {
  for (const rows of Object.values(specs)) {
    const existing = rows.find(row => String(row[0]) === code);
    if (existing) return [existing];
  }
  const row = rowFromDatabase(code);
  return row ? [row] : [];
});
const originalNeuroRows = specs.Neurosurgery || [
  ...(specs[cranialName] || []),
  ...(specs[spineName] || []),
  ...Object.entries(specialtyMoves).flatMap(([code, destination]) => (specs[destination] || []).filter(row => String(row[0]) === code)),
  ...extraRows
];
if (!originalNeuroRows.length) throw new Error('No Neurosurgery rows found in SPECS');

const cranialRows = uniqueRows(originalNeuroRows.filter(row => classifyRow(row) === cranialName));
const spineRows = uniqueRows(originalNeuroRows.filter(row => classifyRow(row) === spineName));
const relocatedRows = uniqueRows(originalNeuroRows.filter(row => ![cranialName, spineName].includes(classifyRow(row))));
const originalCodes = [...new Set(originalNeuroRows.map(row => String(row[0])))].sort();
const movedCodes = [...cranialRows.map(row => String(row[0])), ...spineRows.map(row => String(row[0])), ...relocatedRows.map(row => String(row[0]))].sort();
const lostCodes = originalCodes.filter(code => !movedCodes.includes(code));
const duplicatedCodes = movedCodes.filter((code, idx, arr) => arr.indexOf(code) !== idx);
if (lostCodes.length) throw new Error('Lost Neurosurgery codes: ' + lostCodes.join(', '));
if (duplicatedCodes.length) throw new Error('Duplicated split codes: ' + duplicatedCodes.join(', '));

const nextSpecs = {};
let insertedSplitSpecs = false;
for (const [name, rows] of Object.entries(specs)) {
  if (name === 'Neurosurgery' || name === cranialName || name === spineName) {
    if (insertedSplitSpecs) continue;
    nextSpecs[cranialName] = cranialRows;
    nextSpecs[spineName] = spineRows;
    insertedSplitSpecs = true;
  } else {
    nextSpecs[name] = rows;
  }
}
for (const [code, destination] of Object.entries(specialtyMoves)) {
  for (const [name, rows] of Object.entries(nextSpecs)) {
    if (name !== destination) nextSpecs[name] = rows.filter(row => String(row[0]) !== code);
  }
}
for (const row of relocatedRows) {
  const destination = classifyRow(row);
  if (!nextSpecs[destination]) nextSpecs[destination] = [];
  const code = String(row[0]);
  if (!nextSpecs[destination].some(existing => String(existing[0]) === code)) {
    nextSpecs[destination].push(row);
  }
}
const nextLiteral = JSON.stringify(nextSpecs);
fs.writeFileSync(indexPath, indexHtml.replace(full, 'const SPECS=' + nextLiteral + ';\n\n// ===== STATE ====='));

const treePath = path.join(root, 'cpt_decision_tree.json');
const tree = JSON.parse(fs.readFileSync(treePath, 'utf8'));
let neuroIndex = tree.categories.findIndex(c => c.name === 'Neurosurgery');
let neuro = neuroIndex === -1 ? null : tree.categories[neuroIndex];
if (!neuro) {
  const cranialExisting = tree.categories.find(c => c.name === cranialName);
  const spineExisting = tree.categories.find(c => c.name === spineName);
  if (!cranialExisting || !spineExisting) throw new Error('No Neurosurgery or split Neurosurgery categories in cpt_decision_tree.json');
  neuro = {
    branches: {
      ...cranialExisting.branches,
      spinal_fusion_questions: spineExisting.branches.spinal_fusion_questions,
      decompress_questions: spineExisting.branches.decompress_questions,
      peripheral_nerve_questions: {
        question: 'Type of nerve procedure?',
        options: [
          ...(cranialExisting.branches.peripheral_nerve_cranial_review?.options || []),
          ...(spineExisting.branches.spinal_stimulator_questions?.options || [])
        ]
      }
    }
  };
  neuroIndex = Math.min(
    tree.categories.findIndex(c => c.name === cranialName),
    tree.categories.findIndex(c => c.name === spineName)
  );
  tree.categories = tree.categories.filter(c => c.name !== cranialName && c.name !== spineName);
}
const branchCopy = name => JSON.parse(JSON.stringify(neuro.branches[name]));
const cranialCategory = {
  name: cranialName,
  specialty: cranialName,
  questions: [{
    question: 'Type of skull base or cranial neurosurgical procedure?',
    options: [
      { label: 'Craniotomy', next: 'craniotomy_questions' },
      { label: 'Burr Hole Procedures', next: 'burr_hole_questions' },
      { label: 'Shunt Procedures', next: 'shunt_questions' },
      { label: 'ICP Monitoring', next: 'icp_monitor_questions' },
      { label: 'Cranial / hemorrhage / decompression', next: 'neuro_cranial_extra' },
      { label: 'Tumor / skull base / stereotactic', next: 'neuro_tumor_extra' },
      { label: 'Functional / shunt / cranial reconstruction', next: 'neuro_functional_extra' }
    ]
  }],
  branches: {
    craniotomy_questions: branchCopy('craniotomy_questions'),
    burr_hole_questions: branchCopy('burr_hole_questions'),
    shunt_questions: branchCopy('shunt_questions'),
    icp_monitor_questions: branchCopy('icp_monitor_questions'),
    neuro_cranial_extra: branchCopy('neuro_cranial_extra'),
    neuro_tumor_extra: branchCopy('neuro_tumor_extra'),
    neuro_functional_extra: branchCopy('neuro_functional_extra')
  }
};
for (const branch of Object.values(cranialCategory.branches)) {
  if (Array.isArray(branch.options)) {
    branch.options = branch.options.filter(option => String(option.cpt_code || '') !== '61782');
  }
}
const spineStimOptions = branchCopy('peripheral_nerve_questions').options.filter(o => ['63650','63655'].includes(String(o.cpt_code)));
const spineCategory = {
  name: spineName,
  specialty: spineName,
  questions: [{
    question: 'Type of spine neurosurgical procedure?',
    options: [
      { label: 'Spinal Fusion', next: 'spinal_fusion_questions' },
      { label: 'Laminectomy/Discectomy', next: 'decompress_questions' },
      { label: 'Lumbar puncture / epidural access / navigation', next: 'spinal_access_navigation_questions' },
      { label: 'Spinal Cord Stimulator', next: 'spinal_stimulator_questions' }
    ]
  }],
  branches: {
    spinal_fusion_questions: branchCopy('spinal_fusion_questions'),
    decompress_questions: branchCopy('decompress_questions'),
    spinal_access_navigation_questions: {
      question: 'Type of spinal access or navigation procedure?',
      options: [
        optionFromDatabase('62270', 'Lumbar puncture, diagnostic', ['G03.9', 'G93.2']),
        optionFromDatabase('62322', 'Lumbar epidural injection, without imaging', ['M54.16']),
        optionFromDatabase('62323', 'Lumbar epidural injection, with imaging guidance', ['M54.16']),
        optionFromDatabase('61782', 'Stereotactic spinal navigation', ['M48.00']),
        optionFromDatabase('61783', 'Stereotactic navigation, spinal add-on', ['M48.00'])
      ]
    },
    spinal_stimulator_questions: {
      question: 'Type of spinal cord stimulator procedure?',
      options: spineStimOptions
    }
  }
};
tree.categories.splice(neuroIndex, neuro.name === 'Neurosurgery' ? 1 : 0, cranialCategory, spineCategory);
writeJson(treePath, tree);

const dbPath = path.join(root, 'cpt_database.json');
if (fs.existsSync(dbPath)) {
  const originalDbText = fs.readFileSync(dbPath, 'utf8');
  const db = JSON.parse(originalDbText);
  if (Array.isArray(db.codes)) {
    for (const row of db.codes) {
      const code = String(row.code);
      if (originalCodes.includes(code)) {
        const nextName = classifyRow([code]);
        row.specialty = nextName;
        row.specialty_id = specialtyIdFor(nextName);
        row.code_family = specialtyIdFor(nextName);
      }
    }
    writeJson(dbPath, db);
  } else {
    const changedKeys = new Set();
    for (const code of originalCodes) {
      if (!db[code]) continue;
      const nextName = classifyRow([code]);
      db[code].specialty = nextName;
      db[code].specialty_id = specialtyIdFor(nextName);
      db[code].code_family = specialtyIdFor(nextName);
      changedKeys.add(code);
    }
    writeObjectJsonPreserveKeyOrder(dbPath, db, originalDbText, changedKeys);
  }
}

fs.writeFileSync(path.join(root, 'categories', cranialSlug + '.html'), renderCategoryPage(
  cranialName,
  cranialSlug,
  cranialRows,
  'Skull Base / Cranial Neurosurgery includes craniotomy, cranial trauma, intracranial tumor and vascular procedures, CSF shunts, stereotactic cranial work, functional cranial procedures, and legacy non-spine rows that were previously grouped under the broad Neurosurgery section.'
));
fs.writeFileSync(path.join(root, 'categories', spineSlug + '.html'), renderCategoryPage(
  spineName,
  spineSlug,
  spineRows,
  'Spine Neurosurgery includes cervical, thoracic, lumbar, and sacral decompression, discectomy, fusion, spinal navigation, epidural access, and spinal cord stimulator procedures moved from the prior broad Neurosurgery section.'
));

for (const [name, rows] of [[cranialName, cranialRows], [spineName, spineRows], ...Object.entries(Object.groupBy ? Object.groupBy(relocatedRows, classifyRow) : relocatedRows.reduce((acc,row)=>{(acc[classifyRow(row)] ||= []).push(row); return acc;}, {}))]) {
  for (const [code] of rows) {
    const file = path.join(root, 'codes', String(code) + '.html');
    if (!fs.existsSync(file)) continue;
    let html = fs.readFileSync(file, 'utf8');
    html = html.replace(/(<div class="breadcrumb"><a href="\/">Home<\/a> → <a href="\/">CPT Codes<\/a> → <a href="\/">)(?:Neurosurgery|Skull Base \/ Cranial Neurosurgery|Spine Neurosurgery)(<\/a> → CPT )/g, '$1' + name + '$2');
    html = html.replace(/<span class="badge">(?:Neurosurgery|Skull Base \/ Cranial Neurosurgery|Spine Neurosurgery)<\/span>/g, '<span class="badge">' + name + '</span>');
    html = html.replace(/Related CPT Codes in (?:Neurosurgery|Skull Base \/ Cranial Neurosurgery|Spine Neurosurgery)/g, 'Related CPT Codes in ' + name);
    html = html.replace(/Common audit checks for (?:neurosurgery|skull base \/ cranial neurosurgery|spine neurosurgery) cases/g, 'Common audit checks for ' + name.toLowerCase() + ' cases');
    fs.writeFileSync(file, html);
  }
}

const sitemapPath = path.join(root, 'sitemap.xml');
if (fs.existsSync(sitemapPath)) {
  let sitemap = fs.readFileSync(sitemapPath, 'utf8');
  const entries = [cranialSlug, spineSlug].map(slug => `  <url>
    <loc>https://freecptcodefinder.com/categories/${slug}.html</loc>
    <lastmod>${today}</lastmod>
  </url>`).join('\n');
  for (const slug of [cranialSlug, spineSlug]) {
    if (!sitemap.includes('/categories/' + slug + '.html')) {
      sitemap = sitemap.replace(/<\/urlset>\s*$/, entries + '\n</urlset>\n');
      break;
    }
  }
  fs.writeFileSync(sitemapPath, sitemap);
}

const manualReview = Object.entries(manualReviewNotes)
  .filter(([code]) => originalCodes.includes(code))
  .filter(([code]) => !specialtyMoves[code])
  .map(([code, note]) => ({ code, assigned_to: classifyRow([code]), note }));
const relocated = relocatedRows.map(row => ({
  code: String(row[0]),
  destination: classifyRow(row),
  description: row[1]
}));

const report = {
  generated_at: new Date().toISOString(),
  source_category: 'Neurosurgery',
  original_unique_code_count: originalCodes.length,
  skull_base_cranial_neurosurgery: {
    count: cranialRows.length,
    codes: cranialRows.map(row => String(row[0]))
  },
  spine_neurosurgery: {
    count: spineRows.length,
    codes: spineRows.map(row => String(row[0]))
  },
  relocated_to_existing_specialties: relocated,
  manual_review: manualReview,
  lost_codes: lostCodes,
  duplicate_codes_after_split: duplicatedCodes
};
writeJson(path.join(artifactDir, 'migration_report.json'), report);

const md = `# Neurosurgery Split Migration Report

Generated: ${today}

## Summary

- Source category audited: Neurosurgery
- Original unique CPT codes: ${originalCodes.length}
- Skull Base / Cranial Neurosurgery: ${cranialRows.length}
- Spine Neurosurgery: ${spineRows.length}
- Relocated to existing non-neurosurgery specialties: ${relocatedRows.length}
- Lost CPT codes during migration: ${lostCodes.length}
- Duplicate CPT codes after split: ${duplicatedCodes.length}

## Skull Base / Cranial Neurosurgery Codes

${cranialRows.map(row => '- ' + row[0] + ' - ' + row[1]).join('\n')}

## Spine Neurosurgery Codes

${spineRows.map(row => '- ' + row[0] + ' - ' + row[1]).join('\n')}

## Manual Review

${manualReview.map(item => '- ' + item.code + ' assigned to ' + item.assigned_to + ': ' + item.note).join('\n') || '- None'}

## Relocated To Existing Specialties

${relocated.map(item => '- ' + item.code + ' -> ' + item.destination + ' - ' + item.description).join('\n') || '- None'}

## Integrity Check

- Original Neurosurgery code union equals cranial + spine + relocated union: ${lostCodes.length === 0 && duplicatedCodes.length === 0 ? 'PASS' : 'FAIL'}
- No code intentionally duplicated between the two new Neurosurgery categories.
- CPT descriptors, work RVUs, and global-period values were preserved from the existing homepage data.
- Deployment status: NOT DEPLOYED. Awaiting review.

## Screenshots

- Skull Base / Cranial Neurosurgery: qa_artifacts/neurosurgery_split_2026_06_07/screenshots/skull-base-cranial-neurosurgery.png
- Spine Neurosurgery: qa_artifacts/neurosurgery_split_2026_06_07/screenshots/spine-neurosurgery.png
`;
fs.writeFileSync(path.join(artifactDir, 'migration_report.md'), md);

console.log(JSON.stringify({
  original: originalCodes.length,
  cranial: cranialRows.length,
  spine: spineRows.length,
  manual_review: manualReview.length,
  lost: lostCodes.length,
  duplicates: duplicatedCodes.length,
  report: path.relative(root, path.join(artifactDir, 'migration_report.md'))
}, null, 2));
