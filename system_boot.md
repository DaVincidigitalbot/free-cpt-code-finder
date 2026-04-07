# SYSTEM BOOT — Recovery First Read

Last updated: 2026-04-06
Read this first after crash/reset.

## What is this system?
FreeCPTCodeFinder is a live static surgical coding and billing intelligence app. It combines CPT discovery, ICD support, modifier logic, NCCI logic, case-level wRVU calculation, validation, and audit/defensibility guidance.

## What has been built?
- CPT decision tree and search workflows
- RVU calculator and case builder
- advanced modifier engine
- NCCI bundle detection and warnings
- validation/copy blocking system
- hernia + 15734 ranking and bilateral normalization logic
- audit/defensibility layer
- lightweight performance profiler
- production deployment on GitHub Pages

## Current priority
- persistent memory recovery system is now established in-repo
- preserve and improve FreeCPTCodeFinder as primary project
- continue hardening billing accuracy, defensibility, and performance

## What should be done next?
1. read `memory_master.md`
2. read task-relevant module files
3. inspect `git log --oneline -n 10`
4. verify current app behavior before changing core billing logic
5. update memory files immediately after meaningful work

## Immediate warnings
- `index.html` is large and regression-prone
- do not desync inline CPT data from `cpt_decision_tree.json`
- hernia + 15734 logic is deliberate and documentation-sensitive
- performance claims should come from profiler output, not assumptions

## If task involves...
- overall architecture/product state → `memory_master.md`
- ranking/modifier logic → `modifier_engine_memory.md`
- CPT/decision-tree/search behavior → `cpt_engine_memory.md`
- defensibility/risk guidance → `audit_defensibility_memory.md`
- product/admin/account state beyond FreeCPTCodeFinder → `clinicalcaselog_memory.md`, `admin_system_memory.md`
- why a direction was chosen → `decision_log.md`
