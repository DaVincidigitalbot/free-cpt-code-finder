#!/usr/bin/env node
const fs = require('fs');
const modifierRules = JSON.parse(fs.readFileSync('./modifier_rules.json', 'utf8'));
const ncciBundles = JSON.parse(fs.readFileSync('./ncci_bundles.json', 'utf8'));

function isMajor(family) {
    return ['bowel_resection','cardiac_cabg','cardiac_valve','vascular_open','splenectomy','pancreas','liver','kidney','component_separation'].includes(family);
}

function trace(name, procs) {
    console.log(`\n=== ${name} ===`);
    
    // Get families and tiers
    procs.forEach(p => {
        const r = modifierRules[p.code] || {};
        p.tier = r.hierarchy_tier || 3;
        p.family = r.code_family || 'unclassified';
        p.inclusiveOf = r.inclusive_of || [];
    });
    
    // Check suppression
    procs.forEach(p => {
        p.suppressed = false;
        procs.forEach(other => {
            if (other.code !== p.code && other.inclusiveOf.includes(p.code)) {
                p.suppressed = true;
                p.suppressedBy = other.code;
            }
        });
    });
    
    // Check never_primary_with for demotion
    procs.forEach(p => {
        const r = modifierRules[p.code] || {};
        if (r.never_primary_with) {
            procs.forEach(other => {
                if (other.code !== p.code && r.never_primary_with.includes(other.code)) {
                    p.tier = Math.max(p.tier, other.tier + 1);
                }
            });
        }
    });
    
    // Sort by tier then wRVU for ranking
    const active = procs.filter(p => !p.suppressed);
    active.sort((a, b) => a.tier !== b.tier ? a.tier - b.tier : b.rvu - a.rvu);
    
    const primary = active[0];
    const secondaries = active.slice(1);
    
    console.log(`Primary: ${primary.code} (tier ${primary.tier}, family ${primary.family}, wRVU ${primary.rvu})`);
    
    let total = primary.rvu;
    
    secondaries.forEach(s => {
        const sameFamily = s.family === primary.family && s.family !== 'unclassified';
        const crossMajor = isMajor(s.family) && isMajor(primary.family) && !sameFamily;
        
        let reduction, reason;
        if (sameFamily) { reduction = 0.5; reason = 'same-family 50%'; }
        else if (crossMajor) { reduction = 0.6; reason = 'cross-major 60%'; }
        else { reduction = 0.5; reason = 'default 50%'; }
        
        const adjusted = Math.round(s.rvu * reduction * 100) / 100;
        total += adjusted;
        console.log(`Secondary: ${s.code} (tier ${s.tier}, family ${s.family}, wRVU ${s.rvu} × ${reduction} = ${adjusted}) [${reason}]`);
    });
    
    procs.filter(p => p.suppressed).forEach(p => {
        console.log(`Suppressed: ${p.code} (included in ${p.suppressedBy}, $0)`);
    });
    
    total = Math.round(total * 100) / 100;
    console.log(`TOTAL wRVU: ${total}`);
    
    // Check NCCI warnings that trigger blocking
    let ncciWarnings = 0;
    procs.forEach(p => {
        const bundle = ncciBundles.bundles[p.code];
        if (bundle) {
            procs.forEach(other => {
                if (other.code !== p.code && bundle.column2_codes.includes(other.code)) {
                    if (bundle.modifier59_allowed && !other.suppressed) {
                        ncciWarnings++;
                        console.log(`⚠️ NCCI WARNING: ${other.code} bundles with ${p.code} (modifier59_allowed=true → needs -59)`);
                    }
                }
            });
        }
    });
    
    // Confidence
    let confidence = 100;
    const unknowns = procs.filter(p => !modifierRules[p.code]).length;
    if (unknowns > 0) confidence -= unknowns * 15;
    if (ncciWarnings > 0) confidence -= ncciWarnings * 30;
    console.log(`Confidence: ${confidence}% (unknowns: ${unknowns}, ncci_warnings: ${ncciWarnings})`);
    console.log(`Blocked (< 80): ${confidence < 80 ? 'YES' : 'NO'}`);
    
    return total;
}

// Trace all 6 failures
trace("Trauma: Ex lap + splenectomy + bowel", [
    {code: "49000", rvu: 10.5},
    {code: "38100", rvu: 18.2},
    {code: "44120", rvu: 22.1}
]);

trace("Trauma: Laparotomy + colostomy creation", [
    {code: "49000", rvu: 10.5},
    {code: "44140", rvu: 20.5},
    {code: "44141", rvu: 23.2}
]);

trace("Trauma: Splenectomy + distal pancreatectomy", [
    {code: "38100", rvu: 18.2},
    {code: "48140", rvu: 28.5}
]);

trace("Trauma: Ex lap + bladder repair + colon repair", [
    {code: "49000", rvu: 10.5},
    {code: "44604", rvu: 16.8},
    {code: "51860", rvu: 14.2}
]);

trace("Cardiac: CABG + valve replacement", [
    {code: "33535", rvu: 45.2},
    {code: "33405", rvu: 52.8}
]);

trace("Edge Case: 10+ procedures MPPR cascade", [
    {code: "44120", rvu: 22.1},
    {code: "44140", rvu: 20.5},
    {code: "38100", rvu: 18.2},
    {code: "51860", rvu: 14.2},
    {code: "49000", rvu: 10.5}
]);
