#!/usr/bin/env python3
"""Visual guardrail for Cardiac Electrophysiology category cards."""

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8134"
OUT = Path("qa_artifacts/ep_card_audit")
OUT.mkdir(parents=True, exist_ok=True)


def audit_viewport(page, name, width, height):
    page.set_viewport_size({"width": width, "height": height})
    page.goto(f"{BASE_URL}/categories/cardiac-electrophysiology.html", wait_until="domcontentloaded")
    page.wait_for_timeout(1000)
    page.screenshot(path=str(OUT / f"{name}.png"), full_page=True)
    return page.evaluate(
        r"""() => {
          const failures = [];
          const cards = [...document.querySelectorAll('.code-card')];
          for (const card of cards) {
            const cardRect = card.getBoundingClientRect();
            const desc = card.querySelector('.code-desc');
            const descRect = desc ? desc.getBoundingClientRect() : {width: 0, height: 0};
            const badges = [...card.querySelectorAll('.wrvu-pill,.flag')];
            const badgeSpills = badges.filter((badge) => {
              const r = badge.getBoundingClientRect();
              return r.left < cardRect.left - 1 || r.right > cardRect.right + 1 || r.top < cardRect.top - 1 || r.bottom > cardRect.bottom + 1;
            }).map((badge) => badge.textContent.trim());
            const ratio = cardRect.height / Math.max(cardRect.width, 1);
            const text = card.textContent.trim().replace(/\s+/g, ' ').slice(0, 120);
            if (cardRect.height > 300) failures.push({text, reason: 'card-height', height: cardRect.height, width: cardRect.width});
            if (descRect.width < 140) failures.push({text, reason: 'description-width', descWidth: descRect.width});
            if (ratio > 0.95 && cardRect.height > 180) failures.push({text, reason: 'tall-skinny-ratio', ratio, height: cardRect.height, width: cardRect.width});
            if (badgeSpills.length) failures.push({text, reason: 'badge-spill', badgeSpills});
          }
          return {
            name: document.title,
            viewport: [window.innerWidth, window.innerHeight],
            cardCount: cards.length,
            failures,
            maxCardHeight: Math.max(...cards.map((card) => card.getBoundingClientRect().height)),
            minDescriptionWidth: Math.min(...cards.map((card) => card.querySelector('.code-desc')?.getBoundingClientRect().width || 0))
          };
        }"""
    )


def main():
    report = {"baseUrl": BASE_URL, "viewports": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path="/usr/bin/google-chrome")
        page = browser.new_page()
        for args in [
            ("desktop", 1440, 1000),
            ("tablet", 820, 1000),
            ("mobile", 390, 900),
        ]:
            report["viewports"].append(audit_viewport(page, *args))
        browser.close()
    (OUT / "ep_card_audit_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    failures = [failure for viewport in report["viewports"] for failure in viewport["failures"]]
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
