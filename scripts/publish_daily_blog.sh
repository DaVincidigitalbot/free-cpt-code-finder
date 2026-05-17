#!/usr/bin/env bash
set -euo pipefail

REPO="/home/setup/Desktop/FreeCPTCodeFinder"
LOG_DIR="/home/setup/.openclaw/workspace/logs/freecpt"
TODAY="$(date +%F)"
LOG_FILE="$LOG_DIR/daily-blog-$TODAY.log"

mkdir -p "$LOG_DIR"
cd "$REPO"
exec >> "$LOG_FILE" 2>&1

echo "== FreeCPTCodeFinder daily blog publish =="
echo "date: $TODAY"
echo "repo: $REPO"

TOPICS=(
  "trauma-laparotomy-cpt-guide"
  "icd10-postop-complications-guide"
  "modifier-24-postop-em"
  "rvu-90-day-global-surprises"
)

published=""
for topic in "${TOPICS[@]}"; do
  section="$(python3 - "$topic" <<'PY'
import sys
sys.path.insert(0, 'scripts')
import generate_daily_blog
print(generate_daily_blog.TOPICS[sys.argv[1]].section)
PY
)"
  slug="$(python3 - "$topic" <<'PY'
import sys
sys.path.insert(0, 'scripts')
import generate_daily_blog
print(generate_daily_blog.TOPICS[sys.argv[1]].slug)
PY
)"
  target="blog/$section/$slug.html"
  if [[ ! -f "$target" ]]; then
    python3 scripts/generate_daily_blog.py --topic "$topic" --publish
    published="$target"
    break
  fi
done

if [[ -z "$published" ]]; then
  echo "No unpublished generator topics remain. Add topics to scripts/generate_daily_blog.py."
  exit 2
fi

ADSENSE='<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3385830962144023" crossorigin="anonymous"></script>'
if ! grep -q 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' "$published"; then
  python3 - "$published" "$ADSENSE" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
ads = sys.argv[2]
html = path.read_text()
html = html.replace('</head>', ads + '\n</head>', 1)
path.write_text(html)
PY
fi

if ! grep -q 'Last reviewed:' "$published"; then
  python3 - "$published" <<'PY'
from pathlib import Path
import sys
path = Path(sys.argv[1])
html = path.read_text()
html = html.replace('</h1>', '</h1>\n<p class="last-updated">Last reviewed: May 2026</p>', 1)
path.write_text(html)
PY
fi

python3 - <<'PY'
import xml.etree.ElementTree as ET
ET.parse('sitemap.xml')
print('sitemap xml ok')
PY

python3 scripts/generate_seo_assets.py

if ! grep -q 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' "$published"; then
  echo "AdSense script missing from $published"
  exit 3
fi

git add "$published" blog/index.html sitemap.xml feed.xml robots.txt index.html
git commit -m "Publish daily FreeCPTCodeFinder blog: $(basename "$published" .html)"
git push origin main

url="https://freecptcodefinder.com/${published}"
echo "published: $published"
echo "url: $url"

for i in {1..12}; do
  code="$(curl -L -s -o /tmp/freecpt_daily_blog.html -w '%{http_code}' "$url" || true)"
  has_ads="$(grep -c 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' /tmp/freecpt_daily_blog.html || true)"
  echo "live_check attempt=$i code=$code ads=$has_ads"
  if [[ "$code" == "200" && "$has_ads" != "0" ]]; then
    echo "live verified"
    exit 0
  fi
  sleep 15
done

echo "published but live verification timed out"
exit 4
