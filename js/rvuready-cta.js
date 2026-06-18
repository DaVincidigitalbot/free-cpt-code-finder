(function () {
  const path = location.pathname.replace(/index\.html$/, "");
  if (
    path.startsWith("/rvuready") ||
    path.startsWith("/admin") ||
    path.startsWith("/privacy") ||
    path.startsWith("/terms") ||
    path.startsWith("/legal") ||
    path.startsWith("/sources") ||
    document.querySelector("[data-rvuready-cta]")
  ) {
    return;
  }

  function relRoot() {
    if (path === "/" || path === "/index.html") return "";
    const depth = location.pathname.replace(/^\//, "").split("/").filter(Boolean).length - (location.pathname.endsWith(".html") ? 1 : 0);
    return depth > 0 ? "../".repeat(depth) : "";
  }

  function sourceLabel() {
    if (path === "/" || path === "/index.html") return "homepage";
    if (path.startsWith("/codes/")) return "cpt-page";
    if (path.startsWith("/modifiers") || path.includes("/modifiers/")) return "modifier-page";
    if (path.startsWith("/coding-centers/")) return "coding-center";
    if (path.includes("orthopedic-hand")) return "orthopedic-hand";
    if (path.startsWith("/blog/")) return "blog";
    return "site-page";
  }

  function trackRvuready(eventType) {
    const payload = {
      eventType,
      sourcePath: path || "/",
      sourcePage: location.href,
      sourceContext: sourceLabel()
    };
    if (typeof gtag === "function") {
      gtag("event", "rvuready_" + eventType, {
        source_path: payload.sourcePath,
        source_context: payload.sourceContext
      });
    }
    const body = JSON.stringify(payload);
    fetch("https://free-cpt-code-finder.onrender.com/rvuready-analytics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      credentials: "omit",
      keepalive: true
    }).catch(function () {});
  }

  function createCta() {
    const root = relRoot();
    const href = root + "rvuready/?source=" + encodeURIComponent(path || "/") + "&context=" + encodeURIComponent(sourceLabel());
    const section = document.createElement("section");
    section.className = "rvuready-inline-cta";
    section.dataset.rvureadyCta = "1";
    section.innerHTML = [
      '<div class="rvuready-inline-cta__copy">',
      '<div class="rvuready-inline-cta__eyebrow">RVUReady beta</div>',
      '<h2>You already did the work. Did your note get credit for it?</h2>',
      '<p>RVUReady helps physicians and APPs identify documentation gaps before the note is signed.</p>',
      '</div>',
      '<div class="rvuready-inline-cta__actions">',
      '<a class="rvuready-inline-cta__button" href="' + href + '">Get founding-user access</a>',
      '<span>Surgeon-built. No PHI required for signup.</span>',
      '</div>'
    ].join("");
    return section;
  }

  function addStyles() {
    if (document.querySelector("style[data-rvuready-cta-style]")) return;
    const style = document.createElement("style");
    style.dataset.rvureadyCtaStyle = "1";
    style.textContent = [
      ".rvuready-inline-cta{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:18px;align-items:center;margin:28px 0;padding:20px;border:1px solid #c7d2fe;background:#eef2ff;color:#0f172a;border-radius:8px}",
      ".rvuready-inline-cta__eyebrow{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:#2563eb;margin-bottom:6px}",
      ".rvuready-inline-cta h2{font-size:22px;line-height:1.2;margin:0 0 8px;color:#0b1f3a}",
      ".rvuready-inline-cta p{margin:0;color:#334155;line-height:1.55}",
      ".rvuready-inline-cta__actions{display:flex;flex-direction:column;gap:8px;align-items:flex-start}",
      ".rvuready-inline-cta__button{display:inline-flex;align-items:center;justify-content:center;min-height:42px;padding:0 14px;background:#0b1f3a;color:white!important;text-decoration:none;border-radius:7px;font-weight:800;white-space:nowrap}",
      ".rvuready-inline-cta__actions span{font-size:12px;color:#475569;max-width:220px;line-height:1.35}",
      "@media(max-width:720px){.rvuready-inline-cta{grid-template-columns:1fr}.rvuready-inline-cta__button{width:100%;box-sizing:border-box}.rvuready-inline-cta h2{font-size:20px}}"
    ].join("");
    document.head.appendChild(style);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const main = document.querySelector("main") || document.querySelector(".main") || document.body;
    if (!main) return;
    addStyles();
    const cta = createCta();
    const anchor = main.querySelector(".content-grid, .blog-list, article, section:last-of-type");
    if (anchor && anchor.parentElement === main) {
      main.insertBefore(cta, anchor.nextSibling);
    } else {
      main.appendChild(cta);
    }
    const ctaLink = cta.querySelector("a");
    if (ctaLink) ctaLink.addEventListener("click", () => trackRvuready("cta_click"));
    if ("IntersectionObserver" in window) {
      const observer = new IntersectionObserver((entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          trackRvuready("cta_impression");
          observer.disconnect();
        }
      }, { threshold: 0.35 });
      observer.observe(cta);
    } else {
      trackRvuready("cta_impression");
    }
  });
})();
