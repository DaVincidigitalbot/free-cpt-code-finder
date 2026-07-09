#!/usr/bin/env python3
"""Canonical musculoskeletal soft tissue tumor CPT source for FreeCPTCodeFinder.

Descriptors are matched to the CMS PFS RVU26C July 2026 CPT/HCPCS rows and
expanded into site-facing descriptor text so depth, size, and region do not
drift when JSON/search indexes are regenerated.
"""

SOURCE_NAME = "CMS PFS RVU26C July 2026 non-QPP"
SOURCE_FILE = "tmp/abos_sports_import/rvu26c/PPRRVU2026_Jul_nonQPP.csv"
SOURCE_URL = "https://www.cms.gov/files/zip/rvu26c.zip"

SOFT_TISSUE_TUMOR_CODES = {
    # Chest wall tumor excision family. These are not size/depth soft-tissue
    # threshold codes, but they are included in this audit because production
    # links chest-wall tumor work beside the soft-tissue tumor families.
    "21601": {"descriptor": "Excision of chest wall tumor including ribs", "region": "Chest wall", "depth": "chest wall including ribs", "size": "not size-based", "resection": "chest wall tumor excision"},
    "21602": {"descriptor": "Excision of chest wall tumor involving ribs, with plastic reconstruction; without mediastinal lymphadenectomy", "region": "Chest wall", "depth": "chest wall including ribs", "size": "not size-based", "resection": "chest wall tumor excision with reconstruction"},
    "21603": {"descriptor": "Excision of chest wall tumor involving ribs, with plastic reconstruction; with mediastinal lymphadenectomy", "region": "Chest wall", "depth": "chest wall including ribs", "size": "not size-based", "resection": "chest wall tumor excision with reconstruction and lymphadenectomy"},

    # Neck / anterior thorax
    "21550": {"descriptor": "Biopsy, soft tissue of neck or thorax", "region": "Neck / thorax", "depth": "biopsy", "size": "not size-based", "resection": "biopsy"},
    "21552": {"descriptor": "Excision, tumor, soft tissue of neck or anterior thorax, subcutaneous; 3 cm or greater", "region": "Neck / anterior thorax", "depth": "subcutaneous", "size": "3 cm or greater", "resection": "simple excision"},
    "21554": {"descriptor": "Excision, tumor, soft tissue of neck or anterior thorax, deep, subfascial, intramuscular; 5 cm or greater", "region": "Neck / anterior thorax", "depth": "deep subfascial or intramuscular", "size": "5 cm or greater", "resection": "simple excision"},
    "21555": {"descriptor": "Excision, tumor, soft tissue of neck or anterior thorax, subcutaneous; less than 3 cm", "region": "Neck / anterior thorax", "depth": "subcutaneous", "size": "less than 3 cm", "resection": "simple excision"},
    "21556": {"descriptor": "Excision, tumor, soft tissue of neck or anterior thorax, deep, subfascial, intramuscular; less than 5 cm", "region": "Neck / anterior thorax", "depth": "deep subfascial or intramuscular", "size": "less than 5 cm", "resection": "simple excision"},
    "21557": {"descriptor": "Radical resection of tumor, soft tissue of neck or anterior thorax; less than 5 cm", "region": "Neck / anterior thorax", "depth": "radical soft tissue resection", "size": "less than 5 cm", "resection": "radical resection"},
    "21558": {"descriptor": "Radical resection of tumor, soft tissue of neck or anterior thorax; 5 cm or greater", "region": "Neck / anterior thorax", "depth": "radical soft tissue resection", "size": "5 cm or greater", "resection": "radical resection"},

    # Back / flank
    "21920": {"descriptor": "Biopsy, soft tissue of back or flank; superficial", "region": "Back / flank", "depth": "superficial", "size": "not size-based", "resection": "biopsy"},
    "21925": {"descriptor": "Biopsy, soft tissue of back or flank; deep", "region": "Back / flank", "depth": "deep", "size": "not size-based", "resection": "biopsy"},
    "21930": {"descriptor": "Excision, tumor, soft tissue of back or flank, subcutaneous; less than 3 cm", "region": "Back / flank", "depth": "subcutaneous", "size": "less than 3 cm", "resection": "simple excision"},
    "21931": {"descriptor": "Excision, tumor, soft tissue of back or flank, subcutaneous; 3 cm or greater", "region": "Back / flank", "depth": "subcutaneous", "size": "3 cm or greater", "resection": "simple excision"},
    "21932": {"descriptor": "Excision, tumor, soft tissue of back or flank, deep, subfascial or intramuscular; less than 5 cm", "region": "Back / flank", "depth": "deep subfascial or intramuscular", "size": "less than 5 cm", "resection": "simple excision"},
    "21933": {"descriptor": "Excision, tumor, soft tissue of back or flank, deep, subfascial or intramuscular; 5 cm or greater", "region": "Back / flank", "depth": "deep subfascial or intramuscular", "size": "5 cm or greater", "resection": "simple excision"},
    "21935": {"descriptor": "Radical resection of tumor, soft tissue of back or flank; less than 5 cm", "region": "Back / flank", "depth": "radical soft tissue resection", "size": "less than 5 cm", "resection": "radical resection"},
    "21936": {"descriptor": "Radical resection of tumor, soft tissue of back or flank; 5 cm or greater", "region": "Back / flank", "depth": "radical soft tissue resection", "size": "5 cm or greater", "resection": "radical resection"},

    # Abdominal wall
    "22900": {"descriptor": "Excision, tumor, soft tissue of abdominal wall, deep, subfascial or intramuscular; less than 5 cm", "region": "Abdominal wall", "depth": "deep subfascial or intramuscular", "size": "less than 5 cm", "resection": "simple excision"},
    "22901": {"descriptor": "Excision, tumor, soft tissue of abdominal wall, deep, subfascial or intramuscular; 5 cm or greater", "region": "Abdominal wall", "depth": "deep subfascial or intramuscular", "size": "5 cm or greater", "resection": "simple excision"},
    "22902": {"descriptor": "Excision, tumor, soft tissue of abdominal wall, subcutaneous; less than 3 cm", "region": "Abdominal wall", "depth": "subcutaneous", "size": "less than 3 cm", "resection": "simple excision"},
    "22903": {"descriptor": "Excision, tumor, soft tissue of abdominal wall, subcutaneous; 3 cm or greater", "region": "Abdominal wall", "depth": "subcutaneous", "size": "3 cm or greater", "resection": "simple excision"},
    "22904": {"descriptor": "Radical resection of tumor, soft tissue of abdominal wall; less than 5 cm", "region": "Abdominal wall", "depth": "radical soft tissue resection", "size": "less than 5 cm", "resection": "radical resection"},
    "22905": {"descriptor": "Radical resection of tumor, soft tissue of abdominal wall; 5 cm or greater", "region": "Abdominal wall", "depth": "radical soft tissue resection", "size": "5 cm or greater", "resection": "radical resection"},

    # Shoulder / upper arm
    "23065": {"descriptor": "Biopsy, soft tissue of shoulder area; superficial", "region": "Shoulder", "depth": "superficial", "size": "not size-based", "resection": "biopsy"},
    "23066": {"descriptor": "Biopsy, soft tissue of shoulder area; deep", "region": "Shoulder", "depth": "deep", "size": "not size-based", "resection": "biopsy"},
    "23071": {"descriptor": "Excision, tumor, soft tissue of shoulder area, subcutaneous; 3 cm or greater", "region": "Shoulder", "depth": "subcutaneous", "size": "3 cm or greater", "resection": "simple excision"},
    "23073": {"descriptor": "Excision, tumor, soft tissue of shoulder area, deep, subfascial or intramuscular; 5 cm or greater", "region": "Shoulder", "depth": "deep subfascial or intramuscular", "size": "5 cm or greater", "resection": "simple excision"},
    "23075": {"descriptor": "Excision, tumor, soft tissue of shoulder area, subcutaneous; less than 3 cm", "region": "Shoulder", "depth": "subcutaneous", "size": "less than 3 cm", "resection": "simple excision"},
    "23076": {"descriptor": "Excision, tumor, soft tissue of shoulder area, deep, subfascial or intramuscular; less than 5 cm", "region": "Shoulder", "depth": "deep subfascial or intramuscular", "size": "less than 5 cm", "resection": "simple excision"},
    "23077": {"descriptor": "Radical resection of tumor, soft tissue of shoulder area; less than 5 cm", "region": "Shoulder", "depth": "radical soft tissue resection", "size": "less than 5 cm", "resection": "radical resection"},
    "23078": {"descriptor": "Radical resection of tumor, soft tissue of shoulder area; 5 cm or greater", "region": "Shoulder", "depth": "radical soft tissue resection", "size": "5 cm or greater", "resection": "radical resection"},

    # Upper arm / elbow
    "24065": {"descriptor": "Biopsy, soft tissue of upper arm or elbow area; superficial", "region": "Upper arm / elbow", "depth": "superficial", "size": "not size-based", "resection": "biopsy"},
    "24066": {"descriptor": "Biopsy, soft tissue of upper arm or elbow area; deep", "region": "Upper arm / elbow", "depth": "deep", "size": "not size-based", "resection": "biopsy"},
    "24071": {"descriptor": "Excision, tumor, soft tissue of upper arm or elbow area, subcutaneous; 3 cm or greater", "region": "Upper arm / elbow", "depth": "subcutaneous", "size": "3 cm or greater", "resection": "simple excision"},
    "24073": {"descriptor": "Excision, tumor, soft tissue of upper arm or elbow area, deep, subfascial or intramuscular; 5 cm or greater", "region": "Upper arm / elbow", "depth": "deep subfascial or intramuscular", "size": "5 cm or greater", "resection": "simple excision"},
    "24075": {"descriptor": "Excision, tumor, soft tissue of upper arm or elbow area, subcutaneous; less than 3 cm", "region": "Upper arm / elbow", "depth": "subcutaneous", "size": "less than 3 cm", "resection": "simple excision"},
    "24076": {"descriptor": "Excision, tumor, soft tissue of upper arm or elbow area, deep, subfascial or intramuscular; less than 5 cm", "region": "Upper arm / elbow", "depth": "deep subfascial or intramuscular", "size": "less than 5 cm", "resection": "simple excision"},
    "24077": {"descriptor": "Radical resection of tumor, soft tissue of upper arm or elbow area; less than 5 cm", "region": "Upper arm / elbow", "depth": "radical soft tissue resection", "size": "less than 5 cm", "resection": "radical resection"},
    "24079": {"descriptor": "Radical resection of tumor, soft tissue of upper arm or elbow area; 5 cm or greater", "region": "Upper arm / elbow", "depth": "radical soft tissue resection", "size": "5 cm or greater", "resection": "radical resection"},

    # Forearm / wrist
    "25065": {"descriptor": "Biopsy, soft tissue of forearm and/or wrist; superficial", "region": "Forearm / wrist", "depth": "superficial", "size": "not size-based", "resection": "biopsy"},
    "25066": {"descriptor": "Biopsy, soft tissue of forearm and/or wrist; deep", "region": "Forearm / wrist", "depth": "deep", "size": "not size-based", "resection": "biopsy"},
    "25071": {"descriptor": "Excision, tumor, soft tissue of forearm and/or wrist area, subcutaneous; 3 cm or greater", "region": "Forearm / wrist", "depth": "subcutaneous", "size": "3 cm or greater", "resection": "simple excision"},
    "25073": {"descriptor": "Excision, tumor, soft tissue of forearm and/or wrist area, deep, subfascial or intramuscular; 3 cm or greater", "region": "Forearm / wrist", "depth": "deep subfascial or intramuscular", "size": "3 cm or greater", "resection": "simple excision"},
    "25075": {"descriptor": "Excision, tumor, soft tissue of forearm and/or wrist area, subcutaneous; less than 3 cm", "region": "Forearm / wrist", "depth": "subcutaneous", "size": "less than 3 cm", "resection": "simple excision"},
    "25076": {"descriptor": "Excision, tumor, soft tissue of forearm and/or wrist area, deep, subfascial or intramuscular; less than 3 cm", "region": "Forearm / wrist", "depth": "deep subfascial or intramuscular", "size": "less than 3 cm", "resection": "simple excision"},
    "25077": {"descriptor": "Radical resection of tumor, soft tissue of forearm and/or wrist area; less than 3 cm", "region": "Forearm / wrist", "depth": "radical soft tissue resection", "size": "less than 3 cm", "resection": "radical resection"},
    "25078": {"descriptor": "Radical resection of tumor, soft tissue of forearm and/or wrist area; 3 cm or greater", "region": "Forearm / wrist", "depth": "radical soft tissue resection", "size": "3 cm or greater", "resection": "radical resection"},

    # Hand / finger
    "26111": {"descriptor": "Excision, tumor or vascular malformation, soft tissue of hand or finger, subcutaneous; 1.5 cm or greater", "region": "Hand / finger", "depth": "subcutaneous", "size": "1.5 cm or greater", "resection": "simple excision"},
    "26113": {"descriptor": "Excision, tumor or vascular malformation, soft tissue of hand or finger, deep, subfascial or intramuscular; 1.5 cm or greater", "region": "Hand / finger", "depth": "deep subfascial or intramuscular", "size": "1.5 cm or greater", "resection": "simple excision"},
    "26115": {"descriptor": "Excision, tumor or vascular malformation, soft tissue of hand or finger, subcutaneous; less than 1.5 cm", "region": "Hand / finger", "depth": "subcutaneous", "size": "less than 1.5 cm", "resection": "simple excision"},
    "26116": {"descriptor": "Excision, tumor or vascular malformation, soft tissue of hand or finger, deep, subfascial or intramuscular; less than 1.5 cm", "region": "Hand / finger", "depth": "deep subfascial or intramuscular", "size": "less than 1.5 cm", "resection": "simple excision"},
    "26117": {"descriptor": "Radical resection of tumor, soft tissue of hand or finger; less than 3 cm", "region": "Hand / finger", "depth": "radical soft tissue resection", "size": "less than 3 cm", "resection": "radical resection"},
    "26118": {"descriptor": "Radical resection of tumor, soft tissue of hand or finger; 3 cm or greater", "region": "Hand / finger", "depth": "radical soft tissue resection", "size": "3 cm or greater", "resection": "radical resection"},

    # Pelvis / hip
    "27040": {"descriptor": "Biopsy, soft tissue of pelvis and hip area; superficial", "region": "Pelvis / hip", "depth": "superficial", "size": "not size-based", "resection": "biopsy"},
    "27041": {"descriptor": "Biopsy, soft tissue of pelvis and hip area; deep", "region": "Pelvis / hip", "depth": "deep", "size": "not size-based", "resection": "biopsy"},
    "27043": {"descriptor": "Excision, tumor, soft tissue of pelvis and hip area, subcutaneous; 3 cm or greater", "region": "Pelvis / hip", "depth": "subcutaneous", "size": "3 cm or greater", "resection": "simple excision"},
    "27045": {"descriptor": "Excision, tumor, soft tissue of pelvis and hip area, deep, subfascial or intramuscular; 5 cm or greater", "region": "Pelvis / hip", "depth": "deep subfascial or intramuscular", "size": "5 cm or greater", "resection": "simple excision"},
    "27047": {"descriptor": "Excision, tumor, soft tissue of pelvis and hip area, subcutaneous; less than 3 cm", "region": "Pelvis / hip", "depth": "subcutaneous", "size": "less than 3 cm", "resection": "simple excision"},
    "27048": {"descriptor": "Excision, tumor, soft tissue of pelvis and hip area, deep, subfascial or intramuscular; less than 5 cm", "region": "Pelvis / hip", "depth": "deep subfascial or intramuscular", "size": "less than 5 cm", "resection": "simple excision"},
    "27049": {"descriptor": "Radical resection of tumor, soft tissue of pelvis and hip area; less than 5 cm", "region": "Pelvis / hip", "depth": "radical soft tissue resection", "size": "less than 5 cm", "resection": "radical resection"},
    "27059": {"descriptor": "Radical resection of tumor, soft tissue of pelvis and hip area; 5 cm or greater", "region": "Pelvis / hip", "depth": "radical soft tissue resection", "size": "5 cm or greater", "resection": "radical resection"},

    # Thigh / knee
    "27323": {"descriptor": "Biopsy, soft tissue of thigh or knee area; superficial", "region": "Thigh / knee", "depth": "superficial", "size": "not size-based", "resection": "biopsy"},
    "27324": {"descriptor": "Biopsy, soft tissue of thigh or knee area; deep", "region": "Thigh / knee", "depth": "deep", "size": "not size-based", "resection": "biopsy"},
    "27327": {"descriptor": "Excision, tumor, soft tissue of thigh or knee area, subcutaneous; less than 3 cm", "region": "Thigh / knee", "depth": "subcutaneous", "size": "less than 3 cm", "resection": "simple excision"},
    "27328": {"descriptor": "Excision, tumor, soft tissue of thigh or knee area, deep, subfascial or intramuscular; less than 5 cm", "region": "Thigh / knee", "depth": "deep subfascial or intramuscular", "size": "less than 5 cm", "resection": "simple excision"},
    "27329": {"descriptor": "Radical resection of tumor, soft tissue of thigh or knee area; less than 5 cm", "region": "Thigh / knee", "depth": "radical soft tissue resection", "size": "less than 5 cm", "resection": "radical resection"},
    "27337": {"descriptor": "Excision, tumor, soft tissue of thigh or knee area, subcutaneous; 3 cm or greater", "region": "Thigh / knee", "depth": "subcutaneous", "size": "3 cm or greater", "resection": "simple excision"},
    "27339": {"descriptor": "Excision, tumor, soft tissue of thigh or knee area, deep, subfascial or intramuscular; 5 cm or greater", "region": "Thigh / knee", "depth": "deep subfascial or intramuscular", "size": "5 cm or greater", "resection": "simple excision"},
    "27364": {"descriptor": "Radical resection of tumor, soft tissue of thigh or knee area; 5 cm or greater", "region": "Thigh / knee", "depth": "radical soft tissue resection", "size": "5 cm or greater", "resection": "radical resection"},

    # Leg / ankle
    "27613": {"descriptor": "Biopsy, soft tissue of leg or ankle area; superficial", "region": "Leg / ankle", "depth": "superficial", "size": "not size-based", "resection": "biopsy"},
    "27614": {"descriptor": "Biopsy, soft tissue of leg or ankle area; deep", "region": "Leg / ankle", "depth": "deep", "size": "not size-based", "resection": "biopsy"},
    "27615": {"descriptor": "Radical resection of tumor, soft tissue of leg or ankle area; less than 5 cm", "region": "Leg / ankle", "depth": "radical soft tissue resection", "size": "less than 5 cm", "resection": "radical resection"},
    "27616": {"descriptor": "Radical resection of tumor, soft tissue of leg or ankle area; 5 cm or greater", "region": "Leg / ankle", "depth": "radical soft tissue resection", "size": "5 cm or greater", "resection": "radical resection"},
    "27618": {"descriptor": "Excision, tumor, soft tissue of leg or ankle area, subcutaneous; less than 3 cm", "region": "Leg / ankle", "depth": "subcutaneous", "size": "less than 3 cm", "resection": "simple excision"},
    "27619": {"descriptor": "Excision, tumor, soft tissue of leg or ankle area, deep, subfascial or intramuscular; less than 5 cm", "region": "Leg / ankle", "depth": "deep subfascial or intramuscular", "size": "less than 5 cm", "resection": "simple excision"},
    "27632": {"descriptor": "Excision, tumor, soft tissue of leg or ankle area, subcutaneous; 3 cm or greater", "region": "Leg / ankle", "depth": "subcutaneous", "size": "3 cm or greater", "resection": "simple excision"},
    "27634": {"descriptor": "Excision, tumor, soft tissue of leg or ankle area, deep, subfascial or intramuscular; 5 cm or greater", "region": "Leg / ankle", "depth": "deep subfascial or intramuscular", "size": "5 cm or greater", "resection": "simple excision"},

    # Foot / toe
    "28039": {"descriptor": "Excision, tumor, soft tissue of foot or toe, subcutaneous; 1.5 cm or greater", "region": "Foot / toe", "depth": "subcutaneous", "size": "1.5 cm or greater", "resection": "simple excision"},
    "28041": {"descriptor": "Excision, tumor, soft tissue of foot or toe, deep, subfascial or intramuscular; 1.5 cm or greater", "region": "Foot / toe", "depth": "deep subfascial or intramuscular", "size": "1.5 cm or greater", "resection": "simple excision"},
    "28043": {"descriptor": "Excision, tumor, soft tissue of foot or toe, subcutaneous; less than 1.5 cm", "region": "Foot / toe", "depth": "subcutaneous", "size": "less than 1.5 cm", "resection": "simple excision"},
    "28045": {"descriptor": "Excision, tumor, soft tissue of foot or toe, deep, subfascial or intramuscular; less than 1.5 cm", "region": "Foot / toe", "depth": "deep subfascial or intramuscular", "size": "less than 1.5 cm", "resection": "simple excision"},
    "28046": {"descriptor": "Radical resection of tumor, soft tissue of foot or toe; less than 3 cm", "region": "Foot / toe", "depth": "radical soft tissue resection", "size": "less than 3 cm", "resection": "radical resection"},
    "28047": {"descriptor": "Radical resection of tumor, soft tissue of foot or toe; 3 cm or greater", "region": "Foot / toe", "depth": "radical soft tissue resection", "size": "3 cm or greater", "resection": "radical resection"},
}
