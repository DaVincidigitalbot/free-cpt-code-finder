#!/usr/bin/env python3
"""
FINAL HARDENING — Data fixes for modifier_rules.json and ncci_bundles.json
"""
import json

# Load
with open('modifier_rules.json') as f:
    rules = json.load(f)
with open('ncci_bundles.json') as f:
    bundles = json.load(f)

print("=== FIX 1: INHERENT PROCEDURE SUPPRESSION ===")

# Organ-specific procedures that inherently include exploratory laparotomy (49000)
# When you do a bowel resection, splenectomy, etc., you ALWAYS do an ex lap first.
# 49000 is NOT separately billable with these.
organ_specific_codes = [
    '38100',  # Splenectomy
    '38102',  # Splenectomy, partial
    '44120',  # Small bowel resection
    '44140',  # Colon resection
    '44141',  # Colon resection with colostomy
    '44143',  # Colectomy, partial
    '44144',  # Colectomy, partial with colostomy
    '44145',  # Colectomy, partial with ileostomy
    '44146',  # Colectomy with ileocolostomy
    '44147',  # Colectomy, partial with anastomosis
    '44150',  # Colectomy, total
    '44155',  # Colectomy, total with ileostomy
    '44160',  # Colectomy, partial with cecostomy
    '44604',  # Colon repair (suture)
    '44605',  # Colon repair, with colostomy
    '47350',  # Liver repair
    '47360',  # Liver repair, complex
    '47550',  # Liver biopsy
    '47562',  # Lap cholecystectomy
    '47563',  # Lap cholecystectomy with cholangiography
    '47564',  # Lap cholecystectomy with exploration
    '48140',  # Distal pancreatectomy
    '48145',  # Distal pancreatectomy with splenectomy
    '48150',  # Whipple
    '48153',  # Whipple, total
    '50220',  # Nephrectomy
    '50230',  # Nephrectomy, radical
    '50240',  # Nephrectomy, partial
    '50520',  # Ureter repair
    '51860',  # Bladder repair
    '51900',  # Bladder repair, suture
    '35221',  # Aortic repair
    '35081',  # Aortic repair, abdominal
    '39501',  # Diaphragm repair
    '39560',  # Diaphragm repair, neonatal
]

count = 0
for code in organ_specific_codes:
    if code in rules:
        inc = rules[code].get('inclusive_of', [])
        if '49000' not in inc:
            inc.append('49000')
            rules[code]['inclusive_of'] = inc
            count += 1

print(f"  Added 49000 to inclusive_of for {count} organ-specific procedures")

# Also: diagnostic laparoscopy (49320) included in all therapeutic lap procedures
lap_therapeutic = [
    '47562', '47563', '47564',  # Lap chole
    '44970',  # Lap appendectomy
    '44180',  # Lap adhesiolysis  
    '44202', '44204', '44205', '44206', '44207', '44208',  # Lap colectomy
    '58661', '58662',  # Lap gynecologic
    '49650', '49651', '49652', '49653',  # Lap hernia
]

count2 = 0
for code in lap_therapeutic:
    if code in rules:
        inc = rules[code].get('inclusive_of', [])
        if '49320' not in inc:
            inc.append('49320')
            rules[code]['inclusive_of'] = inc
            count2 += 1

print(f"  Added 49320 to inclusive_of for {count2} therapeutic laparoscopic procedures")

# Thoracotomy (32100) includes chest tube (32551)
# Already done, verify
if '32100' in rules:
    inc = rules['32100'].get('inclusive_of', [])
    if '32551' not in inc:
        inc.append('32551')
        rules['32100']['inclusive_of'] = inc
        print("  Added 32551 to 32100 inclusive_of")

# Also add NCCI bundles for organ-specific procedures that include 49000
for code in organ_specific_codes:
    if code in bundles['bundles']:
        if '49000' not in bundles['bundles'][code].get('column2_codes', []):
            bundles['bundles'][code]['column2_codes'].append('49000')
    else:
        bundles['bundles'][code] = {
            "column2_codes": ["49000"],
            "description": f"{code} includes exploratory laparotomy",
            "modifier59_allowed": False,
            "reason": "Exploratory laparotomy is inherent to organ-specific abdominal surgery"
        }

print(f"  Updated NCCI bundles for organ-specific procedures")
print(f"  Total bundles now: {len(bundles['bundles'])}")

print()
print("=== FIX 2: CODE FAMILY DATA FOR MPPR ===")

# Add code_family field to rules for MPPR differentiation
code_families = {
    'wound_repair': ['12001','12002','12004','12005','12006','12007','12011','12013','12014','12015','12016','12017','12018','12020','12021','12031','12032','12034','12035','12036','12037','12041','12042','12044','12045','12046','12047','12051','12052','12053','12054','12055','12056','12057','13100','13101','13120','13121','13131','13132','13133','13151','13152','13153','13160'],
    'bowel_resection': ['44120','44121','44125','44126','44127','44128','44130','44140','44141','44143','44144','44145','44146','44147','44150','44155','44160','44202','44204','44205','44206','44207','44208'],
    'hernia_repair': ['49505','49507','49520','49521','49525','49540','49550','49553','49555','49557','49560','49561','49565','49566','49568','49570','49572','49580','49582','49585','49587','49590','49593','49595','49596','49600','49605','49606','49610','49611'],
    'sinus_endoscopy': ['31231','31233','31235','31237','31238','31239','31240','31253','31254','31255','31256','31257','31259','31267','31276','31287','31288','31290','31291','31292','31293','31294','31295','31296','31297','31298','31299'],
    'cardiac_cabg': ['33510','33511','33512','33513','33514','33516','33517','33518','33519','33521','33522','33523','33530','33533','33534','33535','33536'],
    'cardiac_valve': ['33361','33362','33363','33364','33365','33366','33400','33401','33403','33404','33405','33406','33410','33411','33412','33413','33414','33415','33416','33417','33418','33420','33422','33425','33426','33427','33430'],
    'vascular_open': ['35001','35002','35005','35011','35013','35021','35022','35045','35081','35082','35091','35092','35102','35103','35111','35112','35121','35122','35131','35132','35141','35142','35151','35152','35161','35162','35180','35182','35184','35188','35189','35190','35201','35206','35207','35211','35216','35221','35226','35231','35236','35241','35246','35251','35256','35261','35266','35271','35276','35281','35286'],
    'critical_care': ['99291','99292'],
    'ent_tonsil_adenoid': ['42820','42821','42825','42826','42830','42831','42835','42836'],
    'fasciotomy': ['27600','27601','27602','27603','27604','27605','27606','27607'],
    'component_separation': ['15734','15736','15738'],
    'debridement': ['11042','11043','11044','11045','11046','11047'],
    'exploratory': ['49000','49002','49010','49020'],
    'splenectomy': ['38100','38101','38102','38115','38120'],
    'pancreas': ['48140','48145','48146','48148','48150','48152','48153','48154','48155'],
    'liver': ['47100','47120','47122','47125','47130','47133','47135','47140','47141','47350','47360','47361','47362','47370','47371','47379','47380','47381','47382'],
    'kidney': ['50220','50225','50230','50234','50236','50240','50280','50290'],
}

family_count = 0
for family_name, codes in code_families.items():
    for code in codes:
        if code in rules:
            rules[code]['code_family'] = family_name
            family_count += 1

print(f"  Assigned code_family to {family_count} CPT codes across {len(code_families)} families")

print()
print("=== SAVING ===")
with open('modifier_rules.json', 'w') as f:
    json.dump(rules, f, indent=2)
with open('ncci_bundles.json', 'w') as f:
    json.dump(bundles, f, indent=2)

print("  modifier_rules.json saved")
print("  ncci_bundles.json saved")
print(f"  Total CPT codes: {len(rules)}")
print(f"  Total NCCI bundles: {len(bundles['bundles'])}")
print("  Done.")
