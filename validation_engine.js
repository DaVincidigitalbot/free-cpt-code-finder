#!/usr/bin/env node

/**
 * VALIDATION ENGINE — FreeCPTCodeFinder Database Integrity Checker
 * 
 * Loads cpt_database.json, modifier_rules.json, ncci_bundles.json, specialty_hierarchy.json
 * Runs 7 comprehensive validation checks and outputs a gap report with recommendations.
 * 
 * Usage: node validation_engine.js
 */

const fs = require('fs');
const path = require('path');

// ─── Load Data ──────────────────────────────────────────────────────────────

function loadJSON(filename) {
    const filePath = path.join(__dirname, filename);
    try {
        return JSON.parse(fs.readFileSync(filePath, 'utf8'));
    } catch (err) {
        console.error(`❌ Failed to load ${filename}: ${err.message}`);
        process.exit(1);
    }
}

const cptDB = loadJSON('cpt_database.json');
const modifierRules = loadJSON('modifier_rules.json');
const ncciBundles = loadJSON('ncci_bundles.json');
const specialtyHierarchy = loadJSON('specialty_hierarchy.json');

const cptCodes = new Set(Object.keys(cptDB));
const modifierCodes = new Set(Object.keys(modifierRules));

// ─── Report Accumulator ────────────────────────────────────────────────────

const report = {
    checks: [],
    totalIssues: 0,
    criticalIssues: 0,
    warningIssues: 0,
    infoIssues: 0
};

function addCheck(name, severity, issues, recommendations) {
    const check = {
        name,
        severity, // 'critical' | 'warning' | 'info'
        issueCount: issues.length,
        issues: issues.slice(0, 50), // Cap output for readability
        truncated: issues.length > 50,
        totalFound: issues.length,
        recommendations
    };
    report.checks.push(check);
    report.totalIssues += issues.length;
    if (severity === 'critical') report.criticalIssues += issues.length;
    else if (severity === 'warning') report.warningIssues += issues.length;
    else report.infoIssues += issues.length;
    return check;
}

// ─── CHECK 1: Missing CPT Codes by Range ────────────────────────────────────

function checkMissingCodesByRange() {
    console.log('🔍 Check 1: Missing CPT codes in surgical range (10000-69999)...');
    
    // Get all numeric codes in our DB within surgical range
    const surgicalCodes = Object.keys(cptDB)
        .filter(c => /^\d{5}$/.test(c))
        .map(Number)
        .filter(c => c >= 10000 && c <= 69999)
        .sort((a, b) => a - b);

    // Define key surgical sub-ranges and expected code density
    const ranges = [
        { name: 'Integumentary (10000-19999)', start: 10000, end: 19999 },
        { name: 'Musculoskeletal (20000-29999)', start: 20000, end: 29999 },
        { name: 'Respiratory (30000-32999)', start: 30000, end: 32999 },
        { name: 'Cardiovascular (33000-37799)', start: 33000, end: 37799 },
        { name: 'Hemic/Lymphatic (38100-38999)', start: 38100, end: 38999 },
        { name: 'Digestive (40000-49999)', start: 40000, end: 49999 },
        { name: 'Urinary (50000-53899)', start: 50000, end: 53899 },
        { name: 'Male Genital (54000-55899)', start: 54000, end: 55899 },
        { name: 'Female Genital (56000-58999)', start: 56000, end: 58999 },
        { name: 'Endocrine (60000-60699)', start: 60000, end: 60699 },
        { name: 'Nervous System (61000-64999)', start: 61000, end: 64999 },
        { name: 'Eye/Ear (65000-69999)', start: 65000, end: 69999 },
    ];

    const issues = [];
    const rangeStats = [];

    ranges.forEach(range => {
        const codesInRange = surgicalCodes.filter(c => c >= range.start && c <= range.end);
        const rangeSize = range.end - range.start + 1;
        const coverage = codesInRange.length;
        
        // Flag ranges with very low coverage (< 5 codes)
        if (coverage < 5) {
            issues.push(`${range.name}: Only ${coverage} codes (severely underrepresented)`);
        } else if (coverage < 15) {
            issues.push(`${range.name}: Only ${coverage} codes (below typical density)`);
        }
        
        rangeStats.push({ range: range.name, codes: coverage, span: rangeSize });
    });

    // Find specific notable gaps — common high-volume procedures missing
    const criticalCodes = {
        '27447': 'Total knee arthroplasty (TKA)',
        '27130': 'Total hip arthroplasty (THA)',
        '29881': 'Arthroscopy knee, meniscectomy',
        '23472': 'Reverse total shoulder arthroplasty',
        '22612': 'Posterior lumbar interbody fusion',
        '27236': 'Open treatment femoral fracture',
        '27244': 'Open treatment intertrochanteric fracture',
        '27506': 'Open treatment tibial shaft fracture',
        '27507': 'Open treatment tibial plateau fracture',
    };

    const missingCritical = [];
    Object.entries(criticalCodes).forEach(([code, desc]) => {
        if (cptDB[code]) {
            // Check if it has 0 wRVU (placeholder)
            if (cptDB[code].work_rvu === 0) {
                missingCritical.push(`${code} (${desc}): EXISTS but has 0 wRVU — placeholder entry`);
            }
        } else {
            missingCritical.push(`${code} (${desc}): MISSING entirely`);
        }
    });

    if (missingCritical.length > 0) {
        issues.push(...missingCritical.map(m => `CRITICAL MISSING: ${m}`));
    }

    addCheck(
        'Missing CPT Codes by Surgical Range',
        issues.length > 5 ? 'critical' : 'warning',
        issues,
        [
            'Add wRVU values for placeholder codes (0 wRVU surgical codes)',
            'Prioritize high-volume orthopedic codes (TKA 27447, THA 27130)',
            'Expand Musculoskeletal range — most common surgical subspecialty',
            `Total surgical codes in DB: ${surgicalCodes.length}`,
            `Range stats:\n${rangeStats.map(r => `  ${r.range}: ${r.codes} codes`).join('\n')}`
        ]
    );
}

// ─── CHECK 2: Incomplete Specialty Trees ────────────────────────────────────

function checkIncompleteSpecialtyTrees() {
    console.log('🔍 Check 2: Incomplete specialty trees (specialties with <20 codes)...');
    
    const specialtyCounts = {};
    Object.values(cptDB).forEach(entry => {
        const spec = entry.specialty || 'unknown';
        specialtyCounts[spec] = (specialtyCounts[spec] || 0) + 1;
    });

    const issues = [];
    const allSpecialties = Object.entries(specialtyCounts).sort((a, b) => a[1] - b[1]);

    allSpecialties.forEach(([specialty, count]) => {
        if (count < 20) {
            issues.push(`${specialty}: ${count} codes (minimum 20 recommended for clinical utility)`);
        }
    });

    addCheck(
        'Incomplete Specialty Trees (<20 codes)',
        issues.length > 5 ? 'warning' : 'info',
        issues,
        [
            'Merge micro-specialties where appropriate (e.g., "fasciotomy" → "orthopedic")',
            'Expand cardiac subspecialties (cardiology=15, cardiac_valve=6, cardiac_cabg=4 → combine or expand)',
            'Add common codes for: debridement, wound_repair, component_separation',
            `Total specialties: ${allSpecialties.length}`,
            `Specialty distribution:\n${allSpecialties.map(([s, c]) => `  ${s}: ${c}`).join('\n')}`
        ]
    );
}

// ─── CHECK 3: Zero wRVU Surgical Codes ──────────────────────────────────────

function checkZeroWRVUSurgicalCodes() {
    console.log('🔍 Check 3: Surgical codes with 0 wRVU that should not be 0...');
    
    // Surgical codes should have wRVU > 0 (except certain technical/professional component codes)
    const exemptPatterns = [
        /^9300[0-9]/, // ECG technical components
        /^9301[0-9]/, // Stress test technical
        /^7[0-9]{4}/, // Radiology technical
        /^8[0-9]{4}/, // Pathology technical
        /^0[0-9]{4}/, // Anesthesia / Category III
    ];

    const issues = [];
    Object.values(cptDB).forEach(entry => {
        if (entry.work_rvu !== 0) return;
        
        const code = entry.code;
        const isExempt = exemptPatterns.some(p => p.test(code));
        if (isExempt) return;

        // Only flag codes in surgical range or with surgical category
        const numCode = parseInt(code);
        const isSurgicalRange = numCode >= 10000 && numCode <= 69999;
        const isSurgicalCategory = entry.category === 'Surgery';
        
        if (isSurgicalRange || isSurgicalCategory) {
            issues.push(`${code}: "${entry.description}" (${entry.specialty}) — 0 wRVU in surgical range`);
        }
    });

    addCheck(
        'Zero wRVU Surgical Codes',
        issues.length > 10 ? 'critical' : 'warning',
        issues,
        [
            'These codes appear to be placeholder entries without real wRVU data',
            'Cross-reference with CMS Physician Fee Schedule for actual wRVU values',
            'Priority: High-volume codes (TKA, THA, arthroscopy, spine) need accurate wRVU',
            'Codes with 0 wRVU will produce incorrect billing calculations',
            `Total zero-wRVU surgical codes: ${issues.length}`
        ]
    );
}

// ─── CHECK 4: Improper Bundling Logic ───────────────────────────────────────

function checkImproperBundlingLogic() {
    console.log('🔍 Check 4: Improper bundling — inclusive_of referencing non-existent codes...');
    
    const issues = [];
    
    // Check cpt_database inclusive_of references
    Object.values(cptDB).forEach(entry => {
        if (!entry.inclusive_of || entry.inclusive_of.length === 0) return;
        
        entry.inclusive_of.forEach(includedCode => {
            if (!cptDB[includedCode]) {
                issues.push(`${entry.code} inclusive_of "${includedCode}" — code not in cpt_database`);
            }
        });
    });

    // Check modifier_rules inclusive_of references
    Object.entries(modifierRules).forEach(([code, rules]) => {
        if (!rules.inclusive_of || rules.inclusive_of.length === 0) return;
        
        rules.inclusive_of.forEach(includedCode => {
            if (!cptDB[includedCode]) {
                issues.push(`modifier_rules[${code}].inclusive_of "${includedCode}" — code not in cpt_database`);
            }
        });
    });

    // Check NCCI bundles reference valid codes
    const bundles = ncciBundles.bundles || {};
    Object.entries(bundles).forEach(([primaryCode, bundle]) => {
        if (!cptDB[primaryCode]) {
            issues.push(`NCCI bundle primary "${primaryCode}" — not in cpt_database`);
        }
        (bundle.column2_codes || []).forEach(col2 => {
            if (!cptDB[col2]) {
                issues.push(`NCCI bundle ${primaryCode} column2 "${col2}" — not in cpt_database`);
            }
        });
    });

    addCheck(
        'Improper Bundling Logic (Non-existent Code References)',
        issues.length > 0 ? 'critical' : 'info',
        issues,
        [
            'Every code referenced in inclusive_of must exist in cpt_database',
            'Every NCCI bundle primary and column2 code must exist in cpt_database',
            'Missing referenced codes cause silent suppression failures',
            'Add missing codes or remove invalid references',
            `Total invalid references: ${issues.length}`
        ]
    );
}

// ─── CHECK 5: Missing Bilateral Eligibility on Paired Procedures ────────────

function checkMissingBilateralEligibility() {
    console.log('🔍 Check 5: Missing bilateral eligibility on paired procedures...');
    
    // Procedures that are inherently paired (anatomical bilateral candidates)
    const bilateralKeywords = [
        'bilateral', 'right', 'left', 'unilateral',
        'knee', 'hip', 'shoulder', 'wrist', 'ankle', 'elbow',
        'inguinal', 'femoral', 'carpal tunnel', 'tympano',
        'mastoid', 'sinus', 'nasal', 'breast',
        'nephrectomy', 'adrenalectomy', 'oophorectomy',
        'fasciotomy', 'arthroscopy', 'arthroplasty',
    ];

    // Known codes that should be bilateral-eligible
    const knownBilateralCodes = [
        '27447', '27130', '27132', '23473', '23474', // Arthroplasty
        '29880', '29881', '29882', // Arthroscopy knee
        '27601', '27602', // Fasciotomy
        '49505', '49507', '49520', '49525', // Inguinal hernia
        '19301', '19302', '19303', // Mastectomy
        '10060', '10061', // I&D
        '36818', '36819', // AV fistula
        '31254', '31256', '31267', '31276', '31287', '31288', // Sinus
        '69631', '69641', '69601', // Ear
        '50543', '50545', '50546', // Nephrectomy
    ];

    const issues = [];

    // Check known bilateral codes
    knownBilateralCodes.forEach(code => {
        if (!cptDB[code]) return;
        
        const dbEntry = cptDB[code];
        const ruleEntry = modifierRules[code];
        
        if (dbEntry && !dbEntry.bilateral_eligible) {
            issues.push(`${code} (${dbEntry.description.substring(0, 50)}): bilateral_eligible=false in cpt_database`);
        }
        if (ruleEntry && !ruleEntry.bilateral_eligible) {
            issues.push(`${code}: bilateral_eligible=false in modifier_rules`);
        }
    });

    // Scan descriptions for bilateral keywords in non-bilateral-eligible codes
    Object.values(cptDB).forEach(entry => {
        if (entry.bilateral_eligible) return;
        const desc = (entry.description || '').toLowerCase();
        
        // Only flag arthroplasty, arthroscopy, and fasciotomy codes
        if (desc.includes('arthroplasty') || desc.includes('arthroscopy') || desc.includes('fasciotomy')) {
            if (!entry.bilateral_eligible) {
                issues.push(`${entry.code} "${entry.description.substring(0, 60)}": Likely bilateral candidate but bilateral_eligible=false`);
            }
        }
    });

    // Check consistency between cpt_database and modifier_rules
    Object.keys(cptDB).forEach(code => {
        if (!modifierRules[code]) return;
        const dbBilateral = cptDB[code].bilateral_eligible;
        const rulesBilateral = modifierRules[code].bilateral_eligible;
        if (dbBilateral !== rulesBilateral) {
            issues.push(`${code}: bilateral mismatch — cpt_database=${dbBilateral}, modifier_rules=${rulesBilateral}`);
        }
    });

    addCheck(
        'Missing Bilateral Eligibility on Paired Procedures',
        issues.length > 5 ? 'warning' : 'info',
        issues,
        [
            'Review arthroplasty, arthroscopy, and fasciotomy codes for bilateral eligibility',
            'Ensure cpt_database and modifier_rules agree on bilateral_eligible',
            'Add bilateral_method (modifier_50 vs rt_lt) for all bilateral-eligible codes',
            `Total bilateral issues: ${issues.length}`
        ]
    );
}

// ─── CHECK 6: Cross-file Code Mismatches ────────────────────────────────────

function checkCrossFileMismatches() {
    console.log('🔍 Check 6: Codes in modifier_rules not in cpt_database (and vice versa)...');
    
    const issues = [];

    // Codes in modifier_rules but NOT in cpt_database
    const inRulesNotDB = [];
    modifierCodes.forEach(code => {
        if (!cptCodes.has(code)) {
            inRulesNotDB.push(code);
        }
    });
    if (inRulesNotDB.length > 0) {
        issues.push(`${inRulesNotDB.length} codes in modifier_rules but NOT in cpt_database: ${inRulesNotDB.slice(0, 20).join(', ')}${inRulesNotDB.length > 20 ? '...' : ''}`);
    }

    // Codes in cpt_database but NOT in modifier_rules (surgical codes only)
    const inDBNotRules = [];
    cptCodes.forEach(code => {
        if (modifierCodes.has(code)) return;
        const entry = cptDB[code];
        const numCode = parseInt(code);
        // Only flag surgical codes (10000-69999) that lack modifier rules
        if (numCode >= 10000 && numCode <= 69999) {
            inDBNotRules.push(`${code} (${entry.specialty})`);
        }
    });
    if (inDBNotRules.length > 0) {
        issues.push(`${inDBNotRules.length} surgical codes in cpt_database but NOT in modifier_rules: ${inDBNotRules.slice(0, 20).join(', ')}${inDBNotRules.length > 20 ? '...' : ''}`);
    }

    // Check for field consistency between matched codes
    let fieldMismatches = 0;
    cptCodes.forEach(code => {
        if (!modifierCodes.has(code)) return;
        const db = cptDB[code];
        const rules = modifierRules[code];
        
        // Check addon_code consistency
        if (db.addon_code !== rules.addon_code) {
            if (fieldMismatches < 10) {
                issues.push(`${code}: addon_code mismatch — DB=${db.addon_code}, Rules=${rules.addon_code}`);
            }
            fieldMismatches++;
        }
        // Check assistant_allowed consistency
        if (db.assistant_allowed !== rules.assistant_allowed) {
            if (fieldMismatches < 20) {
                issues.push(`${code}: assistant_allowed mismatch — DB=${db.assistant_allowed}, Rules=${rules.assistant_allowed}`);
            }
            fieldMismatches++;
        }
        // Check cosurgeon_eligible consistency
        if (db.cosurgeon_eligible !== rules.cosurgeon_eligible) {
            if (fieldMismatches < 30) {
                issues.push(`${code}: cosurgeon_eligible mismatch — DB=${db.cosurgeon_eligible}, Rules=${rules.cosurgeon_eligible}`);
            }
            fieldMismatches++;
        }
    });
    if (fieldMismatches > 0) {
        issues.push(`Total field mismatches between cpt_database and modifier_rules: ${fieldMismatches}`);
    }

    addCheck(
        'Cross-file Code Mismatches (cpt_database ↔ modifier_rules)',
        (inRulesNotDB.length > 0 || inDBNotRules.length > 10) ? 'critical' : 'warning',
        issues,
        [
            'Every surgical code in cpt_database should have a corresponding modifier_rules entry',
            'Every modifier_rules code must exist in cpt_database for engine to function',
            'Sync addon_code, assistant_allowed, cosurgeon_eligible between files',
            `Codes only in modifier_rules: ${inRulesNotDB.length}`,
            `Surgical codes only in cpt_database: ${inDBNotRules.length}`,
            `Field mismatches: ${fieldMismatches}`
        ]
    );
}

// ─── CHECK 7: Specialty Hierarchy Code Validation ───────────────────────────

function checkSpecialtyHierarchyCodes() {
    console.log('🔍 Check 7: Specialty hierarchy codes that don\'t exist in cpt_database...');
    
    const issues = [];
    let totalHierarchyCodes = 0;
    let missingCodes = 0;
    let zeroWRVUCodes = 0;

    const specialties = specialtyHierarchy.specialties || [];

    specialties.forEach(specialty => {
        const systems = specialty.systems || [];
        systems.forEach(system => {
            const groups = system.groups || [];
            groups.forEach(group => {
                const codes = group.codes || [];
                codes.forEach(code => {
                    totalHierarchyCodes++;
                    
                    if (!cptDB[code]) {
                        missingCodes++;
                        if (missingCodes <= 30) {
                            issues.push(`MISSING: ${specialty.id} → ${system.label} → ${group.label} → ${code} — not in cpt_database`);
                        }
                    } else if (cptDB[code].work_rvu === 0) {
                        zeroWRVUCodes++;
                        if (zeroWRVUCodes <= 20) {
                            issues.push(`ZERO_WRVU: ${code} in ${specialty.id}/${group.label} — has 0 wRVU (placeholder)`);
                        }
                    }
                });
            });
        });
    });

    if (missingCodes > 30) {
        issues.push(`... and ${missingCodes - 30} more missing codes`);
    }
    if (zeroWRVUCodes > 20) {
        issues.push(`... and ${zeroWRVUCodes - 20} more zero-wRVU codes`);
    }

    // Check for specialties in hierarchy but not represented in DB
    const hierarchySpecIds = specialties.map(s => s.id);
    const dbSpecialties = new Set(Object.values(cptDB).map(c => c.specialty));
    
    hierarchySpecIds.forEach(specId => {
        if (!dbSpecialties.has(specId)) {
            issues.push(`Specialty "${specId}" in hierarchy but no codes in cpt_database with this specialty`);
        }
    });

    addCheck(
        'Specialty Hierarchy Code Validation',
        missingCodes > 0 ? 'critical' : (zeroWRVUCodes > 5 ? 'warning' : 'info'),
        issues,
        [
            'All codes referenced in specialty_hierarchy.json must exist in cpt_database.json',
            'Codes with 0 wRVU in hierarchy trees break wRVU calculations for specialty views',
            `Total hierarchy codes: ${totalHierarchyCodes}`,
            `Missing from cpt_database: ${missingCodes}`,
            `Zero wRVU placeholders: ${zeroWRVUCodes}`,
            'Add missing codes or remove from hierarchy to prevent UI/calculation errors'
        ]
    );
}

// ─── Run All Checks ─────────────────────────────────────────────────────────

console.log('═══════════════════════════════════════════════════════════════');
console.log('  FreeCPTCodeFinder — Database Validation Engine');
console.log('═══════════════════════════════════════════════════════════════');
console.log(`  CPT Database:        ${Object.keys(cptDB).length} codes`);
console.log(`  Modifier Rules:      ${Object.keys(modifierRules).length} entries`);
console.log(`  NCCI Bundles:        ${Object.keys(ncciBundles.bundles || {}).length} bundles`);
console.log(`  Specialty Hierarchy: ${(specialtyHierarchy.specialties || []).length} specialties`);
console.log('═══════════════════════════════════════════════════════════════\n');

checkMissingCodesByRange();
checkIncompleteSpecialtyTrees();
checkZeroWRVUSurgicalCodes();
checkImproperBundlingLogic();
checkMissingBilateralEligibility();
checkCrossFileMismatches();
checkSpecialtyHierarchyCodes();

// ─── Print Report ───────────────────────────────────────────────────────────

console.log('\n═══════════════════════════════════════════════════════════════');
console.log('  GAP REPORT SUMMARY');
console.log('═══════════════════════════════════════════════════════════════\n');

report.checks.forEach((check, i) => {
    const icon = check.severity === 'critical' ? '🔴' : check.severity === 'warning' ? '🟡' : '🟢';
    console.log(`${icon} CHECK ${i + 1}: ${check.name}`);
    console.log(`   Severity: ${check.severity.toUpperCase()} | Issues: ${check.totalFound}`);
    
    if (check.issues.length > 0) {
        console.log('   Issues:');
        check.issues.forEach(issue => {
            console.log(`     • ${issue}`);
        });
        if (check.truncated) {
            console.log(`     ... (${check.totalFound - 50} more not shown)`);
        }
    }
    
    console.log('   Recommendations:');
    check.recommendations.forEach(rec => {
        console.log(`     → ${rec}`);
    });
    console.log('');
});

console.log('═══════════════════════════════════════════════════════════════');
console.log(`  TOTALS: ${report.totalIssues} issues found`);
console.log(`    🔴 Critical: ${report.criticalIssues}`);
console.log(`    🟡 Warning:  ${report.warningIssues}`);
console.log(`    🟢 Info:     ${report.infoIssues}`);
console.log('═══════════════════════════════════════════════════════════════');

// Exit code: non-zero if critical issues found
if (report.criticalIssues > 0) {
    console.log('\n⚠️  Critical issues detected — database needs attention before production use.');
    process.exit(1);
} else if (report.warningIssues > 0) {
    console.log('\n⚡ Warnings found — review recommended but not blocking.');
    process.exit(0);
} else {
    console.log('\n✅ All checks passed — database is in good shape.');
    process.exit(0);
}
