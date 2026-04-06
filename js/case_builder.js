/**
 * CaseBuilder for FreeCPTCodeFinder
 * v2.0 — Supports bilateral procedures, laterality, and duplicate CPT instances
 */

class CaseBuilder {
  constructor() {
    this.procedures = [];
    this.modifierEngine = null;
    this.auditPanel = null;
    this.searchEngine = null;
    this.nextId = 1;
    this.bodyEl = null;
    this.footerEl = null;
    this.lastAnalysis = null;
  }

  initialize(bodyEl, footerEl) {
    this.bodyEl = bodyEl;
    this.footerEl = footerEl;
    this.render();
    console.log('[CaseBuilder] v2.1 Ready — Bilateral + Duplicate Logic');
  }

  _getProcedureMetadata(code) {
    if (!this.modifierEngine || !this.modifierEngine.modifierRules) {
      return { bilateral_eligible: false, laterality_applicable: false, bilateral_method: null };
    }
    return this.modifierEngine.modifierRules[code] || {};
  }

  /**
   * Duplicate detection: allows duplicates when clinically appropriate
   * - Different laterality (L vs R) = allowed
   * - Bilateral on one, none on other = needs resolution
   * - Same laterality = prompt user for reason (-76/-77/-59)
   */
  _checkDuplicateAllowed(newProc) {
    const existingWithSameCode = this.procedures.filter(p => p.code === newProc.code);
    if (existingWithSameCode.length === 0) return { allowed: true };
    
    // Check if existing has bilateral — block duplicate (should use qty or bilateral flag)
    const existingBilateral = existingWithSameCode.find(p => p.laterality === 'bilateral');
    if (existingBilateral) {
      return { 
        allowed: false, 
        reason: 'bilateral_exists',
        message: `${newProc.code} already exists as bilateral. Remove bilateral modifier first to add separate entries.`
      };
    }
    
    // If new is bilateral but existing entries exist, convert to bilateral
    if (newProc.laterality === 'bilateral' && existingWithSameCode.length > 0) {
      return {
        allowed: true,
        convertToBilateral: true,
        existingIds: existingWithSameCode.map(p => p.id)
      };
    }
    
    // Different laterality = allowed (L + R = separate anatomic sites)
    const newLat = newProc.laterality || 'none';
    const existingLateralities = existingWithSameCode.map(p => p.laterality || 'none');
    
    if (newLat !== 'none' && !existingLateralities.includes(newLat)) {
      return { allowed: true, reason: 'different_laterality' };
    }
    
    // Same code, same/no laterality = allow but flag for modifier selection
    return { 
      allowed: true, 
      needsModifier: true,
      reason: 'duplicate_same_laterality',
      message: `Duplicate ${newProc.code} added. Select modifier: -76 (repeat same MD), -77 (repeat different MD), or -59 (distinct service).`
    };
  }

  addProcedure(item, options = {}) {
    const meta = this._getProcedureMetadata(item.code);
    
    const proc = {
      id: this.nextId++,
      code: item.code,
      description: item.description || '',
      work_rvu: item.wRVU || item.work_rvu || 0,
      pe_rvu: item.peRVU || item.pe_rvu || 0,
      mp_rvu: item.mpRVU || item.mp_rvu || 0,
      total_rvu: item.totalRVU || item.total_rvu || 0,
      globalPeriod: item.globalPeriod || item.global_period || 0,
      specialty: item.specialty || item.category || '',
      laterality: options.laterality || 'none',
      bilateral: options.bilateral || false,
      bilateral_eligible: meta.bilateral_eligible || false,
      laterality_applicable: meta.laterality_applicable || false,
      bilateral_method: meta.bilateral_method || null,
      duplicateModifier: options.duplicateModifier || null,
    };

    // Check duplicate rules
    const dupCheck = this._checkDuplicateAllowed(proc);
    
    if (!dupCheck.allowed) {
      console.warn(`[CaseBuilder] Duplicate blocked: ${dupCheck.message}`);
      return false;
    }
    
    if (dupCheck.convertToBilateral && dupCheck.existingIds) {
      dupCheck.existingIds.forEach(id => {
        this.procedures = this.procedures.filter(p => p.id !== id);
      });
      proc.laterality = 'bilateral';
      proc.bilateral = true;
    }
    
    if (dupCheck.needsModifier) {
      proc._needsDuplicateModifier = true;
    }

    this.procedures.push(proc);
    this._analyzeAndRender();
    return true;
  }

  removeProcedure(id) {
    this.procedures = this.procedures.filter(p => p.id !== id);
    this._analyzeAndRender();
  }

  setLaterality(id, laterality) {
    const proc = this.procedures.find(p => p.id === id);
    if (!proc) return;
    proc.laterality = laterality;
    proc.bilateral = (laterality === 'bilateral');
    this._analyzeAndRender();
  }

  clearAll() {
    this.procedures = [];
    this.lastAnalysis = null;
    this.render();
    if (this.auditPanel) this.auditPanel.clear();
  }

  _buildContext() {
    const context = { bilateral: {}, laterality: {} };
    for (const proc of this.procedures) {
      if (proc.bilateral) {
        context.bilateral[proc.code] = true;
      }
      if (proc.laterality && proc.laterality !== 'none') {
        context.laterality[proc.code] = proc.laterality;
      }
    }
    return context;
  }

  _analyzeAndRender() {
    if (this.modifierEngine && this.procedures.length > 0) {
      try {
        const context = this._buildContext();
        this.lastAnalysis = this.modifierEngine.analyze(this.procedures, context);
      } catch (err) {
        console.error('[CaseBuilder] ModifierEngine error:', err);
        this.lastAnalysis = null;
      }
    } else {
      this.lastAnalysis = null;
    }
    this.render();
    if (this.auditPanel && this.lastAnalysis) {
      this.auditPanel.update(this.lastAnalysis);
    } else if (this.auditPanel) {
      this.auditPanel.clear();
    }
  }

  render() {
    if (!this.bodyEl) return;

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

    const analysis = this.lastAnalysis;
    const procMap = {};
    if (analysis && analysis.procedures) {
      for (const p of analysis.procedures) {
        procMap[p.id] = p;
      }
    }

    let html = '';
    for (const proc of this.procedures) {
      const ap = procMap[proc.id];
      const role = this._getRole(ap);
      const isSuppressed = ap && (ap.suppressedBy || ap.rank === 'bundled' || ap.rank === 'suppressed' || ap.rank === 'included');

      let lateralityBadge = '';
      if (proc.laterality === 'bilateral') {
        lateralityBadge = '<span class="laterality-badge bilateral">BILATERAL</span>';
      } else if (proc.laterality === 'left') {
        lateralityBadge = '<span class="laterality-badge left">LEFT</span>';
      } else if (proc.laterality === 'right') {
        lateralityBadge = '<span class="laterality-badge right">RIGHT</span>';
      }

      let lateralityControls = '';
      if (proc.bilateral_eligible && !isSuppressed) {
        const isNone = proc.laterality === 'none';
        const isLeft = proc.laterality === 'left';
        const isRight = proc.laterality === 'right';
        const isBilateral = proc.laterality === 'bilateral';
        
        lateralityControls = `
          <div class="laterality-controls" data-proc-id="${proc.id}">
            <button class="lat-btn ${isNone ? 'active' : ''}" data-lat="none" title="Unilateral">—</button>
            <button class="lat-btn ${isLeft ? 'active' : ''}" data-lat="left" title="Left">L</button>
            <button class="lat-btn ${isRight ? 'active' : ''}" data-lat="right" title="Right">R</button>
            <button class="lat-btn bilateral ${isBilateral ? 'active' : ''}" data-lat="bilateral" title="Bilateral -50">B</button>
          </div>
        `;
      }

      const baseWRVU = proc.work_rvu || 0;
      const adjustedWRVU = ap ? ap.adjustedWRVU : baseWRVU;

      html += `
        <div class="case-item ${role} ${isSuppressed ? 'suppressed' : ''}" data-id="${proc.id}">
          <div class="case-item__top">
            <span class="case-item__code">${proc.code}</span>
            ${lateralityBadge}
            <button class="case-item__remove" data-remove="${proc.id}" title="Remove">&times;</button>
          </div>
          <div class="case-item__desc">${this._truncate(proc.description, 80)}</div>
          ${lateralityControls}
          <div class="case-item__meta">
            ${this._renderModifiers(ap)}
            <span class="case-item__wrvu">${baseWRVU.toFixed(2)} → ${adjustedWRVU.toFixed(2)} wRVU</span>
            <span class="case-item__role ${this._roleClass(role)}">${role}</span>
          </div>
          ${ap && ap.explanations && ap.explanations.length ? `<div style="font-size:0.6875rem;color:var(--text-muted);margin-top:4px">${ap.explanations.slice(0,2).join(' | ')}</div>` : ''}
        </div>
      `;
    }

    this.bodyEl.innerHTML = html;

    this.bodyEl.querySelectorAll('[data-remove]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.removeProcedure(parseInt(btn.dataset.remove, 10));
      });
    });

    this.bodyEl.querySelectorAll('.laterality-controls').forEach(controls => {
      const procId = parseInt(controls.dataset.procId, 10);
      controls.querySelectorAll('.lat-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          e.stopPropagation();
          this.setLaterality(procId, btn.dataset.lat);
        });
      });
    });

    this._renderFooter(analysis);
  }

  _renderFooter(analysis) {
    if (!this.footerEl) return;

    if (!analysis || this.procedures.length === 0) {
      this.footerEl.innerHTML = `<div style="text-align:center;color:var(--text-muted);font-size:0.75rem">Add procedures to see analysis</div>`;
      return;
    }

    const conf = analysis.confidence || { score: 0 };
    const score = conf.score || 0;
    const blocked = analysis.blockingIssues && analysis.blockingIssues.length > 0;

    let totalWRVU = 0;
    let totalRVU = 0;
    for (const p of (analysis.procedures || [])) {
      if (p.rank !== 'suppressed' && p.rank !== 'bundled' && p.rank !== 'included') {
        totalWRVU += (p.adjustedWRVU || 0);
        totalRVU += (p.adjustedWRVU || 0) + (p.pe_rvu || 0) + (p.mp_rvu || 0);
      }
    }

    this.footerEl.innerHTML = `
      <div style="display:flex;align-items:center;justify-content:space-between">
        <span class="confidence-badge ${this._confClass(score)}">${this._confIcon(score)} ${score}%</span>
        <span style="font-size:0.6875rem;color:var(--text-muted)">${this.procedures.length} procedure${this.procedures.length > 1 ? 's' : ''}</span>
      </div>
      <div class="case-totals">
        <div class="case-total-item">
          <div class="case-total-item__label">Work RVU</div>
          <div class="case-total-item__value">${totalWRVU.toFixed(2)}</div>
        </div>
        <div class="case-total-item">
          <div class="case-total-item__label">Est. Payment</div>
          <div class="case-total-item__value big">$${(totalRVU * 33.89).toFixed(0)}</div>
        </div>
      </div>
      <div style="display:flex;gap:6px">
        <button class="btn btn--primary btn--sm" style="flex:1" id="caseExportBtn" ${blocked ? 'disabled' : ''}>${blocked ? '⚠ Issues' : '📋 Export'}</button>
        <button class="btn btn--danger btn--sm" id="caseClearBtn">Clear</button>
      </div>
    `;

    this.footerEl.querySelector('#caseExportBtn')?.addEventListener('click', () => this.exportCase());
    this.footerEl.querySelector('#caseClearBtn')?.addEventListener('click', () => this.clearAll());
  }

  exportCase() {
    if (!this.lastAnalysis) return;
    const lines = ['FreeCPTCodeFinder Case Summary', '═'.repeat(40), ''];
    for (const p of (this.lastAnalysis.procedures || [])) {
      const mods = (p.modifiers || []).join(' ');
      const lat = p.laterality && p.laterality !== 'none' ? ` [${p.laterality.toUpperCase()}]` : '';
      lines.push(`${p.code}${lat}  ${mods}  wRVU: ${(p.adjustedWRVU || 0).toFixed(2)}  ${p.rank || ''}`);
      if (p.explanations?.length) lines.push(`  → ${p.explanations[0]}`);
      lines.push('');
    }
    navigator.clipboard.writeText(lines.join('\n')).catch(console.error);
  }

  _getRole(ap) {
    if (!ap) return 'primary';
    if (ap.rank === 'bundled' || ap.rank === 'suppressed' || ap.rank === 'included') return 'suppressed';
    if (ap.rank === 'primary') return 'primary';
    if (ap.rank === 'secondary' || ap.rank === 'additional') return 'secondary';
    if (ap.rank === 'addon') return 'addon';
    if (ap.rank === 'reconstructive') return 'reconstructive';
    return 'secondary';
  }

  _roleClass(role) { return `role-${role}`; }
  _renderModifiers(ap) {
    if (!ap || !ap.modifiers || !ap.modifiers.length) return '';
    return ap.modifiers.map(m => `<span class="case-item__modifier">${m}</span>`).join('');
  }
  _confClass(s) { return s >= 95 ? 'confidence-badge--high' : s >= 80 ? 'confidence-badge--medium' : 'confidence-badge--low'; }
  _confIcon(s) { return s >= 95 ? '✓' : s >= 80 ? '⚠' : '✗'; }
  _truncate(t, l) { return t && t.length > l ? t.slice(0, l) + '...' : (t || ''); }
}

if (typeof module !== 'undefined' && module.exports) module.exports = CaseBuilder;
