# FreeCPTCodeFinder Assistant Backend

## Purpose
Node/Express backend for the FreeCPTCodeFinder assistant. It uses OpenAI's Responses API, not the deprecated Assistants API.

## Endpoints
- GET /health - readiness, OpenAI config, CPT rows, report count
- GET /report-tester - staging submission form with a no-PHI warning
- POST /assistant - grounded coding assistant; bug/report language is routed into the report workflow
- POST /reports - structured report intake for CPT errors, Wrong wRVU reports, modifier bugs, missing codes, search problems, and Case Builder issues
- GET /admin/reports?key=... - simple admin dashboard backed by assistant-backend/data/bug_reports.json

## Required OpenAI Tools/Functions
The report workflow exposes these function tools to the Responses API:
- create_bug_report
- create_github_issue
- notify_agent
- attach_page_context
- classify_issue_type
- suggest_fix_for_review

The server also has deterministic local handlers for the same functions so reports still get classified, logged, and review-gated if OpenAI is not configured. The machine classification for Wrong wRVU is wrvu_error.

## Safety Guardrail
The AI may suggest a fix for human review only. Every report includes:
- canCommit: false
- canMerge: false
- canDeploy: false
- humanApprovalRequired: true

No code path commits, merges, pushes, or deploys production changes.

## Environment
~~~bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
ALLOWED_ORIGINS=https://freecptcodefinder.com,https://www.freecptcodefinder.com
ADMIN_REPORTS_KEY=change_me

# Optional delivery
CREATE_GITHUB_ISSUES=false
GITHUB_TOKEN=optional_github_token
GITHUB_REPO=DaVincidigitalbot/free-cpt-code-finder
NOTIFY_EMAIL=developer@example.com
NOTIFY_EMAIL_PROVIDER=resend
RESEND_API_KEY=optional_resend_key
NOTIFY_FROM_EMAIL=FreeCPTCodeFinder <reports@freecptcodefinder.com>
REPORT_RATE_LIMIT_WINDOW_MS=900000
REPORT_RATE_LIMIT_MAX=30
~~~

GitHub issues are created only when CREATE_GITHUB_ISSUES=true and GITHUB_TOKEN is configured. Email notification uses Resend when NOTIFY_EMAIL and RESEND_API_KEY are configured. Otherwise the report is still logged and visible in the admin dashboard.

## Security Notes
- /admin/reports requires ADMIN_REPORTS_KEY when configured.
- /reports is rate limited by REPORT_RATE_LIMIT_WINDOW_MS and REPORT_RATE_LIMIT_MAX.
- User input is sanitized, HTML-escaped in the dashboard, and obvious API tokens/secrets are redacted.
- The tester page and health response warn users not to submit PHI. Use test data or de-identified workflow details only.
- CORS is limited by ALLOWED_ORIGINS.

## Persistence Warning
assistant-backend/data/bug_reports.json is runtime filesystem storage. It is acceptable for staging validation, but it may not survive Render redeploys, restarts, or instance replacement. Production should use persistent storage such as Render PostgreSQL, Supabase Postgres, Neon, or a GitHub Issues-only workflow with the admin dashboard reading from GitHub.

## Example Report Request
~~~json
{
  "description": "CPT 22585 repeats in Case Builder are asking for modifier 59, but it is an add-on code.",
  "pageContext": {
    "pageUrl": "https://freecptcodefinder.com/cpt/22585.html",
    "pageTitle": "CPT 22585",
    "searchQuery": "22585",
    "cptCodes": ["22585"],
    "activeCase": [{"cpt": "22558"}, {"cpt": "22585"}, {"cpt": "22585"}]
  }
}
~~~

## Render Deployment
- Environment: Node
- Root Directory: assistant-backend
- Build Command: npm install
- Start Command: npm start
- Health Check Path: /health
