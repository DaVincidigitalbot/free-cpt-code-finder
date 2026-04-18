#!/usr/bin/env python3
import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path('/home/setup/Desktop/FreeCPTCodeFinder')
INDEX = ROOT / 'index.html'
TREE = ROOT / 'cpt_decision_tree.json'

GENERAL_SURGERY_FAMILIES = {
    'ventral_hernia': ['49591','49592','49593','49594','49595','49596','49613','49614','49615','49616','49617','49618','49652','49653','49654','49656','49657','15734'],
    'inguinal_hernia': ['49500','49505','49507','49520','49521','49525','49650'],
    'umbilical_hernia': ['49580','49582','49585','49587'],
    'pd_catheter': ['49324','49421','49422','49435','49436'],
    'soft_tissue_lesions': ['11400','11401','11402','11403','11404','11406','11420','11421','11422','11424','11426','21931','21932','22902','22903','24071','24073','27327','27328'],
    'drainage_minor': ['10060','10061','10140','49020','49084']
}

GUIDED_WORKFLOW_HINTS = {
    'ventral-hernia': ['Ventral / Incisional Hernia','15734','49653','49596'],
    'soft-tissue': ['Soft Tissue Lesions / Lipoma / Cyst','21931','11404','27327'],
    'pd-catheter': ['Peritoneal Dialysis Catheter','49421','49422']
}

DX_KEYS = ['const DX_BY_CPT={', 'function renderDxList(){']


def load_index_text():
    return INDEX.read_text(encoding='utf-8', errors='ignore')


def load_tree():
    return json.loads(TREE.read_text(encoding='utf-8'))


def extract_spec_codes(index_text):
    m = re.search(r'const SPECS=\{(.*?)\n\};', index_text, re.S)
    if not m:
        return set()
    return set(re.findall(r'\["(\d{5})"', m.group(1)))


def extract_dx_codes(index_text):
    m = re.search(r'const DX_BY_CPT=\{(.*?)\n\};', index_text, re.S)
    if not m:
        return set()
    return set(re.findall(r"'?(\d{5})'?:", m.group(1)))


def extract_tree_codes(tree):
    codes = set()
    cats = tree.get('categories', [])
    for cat in cats:
        payload = json.dumps(cat)
        codes.update(re.findall(r'"cpt_code"\s*:\s*"(\d{5})"', payload))
    return codes


def audit_families(spec_codes, tree_codes, dx_codes):
    findings = []
    for family, codes in GENERAL_SURGERY_FAMILIES.items():
        missing_specs = [c for c in codes if c not in spec_codes]
        missing_tree = [c for c in codes if c not in tree_codes]
        missing_dx = [c for c in codes if c not in dx_codes]
        findings.append({
            'family': family,
            'missing_from_specs': missing_specs,
            'missing_from_decision_tree': missing_tree,
            'missing_from_dx_map': missing_dx,
        })
    return findings


def audit_guided_workflows(index_text):
    findings = []
    for workflow, hints in GUIDED_WORKFLOW_HINTS.items():
        missing = [h for h in hints if h not in index_text]
        findings.append({
            'workflow': workflow,
            'present': not missing,
            'missing_markers': missing,
        })
    return findings


def summarize(findings, guided):
    lines = []
    lines.append('# FreeCPT Workflow Auditor Report')
    lines.append('')
    lines.append('## Family coverage')
    for f in findings:
        lines.append(f"- {f['family']}")
        lines.append(f"  - missing from specs: {', '.join(f['missing_from_specs']) if f['missing_from_specs'] else 'none'}")
        lines.append(f"  - missing from decision tree: {', '.join(f['missing_from_decision_tree']) if f['missing_from_decision_tree'] else 'none'}")
        lines.append(f"  - missing from dx map: {', '.join(f['missing_from_dx_map']) if f['missing_from_dx_map'] else 'none'}")
    lines.append('')
    lines.append('## Guided workflow checks')
    for g in guided:
        lines.append(f"- {g['workflow']}: {'OK' if g['present'] else 'MISSING'}")
        if g['missing_markers']:
            lines.append(f"  - missing markers: {', '.join(g['missing_markers'])}")
    return '\n'.join(lines) + '\n'


def main():
    index_text = load_index_text()
    tree = load_tree()
    spec_codes = extract_spec_codes(index_text)
    dx_codes = extract_dx_codes(index_text)
    tree_codes = extract_tree_codes(tree)
    findings = audit_families(spec_codes, tree_codes, dx_codes)
    guided = audit_guided_workflows(index_text)
    out = summarize(findings, guided)
    report = ROOT / 'tools' / 'freecpt_workflow_audit_report.md'
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(out, encoding='utf-8')
    print(out)
    print(f'Report written to {report}')


if __name__ == '__main__':
    main()
