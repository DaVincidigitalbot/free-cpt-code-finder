(function () {
  const DATA_URL = "/case-prep/case-prep-data.json";
  const state = { data: null, cpt: null };
  const labels = {
    student: "🟢 Medical Student",
    resident: "🟡 Resident",
    oral_boards: "🔴 Advanced Decision-Making",
  };
  const esc = (s) =>
    String(s || "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  const money = (v) => (typeof v === "number" ? "$" + v.toFixed(2) : "—");
  function track(eventName, params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: eventName, ...(params || {}) });
    if (typeof window.gtag === "function") window.gtag("event", eventName, params || {});
  }
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
  function renderQuestionCard(q, index) {
    return '<article class="pimp-card" data-level="' + esc(q.level) + '" data-question-index="' + index + '">' +
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
        if (open) track("case_prep_pimp_question_open", {
          procedure_slug: document.body && document.body.dataset.procedureSlug || "",
          question_index: card.dataset.questionIndex || "",
          question_level: card.dataset.level || "",
        });
        const label = btn.querySelector(".pimp-reveal");
        if (label) label.textContent = open ? "Click to Collapse Answer" : "Click to Reveal Answer";
      });
    });
  }
  function listHtml(items) {
    return items && items.length ? "<ul>" + items.map((item) => "<li>" + esc(item) + "</li>").join("") + "</ul>" : "";
  }
  function cptLinkList(codes) {
    return codes && codes.length ? '<div class="case-challenge-cpt-links"><strong>Related CPT review:</strong> ' + codes.map((code) => '<a data-case-prep-cpt-link href="/codes/' + esc(code) + '.html">' + esc(code) + '</a>').join(" ") + '</div>' : "";
  }
  function renderChallengeCard(challenge, index, cptCodes) {
    const discussion = challenge.expertDiscussion || {};
    const answerBlocks = [
      ["Correct Answer", discussion.correctAnswer || challenge.discussion],
      ["Why This Is Correct", discussion.whyCorrect],
      ["Why Alternatives Are Wrong", discussion.whyAlternativesWrong],
      ["Common Trainee Mistakes", discussion.commonTraineeMistakes],
      ["Attending Pearl", discussion.attendingPearl],
      ["Coding / Documentation Pearl", discussion.codingDocumentationPearl],
    ].filter((block) => block[1] && (!Array.isArray(block[1]) || block[1].length));
    return '<article class="case-challenge-card">' +
      '<div class="case-challenge-header"><div><span class="case-challenge-eyebrow">Surgical Decision Challenge ' + (index + 1) + '</span><h3>' + esc(challenge.title) + '</h3></div><span class="case-challenge-badge">' + esc(challenge.focus || "Judgment") + '</span></div>' +
      '<div class="case-challenge-grid">' +
      '<section><h4>History</h4><p>' + esc(challenge.history) + '</p></section>' +
      '<section><h4>Physical Examination</h4><p>' + esc(challenge.physical) + '</p></section>' +
      '<section><h4>Vitals</h4>' + listHtml(challenge.vitals) + '</section>' +
      '<section><h4>Labs</h4>' + listHtml(challenge.labs) + '</section>' +
      '<section><h4>Imaging</h4><p>' + esc(challenge.imaging) + '</p></section>' +
      '<section><h4>Relevant Operative Findings</h4><p>' + esc(challenge.intraoperative) + '</p></section>' +
      '</div>' +
      '<div class="case-challenge-decision"><h4>Decision Question</h4><p>' + esc(challenge.decisionPoint) + '</p></div>' +
      '<button class="case-challenge-reveal" type="button" aria-expanded="false">Reveal Expert Discussion</button>' +
      '<div class="case-challenge-answer"><div class="case-challenge-answer-inner">' +
      answerBlocks.map((block) => '<section class="case-challenge-answer-block"><h4>' + esc(block[0]) + '</h4>' + (Array.isArray(block[1]) ? listHtml(block[1]) : '<p>' + esc(block[1]) + '</p>') + '</section>').join("") +
      cptLinkList(cptCodes) +
      '</div></div>' +
      '</article>';
  }
  function bindChallenges(scope) {
    scope.querySelectorAll(".case-challenge-reveal").forEach((btn) => {
      btn.addEventListener("click", () => {
        const card = btn.closest(".case-challenge-card");
        const open = card.classList.toggle("open");
        btn.setAttribute("aria-expanded", String(open));
        btn.textContent = open ? "Hide Expert Discussion" : "Reveal Expert Discussion";
        if (open) track("case_prep_decision_challenge_open", {
          procedure_slug: document.body && document.body.dataset.procedureSlug || "",
          challenge_title: card.querySelector("h3") ? card.querySelector("h3").textContent : "",
        });
      });
    });
    scope.querySelectorAll("[data-case-prep-cpt-link]").forEach((link) => {
      link.addEventListener("click", () => track("case_prep_to_cpt_click", {
        procedure_slug: document.body && document.body.dataset.procedureSlug || "",
        cpt_code: link.textContent.replace(/[^0-9A-Z]/g, ""),
        source_area: "decision_challenge",
      }));
    });
  }
  function renderCaseChallenges(slug) {
    const root = document.querySelector("[data-case-challenges]");
    if (!root) return;
    const challenges = (state.data.caseChallenges && state.data.caseChallenges[slug]) || [];
    const proc = state.data.procedures.find((p) => p.slug === slug);
    const cptCodes = proc && proc.cptCodes ? proc.cptCodes : [];
    if (!challenges.length) {
      root.innerHTML = '<p>Case challenges are being built for this procedure.</p>';
      return;
    }
    root.innerHTML = '<div class="case-challenge-list">' + challenges.map((c, i) => renderChallengeCard(c, i, cptCodes)).join("") + '</div>';
    bindChallenges(root);
  }
  function renderPimpBank(slug) {
    const root = document.querySelector("[data-pimp-bank]");
    if (!root) return;
    const questions = state.data.questions[slug] || [];
    root.innerHTML = '<div class="pimp-toolbar"><div class="pimp-filters" aria-label="Question filters">' +
      '<button class="pimp-filter active" data-filter="all" type="button">All Questions</button>' +
      '<button class="pimp-filter" data-filter="student" type="button">Medical Student</button>' +
      '<button class="pimp-filter" data-filter="resident" type="button">Resident</button>' +
      '<button class="pimp-filter" data-filter="oral_boards" type="button">Advanced</button>' +
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
    root.innerHTML = '<div class="case-prep-cpt-context"><h3>Core CPT Review for This Case</h3><p>Use the CPT table with the operative anatomy and documentation pearls above. The goal is not just picking a code; it is documenting the clinical facts that justify the code.</p><div class="case-prep-cpt-chiprow">' + codes.map((code) => '<a data-case-prep-cpt-link href="/codes/' + esc(code) + '.html">CPT ' + esc(code) + '</a>').join("") + '</div></div>' +
      '<div class="case-prep-table-scroll"><table><thead><tr><th>CPT</th><th>Description</th><th>wRVU</th><th>Global</th><th>Estimated Medicare</th></tr></thead><tbody>' +
      codes.map((code) => {
        const d = state.cpt[code] || {};
        return '<tr><td><a class="inline-code-link" data-case-prep-cpt-link href="/codes/' + code + '.html"><strong>' + code + '</strong></a></td><td>' + esc(d.description || "") + '</td><td>' + esc(d.work_rvu ?? "—") + '</td><td>' + esc((d.global_period_days ?? "—") + " days") + '</td><td>' + money(d.estimated_medicare_payment) + '</td></tr>';
      }).join("") + '</tbody></table></div>';
    root.querySelectorAll("[data-case-prep-cpt-link]").forEach((link) => link.addEventListener("click", () => track("case_prep_to_cpt_click", {
      procedure_slug: slug,
      cpt_code: link.textContent.replace(/[^0-9A-Z]/g, ""),
    })));
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
    root.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => track("case_prep_related_click", {
      procedure_slug: slug,
      target_url: link.getAttribute("href") || "",
    })));
  }
  function renderGraydonPearls(slug) {
    const root = document.querySelector("[data-graydon-pearls]");
    if (!root) return;
    const pearls = (state.data.graydonPearls && state.data.graydonPearls[slug]) || [];
    if (!pearls.length) {
      root.closest(".case-prep-section").style.display = "none";
      return;
    }
    root.innerHTML = '<div class="graydon-pearls">' + pearls.map((p) => '<article class="graydon-pearl graydon-pearl--' + esc(p.severity || "standard") + '"><div class="graydon-pearl__label">' + esc(p.context || "Pearl") + '</div><h3>' + esc(p.title) + '</h3><p>' + esc(p.text) + '</p></article>').join("") + '</div>';
  }
  function observeAtlas(slug) {
    const atlas = document.querySelector(".case-prep-atlas,.anatomy-diagram");
    if (!atlas || !("IntersectionObserver" in window)) return;
    let sent = false;
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!sent && entry.isIntersecting) {
          sent = true;
          track("case_prep_anatomy_atlas_view", { procedure_slug: slug });
          observer.disconnect();
        }
      });
    }, { threshold: 0.45 });
    observer.observe(atlas);
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
    const featured = ["transversus-abdominis-release", "ventral-hernia-repair", "exploratory-laparotomy", "total-thyroidectomy"].map((slug) => procedures.find((p) => p.slug === slug)).filter(Boolean);
    const featuredRoot = root.querySelector("[data-featured-procedures]");
    if (featuredRoot) featuredRoot.innerHTML = featured.map(procedureHtml).join("");
    const updatedRoot = root.querySelector("[data-recently-updated]");
    if (updatedRoot) updatedRoot.innerHTML = procedures.filter((p) => p.status === "live").slice().sort((a,b)=>(b.recentlyUpdatedScore||0)-(a.recentlyUpdatedScore||0)).slice(0,6).map(procedureHtml).join("");
    const challengesRoot = root.querySelector("[data-new-decision-challenges]");
    if (challengesRoot) challengesRoot.innerHTML = procedures.filter((p) => p.status === "live" && state.data.caseChallenges && state.data.caseChallenges[p.slug]).map(procedureHtml).join("");
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
        renderCaseChallenges(slug);
        renderCptPearls(slug);
        renderGraydonPearls(slug);
        renderRelated(slug);
        injectFaqSchema(slug);
        observeAtlas(slug);
      }
    } catch (err) {
      console.error(err);
    }
  });
})();
