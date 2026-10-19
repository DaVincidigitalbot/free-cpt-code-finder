(function () {
  "use strict";

  const INDEX_URL = "/case-prep/clinical-library-index.json";
  const PAGE_SIZE = 30;
  const state = { data: null, query: "", category: "all", visible: PAGE_SIZE };

  function escapeHtml(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, (character) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    })[character]);
  }

  function track(eventName, parameters) {
    try {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ event: eventName, ...(parameters || {}) });
      if (typeof window.gtag === "function") window.gtag("event", eventName, parameters || {});
    } catch (_) {
      // Analytics must never interrupt education content.
    }
  }

  async function loadLibrary() {
    if (state.data) return state.data;
    const response = await fetch(INDEX_URL, { credentials: "same-origin" });
    if (!response.ok) throw new Error("Unable to load the surgical case-prep library.");
    state.data = await response.json();
    return state.data;
  }

  function procedureSearchText(procedure) {
    return [
      procedure.name,
      procedure.category,
      procedure.overview,
      ...(procedure.searchTerms || []),
    ].join(" ").toLowerCase();
  }

  function procedureUrl(id) {
    return "/case-prep/library/?procedure=" + encodeURIComponent(id);
  }

  function procedureDataUrl(id) {
    return "/case-prep/library-data/" + encodeURIComponent(id) + ".json";
  }

  function cardMarkup(procedure) {
    return '<a class="library-card" href="' + procedureUrl(procedure.id) + '" data-library-card data-procedure-id="' + escapeHtml(procedure.id) + '">' +
      '<div class="library-card-meta"><span>' + escapeHtml(procedure.category) + '</span><b>' + procedure.questionCount + ' questions</b></div>' +
      '<h3>' + escapeHtml(procedure.name) + '</h3>' +
      '<p>' + escapeHtml(procedure.overview) + '</p>' +
      '<div class="library-card-footer"><span>Anatomy · Steps · Pitfalls</span><strong>Open prep sheet →</strong></div>' +
      '</a>';
  }

  function filteredProcedures() {
    const query = state.query.trim().toLowerCase();
    return state.data.procedures.filter((procedure) => {
      const categoryMatch = state.category === "all" || procedure.category === state.category;
      const queryMatch = !query || procedureSearchText(procedure).includes(query);
      return categoryMatch && queryMatch;
    });
  }

  function renderLibraryResults() {
    const grid = document.querySelector("[data-library-grid]");
    if (!grid) return;
    const matches = filteredProcedures();
    const shown = matches.slice(0, state.visible);
    const count = document.querySelector("[data-library-count]");
    const empty = document.querySelector("[data-library-empty]");
    const more = document.querySelector("[data-library-more]");

    grid.innerHTML = shown.map(cardMarkup).join("");
    grid.setAttribute("aria-busy", "false");
    count.textContent = matches.length + (matches.length === 1 ? " procedure" : " procedures");
    empty.hidden = matches.length !== 0;
    more.hidden = state.visible >= matches.length;
    if (!more.hidden) more.textContent = "Show " + Math.min(PAGE_SIZE, matches.length - state.visible) + " more procedures";

    grid.querySelectorAll("[data-library-card]").forEach((card) => {
      card.addEventListener("click", () => track("case_prep_library_open", {
        procedure_id: card.dataset.procedureId || "",
        query: state.query,
        category: state.category,
      }));
    });
  }

  function renderLibraryHome() {
    const root = document.querySelector("[data-case-prep-library-home]");
    if (!root) return;
    const search = root.querySelector("[data-library-search]");
    const category = root.querySelector("[data-library-category]");
    const reset = root.querySelector("[data-library-reset]");
    const more = root.querySelector("[data-library-more]");

    category.insertAdjacentHTML("beforeend", state.data.categories.map((name) => '<option value="' + escapeHtml(name) + '">' + escapeHtml(name) + '</option>').join(""));

    search.addEventListener("input", () => {
      state.query = search.value;
      state.visible = PAGE_SIZE;
      renderLibraryResults();
    });
    category.addEventListener("change", () => {
      state.category = category.value;
      state.visible = PAGE_SIZE;
      renderLibraryResults();
    });
    reset.addEventListener("click", () => {
      search.value = "";
      category.value = "all";
      state.query = "";
      state.category = "all";
      state.visible = PAGE_SIZE;
      renderLibraryResults();
      search.focus();
    });
    more.addEventListener("click", () => {
      state.visible += PAGE_SIZE;
      renderLibraryResults();
    });
    document.addEventListener("keydown", (event) => {
      const tag = document.activeElement && document.activeElement.tagName;
      if (event.key === "/" && tag !== "INPUT" && tag !== "TEXTAREA" && tag !== "SELECT") {
        event.preventDefault();
        search.focus();
      }
    });
    renderLibraryResults();
  }

  function listMarkup(items, ordered) {
    if (!items || !items.length) return '<p class="prep-none">No additional items listed.</p>';
    const tag = ordered ? "ol" : "ul";
    return "<" + tag + ">" + items.map((item) => "<li>" + escapeHtml(item) + "</li>").join("") + "</" + tag + ">";
  }

  function questionMarkup(question, index) {
    const answerId = "question-answer-" + index;
    const level = question.level || "resident";
    const labels = { medical_student: "Medical Student", resident: "Resident", attending: "Attending" };
    return '<article class="question-card" data-question-level-card="' + escapeHtml(level) + '"><button type="button" aria-expanded="false" aria-controls="' + answerId + '"><span><small>Question ' + String(index + 1).padStart(2, "0") + '</small>' + escapeHtml(question.question) + '</span><span class="question-level-badge question-level-badge--' + escapeHtml(level) + '">' + escapeHtml(labels[level] || level) + '</span><b>Reveal answer</b></button><div class="question-answer" id="' + answerId + '" hidden><strong>Answer</strong><p>' + escapeHtml(question.answer) + '</p></div></article>';
  }

  function filterQuestionsByLevel(root, level) {
    let visible = 0;
    root.querySelectorAll("[data-question-level-card]").forEach((card) => {
      const show = level === "all" || card.dataset.questionLevelCard === level;
      card.hidden = !show;
      if (show) visible += 1;
    });
    const labels = { all: "", medical_student: " · Medical Student", resident: " · Resident", attending: " · Attending" };
    document.querySelector("[data-question-count]").textContent = visible + (visible === 1 ? " question" : " questions") + labels[level];
  }

  function humanizeSlug(value) {
    return String(value || "")
      .split("-")
      .filter(Boolean)
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  }

  function relatedMarkup(procedure, lookup) {
    return (procedure.relatedProcedures || []).map((id) => {
      const item = lookup.get(id);
      if (item) {
        return '<a href="' + procedureUrl(item.id) + '"><span>' + escapeHtml(item.category) + '</span><strong>' + escapeHtml(item.name) + '</strong></a>';
      }
      return '<span class="prep-related-unavailable"><span>Related reference</span><strong>' + escapeHtml(humanizeSlug(id)) + '</strong></span>';
    }).join("");
  }

  function updateMetadata(procedure) {
    const title = procedure.name + " Case Prep | FreeCPTCodeFinder.com";
    const description = "Prepare for " + procedure.name + ": anatomy, indications, critical steps, pitfalls, complications, postoperative priorities, and attending-style questions.";
    const url = "https://freecptcodefinder.com" + procedureUrl(procedure.id);
    document.title = title;
    const meta = document.querySelector('meta[name="description"]');
    if (meta) meta.setAttribute("content", description);
    const canonical = document.querySelector('link[rel="canonical"]');
    if (canonical) canonical.setAttribute("href", url);
    const openGraph = { "og:title": title, "og:description": description, "og:url": url };
    Object.entries(openGraph).forEach(([property, content]) => {
      const element = document.querySelector('meta[property="' + property + '"]');
      if (element) element.setAttribute("content", content);
    });
  }

  async function renderProcedureDetail() {
    const root = document.querySelector("[data-procedure-detail]");
    if (!root) return;
    const parameters = new URLSearchParams(window.location.search);
    let id = parameters.get("procedure");
    if (!id && state.data.procedures.length) {
      id = state.data.procedures[0].id;
      history.replaceState(null, "", procedureUrl(id));
    }
    const summary = state.data.procedures.find((item) => item.id === id);
    if (!summary) {
      root.hidden = true;
      document.querySelector("[data-procedure-error]").hidden = false;
      return;
    }
    const response = await fetch(procedureDataUrl(id), { credentials: "same-origin" });
    if (!response.ok) throw new Error("Unable to load this procedure.");
    const procedure = await response.json();

    updateMetadata(procedure);
    document.querySelector("[data-breadcrumb-name]").textContent = procedure.name;
    document.querySelector("[data-procedure-category]").textContent = procedure.category + " · Case Prep Sheet";
    document.querySelector("[data-procedure-name]").textContent = procedure.name;
    document.querySelector("[data-procedure-overview]").textContent = procedure.overview;

    const orderedFields = new Set(["criticalSteps"]);
    document.querySelectorAll("[data-field]").forEach((container) => {
      const field = container.dataset.field;
      const value = procedure[field];
      container.innerHTML = Array.isArray(value) ? listMarkup(value, orderedFields.has(field)) : '<p class="prep-position">' + escapeHtml(value) + '</p>';
    });

    const bank = document.querySelector("[data-question-bank]");
    const questionCards = procedure.pimpingQuestions.map(questionMarkup).join("");
    bank.innerHTML = questionCards;
    document.querySelector("[data-question-count]").textContent = procedure.pimpingQuestions.length + " questions";
    const filters = document.querySelector("[data-question-level-filter]");
    filters.querySelectorAll("[data-question-level]").forEach((filterButton) => {
      filterButton.addEventListener("click", () => {
        filters.querySelectorAll("[data-question-level]").forEach((button) => {
          button.setAttribute("aria-pressed", String(button === filterButton));
        });
        filterQuestionsByLevel(bank, filterButton.dataset.questionLevel);
      });
    });
    bank.querySelectorAll(".question-card button").forEach((button) => {
      button.addEventListener("click", () => {
        const answer = document.getElementById(button.getAttribute("aria-controls"));
        const open = button.getAttribute("aria-expanded") === "true";
        button.setAttribute("aria-expanded", String(!open));
        answer.hidden = open;
        button.querySelector("b").textContent = open ? "Reveal answer" : "Hide answer";
        if (!open) track("case_prep_library_question_open", { procedure_id: procedure.id });
      });
    });

    const lookup = new Map(state.data.procedures.map((item) => [item.id, item]));
    const related = document.querySelector("[data-related-procedures]");
    const relatedHtml = relatedMarkup(procedure, lookup);
    const relatedSection = document.querySelector("[data-related-section]");
    related.innerHTML = relatedHtml;
    relatedSection.hidden = !relatedHtml;

    document.querySelector("[data-print-sheet]").addEventListener("click", () => window.print());
    root.setAttribute("aria-busy", "false");
    track("case_prep_library_view", { procedure_id: procedure.id, category: procedure.category });
  }

  document.addEventListener("DOMContentLoaded", async () => {
    try {
      await loadLibrary();
      renderLibraryHome();
      await renderProcedureDetail();
    } catch (error) {
      console.error(error);
      const count = document.querySelector("[data-library-count]");
      if (count) count.textContent = "The library could not be loaded. Please refresh.";
      const detail = document.querySelector("[data-procedure-detail]");
      const errorPanel = document.querySelector("[data-procedure-error]");
      if (detail && errorPanel) {
        detail.hidden = true;
        errorPanel.hidden = false;
      }
    }
  });
})();
