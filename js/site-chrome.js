(function () {
  function relRoot() {
    const p = location.pathname;
    if (p === "/" || p === "/index.html") return "";
    const depth =
      p.replace(/^\//, "").split("/").filter(Boolean).length -
      (p.endsWith(".html") ? 1 : 0);
    return depth > 0 ? "../".repeat(depth) : "";
  }
  const THEME_KEY = "fccf-theme";
  function applyTheme(theme) {
    const next = theme === "dark" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", next);
    document.querySelectorAll("[data-theme-toggle-label]").forEach((el) => {
      el.textContent = next === "dark" ? "Light mode" : "Dark mode";
    });
    document.querySelectorAll("[data-theme-toggle-icon]").forEach((el) => {
      el.textContent = next === "dark" ? "☀️" : "🌙";
    });
  }
  function getPreferredTheme() {
    try {
      const saved = localStorage.getItem(THEME_KEY);
      if (saved === "dark" || saved === "light") return saved;
    } catch (e) {}
    return window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }
  function bindThemeToggles(scope = document) {
    scope.querySelectorAll("[data-theme-toggle]").forEach((el) => {
      if (el.dataset.themeBound === "1") return;
      el.dataset.themeBound = "1";
      el.addEventListener("click", (e) => {
        e.preventDefault();
        const next =
          document.documentElement.getAttribute("data-theme") === "dark"
            ? "light"
            : "dark";
        try {
          localStorage.setItem(THEME_KEY, next);
        } catch (err) {}
        applyTheme(next);
      });
    });
  }
  function bindDescriptionTooltips(scope = document) {
    if (!document.body || document.body.dataset.descTooltipBound === "1") return;
    document.body.dataset.descTooltipBound = "1";
    const tooltip = document.createElement("div");
    tooltip.id = "descTooltip";
    tooltip.className = "desc-popover";
    tooltip.setAttribute("role", "tooltip");
    tooltip.setAttribute("aria-hidden", "true");
    document.body.appendChild(tooltip);
    let active = null;
    let shownAt = 0;
    const targetFromEvent = (e) => e.target.closest("[data-full-desc]");
    const place = (el) => {
      const text = el && el.getAttribute("data-full-desc");
      if (!text) return;
      active = el;
      shownAt = Date.now();
      tooltip.textContent = text;
      tooltip.setAttribute("aria-hidden", "false");
      tooltip.classList.add("show");
      const rect = el.getBoundingClientRect();
      const margin = 14;
      const width = Math.min(520, window.innerWidth - margin * 2);
      tooltip.style.maxWidth = width + "px";
      tooltip.style.left = margin + "px";
      tooltip.style.top = margin + "px";
      const tip = tooltip.getBoundingClientRect();
      const tipWidth = tip.width || width;
      const tipHeight = tip.height || 64;
      let left = Math.min(Math.max(rect.left, margin), window.innerWidth - tipWidth - margin);
      let top = rect.bottom + 8;
      if (top + tipHeight > window.innerHeight - margin) top = rect.top - tipHeight - 8;
      top = Math.min(Math.max(top, margin), Math.max(margin, window.innerHeight - tipHeight - margin));
      tooltip.style.left = left + "px";
      tooltip.style.top = top + "px";
    };
    const hide = () => {
      active = null;
      tooltip.classList.remove("show");
      tooltip.setAttribute("aria-hidden", "true");
    };
    document.addEventListener("mouseover", (e) => {
      const el = targetFromEvent(e);
      if (el) place(el);
    });
    document.addEventListener("focusin", (e) => {
      const el = targetFromEvent(e);
      if (el) place(el);
    });
    document.addEventListener("click", (e) => {
      const el = targetFromEvent(e);
      if (el) {
        e.preventDefault();
        e.stopPropagation();
        place(el);
        return;
      }
      hide();
    }, true);
    document.addEventListener("mouseout", (e) => {
      if (active && e.target.closest("[data-full-desc]") === active && !active.contains(e.relatedTarget)) hide();
    });
    document.addEventListener("focusout", (e) => {
      if (active && e.target.closest("[data-full-desc]") === active) hide();
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") hide();
    });
    window.addEventListener("scroll", () => { if (Date.now() - shownAt > 150) hide(); }, true);
    window.addEventListener("resize", hide);
  }
  function enhanceDescriptionTooltipTargets(scope = document) {
    scope
      .querySelectorAll(".code-card .desc, .code-card .code-desc, .code-card p, td")
      .forEach((el) => {
        if (el.dataset.fullDesc) return;
        const text = (el.textContent || "").trim();
        if (text.length < 42) return;
        el.dataset.fullDesc = text;
        el.setAttribute("title", text);
        el.setAttribute("tabindex", "0");
        el.setAttribute("aria-describedby", "descTooltip");
      });
    bindDescriptionTooltips(scope);
  }
  applyTheme(getPreferredTheme());
  const root = relRoot();
  const path =
    location.pathname.replace(/index\.html$/, "").replace(/\/$/, "") || "/";
  const nav = [
    ["/cpt-code-for/", "CPT Code For"],
    ["/codes/", "Codes"],
    ["/app-productivity.html", "APP"],
    ["/blog/", "Blog"],
    ["/sources.html", "Sources"],
    ["/about.html", "About"],
    ["/contact.html", "Contact"],
    ["/privacy.html", "Privacy"],
    ["/terms.html", "Terms"],
    ["/legal.html", "Legal"],
  ];
  const isActive = (href) =>
    href === "/"
      ? path === "/"
      : path === href.replace(/index\.html$/, "").replace(/\/$/, "") ||
        path.startsWith(href.replace(/index\.html$/, "").replace(/\/$/, ""));
  const navHtml = nav
    .map(
      ([href, label]) =>
        `<a href="${root}${href.replace(/^\//, "")}"${isActive(href) ? ' class="active"' : ""}>${label}</a>`,
    )
    .join("");
  const appModeToggle =
    '<div class="app-mode-toggle" data-app-mode-toggle role="radiogroup" aria-label="Productivity View"><span class="app-mode-toggle__label">Productivity View</span><button type="button" data-app-mode-choice="physician" aria-pressed="true">Physician</button><button type="button" data-app-mode-choice="app" aria-pressed="false">APP</button></div>';
  const themeToggle =
    '<a href="#" class="theme-toggle" data-theme-toggle aria-label="Toggle dark mode"><span class="theme-icon" data-theme-toggle-icon>🌙</span><span data-theme-toggle-label>Dark mode</span></a>';
  const homeHref = root || "/";
  const header = `<header class="hdr"><div class="hdr-top"><div><div class="logo"><svg class="mk" viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true"><path d="M6 6l20 20M11 6h15v15"/><circle cx="8" cy="8" r="2.5"/></svg><div><a class="title" href="${homeHref}" aria-label="Free CPT Code Finder home">Free CPT Code Finder</a><div class="sub"><span>CPT lookup · wRVUs · </span><a href="${root}modifiers.html">modifiers</a><span> · billing guides</span></div></div></div></div><div class="hdr-right"><button class="site-menu-btn" type="button" aria-expanded="false" aria-controls="site-mobile-nav">Menu</button><nav class="topnav" aria-label="Primary">${navHtml}${themeToggle}</nav><div class="header-tools">${appModeToggle}</div><div class="meta"><span>CMS 2026</span><span class="sep"></span><span>CF 32.3465</span><span class="sep"></span><span class="live">live</span></div></div></div><div id="site-mobile-nav" class="site-mobile-nav"><nav class="topnav" aria-label="Mobile primary">${navHtml}${themeToggle}</nav><div class="header-tools mobile">${appModeToggle}</div></div></header>`;
  const footer = `<footer class="site-footer"><div class="site-footer-inner"><div class="site-footer-brand">FreeCPTCodeFinder.com</div><p class="site-footer-copy">FreeCPTCodeFinder.com is an independent educational reference for CPT coding, RVUs, reimbursement, and documentation. Educational information only. Always verify coding, coverage, reimbursement, and compliance decisions with current AMA, CMS, payer, and regulatory guidance.</p><nav class="site-footer-nav" aria-label="Footer"><a href="${homeHref}">Home</a><a href="${root}about.html">About</a><a href="${root}contact.html">Contact</a><a href="${root}privacy.html">Privacy Policy</a><a href="${root}terms.html">Terms of Use</a><a href="${root}legal.html">Legal / CPT Notice</a><a href="${root}editorial-policy.html">Editorial Policy</a><a href="${root}sources.html">Sources</a><a href="${root}sitemap.xml">Sitemap</a><a href="${root}blog/">Blog / Guides</a><a href="${root}codes/">CPT Code Search</a><a href="${root}cpt-code-for/">CPT Code For</a></nav></div></footer>`;
  document.addEventListener("DOMContentLoaded", () => {
    if (!document.querySelector("link[data-fccf-app-mode-css]")) {
      const appCss = document.createElement("link");
      appCss.rel = "stylesheet";
      appCss.href = root + "styles/app-mode.css";
      appCss.dataset.fccfAppModeCss = "1";
      document.head.appendChild(appCss);
    }
    const mountHeader = document.querySelector("[data-site-header]");
    if (mountHeader) mountHeader.innerHTML = header;
    const mountFooter = document.querySelector("[data-site-footer]");
    if (mountFooter) mountFooter.innerHTML = footer;
	    bindThemeToggles(document);
	    enhanceDescriptionTooltipTargets(document);
	    applyTheme(getPreferredTheme());
    const btn = document.querySelector(".site-menu-btn");
    const mobile = document.getElementById("site-mobile-nav");
    if (btn && mobile) {
      btn.addEventListener("click", () => {
        const open = mobile.classList.toggle("open");
        btn.setAttribute("aria-expanded", String(open));
      });
    }
    document
      .querySelectorAll(
        ".header,.cyrionyx-header,.footer,.cyrionyx-footer,.site-footer",
      )
      .forEach((el) => {
        if (
          !el.closest("[data-site-header]") &&
          !el.closest("[data-site-footer]")
        )
          el.classList.add("site-hide-legacy");
      });
    if (!document.querySelector("script[data-fccf-report-widget]")) {
      const reportScript = document.createElement("script");
      reportScript.src = root + "js/report-widget.js";
      reportScript.defer = true;
      reportScript.dataset.fccfReportWidget = "1";
      document.head.appendChild(reportScript);
    }
    if (!document.querySelector("script[data-fccf-app-mode]")) {
      const appScript = document.createElement("script");
      appScript.src = root + "js/app_mode.js";
      appScript.defer = true;
      appScript.dataset.fccfAppMode = "1";
      document.head.appendChild(appScript);
    }
  });
})();
