#!/usr/bin/env bash
set -euo pipefail

REPO="/home/setup/Desktop/FreeCPTCodeFinder"
LOG_DIR="/home/setup/.openclaw/workspace/logs/freecpt"
TODAY="$(date +%F)"
LOG_FILE="$LOG_DIR/seo-workflow-$TODAY.log"

mkdir -p "$LOG_DIR"
cd "$REPO"
exec >> "$LOG_FILE" 2>&1

echo "== FreeCPTCodeFinder daily legitimate SEO workflow =="
echo "date: $TODAY"

python3 scripts/seo_enhance_site.py
python3 scripts/daily_seo_report.py

# IndexNow is legitimate index-notification plumbing for supported search engines.
# Google Search Console data is read only when GOOGLE_APPLICATION_CREDENTIALS is configured.
python3 scripts/submit_indexnow.py 100 || true

echo "report: $REPO/seo_reports/daily-seo-report-$TODAY.md"
