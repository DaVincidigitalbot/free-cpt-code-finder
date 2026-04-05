#!/usr/bin/env python3
"""
Fix test expectations based on hardening changes:
1. Procedure suppression (49000 included in organ-specific procedures)
2. Stricter confidence thresholds (95=HIGH, 80=MED, <80=BLOCK)
3. Advanced MPPR logic (family-aware reductions)
"""
import json
import re

# Load test file
with open('kill_test_suite.js', 'r') as f:
    content = f.read()

# Define fixes based on new logic
fixes = [
    # Trauma: Ex lap + splenectomy + bowel - 49000 should be included (not billable)
    {
        'scenario': 'Trauma: Ex lap + splenectomy + small bowel resection',
        'old_wRVU': '36.45',
        'new_wRVU': '31.2',  # 22.1 + 9.1 (49000 = $0, included)
        'old_billable': '3/3',
        'new_billable': '2/3'  # 49000 not billable
    },
    # Other trauma scenarios with 49000 + organ procedures
    {
        'scenario': 'Trauma: Ex lap + liver repair + diaphragm repair',
        'recalculate': True  # Will need manual check
    },
    {
        'scenario': 'Trauma: Ex lap + bladder repair + colon repair', 
        'recalculate': True
    },
    {
        'scenario': 'Edge Case: 10+ procedures in one case',
        'recalculate': True  # Complex MPPR cascade
    }
]

print("=== ANALYZING TEST EXPECTATIONS ===")

# Function to find and update test scenarios
def update_scenario_expectation(content, scenario_name, old_wrvu, new_wrvu, old_billable=None, new_billable=None):
    """Update wRVU and billable procedure count for a scenario"""
    
    # Find the scenario
    pattern = rf'name: "{re.escape(scenario_name)}".*?}}\s*}}'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"❌ Could not find scenario: {scenario_name}")
        return content
    
    scenario_block = match.group(0)
    
    # Update wRVU expectation
    if old_wrvu and new_wrvu:
        old_pattern = rf'totalWRVU: {re.escape(old_wrvu)}'
        new_replacement = f'totalWRVU: {new_wrvu}'
        
        if re.search(old_pattern, scenario_block):
            content = content.replace(scenario_block, 
                re.sub(old_pattern, new_replacement, scenario_block))
            print(f"✅ Updated {scenario_name}: wRVU {old_wrvu} → {new_wrvu}")
        else:
            print(f"⚠️  Could not find wRVU {old_wrvu} in {scenario_name}")
    
    return content

# Apply known fixes
for fix in fixes:
    if not fix.get('recalculate'):
        content = update_scenario_expectation(
            content, 
            fix['scenario'], 
            fix.get('old_wRVU'), 
            fix.get('new_wRVU'),
            fix.get('old_billable'),
            fix.get('new_billable')
        )

print("\n=== CONFIDENCE THRESHOLD UPDATES ===")

# Lower confidence thresholds for scenarios that should now be MEDIUM (not HIGH)
# Any scenario with unknown codes, NCCI warnings, etc. may drop below 95%

# Find scenarios that might have 85-94% confidence (now MEDIUM, not HIGH)
medium_confidence_scenarios = [
    "Trauma: Damage control laparotomy with abbreviated procedure",  # Unknown 49002
    "Trauma: Negative ex lap + wound closure",  # Multiple wound codes
    "ENT: Diagnostic nasal endoscopy + maxillary antrostomy",  # Possible NCCI
]

print("Scenarios likely to have MEDIUM confidence (80-94%):")
for scenario in medium_confidence_scenarios:
    print(f"  - {scenario}")

print("\n=== MANUAL REVIEW NEEDED ===")
print("The following scenarios require manual wRVU recalculation:")
print("1. Trauma: Ex lap + liver repair + diaphragm repair")
print("   - 49000 may be included in 47350 (liver repair)")
print("   - Check if 39501 (diaphragm) also includes 49000") 
print("2. Trauma: Ex lap + bladder repair + colon repair")
print("   - Both 51860 (bladder) and 44604 (colon repair) include 49000")
print("   - Only highest wRVU should be primary")
print("3. ENT multi-procedure scenarios")  
print("   - Code family MPPR logic may change payment percentages")
print("4. Edge Case: 10+ procedures")
print("   - Complex family-aware MPPR cascade")

print("\n=== BLOCKING THRESHOLD CHANGES ===")
print("Confidence threshold: <80% now blocks (was <50%)")
print("Scenarios with <95% confidence will be labeled MEDIUM, not HIGH")
print("Review all shouldBlock: false expectations")

# Write the updated file
with open('kill_test_suite.js', 'w') as f:
    f.write(content)

print("\n✅ Test expectations updated")
print("🔧 Manual review still required for complex scenarios")