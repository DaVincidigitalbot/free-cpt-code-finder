// Enhanced Billing Intelligence Functions for FreeCPTCodeFinder.com
// Version 2.0.0 - Surgical Billing Intelligence

// Global context for enhanced billing features
let billingContext = {
    payerType: 'medicare',
    withinGlobalPeriod: false,
    globalPeriodRelationship: null
};

// Toggle global period context
function toggleGlobalPeriod() {
    const checkbox = document.getElementById('globalPeriodToggle');
    const dropdown = document.getElementById('globalPeriodRelationship');
    const panel = document.getElementById('billingContextPanel');
    
    if (checkbox.checked) {
        dropdown.style.display = 'inline';
        billingContext.withinGlobalPeriod = true;
    } else {
        dropdown.style.display = 'none';
        billingContext.withinGlobalPeriod = false;
        billingContext.globalPeriodRelationship = null;
        dropdown.value = '';
    }
    
    // Re-run modifier analysis if there are procedures
    if (typeof caseProcs !== 'undefined' && caseProcs.length > 0) {
        runEnhancedModifierAnalysis();
    }
}

// Select payer type
function selectPayer(payerType) {
    billingContext.payerType = payerType;
    
    // Update button states
    const medicareBtn = document.getElementById('medicareBtn');
    const commercialBtn = document.getElementById('commercialBtn');
    
    if (payerType === 'medicare') {
        medicareBtn.classList.add('active');
        commercialBtn.classList.remove('active');
    } else {
        commercialBtn.classList.add('active');
        medicareBtn.classList.remove('active');
    }
    
    // Re-run analysis if there are procedures
    if (typeof caseProcs !== 'undefined' && caseProcs.length > 0) {
        runEnhancedModifierAnalysis();
    }
}

// Enhanced modifier analysis using the upgraded engine
async function runEnhancedModifierAnalysis() {
    if (!window.ModifierEngine || typeof caseProcs === 'undefined' || caseProcs.length === 0) return;
    
    try {
        // Show billing context panel when there are procedures
        const contextPanel = document.getElementById('billingContextPanel');
        if (contextPanel) {
            contextPanel.style.display = 'block';
        }
        
        // Build context object
        const context = {
            ...billingContext,
            bilateral: {},
            laterality: {}
        };
        
        // Run analysis
        const analysis = await window.ModifierEngine.analyze(caseProcs, context);
        
        // Update audit trail
        updateAuditTrail(analysis.auditTrail);
        
        // Show smart suggestions
        if (analysis.procedures) {
            const procWithSuggestions = analysis.procedures.filter(p => p.suggestions && p.suggestions.length > 0);
            displaySmartSuggestions(procWithSuggestions);
        }
        
        console.log('✅ Enhanced modifier analysis completed', analysis);
        
    } catch (error) {
        console.error('❌ Enhanced modifier analysis failed:', error);
    }
}

// Update audit trail display
function updateAuditTrail(auditTrail) {
    const auditPanel = document.getElementById('auditTrailPanel');
    const auditContent = document.getElementById('auditTrailContent');
    
    if (!auditTrail || auditTrail.length === 0) {
        if (auditPanel) auditPanel.style.display = 'none';
        return;
    }
    
    if (auditPanel) auditPanel.style.display = 'block';
    
    let html = '';
    auditTrail.slice(-10).forEach(entry => {
        const time = new Date(entry.timestamp).toLocaleTimeString();
        
        html += `
            <div class="audit-entry">
                <span class="audit-reason">
                    <strong>${time}</strong> - ${entry.description}
                    ${entry.cptCode ? ` (${entry.cptCode})` : ''}
                </span>
                <span class="audit-risk risk-low">
                    ${entry.action.replace('_', ' ')}
                </span>
            </div>
        `;
    });
    
    if (auditContent) auditContent.innerHTML = html;
}

// Toggle audit trail visibility
function toggleAuditTrail() {
    const content = document.getElementById('auditTrailContent');
    const toggle = document.getElementById('auditTrailToggle');
    
    if (content && toggle) {
        if (content.style.display === 'none' || !content.style.display) {
            content.style.display = 'block';
            toggle.textContent = '▲';
        } else {
            content.style.display = 'none';
            toggle.textContent = '▼';
        }
    }
}

// Display smart suggestions
function displaySmartSuggestions(proceduresWithSuggestions) {
    // Remove existing suggestions
    document.querySelectorAll('.smart-suggestion').forEach(el => el.remove());
    
    if (!proceduresWithSuggestions || proceduresWithSuggestions.length === 0) return;
    
    const caseTrayDetail = document.getElementById('caseTrayDetail');
    if (!caseTrayDetail) return;
    
    proceduresWithSuggestions.forEach(proc => {
        if (proc.suggestions) {
            proc.suggestions.forEach(suggestion => {
                const suggestionEl = document.createElement('div');
                suggestionEl.className = 'smart-suggestion';
                suggestionEl.innerHTML = `
                    <div class="suggestion-text">${suggestion.message}</div>
                    <div class="suggestion-actions">
                        <button class="suggestion-btn btn-apply" 
                                onclick="applySuggestion('${proc.code}', '${suggestion.modifier || ''}', '${suggestion.action || ''}')">
                            Apply
                        </button>
                        <button class="suggestion-btn btn-dismiss" 
                                onclick="dismissSuggestion(this)">
                            Dismiss
                        </button>
                    </div>
                `;
                
                caseTrayDetail.appendChild(suggestionEl);
            });
        }
    });
}

// Apply a suggestion
function applySuggestion(cptCode, modifier, action) {
    if (typeof caseProcs === 'undefined') return;
    
    const proc = caseProcs.find(p => p.code === cptCode);
    if (!proc) return;
    
    if (action === 'apply_modifier' && modifier && typeof updateCaseMod !== 'undefined') {
        updateCaseMod(proc.id, modifier);
    } else if (action === 'question_bilateral') {
        // Show bilateral question
        if (confirm(`Was ${cptCode} performed bilaterally?`)) {
            if (typeof updateCaseMod !== 'undefined') {
                updateCaseMod(proc.id, '-50');
            }
        }
    } else if (action === 'question_duplicate') {
        // Handle duplicate CPT scenario
        if (typeof showDuplicateCPTPrompt !== 'undefined') {
            showDuplicateCPTPrompt(cptCode);
        }
        return;
    }
    
    // Remove the suggestion and refresh
    if (event && event.target) {
        const suggestionEl = event.target.closest('.smart-suggestion');
        if (suggestionEl) suggestionEl.remove();
    }
}

// Dismiss a suggestion
function dismissSuggestion(buttonEl) {
    if (buttonEl) {
        const suggestionEl = buttonEl.closest('.smart-suggestion');
        if (suggestionEl) suggestionEl.remove();
    }
}

// Run clinical validation (for testing)
function runClinicalValidation() {
    if (!window.ModifierEngine) {
        console.error('ModifierEngine not available');
        return;
    }
    
    console.log('🧪 Running clinical validation...');
    const results = window.ModifierEngine.runClinicalValidation();
    
    // Display results in console and alert
    const passCount = results.filter(r => r.passed).length;
    const totalCount = results.length;
    
    console.log(`\n🧪 Validation Results: ${passCount}/${totalCount} passed`);
    
    if (passCount === totalCount) {
        alert(`✅ All ${totalCount} clinical validation scenarios passed!`);
    } else {
        const failedScenarios = results.filter(r => !r.passed).map((r, i) => 
            `Scenario ${i + 1}: ${r.issues.join(', ')}`
        ).join('\n');
        alert(`❌ ${totalCount - passCount} scenarios failed:\n\n${failedScenarios}`);
    }
    
    return results;
}

// Enhanced toggle case tray
let originalToggleCaseTray = null;

function enhanceToggleCaseTray() {
    // Store original function if it exists
    if (typeof toggleCaseTray !== 'undefined') {
        originalToggleCaseTray = toggleCaseTray;
    }
    
    // Override with enhanced version
    window.toggleCaseTray = function() {
        // Call original function if it exists
        if (originalToggleCaseTray) {
            originalToggleCaseTray();
        }
        
        const tray = document.getElementById('caseTray');
        const modifierPanel = document.getElementById('modifierIntelligencePanel');
        const auditPanel = document.getElementById('auditTrailPanel');
        const billingPanel = document.getElementById('billingContextPanel');
        
        if (tray && tray.classList.contains('expanded')) {
            // Show enhanced panels when case tray is expanded
            if (modifierPanel) modifierPanel.style.display = 'block';
            if (auditPanel) auditPanel.style.display = 'block';
            if (billingPanel && typeof caseProcs !== 'undefined' && caseProcs.length > 0) {
                billingPanel.style.display = 'block';
                // Run enhanced analysis
                setTimeout(runEnhancedModifierAnalysis, 100);
            }
        } else {
            // Hide enhanced panels when collapsed
            if (billingPanel) billingPanel.style.display = 'none';
        }
    };
}

// Initialize enhanced features
function initializeEnhancedBilling() {
    // Set up event listeners
    const dropdown = document.getElementById('globalPeriodRelationship');
    if (dropdown) {
        dropdown.addEventListener('change', (e) => {
            billingContext.globalPeriodRelationship = e.target.value;
            if (typeof caseProcs !== 'undefined' && caseProcs.length > 0) {
                runEnhancedModifierAnalysis();
            }
        });
    }
    
    // Enhance the toggle case tray function
    enhanceToggleCaseTray();
    
    console.log('🚀 Enhanced Billing Intelligence initialized');
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeEnhancedBilling);
} else {
    // DOM is already ready
    initializeEnhancedBilling();
}

// Export functions for global access
window.toggleGlobalPeriod = toggleGlobalPeriod;
window.selectPayer = selectPayer;
window.toggleAuditTrail = toggleAuditTrail;
window.applySuggestion = applySuggestion;
window.dismissSuggestion = dismissSuggestion;
window.runClinicalValidation = runClinicalValidation;