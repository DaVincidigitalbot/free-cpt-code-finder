#!/usr/bin/env node
// Debug why 49000 isn't being suppressed

const fs = require('fs');

class DebugEngine {
    constructor() {
        this.modifierRules = JSON.parse(fs.readFileSync('./modifier_rules.json', 'utf8'));
    }
    
    checkProcedureHierarchy(procedures) {
        console.log('\n=== HIERARCHY CHECK ===');
        
        // FIRST PASS: Set tiers and families
        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            if (rules) {
                proc.hierarchyTier = rules.hierarchy_tier || 3;
                proc.codeFamily = rules.code_family || 'unclassified';
            }
            console.log(`${proc.code}: tier=${proc.hierarchyTier}, family=${proc.codeFamily}`);
        });

        console.log('\n=== CHECKING INCLUSIVE RELATIONSHIPS ===');
        // SECOND PASS: Check inclusive relationships
        procedures.forEach(proc => {
            const rules = this.modifierRules[proc.code];
            if (!rules) return;

            console.log(`\nChecking ${proc.code}:`);
            console.log(`  inclusive_of: ${JSON.stringify(rules.inclusive_of || [])}`);
            
            if (rules.inclusive_of && rules.inclusive_of.length > 0) {
                procedures.forEach(otherProc => {
                    if (otherProc.id !== proc.id && rules.inclusive_of.includes(otherProc.code)) {
                        console.log(`  → ${otherProc.code} SHOULD BE SUPPRESSED (included in ${proc.code})`);
                        otherProc.rank = 'included';
                        otherProc.adjustedWRVU = 0;
                        otherProc.explanations = otherProc.explanations || [];
                        otherProc.explanations.push(`Included in primary procedure ${proc.code} — not separately billable`);
                    }
                });
            }
        });
        
        console.log('\n=== RESULTS ===');
        procedures.forEach(proc => {
            console.log(`${proc.code}: rank=${proc.rank || 'unset'}, adjustedWRVU=${proc.adjustedWRVU || 'unset'}`);
        });
    }
}

const engine = new DebugEngine();

// Test scenario: ex lap + splenectomy + bowel
const procedures = [
    {id: 'proc_0', code: "49000", description: "Exploratory laparotomy", work_rvu: 10.5, modifiers: [], adjustedWRVU: 10.5, explanations: []},
    {id: 'proc_1', code: "38100", description: "Splenectomy", work_rvu: 18.2, modifiers: [], adjustedWRVU: 18.2, explanations: []},
    {id: 'proc_2', code: "44120", description: "Small bowel resection", work_rvu: 22.1, modifiers: [], adjustedWRVU: 22.1, explanations: []}
];

engine.checkProcedureHierarchy(procedures);