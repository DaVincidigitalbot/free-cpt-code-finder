#!/usr/bin/env bash
set -euo pipefail

REPO="/home/setup/Desktop/FreeCPTCodeFinder"
LOG_DIR="/home/setup/.openclaw/workspace/logs/freecpt"
LOG_FILE="$LOG_DIR/resident-operative-notes-publish-2026-05-30.log"
SLUG="teaching-residents-operative-notes"
DRAFT="scheduled-posts/$SLUG.html"
TARGET="blog/guides/$SLUG.html"
URL="https://freecptcodefinder.com/$TARGET"

mkdir -p "$LOG_DIR"
cd "$REPO"
exec >> "$LOG_FILE" 2>&1

echo "== Scheduled FreeCPTCodeFinder post: resident operative notes =="
date -Is

if [[ -f "$TARGET" ]]; then
  echo "Target already exists: $TARGET"
else
  if [[ ! -f "$DRAFT" ]]; then
    echo "Missing draft: $DRAFT"
    exit 2
  fi
  mv "$DRAFT" "$TARGET"
  echo "Moved $DRAFT -> $TARGET"
fi

python3 - <<'PY'
from pathlib import Path
from email.utils import formatdate
import time
import re

repo = Path('/home/setup/Desktop/FreeCPTCodeFinder')
slug = 'teaching-residents-operative-notes'
target = f'blog/guides/{slug}.html'
url = f'https://freecptcodefinder.com/{target}'
title = 'Teaching Residents to Write Better Operative Notes'
description = "An attending surgeon's practical framework for teaching residents to write better operative notes, document complexity, and understand the purpose of surgical documentation."

index = repo / 'blog/index.html'
html = index.read_text()
card = '''            <a href="/blog/guides/teaching-residents-operative-notes.html" class="article-card">
                <span class="category cat-guide">Documentation</span>
                <h2>Teaching Residents to Write Better Operative Notes</h2>
                <p>An attending surgeon's framework for teaching residents to write operative notes that are clinically useful, complete, and defensible.</p>
                <div class="meta">Graydon Stallard, DO, FACOS, FACS &middot; May 2026</div>
            </a>

'''
if '/blog/guides/teaching-residents-operative-notes.html' not in html:
    html = html.replace('        <div class="articles">\n\n', '        <div class="articles">\n\n' + card, 1)
    index.write_text(html)
    print('blog index updated')
else:
    print('blog index already contains post')

sitemap = repo / 'sitemap.xml'
xml = sitemap.read_text()
entry = '''  <url>
    <loc>https://freecptcodefinder.com/blog/guides/teaching-residents-operative-notes.html</loc>
    <lastmod>2026-05-30</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.82</priority>
  </url>
'''
if url not in xml:
    xml = xml.replace('</urlset>', entry + '</urlset>', 1)
    sitemap.write_text(xml)
    print('sitemap updated')
else:
    print('sitemap already contains post')

feed = repo / 'feed.xml'
rss = feed.read_text()
now = formatdate(time.time(), usegmt=True)
item = f'''    <item>
      <title>{title}</title>
      <link>{url}</link>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{now}</pubDate>
      <description>{description}</description>
    </item>
'''
if url not in rss:
    rss = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{now}</lastBuildDate>', rss, count=1)
    rss = rss.replace('    <item>\n', item + '    <item>\n', 1)
    feed.write_text(rss)
    print('feed updated')
else:
    print('feed already contains post')
PY

python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse('sitemap.xml')
ET.parse('feed.xml')
print('xml ok')
PY

changed="$(git status --porcelain -- "$TARGET" blog/index.html sitemap.xml feed.xml)"
if [[ -z "$changed" ]]; then
  echo "No changes to commit."
else
  git add "$TARGET" blog/index.html sitemap.xml feed.xml
  git commit -m "Publish resident operative note documentation guide" -- "$TARGET" blog/index.html sitemap.xml feed.xml
  git push origin main
fi

for i in {1..20}; do
  code="$(curl -L -s -o /tmp/freecpt_resident_operative_notes.html -w '%{http_code}' "$URL" || true)"
  title_count="$(grep -c 'Teaching Residents to Write Better Operative Notes' /tmp/freecpt_resident_operative_notes.html || true)"
  echo "live_check attempt=$i code=$code title_count=$title_count"
  if [[ "$code" == "200" && "$title_count" != "0" ]]; then
    python3 scripts/submit_indexnow.py 100 || true
    echo "live verified: $URL"
    exit 0
  fi
  sleep 30
done

echo "Publish ran, but live verification timed out: $URL"
exit 4
