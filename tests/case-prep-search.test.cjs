const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const read = path => JSON.parse(fs.readFileSync(path, 'utf8'));
const context = { document: { addEventListener() {} }, URL };
vm.createContext(context);
const source = fs.readFileSync('js/case-prep-library.js', 'utf8').replace(/\}\)\(\);\s*$/, 'globalThis.api = {buildCatalog, searchCatalog, cardMarkup, expandSearch};})();');
vm.runInContext(source, context);
const {buildCatalog, searchCatalog, cardMarkup, expandSearch} = context.api;
const imported = read('case-prep/clinical-library-index.json').procedures;
const guides = read('case-prep/case-prep-data.json').procedures;
const catalog = buildCatalog(imported, guides);
const search = (q, category='all') => searchCatalog(catalog, q, category);
test('common searches work with reordered words, punctuation, case, and abbreviations', () => {
  for (const q of ['robotic inguinal hernia', 'hernia inguinal robotic', ' ROBOTIC / inguinal--hernia ']) {
    assert.deepEqual(search(q).slice(0, 2).map(x => x.id).sort(), ['robotic-etep-inguinal-hernia', 'robotic-tapp-inguinal-hernia']);
  }
  for (const q of ['lap chole', 'chole lap', 'LAP-CHOLE']) {
    assert.equal(search(q)[0].url, '/case-prep/laparoscopic-cholecystectomy/');
    assert.equal(search(q).filter(x => x.id === 'lap-chole').length, 0);
    assert.equal(search(q)[0].rapidUrl, '/case-prep/library/?procedure=lap-chole');
  }
  assert.equal(search('appy')[0].url, '/case-prep/laparoscopic-appendectomy/');
  assert.equal(search('ex lap')[0].url, '/case-prep/exploratory-laparotomy/');
  assert.equal(search('lap ex')[0].url, '/case-prep/exploratory-laparotomy/');
  assert.equal(search('lap/ex')[0].url, '/case-prep/exploratory-laparotomy/');
  assert.equal(search('TAR')[0].url, '/case-prep/transversus-abdominis-release/');
  assert.equal(search('T.A.R.')[0].url, '/case-prep/transversus-abdominis-release/');
  assert.ok(search('T.A.R.').length < 10);
  assert.ok(search('eTEP').some(x => x.id === 'robotic-etep-inguinal-hernia'));
  assert.equal(search('robotic TAPP inguinal hernia')[0].id, 'robotic-tapp-inguinal-hernia');
  assert.equal(search('TAPP')[0].id, 'robotic-tapp-inguinal-hernia');
  assert.equal(search('T.A.P.P.')[0].id, 'robotic-tapp-inguinal-hernia');
  assert.equal(search('T.A.P.P.').length, 1);
  assert.equal(search('robotic eTEP inguinal hernia')[0].id, 'robotic-etep-inguinal-hernia');
  assert.notEqual(search('TAPP')[0].id, search('eTEP')[0].id);
  assert.equal(search('chest tube')[0].url, '/case-prep/chest-tube-placement/');
  assert.equal(search('chest tube').length, 1);
  assert.equal(search('Whipple')[0].id, 'whipple');
  assert.equal(search('robotic eTEP ventral hernia').length, 0);
});
test('category filters, empty searches, and no matches remain predictable', () => {
  assert.ok(search('', 'Hernia').length > 0);
  assert.ok(search('', 'Hernia').every(x => x.category === 'Hernia'));
  assert.equal(search('lap chole', 'Hernia').length, 0);
  assert.equal(search('zzzznooperation').length, 0);
  assert.equal(search('  /  ').length, catalog.length);
  assert.equal(new Set(catalog.map(x => x.id)).size, catalog.length);
  const canonicalCategories = new Set(read('case-prep/clinical-library-index.json').categories);
  assert.deepEqual([...new Set(catalog.map(x => x.category).filter(x => !canonicalCategories.has(x)))], []);
  assert.equal(search('TAR', 'Hernia')[0].url, '/case-prep/transversus-abdominis-release/');
  assert.equal(search('hiatal hernia', 'Hernia')[0].url, '/case-prep/hiatal-hernia-repair/');
});
test('all source records remain reachable and planned guides stay unpublished', () => {
  const html = catalog.map(cardMarkup).join('');
  for (const record of imported) assert.ok(html.includes('procedure=' + record.id), record.id);
  for (const guide of guides.filter(x => x.status === 'live')) assert.ok(html.includes('/case-prep/' + guide.slug + '/'));
  assert.ok(!html.includes('href="/case-prep/inguinal-hernia-repair/"'));
});
test('untrusted titles and URLs are escaped', () => {
  const html = cardMarkup({id:'x',name:'<script>alert(1)</script>', category:'"',overview:'<img>',url:'" onmouseover="x'});
  assert.ok(!html.includes('<script>'));
  assert.ok(html.includes('&lt;script&gt;'));
  assert.ok(!html.includes('href="" onmouseover='));
  const unsafe = cardMarkup({id:'x',name:'Unsafe',category:'Test',overview:'Test',url:'javascript:alert(1)'});
  assert.ok(!unsafe.includes('javascript:'));
  assert.ok(unsafe.includes('/case-prep/library/?procedure=x'));
  for (const url of [String.raw`/\evil.example/path`, String.raw`/\\evil.example/path`, '//evil.example/path']) {
    const backslash = cardMarkup({id:'x',name:'Unsafe',category:'Test',overview:'Test',url});
    assert.ok(!backslash.includes('evil.example'));
    assert.ok(backslash.includes('/case-prep/library/?procedure=x'));
  }
});
test('landing controls wire to live results, clear, category, and example actions', async () => {
  const elements = new Map();
  const element = selector => {
    if (!elements.has(selector)) elements.set(selector, {
      value: selector === '[data-library-category]' ? 'all' : '', hidden: false,
      dataset: {}, innerHTML: '', textContent: '', listeners: {},
      addEventListener(name, callback) { this.listeners[name] = callback; },
      dispatchEvent(event) { this.listeners[event.type]?.(event); },
      setAttribute(name, value) { this[name] = value; },
      querySelectorAll() { return []; }, insertAdjacentHTML() {}, focus() {},
    });
    return elements.get(selector);
  };
  const root = { querySelector: element, querySelectorAll: () => [] };
  let ready;
  const document = {
    addEventListener(name, cb) { if(name === 'DOMContentLoaded') ready = cb; },
    querySelector(selector) {
      if(selector === '[data-case-prep-library-home]') return root;
      if(selector === '[data-procedure-detail]') return null;
      return element(selector);
    },
    querySelectorAll(selector) {
      if(selector === '[data-library-search],[data-library-category],[data-library-reset],[data-search-example]') {
        return ['[data-library-search]','[data-library-category]','[data-library-reset]','[data-search-example]'].map(element);
      }
      return [];
    },
  };
  const sandbox = {document, console, URL, fetch: async url => ({ok:true, json:async () =>
    read(url.includes('clinical-library-index') ? 'case-prep/clinical-library-index.json' : 'case-prep/case-prep-data.json')})};
  vm.createContext(sandbox);
  vm.runInContext(fs.readFileSync('js/case-prep-library.js','utf8'), sandbox);
  // A visitor may type before the catalogs finish downloading.
  element('[data-library-search]').value = 'robotic inguinal hernia';
  await ready();
  assert.equal(element('[data-library-search]').disabled, false);
  assert.equal(element('[data-library-count]').textContent, '2 resources matching “robotic inguinal hernia”');
  const grid = element('[data-library-grid]');
  assert.ok(grid.innerHTML.includes('Robotic eTEP Inguinal Hernia Repair'));
  const input = element('[data-library-search]');
  input.value = 'lap chole'; input.dispatchEvent({type:'input'});
  assert.ok(grid.innerHTML.includes('/case-prep/laparoscopic-cholecystectomy/'));
  const category = element('[data-library-category]');
  category.value = 'Hernia'; category.dispatchEvent({type:'change'});
  assert.equal(element('[data-library-empty]').hidden, false);
  element('[data-library-reset]').dispatchEvent({type:'click'});
  assert.equal(input.value, '');
  assert.equal(category.value, 'all');
  assert.equal(element('[data-library-empty]').hidden, true);
});
