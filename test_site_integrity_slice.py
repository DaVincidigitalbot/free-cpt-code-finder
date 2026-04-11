from pathlib import Path
import re

ROOT = Path('.').resolve()
HTML_FILES = sorted([p for p in ROOT.rglob('*.html') if '.git' not in p.parts])


def _local_links(path: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', text, re.I)
    for href in hrefs:
        if href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#', 'javascript:', 'data:')):
            continue
        yield href.split('#')[0]


def test_core_pages_exist():
    for rel in ['index.html', 'about.html', 'contact.html', 'outpatient.html', 'blog/index.html', 'privacy.html', 'terms.html', 'favicon.png', 'logo-192.png']:
        assert (ROOT / rel).exists(), rel


def _resolve_local_target(path: Path, href: str) -> Path:
    path_only = href.split('#')[0]
    if href.startswith('/'):
        return (ROOT / path_only.lstrip('/')).resolve()
    return (path.parent / path_only).resolve()


def test_no_dead_internal_links_on_core_pages():
    core = [ROOT / 'index.html', ROOT / 'about.html', ROOT / 'contact.html', ROOT / 'outpatient.html', ROOT / 'blog/index.html', ROOT / 'privacy.html', ROOT / 'terms.html']
    dead = []
    for path in core:
        for href in _local_links(path):
            if not href.split('#')[0]:
                continue
            target = _resolve_local_target(path, href)
            if not target.exists():
                dead.append((str(path), href))
    assert not dead, dead[:50]


def test_no_dead_internal_links_on_priority_blog_pages():
    pages = [
        ROOT / 'blog/index.html',
        ROOT / 'blog/guides/cpt-code-central-line-placement.html',
        ROOT / 'blog/guides/cpt-code-breast-surgery.html',
        ROOT / 'blog/guides/cpt-code-critical-care-billing.html',
        ROOT / 'blog/guides/cpt-code-exploratory-laparotomy.html',
        ROOT / 'blog/guides/cpt-code-ventral-hernia-repair.html',
        ROOT / 'blog/guides/cpt-code-abscess-drainage.html',
        ROOT / 'blog/modifiers/modifier-57-explained.html',
        ROOT / 'blog/rvu/wrvu-breakdown-trauma-laparotomy.html',
    ]
    dead = []
    for path in pages:
        for href in _local_links(path):
            if not href.split('#')[0]:
                continue
            target = _resolve_local_target(path, href)
            if not target.exists():
                dead.append((path.relative_to(ROOT).as_posix(), href))
    assert not dead, dead
