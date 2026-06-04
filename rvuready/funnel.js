(function () {
  document.addEventListener("click", function (event) {
    const link = event.target.closest("[data-rvu-event]");
    if (!link) return;
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ event: link.dataset.rvuEvent, location: "freecpt_rvuready_funnel" });
    if (typeof window.gtag === "function") {
      window.gtag("event", link.dataset.rvuEvent, { location: "freecpt_rvuready_funnel" });
    }
  });
})();
