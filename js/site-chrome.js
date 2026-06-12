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
  applyTheme(getPreferredTheme());
  const root = relRoot();
  const path =
    location.pathname.replace(/index\.html$/, "").replace(/\/$/, "") || "/";
  const nav = [
    ["/cpt-code-for/", "CPT Code For"],
    ["/codes/", "Codes"],
    ["/rvuready/", "RVUReady"],
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
    if (!document.querySelector("script[data-fccf-rvuready-cta]")) {
      const rvuScript = document.createElement("script");
      rvuScript.src = root + "js/rvuready-cta.js";
      rvuScript.defer = true;
      rvuScript.dataset.fccfRvureadyCta = "1";
      document.head.appendChild(rvuScript);
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
