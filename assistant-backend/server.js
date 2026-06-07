import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import rateLimit from 'express-rate-limit';
import OpenAI from 'openai';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const cptDbPath = path.join(projectRoot, 'cpt_database.json');
const dataDir = path.join(__dirname, 'data');
const reportLogPath = path.join(dataDir, 'bug_reports.json');
const openai = process.env.OPENAI_API_KEY ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY }) : null;
const app = express();
const allowedOrigins = (process.env.ALLOWED_ORIGINS || 'https://freecptcodefinder.com,https://www.freecptcodefinder.com').split(',').map(s => s.trim()).filter(Boolean);
const adminReportsKey = process.env.ADMIN_REPORTS_KEY || process.env.ADMIN_DASHBOARD_KEY;
const notifyEmail = process.env.NOTIFY_EMAIL || process.env.DEVELOPER_EMAIL;
const notifyEmailProvider = process.env.NOTIFY_EMAIL_PROVIDER || 'resend';
const reportFromEmail = process.env.NOTIFY_FROM_EMAIL || process.env.REPORT_FROM_EMAIL || 'FreeCPTCodeFinder <reports@freecptcodefinder.com>';
const githubRepo = process.env.GITHUB_REPO || 'DaVincidigitalbot/free-cpt-code-finder';
const githubToken = process.env.GITHUB_TOKEN;
const githubIssuesEnabled = process.env.CREATE_GITHUB_ISSUES === 'true';
const githubIssuesDurableStore = process.env.GITHUB_ISSUES_DURABLE_STORE === 'true';
const reportRateLimit = rateLimit({
  windowMs: Number(process.env.REPORT_RATE_LIMIT_WINDOW_MS || 15 * 60 * 1000),
  max: Number(process.env.REPORT_RATE_LIMIT_MAX || 30),
  standardHeaders: true,
  legacyHeaders: false
});

app.use(cors({ origin(origin, callback) { if (!origin || allowedOrigins.includes(origin)) return callback(null, true); return callback(null, false); } }));
app.use(express.json({ limit: '1mb' }));

let cptDb = [];
try {
  const rawDb = JSON.parse(fs.readFileSync(cptDbPath, 'utf8'));
  cptDb = Array.isArray(rawDb) ? rawDb : Object.values(rawDb || {});
} catch (err) {
  console.error('Failed to load CPT database', err);
}

function ensureDataDir() {
  fs.mkdirSync(dataDir, { recursive: true });
  if (!fs.existsSync(reportLogPath)) fs.writeFileSync(reportLogPath, '[]\n');
}

function loadReports() {
  ensureDataDir();
  try {
    const parsed = JSON.parse(fs.readFileSync(reportLogPath, 'utf8'));
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveReport(report) {
  const reports = loadReports();
  reports.unshift(report);
  fs.writeFileSync(reportLogPath, JSON.stringify(reports.slice(0, 1000), null, 2) + '\n');
}

function sanitizeText(value, maxLength = 2000) {
  return String(value ?? '')
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '')
    .replace(/\b(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9_]{20,}|re_[A-Za-z0-9_]{20,})\b/g, '[redacted_secret]')
    .replace(/\b\d{3}-\d{2}-\d{4}\b/g, '[redacted_ssn]')
    .trim()
    .slice(0, maxLength);
}

function sanitizeStringArray(values, maxItems = 20, maxLength = 200) {
  if (!Array.isArray(values)) return [];
  return values.slice(0, maxItems).map(value => sanitizeText(value, maxLength)).filter(Boolean);
}

function sanitizeObject(value, depth = 0) {
  if (depth > 4) return '[truncated]';
  if (Array.isArray(value)) return value.slice(0, 30).map(item => sanitizeObject(item, depth + 1));
  if (value && typeof value === 'object') {
    const out = {};
    for (const [key, item] of Object.entries(value)) {
      if (/api[_-]?key|token|secret|password|authorization/i.test(key)) {
        out[key] = '[redacted_secret]';
      } else {
        out[key] = sanitizeObject(item, depth + 1);
      }
    }
    return out;
  }
  if (typeof value === 'string') return sanitizeText(value, 1000);
  return value;
}

function searchCpt(query, limit = 8) {
  const q = String(query || '').toLowerCase().trim();
  if (!q || !Array.isArray(cptDb)) return [];
  const scored = cptDb.map(item => {
    const code = String(item.code || '');
    const desc = String(item.description || '');
    let score = 0;
    if (code === q) score += 100;
    if (code.startsWith(q)) score += 40;
    if (desc.toLowerCase().includes(q)) score += 25;
    for (const token of q.split(/\s+/)) if (desc.toLowerCase().includes(token)) score += 5;
    return { item, score };
  }).filter(x => x.score > 0).sort((a, b) => b.score - a.score).slice(0, limit);
  return scored.map(({ item }) => ({ code: item.code, description: item.description, wrvu: item.work_rvu ?? item.wrvu ?? null, globalDays: item.global_days ?? item.global ?? null, category: item.category ?? null }));
}

function classifyIssueType({ description = '', reportedType = '' }) {
  const text = (reportedType + ' ' + description).toLowerCase();
  if (/w\s*rvu|rvu|work\s*rvu|medicare|payment/.test(text)) return 'wrvu_error';
  if (/modifier|mod\s?\d+|-\d{2}|x[epsu]|59|80|62|51/.test(text)) return 'modifier_bug';
  if (/category|placement|specialty|section|taxonomy|under neurosurgery|under spine/.test(text)) return 'category_placement';
  if (/search|autocomplete|result|finding|query/.test(text)) return 'search_problem';
  if (/missing|add code|not listed|absent|can't find code/.test(text)) return 'missing_code';
  if (/case builder|builder|case line|duplicate|bundle|mppr|ncci/.test(text)) return 'case_builder_issue';
  if (/cpt|description|wrong code|incorrect code|taxonomy|specialty/.test(text)) return 'cpt_error';
  return 'other';
}

function attachPageContext(args = {}) {
  const cleanArgs = sanitizeObject(args);
  const codes = sanitizeStringArray(cleanArgs.cptCodes, 12, 20);
  const query = [cleanArgs.searchQuery, cleanArgs.pageUrl, cleanArgs.description, ...codes].filter(Boolean).join(' ');
  return {
    pageUrl: sanitizeText(cleanArgs.pageUrl || '', 500) || null,
    pageTitle: sanitizeText(cleanArgs.pageTitle || '', 200) || null,
    searchQuery: sanitizeText(cleanArgs.searchQuery || '', 200) || null,
    cptCodes: codes,
    browser: sanitizeText(cleanArgs.browser || '', 200) || null,
    viewport: sanitizeText(cleanArgs.viewport || '', 100) || null,
    activeCase: Array.isArray(cleanArgs.activeCase) ? cleanArgs.activeCase.slice(0, 30) : [],
    likelyMatches: searchCpt(query, 10)
  };
}

function suggestFixForReview(args = {}) {
  const issueType = args.issueType || 'other';
  const codes = Array.isArray(args.cptCodes) ? args.cptCodes : [];
  const guidance = {
    cpt_error: 'Review CPT description, specialty taxonomy, code page content, inline CPT_DATA, and cpt_decision_tree.json for sync drift.',
    wrvu_error: 'Verify work RVU, total RVU, global period, MPPR behavior, and Medicare estimate against the current CMS physician fee schedule.',
    modifier_bug: 'Reproduce in Case Builder, then inspect modifier_engine_enhanced.js, enhanced_billing.js, and related Case Builder UI state.',
    missing_code: 'Add the CPT row to the canonical database, generated pages, specialty/category indexes, search data, sitemap, and inline CPT_DATA if applicable.',
    search_problem: 'Check search aliases, specialty hierarchy, tokenization, and generated index coverage for the reported query.',
    category_placement: 'Review specialty/category placement in specialty_hierarchy.json, generated category pages, code pages, search filters, and cpt_decision_tree.json.',
    case_builder_issue: 'Reproduce with the reported active case, then inspect duplicate/add-on handling, modifier prompts, MPPR math, and right-rail rendering.'
  };
  return {
    summary: (guidance[issueType] || 'Triage the report against the reported page context and current CPT database.') + (codes.length ? ' Review CPT ' + codes.join(', ') + ' against source data.' : ''),
    reviewOnly: true,
    prohibitedActions: ['commit', 'merge', 'push', 'deploy'],
    approvalRequiredBeforeCodeChange: true
  };
}

function issueLabel(issueType) {
  return ({
    wrvu_error: 'Wrong wRVU',
    cpt_error: 'CPT Error',
    modifier_bug: 'Modifier Bug',
    missing_code: 'Missing CPT Code',
    search_problem: 'Search Issue',
    category_placement: 'Category Placement Issue',
    case_builder_issue: 'Case Builder Issue',
    other: 'Other Report'
  })[issueType] || issueType.replace(/_/g, ' ');
}

function buildBugReport(args = {}) {
  args = sanitizeObject(args);
  const now = new Date().toISOString();
  const context = attachPageContext(args.pageContext || args);
  const issueType = args.issueType || classifyIssueType({ description: args.description || args.summary || '', reportedType: args.reportedType || '' });
  return {
    id: 'FCCF-' + now.slice(0, 10).replace(/-/g, '') + '-' + crypto.randomBytes(3).toString('hex').toUpperCase(),
    createdAt: now,
    status: 'new',
    issueType,
    issueLabel: issueLabel(issueType),
    severity: args.severity || 'needs_triage',
    title: sanitizeText(args.title || issueType.replace(/_/g, ' ') + ' report', 160),
    summary: sanitizeText(args.summary || args.description || '', 2000),
    description: sanitizeText(args.description || '', 4000),
    expectedBehavior: sanitizeText(args.expectedBehavior || '', 2000),
    actualBehavior: sanitizeText(args.actualBehavior || '', 2000),
    reproductionSteps: sanitizeStringArray(args.reproductionSteps, 12, 500),
    cptCodes: Array.isArray(args.cptCodes) ? sanitizeStringArray(args.cptCodes, 20, 20) : context.cptCodes,
    reporter: { name: sanitizeText(args.reporterName || '', 100), email: sanitizeText(args.reporterEmail || '', 200) },
    pageContext: context,
    suggestedFix: args.suggestedFix || null,
    delivery: { githubIssueUrl: null, emailSent: false, agentNotified: false, errors: [] },
    safety: { canSuggestFix: true, canCommit: false, canMerge: false, canDeploy: false, humanApprovalRequired: true }
  };
}

function markOpenAiFallback(report, err) {
  report.ai = {
    provider: 'openai_responses_api',
    used: false,
    error: sanitizeText(err?.message || err || 'OpenAI Responses API call failed', 500)
  };
  report.delivery.errors.push('OpenAI Responses API unavailable; deterministic fallback classification used');
  return report;
}

async function createGithubIssue(report) {
  if (!githubIssuesEnabled) return { skipped: true, reason: 'CREATE_GITHUB_ISSUES is not true' };
  if (!githubToken) return { skipped: true, reason: 'GITHUB_TOKEN is not set' };
  await ensureGithubLabels(['user-report', report.issueType]);
  const body = [
    '<!-- FREECPT_REPORT_JSON_START',
    JSON.stringify(report, null, 2),
    'FREECPT_REPORT_JSON_END -->',
    '',
    'Report ID: ' + report.id,
    'Type: ' + report.issueType,
    'Label: ' + (report.issueLabel || issueLabel(report.issueType)),
    'Severity: ' + report.severity,
    '',
    '## Summary',
    report.summary || report.description || '(none)',
    '',
    '## Expected',
    report.expectedBehavior || '(not provided)',
    '',
    '## Actual',
    report.actualBehavior || '(not provided)',
    '',
    '## Reproduction Steps',
    report.reproductionSteps.length ? report.reproductionSteps.map((s, i) => String(i + 1) + '. ' + s).join('\n') : '(not provided)',
    '',
    '## Page Context',
    '~~~json',
    JSON.stringify(report.pageContext, null, 2),
    '~~~',
    '',
    '## Suggested Fix For Human Review',
    report.suggestedFix?.summary || '(none)',
    '',
    'Safety: AI may suggest a fix only. No autonomous commit, merge, push, or deploy.'
  ].join('\n');
  const response = await githubFetch('/issues', {
    method: 'POST',
    body: JSON.stringify({ title: '[freecpt-report][' + report.issueType + '] ' + report.title, body, labels: ['user-report', report.issueType] })
  });
  const json = await response.json();
  if (!response.ok) throw new Error(json.message || 'GitHub issue creation failed (' + response.status + ')');
  return { url: json.html_url, number: json.number };
}

async function githubFetch(pathname, options = {}) {
  const response = await fetch('https://api.github.com/repos/' + githubRepo + pathname, {
    ...options,
    headers: {
      Authorization: 'Bearer ' + githubToken,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });
  return response;
}

async function ensureGithubLabels(labels) {
  for (const name of labels) {
    const safeName = sanitizeText(name, 50);
    if (!safeName) continue;
    const check = await githubFetch('/labels/' + encodeURIComponent(safeName));
    if (check.ok) continue;
    const color = safeName === 'user-report' ? '2563eb' : '64748b';
    const created = await githubFetch('/labels', {
      method: 'POST',
      body: JSON.stringify({ name: safeName, color, description: 'FreeCPTCodeFinder report intake label' })
    });
    if (!created.ok && created.status !== 422) {
      const json = await created.json().catch(() => ({}));
      throw new Error(json.message || 'GitHub label creation failed (' + created.status + ')');
    }
  }
}

async function listGithubIssueReports() {
  if (!githubIssuesDurableStore || !githubToken) return [];
  const response = await githubFetch('/issues?state=open&labels=user-report&per_page=100&sort=created&direction=desc');
  const issues = await response.json();
  if (!response.ok) throw new Error(issues.message || 'GitHub issue report list failed (' + response.status + ')');
  return issues.map(issue => reportFromGithubIssue(issue)).filter(Boolean);
}

function reportFromGithubIssue(issue) {
  const body = String(issue.body || '');
  const match = body.match(/FREECPT_REPORT_JSON_START\n([\s\S]*?)\nFREECPT_REPORT_JSON_END/);
  if (match) {
    try {
      const report = JSON.parse(match[1]);
      report.delivery = report.delivery || {};
      report.delivery.githubIssueUrl = issue.html_url;
      report.github = { issueNumber: issue.number, state: issue.state, url: issue.html_url };
      return report;
    } catch {}
  }
  const label = (issue.labels || []).map(l => l.name).find(name => name !== 'user-report') || 'other';
  return {
    id: 'GH-' + issue.number,
    createdAt: issue.created_at,
    status: issue.state,
    issueType: label,
    issueLabel: issueLabel(label),
    severity: 'needs_triage',
    title: issue.title,
    summary: body.slice(0, 500),
    cptCodes: [],
    delivery: { githubIssueUrl: issue.html_url, errors: [] },
    suggestedFix: { summary: 'Review GitHub issue body.', reviewOnly: true },
    safety: { canSuggestFix: true, canCommit: false, canMerge: false, canDeploy: false, humanApprovalRequired: true },
    github: { issueNumber: issue.number, state: issue.state, url: issue.html_url }
  };
}

async function notifyAgent(report) {
  const emailTo = notifyEmail;
  const resendKey = process.env.RESEND_API_KEY;
  if (notifyEmailProvider !== 'resend') return { skipped: true, reason: 'Only Resend notification provider is implemented' };
  if (!emailTo || !resendKey) return { skipped: true, reason: 'NOTIFY_EMAIL/DEVELOPER_EMAIL or RESEND_API_KEY is not set' };
  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: 'Bearer ' + resendKey, 'Content-Type': 'application/json' },
    body: JSON.stringify({ from: reportFromEmail, to: [emailTo], subject: '[FreeCPT Report] ' + report.issueType + ': ' + report.title, text: JSON.stringify(report, null, 2) })
  });
  const json = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(json.message || 'Email notification failed (' + response.status + ')');
  return { sent: true, id: json.id || null };
}

const reportTools = [
  { type: 'function', name: 'create_bug_report', description: 'Create the structured FreeCPTCodeFinder report object to log in the admin dashboard.', parameters: { type: 'object', additionalProperties: false, properties: { title: { type: 'string' }, summary: { type: 'string' }, description: { type: 'string' }, issueType: { type: 'string' }, severity: { type: 'string' }, expectedBehavior: { type: ['string', 'null'] }, actualBehavior: { type: ['string', 'null'] }, reproductionSteps: { type: 'array', items: { type: 'string' } }, cptCodes: { type: 'array', items: { type: 'string' } }, reporterName: { type: ['string', 'null'] }, reporterEmail: { type: ['string', 'null'] }, pageContext: { type: 'object', additionalProperties: true }, suggestedFix: { type: ['object', 'null'], additionalProperties: true } }, required: ['title', 'summary', 'description', 'issueType', 'severity', 'expectedBehavior', 'actualBehavior', 'reproductionSteps', 'cptCodes', 'reporterName', 'reporterEmail', 'pageContext', 'suggestedFix'] } },
  { type: 'function', name: 'create_github_issue', description: 'Create a GitHub issue for the completed report when GitHub delivery is configured.', parameters: { type: 'object', additionalProperties: false, properties: { reportId: { type: 'string' } }, required: ['reportId'] } },
  { type: 'function', name: 'notify_agent', description: 'Send a structured email notification to the developer or agent when email delivery is configured.', parameters: { type: 'object', additionalProperties: false, properties: { reportId: { type: 'string' } }, required: ['reportId'] } },
  { type: 'function', name: 'attach_page_context', description: 'Attach page, query, CPT codes, browser, viewport, and active Case Builder context to a report.', parameters: { type: 'object', additionalProperties: false, properties: { pageUrl: { type: ['string', 'null'] }, pageTitle: { type: ['string', 'null'] }, searchQuery: { type: ['string', 'null'] }, cptCodes: { type: 'array', items: { type: 'string' } }, browser: { type: ['string', 'null'] }, viewport: { type: ['string', 'null'] }, activeCase: { type: 'array', items: { type: 'object', additionalProperties: true } }, description: { type: ['string', 'null'] } }, required: ['pageUrl', 'pageTitle', 'searchQuery', 'cptCodes', 'browser', 'viewport', 'activeCase', 'description'] } },
  { type: 'function', name: 'classify_issue_type', description: 'Classify report into cpt_error, wrvu_error (user-facing label: Wrong wRVU), modifier_bug, missing_code, search_problem, category_placement, case_builder_issue, or other.', parameters: { type: 'object', additionalProperties: false, properties: { description: { type: 'string' }, reportedType: { type: ['string', 'null'] } }, required: ['description', 'reportedType'] } },
  { type: 'function', name: 'suggest_fix_for_review', description: 'Suggest a possible fix for human review only. Never commit, merge, push, or deploy.', parameters: { type: 'object', additionalProperties: false, properties: { issueType: { type: 'string' }, cptCodes: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } }, required: ['issueType', 'cptCodes', 'summary'] } }
];

async function runReportPipeline(input) {
  input = sanitizeObject(input);
  const description = sanitizeText(input.description || input.message || input.question || '', 4000);
  const pageContext = attachPageContext({ ...(input.pageContext || {}), description });
  const issueType = classifyIssueType({ description, reportedType: input.issueType || '' });
  const suggestedFix = suggestFixForReview({ issueType, cptCodes: input.cptCodes || pageContext.cptCodes || [], summary: description });
  let report = buildBugReport({ title: input.title || description.slice(0, 90) || 'FreeCPTCodeFinder user report', summary: input.summary || description, description, issueType, severity: input.severity || 'needs_triage', expectedBehavior: input.expectedBehavior || '', actualBehavior: input.actualBehavior || '', reproductionSteps: input.reproductionSteps || [], cptCodes: input.cptCodes || pageContext.cptCodes, reporterName: input.reporterName || '', reporterEmail: input.reporterEmail || '', pageContext, suggestedFix });

  if (openai) {
    try {
      const response = await openai.responses.create({
        model: process.env.OPENAI_MODEL || 'gpt-4.1-mini',
        temperature: 0.1,
        input: [
          { role: 'system', content: 'You structure FreeCPTCodeFinder reports using the provided function tools. Reports may involve CPT errors, wRVU errors, modifier bugs, missing codes, search problems, and Case Builder issues. Suggest fixes for human review only. Never commit, merge, push, deploy, or imply production changes are approved.' },
          { role: 'user', content: JSON.stringify({ ...input, description, pageContext }, null, 2) }
        ],
        tools: reportTools,
        tool_choice: 'required'
      });
      report.ai = { provider: 'openai_responses_api', used: true, responseId: response.id || null };
      for (const item of response.output || []) {
        if (item.type !== 'function_call') continue;
        const args = JSON.parse(item.arguments || '{}');
        if (item.name === 'classify_issue_type') report.issueType = classifyIssueType(args);
        if (item.name === 'attach_page_context') report.pageContext = attachPageContext(args);
        if (item.name === 'suggest_fix_for_review') report.suggestedFix = suggestFixForReview(args);
        if (item.name === 'create_bug_report') {
          const structured = buildBugReport(args);
          report = { ...report, ...structured, id: report.id, createdAt: report.createdAt, ai: report.ai };
        }
      }
      report.issueLabel = issueLabel(report.issueType);
    } catch (err) {
      report = markOpenAiFallback(report, err);
    }
  } else {
    report.ai = { provider: 'openai_responses_api', used: false, error: 'OPENAI_API_KEY is not configured' };
  }

  report.suggestedFix = report.suggestedFix || suggestFixForReview(report);
  try {
    const github = await createGithubIssue(report);
    if (github.url) report.delivery.githubIssueUrl = github.url;
    if (github.skipped) report.delivery.errors.push(github.reason);
  } catch (err) {
    report.delivery.errors.push(err.message);
  }
  try {
    const notified = await notifyAgent(report);
    report.delivery.agentNotified = !!notified.sent;
    report.delivery.emailSent = !!notified.sent;
    if (notified.skipped) report.delivery.errors.push(notified.reason);
  } catch (err) {
    report.delivery.errors.push(err.message);
  }
  saveReport(report);
  return report;
}

function answerTextFromResponse(response) {
  if (response.output_text) return response.output_text.trim();
  return (response.output || []).flatMap(item => item.content || []).map(part => part.text || '').join('\n').trim();
}

app.get('/health', (_req, res) => {
  res.json({ ok: true, provider: 'openai_responses_api', openai: !!openai, cptRows: Array.isArray(cptDb) ? cptDb.length : 0, reports: loadReports().length, reportStore: githubIssuesDurableStore ? 'github_issues' : 'runtime_json', githubIssues: { enabled: githubIssuesEnabled, durableStore: githubIssuesDurableStore, repo: githubRepo }, allowedOrigins, rateLimit: { reports: { windowMs: reportRateLimit.windowMs || Number(process.env.REPORT_RATE_LIMIT_WINDOW_MS || 15 * 60 * 1000), max: Number(process.env.REPORT_RATE_LIMIT_MAX || 30) } }, phiWarning: 'Do not submit PHI. Reports should use test data or de-identified workflow details only.' });
});

app.get('/report-tester', (_req, res) => {
  res.type('html').send('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FreeCPTCodeFinder Staging Report Tester</title><style>body{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;background:#f8fafc;color:#0f172a}main{max-width:820px;margin:0 auto;padding:28px}label{display:block;font-weight:700;margin:14px 0 6px}textarea,input,select{width:100%;box-sizing:border-box;border:1px solid #cbd5e1;border-radius:8px;padding:10px;font:inherit}textarea{min-height:120px}button{margin-top:16px;background:#2563eb;color:white;border:0;border-radius:8px;padding:10px 14px;font-weight:800;cursor:pointer}.warn{background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:12px;color:#9a3412}.out{white-space:pre-wrap;background:#0f172a;color:#e2e8f0;border-radius:8px;padding:14px;margin-top:18px;overflow:auto}</style></head><body><main><h1>Staging Report Tester</h1><p class="warn"><strong>Do not submit PHI.</strong> Use test data or de-identified workflow details only.</p><form id="f"><label>Report Type</label><select name="issueType"><option value="wrvu_error">Wrong wRVU</option><option value="cpt_error">CPT Error</option><option value="modifier_bug">Modifier Bug</option><option value="missing_code">Missing CPT Code</option><option value="search_problem">Search Issue</option><option value="case_builder_issue">Case Builder Issue</option><option value="category_placement">Category Placement Issue</option></select><label>Report</label><textarea name="description" required>CPT 22585 WRVU appears incorrect.</textarea><label>Page URL</label><input name="pageUrl" value="https://freecptcodefinder.com/cpt/22585.html"><label>Search Query</label><input name="searchQuery" value="22585"><label>CPT Codes, comma-separated</label><input name="cptCodes" value="22585"><button type="submit">Submit Test Report</button></form><div id="out" class="out" hidden></div><script>document.getElementById("f").addEventListener("submit",async e=>{e.preventDefault();const fd=new FormData(e.currentTarget);const body={issueType:fd.get("issueType"),description:fd.get("description"),pageContext:{pageUrl:fd.get("pageUrl"),pageTitle:document.title,searchQuery:fd.get("searchQuery"),cptCodes:String(fd.get("cptCodes")||"").split(",").map(s=>s.trim()).filter(Boolean),activeCase:[]}};const out=document.getElementById("out");out.hidden=false;out.textContent="Submitting...";const res=await fetch("/reports",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});out.textContent=JSON.stringify(await res.json(),null,2);});</script></main></body></html>');
});

app.post('/assistant', async (req, res) => {
  const question = String(req.body?.question || '').trim();
  const caseLines = Array.isArray(req.body?.caseLines) ? req.body.caseLines.slice(0, 20) : [];
  if (!question) return res.status(400).json({ error: 'question required' });
  const reportIntent = /\b(report|wrong|bug|error|missing|broken|issue|incorrect|doesn't find|does not find|case builder|wrvu|modifier)\b/i.test(question);
  if (reportIntent && /\b(report|bug|issue|wrong|incorrect|missing|broken)\b/i.test(question)) {
    const report = await runReportPipeline({ description: question, pageContext: req.body?.pageContext || {}, cptCodes: req.body?.cptCodes || [], reproductionSteps: req.body?.reproductionSteps || [], reporterName: req.body?.reporterName || '', reporterEmail: req.body?.reporterEmail || '' });
    return res.json({ answer: 'I logged this as ' + report.id + ' (' + report.issueType + '). The AI suggested a review-only fix and cannot commit, merge, or deploy changes.', report });
  }
  const matches = searchCpt(question, 10);
  const grounded = { question, likelyMatches: matches, activeCase: caseLines.map(l => ({ cpt: l.cpt, desc: l.desc, mods: l.mods || [], userMod: l.userMod || '', approach: l.approach || '', wrvu: l.baseWrvu || l.effWrvu || null })) };
  if (!openai) return res.json({ answer: 'Backend is running, but OPENAI_API_KEY is not set yet. Top grounded matches for this question: ' + (matches.map(m => m.code + ' ' + m.description).join(' | ') || 'none found') + '.', matches });
  try {
    const response = await openai.responses.create({
      model: process.env.OPENAI_MODEL || 'gpt-4.1-mini',
      temperature: 0.2,
      input: [
        { role: 'system', content: 'You are the Free CPT Code Finder AI Assistant. Help with CPT coding, modifiers, wRVUs, and case-structure questions. Be concise, practical, and cautious. Never fabricate CPT facts. If rules depend on documentation, payer policy, NCCI edits, laterality, or global-period context, say so. Treat provided CPT matches as grounding data. Never commit, merge, push, or deploy changes.' },
        { role: 'user', content: 'Use this grounded site data when answering:\n' + JSON.stringify(grounded, null, 2) }
      ]
    });
    res.json({ answer: answerTextFromResponse(response) || 'No answer returned.', matches });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'assistant_failed', detail: err.message });
  }
});

app.post('/reports', reportRateLimit, async (req, res) => {
  const description = sanitizeText(req.body?.description || req.body?.message || '', 4000);
  if (!description) return res.status(400).json({ error: 'description required' });
  try {
    const report = await runReportPipeline(req.body);
    res.status(201).json({ ok: true, report });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'report_failed', detail: err.message });
  }
});

app.get('/admin/reports', async (req, res) => {
  const configuredKey = adminReportsKey;
  if (configuredKey && req.query.key !== configuredKey) return res.status(401).send('Unauthorized');
  let dashboardErrors = [];
  let reports = loadReports();
  try {
    const githubReports = await listGithubIssueReports();
    const seen = new Set(githubReports.map(report => report.id));
    reports = githubReports.concat(reports.filter(report => !seen.has(report.id)));
  } catch (err) {
    dashboardErrors.push(err.message);
  }
  const rows = reports.map(report => '<tr><td><code>' + escapeHtml(report.id) + '</code><br><small>' + escapeHtml(report.createdAt) + '</small></td><td>' + escapeHtml(report.issueLabel || issueLabel(report.issueType)) + '<br><small>' + escapeHtml(report.issueType) + ' / ' + escapeHtml(report.severity) + '</small></td><td><strong>' + escapeHtml(report.title) + '</strong><br>' + escapeHtml(report.summary || report.description) + '</td><td>' + escapeHtml((report.cptCodes || []).join(', ')) + '</td><td>' + (report.delivery.githubIssueUrl ? '<a href="' + escapeAttr(report.delivery.githubIssueUrl) + '">GitHub</a>' : 'Logged') + '<br><small>' + escapeHtml((report.delivery.errors || []).join(' | ')) + '</small></td><td>' + escapeHtml(report.suggestedFix?.summary || '') + '<br><small>No commit, merge, push, or deploy without human approval.</small></td></tr>').join('');
  const errorBlock = dashboardErrors.length ? '<div class="err">GitHub dashboard store error: ' + escapeHtml(dashboardErrors.join(' | ')) + '</div>' : '';
  res.type('html').send('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FreeCPTCodeFinder Report Dashboard</title><style>body{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;background:#f8fafc;color:#0f172a}header{padding:24px 28px;background:#0b1f3a;color:white}main{padding:24px 28px}.err{background:#fef2f2;border:1px solid #fecaca;color:#991b1b;padding:12px;margin-bottom:14px}table{width:100%;border-collapse:collapse;background:white;border:1px solid #e2e8f0}th,td{padding:12px;border-bottom:1px solid #e2e8f0;text-align:left;vertical-align:top;font-size:14px}th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#475569;background:#f1f5f9}code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}small{color:#64748b}</style></head><body><header><h1>Report Dashboard</h1><div>' + reports.length + ' logged reports | store: ' + (githubIssuesDurableStore ? 'GitHub Issues' : 'runtime JSON') + '</div></header><main>' + errorBlock + '<table><thead><tr><th>ID</th><th>Type</th><th>Report</th><th>CPT</th><th>Delivery</th><th>Review-only Suggestion</th></tr></thead><tbody>' + (rows || '<tr><td colspan="6">No reports logged yet.</td></tr>') + '</tbody></table></main></body></html>');
});

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/"/g, '&quot;');
}

const port = process.env.PORT || 8787;
app.listen(port, () => console.log('Assistant backend listening on ' + port));
