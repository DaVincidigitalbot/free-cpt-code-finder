/**
 * Enhanced Modifier Intelligence Engine for FreeCPTCodeFinder.com
 * 
 * Analyzes CPT code combinations and automatically assigns appropriate modifiers
 * based on NCCI guidelines, CMS rules, clinical hierarchies, and payer context.
 * 
 * @author FreeCPTCodeFinder.com
 * @version 2.0.0 - Surgical Billing Intelligence
 */

class ModifierEngine {
    constructor() {
        this.modifierRules = null;
        this.ncciBundles = null;
        this.pendingQuestions = [];
        this.userResponses = {};
        this.debugMode = false;
        this.auditTrail = [];
    }

    /**
     * Initialize the engine by loading rule data
     */
    async initialize() {
        const perfToken = window.PerfProfiler?.start('ModifierEngine.initialize', { blocksUI: false, category: 'fetch' });
        try {
            // Load modifier rules and NCCI bundles
            const rulesFetchToken = window.PerfProfiler?.start('fetch:modifier_rules.json', { blocksUI: false, category: 'fetch' });
            const bundlesFetchToken = window.PerfProfiler?.start('fetch:ncci_bundles.json', { blocksUI: false, category: 'fetch' });
            const [rulesResponse, bundlesResponse] = await Promise.all([
                fetch('./modifier_rules.json'),
                fetch('./ncci_bundles.json')
            ]);
            window.PerfProfiler?.end(rulesFetchToken, { status: rulesResponse.status });
            window.PerfProfiler?.end(bundlesFetchToken, { status: bundlesResponse.status });

            const rulesParseToken = window.PerfProfiler?.start('parse:modifier_rules.json', { blocksUI: false, category: 'parse' });
            this.modifierRules = await rulesResponse.json();
            window.PerfProfiler?.end(rulesParseToken, { ruleCount: Object.keys(this.modifierRules).length });

            const bundlesParseToken = window.PerfProfiler?.start('parse:ncci_bundles.json', { blocksUI: false, category: 'parse' });
            this.ncciBundles = await bundlesResponse.json();
            window.PerfProfiler?.end(bundlesParseToken, { bundleCount: Object.keys(this.ncciBundles.bundles).length });
            
            console.log('🧠 Enhanced Modifier Intelligence Engine initialized successfully');
            console.log(`📊 Loaded ${Object.keys(this.modifierRules).length} CPT rules`);
            console.log(`📊 Loaded ${Object.keys(this.ncciBundles.bundles).length} NCCI bundles`);
            window.PerfProfiler?.end(perfToken, { ruleCount: Object.keys(this.modifierRules).length, bundleCount: Object.keys(this.ncciBundles.bundles).length });
            return true;
        } catch (error) {
            console.error('❌ Failed to initialize Enhanced Modifier Engine:', error);
            window.PerfProfiler?.end(perfToken, { error: error.message });
            return false;
        }
    }

    /**
     * Main analysis function - analyzes case and returns modifier assignments
     * @param {Array} caseItems - Array of procedure objects with CPT codes and wRVUs
     * @param {Object} context - Additional context (bilateral, surgeon role, payer, global period, etc.)
     * @returns {Object} Analysis results with modifier assignments and explanations
     */
    analyze(caseItems, context = {}) {
        const perfToken = window.PerfProfiler?.start('ModifierEngine.analyze', { blocksUI: true, category: 'compute', caseCount: caseItems?.length || 0 });
        if (!this.modifierRules || !this.ncciBundles) {
            window.PerfProfiler?.end(perfToken, { error: 'not_initialized' });
            throw new Error('Enhanced Modifier Engine not initialized. Call initialize() first.');
        }

        if (!caseItems || caseItems.length === 0) {
            window.PerfProfiler?.end(perfToken, { caseCount: 0, skipped: 'empty case' });
            return { 
                procedures: [], 
                questions: [], 
                warnings: [], 
                auditTrail: [],
                summary: {} 
            };
        }

        // Reset state
        this.pendingQuestions = [];
        this.auditTrail = [];
        
        // Create working copy of procedures
        const procedures = caseItems.map(item => ({
            ...item,
            modifiers: [],
            adjustedWRVU: item.work_rvu || 0,
            rank: 'unknown',
            explanations: [],
            warnings: [],
            auditRisk: 'low',
            hierarchyTier: 3
        }));

        this.addAuditEntry('analysis_start', null, 'Beginning case analysis', { procedureCount: procedures.length });

        // Step 1: Check procedure hierarchies and determine primary procedures
        this.checkProcedureHierarchy(procedures);

        // Step 2: Rank procedures by hierarchy tier and wRVU
        this.rankProcedures(procedures);

        // Step 3: Apply payer-aware logic
        this.applyPayerLogic(procedures, context.payerType || 'medicare');

        // Step 4: Check global period context
        this.checkGlobalPeriod(procedures, context);

        // Step 5: Apply modifier -51 (Multiple Procedures) 
        this.applyModifier51(procedures);

        // Step 6: Check for bilateral procedures
        this.checkBilateralProcedures(procedures, context);

        // Step 7: Check for NCCI bundles and enhanced bundling logic
        this.checkEnhancedNCCIBundles(procedures, context);
        this.applyDiagnosticLaparoscopyOverride(procedures, context);

        // Step 8: Apply laterality modifiers (-RT/-LT)
        this.applyLateralityModifiers(procedures, context);

        // Step 9: Apply surgeon role modifiers
        this.applySurgeonRoleModifiers(procedures, context);

        // Step 10: Apply return to OR modifiers
        this.applyReturnToORModifiers(procedures, context);

        // Step 10.5: Apply incomplete/reduced service modifiers  
        this.applyReducedServiceModifiers(procedures, context);

        // Step 11: Auto-suggest modifiers based on intelligent analysis
        this.autoSuggestModifiers(procedures, context);

        // Step 12: Calculate final adjusted wRVUs
        this.calculateAdjustedWRVUs(procedures);

        // Generate summary and audit trail
        const summary = this.generateSummary(procedures);
        this.addAuditEntry('analysis_complete', null, 'Case analysis completed', summary);

        // Calculate confidence score
        const confidence = this.calculateConfidence({
            procedures,
            questions: this.pendingQuestions,
            warnings: this.collectWarnings(procedures),
            summary
        });

        // Check for blocking issues
        const blockingIssues = this.checkForBlockingIssues({
            procedures,
            questions: this.pendingQuestions,
            warnings: this.collectWarnings(procedures),
            confidence
        });

        const result = {
            procedures,
            questions: this.pendingQuestions,
            warnings: this.collectWarnings(procedures),
            auditTrail: this.auditTrail,
            summary,
            confidence,
            blockingIssues,
            auditMode: this.generateAuditOutput(procedures, confidence, blockingIssues),
            debugInfo: this.debugMode ? this.generateDebugInfo(procedures) : null
        };
        window.PerfProfiler?.end(perfToken, {
            caseCount: procedures.length,
            questionCount: this.pendingQuestions.length,
            warningCount: result.warnings.length,
            auditEntries: this.auditTrail.length
        });
        return result;
    }

    /**
     * FIX 1: INHERENT PROCEDURE SUPPRESSION - Properly handle inclusive relationships
     */
    checkProcedureHierarchy(procedures) {
        this.addAuditEntry('hierarchy_check', null, 'Checking procedure hierarchies and inclusive relationships');

        // FIRST PASS: Set all hierarchy tiers from rules data
        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            if (rules) {
                proc.hierarchyTier = rules.hierarchy_tier || 3;
                proc.codeFamily = rules.code_family || 'unclassified';
            }
        });

        // SECOND PASS: Check inclusive relationships - REMOVE included procedures entirely
        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            if (!rules) return;

            // Check if this procedure includes others (inclusive_of)
            if (rules.inclusive_of && rules.inclusive_of.length > 0) {
                procedures.forEach(otherProc => {
                    if (otherProc.id !== proc.id && rules.inclusive_of.includes(otherProc.code)) {
                        otherProc.warnings.push({
                            type: 'included_procedure',
                            message: `${otherProc.code} included in ${proc.code} — not separately billable`,
                            severity: 'info'
                        });
                        otherProc.rank = 'included';
                        otherProc.adjustedWRVU = 0;  // Force to $0
                        otherProc.explanations = otherProc.explanations || [];
                        otherProc.explanations.push(`Included in primary procedure ${proc.code} — not separately billable`);
                        
                        this.addAuditEntry('procedure_suppressed', proc.code, 
                            `${otherProc.code} suppressed (included in ${proc.code})`, 
                            { reason: 'inherent_inclusion', primaryCode: proc.code });
                    }
                });
            }

            // Check never_primary_with rules (hierarchy demotion)
            if (rules.never_primary_with && rules.never_primary_with.length > 0) {
                procedures.forEach(primaryProc => {
                    if (primaryProc.id !== proc.id && rules.never_primary_with.includes(primaryProc.code)) {
                        proc.warnings.push({
                            type: 'hierarchy_violation',
                            message: `${proc.code} should not be primary when performed with ${primaryProc.code}`,
                            severity: 'warning'
                        });
                        
                        // Force reordering - primary procedure takes precedence
                        proc.hierarchyTier = Math.max(proc.hierarchyTier, primaryProc.hierarchyTier + 1);
                        
                        this.addAuditEntry('hierarchy_demotion', proc.code,
                            `${proc.code} demoted (tier→${proc.hierarchyTier}) due to ${primaryProc.code}`,
                            { primaryProcedure: primaryProc.code });
                    }
                });
            }
        });
    }

    /**
     * ENHANCED: Rank procedures by hierarchy tier first, then wRVU
     */
    rankProcedures(procedures) {
        // Filter out included procedures
        const activeProcedures = procedures.filter(p => p.rank !== 'included');
        const addons = activeProcedures.filter(p => this.isAddonCode(p.code));
        const reconstructive = activeProcedures.filter(p => !this.isAddonCode(p.code) && this.isReconstructive(p.code));
        const regular = activeProcedures.filter(p => !this.isAddonCode(p.code) && !this.isReconstructive(p.code));

        // Sort by hierarchy tier first (lower tier = more complex), then by wRVU
        regular.sort((a, b) => {
            if (a.hierarchyTier !== b.hierarchyTier) {
                return a.hierarchyTier - b.hierarchyTier; // Tier 1 = most complex comes first
            }
            return (b.work_rvu || 0) - (a.work_rvu || 0); // Then by wRVU descending
        });
        
        reconstructive.sort((a, b) => {
            if (a.hierarchyTier !== b.hierarchyTier) {
                return a.hierarchyTier - b.hierarchyTier;
            }
            return (b.work_rvu || 0) - (a.work_rvu || 0);
        });

        // Assign ranks based on hierarchy
        if (reconstructive.length > 0) {
            reconstructive.forEach((proc, index) => {
                proc.rank = index === 0 ? 'primary' : 'reconstructive';
                proc.explanations.push(
                    index === 0 
                        ? `Primary procedure - Tier ${proc.hierarchyTier} reconstructive (highest complexity)`
                        : 'Distinct reconstructive procedure - billed separately'
                );
                
                this.addAuditEntry('rank_assigned', proc.code, `Ranked as ${proc.rank}`, 
                    { tier: proc.hierarchyTier, reason: 'reconstructive' });
            });
            
            regular.forEach((proc, index) => {
                proc.rank = 'secondary';
                proc.explanations.push('Secondary to reconstructive procedure');
                
                this.addAuditEntry('rank_assigned', proc.code, 'Ranked as secondary', 
                    { reason: 'secondary_to_reconstructive' });
            });
        } else {
            regular.forEach((proc, index) => {
                proc.rank = index === 0 ? 'primary' : 'secondary';
                proc.explanations.push(
                    index === 0 
                        ? `Primary procedure - Tier ${proc.hierarchyTier}, highest wRVU (${proc.work_rvu})`
                        : `Secondary procedure - Tier ${proc.hierarchyTier}, ranked #${index + 1} by complexity/wRVU`
                );
                
                this.addAuditEntry('rank_assigned', proc.code, `Ranked as ${proc.rank}`, 
                    { tier: proc.hierarchyTier, wRVU: proc.work_rvu });
            });
        }

        addons.forEach(proc => {
            proc.rank = 'addon';
            proc.explanations.push('Add-on code - always billed at full value, no modifier -51');
            
            this.addAuditEntry('rank_assigned', proc.code, 'Ranked as add-on', 
                { reason: 'addon_code' });
        });
    }

    /**
     * NEW: Apply payer-aware logic (Medicare vs Commercial)
     */
    applyPayerLogic(procedures, payerType) {
        this.addAuditEntry('payer_logic', null, `Applying ${payerType} payer rules`);

        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            if (!rules) return;

            // Add payer-specific notes
            if (rules.payer_notes) {
                if (payerType === 'medicare' && rules.payer_notes.medicare) {
                    proc.explanations.push(`Medicare: ${rules.payer_notes.medicare}`);
                }
                if (payerType === 'commercial' && rules.payer_notes.commercial) {
                    proc.explanations.push(`Commercial: ${rules.payer_notes.commercial}`);
                }
            }

            // Set X modifier eligibility for Medicare
            if (payerType === 'medicare' && rules.x_modifier_eligible) {
                proc._xModifierEligible = true;
                proc.explanations.push('Eligible for X{EPSU} modifiers (Medicare)');
            } else if (payerType === 'commercial') {
                proc._xModifierEligible = false;
                proc.explanations.push('Use modifier -59 for commercial payers');
            }
        });
    }

    /**
     * NEW: Check global period context and require appropriate modifiers
     */
    checkGlobalPeriod(procedures, context) {
        if (!context.withinGlobalPeriod) return;

        this.addAuditEntry('global_period_check', null, 'Checking global period context');

        procedures.forEach(proc => {
            if (context.globalPeriodRelationship) {
                const relationship = context.globalPeriodRelationship;
                
                switch (relationship) {
                    case 'staged':
                        proc.modifiers.push('-58');
                        proc.explanations.push('Modifier -58: Staged procedure during global period');
                        proc.auditRisk = 'medium';
                        
                        this.addAuditEntry('global_modifier', proc.code, 'Applied -58 for staged procedure');
                        break;
                        
                    case 'unplanned_related':
                        proc.modifiers.push('-78');
                        proc.explanations.push('Modifier -78: Unplanned return to OR during global period');
                        proc.auditRisk = 'medium';
                        
                        this.addAuditEntry('global_modifier', proc.code, 'Applied -78 for unplanned return');
                        break;
                        
                    case 'unrelated':
                        // E/M codes get -24, not -79
                        if (proc.code.startsWith('99') && (proc.code.startsWith('991') || proc.code.startsWith('992') || proc.code.startsWith('993') || proc.code.startsWith('994'))) {
                            proc.modifiers.push('-24');
                            proc.explanations.push('Modifier -24: Unrelated E/M service during global period');
                        } else {
                            proc.modifiers.push('-79');
                            proc.explanations.push('Modifier -79: Unrelated procedure during global period');
                        }
                        proc.auditRisk = 'low';
                        
                        this.addAuditEntry('global_modifier', proc.code, 'Applied unrelated global period modifier');
                        break;
                }
            } else {
                // No modifier selected - block billing
                proc.warnings.push({
                    type: 'global_period_violation',
                    message: 'Procedure performed within global period requires modifier (-58, -78, or -79)',
                    severity: 'error'
                });
                proc.auditRisk = 'high';
                
                this.addAuditEntry('global_period_error', proc.code, 'Missing required global period modifier');
            }
        });
    }

    /**
     * ENHANCED: Check NCCI bundles with advanced bundling logic
     */
    checkEnhancedNCCIBundles(procedures, context) {
        this.addAuditEntry('ncci_check', null, 'Checking enhanced NCCI bundles');

        const bundleInfo = this.ncciBundles.bundles;

        procedures.forEach(primaryProc => {
            const primaryCode = primaryProc.code;
            const bundledCodes = bundleInfo[primaryCode];
            
            if (!bundledCodes) return;

            procedures.forEach(secondaryProc => {
                if (primaryProc.id === secondaryProc.id) return;
                if (secondaryProc.rank === 'included') return; // Skip suppressed procedures
                
                const secondaryCode = secondaryProc.code;
                
                if (bundledCodes.column2_codes.includes(secondaryCode)) {
                    if (bundledCodes.modifier59_allowed) {
                        // Generate intelligent suggestion
                        const suggestion = this.generateBundleSuggestion(primaryCode, secondaryCode, bundledCodes, context);
                        
                        secondaryProc.warnings.push({
                            type: 'ncci_bundle',
                            message: suggestion.message,
                            severity: 'warning',
                            suggestion: suggestion
                        });
                        
                        this.addAuditEntry('ncci_bundle_detected', secondaryCode, 
                            `Bundled with ${primaryCode}`, { suggestion: suggestion.type });
                            
                    } else {
                        secondaryProc.warnings.push({
                            type: 'ncci_bundle',
                            message: `${secondaryCode} bundles with ${primaryCode}. ${bundledCodes.reason}`,
                            severity: 'info'
                        });
                        secondaryProc.auditRisk = 'low';
                        
                        this.addAuditEntry('ncci_bundle_blocked', secondaryCode,
                            `Cannot unbundle from ${primaryCode}`, { reason: bundledCodes.reason });
                    }
                }
            });
        });
    }

    /**
     * NEW: Generate intelligent bundle suggestions
     */
    generateBundleSuggestion(primaryCode, secondaryCode, bundleData, context) {
        const payerType = context.payerType || 'medicare';
        const suggestedModifier = payerType === 'medicare' ? '-59 or X{EPSU}' : '-59';
        
        // Determine suggestion confidence based on bundling reason
        if (bundleData.description.includes('separate site')) {
            return {
                type: 'separate_site',
                modifier: suggestedModifier,
                message: `💡 ${secondaryCode} may be unbundled with ${suggestedModifier} if performed at anatomically separate site`,
                confidence: 'medium'
            };
        } else if (bundleData.description.includes('different session')) {
            return {
                type: 'separate_session',
                modifier: suggestedModifier,
                message: `💡 ${secondaryCode} may be unbundled with ${suggestedModifier} if performed in separate session`,
                confidence: 'high'
            };
        } else if (bundleData.description.includes('extensive')) {
            return {
                type: 'extensive',
                modifier: `${suggestedModifier} + -22`,
                message: `💡 ${secondaryCode} may be unbundled with ${suggestedModifier} if extensive and unrelated. Consider -22 for complexity.`,
                confidence: 'low'
            };
        }
        
        return {
            type: 'standard',
            modifier: suggestedModifier,
            message: `💡 ${secondaryCode} bundles with ${primaryCode}. Consider ${suggestedModifier} if separate circumstances documented.`,
            confidence: 'medium'
        };
    }

    /**
     * ENHANCED: Auto-suggest modifiers with confidence levels
     */
    autoSuggestModifiers(procedures, context) {
        this.addAuditEntry('auto_suggest', null, 'Generating auto-suggestions');

        procedures.forEach(proc => {
            const suggestions = [];
            
            // Bilateral detection
            if (this.isBilateralEligible(proc.code) && !proc.modifiers.includes('-50')) {
                suggestions.push({
                    type: 'bilateral',
                    modifier: '-50',
                    message: `💡 Was ${proc.code} performed bilaterally? Consider modifier -50`,
                    confidence: 'medium',
                    action: 'question_bilateral'
                });
            }
            
            // NCCI override suggestion
            if (proc.warnings.some(w => w.type === 'ncci_bundle' && w.suggestion)) {
                const bundleWarning = proc.warnings.find(w => w.type === 'ncci_bundle' && w.suggestion);
                suggestions.push({
                    type: 'ncci_override',
                    modifier: bundleWarning.suggestion.modifier,
                    message: bundleWarning.suggestion.message,
                    confidence: bundleWarning.suggestion.confidence,
                    action: 'apply_modifier'
                });
            }
            
            // Duplicate CPT detection
            const duplicates = procedures.filter(p => p.code === proc.code && p.id !== proc.id);
            if (duplicates.length > 0) {
                suggestions.push({
                    type: 'duplicate_cpt',
                    modifier: '-59 or -76/-77',
                    message: `💡 Duplicate ${proc.code} detected. Was this bilateral (-50), repeat procedure (-76/-77), or distinct service (-59)?`,
                    confidence: 'high',
                    action: 'question_duplicate'
                });
            }
            
            proc.suggestions = suggestions;
        });
    }

    /**
     * ENHANCED: Generate comprehensive audit trail
     */
    generateAuditTrail(procedures) {
        const auditData = {
            timestamp: new Date().toISOString(),
            analysisSteps: this.auditTrail,
            procedureDecisions: procedures.map(proc => ({
                code: proc.code,
                rank: proc.rank,
                modifiers: proc.modifiers,
                hierarchyTier: proc.hierarchyTier,
                auditRisk: proc.auditRisk,
                reasoningChain: proc.explanations,
                warnings: proc.warnings.length,
                suggestions: (proc.suggestions || []).length
            })),
            riskAssessment: this.calculateRiskAssessment(procedures),
            billingCompliance: this.assessBillingCompliance(procedures)
        };
        
        return auditData;
    }

    /**
     * Helper: Add entry to audit trail
     */
    addAuditEntry(action, cptCode, description, metadata = {}) {
        this.auditTrail.push({
            timestamp: new Date().toISOString(),
            action,
            cptCode,
            description,
            metadata
        });
    }

    /**
     * Helper: Calculate overall risk assessment
     */
    calculateRiskAssessment(procedures) {
        const riskCounts = procedures.reduce((acc, proc) => {
            acc[proc.auditRisk] = (acc[proc.auditRisk] || 0) + 1;
            return acc;
        }, {});
        
        const totalProcs = procedures.length;
        const highRiskProcs = riskCounts.high || 0;
        const mediumRiskProcs = riskCounts.medium || 0;
        
        let overallRisk = 'low';
        if (highRiskProcs > 0) {
            overallRisk = 'high';
        } else if (mediumRiskProcs > totalProcs / 2) {
            overallRisk = 'medium';
        }
        
        return {
            overall: overallRisk,
            breakdown: riskCounts,
            riskFactors: procedures
                .filter(p => p.auditRisk !== 'low')
                .map(p => `${p.code} (${p.auditRisk})`)
        };
    }

    /**
     * Helper: Assess billing compliance
     */
    assessBillingCompliance(procedures) {
        const issues = [];
        const includedProcs = procedures.filter(p => p.rank === 'included').length;
        const missingModifiers = procedures.filter(p => 
            p.warnings.some(w => w.type === 'global_period_violation')
        ).length;
        const bundleViolations = procedures.filter(p =>
            p.warnings.some(w => w.type === 'ncci_bundle' && w.severity === 'error')
        ).length;
        
        if (includedProcs > 0) {
            issues.push(`${includedProcs} procedures marked as included - cannot be billed`);
        }
        if (missingModifiers > 0) {
            issues.push(`${missingModifiers} procedures missing required global period modifiers`);
        }
        if (bundleViolations > 0) {
            issues.push(`${bundleViolations} NCCI bundle violations detected`);
        }
        
        return {
            compliant: issues.length === 0,
            issues,
            score: Math.max(0, 100 - (issues.length * 20))
        };
    }

    /**
     * NEW: Run clinical validation test scenarios
     */
    runClinicalValidation() {
        console.log('🧪 Running clinical validation scenarios...');
        
        const scenarios = [
            {
                name: 'Trauma laparotomy',
                codes: ['49000', '38100', '44120', '97606'],
                expected: {
                    primary: ['38100', '44120'], // NOT 49000
                    bundled: ['49000'],
                    modifiers: ['-51']
                }
            },
            {
                name: 'ENT multi-sinus bilateral',
                codes: ['31253', '31256', '31276'],
                context: { bilateral: true },
                expected: {
                    excluded: ['31254'], // Included in 31253
                    modifiers: ['-50'],
                    primary: '31253'
                }
            },
            {
                name: 'CABG with vein harvest',
                codes: ['33535', '33508'],
                expected: {
                    primary: '33535',
                    addon: '33508',
                    noModifier51: ['33508']
                }
            },
            {
                name: 'Re-operation within global',
                codes: ['49000'],
                context: { 
                    withinGlobalPeriod: true,
                    priorProcedure: '44140',
                    daysAgo: 30
                },
                expected: {
                    requiredModifiers: ['-78', '-79'],
                    blockWithoutModifier: true
                }
            },
            {
                name: 'Bilateral inguinal hernia',
                codes: ['49505', '49505'],
                expected: {
                    singleLine: true,
                    modifier: '-50',
                    notTwoLines: true
                }
            },
            {
                name: 'Component separation + hernia',
                codes: ['15734', '49593'],
                expected: {
                    primary: '15734',
                    secondary: '49593',
                    modifiers: ['-51']
                }
            },
            {
                name: 'Critical care bundling',
                codes: ['99291', '36556', '31500'],
                expected: {
                    included: ['36556', '31500'],
                    billableSeparately: false
                }
            }
        ];
        
        const results = scenarios.map(scenario => this.validateScenario(scenario));
        
        console.log('🧪 Validation Results:');
        results.forEach((result, index) => {
            const status = result.passed ? '✅ PASS' : '❌ FAIL';
            console.log(`${status}: ${scenarios[index].name}`);
            if (!result.passed) {
                console.log(`   Issues: ${result.issues.join(', ')}`);
            }
        });
        
        return results;
    }

    /**
     * Helper: Validate individual scenario
     */
    validateScenario(scenario) {
        // Convert codes to mock case items
        const caseItems = scenario.codes.map((code, index) => ({
            id: `test_${index}`,
            code: code,
            work_rvu: this.getMockWRVU(code),
            description: `Test procedure ${code}`
        }));
        
        const analysis = this.analyze(caseItems, scenario.context || {});
        const issues = [];
        
        // Validate expected results
        if (scenario.expected.primary) {
            const primaryProcs = analysis.procedures.filter(p => p.rank === 'primary');
            const expectedPrimary = Array.isArray(scenario.expected.primary) 
                ? scenario.expected.primary 
                : [scenario.expected.primary];
            
            if (!expectedPrimary.some(code => primaryProcs.some(p => p.code === code))) {
                issues.push(`Expected primary ${expectedPrimary.join(' or ')}, got ${primaryProcs.map(p => p.code).join(', ')}`);
            }
        }
        
        if (scenario.expected.bundled) {
            scenario.expected.bundled.forEach(code => {
                const proc = analysis.procedures.find(p => p.code === code);
                if (!proc || proc.rank !== 'included') {
                    issues.push(`Expected ${code} to be bundled`);
                }
            });
        }
        
        if (scenario.expected.requiredModifiers) {
            scenario.expected.requiredModifiers.forEach(modifier => {
                const hasModifier = analysis.procedures.some(p => p.modifiers.includes(modifier));
                if (!hasModifier) {
                    issues.push(`Missing required modifier ${modifier}`);
                }
            });
        }
        
        return {
            passed: issues.length === 0,
            issues,
            analysis
        };
    }

    /**
     * Helper: Get mock wRVU for testing
     */
    getMockWRVU(code) {
        const mockRVUs = {
            '49000': 10.5, '38100': 18.2, '44120': 22.1, '97606': 2.1,
            '31253': 8.5, '31256': 6.2, '31276': 7.8,
            '33535': 45.2, '33508': 8.1,
            '15734': 25.3, '49593': 18.7,
            '99291': 4.5, '36556': 2.1, '31500': 1.8,
            '49505': 12.3
        };
        return mockRVUs[code] || 5.0;
    }

    // ========================================================================
    // EXISTING METHODS (Enhanced where noted)
    // ========================================================================

    /**
     * Apply modifier -51 (Multiple Procedures)
     */
    applyModifier51(procedures) {
        const nonAddonProcs = procedures.filter(p => !this.isAddonCode(p.code) && p.rank !== 'included');
        
        if (nonAddonProcs.length <= 1) return;

        nonAddonProcs.forEach(proc => {
            if (proc.rank === 'secondary') {
                const rules = this.modifierRules[proc.code];
                
                // Check if exempt from modifier -51
                if (rules && rules.mod51_exempt) {
                    proc.explanations.push('Exempt from modifier -51 per CMS guidelines');
                    this.addAuditEntry('mod51_exempt', proc.code, 'Exempt from modifier -51');
                    return;
                }

                proc.modifiers.push('-51');
                proc.explanations.push('Modifier -51: Multiple procedure performed in same session');
                this.addAuditEntry('mod51_applied', proc.code, 'Applied modifier -51 for multiple procedures');
            }
        });
    }

    /**
     * Check for bilateral procedures and apply modifier -50
     * Handles: user-selected bilateral, duplicate CPT consolidation, RT/LT pairs
     */
    checkBilateralProcedures(procedures, context) {
        // STEP 1: Check if user explicitly set bilateral on any procedure
        procedures.forEach(proc => {
            if (proc.rank === 'included' || proc.rank === 'suppressed') return;
            if (proc.modifiers.includes('-50')) return; // Already has it
            
            const rules = this.modifierRules[proc.code];
            if (!rules || !rules.bilateral_eligible) return;
            
            if (rules.inherently_bilateral) {
                proc.explanations.push('Inherently bilateral procedure — no modifier -50 needed');
                return;
            }
            
            // Check if user specified bilateral via proc.bilateral or proc.laterality
            const isBilateral = proc.bilateral === true || proc.laterality === 'bilateral';
            
            // Also check context.bilateral map
            const contextBilateral = context.bilateral === true || 
                (context.bilateral && context.bilateral[proc.code]);
            
            if (isBilateral || contextBilateral) {
                if (rules.bilateral_method === 'modifier_50') {
                    proc.modifiers.push('-50');
                    proc.explanations.push('Modifier -50: Bilateral procedure (150% payment)');
                    this.addAuditEntry('bilateral_mod50', proc.code, 'Applied modifier -50 for bilateral procedure');
                } else if (rules.bilateral_method === 'rt_lt') {
                    proc.explanations.push('Bilateral procedure — bill as separate -RT and -LT line items');
                    this.addAuditEntry('bilateral_rtlt', proc.code, 'Bilateral requires -RT/-LT line items, not -50');
                } else if (rules.bilateral_method === 'units_2') {
                    proc.explanations.push('Bilateral procedure — bill as single line with units = 2');
                    this.addAuditEntry('bilateral_units', proc.code, 'Bilateral with units = 2');
                } else {
                    // Default to modifier -50 if method not specified
                    proc.modifiers.push('-50');
                    proc.explanations.push('Modifier -50: Bilateral procedure (default)');
                    this.addAuditEntry('bilateral_mod50_default', proc.code, 'Applied -50 (default bilateral method)');
                }
            }
        });
        
        // STEP 2: Check for duplicate codes that should be consolidated as bilateral
        // (L + R same code = should be -50 instead of two lines)
        const codeCounts = {};
        procedures.forEach(proc => {
            if (proc.rank === 'included' || proc.rank === 'suppressed') return;
            codeCounts[proc.code] = (codeCounts[proc.code] || 0) + 1;
        });
        
        Object.entries(codeCounts).forEach(([code, count]) => {
            if (count >= 2) {
                const rules = this.modifierRules[code];
                const dupes = procedures.filter(p => p.code === code && p.rank !== 'included');
                
                // Check if dupes have RT + LT (should consolidate to -50 if eligible)
                const hasRT = dupes.some(p => p.modifiers.includes('-RT') || p.laterality === 'right');
                const hasLT = dupes.some(p => p.modifiers.includes('-LT') || p.laterality === 'left');
                
                if (rules && rules.bilateral_eligible && rules.bilateral_method === 'modifier_50' && hasRT && hasLT) {
                    // Consolidate RT+LT into bilateral -50 on first entry
                    const primary = dupes[0];
                    primary.modifiers = primary.modifiers.filter(m => m !== '-RT' && m !== '-LT');
                    if (!primary.modifiers.includes('-50')) {
                        primary.modifiers.push('-50');
                    }
                    primary.laterality = 'bilateral';
                    primary.explanations.push('Modifier -50: Bilateral (consolidated from RT+LT duplicate lines)');
                    this.addAuditEntry('bilateral_consolidation', code, `Consolidated ${count} duplicate ${code} RT+LT into bilateral -50`);
                    
                    // Suppress other entries
                    for (let i = 1; i < dupes.length; i++) {
                        dupes[i].rank = 'suppressed';
                        dupes[i].adjustedWRVU = 0;
                        dupes[i].warnings.push({
                            type: 'bilateral_consolidation',
                            message: `Duplicate ${code} consolidated into bilateral -50 on first line`,
                            severity: 'info'
                        });
                    }
                } else if (rules && rules.bilateral_eligible && count >= 2 && !hasRT && !hasLT) {
                    // Duplicate without laterality — flag for user decision
                    dupes.forEach((proc, idx) => {
                        if (idx > 0) {
                            proc.warnings.push({
                                type: 'duplicate_needs_resolution',
                                message: `Duplicate ${code} — add laterality (RT/LT), -50 bilateral, -76/-77 repeat, or -59 distinct`,
                                severity: 'warning'
                            });
                        }
                    });
                }
            }
        });
    }

    /**
     * Apply laterality modifiers (-RT/-LT)
     */
    applyLateralityModifiers(procedures, context) {
        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            if (!rules || !rules.laterality_applicable) return;

            // Skip if already has bilateral modifier
            if (proc.modifiers.includes('-50')) return;

            const laterality = context.laterality && context.laterality[proc.code];
            
            if (laterality === 'right') {
                proc.modifiers.push('-RT');
                proc.explanations.push('Modifier -RT: Right side procedure');
                this.addAuditEntry('laterality_rt', proc.code, 'Applied -RT modifier');
            } else if (laterality === 'left') {
                proc.modifiers.push('-LT');
                proc.explanations.push('Modifier -LT: Left side procedure');
                this.addAuditEntry('laterality_lt', proc.code, 'Applied -LT modifier');
            } else {
                // Generate question for laterality
                this.pendingQuestions.push({
                    type: 'laterality',
                    code: proc.code,
                    question: `Which side was ${proc.code} performed on?`,
                    options: ['Right (-RT)', 'Left (-LT)', 'Bilateral']
                });
            }
        });
    }

    /**
     * Apply surgeon role modifiers (-62, -80, -81, -82, -AS)
     */
    applySurgeonRoleModifiers(procedures, context) {
        const surgeonRole = context.surgeonRole;
        if (!surgeonRole) return;

        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            
            switch (surgeonRole) {
                case 'cosurgeon':
                    if (rules && rules.cosurgeon_eligible) {
                        proc.modifiers.push('-62');
                        proc.explanations.push('Modifier -62: Co-surgeon');
                        this.addAuditEntry('surgeon_role', proc.code, 'Applied -62 for co-surgeon');
                    } else {
                        proc.warnings.push({
                            type: 'role_not_allowed',
                            message: `${proc.code} does not allow co-surgeon billing`,
                            severity: 'error'
                        });
                    }
                    break;
                    
                case 'assistant':
                    if (rules && rules.assistant_allowed) {
                        proc.modifiers.push('-80');
                        proc.explanations.push('Modifier -80: Assistant surgeon');
                        this.addAuditEntry('surgeon_role', proc.code, 'Applied -80 for assistant surgeon');
                    } else {
                        proc.warnings.push({
                            type: 'role_not_allowed',
                            message: `${proc.code} does not allow assistant surgeon billing`,
                            severity: 'error'
                        });
                    }
                    break;
                    
                case 'assistant_minimum':
                    if (rules && rules.assistant_allowed) {
                        proc.modifiers.push('-81');
                        proc.explanations.push('Modifier -81: Minimum assistant surgeon');
                        this.addAuditEntry('surgeon_role', proc.code, 'Applied -81 for minimum assistant');
                    }
                    break;
                    
                case 'assistant_no_resident':
                    if (rules && rules.assistant_allowed) {
                        proc.modifiers.push('-82');
                        proc.explanations.push('Modifier -82: Assistant surgeon (no qualified resident available)');
                        this.addAuditEntry('surgeon_role', proc.code, 'Applied -82 for assistant (no resident)');
                    }
                    break;
                    
                case 'assistant_nonphysician':
                    if (rules && rules.assistant_allowed) {
                        proc.modifiers.push('-AS');
                        proc.explanations.push('Modifier -AS: Physician assistant or nurse practitioner services');
                        this.addAuditEntry('surgeon_role', proc.code, 'Applied -AS for non-physician assistant');
                    }
                    break;
            }
        });
    }

    /**
     * Apply return to OR modifiers (-76, -77, -78, -79, -58)
     */
    applyReturnToORModifiers(procedures, context) {
        const returnContext = context.returnToOR;
        if (!returnContext) return;

        procedures.forEach(proc => {
            const procContext = returnContext[proc.code];
            if (!procContext) return;

            switch (procContext.type) {
                case 'repeat_same_physician':
                    proc.modifiers.push('-76');
                    proc.explanations.push('Modifier -76: Repeat procedure by same physician');
                    this.addAuditEntry('return_to_or', proc.code, 'Applied -76 for repeat procedure');
                    break;
                    
                case 'repeat_different_physician':
                    proc.modifiers.push('-77');
                    proc.explanations.push('Modifier -77: Repeat procedure by different physician');
                    this.addAuditEntry('return_to_or', proc.code, 'Applied -77 for repeat by different physician');
                    break;
                    
                case 'unplanned_return':
                    proc.modifiers.push('-78');
                    proc.explanations.push('Modifier -78: Unplanned return to OR for related procedure during global period');
                    this.addAuditEntry('return_to_or', proc.code, 'Applied -78 for unplanned return');
                    break;
                    
                case 'unrelated_procedure':
                    proc.modifiers.push('-79');
                    proc.explanations.push('Modifier -79: Unrelated procedure during global period');
                    this.addAuditEntry('return_to_or', proc.code, 'Applied -79 for unrelated procedure');
                    break;
                    
                case 'staged_procedure':
                    proc.modifiers.push('-58');
                    proc.explanations.push('Modifier -58: Staged or planned procedure during global period');
                    this.addAuditEntry('return_to_or', proc.code, 'Applied -58 for staged procedure');
                    break;
            }
        });
    }

    /**
     * Apply reduced service modifiers (-52, -53)
     */
    applyReducedServiceModifiers(procedures, context) {
        if (!context.reducedService) return;
        
        procedures.forEach(proc => {
            let serviceType;
            if (typeof context.reducedService === 'string') {
                serviceType = context.reducedService;
            } else if (typeof context.reducedService === 'object' && context.reducedService[proc.code]) {
                serviceType = context.reducedService[proc.code];
            } else {
                return;
            }
            
            switch (serviceType) {
                case 'incomplete':
                case 'discontinued':
                    proc.modifiers.push('-52');
                    proc.explanations.push('Modifier -52: Reduced services/incomplete procedure');
                    proc.auditRisk = 'medium';
                    this.addAuditEntry('reduced_service', proc.code, 'Applied -52 for reduced services');
                    break;
                    
                case 'discontinued_anesthesia':
                    proc.modifiers.push('-53');
                    proc.explanations.push('Modifier -53: Discontinued procedure due to threat to patient');
                    proc.auditRisk = 'high';
                    this.addAuditEntry('reduced_service', proc.code, 'Applied -53 for discontinued procedure');
                    break;
            }
        });
    }

    /**
     * Calculate adjusted wRVUs based on modifiers
     * CMS MPPR: 100% for primary, 50% for 2nd+
     * Bilateral (-50): 150% of base wRVU
     * Reconstructive codes (15734): Always 100%, but counts as a procedure for MPPR ordering
     */
    calculateAdjustedWRVUs(procedures) {
        // First pass: calculate MPPR reductions based on rank
        const activeProcedures = procedures.filter(p => p.rank !== 'included' && p.rank !== 'suppressed' && p.rank !== 'bundled');
        const sortedByWRVU = [...activeProcedures].sort((a, b) => (b.work_rvu || 0) - (a.work_rvu || 0));
        
        // Assign MPPR position
        // CMS MPPR: 100% for highest wRVU, 50% for all subsequent
        // Reconstructive = always 100% but DOES occupy a slot (so next procedure is 50%)
        // Add-ons = always 100%, do NOT occupy a slot
        let mpprPosition = 0;
        sortedByWRVU.forEach(proc => {
            const rules = this.modifierRules[proc.code] || {};
            const isReconstructive = rules.distinct_procedure_class === 'reconstructive';
            const isAddon = rules.addon_code === true;
            
            if (isAddon) {
                proc.mpprReduction = 1.0; // Add-ons always 100%
                proc.mpprPosition = 'addon';
                // Add-ons don't increment position
            } else if (isReconstructive) {
                proc.mpprReduction = 1.0; // Reconstructive always 100%
                proc.mpprPosition = 'reconstructive';
                mpprPosition++; // BUT it occupies a slot, so next non-addon is 50%
            } else {
                proc.mpprReduction = mpprPosition === 0 ? 1.0 : 0.5; // Primary 100%, secondary 50%
                proc.mpprPosition = mpprPosition;
                mpprPosition++;
            }
        });

        procedures.forEach(proc => {
            let adjustedWRVU = proc.work_rvu || 0;
            let adjustmentFactors = [];
            const rules = this.modifierRules[proc.code] || {};
            const isReconstructive = rules.distinct_procedure_class === 'reconstructive';
            const isAddon = rules.addon_code === true;

            // Apply bilateral first (before MPPR)
            if (proc.modifiers.includes('-50')) {
                adjustedWRVU *= 1.5;
                adjustmentFactors.push('Bilateral -50: 150% payment');
            }

            // Apply MPPR for -51 (only if not addon/reconstructive)
            if (proc.modifiers.includes('-51') && !isAddon && !isReconstructive) {
                const reduction = proc.mpprReduction || 0.5;
                adjustedWRVU *= reduction;
                adjustmentFactors.push(`MPPR -51: ${Math.round(reduction * 100)}% payment`);
            }

            // Other modifiers
            proc.modifiers.forEach(modifier => {
                switch (modifier) {
                    case '-51':
                    case '-50':
                        // Already handled above
                        break;
                    case '-62':
                        adjustedWRVU *= 0.625;
                        adjustmentFactors.push('Co-surgeon -62: 62.5% payment');
                        break;
                    case '-80':
                    case '-81':
                    case '-82':
                        adjustedWRVU *= 0.16;
                        adjustmentFactors.push('Assistant surgeon: 16% payment');
                        break;
                    case '-AS':
                        adjustedWRVU *= 0.85;
                        adjustmentFactors.push('Non-physician assistant -AS: 85% payment');
                        break;
                    case '-22':
                        adjustedWRVU *= 1.25;
                        adjustmentFactors.push('Increased complexity -22: ~125% payment');
                        break;
                    case '-52':
                        adjustedWRVU *= 0.8;
                        adjustmentFactors.push('Reduced services -52: ~80% payment');
                        break;
                    case '-53':
                        adjustedWRVU *= 0.0;
                        adjustmentFactors.push('Discontinued -53: no payment');
                        break;
                }
            });

            // Included/suppressed procedures get zero wRVU
            if (proc.rank === 'included' || proc.rank === 'suppressed' || proc.rank === 'bundled') {
                adjustedWRVU = 0;
                adjustmentFactors.push('Included/bundled — not billable separately');
            }

            proc.adjustedWRVU = Math.round(adjustedWRVU * 100) / 100;
            proc.adjustmentFactors = adjustmentFactors;
        });
    }

    /**
     * Generate case summary
     */

    applyDiagnosticLaparoscopyOverride(procedures, context = {}) {
        const diagnosticCodes = new Set(['49320']);
        const therapeuticCodes = new Set(['44005', '44120', '44121', '44140', '44143', '44144', '44970', '44950', '47562', '47563', '47564']);
        const hasDiagnosticLap = procedures.some(proc => diagnosticCodes.has(String(proc.code)));
        const therapeuticProcedures = procedures.filter(proc => therapeuticCodes.has(String(proc.code)));
        if (!hasDiagnosticLap || therapeuticProcedures.length === 0) return;

        procedures.forEach(proc => {
            if (!diagnosticCodes.has(String(proc.code))) return;
            proc.rank = 'bundled';
            proc.adjustedWRVU = 0;
            proc.allowed = false;
            proc.exclusionReason = 'Diagnostic laparoscopy is not separately billable when a therapeutic procedure is performed';
            proc.internalNote = 'Diagnostic vs therapeutic distinction: therapeutic procedure overrides CPT 49320';
            proc.suppressed = true;
            proc.bundledInto = therapeuticProcedures.map(tp => tp.code).join(', ');
            if (Array.isArray(proc.auditTrail)) {
                proc.auditTrail.push('Diagnostic laparoscopy removed because a therapeutic abdominal procedure was performed');
            } else {
                proc.auditTrail = ['Diagnostic laparoscopy removed because a therapeutic abdominal procedure was performed'];
            }
        });
    }

    generateSummary(procedures) {
        const billableProcedures = procedures.filter(p => p.rank !== 'included');
        const totalWRVU = billableProcedures.reduce((sum, proc) => sum + proc.adjustedWRVU, 0);
        const procedureCount = procedures.length;
        const billableProcedureCount = billableProcedures.length;
        const modifierCount = procedures.reduce((sum, proc) => sum + proc.modifiers.length, 0);
        
        const primaryProc = procedures.find(p => p.rank === 'primary');
        const secondaryProcs = procedures.filter(p => p.rank === 'secondary');
        const addonProcs = procedures.filter(p => p.rank === 'addon');
        const includedProcs = procedures.filter(p => p.rank === 'included');

        const riskAssessment = this.calculateRiskAssessment(procedures);

        return {
            totalWRVU: Math.round(totalWRVU * 100) / 100,
            procedureCount,
            billableProcedureCount,
            includedProcedureCount: includedProcs.length,
            modifierCount,
            primaryProcedure: primaryProc ? primaryProc.code : null,
            secondaryCount: secondaryProcs.length,
            addonCount: addonProcs.length,
            hasComplexModifiers: procedures.some(p => 
                p.modifiers.some(m => ['-59', '-78', '-79', '-58', '-22'].includes(m))
            ),
            auditRisk: riskAssessment.overall,
            riskFactors: riskAssessment.riskFactors,
            billingCompliance: this.assessBillingCompliance(procedures)
        };
    }

    /**
     * Collect all warnings from procedures
     */
    collectWarnings(procedures) {
        const warnings = [];
        
        procedures.forEach(proc => {
            proc.warnings.forEach(warning => {
                warnings.push({
                    ...warning,
                    code: proc.code
                });
            });
        });

        return warnings;
    }

    /**
     * Helper functions
     */
    isAddonCode(code) {
        const rules = this.modifierRules[code];
        return rules && rules.addon_code === true;
    }

    isReconstructive(code) {
        const rules = this.modifierRules[code];
        return rules && rules.distinct_procedure_class === 'reconstructive';
    }

    isBilateralEligible(code) {
        const rules = this.modifierRules[code];
        return rules && rules.bilateral_eligible === true;
    }

    generateDebugInfo(procedures) {
        return {
            timestamp: new Date().toISOString(),
            procedureCount: procedures.length,
            rulesLoaded: Object.keys(this.modifierRules).length,
            bundlesLoaded: Object.keys(this.ncciBundles.bundles).length,
            questionsGenerated: this.pendingQuestions.length,
            auditTrailEntries: this.auditTrail.length,
            enhancedFeatures: [
                'procedure_hierarchy',
                'global_period_logic',
                'payer_aware_logic',
                'enhanced_bundling',
                'auto_suggestions',
                'audit_trail',
                'clinical_validation'
            ]
        };
    }

    /**
     * Process user responses to questions
     */
    processUserResponse(questionId, response) {
        this.userResponses[questionId] = response;
        // Re-run analysis with new context
        // This would typically be called from the UI
    }

    /**
     * Enable debug mode
     */
    enableDebugMode() {
        this.debugMode = true;
    }

    /**
     * Disable debug mode  
     */
    disableDebugMode() {
        this.debugMode = false;
    }

    /**
     * DELIVERABLE 2: Calculate confidence score for billing accuracy
     * @param {Object} analysis - The analysis results
     * @returns {Object} Confidence assessment
     */
    calculateConfidence(analysis) {
        let score = 100; // Start at perfect score
        const factors = [];
        
        const procedures = analysis.procedures || [];
        const warnings = analysis.warnings || [];
        const questions = analysis.questions || [];
        
        // Factor 1: All procedures have known rules (+20 if true, -15 per unknown)
        const unknownRules = procedures.filter(p => !this.modifierRules[p.code]);
        if (unknownRules.length === 0 && procedures.length > 0) {
            factors.push({
                factor: "All procedures have known rules",
                impact: +20,
                description: "All CPT codes found in billing rules database"
            });
            score += 20;
        } else {
            const penalty = unknownRules.length * 15;
            factors.push({
                factor: `${unknownRules.length} procedures without known rules`,
                impact: -penalty,
                description: `Codes: ${unknownRules.map(p => p.code).join(', ')}`
            });
            score -= penalty;
        }
        
        // Factor 2: NCCI bundles resolved (-30 per unresolved bundle)
        const ncciBundleWarnings = warnings.filter(w => w.type === 'ncci_bundle' && w.severity === 'warning');
        if (ncciBundleWarnings.length > 0) {
            const penalty = ncciBundleWarnings.length * 10; // Reduced: resolvable with -59
            factors.push({
                factor: `${ncciBundleWarnings.length} resolvable NCCI bundles (need -59 or review)`,
                impact: -penalty,
                description: "Bundle pairs resolvable with -59 modifier"
            });
            score -= penalty;
        } else if (procedures.length > 1) {
            factors.push({
                factor: "All NCCI bundles resolved",
                impact: +15,
                description: "No unresolved bundling conflicts detected"
            });
            score += 15;
        }
        
        // Factor 3: Duplicate CPT codes resolved (-20 per duplicate without modifier)
        const duplicateCodes = this.findDuplicateCodes(procedures);
        const unresolvedDuplicates = duplicateCodes.filter(dup => {
            return !dup.procedures.some(p => 
                p.modifiers.includes('-50') || 
                p.modifiers.includes('-RT') || 
                p.modifiers.includes('-LT') ||
                p.modifiers.includes('-59') ||
                p.modifiers.includes('-76') || 
                p.modifiers.includes('-77')
            );
        });
        
        if (unresolvedDuplicates.length > 0) {
            const penalty = unresolvedDuplicates.length * 20;
            factors.push({
                factor: `${unresolvedDuplicates.length} duplicate CPT codes without modifiers`,
                impact: -penalty,
                description: `Codes: ${unresolvedDuplicates.map(d => d.code).join(', ')}`
            });
            score -= penalty;
        } else if (duplicateCodes.length > 0) {
            factors.push({
                factor: "All duplicate codes properly modified",
                impact: +10,
                description: "Bilateral, laterality, or repeat modifiers applied"
            });
            score += 10;
        }
        
        // Factor 4: Laterality-eligible codes have appropriate modifiers (-10 per missing)
        const lateralityEligible = procedures.filter(p => {
            const rules = this.modifierRules[p.code];
            return rules && rules.laterality_applicable && !rules.inherently_bilateral;
        });
        
        const missingLaterality = lateralityEligible.filter(p => 
            !p.modifiers.includes('-50') && 
            !p.modifiers.includes('-RT') && 
            !p.modifiers.includes('-LT')
        );
        
        if (missingLaterality.length > 0) {
            const penalty = missingLaterality.length * 10;
            factors.push({
                factor: `${missingLaterality.length} laterality-eligible procedures missing RT/LT/-50`,
                impact: -penalty,
                description: `Codes: ${missingLaterality.map(p => p.code).join(', ')}`
            });
            score -= penalty;
        } else if (lateralityEligible.length > 0) {
            factors.push({
                factor: "All laterality requirements satisfied",
                impact: +10,
                description: "Bilateral or side-specific modifiers applied"
            });
            score += 10;
        }
        
        // Factor 5: Unresolved questions (-5 per question)
        if (questions.length > 0) {
            const penalty = questions.length * 5;
            factors.push({
                factor: `${questions.length} unresolved questions`,
                impact: -penalty,
                description: "User input required for complete analysis"
            });
            score -= penalty;
        }
        
        // Factor 6: Global period violations (-25 per violation)
        const globalViolations = warnings.filter(w => w.type === 'global_period_violation');
        if (globalViolations.length > 0) {
            const penalty = globalViolations.length * 25;
            factors.push({
                factor: `${globalViolations.length} global period violations`,
                impact: -penalty,
                description: "Missing -58, -78, or -79 modifiers"
            });
            score -= penalty;
        }
        
        // Factor 7: Included procedures properly handled (+5 if any found and handled)
        const includedProcedures = procedures.filter(p => p.rank === 'included');
        if (includedProcedures.length > 0) {
            factors.push({
                factor: "Included procedures properly identified",
                impact: +5,
                description: `${includedProcedures.length} procedures marked as not separately billable`
            });
            score += 5;
        }
        
        // Factor 8: Surgeon role modifiers properly applied
        const roleErrors = warnings.filter(w => w.type === 'role_not_allowed');
        if (roleErrors.length > 0) {
            const penalty = roleErrors.length * 15;
            factors.push({
                factor: `${roleErrors.length} invalid surgeon role assignments`,
                impact: -penalty,
                description: "Co-surgeon or assistant not allowed for these procedures"
            });
            score -= penalty;
        }
        
        // Ensure score stays within bounds
        score = Math.max(0, Math.min(100, Math.round(score)));
        
        // Determine confidence level and recommendation
        let overall, recommendation;
        // FIX 3: STRICTER CONFIDENCE THRESHOLDS
        if (score >= 95) {
            overall = 'high';
            recommendation = 'Safe to submit';
        } else if (score >= 80) {
            overall = 'medium';
            recommendation = 'Review required before submission';
        } else {
            overall = 'low';
            recommendation = 'DO NOT SUBMIT — resolve issues';
        }
        
        this.addAuditEntry('confidence_calculated', null, 
            `Confidence score calculated: ${score}%`, 
            { overall, factorCount: factors.length }
        );
        
        return {
            overall,
            score,
            factors,
            recommendation,
            timestamp: new Date().toISOString()
        };
    }
    
    /**
     * DELIVERABLE 3: Check for blocking issues that prevent case export
     * @param {Object} analysis - The analysis results
     * @returns {Array} Array of blocking issues
     */
    checkForBlockingIssues(analysis) {
        const blockingIssues = [];
        const procedures = analysis.procedures || [];
        const warnings = analysis.warnings || [];
        const confidence = analysis.confidence || { score: 100 };
        
        // 1. Duplicate CPT without modifier resolution
        const duplicateCodes = this.findDuplicateCodes(procedures);
        const unresolvedDuplicates = duplicateCodes.filter(dup => {
            return !dup.procedures.some(p => 
                p.modifiers.includes('-50') || 
                p.modifiers.includes('-RT') || 
                p.modifiers.includes('-LT') ||
                p.modifiers.includes('-59') ||
                p.modifiers.includes('-76') || 
                p.modifiers.includes('-77')
            );
        });
        
        unresolvedDuplicates.forEach(dup => {
            blockingIssues.push({
                type: 'unresolved_duplicate',
                severity: 'critical',
                message: `Duplicate CPT code ${dup.code} without distinguishing modifier`,
                description: "Multiple instances of same CPT require bilateral (-50), laterality (-RT/-LT), or distinct service (-59) modifier",
                affectedCodes: [dup.code]
            });
        });
        
        // 2. NCCI bundle pair without -59 and no user dismissal
        const criticalBundleWarnings = warnings.filter(w => 
            w.type === 'ncci_bundle' && 
            w.severity === 'warning' &&
            !w.userDismissed // Would need to track user dismissals in real implementation
        );
        
        criticalBundleWarnings.forEach(warning => {
            blockingIssues.push({
                type: 'ncci_bundle_unresolved',
                severity: 'critical',
                message: `NCCI bundle conflict requires resolution: ${warning.message}`,
                description: "Apply -59 modifier if separate circumstances, or dismiss if bundling is appropriate",
                affectedCodes: [warning.code]
            });
        });
        
        // 3. Procedure within global period without required modifier
        const globalViolations = warnings.filter(w => w.type === 'global_period_violation');
        globalViolations.forEach(warning => {
            blockingIssues.push({
                type: 'global_period_violation',
                severity: 'critical',
                message: `Procedure within global period requires modifier: ${warning.message}`,
                description: "Must apply -58 (staged), -78 (unplanned return), or -79 (unrelated) modifier",
                affectedCodes: [warning.code]
            });
        });
        
        // 4. Confidence score below 80 (UPDATED THRESHOLD)
        if (confidence.score < 80) {
            blockingIssues.push({
                type: 'low_confidence',
                severity: 'critical',
                message: `Case confidence below export threshold (${confidence.score}% < 80%)`,
                description: "Billing issues detected - review required before export",
                affectedCodes: procedures.map(p => p.code)
            });
        }
        
        // 5. Critical warnings that should block submission
        const criticalWarnings = warnings.filter(w => 
            w.severity === 'error' && 
            !['included_procedure'].includes(w.type) // Included procedures don't block, just inform
        );
        
        criticalWarnings.forEach(warning => {
            if (!blockingIssues.some(issue => issue.type === warning.type && issue.affectedCodes?.includes(warning.code))) {
                blockingIssues.push({
                    type: warning.type,
                    severity: 'critical',
                    message: warning.message,
                    description: "Critical billing error that prevents case submission",
                    affectedCodes: [warning.code]
                });
            }
        });
        
        this.addAuditEntry('blocking_issues_checked', null, 
            `Found ${blockingIssues.length} blocking issues`, 
            { issueTypes: blockingIssues.map(i => i.type) }
        );
        
        return blockingIssues;
    }
    
    /**
     * Helper: Find duplicate CPT codes in procedures
     * @param {Array} procedures - Array of procedures
     * @returns {Array} Array of duplicate code groups
     */
    findDuplicateCodes(procedures) {
        const codeGroups = {};
        const duplicates = [];
        
        procedures.forEach(proc => {
            if (!codeGroups[proc.code]) {
                codeGroups[proc.code] = [];
            }
            codeGroups[proc.code].push(proc);
        });
        
        for (const [code, procs] of Object.entries(codeGroups)) {
            if (procs.length > 1) {
                duplicates.push({
                    code,
                    count: procs.length,
                    procedures: procs
                });
            }
        }
        
        return duplicates;
    }

    /**
     * FIX 6: AUDIT MODE OUTPUT - Generate structured justification for each CPT
     */
    generateAuditOutput(procedures, confidence, blockingIssues) {
        const auditEntries = procedures.map(proc => {
            const rules = this.modifierRules[proc.code] || {};
            let billabilityStatus, justification, riskFactors = [];

            if (proc.rank === 'included') {
                billabilityStatus = 'NOT_BILLABLE';
                justification = `Included in higher-order procedure - inherent component`;
                riskFactors = ['included_service'];
            } else if (proc.rank === 'primary') {
                billabilityStatus = 'PRIMARY';
                justification = `Highest wRVU (${proc.work_rvu}) and appropriate hierarchy tier (${proc.hierarchyTier})`;
            } else if (proc.rank === 'secondary') {
                billabilityStatus = 'SECONDARY';
                justification = `Lower wRVU than primary, subject to MPPR reduction (${Math.round((proc.mpprReduction || 0.5) * 100)}%)`;
                if (proc.codeFamily) {
                    justification += ` [${proc.codeFamily} family]`;
                }
            } else if (proc.rank === 'addon') {
                billabilityStatus = 'ADDON';
                justification = 'Add-on code - full payment, no MPPR reduction';
            } else {
                billabilityStatus = 'UNKNOWN';
                justification = 'Billing status could not be determined';
                riskFactors.push('unknown_classification');
            }

            // Modifier justifications
            const modifierJustifications = proc.modifiers.map(mod => {
                switch (mod) {
                    case '-50': return 'Bilateral procedure performed';
                    case '-51': return `MPPR secondary (${Math.round((proc.mprrReduction || 0.5) * 100)}% payment)`;
                    case '-RT': return 'Right side laterality';
                    case '-LT': return 'Left side laterality';
                    case '-78': return 'Unplanned return to OR during global period';
                    case '-79': return 'Unrelated procedure during global period';
                    case '-58': return 'Staged procedure during global period';
                    case '-24': return 'Unrelated E/M service during global period';
                    case '-62': return 'Co-surgeon eligible procedure';
                    case '-80': return 'Assistant surgeon';
                    case '-52': return 'Reduced/discontinued service';
                    case '-76': return 'Repeat procedure, same physician';
                    case '-77': return 'Repeat procedure, different physician';
                    default: return `Modifier ${mod} applied per CMS guidelines`;
                }
            });

            // Risk assessment
            if (proc.auditRisk === 'high') riskFactors.push('high_audit_risk');
            if (proc.warnings && proc.warnings.length > 0) {
                proc.warnings.forEach(w => {
                    if (w.severity === 'error') riskFactors.push('billing_error');
                    if (w.type === 'ncci_bundle') riskFactors.push('bundle_conflict');
                });
            }
            if (!rules.hierarchy_tier) riskFactors.push('unknown_rules');

            return {
                code: proc.code,
                description: proc.description || 'Unknown procedure',
                billabilityStatus,
                justification,
                modifiers: proc.modifiers,
                modifierJustifications,
                baseWRVU: proc.work_rvu,
                adjustedWRVU: proc.adjustedWRVU,
                paymentAdjustments: proc.adjustmentFactors || [],
                codeFamily: proc.codeFamily || 'unclassified',
                hierarchyTier: proc.hierarchyTier,
                riskFactors,
                auditRisk: proc.auditRisk || 'low'
            };
        });

        return {
            timestamp: new Date().toISOString(),
            caseConfidence: {
                score: confidence.score,
                level: confidence.overall,
                recommendation: confidence.recommendation
            },
            exportEligible: blockingIssues.length === 0 && confidence.score >= 80,
            blockingIssues: blockingIssues.map(issue => ({
                type: issue.type,
                severity: issue.severity,
                message: issue.message,
                affectedCodes: issue.affectedCodes || []
            })),
            procedures: auditEntries,
            summaryMetrics: {
                totalProcedures: procedures.length,
                billableProcedures: auditEntries.filter(p => p.billabilityStatus !== 'NOT_BILLABLE').length,
                includedProcedures: auditEntries.filter(p => p.billabilityStatus === 'NOT_BILLABLE').length,
                totalModifiers: auditEntries.reduce((sum, p) => sum + p.modifiers.length, 0),
                totalWRVU: auditEntries.reduce((sum, p) => sum + (p.adjustedWRVU || 0), 0),
                highRiskProcedures: auditEntries.filter(p => p.auditRisk === 'high').length
            }
        };
    }
}

// Create global instance
window.ModifierEngine = new ModifierEngine();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await window.ModifierEngine.initialize();
        console.log('🧠✨ Enhanced Modifier Intelligence Engine ready');
        
        // Run clinical validation in debug mode
        if (window.location.search.includes('debug')) {
            window.ModifierEngine.enableDebugMode();
            window.ModifierEngine.runClinicalValidation();
        }
    } catch (error) {
        console.error('❌ Failed to initialize Enhanced Modifier Engine:', error);
    }
});