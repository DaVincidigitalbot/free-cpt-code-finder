# MEMORY UPDATE CHECKLIST

Use this after every meaningful change.

## 1. Update recovery docs immediately
- Update `system_boot.md` if startup order, immediate priorities, or warnings changed
- Update `memory_master.md` if architecture, capabilities, priorities, risks, or major project state changed
- Update the relevant module memory file if the change affected a specific subsystem
- Update `decision_log.md` if a meaningful product or technical decision changed

## 2. Choose the right module file
- CPT / decision tree / search / add flow → `cpt_engine_memory.md`
- modifiers / NCCI / ranking / bilateral / global-period logic → `modifier_engine_memory.md`
- audit / defensibility / confidence / blocking / billing risk → `audit_defensibility_memory.md`
- ClinicalCaseLog product, subscription, admin, account state → `clinicalcaselog_memory.md`
- admin auth / RBAC / security / privilege changes → `admin_system_memory.md`

## 3. What to capture
- what changed
- why it changed
- current behavior now
- known risk or limitation introduced
- any recovery-critical warnings for future agents

## 4. Minimum standard
A fresh agent should be able to read:
1. `system_boot.md`
2. `memory_master.md`
3. relevant module memory
4. `decision_log.md`
and continue without chat history.

## 5. Commit discipline
- Commit memory updates with code changes when possible
- Do not leave major system changes undocumented in chat only
- Repo memory is source of truth for crash recovery

## 6. Trigger examples
Update memory when you:
- change ranking logic
- change modifier behavior
- change NCCI or validation rules
- change hernia / 15734 behavior
- change admin or subscription logic
- ship a new risk model or audit rule
- fix a major regression
- add profiling or performance infrastructure
- change product priorities

## 7. Anti-patterns
- do not rely on chat memory alone
- do not write vague summaries like "fixed stuff"
- do not let docs drift from live behavior
- do not skip decision logging for controversial billing logic
