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
const leadLogPath = path.join(dataDir, 'rvuready_leads.json');
const unsuccessfulSearchLogPath = path.join(dataDir, 'unsuccessful_searches.json');
const suggestionAnalyticsLogPath = path.join(dataDir, 'suggestion_analytics.json');
const mappingStoreTitle = '[FREECPT SUGGESTED CPT MAPPINGS]';
const procedureIntelligenceStoreTitle = '[FREECPT PROCEDURE INTELLIGENCE]';
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
app.use(express.urlencoded({ extended: false, limit: '100kb' }));
app.use('/staging-frontend', express.static(projectRoot));
app.use('/styles', express.static(path.join(projectRoot, 'styles')));
app.use('/js', express.static(path.join(projectRoot, 'js')));
app.use('/assets', express.static(path.join(projectRoot, 'assets')));
app.get('/favicon.png', (_req, res) => res.sendFile(path.join(projectRoot, 'favicon.png')));
app.get('/cpt_database.json', (_req, res) => res.sendFile(cptDbPath));

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
  if (!fs.existsSync(leadLogPath)) fs.writeFileSync(leadLogPath, '[]\n');
  if (!fs.existsSync(unsuccessfulSearchLogPath)) fs.writeFileSync(unsuccessfulSearchLogPath, '[]\n');
  if (!fs.existsSync(suggestionAnalyticsLogPath)) fs.writeFileSync(suggestionAnalyticsLogPath, '[]\n');
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

function loadLeads() {
  ensureDataDir();
  try {
    const parsed = JSON.parse(fs.readFileSync(leadLogPath, 'utf8'));
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveLead(lead) {
  const leads = loadLeads();
  leads.unshift(lead);
  fs.writeFileSync(leadLogPath, JSON.stringify(leads.slice(0, 3000), null, 2) + '\n');
}

function loadUnsuccessfulSearches() {
  ensureDataDir();
  try {
    const parsed = JSON.parse(fs.readFileSync(unsuccessfulSearchLogPath, 'utf8'));
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveUnsuccessfulSearch(entry) {
  const searches = loadUnsuccessfulSearches();
  searches.unshift(entry);
  fs.writeFileSync(unsuccessfulSearchLogPath, JSON.stringify(searches.slice(0, 2000), null, 2) + '\n');
}

function loadSuggestionAnalytics() {
  ensureDataDir();
  try {
    const parsed = JSON.parse(fs.readFileSync(suggestionAnalyticsLogPath, 'utf8'));
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function saveSuggestionAnalytics(entry) {
  const analytics = loadSuggestionAnalytics();
  analytics.unshift(entry);
  fs.writeFileSync(suggestionAnalyticsLogPath, JSON.stringify(analytics.slice(0, 3000), null, 2) + '\n');
}

function suggestionAnalyticsSummary(limit = 20) {
  const grouped = new Map();
  for (const entry of loadSuggestionAnalytics()) {
    const term = normalizeSearchTerm(entry.searchTerm || '');
    if (!term) continue;
    const current = grouped.get(term) || { searchTerm: term, shown: 0, clicks: 0, clickedCpts: new Map(), lastSeenAt: entry.createdAt || '' };
    if (entry.eventType === 'clicked') {
      current.clicks += 1;
      const code = sanitizeText(entry.clickedCpt || '', 20);
      if (code) current.clickedCpts.set(code, (current.clickedCpts.get(code) || 0) + 1);
    } else {
      current.shown += 1;
    }
    if (String(entry.createdAt || '') > String(current.lastSeenAt || '')) current.lastSeenAt = entry.createdAt;
    grouped.set(term, current);
  }
  return [...grouped.values()]
    .map(row => {
      const clickedEntries = [...row.clickedCpts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
      const topClickedCpt = clickedEntries[0]?.[0] || '';
      const ctr = row.shown ? Math.min(100, Number(((row.clicks / row.shown) * 100).toFixed(1))) : 0;
      return {
        ...row,
        topClickedCpt,
        ctr,
        currentSuggestedRanking: clickedEntries.map(([code]) => code).join(', '),
        clickedCpts: clickedEntries.map(([code, count]) => code + ' (' + count + ')').join(', ')
      };
    })
    .sort((a, b) => (b.clicks + b.shown) - (a.clicks + a.shown) || String(b.lastSeenAt).localeCompare(String(a.lastSeenAt)))
    .slice(0, limit);
}

function suggestionRankingData(limit = 200) {
  const grouped = new Map();
  const now = Date.now();
  for (const entry of loadSuggestionAnalytics()) {
    const term = normalizeSearchTerm(entry.searchTerm || '');
    if (!term) continue;
    const current = grouped.get(term) || { searchTerm: term, shown: 0, clicks: 0, cptScores: {}, topClickedCpt: '', ctr: 0 };
    if (entry.eventType === 'clicked') {
      current.clicks += 1;
      const code = sanitizeText(entry.clickedCpt || '', 20);
      if (/^\d{5}$/.test(code)) {
        const ageDays = Math.max(0, (now - Date.parse(entry.createdAt || '')) / 86400000);
        const recentWeight = ageDays <= 30 ? 2 : ageDays <= 90 ? 1 : 0;
        const score = 3 + recentWeight;
        current.cptScores[code] = (current.cptScores[code] || 0) + score;
      }
    } else {
      current.shown += 1;
    }
    grouped.set(term, current);
  }
  return [...grouped.values()].map(row => {
    const ranked = Object.entries(row.cptScores).sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    return {
      ...row,
      topClickedCpt: ranked[0]?.[0] || '',
      ctr: row.shown ? Math.min(100, Number(((row.clicks / row.shown) * 100).toFixed(1))) : 0
    };
  }).sort((a, b) => b.clicks - a.clicks || b.shown - a.shown).slice(0, limit);
}

function topUnsuccessfulSearches(limit = 20) {
  const grouped = new Map();
  for (const entry of loadUnsuccessfulSearches()) {
    const term = normalizeSearchTerm(entry.searchTerm || '');
    if (!term) continue;
    const current = grouped.get(term) || { searchTerm: term, count: 0, lastSeenAt: entry.createdAt || '' };
    current.count += 1;
    if (String(entry.createdAt || '') > String(current.lastSeenAt || '')) current.lastSeenAt = entry.createdAt;
    grouped.set(term, current);
  }
  return [...grouped.values()].sort((a, b) => b.count - a.count || String(b.lastSeenAt).localeCompare(String(a.lastSeenAt))).slice(0, limit);
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

function normalizeIssueType(issueType) {
  const value = sanitizeText(issueType || '', 80).toLowerCase();
  if (value === 'missing_code' || value === 'missing-cpt-code' || value === 'missing cpt code') return 'missing_cpt_code';
  return value || 'other';
}

function normalizeSearchTerm(value) {
  return sanitizeText(value || '', 160).toLowerCase().replace(/[^a-z0-9]+/g, ' ').replace(/\s+/g, ' ').trim();
}

function looksLikePhiSearch(value) {
  const text = String(value || '').trim();
  if (!text) return false;
  if (/\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b/.test(text)) return true;
  if (/\b\d{3}-\d{2}-\d{4}\b/.test(text)) return true;
  if (/\b(?:mrn|dob|patient|chart|acct|account|ssn)\b/i.test(text)) return true;
  if (/[A-Z][a-z]+,\s*[A-Z][a-z]+/.test(text)) return true;
  if (/\b[A-Z][a-z]+\s+[A-Z][a-z]+\b/.test(text) && !/\b(cpt|rvu|colostomy|ileostomy|ostomy|hartmann|amputation|hernia|appendectomy|cholecystectomy|colectomy|reversal|closure|takedown|procedure|surgery)\b/i.test(text)) return true;
  return false;
}

function looksLikePhiReport(fields) {
  return fields.some(value => looksLikePhiSearch(value));
}

function pagePathOnly(value) {
  try {
    const parsed = new URL(String(value || ''), 'https://freecptcodefinder.com');
    return sanitizeText(parsed.pathname || '/', 240);
  } catch {
    return null;
  }
}

function normalizeEmail(value) {
  return sanitizeText(value || '', 200).toLowerCase();
}

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value || ''));
}

function buildRvureadyLead(input = {}) {
  const email = normalizeEmail(input.email);
  const name = sanitizeText(input.name || '', 120);
  const role = sanitizeText(input.role || '', 80);
  const specialty = sanitizeText(input.specialty || '', 120);
  const practiceSetting = sanitizeText(input.practiceSetting || input.practice || '', 120);
  const documentationPain = sanitizeText(input.documentationPain || input.painPoint || input.message || '', 1000);
  const sourcePage = sanitizeText(input.sourcePage || input.pageUrl || '', 240);
  const sourcePath = pagePathOnly(input.sourcePath || input.sourcePage || input.pageUrl || '');
  const sourceContext = sanitizeText(input.sourceContext || '', 240);
  if (!isValidEmail(email)) {
    const err = new Error('valid email required');
    err.statusCode = 400;
    throw err;
  }
  if (looksLikePhiReport([documentationPain, sourceContext])) {
    const err = new Error('phi_like_lead_rejected');
    err.statusCode = 400;
    throw err;
  }
  return {
    id: 'RVU-' + new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14) + '-' + crypto.randomBytes(2).toString('hex').toUpperCase(),
    createdAt: new Date().toISOString(),
    name,
    email,
    role,
    specialty,
    practiceSetting,
    documentationPain,
    foundingUserInterest: input.foundingUserInterest === true || input.foundingInterest === true || input.foundingUserInterest === 'true' || input.foundingInterest === 'true',
    sourcePage,
    sourcePath,
    sourceContext,
    userAgent: sanitizeText(input.userAgent || '', 240),
    delivery: { githubIssueUrl: null, errors: [] },
    safety: { noPhiRequested: true, rawClinicalNoteStored: false, signupOnly: true }
  };
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
  const normalizedReportedType = normalizeIssueType(reportedType);
  if (normalizedReportedType === 'missing_cpt_code') return 'missing_cpt_code';
  if (/w\s*rvu|rvu|work\s*rvu|medicare|payment/.test(text)) return 'wrvu_error';
  if (/modifier|mod\s?\d+|-\d{2}|x[epsu]|59|80|62|51/.test(text)) return 'modifier_bug';
  if (/category|placement|specialty|section|taxonomy|under neurosurgery|under spine/.test(text)) return 'category_placement';
  if (/search|autocomplete|result|finding|query/.test(text)) return 'search_problem';
  if (/missing|add code|not listed|absent|can't find code|cannot find code/.test(text)) return 'missing_cpt_code';
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
  const issueType = normalizeIssueType(args.issueType || 'other');
  const codes = Array.isArray(args.cptCodes) ? args.cptCodes : [];
  const guidance = {
    cpt_error: 'Review CPT description, specialty taxonomy, code page content, inline CPT_DATA, and cpt_decision_tree.json for sync drift.',
    wrvu_error: 'Verify work RVU, total RVU, global period, MPPR behavior, and Medicare estimate against the current CMS physician fee schedule.',
    modifier_bug: 'Reproduce in Case Builder, then inspect modifier_engine_enhanced.js, enhanced_billing.js, and related Case Builder UI state.',
    missing_cpt_code: 'Review whether the requested procedure is absent or hard to find. If missing, add the CPT row to the canonical database, generated pages, specialty/category indexes, search data, sitemap, and inline CPT_DATA if applicable.',
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
    missing_cpt_code: 'Missing CPT Code',
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
  const issueType = normalizeIssueType(args.issueType || classifyIssueType({ description: args.description || args.summary || '', reportedType: args.reportedType || '' }));
  const missingCpt = issueType === 'missing_cpt_code' ? {
    procedureName: sanitizeText(args.procedureName || args.procedure || '', 160),
    specialty: sanitizeText(args.specialty || '', 120),
    suggestedCpt: sanitizeText(args.suggestedCpt || args.cptCode || (Array.isArray(args.cptCodes) ? args.cptCodes[0] : ''), 20),
    notes: sanitizeText(args.notes || args.description || '', 2000),
    status: sanitizeText(args.missingCptStatus || args.status || 'New', 40) || 'New'
  } : null;
  return {
    id: 'FCCF-' + now.slice(0, 10).replace(/-/g, '') + '-' + crypto.randomBytes(3).toString('hex').toUpperCase(),
    createdAt: now,
    status: issueType === 'missing_cpt_code' ? missingCpt.status : 'new',
    issueType,
    issueLabel: issueLabel(issueType),
    severity: args.severity || 'needs_triage',
    title: sanitizeText(args.title || (missingCpt?.procedureName ? '[MISSING CPT] ' + missingCpt.procedureName : issueType.replace(/_/g, ' ') + ' report'), 160),
    summary: sanitizeText(args.summary || args.description || '', 2000),
    description: sanitizeText(args.description || '', 4000),
    expectedBehavior: sanitizeText(args.expectedBehavior || '', 2000),
    actualBehavior: sanitizeText(args.actualBehavior || '', 2000),
    reproductionSteps: sanitizeStringArray(args.reproductionSteps, 12, 500),
    cptCodes: Array.isArray(args.cptCodes) ? sanitizeStringArray(args.cptCodes, 20, 20) : context.cptCodes,
    missingCpt,
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
  if (report.issueType === 'missing_cpt_code') {
    const procedureName = sanitizeText(report.missingCpt?.procedureName || report.title.replace(/^\[MISSING CPT\]\s*/i, '') || 'Missing CPT Code', 160);
    const body = [
      '<!-- FREECPT_REPORT_JSON_START',
      JSON.stringify(report, null, 2),
      'FREECPT_REPORT_JSON_END -->',
      '',
      'Procedure Name:',
      procedureName || '(not provided)',
      '',
      'Specialty:',
      report.missingCpt?.specialty || '(not provided)',
      '',
      'Suggested CPT:',
      report.missingCpt?.suggestedCpt || '(not provided)',
      '',
      'Notes:',
      report.missingCpt?.notes || report.summary || '(none)',
      '',
      'Submitted From:',
      'FreeCPTCodeFinder.com'
    ].join('\n');
    const response = await githubFetch('/issues', {
      method: 'POST',
      body: JSON.stringify({ title: '[MISSING CPT] ' + procedureName, body, labels: ['user-report', 'missing_cpt_code'] })
    });
    const json = await response.json();
    if (!response.ok) throw new Error(json.message || 'GitHub issue creation failed (' + response.status + ')');
    return { url: json.html_url, number: json.number };
  }
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

async function createRvureadyLeadIssue(lead) {
  if (!githubIssuesEnabled) return { skipped: true, reason: 'CREATE_GITHUB_ISSUES is not true' };
  if (!githubToken) return { skipped: true, reason: 'GITHUB_TOKEN is not set' };
  await ensureGithubLabels(['rvuready-lead', 'lead']);
  const body = [
    '<!-- FREECPT_RVUREADY_LEAD_JSON_START',
    JSON.stringify(lead, null, 2),
    'FREECPT_RVUREADY_LEAD_JSON_END -->',
    '',
    'Lead ID: ' + lead.id,
    'Email: ' + lead.email,
    'Name: ' + (lead.name || '(not provided)'),
    'Role: ' + (lead.role || '(not provided)'),
    'Specialty: ' + (lead.specialty || '(not provided)'),
    'Practice Setting: ' + (lead.practiceSetting || '(not provided)'),
    'Founding User Interest: ' + (lead.foundingUserInterest ? 'Yes' : 'No'),
    '',
    'Documentation Pain:',
    lead.documentationPain || '(not provided)',
    '',
    'Source:',
    lead.sourcePage || lead.sourcePath || '(not provided)',
    '',
    'Safety:',
    'Signup only. No PHI requested. Raw clinical note text is not stored by this lead form.'
  ].join('\n');
  const titleBits = [lead.role, lead.specialty].filter(Boolean).join(' / ') || lead.email;
  const response = await githubFetch('/issues', {
    method: 'POST',
    body: JSON.stringify({ title: '[RVUReady Lead] ' + titleBits, body, labels: ['rvuready-lead', 'lead'] })
  });
  const json = await response.json();
  if (!response.ok) throw new Error(json.message || 'GitHub RVUReady lead issue creation failed (' + response.status + ')');
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

function normalizeMappingTerm(value) {
  return normalizeSearchTerm(value).slice(0, 120);
}

function normalizeMappingCodes(value) {
  const raw = Array.isArray(value) ? value : String(value || '').split(/[\s,]+/);
  return [...new Set(raw.map(code => sanitizeText(code, 20).replace(/[^0-9A-Za-z]/g, '')).filter(code => /^\d{5}$/.test(code)))].slice(0, 12);
}

function normalizeSuggestedMappings(value) {
  const rows = Array.isArray(value) ? value : [];
  return rows.map(row => ({
    term: normalizeMappingTerm(row.term || row.searchTerm || ''),
    cpts: normalizeMappingCodes(row.cpts || row.codes || row.mappedCpts || ''),
    status: sanitizeText(row.status || 'Active', 30) || 'Active',
    note: sanitizeText(row.note || '', 200)
  })).filter(row => row.term && row.cpts.length && /^active$/i.test(row.status));
}

async function getSuggestedMappingIssue() {
  if (!githubToken) return null;
  const response = await githubFetch('/issues?state=open&labels=search-mapping&per_page=20');
  const issues = await response.json();
  if (!response.ok) throw new Error(issues.message || 'GitHub mapping issue list failed (' + response.status + ')');
  return issues.find(issue => issue.title === mappingStoreTitle) || null;
}

async function loadSuggestedMappings() {
  if (!githubToken) return [];
  const issue = await getSuggestedMappingIssue();
  if (!issue) return [];
  const match = String(issue.body || '').match(/FREECPT_SUGGESTED_MAPPINGS_JSON_START\n([\s\S]*?)\nFREECPT_SUGGESTED_MAPPINGS_JSON_END/);
  if (!match) return [];
  try {
    return normalizeSuggestedMappings(JSON.parse(match[1]));
  } catch {
    return [];
  }
}

async function saveSuggestedMappings(mappings) {
  if (!githubToken) throw new Error('GITHUB_TOKEN is not set');
  await ensureGithubLabels(['search-mapping']);
  const normalized = normalizeSuggestedMappings(mappings);
  const body = [
    '<!-- FREECPT_SUGGESTED_MAPPINGS_JSON_START',
    JSON.stringify(normalized, null, 2),
    'FREECPT_SUGGESTED_MAPPINGS_JSON_END -->',
    '',
    'Durable Suggested CPT Mapping Manager store.',
    '',
    'Edit via admin dashboard; public endpoint exposes active term-to-CPT mappings only.'
  ].join('\n');
  const existing = await getSuggestedMappingIssue();
  const payload = JSON.stringify({ title: mappingStoreTitle, body, labels: ['search-mapping'] });
  const response = existing
    ? await githubFetch('/issues/' + existing.number, { method: 'PATCH', body: payload })
    : await githubFetch('/issues', { method: 'POST', body: payload });
  const json = await response.json();
  if (!response.ok) throw new Error(json.message || 'GitHub mapping store update failed (' + response.status + ')');
  return { mappings: normalized, url: json.html_url, number: json.number };
}

function normalizeProcedureTerms(value) {
  const raw = Array.isArray(value) ? value : String(value || '').split(/[,\n]+/);
  return [...new Set(raw.map(term => normalizeSearchTerm(term)).filter(term => term.length >= 2))].slice(0, 30);
}

function normalizeProcedureConsiderations(value) {
  const raw = Array.isArray(value) ? value : String(value || '').split(/\n+/);
  return raw.map(item => sanitizeText(item, 220)).filter(Boolean).slice(0, 12);
}

function normalizeProcedureIntelligence(value) {
  const rows = Array.isArray(value) ? value : [];
  return rows.map(row => ({
    id: sanitizeText(row.id || row.slug || normalizeSearchTerm(row.title || '').replace(/\s+/g, '-'), 80).replace(/[^a-z0-9-]/gi, '').toLowerCase(),
    title: sanitizeText(row.title || '', 120),
    terms: normalizeProcedureTerms(row.terms || row.searchTerms || ''),
    considerations: normalizeProcedureConsiderations(row.considerations || ''),
    cpts: normalizeMappingCodes(row.cpts || row.codes || ''),
    note: sanitizeText(row.note || '', 240),
    status: sanitizeText(row.status || 'Active', 30) || 'Active'
  })).filter(row => row.id && row.title && row.terms.length && row.considerations.length && /^active$/i.test(row.status));
}

async function getProcedureIntelligenceIssue() {
  if (!githubToken) return null;
  const response = await githubFetch('/issues?state=open&labels=procedure-intelligence&per_page=20');
  const issues = await response.json();
  if (!response.ok) throw new Error(issues.message || 'GitHub procedure intelligence issue list failed (' + response.status + ')');
  return issues.find(issue => issue.title === procedureIntelligenceStoreTitle) || null;
}

async function loadProcedureIntelligence() {
  if (!githubToken) return [];
  const issue = await getProcedureIntelligenceIssue();
  if (!issue) return [];
  const match = String(issue.body || '').match(/FREECPT_PROCEDURE_INTELLIGENCE_JSON_START\n([\s\S]*?)\nFREECPT_PROCEDURE_INTELLIGENCE_JSON_END/);
  if (!match) return [];
  try {
    return normalizeProcedureIntelligence(JSON.parse(match[1]));
  } catch {
    return [];
  }
}

async function saveProcedureIntelligence(groups) {
  if (!githubToken) throw new Error('GITHUB_TOKEN is not set');
  await ensureGithubLabels(['procedure-intelligence']);
  const normalized = normalizeProcedureIntelligence(groups);
  const body = [
    '<!-- FREECPT_PROCEDURE_INTELLIGENCE_JSON_START',
    JSON.stringify(normalized, null, 2),
    'FREECPT_PROCEDURE_INTELLIGENCE_JSON_END -->',
    '',
    'Durable Procedure Intelligence store.',
    '',
    'Educational considerations only. Do not use this store for automatic CPT assignment.'
  ].join('\n');
  const existing = await getProcedureIntelligenceIssue();
  const payload = JSON.stringify({ title: procedureIntelligenceStoreTitle, body, labels: ['procedure-intelligence'] });
  const response = existing
    ? await githubFetch('/issues/' + existing.number, { method: 'PATCH', body: payload })
    : await githubFetch('/issues', { method: 'POST', body: payload });
  const json = await response.json();
  if (!response.ok) throw new Error(json.message || 'GitHub procedure intelligence store update failed (' + response.status + ')');
  return { groups: normalized, url: json.html_url, number: json.number };
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
  { type: 'function', name: 'classify_issue_type', description: 'Classify report into cpt_error, wrvu_error (user-facing label: Wrong wRVU), modifier_bug, missing_cpt_code, search_problem, category_placement, case_builder_issue, or other.', parameters: { type: 'object', additionalProperties: false, properties: { description: { type: 'string' }, reportedType: { type: ['string', 'null'] } }, required: ['description', 'reportedType'] } },
  { type: 'function', name: 'suggest_fix_for_review', description: 'Suggest a possible fix for human review only. Never commit, merge, push, or deploy.', parameters: { type: 'object', additionalProperties: false, properties: { issueType: { type: 'string' }, cptCodes: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } }, required: ['issueType', 'cptCodes', 'summary'] } }
];

async function runReportPipeline(input) {
  input = sanitizeObject(input);
  const requestedType = normalizeIssueType(input.issueType || '');
  const missingDescription = requestedType === 'missing_cpt_code'
    ? ['Procedure Name: ' + sanitizeText(input.procedureName || '', 160), 'Specialty: ' + sanitizeText(input.specialty || '', 120), input.suggestedCpt ? 'Suggested CPT: ' + sanitizeText(input.suggestedCpt, 20) : '', input.notes ? 'Notes: ' + sanitizeText(input.notes, 2000) : ''].filter(Boolean).join('\n')
    : '';
  const description = sanitizeText(input.description || input.message || input.question || missingDescription, 4000);
  const pageContext = attachPageContext({ ...(input.pageContext || {}), description });
  const issueType = classifyIssueType({ description, reportedType: input.issueType || '' });
  const suggestedFix = suggestFixForReview({ issueType, cptCodes: input.cptCodes || pageContext.cptCodes || [], summary: description });
  let report = buildBugReport({ title: input.title || (issueType === 'missing_cpt_code' && input.procedureName ? '[MISSING CPT] ' + input.procedureName : description.slice(0, 90)) || 'FreeCPTCodeFinder user report', summary: input.summary || description, description, issueType, severity: input.severity || 'needs_triage', expectedBehavior: input.expectedBehavior || '', actualBehavior: input.actualBehavior || '', reproductionSteps: input.reproductionSteps || [], cptCodes: input.cptCodes || (input.suggestedCpt ? [input.suggestedCpt] : pageContext.cptCodes), reporterName: input.reporterName || '', reporterEmail: input.reporterEmail || '', pageContext, suggestedFix, procedureName: input.procedureName || '', specialty: input.specialty || '', suggestedCpt: input.suggestedCpt || '', notes: input.notes || '' });

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
      if (issueType === 'missing_cpt_code') {
        report.issueType = 'missing_cpt_code';
        report.missingCpt = buildBugReport({ ...input, description, issueType: 'missing_cpt_code' }).missingCpt;
        report.title = '[MISSING CPT] ' + (report.missingCpt.procedureName || report.title.replace(/^\[MISSING CPT\]\s*/i, ''));
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
  res.json({ ok: true, provider: 'openai_responses_api', openai: !!openai, cptRows: Array.isArray(cptDb) ? cptDb.length : 0, reports: loadReports().length, leads: loadLeads().length, reportStore: githubIssuesDurableStore ? 'github_issues' : 'runtime_json', leadStore: githubIssuesDurableStore ? 'github_issues' : 'runtime_json', githubIssues: { enabled: githubIssuesEnabled, durableStore: githubIssuesDurableStore, repo: githubRepo }, allowedOrigins, rateLimit: { reports: { windowMs: reportRateLimit.windowMs || Number(process.env.REPORT_RATE_LIMIT_WINDOW_MS || 15 * 60 * 1000), max: Number(process.env.REPORT_RATE_LIMIT_MAX || 30) } }, phiWarning: 'Do not submit PHI. Reports and leads should use test data or de-identified workflow details only.' });
});

app.get('/report-tester', (_req, res) => {
  res.type('html').send('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FreeCPTCodeFinder Staging Report Tester</title><style>body{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;background:#f8fafc;color:#0f172a}main{max-width:820px;margin:0 auto;padding:28px}label{display:block;font-weight:700;margin:14px 0 6px}textarea,input,select{width:100%;box-sizing:border-box;border:1px solid #cbd5e1;border-radius:8px;padding:10px;font:inherit}textarea{min-height:120px}button{margin-top:16px;background:#2563eb;color:white;border:0;border-radius:8px;padding:10px 14px;font-weight:800;cursor:pointer}.warn{background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:12px;color:#9a3412}.out{white-space:pre-wrap;background:#0f172a;color:#e2e8f0;border-radius:8px;padding:14px;margin-top:18px;overflow:auto}</style></head><body><main><h1>Staging Report Tester</h1><p class="warn"><strong>Do not submit PHI.</strong> Use test data or de-identified workflow details only.</p><form id="f"><label>Report Type</label><select name="issueType"><option value="wrvu_error">Wrong wRVU</option><option value="cpt_error">CPT Error</option><option value="modifier_bug">Modifier Bug</option><option value="missing_cpt_code">Missing CPT Code</option><option value="search_problem">Search Issue</option><option value="case_builder_issue">Case Builder Issue</option><option value="category_placement">Category Placement Issue</option></select><label>Report</label><textarea name="description" required>CPT 22585 WRVU appears incorrect.</textarea><label>Page URL</label><input name="pageUrl" value="https://freecptcodefinder.com/cpt/22585.html"><label>Search Query</label><input name="searchQuery" value="22585"><label>CPT Codes, comma-separated</label><input name="cptCodes" value="22585"><button type="submit">Submit Test Report</button></form><div id="out" class="out" hidden></div><script>document.getElementById("f").addEventListener("submit",async e=>{e.preventDefault();const fd=new FormData(e.currentTarget);const body={issueType:fd.get("issueType"),description:fd.get("description"),pageContext:{pageUrl:fd.get("pageUrl"),pageTitle:document.title,searchQuery:fd.get("searchQuery"),cptCodes:String(fd.get("cptCodes")||"").split(",").map(s=>s.trim()).filter(Boolean),activeCase:[]}};const out=document.getElementById("out");out.hidden=false;out.textContent="Submitting...";const res=await fetch("/reports",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});out.textContent=JSON.stringify(await res.json(),null,2);});</script></main></body></html>');
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
  const requestedType = normalizeIssueType(req.body?.issueType || '');
  const description = sanitizeText(req.body?.description || req.body?.message || '', 4000);
  if (requestedType === 'missing_cpt_code') {
    if (!sanitizeText(req.body?.procedureName || '', 160) || !sanitizeText(req.body?.specialty || '', 120)) {
      return res.status(400).json({ error: 'procedureName and specialty required' });
    }
    if (looksLikePhiReport([
      req.body?.procedureName,
      req.body?.specialty,
      req.body?.suggestedCpt,
      req.body?.notes,
      description
    ])) {
      return res.status(400).json({ error: 'phi_like_report_rejected' });
    }
  } else if (!description) return res.status(400).json({ error: 'description required' });
  try {
    const report = await runReportPipeline(req.body);
    res.status(201).json({ ok: true, report });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'report_failed', detail: err.message });
  }
});

app.post('/leads', reportRateLimit, async (req, res) => {
  try {
    const lead = buildRvureadyLead({
      ...req.body,
      userAgent: req.get('user-agent') || req.body?.userAgent || ''
    });
    try {
      const github = await createRvureadyLeadIssue(lead);
      if (github.url) lead.delivery.githubIssueUrl = github.url;
      if (github.skipped) lead.delivery.errors.push(github.reason);
    } catch (err) {
      lead.delivery.errors.push(err.message);
    }
    saveLead(lead);
    res.status(201).json({
      ok: true,
      lead: {
        id: lead.id,
        createdAt: lead.createdAt,
        delivery: lead.delivery
      }
    });
  } catch (err) {
    const status = err.statusCode || 500;
    if (status >= 500) console.error(err);
    res.status(status).json({ error: err.message || 'lead_failed' });
  }
});

app.post('/search-analytics', reportRateLimit, (req, res) => {
  const rawSearchTerm = sanitizeText(req.body?.searchTerm || req.body?.query || '', 160);
  const searchTerm = normalizeSearchTerm(rawSearchTerm);
  const resultCount = Number(req.body?.resultCount ?? 0);
  if (!searchTerm || searchTerm.length < 2) return res.status(400).json({ error: 'searchTerm required' });
  if (resultCount !== 0) return res.json({ ok: true, logged: false });
  if (looksLikePhiSearch(rawSearchTerm)) return res.json({ ok: true, logged: false, reason: 'phi_like_search_rejected' });
  saveUnsuccessfulSearch({
    id: 'SEARCH-' + new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14) + '-' + crypto.randomBytes(2).toString('hex').toUpperCase(),
    createdAt: new Date().toISOString(),
    searchTerm,
    resultCount: 0,
    pagePath: pagePathOnly(req.body?.pagePath || req.body?.pageUrl || '')
  });
  res.status(201).json({ ok: true, logged: true });
});

app.get('/suggested-cpt-mappings', async (_req, res) => {
  try {
    const mappings = await loadSuggestedMappings();
    res.json({ ok: true, mappings });
  } catch (err) {
    res.status(503).json({ ok: false, mappings: [], error: 'mapping_store_unavailable' });
  }
});

app.get('/suggestion-rankings', (_req, res) => {
  res.json({ ok: true, rankings: suggestionRankingData() });
});

app.get('/procedure-intelligence', async (_req, res) => {
  try {
    const groups = await loadProcedureIntelligence();
    res.json({ ok: true, groups });
  } catch (err) {
    res.status(503).json({ ok: false, groups: [], error: 'procedure_intelligence_store_unavailable' });
  }
});

app.post('/suggested-cpt-mappings', reportRateLimit, async (req, res) => {
  const configuredKey = adminReportsKey;
  if (configuredKey && req.query.key !== configuredKey) return res.status(401).json({ error: 'unauthorized' });
  try {
    const term = normalizeMappingTerm(req.body?.term || req.body?.searchTerm || '');
    const cpts = normalizeMappingCodes(req.body?.cpts || req.body?.codes || req.body?.mappedCpts || '');
    const status = sanitizeText(req.body?.status || 'Active', 30) || 'Active';
    const note = sanitizeText(req.body?.note || '', 200);
    if (!term || !cpts.length) return res.status(400).json({ error: 'term and cpts required' });
    if (looksLikePhiSearch(term)) return res.status(400).json({ error: 'phi_like_mapping_rejected' });
    const existing = await loadSuggestedMappings();
    const next = existing.filter(row => row.term !== term);
    if (/^active$/i.test(status)) next.unshift({ term, cpts, status: 'Active', note });
    const saved = await saveSuggestedMappings(next);
    if (String(req.headers.accept || '').includes('text/html')) {
      return res.redirect('/admin/reports?key=' + encodeURIComponent(req.query.key || ''));
    }
    res.status(201).json({ ok: true, ...saved });
  } catch (err) {
    res.status(500).json({ error: 'mapping_update_failed', detail: err.message });
  }
});

app.post('/procedure-intelligence', reportRateLimit, async (req, res) => {
  const configuredKey = adminReportsKey;
  if (configuredKey && req.query.key !== configuredKey) return res.status(401).json({ error: 'unauthorized' });
  try {
    const id = sanitizeText(req.body?.id || req.body?.slug || normalizeSearchTerm(req.body?.title || '').replace(/\s+/g, '-'), 80).replace(/[^a-z0-9-]/gi, '').toLowerCase();
    const title = sanitizeText(req.body?.title || '', 120);
    const terms = normalizeProcedureTerms(req.body?.terms || req.body?.searchTerms || '');
    const considerations = normalizeProcedureConsiderations(req.body?.considerations || '');
    const cpts = normalizeMappingCodes(req.body?.cpts || req.body?.codes || '');
    const note = sanitizeText(req.body?.note || '', 240);
    const status = sanitizeText(req.body?.status || 'Active', 30) || 'Active';
    if (!id || !title || !terms.length || !considerations.length) return res.status(400).json({ error: 'id, title, terms, and considerations required' });
    if (looksLikePhiReport([title, terms.join(' '), considerations.join(' '), note])) return res.status(400).json({ error: 'phi_like_procedure_intelligence_rejected' });
    const existing = await loadProcedureIntelligence();
    const next = existing.filter(row => row.id !== id);
    if (/^active$/i.test(status)) next.unshift({ id, title, terms, considerations, cpts, note, status: 'Active' });
    const saved = await saveProcedureIntelligence(next);
    if (String(req.headers.accept || '').includes('text/html')) {
      return res.redirect('/admin/reports?key=' + encodeURIComponent(req.query.key || ''));
    }
    res.status(201).json({ ok: true, ...saved });
  } catch (err) {
    res.status(500).json({ error: 'procedure_intelligence_update_failed', detail: err.message });
  }
});

app.post('/suggestion-analytics', reportRateLimit, (req, res) => {
  const rawSearchTerm = sanitizeText(req.body?.searchTerm || '', 160);
  const searchTerm = normalizeSearchTerm(rawSearchTerm);
  const eventType = sanitizeText(req.body?.eventType || req.body?.event || 'shown', 20).toLowerCase() === 'clicked' ? 'clicked' : 'shown';
  const clickedCpt = sanitizeText(req.body?.clickedCpt || '', 20).replace(/[^0-9A-Za-z]/g, '');
  if (!searchTerm || searchTerm.length < 2) return res.status(400).json({ error: 'searchTerm required' });
  if (looksLikePhiSearch(rawSearchTerm)) return res.json({ ok: true, logged: false, reason: 'phi_like_suggestion_rejected' });
  saveSuggestionAnalytics({
    id: 'SUGGEST-' + new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14) + '-' + crypto.randomBytes(2).toString('hex').toUpperCase(),
    createdAt: new Date().toISOString(),
    searchTerm,
    eventType,
    clickedCpt: /^\d{5}$/.test(clickedCpt) ? clickedCpt : '',
    pagePath: pagePathOnly(req.body?.pagePath || req.body?.pageUrl || '')
  });
  res.status(201).json({ ok: true, logged: true });
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
  const typeFilter = normalizeIssueType(req.query.type || '');
  const filteredReports = typeFilter && typeFilter !== 'other' ? reports.filter(report => normalizeIssueType(report.issueType) === typeFilter) : reports;
  const rows = filteredReports.map(report => '<tr><td><code>' + escapeHtml(report.id) + '</code><br><small>' + escapeHtml(report.createdAt) + '</small></td><td>' + escapeHtml(report.issueLabel || issueLabel(report.issueType)) + '<br><small>' + escapeHtml(report.issueType) + ' / ' + escapeHtml(report.severity) + '</small></td><td><strong>' + escapeHtml(report.title) + '</strong><br>' + escapeHtml(report.summary || report.description) + '</td><td>' + escapeHtml(report.missingCpt?.procedureName || '') + '</td><td>' + escapeHtml(report.missingCpt?.specialty || '') + '</td><td>' + escapeHtml(report.missingCpt?.suggestedCpt || (report.cptCodes || []).join(', ')) + '</td><td>' + escapeHtml(report.missingCpt?.status || report.status || 'new') + '</td><td>' + (report.delivery.githubIssueUrl ? '<a href="' + escapeAttr(report.delivery.githubIssueUrl) + '">GitHub</a>' : 'Logged') + '<br><small>' + escapeHtml((report.delivery.errors || []).join(' | ')) + '</small></td><td>' + escapeHtml(report.suggestedFix?.summary || '') + '<br><small>No commit, merge, push, or deploy without human approval.</small></td></tr>').join('');
  const searchRows = topUnsuccessfulSearches(20).map(row => '<tr><td>' + escapeHtml(row.searchTerm) + '</td><td>' + row.count + '</td><td>' + escapeHtml(row.lastSeenAt) + '</td></tr>').join('');
  const suggestedAnalyticsRows = suggestionAnalyticsSummary(20).map(row => '<tr><td>' + escapeHtml(row.searchTerm) + '</td><td>' + row.shown + '</td><td>' + row.clicks + '</td><td>' + row.ctr.toFixed(1) + '%</td><td>' + escapeHtml(row.topClickedCpt || '') + '</td><td><code>' + escapeHtml(row.currentSuggestedRanking || '') + '</code></td><td>' + escapeHtml(row.clickedCpts || '') + '</td><td>' + escapeHtml(row.lastSeenAt) + '</td></tr>').join('');
  let mappingRows = '';
  let mappingStoreError = '';
  try {
    mappingRows = (await loadSuggestedMappings()).map(row => '<tr><td>' + escapeHtml(row.term) + '</td><td><code>' + escapeHtml(row.cpts.join(', ')) + '</code></td><td>' + escapeHtml(row.status) + '</td><td>' + escapeHtml(row.note || '') + '</td></tr>').join('');
  } catch (err) {
    mappingStoreError = '<div class="err">Suggested CPT mapping store error: ' + escapeHtml(err.message) + '</div>';
  }
  let procedureRows = '';
  let procedureStoreError = '';
  try {
    procedureRows = (await loadProcedureIntelligence()).map(row => '<tr><td><strong>' + escapeHtml(row.title) + '</strong><br><small><code>' + escapeHtml(row.id) + '</code></small></td><td>' + escapeHtml(row.terms.join(', ')) + '</td><td>' + escapeHtml(row.considerations.join(' | ')) + '</td><td><code>' + escapeHtml(row.cpts.join(', ')) + '</code></td><td>' + escapeHtml(row.status) + '</td><td>' + escapeHtml(row.note || '') + '</td></tr>').join('');
  } catch (err) {
    procedureStoreError = '<div class="err">Procedure Intelligence store error: ' + escapeHtml(err.message) + '</div>';
  }
  const filterBlock = '<div class="filters"><a href="/admin/reports?key=' + escapeAttr(req.query.key || '') + '">All</a><a href="/admin/reports?type=missing_cpt_code&key=' + escapeAttr(req.query.key || '') + '">Missing CPT Code</a><a href="/admin/reports?type=search_problem&key=' + escapeAttr(req.query.key || '') + '">Search Issue</a><span>Statuses: New, Reviewing, Added, Duplicate, Not Applicable</span></div>';
  const errorBlock = dashboardErrors.length ? '<div class="err">GitHub dashboard store error: ' + escapeHtml(dashboardErrors.join(' | ')) + '</div>' : '';
  const mappingForm = '<h2>Suggested CPT Mapping Manager</h2>' + mappingStoreError + '<form method="post" action="/suggested-cpt-mappings?key=' + escapeAttr(req.query.key || '') + '" style="display:grid;grid-template-columns:2fr 2fr 1fr;gap:10px;background:white;border:1px solid #e2e8f0;padding:14px;margin-bottom:14px"><label>Search Term<br><input name="term" placeholder="completion proctectomy" required></label><label>Mapped CPTs<br><input name="cpts" placeholder="44626, 44625" required></label><label>Status<br><select name="status"><option>Active</option><option>Inactive</option></select></label><label style="grid-column:1 / -2">Note<br><input name="note" placeholder="Internal review note"></label><button type="submit">Save Mapping</button></form>';
  const procedureForm = '<h2>Procedure Intelligence Manager</h2>' + procedureStoreError + '<form method="post" action="/procedure-intelligence?key=' + escapeAttr(req.query.key || '') + '" style="display:grid;grid-template-columns:1fr 2fr 1fr;gap:10px;background:white;border:1px solid #e2e8f0;padding:14px;margin-bottom:14px"><label>ID / Slug<br><input name="id" placeholder="hartmann-reversal" required></label><label>Procedure Title<br><input name="title" placeholder="Hartmann reversal" required></label><label>Status<br><select name="status"><option>Active</option><option>Inactive</option></select></label><label style="grid-column:1 / -1">Search Terms<br><textarea name="terms" rows="3" placeholder="hartmann reversal, colostomy reversal, stoma reversal" required></textarea></label><label style="grid-column:1 / -1">Common Coding Considerations<br><textarea name="considerations" rows="5" placeholder="Was bowel resection performed?\nWas a colorectal anastomosis created?" required></textarea></label><label>Potential CPTs<br><input name="cpts" placeholder="44626, 44625, 44620"></label><label style="grid-column:2 / -1">Note<br><input name="note" placeholder="Educational checklist only"></label><button type="submit">Save Procedure Intelligence</button></form>';
  res.type('html').send('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>FreeCPTCodeFinder Report Dashboard</title><style>body{font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:0;background:#f8fafc;color:#0f172a}header{padding:24px 28px;background:#0b1f3a;color:white}main{padding:24px 28px}.err{background:#fef2f2;border:1px solid #fecaca;color:#991b1b;padding:12px;margin-bottom:14px}.filters{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:14px}.filters a{background:white;border:1px solid #cbd5e1;border-radius:8px;padding:8px 10px;color:#0b1f3a;text-decoration:none;font-weight:800}.filters span{color:#64748b;font-size:13px}table{width:100%;border-collapse:collapse;background:white;border:1px solid #e2e8f0;margin-bottom:24px}th,td{padding:12px;border-bottom:1px solid #e2e8f0;text-align:left;vertical-align:top;font-size:14px}th{font-size:12px;text-transform:uppercase;letter-spacing:.04em;color:#475569;background:#f1f5f9}code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}small{color:#64748b}h2{margin-top:28px}input,select,button,textarea{box-sizing:border-box;width:100%;border:1px solid #cbd5e1;border-radius:8px;padding:9px;font:inherit}textarea{resize:vertical}button{background:#0b1f3a;color:white;font-weight:800}@media(max-width:760px){main{padding:16px}form{grid-template-columns:1fr!important}label{grid-column:auto!important}}</style></head><body><header><h1>Report Dashboard</h1><div>' + filteredReports.length + ' shown / ' + reports.length + ' logged reports | store: ' + (githubIssuesDurableStore ? 'GitHub Issues' : 'runtime JSON') + '</div></header><main>' + errorBlock + filterBlock + '<table><thead><tr><th>ID</th><th>Type</th><th>Report</th><th>Procedure</th><th>Specialty</th><th>Suggested CPT</th><th>Status</th><th>Delivery</th><th>Review-only Suggestion</th></tr></thead><tbody>' + (rows || '<tr><td colspan="9">No reports logged yet.</td></tr>') + '</tbody></table><h2>Top Unsuccessful Searches</h2><table><thead><tr><th>Search Term</th><th>Count</th><th>Last Seen</th></tr></thead><tbody>' + (searchRows || '<tr><td colspan="3">No zero-result searches logged yet.</td></tr>') + '</tbody></table>' + mappingForm + '<table><thead><tr><th>Search Term</th><th>Mapped CPTs</th><th>Status</th><th>Note</th></tr></thead><tbody>' + (mappingRows || '<tr><td colspan="4">No admin mappings yet. Default frontend mappings still apply.</td></tr>') + '</tbody></table><h2>Suggested CPT Analytics</h2><table><thead><tr><th>Search Term</th><th>Times Shown</th><th>Times Clicked</th><th>CTR %</th><th>Top Clicked CPT</th><th>Current Suggested Ranking</th><th>Clicked CPTs</th><th>Last Seen</th></tr></thead><tbody>' + (suggestedAnalyticsRows || '<tr><td colspan="8">No suggestion analytics logged yet.</td></tr>') + '</tbody></table>' + procedureForm + '<table><thead><tr><th>Procedure</th><th>Search Terms</th><th>Considerations</th><th>Potential CPTs</th><th>Status</th><th>Note</th></tr></thead><tbody>' + (procedureRows || '<tr><td colspan="6">No admin procedure intelligence overrides yet. Default frontend groups still apply.</td></tr>') + '</tbody></table></main></body></html>');
});

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/"/g, '&quot;');
}

const port = process.env.PORT || 8787;
app.listen(port, () => console.log('Assistant backend listening on ' + port));
