# Surgical Specialty Cleanup Report

## Before / After Category Report
- Homepage categories before: 53
- Homepage categories after: 41
- Categories removed/consolidated/renamed: 16
- Database specialty/category records reassigned: 144

### Categories Removed / Consolidated
- Otolaryngology (ENT) -> Otolaryngology / ENT: 73 source rows, 73 unique added, 0 duplicates merged
- Otolaryngology (Ent) -> Otolaryngology / ENT: 4 source rows, 4 unique added, 0 duplicates merged
- Bowel Resection -> General Surgery: 9 source rows, 9 unique added, 0 duplicates merged
- Cabg -> Cardiothoracic Surgery: 4 source rows, 4 unique added, 0 duplicates merged
- Component Separation -> General Surgery: 1 source rows, 1 unique added, 0 duplicates merged
- Fasciotomy -> Orthopedic Surgery: 3 source rows, 3 unique added, 0 duplicates merged
- Kidney -> Urology: 1 source rows, 1 unique added, 0 duplicates merged
- Liver -> HPB Surgery: 9 source rows, 9 unique added, 0 duplicates merged
- Pancreas -> HPB Surgery: 3 source rows, 3 unique added, 0 duplicates merged
- Hernia Repair -> General Surgery: 7 source rows, 7 unique added, 0 duplicates merged
- Exploratory -> General Surgery: 2 source rows, 2 unique added, 0 duplicates merged
- Ent Tonsil Adenoid -> Otolaryngology / ENT: 8 source rows, 8 unique added, 0 duplicates merged
- Debridement -> General Surgery: 6 source rows, 6 unique added, 0 duplicates merged
- Sinus Endoscopy -> Otolaryngology / ENT: 11 source rows, 11 unique added, 0 duplicates merged
- Splenectomy -> General Surgery: 2 source rows, 2 unique added, 0 duplicates merged
- Pathology -> Pathology / Lab: 70 source rows, 70 unique added, 0 duplicates merged

### Categories Renamed
- Otolaryngology (ENT) + Otolaryngology (Ent) -> Otolaryngology / ENT
- Pathology -> Pathology / Lab

### Updated Specialty Counts
- General Surgery: 848 CPT rows
- Cardiothoracic Surgery: 43 CPT rows
- Orthopedic Surgery: 3 CPT rows
- Urology: 95 CPT rows
- HPB Surgery: 12 CPT rows
- Otolaryngology / ENT: 96 CPT rows
- Pathology / Lab: 70 CPT rows

## Moved CPT Codes By Category
### Otolaryngology (ENT) -> Otolaryngology / ENT
21550, 21552, 21554, 21556, 21557, 21558, 30801, 30802, 30901, 30903, 30905, 30906, 31233, 31235, 31238, 31239, 31240, 31290, 31291, 31292, 31293, 31294, 31295, 31296, 31297, 31298, 31299, 31520, 31528, 31529, 31530, 31531, 31540, 31546, 31560, 31571, 31575, 31576, 31577, 31578, 31579, 31605, 31611, 31612, 31614, 31615, 42300, 42305, 42310, 42330, 42335, 42400, 42408, 42410, 42425, 42440, 42450, 69420, 69421, 69540, 69601, 69602, 69603, 69604, 69605, 69610, 69620, 69641, 69642, 69643, 69644, 69645, 69646

### Otolaryngology (Ent) -> Otolaryngology / ENT
69210, 69433, 69436, 69501

### Bowel Resection -> General Surgery
44120, 44121, 44140, 44141, 44143, 44155, 44202, 44205, 44320

### Cabg -> Cardiothoracic Surgery
33533, 33534, 33535, 33536

### Component Separation -> General Surgery
15734

### Fasciotomy -> Orthopedic Surgery
27600, 27601, 27602

### Kidney -> Urology
51860

### Liver -> HPB Surgery
47100, 47120, 47125, 47130, 47350, 47360, 47362, 47370, 47382

### Pancreas -> HPB Surgery
48140, 48150, 48153

### Hernia Repair -> General Surgery
49505, 49507, 49520, 49525, 49593, 49595, 49596

### Exploratory -> General Surgery
49000, 49002

### Ent Tonsil Adenoid -> Otolaryngology / ENT
42820, 42821, 42825, 42826, 42830, 42831, 42835, 42836

### Debridement -> General Surgery
11042, 11043, 11044, 11045, 11046, 11047

### Sinus Endoscopy -> Otolaryngology / ENT
31231, 31237, 31253, 31254, 31256, 31257, 31259, 31267, 31276, 31287, 31288

### Splenectomy -> General Surgery
38100, 38101

### Pathology -> Pathology / Lab
80048, 80050, 80053, 80061, 80076, 81001, 81003, 82040, 82247, 82248, 82306, 82310, 82374, 82435, 82550, 82565, 82728, 82784, 82947, 83036, 83540, 83550, 83615, 84075, 84100, 84132, 84153, 84295, 84439, 84443, 84450, 84460, 84520, 85025, 85027, 85610, 85730, 86003, 86200, 86235, 86780, 86803, 86850, 86900, 86901, 87070, 87081, 87086, 87340, 87389, 87491, 87591, 88302, 88304, 88305, 88307, 88309, 88311, 88312, 88313, 88321, 88325, 88331, 88332, 88341, 88342, 88360, 88361, 88365, 88377

## Integrity Validation
- CPT database total records: 3875
- Bad standalone specialty values remaining: 0
- Missing code fields: 0
- Missing descriptions: 0
- Missing specialties: 0
- Search corpus validation: passed for colectomy, CABG, component separation, fasciotomy, nephrectomy, Whipple, hernia repair, exploratory laparotomy, tonsillectomy, debridement bone, sinus endoscopy, splenectomy, and basic metabolic panel.
- Case Builder smoke: CPT 44140 added successfully via staged page helper.

## Recommended Production Deployment Plan
1. Review staging branch and screenshot package.
2. Create rollback branch from current main.
3. Push staging/category-specialty-cleanup to main.
4. Wait for GitHub Pages propagation.
5. Re-run live smoke tests for category tree, moved-code search, and case builder.
