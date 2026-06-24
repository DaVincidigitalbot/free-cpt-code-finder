#!/usr/bin/env node
const fs = require('fs');

function assert(condition, message) {
  if (!condition) {
    console.error('FAIL:', message);
    process.exitCode = 1;
  }
}

const index = fs.readFileSync('index.html', 'utf8');
const telemetry = fs.readFileSync('js/privacy-safe-telemetry.js', 'utf8');
const sample = JSON.parse(fs.readFileSync('data/telemetry/sample_aggregate_report.json', 'utf8'));

assert(/FCCF_TELEMETRY_CONFIG=\{enabled:false/.test(index), 'telemetry must be disabled by default in index.html');
assert(!/searchTerm\s*:/.test(index), 'index.html must not post raw searchTerm fields');
assert(!/pagePath\s*:/.test(index), 'index.html telemetry must not include page path as a tracking dimension');
assert(/unmatched_private_query/.test(telemetry), 'sanitizer must classify unknown search text without storing it');
assert(/storesPatientIdentifiers"\s*:\s*false/.test(JSON.stringify(sample)), 'sample report must assert no patient identifiers');
assert(sample.privacy.storesFreeText === false, 'sample report must assert no free text storage');
assert(sample.privacy.storesIpAddresses === false, 'sample report must assert no IP storage');
assert(sample.privacy.storesUserIdentifiers === false, 'sample report must assert no user identifier storage');

const forbiddenPayloadTerms = [
  'patientName',
  'mrn',
  'dateOfService',
  'operativeNote',
  'email',
  'userId',
  'ipAddress',
  'comment'
];
const newFiles = [
  'js/privacy-safe-telemetry.js',
  'data/telemetry/schema.sql',
  'admin/case-builder-telemetry-dashboard.html'
];
for (const file of newFiles) {
  const raw = fs.readFileSync(file, 'utf8');
  for (const term of forbiddenPayloadTerms) {
    assert(!new RegExp('\\b' + term + '\\b', 'i').test(raw), file + ' contains forbidden telemetry payload term ' + term);
  }
}

if (!process.exitCode) {
  console.log('Telemetry privacy validation passed.');
}
