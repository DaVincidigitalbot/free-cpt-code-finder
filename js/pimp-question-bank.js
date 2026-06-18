(function () {
  const DATA_URL = "/case-prep/case-prep-data.json";
  const state = { data: null, cpt: null };
  const labels = {
    student: "🟢 Medical Student",
    resident: "🟡 Resident",
    oral_boards: "🔴 Chief Resident / Oral Boards",
  };
  const esc = (s) =>
    String(s || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const money = (v) => (typeof v === "number" ? "$" + v.toFixed(2) : "—");
  async function loadJson(url) {
    const res = await fetch(url);
    if (!res.ok) throw new Error("Could not load " + url);
    return res.json();
  }
  async function ensureData() {
    if (!state.data) state.data = await loadJson(DATA_URL);
    if (!state.cpt) state.cpt = await loadJson("/cpt_database.json");
    return state;
  }
  function answerHtml(q) {
    const parts = [];
    if (q.answer) parts.push("<p>" + esc(q.answer) + "</p>");
    if (q.bullets && q.bullets.length) parts.push("<ul>" + q.bullets.map((b) => "<li>" + esc(b) + "</li>").join("") + "</ul>");
    if (q.bottomLine) parts.push("<p><strong>Bottom line:</strong> " + esc(q.bottomLine) + "</p>");
    return parts.join("");
  }
  function renderQuestionCard(q) {
    return '<article class="pimp-card" data-level="' + esc(q.level) + '">' +
      '<button class="pimp-question" type="button" aria-expanded="false">' +
      '<span>Q: ' + esc(q.question) + '</span>' +
      '<span class="pimp-level">' + esc(labels[q.level] || q.level) + '</span>' +
      '<span class="pimp-reveal">Click to Reveal Answer</span>' +
      '</button>' +
      '<div class="pimp-answer"><div class="pimp-answer-inner"><p><strong>ANSWER:</strong></p>' + answerHtml(q) + '</div></div>' +
      '</article>';
  }
  function bindCards(scope) {
    scope.querySelectorAll(".pimp-question").forEach((btn) => {
      btn.addEventListener("click", () => {
        const card = btn.closest(".pimp-card");
        const open = card.classList.toggle("open");
        btn.setAttribute("aria-expanded", String(open));
        const label = btn.querySelector(".pimp-reveal");
        if (label) label.textContent = open ? "Click to Collapse Answer" : "Click to Reveal Answer";
      });
    });
  }
  function renderPimpBank(slug) {
    const root = document.querySelector("[data-pimp-bank]");
    if (!root) return;
    const questions = state.data.questions[slug] || [];
    root.innerHTML = '<div class="pimp-toolbar"><div class="pimp-filters" aria-label="Question filters">' +
      '<button class="pimp-filter active" data-filter="all" type="button">All Questions</button>' +
      '<button class="pimp-filter" data-filter="student" type="button">Medical Student</button>' +
      '<button class="pimp-filter" data-filter="resident" type="button">Resident</button>' +
      '<button class="pimp-filter" data-filter="oral_boards" type="button">Oral Boards</button>' +
      '</div><button class="quiz-toggle" data-quiz-toggle type="button">Quiz Mode</button></div>' +
      '<div class="pimp-list" data-pimp-list>' + questions.map(renderQuestionCard).join("") + '</div>' +
      '<div class="quiz-panel" data-quiz-panel></div>';
    bindCards(root);
    const list = root.querySelector("[data-pimp-list]");
    root.querySelectorAll("[data-filter]").forEach((btn) => {
      btn.addEventListener("click", () => {
        root.querySelectorAll("[data-filter]").forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        const filter = btn.dataset.filter;
        list.querySelectorAll(".pimp-card").forEach((card) => {
          card.style.display = filter === "all" || card.dataset.level === filter ? "" : "none";
        });
      });
    });
    root.querySelector("[data-quiz-toggle]").addEventListener("click", () => toggleQuiz(root, slug, questions));
  }
  function toggleQuiz(root, slug, questions) {
    const panel = root.querySelector("[data-quiz-panel]");
    const list = root.querySelector("[data-pimp-list]");
    const active = panel.classList.toggle("active");
    list.style.display = active ? "none" : "";
    root.querySelector("[data-quiz-toggle]").textContent = active ? "Exit Quiz Mode" : "Quiz Mode";
    if (active) renderQuiz(panel, slug, questions);
  }
  function renderQuiz(panel, slug, questions) {
    const key = "fccf-case-prep-quiz-" + slug;
    let idx = Number(localStorage.getItem(key) || 0);
    if (!questions[idx]) idx = 0;
    let showing = false;
    function draw() {
      const q = questions[idx];
      panel.innerHTML = '<div class="quiz-progress">Question ' + (idx + 1) + ' of ' + questions.length + '</div>' +
        '<div class="pimp-level">' + esc(labels[q.level] || q.level) + '</div>' +
        '<div class="quiz-question">Q: ' + esc(q.question) + '</div>' +
        '<div class="quiz-answer' + (showing ? " show" : "") + '" data-quiz-answer><p><strong>ANSWER:</strong></p>' + answerHtml(q) + '</div>' +
        '<div class="quiz-actions"><button class="quiz-btn" data-prev type="button">Previous Question</button><button class="quiz-btn primary" data-show type="button">' + (showing ? "Hide Answer" : "Show Answer") + '</button><button class="quiz-btn" data-next type="button">Next Question</button></div>';
      panel.querySelector("[data-show]").addEventListener("click", () => { showing = !showing; draw(); });
      panel.querySelector("[data-prev]").addEventListener("click", () => { idx = Math.max(0, idx - 1); showing = false; localStorage.setItem(key, String(idx)); draw(); });
      panel.querySelector("[data-next]").addEventListener("click", () => { idx = Math.min(questions.length - 1, idx + 1); showing = false; localStorage.setItem(key, String(idx)); draw(); });
    }
    draw();
  }
  function renderCptPearls(slug) {
    const root = document.querySelector("[data-cpt-pearls]");
    if (!root) return;
    const proc = state.data.procedures.find((p) => p.slug === slug);
    const codes = proc && proc.cptCodes ? proc.cptCodes : [];
    root.innerHTML = '<div class="case-prep-table-scroll"><table><thead><tr><th>CPT</th><th>Description</th><th>wRVU</th><th>Global</th><th>Estimated Medicare</th></tr></thead><tbody>' +
      codes.map((code) => {
        const d = state.cpt[code] || {};
        return '<tr><td><a class="inline-code-link" href="/codes/' + code + '.html"><strong>' + code + '</strong></a></td><td>' + esc(d.description || "") + '</td><td>' + esc(d.work_rvu ?? "—") + '</td><td>' + esc((d.global_period_days ?? "—") + " days") + '</td><td>' + money(d.estimated_medicare_payment) + '</td></tr>';
      }).join("") + '</tbody></table></div>';
  }
  function renderRelated(slug) {
    const root = document.querySelector("[data-related-content]");
    if (!root) return;
    const proc = state.data.procedures.find((p) => p.slug === slug);
    if (!proc) return;
    const items = [];
    (proc.relatedProcedures || []).forEach((title) => {
      const p = state.data.procedures.find((x) => x.title === title);
      if (p && p.status === "live") items.push([p.title, "/case-prep/" + p.slug + "/"]);
      else items.push([title, "/case-prep/"]);
    });
    (proc.relatedGuides || []).forEach((g) => items.push([g.title, g.url]));
    root.innerHTML = '<div class="related-list">' + items.map((i) => '<a href="' + esc(i[1]) + '">' + esc(i[0]) + '</a>').join("") + '</div>';
  }
  function injectFaqSchema(slug) {
    const questions = (state.data.questions[slug] || []).slice(0, 8);
    if (!questions.length || document.querySelector("script[data-case-prep-faq-schema]")) return;
    const schema = {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": questions.map((q) => ({
        "@type": "Question",
        "name": q.question,
        "acceptedAnswer": {
          "@type": "Answer",
          "text": [q.answer, ...(q.bullets || []), q.bottomLine].filter(Boolean).join(" ")
        }
      }))
    };
    const script = document.createElement("script");
    script.type = "application/ld+json";
    script.dataset.casePrepFaqSchema = "1";
    script.textContent = JSON.stringify(schema);
    document.head.appendChild(script);
  }
  function renderLanding() {
    const root = document.querySelector("[data-case-prep-landing]");
    if (!root) return;
    const categories = state.data.categories || [];
    const procedures = state.data.procedures || [];
    root.querySelector("[data-categories]").innerHTML = categories.map((cat) => '<article class="case-prep-card"><h3>' + esc(cat.name) + '</h3><p>' + esc(cat.description) + '</p><div class="case-prep-tagrow">' + cat.procedures.map((p) => '<span class="badge">' + esc(p) + '</span>').join("") + '</div></article>').join("");
    const procedureHtml = (p) => {
      const inner = '<h3>' + esc(p.title) + '</h3><p>' + esc(p.summary) + '</p><div class="case-prep-tagrow"><span class="badge">' + esc(p.category) + '</span>' + (p.cptCodes || []).map((c) => '<span class="badge">' + c + '</span>').join("") + (p.status === "live" ? "" : '<span class="badge">Coming soon</span>') + '</div>';
      return p.status === "live"
        ? '<a class="case-prep-card" data-procedure-card href="/case-prep/' + esc(p.slug) + '/">' + inner + '</a>'
        : '<article class="case-prep-card" data-procedure-card>' + inner + '</article>';
    };
    const searchResults = root.querySelector("[data-search-results]");
    root.querySelector("[data-recent]").innerHTML = procedures.filter((p) => p.status === "live").map(procedureHtml).join("");
    root.querySelector("[data-most-viewed]").innerHTML = procedures.slice().sort((a,b)=>(b.mostViewedScore||0)-(a.mostViewedScore||0)).slice(0,6).map(procedureHtml).join("");
    root.querySelector("[data-related-guides]").innerHTML = state.data.relatedCodingGuides.map((g) => '<a class="case-prep-card" href="' + esc(g.url) + '"><h3>' + esc(g.title) + '</h3><p>' + esc(g.summary) + '</p></a>').join("");
    const input = root.querySelector("[data-case-prep-search]");
    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      if (!searchResults) return;
      const matches = procedures.filter((p) => !q || [p.title, p.summary, p.category, ...(p.cptCodes || [])].join(" ").toLowerCase().includes(q));
      searchResults.hidden = !q;
      searchResults.innerHTML = q ? matches.map(procedureHtml).join("") || '<p>No procedure matches yet.</p>' : "";
    });
  }
  document.addEventListener("DOMContentLoaded", async () => {
    try {
      await ensureData();
      renderLanding();
      const slug = document.body && document.body.dataset.procedureSlug;
      if (slug) {
        renderPimpBank(slug);
        renderCptPearls(slug);
        renderRelated(slug);
        injectFaqSchema(slug);
      }
    } catch (err) {
      console.error(err);
    }
  });
})();
