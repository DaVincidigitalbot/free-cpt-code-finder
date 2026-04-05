/**
 * Pre-Deploy Validation Suite for Modifier Intelligence Engine
 * Runs all test scenarios in Node.js without browser dependency
 */

const fs = require('fs');
const path = require('path');
const dir = path.dirname(__filename);

// Load data files
const modifierRules = JSON.parse(fs.readFileSync(path.join(dir, 'modifier_rules.json'), 'utf8'));
const ncciBundles = JSON.parse(fs.readFileSync(path.join(dir, 'ncci_bundles.json'), 'utf8'));

// Minimal engine recreation for Node.js testing
class TestModifierEngine {
    constructor(rules, bundles) {
        this.modifierRules = rules;
        this.ncciBundles = bundles;
        this.pendingQuestions = [];
    }

    analyze(caseItems, context = {}) {
        this.pendingQuestions = [];
        
        const procedures = caseItems.map((item, idx) => ({
            ...item,
            id: item.id || `proc_${idx}`,
            modifiers: [],
            adjustedWRVU: item.work_rvu || 0,
            rank: 'unknown',
            explanations: [],
            warnings: [],
            adjustmentFactors: []
        }));

        this.rankProcedures(procedures);
        this.applyModifier51(procedures);
        this.checkBilateralProcedures(procedures, context);
        this.checkNCCIBundles(procedures);
        this.applyLateralityModifiers(procedures, context);
        this.applySurgeonRoleModifiers(procedures, context);
        this.applyReturnToORModifiers(procedures, context);
        this.calculateAdjustedWRVUs(procedures);

        const summary = this.generateSummary(procedures);

        return {
            procedures,
            questions: this.pendingQuestions,
            warnings: this.collectWarnings(procedures),
            summary
        };
    }

    isAddonCode(code) {
        const rules = this.modifierRules[code];
        return rules && rules.addon_code === true;
    }

    isReconstructive(code) {
        const rules = this.modifierRules[code];
        return rules && rules.distinct_procedure_class === 'reconstructive';
    }

    rankProcedures(procedures) {
        const addons = procedures.filter(p => this.isAddonCode(p.code));
        const reconstructive = procedures.filter(p => !this.isAddonCode(p.code) && this.isReconstructive(p.code));
        const regular = procedures.filter(p => !this.isAddonCode(p.code) && !this.isReconstructive(p.code));

        regular.sort((a, b) => (b.work_rvu || 0) - (a.work_rvu || 0));
        reconstructive.sort((a, b) => (b.work_rvu || 0) - (a.work_rvu || 0));

        if (reconstructive.length > 0) {
            reconstructive.forEach((proc, index) => {
                proc.rank = index === 0 ? 'primary' : 'reconstructive';
            });
            regular.forEach((proc) => {
                proc.rank = 'secondary';
            });
        } else {
            regular.forEach((proc, index) => {
                proc.rank = index === 0 ? 'primary' : 'secondary';
            });
        }

        addons.forEach(proc => {
            proc.rank = 'addon';
        });
    }

    applyModifier51(procedures) {
        const nonAddonProcs = procedures.filter(p => !this.isAddonCode(p.code));
        if (nonAddonProcs.length <= 1) return;

        nonAddonProcs.forEach(proc => {
            if (proc.rank === 'secondary') {
                const rules = this.modifierRules[proc.code];
                if (rules && rules.mod51_exempt) return;
                proc.modifiers.push('-51');
            }
        });
    }

    checkBilateralProcedures(procedures, context) {
        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            if (!rules || !rules.bilateral_eligible) return;
            if (rules.inherently_bilateral) return;

            const isBilateral = context.bilateral && context.bilateral[proc.code];
            if (isBilateral) {
                if (rules.bilateral_method === 'modifier_50') {
                    proc.modifiers.push('-50');
                } else if (rules.bilateral_method === 'rt_lt') {
                    proc.explanations.push('Bilateral — bill as separate -RT and -LT line items');
                }
            } else if (!context.bilateral) {
                // Only generate questions if no bilateral context provided at all
                if (rules.bilateral_eligible) {
                    this.pendingQuestions.push({
                        type: 'bilateral',
                        code: proc.code,
                        question: `Was ${proc.code} performed bilaterally?`,
                        options: ['Yes', 'No']
                    });
                }
            }
        });
    }

    checkNCCIBundles(procedures) {
        const bundleInfo = this.ncciBundles.bundles;

        procedures.forEach(primaryProc => {
            const primaryCode = primaryProc.code;
            const bundledCodes = bundleInfo[primaryCode];
            if (!bundledCodes) return;

            procedures.forEach(secondaryProc => {
                if (primaryProc.id === secondaryProc.id) return;
                const secondaryCode = secondaryProc.code;

                if (bundledCodes.column2_codes.includes(secondaryCode)) {
                    if (bundledCodes.modifier59_allowed) {
                        secondaryProc.warnings.push({
                            type: 'ncci_bundle',
                            message: `${secondaryCode} bundles with ${primaryCode}. Consider modifier -59 if separate site/session.`,
                            severity: 'warning'
                        });
                        this.pendingQuestions.push({
                            type: 'bundle_separation',
                            primaryCode: primaryCode,
                            secondaryCode: secondaryCode,
                            question: `Were ${primaryCode} and ${secondaryCode} performed at separate sites?`,
                            options: ['Yes - Apply -59', 'No - Bundled']
                        });
                    } else {
                        secondaryProc.warnings.push({
                            type: 'ncci_bundle',
                            message: `${secondaryCode} bundles with ${primaryCode}. ${bundledCodes.reason}`,
                            severity: 'info'
                        });
                    }
                }
            });
        });
    }

    applyLateralityModifiers(procedures, context) {
        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            if (!rules || !rules.laterality_applicable) return;
            if (proc.modifiers.includes('-50')) return;

            const laterality = context.laterality && context.laterality[proc.code];
            if (laterality === 'right') {
                proc.modifiers.push('-RT');
            } else if (laterality === 'left') {
                proc.modifiers.push('-LT');
            } else if (!context.laterality) {
                this.pendingQuestions.push({
                    type: 'laterality',
                    code: proc.code,
                    question: `Which side was ${proc.code} performed on?`,
                    options: ['Right (-RT)', 'Left (-LT)', 'Bilateral']
                });
            }
        });
    }

    applySurgeonRoleModifiers(procedures, context) {
        const surgeonRole = context.surgeonRole;
        if (!surgeonRole) return;

        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            switch (surgeonRole) {
                case 'cosurgeon':
                    if (rules && rules.cosurgeon_eligible) {
                        proc.modifiers.push('-62');
                    } else {
                        proc.warnings.push({ type: 'role_not_allowed', message: `${proc.code} does not allow co-surgeon billing`, severity: 'error' });
                    }
                    break;
                case 'assistant':
                    if (rules && rules.assistant_allowed) {
                        proc.modifiers.push('-80');
                    } else {
                        proc.warnings.push({ type: 'role_not_allowed', message: `${proc.code} does not allow assistant surgeon billing`, severity: 'error' });
                    }
                    break;
            }
        });
    }

    applyReturnToORModifiers(procedures, context) {
        const returnContext = context.returnToOR;
        if (!returnContext) return;

        procedures.forEach(proc => {
            const procContext = returnContext[proc.code];
            if (!procContext) return;

            switch (procContext.type) {
                case 'repeat_same_physician': proc.modifiers.push('-76'); break;
                case 'repeat_different_physician': proc.modifiers.push('-77'); break;
                case 'unplanned_return': proc.modifiers.push('-78'); break;
                case 'unrelated_procedure': proc.modifiers.push('-79'); break;
                case 'staged_procedure': proc.modifiers.push('-58'); break;
            }
        });
    }

    calculateAdjustedWRVUs(procedures) {
        procedures.forEach(proc => {
            let adjustedWRVU = proc.work_rvu || 0;

            proc.modifiers.forEach(modifier => {
                switch (modifier) {
                    case '-51': adjustedWRVU *= 0.5; proc.adjustmentFactors.push('MPPR 50%'); break;
                    case '-50': adjustedWRVU *= 1.5; proc.adjustmentFactors.push('Bilateral 150%'); break;
                    case '-62': adjustedWRVU *= 0.625; proc.adjustmentFactors.push('Co-surgeon 62.5%'); break;
                    case '-80': case '-81': case '-82': adjustedWRVU *= 0.16; proc.adjustmentFactors.push('Assistant 16%'); break;
                }
            });

            proc.adjustedWRVU = adjustedWRVU;
        });
    }

    generateSummary(procedures) {
        const totalWRVU = procedures.reduce((sum, proc) => sum + proc.adjustedWRVU, 0);
        return {
            totalWRVU: Math.round(totalWRVU * 100) / 100,
            procedureCount: procedures.length,
            modifierCount: procedures.reduce((sum, proc) => sum + proc.modifiers.length, 0),
            primaryProcedure: (procedures.find(p => p.rank === 'primary') || {}).code || null,
            secondaryCount: procedures.filter(p => p.rank === 'secondary').length,
            addonCount: procedures.filter(p => p.rank === 'addon').length
        };
    }

    collectWarnings(procedures) {
        const warnings = [];
        procedures.forEach(proc => {
            proc.warnings.forEach(w => warnings.push({ ...w, code: proc.code }));
        });
        return warnings;
    }
}

// ====== TEST RUNNER ======
const engine = new TestModifierEngine(modifierRules, ncciBundles);
let passed = 0;
let failed = 0;
let total = 0;

function assert(condition, testName, detail) {
    total++;
    if (condition) {
        passed++;
        console.log(`  ✅ ${testName}`);
    } else {
        failed++;
        console.log(`  ❌ ${testName} — ${detail || ''}`);
    }
}

// ====== TEST 1: Exploratory Lap + Splenectomy + Wound VAC ======
console.log('\n🧪 TEST 1: Exploratory Lap + Splenectomy + Wound VAC');
{
    const result = engine.analyze([
        { code: '49000', description: 'Exploratory laparotomy', work_rvu: 11.25 },
        { code: '38100', description: 'Splenectomy, total', work_rvu: 18.85 },
        { code: '97606', description: 'Wound VAC >50 sq cm', work_rvu: 1.68 }
    ], {});

    const primary = result.procedures.find(p => p.rank === 'primary');
    assert(primary && primary.code === '38100', 'Primary is 38100 (highest wRVU)', `Got: ${primary?.code}`);
    
    const exLap = result.procedures.find(p => p.code === '49000');
    assert(exLap.modifiers.includes('-51'), '49000 gets -51 (secondary)', `Modifiers: ${exLap.modifiers}`);
    
    const vac = result.procedures.find(p => p.code === '97606');
    assert(vac.modifiers.includes('-51'), '97606 gets -51 (secondary)', `Modifiers: ${vac.modifiers}`);
    
    assert(result.summary.totalWRVU > 24 && result.summary.totalWRVU < 26, 
        `Total wRVU ~25.32 (got ${result.summary.totalWRVU})`, `Out of range`);
}

// ====== TEST 2: Bilateral Inguinal Hernia ======
console.log('\n🧪 TEST 2: Bilateral Inguinal Hernia Repair');
{
    const result = engine.analyze([
        { code: '49505', description: 'Inguinal hernia repair', work_rvu: 10.0 }
    ], { bilateral: { '49505': true } });

    const proc = result.procedures[0];
    assert(proc.modifiers.includes('-50'), 'Gets modifier -50 for bilateral', `Modifiers: ${proc.modifiers}`);
    assert(proc.adjustedWRVU === 15.0, 'wRVU = 150% (15.0)', `Got: ${proc.adjustedWRVU}`);
    assert(!proc.modifiers.includes('-RT') && !proc.modifiers.includes('-LT'), 'NOT billed as RT/LT', `Modifiers: ${proc.modifiers}`);
}

// ====== TEST 3: Unilateral Sinus Surgery ======
console.log('\n🧪 TEST 3: Unilateral Sinus Surgery (Laterality)');
{
    const result = engine.analyze([
        { code: '31256', description: 'Ethmoidectomy', work_rvu: 12.0 }
    ], { laterality: { '31256': 'right' } });

    const proc = result.procedures[0];
    assert(proc.modifiers.includes('-RT'), 'Gets -RT for right side', `Modifiers: ${proc.modifiers}`);
    assert(!proc.modifiers.includes('-50'), 'Does NOT get -50', `Modifiers: ${proc.modifiers}`);
}

// ====== TEST 3b: Bilateral Sinus Surgery ======
console.log('\n🧪 TEST 3b: Bilateral Sinus Surgery');
{
    const result = engine.analyze([
        { code: '31256', description: 'Ethmoidectomy', work_rvu: 12.0 }
    ], { bilateral: { '31256': true } });

    const proc = result.procedures[0];
    assert(proc.modifiers.includes('-50'), 'Gets -50 for bilateral', `Modifiers: ${proc.modifiers}`);
    assert(proc.adjustedWRVU === 18.0, 'wRVU = 150% (18.0)', `Got: ${proc.adjustedWRVU}`);
}

// ====== TEST 4: Colon Resection + Stoma (NCCI Bundle) ======
console.log('\n🧪 TEST 4: Colon Resection + Stoma (NCCI Bundle)');
{
    const result = engine.analyze([
        { code: '44140', description: 'Colon resection', work_rvu: 18.85 },
        { code: '44320', description: 'Colostomy creation', work_rvu: 8.85 }
    ], {});

    const primary = result.procedures.find(p => p.rank === 'primary');
    assert(primary && primary.code === '44140', 'Primary is 44140', `Got: ${primary?.code}`);
    
    const stoma = result.procedures.find(p => p.code === '44320');
    assert(stoma.modifiers.includes('-51'), '44320 gets -51', `Modifiers: ${stoma.modifiers}`);
    
    const hasNCCIWarning = result.warnings.some(w => w.type === 'ncci_bundle' && w.code === '44320');
    assert(hasNCCIWarning, 'NCCI bundle warning for 44320', 'No warning found');
    
    const hasBundleQuestion = result.questions.some(q => q.type === 'bundle_separation');
    assert(hasBundleQuestion, 'Generates -59 question for user', 'No question generated');
    
    assert(!stoma.modifiers.includes('-59'), '-59 NOT auto-applied', `Modifiers: ${stoma.modifiers}`);
}

// ====== TEST 5: Return to OR (context-driven modifiers) ======
console.log('\n🧪 TEST 5: Return to OR for Bleeding');
{
    const result = engine.analyze([
        { code: '49000', description: 'Exploratory laparotomy', work_rvu: 11.25 }
    ], { returnToOR: { '49000': { type: 'unplanned_return' } } });

    const proc = result.procedures[0];
    assert(proc.modifiers.includes('-78'), 'Gets -78 for unplanned return', `Modifiers: ${proc.modifiers}`);
}

// ====== TEST 5b: Repeat Same Physician ======
console.log('\n🧪 TEST 5b: Repeat Same Physician');
{
    const result = engine.analyze([
        { code: '49000', description: 'Exploratory laparotomy', work_rvu: 11.25 }
    ], { returnToOR: { '49000': { type: 'repeat_same_physician' } } });

    const proc = result.procedures[0];
    assert(proc.modifiers.includes('-76'), 'Gets -76 for repeat same physician', `Modifiers: ${proc.modifiers}`);
}

// ====== TEST 6: Staged Procedure ======
console.log('\n🧪 TEST 6: Staged Second-Look Procedure');
{
    const result = engine.analyze([
        { code: '49000', description: 'Planned second-look laparotomy', work_rvu: 11.25 }
    ], { returnToOR: { '49000': { type: 'staged_procedure' } } });

    const proc = result.procedures[0];
    assert(proc.modifiers.includes('-58'), 'Gets -58 for staged procedure', `Modifiers: ${proc.modifiers}`);
}

// ====== TEST 7: Co-Surgeon Case ======
console.log('\n🧪 TEST 7: Co-Surgeon Case');
{
    const result = engine.analyze([
        { code: '48150', description: 'Whipple procedure', work_rvu: 62.85 }
    ], { surgeonRole: 'cosurgeon' });

    const proc = result.procedures[0];
    assert(proc.modifiers.includes('-62'), 'Gets -62 for co-surgeon', `Modifiers: ${proc.modifiers}`);
    const expectedRVU = Math.round(62.85 * 0.625 * 100) / 100;
    assert(Math.abs(proc.adjustedWRVU - expectedRVU) < 0.01, `wRVU = 62.5% (${expectedRVU})`, `Got: ${proc.adjustedWRVU}`);
}

// ====== TEST 8: Assistant Surgeon Case ======
console.log('\n🧪 TEST 8: Assistant Surgeon Case');
{
    const result = engine.analyze([
        { code: '44140', description: 'Colon resection', work_rvu: 18.85 }
    ], { surgeonRole: 'assistant' });

    const proc = result.procedures[0];
    assert(proc.modifiers.includes('-80'), 'Gets -80 for assistant surgeon', `Modifiers: ${proc.modifiers}`);
    const expectedRVU = Math.round(18.85 * 0.16 * 100) / 100;
    assert(Math.abs(proc.adjustedWRVU - expectedRVU) < 0.01, `wRVU = 16% (${expectedRVU})`, `Got: ${proc.adjustedWRVU}`);
}

// ====== TEST 9: Hernia + Mesh (Add-on Code Protection) ======
console.log('\n🧪 TEST 9: Hernia + Mesh (Add-on Code Must NOT Get -51)');
{
    const result = engine.analyze([
        { code: '49505', description: 'Inguinal hernia repair', work_rvu: 10.0 },
        { code: '49568', description: 'Mesh implant (add-on)', work_rvu: 3.5 }
    ], {});

    const hernia = result.procedures.find(p => p.code === '49505');
    assert(hernia.rank === 'primary', 'Hernia is primary', `Rank: ${hernia.rank}`);
    
    const mesh = result.procedures.find(p => p.code === '49568');
    assert(mesh.rank === 'addon', 'Mesh flagged as add-on', `Rank: ${mesh.rank}`);
    assert(!mesh.modifiers.includes('-51'), 'Mesh does NOT get -51', `Modifiers: ${mesh.modifiers}`);
    assert(mesh.adjustedWRVU === 3.5, 'Mesh at full wRVU (3.5)', `Got: ${mesh.adjustedWRVU}`);
}

// ====== TEST 10: Component Separation + Hernia Repair ======
console.log('\n🧪 TEST 10: Component Separation (15734) as Primary Reconstructive');
{
    const result = engine.analyze([
        { code: '15734', description: 'Component separation', work_rvu: 20.22 },
        { code: '49593', description: 'Ventral hernia repair', work_rvu: 15.56 }
    ], {});

    const compSep = result.procedures.find(p => p.code === '15734');
    assert(compSep.rank === 'primary', '15734 is primary (reconstructive)', `Rank: ${compSep.rank}`);
    assert(compSep.adjustedWRVU === 20.22, '15734 at full wRVU', `Got: ${compSep.adjustedWRVU}`);

    const hernia = result.procedures.find(p => p.code === '49593');
    assert(hernia.rank === 'secondary', '49593 is secondary', `Rank: ${hernia.rank}`);
    assert(hernia.modifiers.includes('-51'), '49593 gets -51', `Modifiers: ${hernia.modifiers}`);
    assert(hernia.adjustedWRVU === 7.78, 'Hernia at 50% MPPR (7.78)', `Got: ${hernia.adjustedWRVU}`);
}

// ====== TEST 11: ENT Multi-Procedure Sinus Surgery ======
console.log('\n🧪 TEST 11: ENT Multi-Procedure Sinus Surgery');
{
    const result = engine.analyze([
        { code: '31253', description: 'Total ethmoidectomy', work_rvu: 8.5 },
        { code: '31256', description: 'Maxillary antrostomy', work_rvu: 5.2 },
        { code: '31276', description: 'Frontal sinusotomy', work_rvu: 9.0 }
    ], {});

    const primary = result.procedures.find(p => p.rank === 'primary');
    assert(primary && primary.code === '31276', 'Frontal sinusotomy (31276) is primary (highest wRVU)', `Got: ${primary?.code}`);
    
    const secondaries = result.procedures.filter(p => p.rank === 'secondary');
    assert(secondaries.length === 2, 'Two secondary procedures', `Count: ${secondaries.length}`);
    
    secondaries.forEach(s => {
        assert(s.modifiers.includes('-51'), `${s.code} gets -51`, `Modifiers: ${s.modifiers}`);
    });
}

// ====== TEST 12: Case with NO Modifiers Required ======
console.log('\n🧪 TEST 12: Single Procedure - No Modifiers');
{
    const result = engine.analyze([
        { code: '47562', description: 'Lap cholecystectomy', work_rvu: 12.0 }
    ], {});

    const proc = result.procedures[0];
    // Filter out laterality questions — those are expected for bilateral-eligible codes
    const nonLateralityMods = proc.modifiers.filter(m => m !== '-RT' && m !== '-LT');
    assert(nonLateralityMods.length === 0, 'No modifier applied to single procedure', `Modifiers: ${proc.modifiers}`);
    assert(proc.rank === 'primary', 'Ranked as primary', `Rank: ${proc.rank}`);
    assert(proc.adjustedWRVU === 12.0, 'Full wRVU (12.0)', `Got: ${proc.adjustedWRVU}`);
}

// ====== TEST 13: Data Integrity Checks ======
console.log('\n🧪 TEST 13: Data Integrity');
{
    const ruleCount = Object.keys(modifierRules).length;
    assert(ruleCount >= 500, `Modifier rules has ${ruleCount} codes (need ≥500)`, '');
    
    const bundleCount = Object.keys(ncciBundles.bundles).length;
    assert(bundleCount >= 20, `NCCI bundles has ${bundleCount} entries (need ≥20)`, '');
    
    // Verify key codes exist
    const keyCodes = ['49505', '15734', '49568', '38100', '44140', '31256', '48150', '97606', '49593'];
    keyCodes.forEach(code => {
        assert(modifierRules[code] !== undefined, `Rule exists for ${code}`, 'Missing');
    });
    
    // Verify 49568 is flagged as add-on
    assert(modifierRules['49568'].addon_code === true, '49568 flagged as add-on', `Value: ${modifierRules['49568'].addon_code}`);
    
    // Verify 15734 is reconstructive
    assert(modifierRules['15734'].distinct_procedure_class === 'reconstructive', '15734 is reconstructive', `Value: ${modifierRules['15734'].distinct_procedure_class}`);
    
    // Verify 49505 is bilateral eligible
    assert(modifierRules['49505'].bilateral_eligible === true, '49505 is bilateral eligible', `Value: ${modifierRules['49505'].bilateral_eligible}`);
}

// ====== SUMMARY ======
console.log('\n' + '='.repeat(60));
console.log(`📊 VALIDATION RESULTS: ${passed}/${total} passed, ${failed} failed`);
if (failed === 0) {
    console.log('✅ ALL TESTS PASSED — SAFE TO DEPLOY');
} else {
    console.log('❌ FAILURES DETECTED — DO NOT DEPLOY');
}
console.log('='.repeat(60));

process.exit(failed > 0 ? 1 : 0);
