#!/usr/bin/env python3
from __future__ import annotations

import html
import re
import subprocess
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')
SITE = 'https://freecptcodefinder.com'
FEED = ROOT / 'feed.xml'
ROBOTS = ROOT / 'robots.txt'

EXCLUDE = {
    'admin.html',
    'blog/template.html',
    'cyrioniq/index.html',
    'index-legacy.html',
    'v2.html',
}

def git_files(*patterns: str) -> list[Path]:
    cmd = ['git', 'ls-files', *patterns]
    out = subprocess.check_output(cmd, cwd=ROOT, text=True)
    return [ROOT / line for line in out.splitlines() if line]

def is_public_html(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    name = path.name
    if rel in EXCLUDE:
        return False
    if rel.startswith('_internal_archive/') or rel.startswith('public/'):
        return False
    if name.startswith(('mockup-', 'test_')) or name in {'modifier_tests.html', 'robotic_test_wrapper.html', 'index-v2-broken.html'}:
        return False
    return path.suffix == '.html'

def text_only(raw: str) -> str:
    raw = re.sub(r'<script[\s\S]*?</script>', ' ', raw, flags=re.I)
    raw = re.sub(r'<style[\s\S]*?</style>', ' ', raw, flags=re.I)
    raw = re.sub(r'<[^>]+>', ' ', raw)
    raw = re.sub(r'\s+', ' ', raw)
    return html.unescape(raw).strip()

def title_for(raw: str, fallback: str) -> str:
    h1 = re.search(r'<h1[^>]*>([\s\S]*?)</h1>', raw, flags=re.I)
    if h1:
        return text_only(h1.group(1))
    title = re.search(r'<title>([\s\S]*?)</title>', raw, flags=re.I)
    return text_only(title.group(1)) if title else fallback

def desc_for(raw: str) -> str:
    meta = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)', raw, flags=re.I)
    if meta:
        return html.unescape(meta.group(1)).strip()
    body = text_only(raw)
    return body[:220].strip()

def url_for(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == 'index.html':
        return SITE + '/'
    if rel.endswith('/index.html'):
        return SITE + '/' + rel[:-10]
    return SITE + '/' + rel

def build_feed() -> None:
    blog_files = [p for p in git_files('blog/**/*.html') if p.exists() and is_public_html(p) and p.name != 'index.html']
    blog_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    items = []
    for path in blog_files[:50]:
        raw = path.read_text()
        title = title_for(raw, path.stem.replace('-', ' ').title())
        desc = desc_for(raw)
        pub = format_datetime(datetime.fromtimestamp(path.stat().st_mtime, timezone.utc))
        url = url_for(path)
        items.append(f'''    <item>
      <title>{html.escape(title)}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{pub}</pubDate>
      <description>{html.escape(desc)}</description>
    </item>''')
    updated = format_datetime(datetime.now(timezone.utc))
    FEED.write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Free CPT Code Finder Blog</title>
    <link>{SITE}/blog/</link>
    <description>Daily CPT coding, modifier, ICD-10, wRVU, and surgical billing education from Free CPT Code Finder.</description>
    <language>en-us</language>
    <lastBuildDate>{updated}</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
''')

def update_robots() -> None:
    text = ROBOTS.read_text() if ROBOTS.exists() else 'User-agent: *\nAllow: /\n'
    required = [
        'Sitemap: https://freecptcodefinder.com/sitemap.xml',
        'Sitemap: https://freecptcodefinder.com/feed.xml',
    ]
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    for line in required:
        if line not in lines:
            lines.append(line)
    ROBOTS.write_text('\n'.join(lines) + '\n')

def add_feed_discovery(path: Path) -> None:
    raw = path.read_text()
    if 'application/rss+xml' in raw:
        return
    link = '<link rel="alternate" type="application/rss+xml" title="Free CPT Code Finder Blog" href="https://freecptcodefinder.com/feed.xml">'
    raw = raw.replace('</head>', link + '\n</head>', 1)
    path.write_text(raw)

def main() -> None:
    build_feed()
    update_robots()
    for rel in ['index.html', 'blog/index.html']:
        path = ROOT / rel
        if path.exists():
            add_feed_discovery(path)
    print('Generated feed.xml, robots.txt, and RSS discovery links')

if __name__ == '__main__':
    main()
