#!/usr/bin/env python3
"""
Modifier Rules Enhancement Script for FreeCPTCodeFinder.com
Adds comprehensive billing intelligence fields to all 559 CPT codes
"""

import json
import re

def load_modifier_rules():
    with open('modifier_rules.json', 'r') as f:
        return json.load(f)

def save_modifier_rules(rules):
    with open('modifier_rules.json', 'w') as f:
        json.dump(rules, f, indent=2)

def determine_hierarchy_tier(code, category, global_period):
    """
    Determine procedure hierarchy tier (1=most complex, 5=simplest)
    Based on global period, procedure complexity, and type
    """
    code_num = int(code) if code.isdigit() else 0
    global_period_int = int(global_period) if isinstance(global_period, (str, int, float)) and str(global_period).isdigit() else 0
    
    # Tier 1: Major surgery (global 90)
    if global_period_int == 90:
        # Major organ procedures
        if code_num >= 38100 and code_num <= 38999:  # Hematologic/lymphatic
            return 1
        if code_num >= 44100 and code_num <= 44999:  # Intestinal
            return 1
        if code_num >= 47000 and code_num <= 47999:  # Liver/biliary
            return 1
        if code_num >= 33000 and code_num <= 33999:  # Cardiovascular
            return 1
        if code_num >= 32000 and code_num <= 32999:  # Respiratory
            return 1
        if code_num >= 50000 and code_num <= 50999:  # Urinary
            return 1
        return 2  # Other major surgery
    
    # Tier 2: Intermediate procedures (global 10-90)
    if global_period_int >= 10:
        if category in ['hernia_repair', 'breast', 'thyroid']:
            return 2
        return 3
    
    # Tier 3: Minor procedures (global 0-10)
    if category in ['endoscopy', 'biopsy']:
        return 4
    
    # Tier 4: Simple procedures
    if category in ['incision_drainage', 'debridement']:
        return 5
    
    # Default tier 3
    return 3

def determine_inclusive_of(code, category, global_period=0):
    """
    Determine what procedures this code inherently includes
    """
    code_num = int(code) if code.isdigit() else 0
    inclusive = []
    
    # ENT sinus hierarchies
    if code == '31253':  # Total ethmoidectomy
        inclusive = ['31254']  # Includes partial ethmoidectomy
    elif code in ['31254', '31255', '31256', '31267', '31276', '31287', '31288']:
        inclusive = ['31231']  # All therapeutic sinus codes include diagnostic endoscopy
    
    # T&A procedures
    elif code in ['42820', '42821']:
        inclusive = ['42830']  # T&A includes adenoidectomy
    
    # Laparoscopic procedures include diagnostic laparoscopy
    elif code == '47562':  # Lap chole
        inclusive = ['49320']  # Includes diagnostic laparoscopy
    elif code_num >= 44180 and code_num <= 44238:  # Lap bowel procedures
        inclusive = ['49320']
    elif code_num >= 49650 and code_num <= 49659:  # Lap hernia repairs
        inclusive = ['49320']
    
    # CABG procedures
    elif code in ['33533', '33534', '33535', '33536']:  # CABG procedures
        if '33508' in code:  # Don't double-include
            pass
        else:
            inclusive = []  # 33508 is add-on, not included
    
    # Critical care includes procedures
    elif code == '99291':
        inclusive = ['36556', '36620', '31500', '32551', '62270']
    
    # Debridement hierarchy - deeper includes shallower
    elif code == '11044':  # Bone debridement
        inclusive = ['11042', '11043']  # Includes skin and subcutaneous
    elif code == '11043':  # Subcutaneous debridement
        inclusive = ['11042']  # Includes skin debridement
    
    # All surgical procedures include wound closure
    if isinstance(global_period, (int, float)) and global_period >= 10:  # Surgical procedures
        wound_closure_codes = [str(i) for i in range(12001, 13161)]
        inclusive.extend(wound_closure_codes[:5])  # Add some common wound closure codes
    
    return inclusive

def determine_never_primary_with(code, category):
    """
    Determine which procedures should always be primary over this one
    """
    code_num = int(code) if code.isdigit() else 0
    never_primary = []
    
    # Exploratory laparotomy (49000) is never primary with organ-specific surgery
    if code == '49000':
        never_primary = ['38100', '44120', '44140', '47550', '47562', '50240']
    
    # Diagnostic procedures never primary with therapeutic
    elif code == '31231':  # Diagnostic nasal endoscopy
        never_primary = ['31254', '31255', '31256', '31267', '31276', '31287', '31288']
    
    # Diagnostic laparoscopy never primary with therapeutic lap
    elif code == '49320':
        never_primary = ['44180', '47562', '49650']
    
    # Add-on codes never primary with their base procedures
    elif code == '49568':  # Hernia mesh
        never_primary = ['49505', '49507', '49520', '49525']
    elif code == '33508':  # Vein harvest
        never_primary = ['33533', '33534', '33535', '33536']
    
    return never_primary

def determine_specialty_rules(code, category):
    """
    Determine specialty-specific bundling rules
    """
    code_num = int(code) if code.isdigit() else 0
    
    rules = {
        "ent": {"always_with": [], "never_with": []},
        "general": {"always_with": [], "never_with": []}
    }
    
    # ENT specialty rules
    if code_num >= 30000 and code_num <= 32999:  # ENT range
        if code == '30520':  # Septoplasty
            rules["ent"]["always_with"] = ['30140']  # Often with turbinate reduction
        elif code == '31254':  # Partial ethmoidectomy
            rules["ent"]["never_with"] = ['31253']  # Never with total ethmoidectomy
    
    # General surgery rules
    elif code_num >= 44000 and code_num <= 49999:  # General surgery range
        if code == '44005':  # Lysis of adhesions
            rules["general"]["never_with"] = ['44120', '44140']  # Usually bundled with bowel resection
        elif code == '49000':  # Exploratory laparotomy
            rules["general"]["never_with"] = ['38100', '44120']  # Usually bundled with organ-specific
    
    return rules

def determine_payer_notes(code, category, global_period):
    """
    Determine payer-specific billing notes
    """
    notes = {"medicare": "", "commercial": ""}
    global_period_int = int(global_period) if isinstance(global_period, (str, int, float)) and str(global_period).isdigit() else 0
    
    # Medicare-specific notes
    if global_period_int == 90:
        notes["medicare"] = "Major surgery - 90-day global period applies"
    elif category == 'endoscopy':
        notes["medicare"] = "Multiple endoscopy rule may apply"
    
    # Commercial payer notes
    if category == 'reconstructive':
        notes["commercial"] = "May require prior authorization for reconstructive procedures"
    elif int(code) if code.isdigit() else 0 >= 15000 and int(code) if code.isdigit() else 0 <= 15999:
        notes["commercial"] = "Plastic surgery codes - verify coverage"
    
    return notes

def determine_x_modifier_eligible(code):
    """
    Determine if procedure is eligible for X{EPSU} modifiers
    """
    code_num = int(code) if code.isdigit() else 0
    
    # Most surgical procedures are eligible for X modifiers
    # Add-on codes typically are not
    if code_num >= 10000 and code_num <= 69999:  # Surgery range
        return True
    
    return False

def upgrade_rules():
    """
    Main upgrade function
    """
    print("Loading modifier rules...")
    rules = load_modifier_rules()
    
    print(f"Upgrading {len(rules)} CPT codes...")
    
    for code, data in rules.items():
        category = data.get('category', '')
        global_period = data.get('global_period', 0)
        
        # Add new fields
        data['inclusive_of'] = determine_inclusive_of(code, category, global_period)
        data['never_primary_with'] = determine_never_primary_with(code, category) 
        data['specialty_bundle_rules'] = determine_specialty_rules(code, category)
        data['payer_notes'] = determine_payer_notes(code, category, global_period)
        data['x_modifier_eligible'] = determine_x_modifier_eligible(code)
        data['hierarchy_tier'] = determine_hierarchy_tier(code, category, global_period)
        
        print(f"✓ Enhanced {code}")
    
    print("Saving enhanced modifier rules...")
    save_modifier_rules(rules)
    print("✓ Done!")

if __name__ == '__main__':
    upgrade_rules()