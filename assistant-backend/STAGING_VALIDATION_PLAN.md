# Staging Validation Plan

## Branch
- staging/responses-report-assistant-2026-06-07
- Production status: not deployed, not merged

## Required Staging Environment
~~~bash
OPENAI_API_KEY=staging_openai_key
OPENAI_MODEL=gpt-4.1-mini
ADMIN_REPORTS_KEY=staging_admin_key
ALLOWED_ORIGINS=https://freecptcodefinder.com,https://www.freecptcodefinder.com,https://freecptcodefinder-assistant-staging.onrender.com
CREATE_GITHUB_ISSUES=false
GITHUB_TOKEN=optional_test_token
GITHUB_REPO=DaVincidigitalbot/free-cpt-code-finder
NOTIFY_EMAIL=optional_test_notification_recipient
NOTIFY_EMAIL_PROVIDER=resend
RESEND_API_KEY=optional_resend_key
NOTIFY_FROM_EMAIL=FreeCPTCodeFinder <reports@freecptcodefinder.com>
REPORT_RATE_LIMIT_WINDOW_MS=900000
REPORT_RATE_LIMIT_MAX=30
~~~

## Staging URLs To Verify
- https://freecptcodefinder-assistant-staging.onrender.com/health
- https://freecptcodefinder-assistant-staging.onrender.com/report-tester
- https://freecptcodefinder-assistant-staging.onrender.com/reports
- https://freecptcodefinder-assistant-staging.onrender.com/admin/reports?key=STAGING_KEY

## Test Matrix
For each test, capture the user submission screenshot, admin dashboard screenshot, generated classification, suggested fix, and safety flags:
- canCommit=false
- canMerge=false
- canDeploy=false
- humanApprovalRequired=true

### A. Wrong WRVU Report
Report: CPT 22585 WRVU appears incorrect.
Expected classification: wrvu_error

### B. Missing CPT Code Report
Report: CPT 20225 is missing.
Expected classification: missing_code

### C. Modifier Logic Bug
Report: Case Builder is incorrectly asking for modifier XS on repeated 22585 add-on codes.
Expected classification: modifier_bug

### D. Search Issue
Report: Searching bone biopsy does not show 20225.
Expected classification: search_problem

### E. Category Placement Issue
Report: 22558 and 22585 should appear under Neurosurgery Spine.
Expected classification: category_placement

## GitHub/Email Workflow
- GitHub issue creation remains off unless CREATE_GITHUB_ISSUES=true and GITHUB_TOKEN are configured in staging.
- Email notification remains off unless NOTIFY_EMAIL and RESEND_API_KEY are configured in staging.
- Use test data only.

## Security Checks
- Confirm /admin/reports returns 401 without ADMIN_REPORTS_KEY.
- Confirm report JSON/dashboard output does not expose OPENAI_API_KEY, GITHUB_TOKEN, RESEND_API_KEY, or other secrets.
- Confirm /health reports limited allowedOrigins.
- Confirm /reports returns rate limit headers and enforces REPORT_RATE_LIMIT_MAX.
- Confirm dashboard output HTML-escapes user input and obvious token patterns are redacted.
- Confirm /report-tester and /health warn not to submit PHI.

## Persistence
Current runtime JSON logging, assistant-backend/data/bug_reports.json, is staging-only. It may not survive Render restarts, redeploys, or instance replacement.

Production storage recommendation:
- Preferred: Render PostgreSQL with a bug_reports table and dashboard queries from Postgres.
- Acceptable lightweight alternative: GitHub Issues as the durable store, with dashboard reading GitHub issues by label.
- Avoid for production: Render local filesystem JSON.

## Production Deployment Plan Draft
- Target: Render web service for assistant-backend, separate from GitHub Pages static site.
- Env vars: same as staging, with production OPENAI_API_KEY, ADMIN_REPORTS_KEY, ALLOWED_ORIGINS, delivery settings, and persistent storage settings.
- Rollback: keep prior Render deployment available and revert service to previous commit; do not touch GitHub Pages during backend rollback.
- Monitoring/logging: Render service logs, /health uptime monitor, report volume/error count, GitHub/email delivery failure count, OpenAI API errors.
- OpenAI cost estimate: report classification/fix suggestion should usually be a few thousand tokens. At low volume, expect pennies to a few dollars monthly; revisit once real report volume is known.
- Initial UI placement candidates: homepage assistant/report entry, CPT code pages, Case Builder right rail, search no-result state, and admin/internal footer link.
