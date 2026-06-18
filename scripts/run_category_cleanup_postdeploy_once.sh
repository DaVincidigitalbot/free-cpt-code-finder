#!/usr/bin/env bash
set -u

MARKER="CATEGORY_CLEANUP_POSTDEPLOY_20260618"
ROOT="/tmp/freecpt-category-cleanup"
OUT_DIR="$ROOT/audit_reports/category_cleanup_postdeploy_2026-06-18"
LOG="$OUT_DIR/cron.log"

cleanup_cron() {
  crontab -l 2>/dev/null | grep -v "$MARKER" | crontab - 2>/dev/null || true
}
trap cleanup_cron EXIT

mkdir -p "$OUT_DIR"
cd "$ROOT" || exit 1

{
  echo "category cleanup postdeploy crawl started $(date -Is)"
  git fetch origin main
  git reset --hard origin/main
  NODE_PATH=/home/setup/.npm/_npx/e41f203b7505f1fb/node_modules node scripts/post_deploy_category_cleanup_crawl.js
  status=$?
  echo "category cleanup postdeploy crawl exit status $status $(date -Is)"
  git add -f audit_reports/category_cleanup_postdeploy_2026-06-18 || true
  git commit -m "Archive category cleanup postdeploy crawl" || true
  git push origin HEAD:main || true
  exit "$status"
} >"$LOG" 2>&1
