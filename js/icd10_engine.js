/**
 * ICD10Engine for FreeCPTCodeFinder
 * Loads icd10_common.json (+ optional icd10_database.json)
 * Provides search, system browsing, and related CPT suggestions.
 */

class ICD10Engine {
  constructor() {
    this.systems = {};           // systemKey → { description, code_range, codes: [...] }
    this.allCodes = [];          // flat array for search
    this.searchEngine = null;    // ref to UnifiedSearchEngine for CPT suggestions
    this.caseBuilder = null;     // ref to CaseBuilder

    // DOM refs
    this.sectionEl = null;
    this.tabsEl = null;
    this.resultsEl = null;
    this.searchInput = null;

    this.activeSystem = null;
    this.ready = false;

    // Rough ICD-10 → CPT mapping for related suggestions
    this._icdCptMap = this._buildRelatedMap();
  }

  /* ── Initialise ─────────────────────────────────────────── */
  async initialize(sectionEl, tabsEl, resultsEl, searchInput) {
    this.sectionEl = sectionEl;
    this.tabsEl = tabsEl;
    this.resultsEl = resultsEl;
    this.searchInput = searchInput;

    const safe = (url) =>
      fetch(url).then(r => r.ok ? r.json() : null).catch(() => null);

    const [icd10Common, icd10Extra] = await Promise.all([
      safe('./icd10_common.json'),
      safe('./icd10_database.json'),
    ]);

    if (icd10Common) Object.assign(this.systems, icd10Common);
    if (icd10Extra) Object.assign(this.systems, icd10Extra);

    // Build flat list
    this.allCodes = [];
    for (const [sysKey, sysData] of Object.entries(this.systems)) {
      const codes = sysData.codes || (Array.isArray(sysData) ? sysData : []);
      for (const item of codes) {
        this.allCodes.push({
          ...item,
          system: sysKey,
          systemLabel: sysData.description || sysKey.replace(/_/g, ' '),
          _search: `${item.code} ${(item.description || '').toLowerCase()}`,
        });
      }
    }

    this.ready = true;
    this._renderTabs();
    this._bindSearch();

    // Show first system by default
    const first = Object.keys(this.systems)[0];
    if (first) this.showSystem(first);

    console.log(`[ICD10Engine] Ready — ${this.allCodes.length} codes across ${Object.keys(this.systems).length} systems`);
  }

  /* ── Tabs ───────────────────────────────────────────────── */
  _renderTabs() {
    if (!this.tabsEl) return;
    this.tabsEl.innerHTML = '';

    const systemLabels = {
      digestive_system: 'Digestive',
      endocrine_system: 'Endocrine',
      circulatory_system: 'Circulatory',
      respiratory_system: 'Respiratory',
      musculoskeletal_system: 'Musculoskeletal',
      injury_trauma_system: 'Injury/Trauma',
      neoplasm_system: 'Neoplasms',
      genitourinary_system: 'Genitourinary',
      skin_system: 'Skin',
      nervous_system: 'Nervous',
      infectious_system: 'Infectious',
      blood_system: 'Blood',
      mental_system: 'Mental',
      pregnancy_system: 'Pregnancy',
      congenital_system: 'Congenital',
      symptoms_system: 'Symptoms',
      external_causes_system: 'External Causes',
    };

    for (const sysKey of Object.keys(this.systems)) {
      const tab = document.createElement('button');
      tab.className = 'icd10-tab';
      tab.textContent = systemLabels[sysKey] || this.systems[sysKey].description || sysKey.replace(/_/g, ' ');
      tab.dataset.system = sysKey;
      tab.addEventListener('click', () => this.showSystem(sysKey));
      this.tabsEl.appendChild(tab);
    }
  }

  showSystem(sysKey) {
    this.activeSystem = sysKey;

    // Update active tab
    if (this.tabsEl) {
      this.tabsEl.querySelectorAll('.icd10-tab').forEach(t => {
        t.classList.toggle('active', t.dataset.system === sysKey);
      });
    }

    const sysData = this.systems[sysKey];
    if (!sysData) return;

    const codes = sysData.codes || [];
    this._renderCodes(codes, sysKey);
  }

  /* ── Search ─────────────────────────────────────────────── */
  _bindSearch() {
    if (!this.searchInput) return;

    let timer = null;
    this.searchInput.addEventListener('input', () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const q = this.searchInput.value.trim().toLowerCase();
        if (q.length < 2) {
          // Show active system
          if (this.activeSystem) this.showSystem(this.activeSystem);
          return;
        }
        this._searchAndRender(q);
      }, 150);
    });
  }

  _searchAndRender(query) {
    const tokens = query.split(/\s+/);
    const results = this.allCodes.filter(item => {
      for (const tok of tokens) {
        if (!item._search.includes(tok)) return false;
      }
      return true;
    }).slice(0, 50);

    this._renderCodes(results, null);
  }

  search(query) {
    const q = (query || '').trim().toLowerCase();
    if (!q) return [];
    const tokens = q.split(/\s+/);
    return this.allCodes.filter(item => {
      for (const tok of tokens) {
        if (!item._search.includes(tok)) return false;
      }
      return true;
    });
  }

  /* ── Render codes ───────────────────────────────────────── */
  _renderCodes(codes, sysKey) {
    if (!this.resultsEl) return;

    if (codes.length === 0) {
      this.resultsEl.innerHTML = '<div class="search-empty">No ICD-10 codes found</div>';
      return;
    }

    let html = '';
    for (const item of codes) {
      const relatedCPT = this._getRelatedCPT(item.code);
      html += `
        <div class="icd10-code-row" data-icd="${item.code}">
          <span class="icd10-code-row__code">${item.code}</span>
          <span class="icd10-code-row__desc">${item.description || ''}</span>
          ${relatedCPT.length > 0
            ? `<span class="icd10-code-row__cpt-link" title="Related CPT: ${relatedCPT.join(', ')}">→ CPT</span>`
            : ''}
        </div>
      `;
    }

    this.resultsEl.innerHTML = html;

    // Click handler for related CPT
    this.resultsEl.querySelectorAll('.icd10-code-row').forEach(row => {
      row.addEventListener('click', () => {
        const icdCode = row.dataset.icd;
        const related = this._getRelatedCPT(icdCode);
        if (related.length > 0 && this.searchEngine) {
          // Show related CPT codes in a tooltip-like popup
          this._showRelatedPopup(row, related);
        }
      });
    });
  }

  _showRelatedPopup(anchorEl, cptCodes) {
    // Remove existing popup
    const existing = document.querySelector('.icd10-related-popup');
    if (existing) existing.remove();

    const popup = document.createElement('div');
    popup.className = 'icd10-related-popup';
    popup.style.cssText = `
      position: absolute;
      background: var(--bg-elevated);
      border: 1px solid var(--border-accent);
      border-radius: var(--radius-md);
      padding: 12px;
      box-shadow: var(--shadow-lg);
      z-index: 50;
      min-width: 240px;
      max-width: 360px;
    `;

    let html = '<div style="font-size:0.6875rem;font-weight:700;color:var(--accent);margin-bottom:8px;text-transform:uppercase;letter-spacing:0.06em">Related CPT Codes</div>';

    for (const code of cptCodes.slice(0, 8)) {
      const cptData = this.searchEngine ? this.searchEngine.getCPT(code) : null;
      if (cptData) {
        html += `
          <div class="search-result-card" data-cpt-add="${code}" style="padding:8px;margin-bottom:4px;border-radius:6px;cursor:pointer">
            <span class="search-result-card__code" style="font-size:0.8125rem">${code}</span>
            <span class="search-result-card__desc" style="font-size:0.75rem">${cptData.description.slice(0, 50)}...</span>
            <span class="search-result-card__wrvu" style="font-size:0.6875rem">${cptData.wRVU.toFixed(2)}</span>
          </div>
        `;
      } else {
        html += `<div style="font-size:0.8125rem;color:var(--text-secondary);padding:4px 0">${code}</div>`;
      }
    }

    popup.innerHTML = html;

    // Position relative to anchor
    anchorEl.style.position = 'relative';
    anchorEl.appendChild(popup);

    // Click to add to case builder
    popup.querySelectorAll('[data-cpt-add]').forEach(el => {
      el.addEventListener('click', (e) => {
        e.stopPropagation();
        const code = el.dataset.cptAdd;
        const cptData = this.searchEngine ? this.searchEngine.getCPT(code) : null;
        if (cptData && this.caseBuilder) {
          this.caseBuilder.addProcedure(cptData);
        }
        popup.remove();
      });
    });

    // Auto-dismiss
    setTimeout(() => {
      document.addEventListener('click', function dismiss(e) {
        if (!popup.contains(e.target)) {
          popup.remove();
          document.removeEventListener('click', dismiss);
        }
      });
    }, 100);
  }

  /* ── Related CPT map (common ICD→CPT associations) ────── */
  _buildRelatedMap() {
    return {
      // Appendicitis
      'K35': ['44950','44960','44970'],
      'K35.0': ['44960','44970'],
      'K35.1': ['44960','44970'],
      'K35.2': ['44960','44970'],
      'K35.3': ['44950','44970'],
      'K35.9': ['44950','44970'],
      'K36': ['44950','44970'],
      'K37': ['44950','44970'],

      // Gallbladder
      'K80.20': ['47562','47563','47600','47605'],
      'K80.30': ['47562','47563'],
      'K80.70': ['47562','47563'],
      'K81.0': ['47562','47563','47600','47605'],
      'K81.1': ['47562','47563'],

      // Hernias
      'K40.90': ['49505','49650'],
      'K40.91': ['49520','49651'],
      'K42.9': ['49585','49587'],
      'K43.9': ['49560','49652'],
      'K44.9': ['43280','43281'],

      // Thyroid
      'E04.1': ['60220','60225'],
      'E04.2': ['60240','60252'],
      'E05.90': ['60240','60252'],
      'C73': ['60240','60252','60254'],

      // Breast
      'C50': ['19301','19302','19303'],
      'D05': ['19301','19120'],
      'N60': ['19100','19120'],

      // GI hemorrhage
      'K92.2': ['43235','43239','45378','45380'],

      // Bowel obstruction
      'K56.50': ['44120','44125','44140','44202'],
      'K56.60': ['44120','44125','44140','44202'],

      // Diverticulitis
      'K57.32': ['44140','44141','44143','44204'],
      'K57.92': ['44140','44141','44204'],

      // Trauma
      'S36.03': ['38100','38101','38115'],
      'S36.11': ['47350','47360','47361'],
    };
  }

  _getRelatedCPT(icdCode) {
    // Try exact match, then prefix matches
    if (this._icdCptMap[icdCode]) return this._icdCptMap[icdCode];

    // Try without trailing character
    const prefix = icdCode.replace(/[.]/g, '').slice(0, 3);
    for (const [key, val] of Object.entries(this._icdCptMap)) {
      if (key.replace(/[.]/g, '').startsWith(prefix)) return val;
    }

    return [];
  }

  /* ── Toggle visibility ──────────────────────────────────── */
  show() {
    if (this.sectionEl) this.sectionEl.classList.add('visible');
  }

  hide() {
    if (this.sectionEl) this.sectionEl.classList.remove('visible');
  }

  toggle() {
    if (this.sectionEl) this.sectionEl.classList.toggle('visible');
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = ICD10Engine;
}
