#!/usr/bin/env node
const fs = require('fs');

// Load engine
class TestEngine {
    constructor() {
        this.modifierRules = JSON.parse(fs.readFileSync('./modifier_rules.json', 'utf8'));
        this.ncciBundles = JSON.parse(fs.readFileSync('./ncci_bundles.json', 'utf8'));
    }
    
    calculateConfidence(analysis) {
        let score = 100;
        const factors = [];
        const procedures = analysis.procedures || [];
        const warnings = analysis.warnings || [];

        const unknownRules = procedures.filter(p => !this.modifierRules[p.code]);
        if (unknownRules.length > 0) {
            const penalty = unknownRules.length * 15;
            score -= penalty;
            factors.push({ factor: `${unknownRules.length} procedures without known rules`, impact: -penalty });
        }

        const ncciWarnings = warnings.filter(w => w.type === 'ncci_bundle' && w.severity === 'warning');
        if (ncciWarnings.length > 0) {
            const penalty = ncciWarnings.length * 30;
            score -= penalty;
            factors.push({ factor: `${ncciWarnings.length} unresolved NCCI bundles`, impact: -penalty });
        }

        const globalViolations = warnings.filter(w => w.type === 'global_period_violation');
        if (globalViolations.length > 0) {
            const penalty = globalViolations.length * 25;
            score -= penalty;
            factors.push({ factor: `${globalViolations.length} global period violations`, impact: -penalty });
        }

        const roleErrors = warnings.filter(w => w.type === 'role_not_allowed');
        if (roleErrors.length > 0) {
            const penalty = roleErrors.length * 15;
            score -= penalty;
            factors.push({ factor: `${roleErrors.length} invalid surgeon role assignments`, impact: -penalty });
        }

        score = Math.max(0, Math.min(100, score));
        
        let overall, recommendation;
        if (score >= 95) { overall = 'high'; recommendation = 'Safe to submit'; }
        else if (score >= 80) { overall = 'medium'; recommendation = 'Review required'; }
        else { overall = 'low'; recommendation = 'DO NOT SUBMIT'; }

        return { overall, score, factors, recommendation };
    }
}

const engine = new TestEngine();

// Test ex lap + splenectomy + bowel
const procedures = [
    {code: "49000", description: "Exploratory laparotomy", work_rvu: 10.5},
    {code: "38100", description: "Splenectomy", work_rvu: 18.2},
    {code: "44120", description: "Small bowel resection", work_rvu: 22.1}
];

// Check rule coverage
procedures.forEach(proc => {
    const hasRules = !!engine.modifierRules[proc.code];
    console.log(`${proc.code}: rules=${hasRules}`);
});

// Simple confidence calc
const confidence = engine.calculateConfidence({procedures, warnings: []});
console.log('\nConfidence for ex lap + splenectomy + bowel:');
console.log(`Score: ${confidence.score}% (${confidence.overall})`);
console.log(`Factors: ${confidence.factors.map(f => f.factor).join(', ') || 'none'}`);
console.log(`Block threshold (<80): ${confidence.score < 80 ? 'BLOCKED' : 'ALLOWED'}`);