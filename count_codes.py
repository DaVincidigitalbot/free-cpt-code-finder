import json

d = json.load(open('/home/setup/Desktop/FreeCPTCodeFinder/icd10_database.json'))
print(f'Total codes: {len(d)}')
systems = {}
for v in d.values():
    s = v.get('system', 'unknown')
    systems[s] = systems.get(s, 0) + 1
for s, c in sorted(systems.items(), key=lambda x: -x[1]):
    print(f'  {s}: {c}')
