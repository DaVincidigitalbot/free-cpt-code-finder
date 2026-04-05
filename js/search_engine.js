/**
 * UnifiedSearchEngine for FreeCPTCodeFinder
 * Loads rvu_database.json + icd10_common.json (+ optional cpt_database.json, icd10_database.json)
 * Real-time search with 150ms debounce, grouped results.
 */

class UnifiedSearchEngine {
  constructor() {
    this.cptIndex = [];          // flat array of indexed CPT items
    this.icd10Index = [];        // flat array of indexed ICD-10 items
    this.rawCPT = {};            // code → data
    this.rawICD10 = {};          // system → { codes: [...] }
    this.debounceTimer = null;
    this.DEBOUNCE_MS = 150;
    this.MAX_RESULTS = 60;
    this.ready = false;
    this.onResultClick = null;   // callback(item) when user clicks a search result
  }

  /* ── Initialise ─────────────────────────────────────────── */
  async initialize() {
    const safe = (url) =>
      fetch(url).then(r => r.ok ? r.json() : null).catch(() => null);

    const [rvuDb, icd10Common, cptExtra, icd10Extra] = await Promise.all([
      safe('./rvu_database.json'),
      safe('./icd10_common.json'),
      safe('./cpt_database.json'),
      safe('./icd10_database.json'),
    ]);

    // Merge CPT sources
    this.rawCPT = {};
    if (rvuDb) {
      const codes = rvuDb.codes || rvuDb;
      Object.assign(this.rawCPT, codes);
    }
    if (cptExtra) {
      const codes = cptExtra.codes || cptExtra;
      Object.assign(this.rawCPT, codes);
    }

    // Merge ICD-10 sources
    this.rawICD10 = {};
    if (icd10Common) Object.assign(this.rawICD10, icd10Common);
    if (icd10Extra)  Object.assign(this.rawICD10, icd10Extra);

    this._buildIndexes();
    this.ready = true;
    console.log(`[SearchEngine] Ready — ${this.cptIndex.length} CPT, ${this.icd10Index.length} ICD-10 codes indexed`);
  }

  _buildIndexes() {
    // CPT index
    this.cptIndex = [];
    for (const [code, d] of Object.entries(this.rawCPT)) {
      if (!d) continue;
      const cat = this._categorizeCPT(code);
      const specialty = d.specialty || cat;
      this.cptIndex.push({
        type: 'cpt',
        code,
        description: d.description || '',
        wRVU: d.work_rvu || 0,
        totalRVU: d.total_rvu || 0,
        peRVU: d.pe_rvu || 0,
        mpRVU: d.mp_rvu || 0,
        globalPeriod: d.global_period || 0,
        category: cat,
        specialty,
        _search: `${code} ${(d.description || '').toLowerCase()} ${specialty.toLowerCase()}`,
      });
    }

    // ICD-10 index
    this.icd10Index = [];
    for (const [system, sysData] of Object.entries(this.rawICD10)) {
      const codes = sysData.codes || (Array.isArray(sysData) ? sysData : []);
      for (const item of codes) {
        this.icd10Index.push({
          type: 'icd10',
          code: item.code,
          description: item.description || '',
          system,
          category: 'ICD-10',
          _search: `${item.code} ${(item.description || '').toLowerCase()} ${system.toLowerCase()}`,
        });
      }
    }
  }

  _categorizeCPT(code) {
    const n = parseInt(code, 10);
    if (n >= 99201 && n <= 99499) return 'E/M';
    if (n >= 10000 && n <= 19999) return 'Surgery — Integumentary';
    if (n >= 20000 && n <= 29999) return 'Surgery — Musculoskeletal';
    if (n >= 30000 && n <= 32999) return 'Surgery — Respiratory';
    if (n >= 33000 && n <= 37999) return 'Surgery — Cardiovascular';
    if (n >= 38000 && n <= 38999) return 'Surgery — Hemic/Lymphatic';
    if (n >= 40000 && n <= 49999) return 'Surgery — Digestive';
    if (n >= 50000 && n <= 53999) return 'Surgery — Urinary';
    if (n >= 54000 && n <= 55899) return 'Surgery — Male Genital';
    if (n >= 55920 && n <= 58999) return 'Surgery — Female Genital';
    if (n >= 59000 && n <= 59899) return 'Surgery — Maternity';
    if (n >= 60000 && n <= 60699) return 'Surgery — Endocrine';
    if (n >= 61000 && n <= 64999) return 'Surgery — Nervous';
    if (n >= 65000 && n <= 68999) return 'Surgery — Eye/Ocular';
    if (n >= 69000 && n <= 69979) return 'Surgery — Auditory';
    if (n >= 70000 && n <= 79999) return 'Radiology';
    if (n >= 80000 && n <= 89999) return 'Pathology';
    if (n >= 90000 && n <= 99199) return 'Medicine';
    return 'Other';
  }

  /* ── Search ─────────────────────────────────────────────── */
  search(query) {
    if (!this.ready) return [];
    const q = (query || '').trim().toLowerCase();
    if (!q) return [];

    const tokens = q.split(/\s+/);
    const scored = [];

    const match = (item) => {
      let score = 0;
      for (const tok of tokens) {
        if (!item._search.includes(tok)) return 0;
        // Exact code match gets highest score
        if (item.code.toLowerCase() === tok) score += 100;
        else if (item.code.toLowerCase().startsWith(tok)) score += 50;
        else score += 10;
      }
      // Boost by wRVU for CPT
      if (item.wRVU) score += Math.min(item.wRVU, 20);
      return score;
    };

    // Score CPT
    for (const item of this.cptIndex) {
      const s = match(item);
      if (s > 0) scored.push({ ...item, _score: s });
    }
    // Score ICD-10
    for (const item of this.icd10Index) {
      const s = match(item);
      if (s > 0) scored.push({ ...item, _score: s });
    }

    scored.sort((a, b) => b._score - a._score);
    return scored.slice(0, this.MAX_RESULTS);
  }

  /* ── Grouped results ────────────────────────────────────── */
  searchGrouped(query) {
    const results = this.search(query);
    const groups = {};
    for (const r of results) {
      const g = r.type === 'icd10' ? 'ICD-10' : (r.category || 'Other');
      if (!groups[g]) groups[g] = [];
      groups[g].push(r);
    }
    return groups;
  }

  /* ── Lookup helpers ─────────────────────────────────────── */
  getCPT(code) {
    return this.cptIndex.find(i => i.code === code) || null;
  }

  getICD10(code) {
    return this.icd10Index.find(i => i.code === code) || null;
  }

  getAllCPT() {
    return this.cptIndex;
  }

  getICD10Systems() {
    return Object.keys(this.rawICD10);
  }

  getICD10BySystem(system) {
    const s = this.rawICD10[system];
    if (!s) return [];
    return s.codes || (Array.isArray(s) ? s : []);
  }

  /* ── UI Binding ─────────────────────────────────────────── */
  bindToInput(inputEl, dropdownEl) {
    if (!inputEl || !dropdownEl) return;

    inputEl.addEventListener('input', () => {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = setTimeout(() => {
        const q = inputEl.value;
        if (q.trim().length < 2) {
          dropdownEl.classList.remove('visible');
          dropdownEl.innerHTML = '';
          return;
        }
        const groups = this.searchGrouped(q);
        this._renderDropdown(dropdownEl, groups);
      }, this.DEBOUNCE_MS);
    });

    inputEl.addEventListener('focus', () => {
      if (inputEl.value.trim().length >= 2 && dropdownEl.children.length) {
        dropdownEl.classList.add('visible');
      }
    });

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
      if (!inputEl.contains(e.target) && !dropdownEl.contains(e.target)) {
        dropdownEl.classList.remove('visible');
      }
    });

    // Keyboard nav
    inputEl.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        dropdownEl.classList.remove('visible');
      }
    });
  }

  _renderDropdown(container, groups) {
    container.innerHTML = '';
    const keys = Object.keys(groups);

    if (keys.length === 0) {
      container.innerHTML = '<div class="search-empty">No results found</div>';
      container.classList.add('visible');
      return;
    }

    // Preferred group order
    const order = [
      'Surgery — Digestive', 'Surgery — Integumentary', 'Surgery — Musculoskeletal',
      'Surgery — Cardiovascular', 'Surgery — Respiratory', 'Surgery — Urinary',
      'Surgery — Endocrine', 'Surgery — Nervous', 'Surgery — Hemic/Lymphatic',
      'Surgery — Male Genital', 'Surgery — Female Genital', 'Surgery — Maternity',
      'Surgery — Eye/Ocular', 'Surgery — Auditory',
      'E/M', 'Radiology', 'Pathology', 'Medicine', 'ICD-10', 'Other'
    ];

    const sortedKeys = keys.sort((a, b) => {
      const ia = order.indexOf(a), ib = order.indexOf(b);
      return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib);
    });

    for (const groupName of sortedKeys) {
      const items = groups[groupName];
      const label = document.createElement('div');
      label.className = 'search-group-label';
      label.textContent = `${groupName} (${items.length})`;
      container.appendChild(label);

      for (const item of items.slice(0, 10)) {
        const card = document.createElement('div');
        card.className = 'search-result-card';
        card.innerHTML = `
          <span class="search-result-card__code">${item.code}</span>
          <span class="search-result-card__desc">${this._highlight(item.description, 80)}</span>
          <span class="search-result-card__meta">
            ${item.type === 'cpt' ? `<span class="search-result-card__wrvu">${item.wRVU.toFixed(2)} wRVU</span>` : ''}
            <span class="search-result-card__specialty">${item.type === 'icd10' ? item.system.replace(/_/g, ' ') : (item.specialty || '')}</span>
          </span>
        `;
        card.addEventListener('click', () => {
          if (typeof this.onResultClick === 'function') {
            this.onResultClick(item);
          }
          container.classList.remove('visible');
        });
        container.appendChild(card);
      }
    }

    container.classList.add('visible');
  }

  _highlight(text, maxLen) {
    if (!text) return '';
    if (text.length > maxLen) return text.slice(0, maxLen) + '...';
    return text;
  }
}

// Export for module or global
if (typeof module !== 'undefined' && module.exports) {
  module.exports = UnifiedSearchEngine;
}
