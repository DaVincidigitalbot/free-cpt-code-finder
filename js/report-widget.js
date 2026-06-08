(function () {
  const BACKEND_URL = "https://free-cpt-code-finder.onrender.com";
  const STYLE_ID = "fccf-report-widget-style";
  const WIDGET_ID = "fccf-report-widget";

  if (window.__fccfReportWidgetLoaded) return;
  window.__fccfReportWidgetLoaded = true;

  const issueTypes = [
    ["wrvu_error", "Wrong wRVU"],
    ["cpt_error", "Incorrect CPT Description"],
    ["modifier_bug", "Modifier Issue"],
    ["search_problem", "Search Result Issue"],
    ["missing_cpt_code", "Missing CPT Code"],
    ["case_builder_issue", "Case Builder Issue"],
    ["category_placement", "Category Placement"],
  ];

  const specialties = [
    "General Surgery",
    "Trauma Surgery",
    "Surgical Critical Care",
    "Acute Care Surgery",
    "Colon & Rectal Surgery",
    "Vascular Surgery",
    "Orthopedic Surgery",
    "Hand Surgery",
    "Plastic Surgery",
    "Neurosurgery",
    "Cardiothoracic Surgery",
    "Cardiac Electrophysiology",
    "Urology",
    "ENT",
    "Gynecology",
    "Ophthalmology",
    "Interventional Radiology",
    "Gastroenterology",
    "Other",
  ];

  function injectStyles() {
    if (document.getElementById(STYLE_ID)) return;
    const style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent = [
      ".fccf-report-launch{position:fixed;right:22px;bottom:22px;z-index:9998;display:inline-flex;align-items:center;gap:8px;border:0;border-radius:999px;background:#23577b;color:#fff;padding:12px 15px;font:700 14px/1.1 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif;box-shadow:0 16px 34px rgba(15,23,32,.22)}",
      ".fccf-report-launch:hover{background:#1b4765}",
      ".fccf-report-backdrop{position:fixed;inset:0;z-index:9998;background:rgba(15,23,32,.28);display:none}",
      ".fccf-report-backdrop.open{display:block}",
      ".fccf-report-panel{position:fixed;right:22px;bottom:78px;width:390px;max-width:calc(100vw - 24px);max-height:calc(100vh - 104px);z-index:9999;display:none;flex-direction:column;background:#fff;color:#0f1720;border:1px solid #d5dae1;border-radius:10px;box-shadow:0 24px 70px rgba(15,23,32,.28);overflow:hidden;font:14px/1.45 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif}",
      ".fccf-report-panel.open{display:flex}",
      ".fccf-report-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;padding:15px 16px;border-bottom:1px solid #e5e7eb;background:#f7f7f3}",
      ".fccf-report-title{font-size:15px;font-weight:800;margin:0;color:#0f1720}",
      ".fccf-report-sub{font-size:12px;color:#4a5563;margin-top:2px}",
      ".fccf-report-close{border:1px solid #d5dae1;background:#fff;color:#0f1720;border-radius:8px;width:32px;height:32px;font-size:18px;line-height:1}",
      ".fccf-report-body{padding:14px 16px;overflow:auto}",
      ".fccf-report-warning{border:1px solid #fed7aa;background:#fff7ed;color:#9a3412;border-radius:8px;padding:10px 11px;font-size:12px;margin-bottom:12px}",
      ".fccf-report-label{display:block;font-size:12px;font-weight:800;color:#0f1720;margin:12px 0 6px}",
      ".fccf-report-select,.fccf-report-input,.fccf-report-textarea{width:100%;box-sizing:border-box;border:1px solid #cbd5e1;border-radius:8px;background:#fff;color:#0f1720;padding:9px 10px;font:inherit}",
      ".fccf-report-textarea{min-height:116px;resize:vertical}",
      ".fccf-report-missing-fields{display:none;border:1px solid #dbe4ee;background:#f8fafc;border-radius:8px;padding:10px 11px;margin-top:10px}",
      ".fccf-report-missing-fields.open{display:block}",
      ".fccf-report-help{font-size:12px;color:#64748b;margin-top:5px}",
      ".fccf-report-actions{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:13px}",
      ".fccf-report-status{font-size:12px;color:#4a5563;min-height:18px}",
      ".fccf-report-submit{border:0;border-radius:8px;background:#23577b;color:#fff;padding:10px 13px;font-weight:800}",
      ".fccf-report-submit:disabled{opacity:.62;cursor:wait}",
      ".fccf-report-success{color:#166534}",
      ".fccf-report-error{color:#991b1b}",
      "@media(max-width:700px){.fccf-report-launch{left:14px;right:14px;bottom:14px;justify-content:center}.fccf-report-panel{left:12px;right:12px;bottom:68px;width:auto;max-height:calc(100vh - 88px)}.fccf-report-backdrop.open{display:block}}",
    ].join("");
    document.head.appendChild(style);
  }

  function currentSearchQuery() {
    const q = document.getElementById("q") || document.querySelector('input[type="search"], input[name="q"]');
    const fromInput = q && q.value ? q.value.trim() : "";
    return fromInput || new URLSearchParams(location.search).get("q") || "";
  }

  function currentCptCodes() {
    const codes = new Set();
    const pathMatch = location.pathname.match(/\/(?:codes|cpt)\/(\d{5})\.html$/);
    if (pathMatch) codes.add(pathMatch[1]);
    document.querySelectorAll("[data-cpt], .cpt, .autocomplete-code, code").forEach((el) => {
      const text = String(el.dataset.cpt || el.textContent || "");
      const match = text.match(/\b\d{5}\b/g);
      if (match) match.slice(0, 8).forEach((code) => codes.add(code));
    });
    return Array.from(codes).slice(0, 20);
  }

  function activeCaseContext() {
    const rows = [];
    document.querySelectorAll(".lns .line, .case-line, [data-case-line]").forEach((el) => {
      const text = String(el.textContent || "").replace(/\s+/g, " ").trim();
      if (text) rows.push({ text });
    });
    return rows.slice(0, 20);
  }

  function pageContext(description) {
    return {
      pageUrl: location.href,
      pageTitle: document.title,
      searchQuery: currentSearchQuery(),
      cptCodes: currentCptCodes(),
      browser: navigator.userAgent,
      viewport: window.innerWidth + "x" + window.innerHeight,
      activeCase: activeCaseContext(),
      description,
    };
  }

  function optionHtml() {
    return issueTypes.map(([value, label]) => '<option value="' + value + '">' + label + "</option>").join("");
  }

  function specialtyHtml() {
    return '<option value="">Select specialty</option>' + specialties.map((label) => '<option value="' + label + '">' + label + "</option>").join("");
  }

  function renderWidget() {
    if (document.getElementById(WIDGET_ID)) return;
    injectStyles();
    const root = document.createElement("div");
    root.id = WIDGET_ID;
    root.innerHTML =
      '<button class="fccf-report-launch" type="button" aria-haspopup="dialog" aria-expanded="false">Report CPT/wRVU issue</button>' +
      '<div class="fccf-report-backdrop" aria-hidden="true"></div>' +
      '<section class="fccf-report-panel" role="dialog" aria-modal="true" aria-label="Report a CPT issue">' +
      '<div class="fccf-report-head"><div><h2 class="fccf-report-title">Report an issue</h2><div class="fccf-report-sub">CPT errors, wrong wRVUs, modifiers, search, or Case Builder bugs.</div></div><button class="fccf-report-close" type="button" aria-label="Close">x</button></div>' +
      '<form class="fccf-report-body"><div class="fccf-report-warning"><strong>Do not submit PHI.</strong> Use de-identified workflow details only.</div>' +
      '<label class="fccf-report-label" for="fccf-report-type">Issue type</label><select class="fccf-report-select" id="fccf-report-type" name="issueType">' + optionHtml() + '</select>' +
      '<div class="fccf-report-missing-fields" id="fccf-report-missing-fields">' +
      '<label class="fccf-report-label" for="fccf-report-procedure">Procedure Name <span aria-hidden="true">*</span></label><input class="fccf-report-input" id="fccf-report-procedure" name="procedureName" type="text" placeholder="Example: Hartmann Reversal">' +
      '<label class="fccf-report-label" for="fccf-report-specialty">Specialty <span aria-hidden="true">*</span></label><select class="fccf-report-select" id="fccf-report-specialty" name="specialty">' + specialtyHtml() + '</select>' +
      '<label class="fccf-report-label" for="fccf-report-cpt">CPT Code, optional</label><input class="fccf-report-input" id="fccf-report-cpt" name="suggestedCpt" type="text" inputmode="numeric" placeholder="Leave blank if unknown">' +
      '<label class="fccf-report-label" for="fccf-report-notes">Notes, optional</label><textarea class="fccf-report-textarea" id="fccf-report-notes" name="notes" placeholder="Example: Robotic colostomy reversal with colorectal anastomosis."></textarea>' +
      '<div class="fccf-report-help">This creates a structured Missing CPT Code report for database review.</div></div>' +
      '<div id="fccf-report-standard-fields"><label class="fccf-report-label" for="fccf-report-description">What is wrong?</label><textarea class="fccf-report-textarea" id="fccf-report-description" name="description" required placeholder="Example: CPT 22585 wRVU appears incorrect."></textarea></div>' +
      '<label class="fccf-report-label" for="fccf-report-email">Email, optional</label><input class="fccf-report-input" id="fccf-report-email" name="reporterEmail" type="email" autocomplete="email" placeholder="Only if you want follow-up">' +
      '<div class="fccf-report-actions"><div class="fccf-report-status" role="status" aria-live="polite"></div><button class="fccf-report-submit" type="submit">Submit report</button></div></form></section>';
    document.body.appendChild(root);

    const launch = root.querySelector(".fccf-report-launch");
    const backdrop = root.querySelector(".fccf-report-backdrop");
    const panel = root.querySelector(".fccf-report-panel");
    const close = root.querySelector(".fccf-report-close");
    const form = root.querySelector("form");
    const status = root.querySelector(".fccf-report-status");
    const submit = root.querySelector(".fccf-report-submit");
    const textarea = root.querySelector("textarea");
    const typeSelect = root.querySelector("#fccf-report-type");
    const standardFields = root.querySelector("#fccf-report-standard-fields");
    const missingFields = root.querySelector("#fccf-report-missing-fields");
    const procedureInput = root.querySelector("#fccf-report-procedure");
    const specialtySelect = root.querySelector("#fccf-report-specialty");
    const descriptionInput = root.querySelector("#fccf-report-description");

    function setOpen(open) {
      panel.classList.toggle("open", open);
      backdrop.classList.toggle("open", open);
      launch.setAttribute("aria-expanded", String(open));
      if (open) setTimeout(() => (typeSelect.value === "missing_cpt_code" ? procedureInput : descriptionInput).focus(), 30);
    }

    function syncIssueTypeFields() {
      const missing = typeSelect.value === "missing_cpt_code";
      missingFields.classList.toggle("open", missing);
      standardFields.style.display = missing ? "none" : "block";
      descriptionInput.required = !missing;
      procedureInput.required = missing;
      specialtySelect.required = missing;
    }

    launch.addEventListener("click", () => setOpen(true));
    close.addEventListener("click", () => setOpen(false));
    backdrop.addEventListener("click", () => setOpen(false));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && panel.classList.contains("open")) setOpen(false);
    });
    typeSelect.addEventListener("change", syncIssueTypeFields);
    syncIssueTypeFields();

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const data = new FormData(form);
      const issueType = String(data.get("issueType") || "");
      const description = String(data.get("description") || "").trim();
      const procedureName = String(data.get("procedureName") || "").trim();
      const specialty = String(data.get("specialty") || "").trim();
      const notes = String(data.get("notes") || "").trim();
      const suggestedCpt = String(data.get("suggestedCpt") || "").trim();
      if (issueType === "missing_cpt_code" && (!procedureName || !specialty)) {
        status.className = "fccf-report-status fccf-report-error";
        status.textContent = "Procedure name and specialty are required.";
        return;
      }
      if (issueType !== "missing_cpt_code" && !description) {
        status.className = "fccf-report-status fccf-report-error";
        status.textContent = "Describe the issue first.";
        return;
      }
      submit.disabled = true;
      status.className = "fccf-report-status";
      status.textContent = "Submitting...";
      try {
        const body = {
          issueType,
          description: issueType === "missing_cpt_code" ? [
            "Procedure Name: " + procedureName,
            "Specialty: " + specialty,
            suggestedCpt ? "Suggested CPT: " + suggestedCpt : "",
            notes ? "Notes: " + notes : "",
          ].filter(Boolean).join("\n") : description,
          procedureName,
          specialty,
          suggestedCpt,
          notes,
          reporterEmail: String(data.get("reporterEmail") || "").trim(),
          pageContext: pageContext(issueType === "missing_cpt_code" ? procedureName + " " + notes : description),
        };
        const response = await fetch(BACKEND_URL + "/reports", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const result = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(result.detail || result.error || "Report failed");
        status.className = "fccf-report-status fccf-report-success";
        status.textContent = "Logged " + (result.report && result.report.id ? result.report.id : "report") + ". Human review required.";
        form.reset();
      } catch (err) {
        status.className = "fccf-report-status fccf-report-error";
        status.textContent = "Could not submit. Please try again.";
      } finally {
        submit.disabled = false;
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderWidget);
  } else {
    renderWidget();
  }
})();
