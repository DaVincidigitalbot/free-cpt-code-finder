/**
 * AuditPanel for FreeCPTCodeFinder
 * Renders structured audit trail from ModifierEngine analysis.
 * Shows Code | Modifier | Role | wRVU | Justification, confidence, blocking issues.
 */

class AuditPanel {
  constructor() {
    this.containerEl = null;
    this.lastAnalysis = null;
    this.isOpen = false;
  }

  /* ── Initialise ─────────────────────────────────────────── */
  initialize(containerEl) {
    this.containerEl = containerEl;
    this.render();
    console.log('[AuditPanel] Ready');
  }

  /* ── Update with new analysis ───────────────────────────── */
  update(analysis) {
    this.lastAnalysis = analysis;
    this.render();
  }

  clear() {
    this.lastAnalysis = null;
    this.render();
  }

  /* ── Render ─────────────────────────────────────────────── */
  render() {
    if (!this.containerEl) return;

    if (!this.lastAnalysis || !this.lastAnalysis.procedures || this.lastAnalysis.procedures.length === 0) {
      this.containerEl.innerHTML = `
        <div class="audit-section">
          <button class="audit-section__toggle">
            <span>📊 Audit Trail</span>
            <span style="font-size:0.75rem;color:var(--text-muted)">No data</span>
          </button>
        </div>
      `;
      return;
    }

    const a = this.lastAnalysis;
    const conf = a.confidence || { score: 0 };
    const score = conf.score || 0;
    const blocking = a.blockingIssues || [];
    const warnings = a.warnings || [];
    const procs = a.procedures || [];

    this.containerEl.innerHTML = `
      <div class="audit-section">
        <button class="audit-section__toggle" id="auditToggle">
          <span>📊 Audit Trail</span>
          <span style="font-size:0.75rem">${this.isOpen ? '▲' : '▼'}</span>
        </button>
        <div class="audit-section__content ${this.isOpen ? 'open' : ''}" id="auditContent">
          
          <!-- Procedures Table -->
          <table class="audit-table">
            <thead>
              <tr>
                <th>Code</th>
                <th>Mod</th>
                <th>Role</th>
                <th>wRVU</th>
                <th>Justification</th>
              </tr>
            </thead>
            <tbody>
              ${procs.map(p => this._renderProcRow(p)).join('')}
            </tbody>
          </table>

          <!-- Confidence -->
          <div class="audit-confidence">
            <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">
              <span style="font-size:0.6875rem;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;color:var(--text-muted)">Confidence</span>
              <span class="confidence-badge ${this._confClass(score)}" style="font-size:0.75rem;padding:3px 10px">
                ${score}%
              </span>
            </div>
            <div class="confidence-bar">
              <div class="confidence-bar__fill ${this._confBarClass(score)}" style="width:${score}%"></div>
            </div>
            ${conf.factors ? this._renderConfFactors(conf.factors) : ''}
          </div>

          <!-- Blocking Issues -->
          ${blocking.length > 0 ? `
            <div class="audit-blocking">
              <div class="audit-blocking__title">⚠ Blocking Issues (${blocking.length})</div>
              ${blocking.map(b => `
                <div class="audit-blocking__item">• ${b.message || b.description || b}</div>
              `).join('')}
            </div>
          ` : ''}

          <!-- Warnings -->
          ${warnings.length > 0 ? `
            <div style="margin-top:12px">
              <div style="font-size:0.6875rem;font-weight:600;color:var(--warning);margin-bottom:4px;text-transform:uppercase;letter-spacing:0.06em">
                Warnings (${warnings.length})
              </div>
              ${warnings.slice(0, 5).map(w => `
                <div style="font-size:0.75rem;color:var(--text-secondary);padding:2px 0">⚡ ${w.message || w}</div>
              `).join('')}
              ${warnings.length > 5 ? `<div style="font-size:0.6875rem;color:var(--text-muted)">...and ${warnings.length - 5} more</div>` : ''}
            </div>
          ` : ''}

          <!-- Copy Button -->
          <div style="margin-top:16px;text-align:center">
            <button class="btn btn--secondary btn--sm" id="auditCopyBtn">
              📋 Copy Audit to Clipboard
            </button>
          </div>
        </div>
      </div>
    `;

    // Bind toggle
    const toggle = this.containerEl.querySelector('#auditToggle');
    if (toggle) {
      toggle.addEventListener('click', () => {
        this.isOpen = !this.isOpen;
        const content = this.containerEl.querySelector('#auditContent');
        if (content) content.classList.toggle('open', this.isOpen);
        const arrow = toggle.querySelector('span:last-child');
        if (arrow) arrow.textContent = this.isOpen ? '▲' : '▼';
      });
    }

    // Bind copy
    const copyBtn = this.containerEl.querySelector('#auditCopyBtn');
    if (copyBtn) {
      copyBtn.addEventListener('click', () => this.copyAudit());
    }
  }

  _renderProcRow(proc) {
    const mods = (proc.modifiers || []).join(', ') || '—';
    const role = proc.rank || 'unknown';
    const wrvu = (proc.adjustedWRVU || proc.work_rvu || 0).toFixed(2);
    const justification = (proc.explanations && proc.explanations.length)
      ? proc.explanations[0]
      : '—';
    const isSuppressed = role === 'suppressed' || role === 'bundled';

    return `
      <tr style="${isSuppressed ? 'opacity:0.5;text-decoration:line-through' : ''}">
        <td>${proc.code}</td>
        <td style="font-family:var(--font-mono);font-size:0.6875rem">${mods}</td>
        <td>
          <span class="case-item__role ${this._roleClass(role)}" style="font-size:0.5625rem">${role}</span>
        </td>
        <td style="font-family:var(--font-mono);text-align:right">${wrvu}</td>
        <td style="font-size:0.6875rem;max-width:140px">${justification}</td>
      </tr>
    `;
  }

  _renderConfFactors(factors) {
    if (!factors || typeof factors !== 'object') return '';
    const entries = Object.entries(factors);
    if (entries.length === 0) return '';

    return `
      <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:4px">
        ${entries.map(([k, v]) => `
          <span style="font-size:0.625rem;padding:2px 6px;border-radius:100px;
            background:${v > 0 ? 'rgba(0,212,170,0.1)' : 'rgba(255,107,107,0.1)'};
            color:${v > 0 ? 'var(--success)' : 'var(--danger)'}">
            ${k}: ${v > 0 ? '+' : ''}${v}
          </span>
        `).join('')}
      </div>
    `;
  }

  /* ── Copy to Clipboard ──────────────────────────────────── */
  copyAudit() {
    if (!this.lastAnalysis) return;

    const a = this.lastAnalysis;
    const lines = [
      'AUDIT TRAIL — FreeCPTCodeFinder',
      '═'.repeat(50),
      '',
      'Code     | Mod      | Role       | wRVU   | Justification',
      '─'.repeat(50),
    ];

    for (const p of (a.procedures || [])) {
      const mods = (p.modifiers || []).join(',') || '—';
      const role = (p.rank || 'unknown').padEnd(10);
      const wrvu = (p.adjustedWRVU || 0).toFixed(2).padStart(6);
      const just = (p.explanations && p.explanations[0]) || '—';
      lines.push(`${p.code.padEnd(8)} | ${mods.padEnd(8)} | ${role} | ${wrvu} | ${just}`);
    }

    lines.push('');
    const conf = a.confidence || {};
    lines.push(`Confidence: ${conf.score || 0}%`);

    const blocking = a.blockingIssues || [];
    if (blocking.length > 0) {
      lines.push('', 'BLOCKING ISSUES:');
      for (const b of blocking) {
        lines.push(`  ⚠ ${b.message || b}`);
      }
    }

    const warnings = a.warnings || [];
    if (warnings.length > 0) {
      lines.push('', 'WARNINGS:');
      for (const w of warnings) {
        lines.push(`  ⚡ ${w.message || w}`);
      }
    }

    navigator.clipboard.writeText(lines.join('\n')).then(() => {
      const btn = this.containerEl.querySelector('#auditCopyBtn');
      if (btn) {
        btn.textContent = '✓ Copied!';
        setTimeout(() => btn.textContent = '📋 Copy Audit to Clipboard', 1500);
      }
    });
  }

  /* ── Helpers ────────────────────────────────────────────── */
  _confClass(score) {
    if (score >= 95) return 'confidence-badge--high';
    if (score >= 80) return 'confidence-badge--medium';
    return 'confidence-badge--low';
  }

  _confBarClass(score) {
    if (score >= 95) return 'confidence-bar__fill--high';
    if (score >= 80) return 'confidence-bar__fill--medium';
    return 'confidence-bar__fill--low';
  }

  _roleClass(role) {
    if (role === 'primary') return 'role-primary';
    if (role === 'secondary' || role === 'additional') return 'role-secondary';
    if (role === 'included') return 'role-included';
    if (role === 'suppressed' || role === 'bundled') return 'role-suppressed';
    return '';
  }
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = AuditPanel;
}
