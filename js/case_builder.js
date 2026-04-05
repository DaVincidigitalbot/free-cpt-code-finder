/**
 * CaseBuilder for FreeCPTCodeFinder
 * Manages a list of selected procedures, integrates with ModifierEngine,
 * renders real-time analysis with confidence scoring, modifier assignments,
 * and export functionality.
 */

class CaseBuilder {
  constructor() {
    this.procedures = [];         // array of procedure objects
    this.modifierEngine = null;   // ref to ModifierEngine
    this.auditPanel = null;       // ref to AuditPanel
    this.searchEngine = null;     // ref to UnifiedSearchEngine

    // DOM refs
    this.bodyEl = null;
    this.footerEl = null;
    this.badgeEl = null;
    this.exportBtn = null;
    this.clearBtn = null;

    this.lastAnalysis = null;
  }

  /* ── Initialise ─────────────────────────────────────────── */
  initialize(bodyEl, footerEl) {
    this.bodyEl = bodyEl;
    this.footerEl = footerEl;
    this.render();
    console.log('[CaseBuilder] Ready');
  }

  /* ── Add / Remove ───────────────────────────────────────── */
  addProcedure(item) {
    // Prevent duplicates
    if (this.procedures.some(p => p.code === item.code)) {
      this._flash(item.code);
      return;
    }

    this.procedures.push({
      code: item.code,
      description: item.description || '',
      work_rvu: item.wRVU || item.work_rvu || 0,
      pe_rvu: item.peRVU || item.pe_rvu || 0,
      mp_rvu: item.mpRVU || item.mp_rvu || 0,
      total_rvu: item.totalRVU || item.total_rvu || 0,
      globalPeriod: item.globalPeriod || item.global_period || 0,
      specialty: item.specialty || item.category || '',
    });

    this._analyzeAndRender();
  }

  removeProcedure(code) {
    this.procedures = this.procedures.filter(p => p.code !== code);
    this._analyzeAndRender();
  }

  clearAll() {
    this.procedures = [];
    this.lastAnalysis = null;
    this.render();
    if (this.auditPanel) this.auditPanel.clear();
  }

  /* ── Analysis ───────────────────────────────────────────── */
  _analyzeAndRender() {
    if (this.modifierEngine && this.procedures.length > 0) {
      try {
        this.lastAnalysis = this.modifierEngine.analyze(this.procedures, {});
      } catch (err) {
        console.error('[CaseBuilder] ModifierEngine error:', err);
        this.lastAnalysis = null;
      }
    } else {
      this.lastAnalysis = null;
    }

    this.render();

    // Update audit panel
    if (this.auditPanel && this.lastAnalysis) {
      this.auditPanel.update(this.lastAnalysis);
    } else if (this.auditPanel) {
      this.auditPanel.clear();
    }
  }

  /* ── Render ─────────────────────────────────────────────── */
  render() {
    if (!this.bodyEl) return;

    // Empty state
    if (this.procedures.length === 0) {
      this.bodyEl.innerHTML = `
        <div class="case-empty">
          <div class="case-empty__icon">📋</div>
          <div>No procedures added yet</div>
          <div style="font-size:0.75rem;margin-top:8px;color:var(--text-muted)">
            Search or browse specialties to add CPT codes
          </div>
        </div>
      `;
      this._renderFooter(null);
      return;
    }

    // Build procedure list
    const analysis = this.lastAnalysis;
    const procMap = {};
    if (analysis && analysis.procedures) {
      for (const p of analysis.procedures) {
        procMap[p.code] = p;
      }
    }

    let html = '';
    for (const proc of this.procedures) {
      const ap = procMap[proc.code]; // analysed procedure
      const role = this._getRole(ap);
      const isSuppressed = ap && (ap.suppressedBy || ap.rank === 'bundled' || ap.rank === 'suppressed');

      html += `
        <div class="case-item ${role} ${isSuppressed ? 'suppressed' : ''}" data-code="${proc.code}">
          <div class="case-item__top">
            <span class="case-item__code">${proc.code}</span>
            <button class="case-item__remove" data-remove="${proc.code}" title="Remove">&times;</button>
          </div>
          <div class="case-item__desc">${this._truncate(proc.description, 80)}</div>
          <div class="case-item__meta">
            ${this._renderModifiers(ap)}
            <span class="case-item__wrvu">${(ap ? ap.adjustedWRVU : proc.work_rvu).toFixed(2)} wRVU</span>
            <span class="case-item__role ${this._roleClass(role)}">${role}</span>
          </div>
          ${isSuppressed && ap.suppressedBy ? `<div style="font-size:0.6875rem;color:var(--danger);margin-top:4px">Bundled with ${ap.suppressedBy}</div>` : ''}
          ${ap && ap.explanations && ap.explanations.length ? `<div style="font-size:0.6875rem;color:var(--text-muted);margin-top:4px">${ap.explanations[0]}</div>` : ''}
        </div>
      `;
    }

    this.bodyEl.innerHTML = html;

    // Attach remove handlers
    this.bodyEl.querySelectorAll('[data-remove]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.removeProcedure(btn.dataset.remove);
      });
    });

    this._renderFooter(analysis);
  }

  _renderFooter(analysis) {
    if (!this.footerEl) return;

    if (!analysis || this.procedures.length === 0) {
      this.footerEl.innerHTML = `
        <div style="text-align:center;color:var(--text-muted);font-size:0.75rem">
          Add procedures to see analysis
        </div>
      `;
      return;
    }

    const conf = analysis.confidence || { score: 0 };
    const score = conf.score || 0;
    const blocked = analysis.blockingIssues && analysis.blockingIssues.length > 0;
    const exportEligible = analysis.exportEligible !== false && !blocked;

    // Calculate totals
    let totalWRVU = 0;
    let totalRVU = 0;
    const procs = analysis.procedures || [];
    for (const p of procs) {
      if (p.rank !== 'suppressed' && p.rank !== 'bundled') {
        totalWRVU += (p.adjustedWRVU || 0);
        totalRVU += (p.adjustedWRVU || 0) + (p.pe_rvu || 0) + (p.mp_rvu || 0);
      }
    }

    const estimated = totalRVU * 33.89; // 2026 CF

    this.footerEl.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between">
        <span class="confidence-badge ${this._confClass(score)}">
          ${this._confIcon(score)} ${score}%
        </span>
        <span style="font-size:0.6875rem;color:var(--text-muted)">${this.procedures.length} procedure${this.procedures.length > 1 ? 's' : ''}</span>
      </div>
      <div class="case-totals">
        <div class="case-total-item">
          <div class="case-total-item__label">Work RVU</div>
          <div class="case-total-item__value">${totalWRVU.toFixed(2)}</div>
        </div>
        <div class="case-total-item">
          <div class="case-total-item__label">Est. Payment</div>
          <div class="case-total-item__value big">$${estimated.toFixed(0)}</div>
        </div>
      </div>
      <div style="display:flex;gap:6px">
        <button class="btn btn--primary btn--sm" style="flex:1" id="caseExportBtn" ${!exportEligible ? 'disabled' : ''}>
          ${blocked ? '⚠ Blocked' : '📋 Export / Copy'}
        </button>
        <button class="btn btn--danger btn--sm" id="caseClearBtn">Clear</button>
      </div>
    `;

    // Bind buttons
    const exportBtn = this.footerEl.querySelector('#caseExportBtn');
    const clearBtn = this.footerEl.querySelector('#caseClearBtn');

    if (exportBtn) {
      exportBtn.addEventListener('click', () => this.exportCase());
    }
    if (clearBtn) {
      clearBtn.addEventListener('click', () => this.clearAll());
    }
  }

  /* ── Export ──────────────────────────────────────────────── */
  exportCase() {
    if (!this.lastAnalysis) return;

    const lines = ['FreeCPTCodeFinder — Case Summary', '═'.repeat(40), ''];
    const procs = this.lastAnalysis.procedures || [];

    for (const p of procs) {
      const mods = (p.modifiers || []).map(m => `-${m}`).join(' ');
      const status = p.rank === 'suppressed' || p.rank === 'bundled' ? ' [SUPPRESSED]' : '';
      lines.push(`${p.code}  ${mods}  wRVU: ${(p.adjustedWRVU || 0).toFixed(2)}  ${p.rank || ''}${status}`);
      if (p.description) lines.push(`  ${p.description}`);
      if (p.explanations && p.explanations.length) {
        for (const e of p.explanations) lines.push(`  → ${e}`);
      }
      lines.push('');
    }

    const conf = this.lastAnalysis.confidence || {};
    lines.push(`Confidence: ${conf.score || 0}%`);

    if (this.lastAnalysis.blockingIssues && this.lastAnalysis.blockingIssues.length) {
      lines.push('', 'BLOCKING ISSUES:');
      for (const b of this.lastAnalysis.blockingIssues) {
        lines.push(`  ⚠ ${b.message || b}`);
      }
    }

    navigator.clipboard.writeText(lines.join('\n')).then(() => {
      const btn = this.footerEl.querySelector('#caseExportBtn');
      if (btn) {
        const orig = btn.textContent;
        btn.textContent = '✓ Copied!';
        setTimeout(() => btn.textContent = orig, 1500);
      }
    }).catch(err => {
      console.error('Copy failed:', err);
    });
  }

  /* ── Helpers ────────────────────────────────────────────── */
  _getRole(analysedProc) {
    if (!analysedProc) return 'primary';
    if (analysedProc.suppressedBy || analysedProc.rank === 'bundled' || analysedProc.rank === 'suppressed') return 'suppressed';
    if (analysedProc.rank === 'primary') return 'primary';
    if (analysedProc.rank === 'secondary' || analysedProc.rank === 'additional') return 'secondary';
    if (analysedProc.rank === 'included') return 'included';
    return 'secondary';
  }

  _roleClass(role) {
    return `role-${role}`;
  }

  _renderModifiers(ap) {
    if (!ap || !ap.modifiers || ap.modifiers.length === 0) return '';
    return ap.modifiers.map(m => `<span class="case-item__modifier">-${m}</span>`).join('');
  }

  _confClass(score) {
    if (score >= 95) return 'confidence-badge--high';
    if (score >= 80) return 'confidence-badge--medium';
    return 'confidence-badge--low';
  }

  _confIcon(score) {
    if (score >= 95) return '✓';
    if (score >= 80) return '⚠';
    return '✗';
  }

  _truncate(text, len) {
    if (!text) return '';
    return text.length > len ? text.slice(0, len) + '...' : text;
  }

  _flash(code) {
    const el = this.bodyEl?.querySelector(`[data-code="${code}"]`);
    if (el) {
      el.style.outline = '2px solid var(--warning)';
      setTimeout(() => el.style.outline = '', 600);
    }
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = CaseBuilder;
}
