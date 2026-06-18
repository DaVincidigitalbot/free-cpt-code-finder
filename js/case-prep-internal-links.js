(function () {
  const codeMap = {
    "47562": ["laparoscopic-cholecystectomy", "Laparoscopic Cholecystectomy"],
    "47563": ["laparoscopic-cholecystectomy", "Laparoscopic Cholecystectomy"],
    "47564": ["laparoscopic-cholecystectomy", "Laparoscopic Cholecystectomy"],
    "44970": ["laparoscopic-appendectomy", "Laparoscopic Appendectomy"],
    "49000": ["exploratory-laparotomy", "Exploratory Laparotomy"],
    "60220": ["thyroid-lobectomy", "Thyroid Lobectomy"],
    "60240": ["total-thyroidectomy", "Total Thyroidectomy"],
    "60252": ["total-thyroidectomy", "Total Thyroidectomy"],
    "60254": ["total-thyroidectomy", "Total Thyroidectomy"],
    "32551": ["chest-tube-placement", "Chest Tube Placement"],
    "49591": ["ventral-hernia-repair", "Ventral Hernia Repair"],
    "49593": ["ventral-hernia-repair", "Ventral Hernia Repair"],
    "49595": ["ventral-hernia-repair", "Ventral Hernia Repair"],
    "49613": ["ventral-hernia-repair", "Ventral Hernia Repair"],
    "49615": ["ventral-hernia-repair", "Ventral Hernia Repair"],
    "49617": ["ventral-hernia-repair", "Ventral Hernia Repair"],
  };
  const blogMap = {
    "/blog/guides/cpt-code-laparoscopic-cholecystectomy.html": [["laparoscopic-cholecystectomy", "Laparoscopic Cholecystectomy", "Before the OR, review critical view anatomy, bailout strategy, complications, and documentation pearls."]],
    "/blog/icd10/icd10-coding-gallbladder-disease.html": [["laparoscopic-cholecystectomy", "Laparoscopic Cholecystectomy", "Connect gallbladder coding with the anatomy and operative decisions that drive the case."]],
    "/blog/guides/cpt-code-appendectomy.html": [["laparoscopic-appendectomy", "Laparoscopic Appendectomy", "Review difficult appendix anatomy, stump management, postoperative abscess, and documentation decisions."]],
    "/blog/icd10/icd10-coding-acute-appendicitis.html": [["laparoscopic-appendectomy", "Laparoscopic Appendectomy", "Pair appendicitis diagnosis coding with operative decision-making and complication awareness."]],
    "/blog/guides/cpt-code-ventral-hernia-repair.html": [["ventral-hernia-repair", "Ventral Hernia Repair", "Review mesh planes, TAR anatomy, enterotomy strategy, and documentation pearls before the case."]],
    "/blog/icd10/icd10-coding-hernias.html": [["ventral-hernia-repair", "Ventral Hernia Repair", "Link hernia diagnosis coding to operative anatomy, mesh selection, and surgical decision challenges."]],
    "/blog/guides/cpt-code-thyroid-surgery.html": [["thyroid-lobectomy", "Thyroid Lobectomy", "Review RLN, EBSLN, parathyroid preservation, and loss-of-signal judgment."], ["total-thyroidectomy", "Total Thyroidectomy", "Review bilateral nerve risk, hypocalcemia prevention, neck hematoma, and documentation pearls."]],
    "/blog/guides/cpt-code-exploratory-laparotomy.html": [["exploratory-laparotomy", "Exploratory Laparotomy", "Review trauma exploration, bowel run technique, retroperitoneal hematoma zones, and damage-control decisions."]],
    "/blog/guides/trauma-laparotomy-cpt-guide.html": [["exploratory-laparotomy", "Exploratory Laparotomy", "Connect laparotomy coding with operative sequencing, source control, and open-abdomen planning."]],
    "/blog/guides/cpt-code-trauma-surgery.html": [["exploratory-laparotomy", "Exploratory Laparotomy", "Review trauma laparotomy strategy and damage-control judgment."], ["chest-tube-placement", "Chest Tube Placement", "Review safe triangle anatomy, hemothorax thresholds, and chest tube troubleshooting."]],
    "/blog/guides/cpt-code-critical-care-billing.html": [["chest-tube-placement", "Chest Tube Placement", "Review tube thoracostomy anatomy, air-versus-fluid direction, and escalation decisions."]],
    "/blog/modifiers/modifier-22-explained.html": [["ventral-hernia-repair", "Ventral Hernia Repair", "See how difficult anatomy, enterotomy, TAR decisions, and physiologic intolerance support stronger documentation."], ["laparoscopic-cholecystectomy", "Laparoscopic Cholecystectomy", "Review difficult gallbladder bailout decisions that may support increased-procedure documentation."]],
    "/blog/modifiers/most-surgeons-under-document-hard-cases.html": [["exploratory-laparotomy", "Exploratory Laparotomy", "Use surgical decision challenges to understand what hard-case documentation should actually capture."]],
    "/blog/modifiers/common-modifier-mistakes-surgeons.html": [["ventral-hernia-repair", "Ventral Hernia Repair", "Review complex hernia decisions where documentation and operative judgment intersect."]],
    "/blog/modifiers/modifier-58-78-79-explained.html": [["exploratory-laparotomy", "Exploratory Laparotomy", "Review planned takeback, open abdomen, and source-control scenarios that shape staged-care documentation."]],
    "/blog/modifiers/modifier-57-explained.html": [["exploratory-laparotomy", "Exploratory Laparotomy", "Review urgent operative decision-making when evaluation leads directly to the OR."]],
  };
  function ensureCss() {
    if (document.querySelector('link[data-case-prep-links-css]')) return;
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = "/styles/case-prep-links.css";
    link.dataset.casePrepLinksCss = "1";
    document.head.appendChild(link);
  }
  function track(eventName, params) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: eventName, ...(params || {}) });
    if (typeof window.gtag === "function") window.gtag("event", eventName, params || {});
  }
  function card(slug, title, copy, sourceType, sourceId) {
    return '<section class="case-prep-link-card" data-case-prep-link-card>' +
      '<div class="case-prep-link-kicker">Preparing for this operation?</div>' +
      '<h2>Preparing for This Operation?</h2>' +
      '<p>' + copy + '</p>' +
      '<ul><li>Anatomy</li><li>Operative steps</li><li>Surgical Decision Challenges</li><li>Common complications</li><li>Documentation pearls</li></ul>' +
      '<a class="case-prep-link-button" data-case-prep-link data-source-type="' + sourceType + '" data-source-id="' + sourceId + '" data-target-slug="' + slug + '" href="/case-prep/' + slug + '/">Go to Surgical Case Prep: ' + title + '</a>' +
      '</section>';
  }
  function bindTracking(root) {
    root.querySelectorAll("[data-case-prep-link]").forEach((link) => {
      link.addEventListener("click", () => track("case_prep_internal_click", {
        source_type: link.dataset.sourceType || "unknown",
        source_id: link.dataset.sourceId || location.pathname,
        target_slug: link.dataset.targetSlug || "",
      }));
    });
  }
  function mountCpt() {
    const match = location.pathname.match(/\/codes\/([A-Z0-9]+)\.html$/);
    if (!match || !codeMap[match[1]]) return;
    ensureCss();
    const [slug, title] = codeMap[match[1]];
    const main = document.querySelector("main");
    if (!main || document.querySelector("[data-case-prep-link-card]")) return;
    const section = document.createElement("div");
    section.innerHTML = card(slug, title, "Use the Case Prep guide to connect this CPT code with the real anatomy, operative decisions, complications, and documentation that drive the case.", "cpt", match[1]);
    const codingNote = [...main.querySelectorAll("section")].find((s) => /Coding Note/i.test(s.textContent || ""));
    (codingNote || main.querySelector("section") || main).insertAdjacentElement("afterend", section.firstElementChild);
    bindTracking(main);
  }
  function mountBlog() {
    const items = blogMap[location.pathname];
    if (!items || !items.length) return;
    ensureCss();
    const article = document.querySelector("article .container") || document.querySelector("article") || document.querySelector("main .container") || document.querySelector("main");
    if (!article || document.querySelector("[data-case-prep-link-card]")) return;
    const wrap = document.createElement("div");
    wrap.className = "case-prep-link-stack";
    wrap.innerHTML = items.map(([slug, title, copy]) => card(slug, title, copy, "blog", location.pathname)).join("");
    const firstH2 = article.querySelector("h2");
    (firstH2 || article.firstElementChild || article).insertAdjacentElement("beforebegin", wrap);
    bindTracking(wrap);
  }
  document.addEventListener("DOMContentLoaded", () => {
    mountCpt();
    mountBlog();
  });
})();
