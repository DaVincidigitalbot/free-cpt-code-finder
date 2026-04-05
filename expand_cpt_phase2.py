#!/usr/bin/env python3
"""
PHASE 2: CPT EXPANSION — Target 5,000+ codes
Runs in chunks to avoid timeouts. Each chunk adds a specialty block.
"""
import json, os
os.chdir('/home/setup/Desktop/FreeCPTCodeFinder')

with open('cpt_database.json') as f:
    db = json.load(f)

start_count = len(db)
print(f"Starting with {start_count} codes")

def add(code, desc, cat, subcat, spec, wrvu, gp=0, bilateral=False, addon=False,
        cosurgeon=False, assistant=True, tier=3, family='unclassified',
        inclusive_of=None, never_primary=None, mods=None):
    if code in db:
        return
    db[code] = {
        "code": code, "description": desc, "category": cat, "subcategory": subcat,
        "specialty": spec, "work_rvu": wrvu, "global_period_days": gp,
        "bilateral_eligible": bilateral, "addon_code": addon,
        "cosurgeon_eligible": cosurgeon, "assistant_allowed": assistant,
        "hierarchy_tier": tier, "code_family": family,
        "inclusive_of": inclusive_of or [], "never_primary_with": never_primary or [],
        "typical_modifiers": mods or [], "estimated": True
    }

# ============================================================================
# E/M DEEP EXPANSION
# ============================================================================

# Office/Outpatient New - already have 99202-99205
# Telephone/Online
for c, d, w in [
    ("99441", "Telephone E/M, 5-10 min", 0.50),
    ("99442", "Telephone E/M, 11-20 min", 0.97),
    ("99443", "Telephone E/M, 21-30 min", 1.50),
    ("99421", "Online digital E/M, 5-10 min", 0.25),
    ("99422", "Online digital E/M, 11-20 min", 0.50),
    ("99423", "Online digital E/M, 21+ min", 0.75),
]:
    add(c, d, "E/M", "telehealth", "internal_medicine", w, family='em', tier=4)

# Pediatric/Preventive
for c, d, w in [
    ("99381", "Preventive visit, new, infant", 1.50),
    ("99382", "Preventive visit, new, 1-4 years", 1.60),
    ("99383", "Preventive visit, new, 5-11 years", 1.60),
    ("99384", "Preventive visit, new, 12-17 years", 1.92),
    ("99385", "Preventive visit, new, 18-39 years", 1.92),
    ("99386", "Preventive visit, new, 40-64 years", 2.33),
    ("99387", "Preventive visit, new, 65+ years", 2.50),
    ("99391", "Preventive visit, established, infant", 1.22),
    ("99392", "Preventive visit, established, 1-4 years", 1.36),
    ("99393", "Preventive visit, established, 5-11 years", 1.36),
    ("99394", "Preventive visit, established, 12-17 years", 1.50),
    ("99395", "Preventive visit, established, 18-39 years", 1.50),
    ("99396", "Preventive visit, established, 40-64 years", 1.75),
    ("99397", "Preventive visit, established, 65+ years", 1.92),
]:
    add(c, d, "E/M", "preventive", "internal_medicine", w, family='em', tier=4)

# Newborn/NICU
for c, d, w in [
    ("99460", "Initial hospital care, newborn, per day", 1.50),
    ("99461", "Initial care, newborn, not in hospital", 1.00),
    ("99462", "Subsequent hospital care, normal newborn", 0.62),
    ("99463", "Initial hospital care, newborn, admit/discharge same day", 1.50),
    ("99464", "Attendance at delivery", 1.98),
    ("99465", "Delivery/birthing room resuscitation", 2.70),
    ("99468", "Initial inpatient neonatal critical care, <28 days", 18.48),
    ("99469", "Subsequent inpatient neonatal critical care", 8.50),
    ("99471", "Initial inpatient pediatric critical care, 29 days-24 months", 15.48),
    ("99472", "Subsequent inpatient pediatric critical care, 29 days-24 months", 7.78),
    ("99475", "Initial inpatient pediatric critical care, 2-5 years", 13.00),
    ("99476", "Subsequent inpatient pediatric critical care, 2-5 years", 6.50),
    ("99477", "Initial day of hospital care for neonates, unstable", 6.90),
    ("99478", "Subsequent intensive care, very low birth weight, <1500g", 3.66),
    ("99479", "Subsequent intensive care, low birth weight, 1500-2500g", 2.40),
    ("99480", "Subsequent intensive care, normal birth weight, 2501-5000g", 1.82),
]:
    add(c, d, "E/M", "neonatal_critical", "pediatrics", w, family='em', tier=4)

# Interprofessional Consultation
for c, d, w in [
    ("99446", "Interprofessional phone/internet consultation, 5-10 min", 0.35),
    ("99447", "Interprofessional phone/internet consultation, 11-20 min", 0.70),
    ("99448", "Interprofessional phone/internet consultation, 21-30 min", 1.05),
    ("99449", "Interprofessional phone/internet consultation, 31+ min", 1.40),
    ("99451", "Interprofessional phone/internet assessment, 5+ min", 0.65),
    ("99452", "Interprofessional phone/internet referral, 16-30 min", 0.49),
]:
    add(c, d, "E/M", "interprofessional", "internal_medicine", w, family='em', tier=4)

print(f"After E/M expansion: {len(db)} codes (+{len(db)-start_count})")

# ============================================================================
# GENERAL SURGERY DEEP EXPANSION
# ============================================================================

gen_surg = [
    # Skin/Subcutaneous
    ("10021", "Fine needle aspiration without imaging guidance", 0.98, 0),
    ("10040", "Acne surgery, comedones/cysts/pustules", 0.76, 10),
    ("10060", "I&D abscess, simple", 2.05, 10),
    ("10061", "I&D abscess, complicated or multiple", 3.12, 10),
    ("10080", "I&D pilonidal cyst, simple", 2.75, 10),
    ("10081", "I&D pilonidal cyst, complicated", 3.97, 10),
    ("10120", "Incision, removal of foreign body, subcutaneous", 2.25, 10),
    ("10121", "Incision, removal of foreign body, subcutaneous, complicated", 4.36, 10),
    ("10140", "I&D hematoma, seroma", 2.52, 10),
    ("10160", "Puncture aspiration of abscess/hematoma/bulla/cyst", 1.33, 0),
    ("10180", "I&D of complex postoperative wound infection", 3.84, 10),
    # Excision - Benign Lesions
    ("11400", "Excision, benign lesion, trunk/arms/legs, ≤0.5 cm", 1.39, 10),
    ("11401", "Excision, benign lesion, trunk/arms/legs, 0.6-1.0 cm", 1.74, 10),
    ("11402", "Excision, benign lesion, trunk/arms/legs, 1.1-2.0 cm", 2.19, 10),
    ("11403", "Excision, benign lesion, trunk/arms/legs, 2.1-3.0 cm", 2.62, 10),
    ("11404", "Excision, benign lesion, trunk/arms/legs, 3.1-4.0 cm", 3.11, 10),
    ("11406", "Excision, benign lesion, trunk/arms/legs, >4.0 cm", 3.91, 10),
    ("11420", "Excision, benign lesion, scalp/neck/hands/feet, ≤0.5 cm", 1.62, 10),
    ("11421", "Excision, benign lesion, scalp/neck/hands/feet, 0.6-1.0 cm", 2.08, 10),
    ("11422", "Excision, benign lesion, scalp/neck/hands/feet, 1.1-2.0 cm", 2.53, 10),
    ("11423", "Excision, benign lesion, scalp/neck/hands/feet, 2.1-3.0 cm", 3.04, 10),
    ("11424", "Excision, benign lesion, scalp/neck/hands/feet, 3.1-4.0 cm", 3.67, 10),
    ("11426", "Excision, benign lesion, scalp/neck/hands/feet, >4.0 cm", 4.43, 10),
    ("11440", "Excision, benign lesion, face/ears/eyelids/nose/lips, ≤0.5 cm", 1.88, 10),
    ("11441", "Excision, benign lesion, face/ears/eyelids/nose/lips, 0.6-1.0 cm", 2.31, 10),
    ("11442", "Excision, benign lesion, face/ears/eyelids/nose/lips, 1.1-2.0 cm", 2.81, 10),
    ("11443", "Excision, benign lesion, face/ears/eyelids/nose/lips, 2.1-3.0 cm", 3.39, 10),
    ("11444", "Excision, benign lesion, face/ears/eyelids/nose/lips, 3.1-4.0 cm", 4.09, 10),
    ("11446", "Excision, benign lesion, face/ears/eyelids/nose/lips, >4.0 cm", 5.23, 10),
    # Excision - Malignant Lesions
    ("11600", "Excision, malignant lesion, trunk/arms/legs, ≤0.5 cm", 1.84, 10),
    ("11601", "Excision, malignant lesion, trunk/arms/legs, 0.6-1.0 cm", 2.25, 10),
    ("11602", "Excision, malignant lesion, trunk/arms/legs, 1.1-2.0 cm", 2.87, 10),
    ("11603", "Excision, malignant lesion, trunk/arms/legs, 2.1-3.0 cm", 3.45, 10),
    ("11604", "Excision, malignant lesion, trunk/arms/legs, 3.1-4.0 cm", 4.04, 10),
    ("11606", "Excision, malignant lesion, trunk/arms/legs, >4.0 cm", 4.80, 10),
    ("11620", "Excision, malignant lesion, scalp/neck/hands/feet, ≤0.5 cm", 2.04, 10),
    ("11621", "Excision, malignant lesion, scalp/neck/hands/feet, 0.6-1.0 cm", 2.43, 10),
    ("11622", "Excision, malignant lesion, scalp/neck/hands/feet, 1.1-2.0 cm", 3.10, 10),
    ("11623", "Excision, malignant lesion, scalp/neck/hands/feet, 2.1-3.0 cm", 3.69, 10),
    ("11624", "Excision, malignant lesion, scalp/neck/hands/feet, 3.1-4.0 cm", 4.36, 10),
    ("11626", "Excision, malignant lesion, scalp/neck/hands/feet, >4.0 cm", 5.33, 10),
    ("11640", "Excision, malignant lesion, face/ears/eyelids/nose/lips, ≤0.5 cm", 2.33, 10),
    ("11641", "Excision, malignant lesion, face/ears/eyelids/nose/lips, 0.6-1.0 cm", 2.77, 10),
    ("11642", "Excision, malignant lesion, face/ears/eyelids/nose/lips, 1.1-2.0 cm", 3.44, 10),
    ("11643", "Excision, malignant lesion, face/ears/eyelids/nose/lips, 2.1-3.0 cm", 4.21, 10),
    ("11644", "Excision, malignant lesion, face/ears/eyelids/nose/lips, 3.1-4.0 cm", 5.19, 10),
    ("11646", "Excision, malignant lesion, face/ears/eyelids/nose/lips, >4.0 cm", 6.26, 10),
    # Wound Repair - Simple
    ("12001", "Simple repair, scalp/neck/axillae/trunk/extremities, 2.5 cm or less", 1.39, 10),
    ("12002", "Simple repair, scalp/neck/axillae/trunk/extremities, 2.6-7.5 cm", 1.73, 10),
    ("12004", "Simple repair, scalp/neck/axillae/trunk/extremities, 7.6-12.5 cm", 2.33, 10),
    ("12005", "Simple repair, scalp/neck/axillae/trunk/extremities, 12.6-20.0 cm", 2.93, 10),
    ("12006", "Simple repair, scalp/neck/axillae/trunk/extremities, 20.1-30.0 cm", 3.33, 10),
    ("12007", "Simple repair, scalp/neck/axillae/trunk/extremities, >30.0 cm", 4.04, 10),
    ("12011", "Simple repair, face/ears/eyelids/nose/lips/mucous, 2.5 cm or less", 1.81, 10),
    ("12013", "Simple repair, face/ears/eyelids/nose/lips, 2.6-5.0 cm", 2.17, 10),
    ("12014", "Simple repair, face/ears/eyelids/nose/lips, 5.1-7.5 cm", 2.49, 10),
    ("12015", "Simple repair, face/ears/eyelids/nose/lips, 7.6-12.5 cm", 3.09, 10),
    ("12016", "Simple repair, face/ears/eyelids/nose/lips, 12.6-20.0 cm", 3.69, 10),
    ("12017", "Simple repair, face/ears/eyelids/nose/lips, 20.1-30.0 cm", 4.14, 10),
    ("12018", "Simple repair, face/ears/eyelids/nose/lips, >30.0 cm", 4.73, 10),
    # Wound Repair - Intermediate
    ("12031", "Intermediate repair, scalp/trunk/extremities, 2.5 cm or less", 2.49, 10),
    ("12032", "Intermediate repair, scalp/trunk/extremities, 2.6-7.5 cm", 2.93, 10),
    ("12034", "Intermediate repair, scalp/trunk/extremities, 7.6-12.5 cm", 3.48, 10),
    ("12035", "Intermediate repair, scalp/trunk/extremities, 12.6-20.0 cm", 4.26, 10),
    ("12036", "Intermediate repair, scalp/trunk/extremities, 20.1-30.0 cm", 4.86, 10),
    ("12037", "Intermediate repair, scalp/trunk/extremities, >30.0 cm", 5.62, 10),
    ("12041", "Intermediate repair, neck/hands/feet/genitalia, 2.5 cm or less", 2.93, 10),
    ("12042", "Intermediate repair, neck/hands/feet/genitalia, 2.6-7.5 cm", 3.09, 10),
    ("12044", "Intermediate repair, neck/hands/feet/genitalia, 7.6-12.5 cm", 3.50, 10),
    ("12045", "Intermediate repair, neck/hands/feet/genitalia, 12.6-20.0 cm", 4.20, 10),
    ("12046", "Intermediate repair, neck/hands/feet/genitalia, 20.1-30.0 cm", 4.88, 10),
    ("12047", "Intermediate repair, neck/hands/feet/genitalia, >30.0 cm", 5.38, 10),
    ("12051", "Intermediate repair, face/ears/eyelids/nose/lips, 2.5 cm or less", 3.04, 10),
    ("12052", "Intermediate repair, face/ears/eyelids/nose/lips, 2.6-5.0 cm", 3.42, 10),
    ("12053", "Intermediate repair, face/ears/eyelids/nose/lips, 5.1-7.5 cm", 3.87, 10),
    ("12054", "Intermediate repair, face/ears/eyelids/nose/lips, 7.6-12.5 cm", 4.42, 10),
    ("12055", "Intermediate repair, face/ears/eyelids/nose/lips, 12.6-20.0 cm", 5.12, 10),
    ("12056", "Intermediate repair, face/ears/eyelids/nose/lips, 20.1-30.0 cm", 5.80, 10),
    ("12057", "Intermediate repair, face/ears/eyelids/nose/lips, >30.0 cm", 6.63, 10),
    # Wound Repair - Complex
    ("13100", "Complex repair, trunk, 1.1-2.5 cm", 3.42, 10),
    ("13101", "Complex repair, trunk, 2.6-7.5 cm", 4.50, 10),
    ("13102", "Complex repair, trunk, each additional 5 cm", 1.24, 0),
    ("13120", "Complex repair, scalp/arms/legs, 1.1-2.5 cm", 3.73, 10),
    ("13121", "Complex repair, scalp/arms/legs, 2.6-7.5 cm", 4.70, 10),
    ("13122", "Complex repair, scalp/arms/legs, each additional 5 cm", 1.24, 0),
    ("13131", "Complex repair, forehead/cheeks/chin/mouth, 1.1-2.5 cm", 4.30, 10),
    ("13132", "Complex repair, forehead/cheeks/chin/mouth, 2.6-7.5 cm", 5.12, 10),
    ("13133", "Complex repair, forehead/cheeks/chin/mouth, each additional 5 cm", 1.46, 0),
    ("13151", "Complex repair, eyelids/nose/ears/lips, 1.1-2.5 cm", 4.80, 10),
    ("13152", "Complex repair, eyelids/nose/ears/lips, 2.6-7.5 cm", 5.61, 10),
    ("13153", "Complex repair, eyelids/nose/ears/lips, each additional 5 cm", 1.60, 0),
    ("13160", "Complex repair, late closure, each additional cm", 6.27, 90),
    # Debridement
    ("11042", "Debridement, subcutaneous, first 20 sq cm", 1.58, 0),
    ("11043", "Debridement, muscle/fascia, first 20 sq cm", 2.53, 0),
    ("11044", "Debridement, bone, first 20 sq cm", 3.51, 0),
    ("11045", "Debridement, subcutaneous, each additional 20 sq cm", 0.50, 0),
    ("11046", "Debridement, muscle/fascia, each additional 20 sq cm", 0.89, 0),
    ("11047", "Debridement, bone, each additional 20 sq cm", 1.19, 0),
    ("16020", "Burn dressing, small", 1.23, 0),
    ("16025", "Burn dressing, medium", 1.72, 0),
    ("16030", "Burn dressing, large", 2.45, 0),
    ("16035", "Escharotomy", 3.40, 0),
    # Hernia repairs - expanded
    ("49491", "Inguinal hernia repair, preterm infant, incarcerated", 8.88, 90),
    ("49495", "Inguinal hernia repair, infant <6 months, reducible", 6.15, 90),
    ("49496", "Inguinal hernia repair, infant <6 months, incarcerated", 7.92, 90),
    ("49500", "Inguinal hernia repair, child age 6 months-5 years, reducible", 5.58, 90),
    ("49501", "Inguinal hernia repair, child age 6 months-5 years, incarcerated", 7.21, 90),
    ("49505", "Inguinal hernia repair, initial, age 5+, reducible", 6.37, 90),
    ("49507", "Inguinal hernia repair, initial, age 5+, incarcerated", 7.83, 90),
    ("49520", "Inguinal hernia repair, recurrent, reducible", 7.39, 90),
    ("49521", "Inguinal hernia repair, recurrent, incarcerated", 9.11, 90),
    ("49525", "Inguinal hernia repair, sliding, any age", 7.06, 90),
    ("49540", "Lumbar hernia repair", 9.93, 90),
    ("49550", "Femoral hernia repair, initial, reducible", 6.37, 90),
    ("49553", "Femoral hernia repair, initial, incarcerated", 7.83, 90),
    ("49555", "Femoral hernia repair, recurrent, reducible", 7.39, 90),
    ("49557", "Femoral hernia repair, recurrent, incarcerated", 9.11, 90),
    ("49560", "Incisional hernia repair, initial, reducible", 10.41, 90),
    ("49561", "Incisional hernia repair, initial, incarcerated", 13.05, 90),
    ("49565", "Incisional hernia repair, recurrent, reducible", 12.55, 90),
    ("49566", "Incisional hernia repair, recurrent, incarcerated", 15.17, 90),
    ("49568", "Implantation of mesh, incisional hernia repair", 4.88, 0),
    ("49570", "Epigastric hernia repair, reducible", 5.07, 90),
    ("49572", "Epigastric hernia repair, incarcerated", 6.43, 90),
    ("49580", "Umbilical hernia repair, <5 years, reducible", 4.38, 90),
    ("49582", "Umbilical hernia repair, <5 years, incarcerated", 5.58, 90),
    ("49585", "Umbilical hernia repair, 5+ years, reducible", 4.80, 90),
    ("49587", "Umbilical hernia repair, 5+ years, incarcerated", 6.15, 90),
    ("49590", "Spigelian hernia repair, reducible", 7.83, 90),
    ("49650", "Laparoscopic inguinal hernia repair, initial", 7.21, 90),
    ("49651", "Laparoscopic inguinal hernia repair, recurrent", 8.44, 90),
    ("49652", "Laparoscopic ventral hernia repair, reducible", 10.58, 90),
    ("49653", "Laparoscopic ventral hernia repair, incarcerated", 12.87, 90),
    ("49654", "Laparoscopic incisional hernia repair, reducible", 11.76, 90),
    ("49655", "Laparoscopic incisional hernia repair, incarcerated", 14.13, 90),
    ("49656", "Laparoscopic ventral/incisional hernia, mesh insertion", 4.24, 0),
    # Appendectomy
    ("44950", "Appendectomy, open", 8.17, 90),
    ("44955", "Appendectomy, during another procedure", 2.60, 0),
    ("44960", "Appendectomy with abscess drainage", 10.48, 90),
    ("44970", "Laparoscopic appendectomy", 7.61, 90),
    # Colon/Rectum expanded
    ("44143", "Colectomy, partial, with colostomy and mucous fistula", 22.90, 90),
    ("44144", "Colectomy, partial, with resection and colostomy", 22.90, 90),
    ("44145", "Colectomy, partial, with creation of ileostomy", 23.73, 90),
    ("44146", "Colectomy, partial, with coloproctostomy", 23.73, 90),
    ("44147", "Colectomy, partial, with low colorectal anastomosis", 24.57, 90),
    ("44150", "Colectomy, total, with ileostomy or ileoproctostomy", 24.57, 90),
    ("44151", "Colectomy, total, with continent ileostomy", 26.24, 90),
    ("44155", "Colectomy, total, with ileostomy, including proctectomy", 27.07, 90),
    ("44156", "Colectomy, total, with continent ileostomy + proctectomy", 28.74, 90),
    ("44157", "Colectomy, total, with ileal pouch anal anastomosis", 30.41, 90),
    ("44158", "Colectomy, total, with IPAA without proctectomy", 28.74, 90),
    ("44160", "Colectomy, partial, with removal of terminal ileum", 22.90, 90),
    ("44180", "Laparoscopic enterolysis (adhesiolysis)", 10.73, 90),
    ("44186", "Laparoscopic jejunostomy", 8.84, 90),
    ("44187", "Laparoscopic ileostomy or jejunostomy, non-tube", 10.03, 90),
    ("44188", "Laparoscopic colostomy or skin level cecostomy", 9.65, 90),
    ("44202", "Laparoscopic resection of small intestine, single", 16.88, 90),
    ("44204", "Laparoscopic colectomy, partial", 20.75, 90),
    ("44205", "Laparoscopic colectomy, partial, with anastomosis", 21.75, 90),
    ("44206", "Laparoscopic colectomy, partial, with colostomy", 21.75, 90),
    ("44207", "Laparoscopic colectomy, partial, with colorectal anastomosis", 23.40, 90),
    ("44208", "Laparoscopic colectomy, partial, with IPAA", 27.24, 90),
    ("44210", "Laparoscopic colectomy, total, with ileostomy", 24.90, 90),
    ("44211", "Laparoscopic colectomy, total, with IPAA", 30.74, 90),
    ("44212", "Laparoscopic colectomy, total, with proctectomy", 27.40, 90),
    # Rectal
    ("45110", "Abdominoperineal resection (APR)", 25.47, 90),
    ("45111", "Proctectomy, partial", 17.50, 90),
    ("45112", "Proctectomy, combined abdominoperineal", 26.57, 90),
    ("45113", "Proctectomy with pull-through", 29.93, 90),
    ("45114", "Proctectomy, partial, with anterior resection", 20.83, 90),
    ("45116", "Proctectomy, partial, transperineal approach", 15.50, 90),
    ("45119", "Proctectomy with low anterior resection", 23.50, 90),
    ("45120", "Proctectomy, complete, perineal approach", 17.00, 90),
    ("45121", "Proctectomy, combined, with colostomy", 26.24, 90),
    ("45123", "Proctectomy, partial, for congenital megacolon", 22.50, 90),
    ("45126", "Pelvic exenteration for colorectal malignancy", 35.78, 90),
    ("45130", "Excision of rectal procidentia with anastomosis", 15.00, 90),
    ("45135", "Excision of rectal procidentia with sigmoidectomy", 18.00, 90),
    ("45160", "Excision of rectal tumor, transanal", 7.41, 90),
    ("45171", "Excision of rectal tumor, not incl muscularis, transanal", 5.30, 90),
    ("45172", "Excision of rectal tumor, incl muscularis, transanal", 6.58, 90),
    # Anorectal
    ("46020", "Incision of perianal abscess, superficial", 2.52, 10),
    ("46040", "Incision of perianal abscess, deep", 5.97, 10),
    ("46050", "Incision of perianal abscess, perirectal", 4.49, 10),
    ("46060", "Incision of ischiorectal/intramural abscess", 6.00, 10),
    ("46200", "Fissurectomy with sphincterotomy", 4.72, 90),
    ("46220", "Excision of anal papilla/tag", 1.83, 10),
    ("46221", "Hemorrhoidectomy, by rubber band ligation", 1.85, 0),
    ("46250", "Hemorrhoidectomy, external, complete", 4.30, 90),
    ("46255", "Hemorrhoidectomy, internal and external, single column", 4.49, 90),
    ("46257", "Hemorrhoidectomy, internal and external, with fissurectomy", 5.21, 90),
    ("46258", "Hemorrhoidectomy, internal and external, with fistulectomy", 5.21, 90),
    ("46260", "Hemorrhoidectomy, 2+ columns", 5.68, 90),
    ("46261", "Hemorrhoidectomy, 2+ columns with fissurectomy", 6.41, 90),
    ("46262", "Hemorrhoidectomy, 2+ columns with fistulectomy", 6.41, 90),
    ("46270", "Hemorrhoidectomy, external, complete (Whitehead type)", 6.74, 90),
    ("46280", "Hemorrhoidectomy, external, complete, extensive", 6.74, 90),
    ("46947", "Hemorrhoidopexy (stapled hemorrhoidectomy)", 6.78, 90),
    ("46270", "Surgical treatment of anal fistula (fistulotomy)", 4.61, 90),
    ("46275", "Surgical treatment of anal fistula, requiring division of sphincter", 5.97, 90),
    ("46280", "Surgical treatment of anal fistula, complex", 7.58, 90),
    ("46285", "Surgical treatment of anal fistula, 2nd stage", 4.20, 90),
    # Liver expanded
    ("47100", "Hepatotomy, wedge biopsy of liver", 10.87, 90),
    ("47120", "Hepatectomy, resection, partial lobectomy", 22.42, 90),
    ("47122", "Hepatectomy, trisegmentectomy", 35.47, 90),
    ("47125", "Hepatectomy, resection of liver, total left lobectomy", 28.74, 90),
    ("47130", "Hepatectomy, resection of liver, total right lobectomy", 35.47, 90),
    ("47133", "Donor hepatectomy, from living donor", 30.08, 90),
    ("47135", "Liver allotransplantation, orthotopic", 55.81, 90),
    ("47140", "Donor hepatectomy, from cadaver", 20.00, 90),
    ("47141", "Donor hepatectomy, from living donor, segment", 35.00, 90),
    # Pancreas expanded
    ("48100", "Biopsy of pancreas, open", 11.71, 90),
    ("48102", "Needle biopsy of pancreas, percutaneous", 2.50, 0),
    ("48105", "Resection of peripancreatic tumor", 18.50, 90),
    ("48120", "Excision of pancreatic lesion", 22.42, 90),
    ("48140", "Distal pancreatectomy", 21.75, 90),
    ("48145", "Distal pancreatectomy with splenectomy", 24.90, 90),
    ("48146", "Pancreatectomy, distal, with near-total", 25.00, 90),
    ("48148", "Excision of ampulla of Vater", 15.83, 90),
    ("48150", "Whipple (pancreaticoduodenectomy)", 38.28, 90),
    ("48152", "Whipple with pancreatojejunostomy", 38.28, 90),
    ("48153", "Total pancreatectomy", 34.62, 90),
    ("48154", "Total pancreatectomy with transplantation of pancreatic islets", 36.95, 90),
    ("48155", "Pancreatectomy, lateral, internal drainage (Puestow)", 27.07, 90),
    ("48160", "Pancreatojejunostomy, side-to-side anastomosis", 22.42, 90),
    # Thyroid/Parathyroid
    ("60100", "Thyroid biopsy, percutaneous", 1.40, 0),
    ("60200", "Thyroid cyst aspiration", 1.50, 0),
    ("60210", "Partial thyroid lobectomy, unilateral, with isthmusectomy", 9.03, 90),
    ("60212", "Partial thyroid lobectomy, with contralateral subtotal lobectomy", 10.36, 90),
    ("60220", "Total thyroid lobectomy, unilateral", 10.36, 90),
    ("60225", "Total thyroid lobectomy, with contralateral subtotal", 12.53, 90),
    ("60240", "Thyroidectomy, total or complete", 13.69, 90),
    ("60252", "Thyroidectomy, total, limited neck dissection", 15.87, 90),
    ("60254", "Thyroidectomy, total, radical neck dissection", 21.75, 90),
    ("60260", "Thyroidectomy for malignancy, total or subtotal", 15.87, 90),
    ("60270", "Thyroidectomy with substernal thyroid", 16.71, 90),
    ("60271", "Thyroidectomy with substernal thyroid, cervical approach", 18.55, 90),
    ("60280", "Excision of thyroglossal duct cyst", 7.06, 90),
    ("60281", "Excision of thyroglossal duct cyst, recurrent", 8.44, 90),
    ("60500", "Parathyroidectomy", 11.20, 90),
    ("60502", "Parathyroidectomy, re-exploration", 14.22, 90),
    ("60505", "Parathyroidectomy with mediastinal exploration", 16.71, 90),
    # Adrenal
    ("60540", "Adrenalectomy, unilateral, complete", 17.55, 90),
    ("60545", "Adrenalectomy, unilateral, with excision of adjacent retroperitoneal tumor", 22.42, 90),
    ("60650", "Laparoscopic adrenalectomy", 16.71, 90),
    # Spleen expanded
    ("38100", "Splenectomy, total", 14.70, 90),
    ("38101", "Splenectomy, total, en bloc", 18.55, 90),
    ("38102", "Splenectomy, partial", 15.54, 90),
    ("38115", "Splenectomy, with repair of ruptured spleen", 16.71, 90),
    ("38120", "Laparoscopic splenectomy", 14.38, 90),
    # Soft tissue tumors
    ("21930", "Excision soft tissue tumor, back/flank, subfascial, <5cm", 5.92, 90),
    ("21931", "Excision soft tissue tumor, back/flank, subfascial, 5+ cm", 8.80, 90),
    ("21932", "Excision soft tissue tumor, back/flank, deep, <5cm", 8.80, 90),
    ("21933", "Excision soft tissue tumor, back/flank, deep, 5+ cm", 12.00, 90),
    ("21935", "Radical resection of tumor, back/flank", 16.00, 90),
    ("27047", "Excision tumor, pelvis/hip, subcutaneous", 4.20, 90),
    ("27048", "Excision tumor, pelvis/hip, deep subfascial/intramuscular", 8.00, 90),
    ("27049", "Radical resection of tumor, pelvis/hip area, <5 cm", 16.50, 90),
    ("27059", "Radical resection of tumor, pelvis/hip area, 5+ cm", 20.00, 90),
    ("27327", "Excision tumor, thigh/knee, subcutaneous", 3.80, 90),
    ("27328", "Excision tumor, thigh/knee, deep subfascial", 7.00, 90),
    ("27337", "Excision tumor, thigh/knee, subfascial, <3 cm", 5.00, 90),
    ("27339", "Excision tumor, thigh/knee, subfascial, 3+ cm", 7.50, 90),
    ("27364", "Radical resection of tumor, thigh/knee area", 14.50, 90),
    # Chest wall
    ("19260", "Excision of chest wall tumor including ribs", 12.53, 90),
    ("19271", "Excision of chest wall tumor including ribs, with reconstruction", 18.55, 90),
    ("19272", "Excision of chest wall tumor, including ribs, with mesh/prosthesis", 20.42, 90),
    # Diaphragm
    ("39501", "Diaphragm repair, acute traumatic", 14.22, 90),
    ("39503", "Diaphragm repair, chronic (non-neonatal)", 18.55, 90),
    ("39540", "Diaphragm repair, neonatal", 20.42, 90),
    ("39560", "Diaphragm repair, neonatal, with prosthesis", 22.42, 90),
    # Thoracic
    ("32100", "Thoracotomy, exploratory", 13.02, 90),
    ("32110", "Thoracotomy, with control of traumatic hemorrhage", 18.55, 90),
    ("32120", "Thoracotomy, with therapeutic rib resection", 12.37, 90),
    ("32140", "Thoracotomy, with cyst removal", 12.37, 90),
    ("32141", "Thoracotomy, with resection-plication of emphysematous lung", 16.71, 90),
    ("32150", "Thoracotomy, with removal of intrapulmonary foreign body", 13.55, 90),
    ("32160", "Thoracotomy, with cardiac massage", 10.48, 90),
    ("32440", "Pneumonectomy, total", 23.73, 90),
    ("32442", "Pneumonectomy, sleeve (bronchoplasty)", 30.41, 90),
    ("32480", "Lobectomy, total or segmentectomy", 20.42, 90),
    ("32482", "Bilobectomy", 22.42, 90),
    ("32484", "Segmentectomy", 18.55, 90),
    ("32486", "Lobectomy with segmental resection", 24.90, 90),
    ("32488", "Completion pneumonectomy", 25.74, 90),
    ("32505", "Thoracotomy, with therapeutic wedge resection, initial", 15.37, 90),
    ("32506", "Thoracotomy, with therapeutic wedge resection, additional", 2.80, 0),
    ("32507", "Thoracotomy, with diagnostic wedge resection, followed by lobectomy", 21.26, 90),
    ("32551", "Tube thoracostomy, including water seal", 3.42, 10),
    ("32552", "Removal of indwelling tunneled pleural catheter", 1.20, 0),
    ("32553", "Thoracostomy, insertion of interpleural catheter with imaging", 2.81, 0),
    ("32601", "Thoracoscopy, diagnostic", 4.50, 0),
    ("32602", "Thoracoscopy, with biopsy", 5.30, 0),
    ("32604", "Thoracoscopy, with parietal pleurodesis", 5.97, 0),
    ("32606", "Thoracoscopy, with therapeutic aspiration of mediastinal cyst", 6.74, 0),
    ("32607", "Thoracoscopy, with diagnostic biopsy of lung infiltrate", 6.00, 90),
    ("32608", "Thoracoscopy, with diagnostic biopsy of lung nodule", 6.00, 90),
    ("32609", "Thoracoscopy, with biopsy of mediastinal mass", 6.74, 90),
    ("32650", "VATS pleurodesis (thoracoscopic)", 6.74, 90),
    ("32651", "VATS with partial pulmonary decortication", 10.48, 90),
    ("32652", "VATS with total pulmonary decortication", 14.22, 90),
    ("32653", "VATS with removal of intrapulmonary foreign body", 8.61, 90),
    ("32654", "VATS with control of traumatic hemorrhage", 12.37, 90),
    ("32655", "VATS with resection-plication for emphysematous lung", 12.37, 90),
    ("32656", "VATS with parietal pleurectomy", 8.61, 90),
    ("32662", "VATS with excision of mediastinal cyst/tumor/mass", 11.54, 90),
    ("32663", "VATS lobectomy, total or segmentectomy", 18.55, 90),
    ("32666", "VATS with therapeutic wedge resection, initial", 10.48, 90),
    ("32667", "VATS with therapeutic wedge resection, additional", 2.80, 0),
    ("32668", "VATS with diagnostic wedge followed by lobectomy", 19.38, 90),
    ("32669", "VATS with removal of 2+ lobes", 20.42, 90),
    ("32670", "VATS with pneumonectomy", 22.42, 90),
    ("32671", "VATS with sleeve lobectomy", 25.74, 90),
    # Esophagus
    ("43020", "Esophagotomy, cervical approach", 12.37, 90),
    ("43030", "Cricopharyngeal myotomy", 10.86, 90),
    ("43045", "Esophagotomy, thoracic approach", 18.55, 90),
    ("43100", "Excision of esophageal lesion", 14.22, 90),
    ("43101", "Excision of esophageal lesion, thoracic approach", 20.42, 90),
    ("43107", "Esophagectomy, total, cervical approach", 35.47, 90),
    ("43108", "Esophagectomy, total, with colon interposition", 39.28, 90),
    ("43112", "Esophagectomy, total, thoracoabdominal approach", 39.28, 90),
    ("43116", "Esophagectomy, partial, cervicothoracic approach", 33.79, 90),
    ("43117", "Esophagectomy, partial, thoracoabdominal approach", 35.47, 90),
    ("43118", "Esophagectomy, partial, neck/thorax/abdomen approach", 38.28, 90),
    ("43121", "Esophagectomy, partial, with jejunal transfer", 36.28, 90),
    ("43122", "Esophagectomy, partial, with colon interposition", 38.28, 90),
    ("43124", "Esophagectomy, total, without reconstruction", 30.41, 90),
    ("43130", "Diverticulectomy of hypopharynx (Zenker's)", 12.37, 90),
    ("43135", "Diverticulectomy of esophagus, thoracic", 18.55, 90),
    ("43180", "Esophagoscopy, with foreign body removal", 3.00, 0),
    ("43191", "Esophagoscopy, rigid, diagnostic", 2.09, 0),
    ("43197", "Flexible esophagoscopy, diagnostic", 1.90, 0),
    ("43200", "Esophagoscopy, flexible, diagnostic", 2.09, 0),
    ("43215", "Esophagoscopy with foreign body removal", 3.00, 0),
    ("43216", "Esophagoscopy with dilation, guide wire", 2.95, 0),
    ("43217", "Esophagoscopy with stent placement", 4.50, 0),
    ("43220", "Esophagoscopy with balloon dilation", 2.95, 0),
    ("43226", "Esophagoscopy with insertion of guide wire", 2.50, 0),
    ("43227", "Esophagoscopy with control of bleeding", 3.50, 0),
    ("43229", "Esophagoscopy with ablation of tumor", 3.80, 0),
    ("43233", "Esophagogastroduodenoscopy with balloon dilation 30mm+", 3.75, 0),
    ("43236", "EGD with directed submucosal injection", 2.72, 0),
    ("43237", "EGD with endoscopic ultrasound", 4.11, 0),
    ("43238", "EGD with transesophageal ultrasound-guided needle aspiration", 5.60, 0),
    ("43240", "EGD with dilation of gastric outlet for obstruction", 3.80, 0),
    ("43241", "EGD with transendoscopic tube placement", 3.42, 0),
    ("43242", "EGD with transendoscopic ultrasound of esophagus", 4.50, 0),
    ("43243", "EGD with injection of varices", 3.42, 0),
    ("43244", "EGD with band ligation of esophageal/gastric varices", 3.95, 0),
    ("43245", "EGD with dilation of stoma", 2.95, 0),
    ("43246", "EGD with gastrostomy tube placement", 3.42, 0),
    ("43247", "EGD with foreign body removal", 3.42, 0),
    ("43250", "EGD with removal of lesion by hot biopsy", 3.42, 0),
    ("43252", "EGD with optical endomicroscopy", 3.20, 0),
    ("43253", "EGD with injection for bleeding", 3.95, 0),
    ("43254", "EGD with endoscopic mucosal resection", 4.20, 0),
    ("43266", "EGD with stent placement (esophageal or gastric)", 4.50, 0),
]

for code, desc, wrvu, gp in gen_surg:
    fam = 'wound_repair' if code.startswith('12') or code.startswith('13') else \
          'debridement' if code.startswith('110') or code.startswith('16') else \
          'hernia_repair' if '495' in code or '496' in code or '497' in code or '498' in code or '49' in code[:4] and int(code) >= 49491 and int(code) <= 49656 else \
          'bowel_resection' if code.startswith('44') and int(code) >= 44100 else \
          'splenectomy' if code.startswith('381') else \
          'pancreas' if code.startswith('48') else \
          'liver' if code.startswith('47') else \
          'general_surgery'
    add(code, desc, "Surgery", "general", "general_surgery", wrvu, gp, family=fam,
        tier=2 if wrvu > 10 else 3)

print(f"After General Surgery expansion: {len(db)} codes (+{len(db)-start_count})")

# ============================================================================
# ENT DEEP EXPANSION — All sinus combinations
# ============================================================================

ent_codes = [
    # Sinus endoscopy - complete
    ("31231", "Nasal endoscopy, diagnostic", 1.10, 0),
    ("31233", "Nasal endoscopy, diagnostic with maxillary sinusoscopy", 1.59, 0),
    ("31235", "Nasal endoscopy, diagnostic with sphenoid sinusoscopy", 1.59, 0),
    ("31237", "Nasal endoscopy, surgical, with biopsy/polypectomy", 2.40, 0),
    ("31238", "Nasal endoscopy, surgical, with control of epistaxis", 3.20, 0),
    ("31239", "Nasal endoscopy, surgical, with dacryocystorhinostomy", 7.58, 90),
    ("31240", "Nasal endoscopy, surgical, with concha bullosa resection", 3.50, 0),
    ("31253", "Nasal endoscopy, with maxillary antrostomy with removal of tissue", 4.85, 0),
    ("31254", "Nasal endoscopy, with ethmoidectomy, partial", 5.85, 0),
    ("31255", "Nasal endoscopy, with ethmoidectomy, total", 7.11, 0),
    ("31256", "Nasal endoscopy, with maxillary antrostomy", 4.11, 0),
    ("31257", "Nasal endoscopy, with maxillary antrostomy with removal of tissue", 4.85, 0),
    ("31259", "Nasal endoscopy, with maxillary antrostomy with inferior meatal window", 4.85, 0),
    ("31267", "Nasal endoscopy, with maxillary antrostomy and ethmoidectomy", 6.85, 0),
    ("31276", "Nasal endoscopy, with frontal sinus exploration", 7.50, 0),
    ("31287", "Nasal endoscopy, with sphenoidotomy", 5.97, 0),
    ("31288", "Nasal endoscopy, with sphenoidotomy with removal of tissue", 6.74, 0),
    ("31290", "Nasal endoscopy, with repair of CSF leak, ethmoid", 12.50, 90),
    ("31291", "Nasal endoscopy, with repair of CSF leak, sphenoid", 12.50, 90),
    ("31292", "Nasal endoscopy, with decompression of orbit, medial wall", 10.50, 90),
    ("31293", "Nasal endoscopy, with decompression of orbit, inferior wall", 10.50, 90),
    ("31294", "Nasal endoscopy, with decompression of optic nerve", 14.00, 90),
    ("31295", "Nasal endoscopy, with dilation of maxillary sinus ostium, balloon", 3.50, 0),
    ("31296", "Nasal endoscopy, with dilation of frontal sinus ostium, balloon", 3.80, 0),
    ("31297", "Nasal endoscopy, with dilation of sphenoid sinus ostium, balloon", 3.50, 0),
    ("31298", "Nasal endoscopy, with dilation of frontal and sphenoid, balloon", 5.00, 0),
    ("31299", "Unlisted procedure, accessory sinuses", 0.00, 0),
    # Septoplasty / Turbinate
    ("30520", "Septoplasty", 6.29, 90),
    ("30130", "Excision inferior turbinate, partial", 3.60, 90),
    ("30140", "Submucous resection of turbinate", 3.60, 90),
    ("30801", "Cautery/ablation of inferior turbinate, superficial", 1.30, 0),
    ("30802", "Cautery/ablation of inferior turbinate, intramural", 1.90, 0),
    ("30901", "Control of nosebleed, anterior, simple", 0.72, 0),
    ("30903", "Control of nosebleed, anterior, complex", 1.44, 0),
    ("30905", "Control of nosebleed, posterior, initial", 2.43, 0),
    ("30906", "Control of nosebleed, posterior, subsequent", 2.43, 0),
    # Tonsils/Adenoids - expanded
    ("42820", "Tonsillectomy and adenoidectomy, under 12", 3.96, 90),
    ("42821", "Tonsillectomy and adenoidectomy, 12+", 4.55, 90),
    ("42825", "Tonsillectomy, primary or secondary, under 12", 3.67, 90),
    ("42826", "Tonsillectomy, primary or secondary, 12+", 4.22, 90),
    ("42830", "Adenoidectomy, primary, under 12", 2.58, 90),
    ("42831", "Adenoidectomy, primary, 12+", 3.07, 90),
    ("42835", "Adenoidectomy, secondary, under 12", 3.07, 90),
    ("42836", "Adenoidectomy, secondary, 12+", 3.68, 90),
    # Ear - expanded
    ("69420", "Myringotomy (tympanic membrane incision)", 1.22, 10),
    ("69421", "Myringotomy with aspiration", 1.38, 10),
    ("69433", "Tympanostomy, under local anesthesia", 1.98, 10),
    ("69436", "Tympanostomy, requiring general anesthesia", 2.72, 10),
    ("69540", "Excision of aural polyp", 2.12, 90),
    ("69601", "Mastoidectomy, complete", 12.70, 90),
    ("69602", "Mastoidectomy, complete, with radical", 14.50, 90),
    ("69603", "Mastoidectomy, complete, with canal wall down", 15.20, 90),
    ("69604", "Mastoidectomy, complete, with obliteration", 12.70, 90),
    ("69605", "Mastoidectomy, complete, modified radical", 14.00, 90),
    ("69610", "Tympanic membrane repair (myringoplasty)", 5.53, 90),
    ("69620", "Myringoplasty (tympanoplasty without mastoidectomy)", 8.30, 90),
    ("69631", "Tympanoplasty without mastoidectomy, without ossicular chain reconstruction", 9.38, 90),
    ("69632", "Tympanoplasty without mastoidectomy, with ossicular chain reconstruction", 11.56, 90),
    ("69633", "Tympanoplasty without mastoidectomy, with ossicular chain reconstruction and synthetic prosthesis", 12.47, 90),
    ("69635", "Tympanoplasty with mastoidectomy, without ossicular chain reconstruction", 13.55, 90),
    ("69636", "Tympanoplasty with mastoidectomy, with ossicular chain reconstruction", 15.83, 90),
    ("69637", "Tympanoplasty with mastoidectomy, with ossicular chain reconstruction and prosthesis", 16.67, 90),
    ("69641", "Tympanoplasty with mastoidectomy, atticotomy", 14.22, 90),
    ("69642", "Tympanoplasty with mastoidectomy, canal wall down", 15.83, 90),
    ("69643", "Tympanoplasty with mastoidectomy, canal wall down, with ossicular reconstruction", 17.55, 90),
    ("69644", "Tympanoplasty with mastoidectomy, radical", 16.67, 90),
    ("69645", "Tympanoplasty with mastoidectomy, radical, with tympanoplasty", 18.38, 90),
    ("69646", "Tympanoplasty with mastoidectomy, 2nd stage", 12.53, 90),
    # Larynx/Pharynx
    ("31510", "Laryngoscopy, indirect, with biopsy", 1.00, 0),
    ("31520", "Laryngoscopy, diagnostic, with or without tracheoscopy", 1.58, 0),
    ("31525", "Laryngoscopy, diagnostic, with biopsy", 2.10, 0),
    ("31526", "Laryngoscopy, diagnostic, with operating microscope", 2.33, 0),
    ("31528", "Laryngoscopy, with dilation", 2.60, 0),
    ("31529", "Laryngoscopy, with dilation, subsequent", 2.60, 0),
    ("31530", "Laryngoscopy, direct, with foreign body removal", 2.93, 0),
    ("31531", "Laryngoscopy, direct, with biopsy", 2.93, 0),
    ("31535", "Laryngoscopy, direct, with operating microscope, diagnostic", 2.93, 0),
    ("31536", "Laryngoscopy, direct, with biopsy, with operating microscope", 3.42, 0),
    ("31540", "Laryngoscopy, direct, with excision of tumor/stripping of cords", 3.84, 0),
    ("31541", "Laryngoscopy, direct, with excision of tumor/stripping of cords, with operating microscope", 4.20, 0),
    ("31545", "Laryngoscopy, direct, with injection into vocal cord", 2.33, 0),
    ("31546", "Laryngoscopy, direct, with injection into vocal cord, bilateral", 2.93, 0),
    ("31560", "Laryngoscopy, direct, with arytenoidectomy", 5.00, 90),
    ("31571", "Laryngoscopy, direct, with injection of therapeutic substance", 2.33, 0),
    ("31575", "Laryngoscopy, flexible, diagnostic", 1.10, 0),
    ("31576", "Laryngoscopy, flexible, with biopsy", 1.60, 0),
    ("31577", "Laryngoscopy, flexible, with removal of foreign body", 2.50, 0),
    ("31578", "Laryngoscopy, flexible, with stroboscopy", 1.50, 0),
    ("31579", "Laryngoscopy, flexible, with stent placement", 3.50, 0),
    # Tracheostomy
    ("31600", "Tracheostomy, planned", 5.58, 90),
    ("31601", "Tracheostomy, under 2 years", 6.74, 90),
    ("31603", "Tracheostomy, emergency, transtracheal", 5.00, 0),
    ("31605", "Tracheostomy, emergency, cricothyrotomy", 4.20, 0),
    ("31610", "Tracheostomy, fenestration for speech prosthesis", 5.58, 90),
    ("31611", "Tracheostomy with construction of tracheoesophageal fistula", 5.00, 90),
    ("31612", "Tracheal stent placement", 3.50, 0),
    ("31613", "Tracheostomy revision", 3.42, 10),
    ("31614", "Tracheostomy revision with flap rotation", 5.00, 10),
    ("31615", "Tracheobronchoscopy through tracheostomy", 2.60, 0),
    # Neck surgery
    ("21550", "Biopsy, soft tissue of neck or thorax", 2.10, 0),
    ("21552", "Excision, tumor, soft tissue, neck, subfascial, <5 cm", 5.50, 90),
    ("21554", "Excision, tumor, soft tissue, neck, subfascial, 5+ cm", 8.00, 90),
    ("21556", "Excision, tumor, soft tissue, neck, deep, <5 cm", 8.50, 90),
    ("21557", "Excision, tumor, soft tissue, neck, deep, 5+ cm", 12.00, 90),
    ("21558", "Radical resection, tumor, soft tissue, neck", 17.00, 90),
    ("38700", "Suprahyoid lymphadenectomy", 8.00, 90),
    ("38720", "Cervical lymphadenectomy (modified radical neck dissection)", 15.50, 90),
    ("38724", "Cervical lymphadenectomy (radical neck dissection)", 20.00, 90),
    # Salivary glands
    ("42300", "Incision and drainage of parotid abscess", 3.50, 10),
    ("42305", "Incision and drainage of parotid abscess, complicated", 5.00, 10),
    ("42310", "Incision and drainage of submandibular abscess", 3.00, 10),
    ("42330", "Sialolithotomy (stone removal), submandibular", 4.50, 90),
    ("42335", "Sialolithotomy (stone removal), parotid", 5.50, 90),
    ("42400", "Biopsy of salivary gland", 2.20, 0),
    ("42408", "Excision of sublingual gland", 5.00, 90),
    ("42410", "Excision of parotid tumor, lateral lobe without nerve dissection", 9.00, 90),
    ("42415", "Excision of parotid tumor, lateral lobe with nerve dissection", 12.50, 90),
    ("42420", "Excision of parotid tumor, total with nerve dissection", 17.50, 90),
    ("42425", "Excision of parotid tumor, total with sacrifice of facial nerve", 20.00, 90),
    ("42440", "Excision of submandibular gland", 7.50, 90),
    ("42450", "Excision of sublingual gland (ranula)", 6.00, 90),
]

for code, desc, wrvu, gp in ent_codes:
    fam = 'sinus_endoscopy' if code.startswith('312') or code.startswith('313') else \
          'ent_tonsil_adenoid' if code.startswith('428') else \
          'ent'
    add(code, desc, "Surgery", "ent", "ent", wrvu, gp, bilateral='bilateral' in desc.lower(),
        family=fam, tier=2 if wrvu > 8 else 3)

print(f"After ENT expansion: {len(db)} codes (+{len(db)-start_count})")

# ============================================================================
# SAVE CHECKPOINT
# ============================================================================

with open('cpt_database.json', 'w') as f:
    json.dump(db, f, indent=2)

# Count by category
cats = {}
specs = {}
for code, data in db.items():
    cat = data['category']
    spec = data['specialty']
    cats[cat] = cats.get(cat, 0) + 1
    specs[spec] = specs.get(spec, 0) + 1

print(f"\n=== PHASE 2 CHECKPOINT: {len(db)} CPT codes (+{len(db)-start_count} new) ===")
print("\nBy Category:")
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")
print("\nBy Specialty (top 10):")
for spec, count in sorted(specs.items(), key=lambda x: -x[1])[:10]:
    print(f"  {spec}: {count}")

print(f"\n✅ Saved cpt_database.json")
