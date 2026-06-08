(function () {
  const STORAGE_KEY = "fccf-productivity-view";
  const APP_TOOLTIP =
    "Estimated APP productivity values are educational estimates and may differ from actual employer compensation plans.";
  const APP_DISCLAIMER =
    "Estimated APP Productivity is not the same as compensation, reimbursement, or guaranteed employer wRVU credit. Actual attribution depends on payer rules, documentation, modifier acceptance, scope of practice, supervision requirements, and employer compensation policy.";
  const MODIFIER_TOOLTIPS = {
    AS: "Physician Assistant, Nurse Practitioner, or Clinical Nurse Specialist assistant at surgery.",
    "80": "Assistant surgeon.",
    "81": "Minimum assistant surgeon.",
    "82": "Assistant surgeon when qualified resident unavailable.",
    "Split/Shared Visit":
      "Productivity attribution depends on payer requirements, documentation, and employer policy.",
  };

  function getMode() {
    try {
      return localStorage.getItem(STORAGE_KEY) === "app" ? "app" : "physician";
    } catch (err) {
      return "physician";
    }
  }

  function setMode(mode) {
    const next = mode === "app" ? "app" : "physician";
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch (err) {}
    applyMode(next);
  }

  function isEMCode(code) {
    const n = Number(code);
    return (
      (n >= 99202 && n <= 99205) ||
      (n >= 99211 && n <= 99215) ||
      (n >= 99221 && n <= 99223) ||
      (n >= 99231 && n <= 99233) ||
      (n >= 99242 && n <= 99245) ||
      (n >= 99252 && n <= 99255) ||
      n === 99238 ||
      n === 99239 ||
      n === 99291 ||
      n === 99292
    );
  }

  function estimateFor(code, wrvu) {
    const n = Number(wrvu) || 0;
    const factor = isEMCode(code) ? 0.85 : 0.136;
    return {
      value: Number((n * factor).toFixed(2)),
      factor,
      label: factor === 0.85 ? "85% Medicare NPP equivalent" : "13.6% assistant-at-surgery equivalent",
    };
  }

  function parseCodeFromPage() {
    const h1 = document.querySelector("h1");
    const match = h1 && h1.textContent.match(/CPT\s*(\d{5})/i);
    return match ? match[1] : "";
  }

  function enhanceRvuPanels() {
    document.querySelectorAll(".rvu-panel").forEach((panel) => {
      if (panel.dataset.appModeEnhanced === "1") return;
      const primary = panel.querySelector(".rvu-value-primary");
      if (!primary) return;
      const wrvu = Number(primary.textContent.trim());
      if (!Number.isFinite(wrvu)) return;
      const code = parseCodeFromPage();
      const estimate = estimateFor(code, wrvu);
      const row = document.createElement("div");
      row.className = "app-productivity-panel";
      row.dataset.appProductivityPanel = "true";
      row.innerHTML =
        '<div><div class="app-productivity-label">Physician wRVU</div><div class="app-productivity-value">' +
        wrvu.toFixed(2) +
        '</div></div><div><div class="app-productivity-label">Estimated APP Productivity <span class="app-tip" title="' +
        APP_TOOLTIP +
        '">?</span></div><div class="app-productivity-value app-productivity-value--accent">' +
        estimate.value.toFixed(2) +
        '</div><div class="app-productivity-note">' +
        estimate.label +
        '</div><div class="app-productivity-note app-productivity-disclaimer">' +
        APP_DISCLAIMER +
        "</div></div>";
      panel.appendChild(row);
      panel.dataset.appModeEnhanced = "1";
    });
  }

  function enhanceTooltips() {
    if (document.querySelector("[data-app-tooltip-library]")) return;
    const target = document.querySelector(".site-content-wrap .container, main .wrap, main .container");
    if (!target) return;
    const section = document.createElement("section");
    section.className = "site-card app-tooltip-library";
    section.dataset.appTooltipLibrary = "true";
    section.innerHTML =
      '<h2>APP Modifier Notes</h2><div class="app-tooltip-grid">' +
      Object.entries(MODIFIER_TOOLTIPS)
        .map(
          ([label, text]) =>
            '<div><strong>' + label + '</strong><p>' + text + "</p></div>",
        )
        .join("") +
      "</div><p>" +
      APP_DISCLAIMER +
      "</p><p>Educational estimate only. This is not legal advice, billing advice, or compensation guidance.</p>";
    target.appendChild(section);
  }

  function syncToggles(mode) {
    document.querySelectorAll("[data-app-mode-toggle]").forEach((toggle) => {
      toggle.querySelectorAll("[data-app-mode-choice]").forEach((btn) => {
        const active = btn.dataset.appModeChoice === mode;
        btn.classList.toggle("active", active);
        btn.setAttribute("aria-pressed", String(active));
      });
    });
  }

  function applyMode(mode) {
    const next = mode || getMode();
    document.documentElement.dataset.productivityView = next;
    enhanceRvuPanels();
    if (next === "app") enhanceTooltips();
    syncToggles(next);
    window.dispatchEvent(new CustomEvent("fccf:app-mode-change", { detail: { mode: next } }));
  }

  function bindToggles() {
    document.querySelectorAll("[data-app-mode-toggle]").forEach((toggle) => {
      if (toggle.dataset.appModeBound === "1") return;
      toggle.dataset.appModeBound = "1";
      toggle.addEventListener("click", (event) => {
        const btn = event.target.closest("[data-app-mode-choice]");
        if (!btn) return;
        setMode(btn.dataset.appModeChoice);
      });
    });
  }

  window.FreeCPTAppMode = {
    getMode,
    setMode,
    isAppMode: () => getMode() === "app",
    estimateFor,
    tooltip: APP_TOOLTIP,
  };

  function init() {
    bindToggles();
    applyMode(getMode());
    setTimeout(() => {
      bindToggles();
      applyMode(getMode());
    }, 0);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
