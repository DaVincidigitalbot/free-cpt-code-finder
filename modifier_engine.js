/**
 * Modifier Intelligence Engine for FreeCPTCodeFinder.com
 * 
 * Analyzes CPT code combinations and automatically assigns appropriate modifiers
 * based on NCCI guidelines, CMS rules, and clinical context.
 * 
 * @author FreeCPTCodeFinder.com
 * @version 1.0.0
 */

class ModifierEngine {
    constructor() {
        this.modifierRules = null;
        this.ncciBundles = null;
        this.pendingQuestions = [];
        this.userResponses = {};
        this.debugMode = false;
    }

    /**
     * Initialize the engine by loading rule data
     */
    async initialize() {
        try {
            // Load modifier rules and NCCI bundles
            const [rulesResponse, bundlesResponse] = await Promise.all([
                fetch('./modifier_rules.json'),
                fetch('./ncci_bundles.json')
            ]);

            this.modifierRules = await rulesResponse.json();
            this.ncciBundles = await bundlesResponse.json();
            
            console.log('Modifier Engine initialized successfully');
            return true;
        } catch (error) {
            console.error('Failed to initialize Modifier Engine:', error);
            return false;
        }
    }

    /**
     * Main analysis function - analyzes case and returns modifier assignments
     * @param {Array} caseItems - Array of procedure objects with CPT codes and wRVUs
     * @param {Object} context - Additional context (bilateral, surgeon role, etc.)
     * @returns {Object} Analysis results with modifier assignments and explanations
     */
    analyze(caseItems, context = {}) {
        if (!this.modifierRules || !this.ncciBundles) {
            throw new Error('Modifier Engine not initialized. Call initialize() first.');
        }

        if (!caseItems || caseItems.length === 0) {
            return { procedures: [], questions: [], warnings: [], summary: {} };
        }

        // Reset state
        this.pendingQuestions = [];
        
        // Create working copy of procedures
        const procedures = caseItems.map(item => ({
            ...item,
            modifiers: [],
            adjustedWRVU: item.work_rvu || 0,
            rank: 'unknown',
            explanations: [],
            warnings: []
        }));

        // Step 1: Rank procedures by wRVU
        this.rankProcedures(procedures);

        // Step 2: Apply modifier -51 (Multiple Procedures)
        this.applyModifier51(procedures);

        // Step 3: Check for bilateral procedures
        this.checkBilateralProcedures(procedures, context);

        // Step 4: Check for NCCI bundles and modifier -59
        this.checkNCCIBundles(procedures);

        // Step 5: Apply laterality modifiers (-RT/-LT)
        this.applyLateralityModifiers(procedures, context);

        // Step 6: Apply surgeon role modifiers
        this.applySurgeonRoleModifiers(procedures, context);

        // Step 7: Apply return to OR modifiers
        this.applyReturnToORModifiers(procedures, context);

        // Step 8: Calculate final adjusted wRVUs
        this.calculateAdjustedWRVUs(procedures);

        // Generate summary
        const summary = this.generateSummary(procedures);

        return {
            procedures,
            questions: this.pendingQuestions,
            warnings: this.collectWarnings(procedures),
            summary,
            debugInfo: this.debugMode ? this.generateDebugInfo(procedures) : null
        };
    }

    /**
     * Rank procedures by wRVU and assign primary/secondary status
     */
    rankProcedures(procedures) {
        // Separate add-on codes and reconstructive procedures
        const addons = procedures.filter(p => this.isAddonCode(p.code));
        const reconstructive = procedures.filter(p => !this.isAddonCode(p.code) && this.isReconstructive(p.code));
        const regular = procedures.filter(p => !this.isAddonCode(p.code) && !this.isReconstructive(p.code));

        // Sort regular procedures by wRVU descending
        regular.sort((a, b) => (b.work_rvu || 0) - (a.work_rvu || 0));
        reconstructive.sort((a, b) => (b.work_rvu || 0) - (a.work_rvu || 0));

        // Assign ranks
        if (reconstructive.length > 0) {
            // Reconstructive procedures are primary
            reconstructive.forEach((proc, index) => {
                proc.rank = index === 0 ? 'primary' : 'reconstructive';
                proc.explanations.push(
                    index === 0 
                        ? 'Primary procedure - highest value reconstructive procedure'
                        : 'Distinct reconstructive procedure - billed separately'
                );
            });
            
            // Regular procedures become secondary
            regular.forEach((proc, index) => {
                proc.rank = 'secondary';
                proc.explanations.push('Secondary to reconstructive procedure');
            });
        } else {
            // Standard ranking by wRVU
            regular.forEach((proc, index) => {
                proc.rank = index === 0 ? 'primary' : 'secondary';
                proc.explanations.push(
                    index === 0 
                        ? 'Primary procedure - highest wRVU value'
                        : `Secondary procedure - ranked #${index + 1} by wRVU`
                );
            });
        }

        // Add-on codes never get ranked
        addons.forEach(proc => {
            proc.rank = 'addon';
            proc.explanations.push('Add-on code - always billed at full value');
        });
    }

    /**
     * Apply modifier -51 (Multiple Procedures)
     */
    applyModifier51(procedures) {
        const nonAddonProcs = procedures.filter(p => !this.isAddonCode(p.code));
        
        if (nonAddonProcs.length <= 1) return;

        nonAddonProcs.forEach(proc => {
            if (proc.rank === 'secondary') {
                const rules = this.modifierRules[proc.code];
                
                // Check if exempt from modifier -51
                if (rules && rules.mod51_exempt) {
                    proc.explanations.push('Exempt from modifier -51 per CMS guidelines');
                    return;
                }

                proc.modifiers.push('-51');
                proc.explanations.push('Modifier -51: Multiple procedure performed in same session');
            }
        });
    }

    /**
     * Check for bilateral procedures and suggest modifier -50
     */
    checkBilateralProcedures(procedures, context) {
        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            if (!rules || !rules.bilateral_eligible) return;

            if (rules.inherently_bilateral) {
                proc.explanations.push('Inherently bilateral procedure - no modifier -50 needed');
                return;
            }

            // Check if user specified bilateral in context
            const isBilateral = context.bilateral && context.bilateral[proc.code];
            
            if (isBilateral) {
                if (rules.bilateral_method === 'modifier_50') {
                    proc.modifiers.push('-50');
                    proc.explanations.push('Modifier -50: Bilateral procedure');
                } else if (rules.bilateral_method === 'rt_lt') {
                    // This should be handled by creating separate line items
                    proc.explanations.push('Bilateral procedure - bill as separate -RT and -LT line items');
                } else if (rules.bilateral_method === 'units_2') {
                    proc.explanations.push('Bilateral procedure - bill as single line item with units = 2');
                }
            } else {
                // Generate question for user
                this.pendingQuestions.push({
                    type: 'bilateral',
                    code: proc.code,
                    question: `Was ${proc.code} performed bilaterally?`,
                    options: ['Yes', 'No']
                });
            }
        });
    }

    /**
     * Check NCCI bundles and flag potential -59 needs
     */
    checkNCCIBundles(procedures) {
        const bundleInfo = this.ncciBundles.bundles;
        const commonPairs = this.ncciBundles.common_pairs;

        procedures.forEach(primaryProc => {
            const primaryCode = primaryProc.code;
            const bundledCodes = bundleInfo[primaryCode];
            
            if (!bundledCodes) return;

            // Check if any other procedures in the case are bundled with this one
            procedures.forEach(secondaryProc => {
                if (primaryProc.id === secondaryProc.id) return;
                
                const secondaryCode = secondaryProc.code;
                
                if (bundledCodes.column2_codes.includes(secondaryCode)) {
                    // Found a bundle - check if -59 is allowed
                    if (bundledCodes.modifier59_allowed) {
                        secondaryProc.warnings.push({
                            type: 'ncci_bundle',
                            message: `${secondaryCode} bundles with ${primaryCode}. Consider modifier -59 if separate site/session.`,
                            severity: 'warning'
                        });
                        
                        // Generate question about separate site
                        this.pendingQuestions.push({
                            type: 'bundle_separation',
                            primaryCode: primaryCode,
                            secondaryCode: secondaryCode,
                            question: `Were ${primaryCode} and ${secondaryCode} performed at separate sites, incisions, or sessions?`,
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
            } else if (laterality === 'left') {
                proc.modifiers.push('-LT');
                proc.explanations.push('Modifier -LT: Left side procedure');
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
                    }
                    break;
                    
                case 'assistant_no_resident':
                    if (rules && rules.assistant_allowed) {
                        proc.modifiers.push('-82');
                        proc.explanations.push('Modifier -82: Assistant surgeon (no qualified resident available)');
                    }
                    break;
                    
                case 'assistant_nonphysician':
                    if (rules && rules.assistant_allowed) {
                        proc.modifiers.push('-AS');
                        proc.explanations.push('Modifier -AS: Physician assistant or nurse practitioner services');
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
                    break;
                    
                case 'repeat_different_physician':
                    proc.modifiers.push('-77');
                    proc.explanations.push('Modifier -77: Repeat procedure by different physician');
                    break;
                    
                case 'unplanned_return':
                    proc.modifiers.push('-78');
                    proc.explanations.push('Modifier -78: Unplanned return to OR for related procedure during global period');
                    break;
                    
                case 'unrelated_procedure':
                    proc.modifiers.push('-79');
                    proc.explanations.push('Modifier -79: Unrelated procedure during global period');
                    break;
                    
                case 'staged_procedure':
                    proc.modifiers.push('-58');
                    proc.explanations.push('Modifier -58: Staged or planned procedure during global period');
                    break;
            }
        });
    }

    /**
     * Calculate adjusted wRVUs based on modifiers
     */
    calculateAdjustedWRVUs(procedures) {
        procedures.forEach(proc => {
            let adjustedWRVU = proc.work_rvu || 0;
            let adjustmentFactors = [];

            proc.modifiers.forEach(modifier => {
                switch (modifier) {
                    case '-51':
                        adjustedWRVU *= 0.5;
                        adjustmentFactors.push('MPPR 50% reduction');
                        break;
                    case '-50':
                        adjustedWRVU *= 1.5;
                        adjustmentFactors.push('Bilateral 150% payment');
                        break;
                    case '-62':
                        adjustedWRVU *= 0.625;
                        adjustmentFactors.push('Co-surgeon 62.5% payment');
                        break;
                    case '-80':
                    case '-81':
                    case '-82':
                        adjustedWRVU *= 0.16;
                        adjustmentFactors.push('Assistant surgeon 16% payment');
                        break;
                    case '-AS':
                        adjustedWRVU *= 0.85;
                        adjustmentFactors.push('Non-physician assistant 85% payment');
                        break;
                    case '-22':
                        adjustedWRVU *= 1.25; // Estimated increase
                        adjustmentFactors.push('Increased complexity 125% payment (estimated)');
                        break;
                }
            });

            proc.adjustedWRVU = adjustedWRVU;
            proc.adjustmentFactors = adjustmentFactors;
        });
    }

    /**
     * Generate case summary
     */
    generateSummary(procedures) {
        const totalWRVU = procedures.reduce((sum, proc) => sum + proc.adjustedWRVU, 0);
        const procedureCount = procedures.length;
        const modifierCount = procedures.reduce((sum, proc) => sum + proc.modifiers.length, 0);
        
        const primaryProc = procedures.find(p => p.rank === 'primary');
        const secondaryProcs = procedures.filter(p => p.rank === 'secondary');
        const addonProcs = procedures.filter(p => p.rank === 'addon');

        return {
            totalWRVU: Math.round(totalWRVU * 100) / 100,
            procedureCount,
            modifierCount,
            primaryProcedure: primaryProc ? primaryProc.code : null,
            secondaryCount: secondaryProcs.length,
            addonCount: addonProcs.length,
            hasComplexModifiers: procedures.some(p => 
                p.modifiers.some(m => ['-59', '-78', '-79', '-58', '-22'].includes(m))
            )
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

    generateDebugInfo(procedures) {
        return {
            timestamp: new Date().toISOString(),
            procedureCount: procedures.length,
            rulesLoaded: Object.keys(this.modifierRules).length,
            bundlesLoaded: Object.keys(this.ncciBundles.bundles).length,
            questionsGenerated: this.pendingQuestions.length
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
}

// Create global instance
window.ModifierEngine = new ModifierEngine();

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await window.ModifierEngine.initialize();
        console.log('🧠 Modifier Intelligence Engine ready');
    } catch (error) {
        console.error('❌ Failed to initialize Modifier Engine:', error);
    }
});