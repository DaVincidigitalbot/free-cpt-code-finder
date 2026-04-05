#!/usr/bin/env python3
"""Expand ICD-10 database to 5000+ codes. Generates codes from parts."""
import json, os, sys

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icd10_database.json")

# Load existing
with open(DB_PATH) as f:
    db = json.load(f)
print(f"Existing codes: {len(db)}")

# Import all parts
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from icd10_parts.part_infectious import get_codes as get_infectious
from icd10_parts.part_neoplasms import get_codes as get_neoplasms
from icd10_parts.part_blood import get_codes as get_blood
from icd10_parts.part_endocrine import get_codes as get_endocrine
from icd10_parts.part_mental import get_codes as get_mental
from icd10_parts.part_nervous import get_codes as get_nervous
from icd10_parts.part_eye_ear import get_codes as get_eye_ear
from icd10_parts.part_circulatory import get_codes as get_circulatory
from icd10_parts.part_respiratory import get_codes as get_respiratory
from icd10_parts.part_digestive import get_codes as get_digestive
from icd10_parts.part_skin import get_codes as get_skin
from icd10_parts.part_musculoskeletal import get_codes as get_musculoskeletal
from icd10_parts.part_genitourinary import get_codes as get_genitourinary
from icd10_parts.part_pregnancy import get_codes as get_pregnancy
from icd10_parts.part_perinatal_congenital import get_codes as get_perinatal_congenital
from icd10_parts.part_symptoms import get_codes as get_symptoms
from icd10_parts.part_injury import get_codes as get_injury
from icd10_parts.part_external import get_codes as get_external

all_parts = [
    ("Infectious", get_infectious),
    ("Neoplasms", get_neoplasms),
    ("Blood/Immune", get_blood),
    ("Endocrine", get_endocrine),
    ("Mental", get_mental),
    ("Nervous", get_nervous),
    ("Eye/Ear", get_eye_ear),
    ("Circulatory", get_circulatory),
    ("Respiratory", get_respiratory),
    ("Digestive", get_digestive),
    ("Skin", get_skin),
    ("Musculoskeletal", get_musculoskeletal),
    ("Genitourinary", get_genitourinary),
    ("Pregnancy", get_pregnancy),
    ("Perinatal/Congenital", get_perinatal_congenital),
    ("Symptoms", get_symptoms),
    ("Injury", get_injury),
    ("External/Factors", get_external),
]

added = 0
skipped = 0
for name, getter in all_parts:
    entries = getter()
    part_added = 0
    for entry in entries:
        code = entry["code"]
        if code not in db:
            db[code] = entry
            added += 1
            part_added += 1
        else:
            skipped += 1
    print(f"  {name}: {part_added} added ({len(entries)} total in part)")

print(f"\nAdded: {added}, Skipped (already existed): {skipped}")
print(f"Total codes now: {len(db)}")

# Save
with open(DB_PATH, 'w') as f:
    json.dump(db, f, indent=2)
print(f"Saved to {DB_PATH}")
