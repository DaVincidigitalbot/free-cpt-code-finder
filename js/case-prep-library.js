(function () {
  "use strict";

  const INDEX_URL = "/case-prep/clinical-library-index.json";
  const PAGE_SIZE = 30;
  const state = { data: null, query: "", category: "all", visible: PAGE_SIZE, catalog: [], guidesAvailable: false };

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

  // Keep discovery rules outside generated JSON so future imports preserve them.
  const SEARCH_ALIASES = {
    lap: "laparoscopic", chole: "cholecystectomy", appy: "appendectomy",
    tar: "transversus abdominis release", etep: "etep",
  };
  function normalizeSearch(value) {
    return String(value || "").toLowerCase().normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, " ").trim()
      .replace(/\s+/g, " ");
  }
  function expandSearch(value) {
    return normalizeSearch(value).replace(/\bex lap\b/g, "exploratory laparotomy")
      .split(" ").map((token) => SEARCH_ALIASES[token] || token).join(" ");
  }
  function procedureSearchText(procedure) {
    return expandSearch([procedure.name, procedure.category, procedure.overview,
      ...(procedure.aliases || []), ...(procedure.searchTerms || [])].join(" "));
  }
  function buildCatalog(imported, guides) {
    const overlaps = {
      "laparoscopic-cholecystectomy": ["lap-chole"],
      "laparoscopic-appendectomy": ["lap-appendectomy"],
      "thyroid-lobectomy": ["hemithyroidectomy", "hemithyroidectomy-lobectomy"],
      "total-thyroidectomy": ["total-thyroidectomy"],
      parathyroidectomy: ["parathyroidectomy"],
      "chest-tube-placement": ["chest-tube-insertion"],
    };
    const guideCategories = {
      "exploratory-laparotomy": "Trauma",
      "ventral-hernia-repair": "Hernia",
      "transversus-abdominis-release": "Hernia",
      "hiatal-hernia-repair": "Hernia",
    };
    const catalog = imported.map((item) => ({ ...item, kind: "Rapid prep", url: procedureUrl(item.id) }));
    guides.filter((guide) => guide.status === "live").forEach((guide) => {
      const ids = overlaps[guide.slug] || [];
      const matching = catalog.filter((item) => ids.includes(item.id));
      const primary = matching[0];
      const record = {
        id: "guide-" + guide.slug, name: guide.title, overview: guide.summary,
        category: primary ? primary.category : guideCategories[guide.slug] || guide.category,
        kind: "Operative guide", url: "/case-prep/" + guide.slug + "/",
        rapidUrl: primary && primary.url,
        rapidSheets: matching.map((item) => ({ name: item.name, url: item.url })),
        questionCount: primary ? primary.questionCount : 0,
        aliases: matching.map((item) => item.name),
        searchTerms: matching.flatMap((item) => item.searchTerms || []).concat(guide.cptCodes || []),
      };
      for (let i = catalog.length - 1; i >= 0; i -= 1) {
        if (ids.includes(catalog[i].id)) catalog.splice(i, 1);
      }
      catalog.push(record);
    });
    return catalog.map((item) => ({ ...item, searchText: procedureSearchText(item), titleText: expandSearch(item.name) }));
  }
  function searchCatalog(catalog, query, category) {
    const normalized = expandSearch(query);
    const tokens = normalized.split(" ").filter(Boolean);
    return catalog.filter((item) => (category === "all" || item.category === category) &&
      tokens.every((token) => item.searchText.includes(token)))
      .map((item) => ({ item, score: !normalized ? 0 :
        (item.titleText === normalized ? 1000 : 0) +
        ((item.aliases || []).some((alias) => expandSearch(alias) === normalized) ? 800 : 0) +
        (item.titleText.includes(normalized) ? 300 : 0) +
        tokens.filter((token) => item.titleText.includes(token)).length * 30 +
        (item.kind === "Operative guide" ? 5 : 0) }))
      .sort((a, b) => b.score - a.score || a.item.name.localeCompare(b.item.name))
      .map(({ item }) => item);
  }

  function procedureUrl(id) {
    return "/case-prep/library/?procedure=" + encodeURIComponent(id);
  }

  function safeInternalUrl(value, fallback) {
    const expectedOrigin = "https://freecptcodefinder.com";
    const url = String(value || "").trim();
    if (!url.startsWith("/") || url.startsWith("//") || url.includes("\\")) return fallback;
    try {
      const parsed = new URL(url, expectedOrigin);
      if (parsed.origin !== expectedOrigin) return fallback;
      return parsed.pathname + parsed.search + parsed.hash;
    } catch (_) {
      return fallback;
    }
  }

  function procedureDataUrl(id) {
    return "/case-prep/library-data/" + encodeURIComponent(id) + ".json";
  }

  function cardMarkup(procedure) {
    const destination = safeInternalUrl(procedure.url, procedureUrl(procedure.id));
    return '<article class="library-card"><a class="library-card-link" href="' + escapeHtml(destination) + '" data-library-card data-procedure-id="' + escapeHtml(procedure.id) + '">' +
      '<div class="library-card-meta"><span>' + escapeHtml(procedure.category) + '</span><b>' + escapeHtml(procedure.kind || 'Rapid prep') + '</b></div>' +
      '<h3>' + escapeHtml(procedure.name) + '</h3>' +
      '<p>' + escapeHtml(procedure.overview) + '</p>' +
      '<div class="library-card-footer"><span>Anatomy · Steps · Pitfalls</span><strong>Open ' + (procedure.kind === 'Operative guide' ? 'guide' : 'prep sheet') + ' →</strong></div></a>' +
      (procedure.rapidSheets || []).map((sheet) => '<a class="library-rapid-link" href="' + escapeHtml(safeInternalUrl(sheet.url, procedureUrl(procedure.id))) + '">Rapid prep &amp; questions: ' + escapeHtml(sheet.name) + ' →</a>').join('') + '</article>';
  }

  function filteredProcedures() {
    return searchCatalog(state.catalog, state.query, state.category);
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
    const coverage = state.guidesAvailable ? " · operative guides and rapid prep" : " · rapid prep";
    count.textContent = matches.length + (matches.length === 1 ? " procedure" : " procedures") + (state.query.trim() ? ' matching “' + state.query.trim() + '”' : coverage);
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

    category.insertAdjacentHTML("beforeend", [...new Set(state.catalog.map((item) => item.category))].sort().map((name) => '<option value="' + escapeHtml(name) + '">' + escapeHtml(name) + '</option>').join(""));

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
    root.querySelectorAll("[data-search-example]").forEach((button) => {
      button.addEventListener("click", () => {
        search.value = button.dataset.searchExample;
        search.dispatchEvent(new Event("input"));
        search.focus();
      });
    });
    state.query = search.value;
    state.category = category.value;
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
      if (document.querySelector("[data-case-prep-library-home]")) {
        let guides = [];
        try {
          const response = await fetch("/case-prep/case-prep-data.json", { credentials: "same-origin" });
          if (!response.ok) throw new Error("Guide catalog unavailable");
          guides = (await response.json()).procedures;
          state.guidesAvailable = true;
        } catch (_) {
          state.guidesAvailable = false;
          document.querySelector("[data-library-notice]").textContent = "Operative guides are temporarily unavailable in search. Rapid prep is available; try reloading for all guides.";
        }
        state.catalog = buildCatalog(state.data.procedures, guides);
        renderLibraryHome();
      }
      await renderProcedureDetail();
    } catch (error) {
      console.error(error);
      const count = document.querySelector("[data-library-count]");
      if (count) {
        count.textContent = "The library could not be loaded. Reload to try again.";
        document.querySelector("[data-library-grid]").setAttribute("aria-busy", "false");
        document.querySelector("[data-library-retry]").hidden = false;
        document.querySelector("[data-library-retry]").onclick = () => window.location.reload();
      }
      const detail = document.querySelector("[data-procedure-detail]");
      const errorPanel = document.querySelector("[data-procedure-error]");
      if (detail && errorPanel) {
        detail.hidden = true;
        errorPanel.hidden = false;
      }
    }
  });
})();
