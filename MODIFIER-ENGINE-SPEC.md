# Modifier Intelligence Engine — Build Specification

## OBJECTIVE
Build a rules-based modifier intelligence engine for FreeCPTCodeFinder.com that automatically determines and assigns surgical modifiers when cases are built. This replaces the current manual dropdown approach.

## ARCHITECTURE

### 1. Create `modifier_engine.js` (new file)
A standalone JavaScript module containing all modifier logic. Must be importable by `index.html`.

### 2. Create `modifier_rules.json` (new data file)  
CPT code metadata for modifier decisions. Structure per code:
```json
{
  "49505": {
    "mod51_exempt": false,
    "addon_code": false,
    "bilateral_eligible": true,
    "laterality_applicable": true,
    "bilateral_method": "modifier_50",
    "global_period": 90,
    "assistant_allowed": true,
    "cosurgeon_eligible": true,
    "inherently_bilateral": false,
    "distinct_procedure_class": "inguinal_hernia",
    "bundled_with": ["49650"],
    "unbundlable_with_59": ["49650"],
    "category": "hernia"
  }
}
```

### 3. Create `ncci_bundles.json` (new data file)
NCCI column 1/column 2 pairs for common surgical combinations:
```json
{
  "49505": {
    "bundled_codes": ["49568"],
    "unbundlable_codes": [{"code": "44120", "requires": "59", "reason": "Separate anatomic site"}]
  }
}
```

## CORE MODIFIER RULES

### Modifier -51 (Multiple Procedures)
- Auto-apply to secondary/subsequent procedures in same session
- NEVER apply to add-on codes (flagged in metadata)
- NEVER apply to modifier-51-exempt codes (flagged in metadata)
- Rank by wRVU: highest = primary (100%), all others = secondary (50% MPPR)
- Component separation (15734) is DISTINCT — ranks as primary reconstructive, not secondary

### Modifier -50 (Bilateral)
- Only apply when `bilateral_eligible: true` AND user confirms bilateral
- Check `bilateral_method`:
  - `"modifier_50"` → single line item with -50
  - `"rt_lt"` → two line items with -RT and -LT
  - `"units_2"` → single line item, units = 2
- NEVER apply to inherently bilateral codes
- Ask user: "Was this performed bilaterally?" ONLY when code is bilateral-eligible

### Modifier -59 / XE/XP/XS/XU (Distinct Procedure)
- ONLY suggest when two codes are in the same NCCI bundle
- Default: conservative (do NOT auto-apply)
- When bundle detected, prompt: "These procedures are typically bundled. Was this performed at a separate site/incision/encounter?"
- If user confirms → apply -59 (or suggest XE/XP/XS/XU with explanation)
- Show warning: "⚠️ Modifier -59 requires documentation of separate site, incision, or encounter"

### Modifiers -RT / -LT (Laterality)
- Apply when `laterality_applicable: true` AND procedure is unilateral
- Ask: "Which side?" → RT or LT
- If bilateral → switch to -50 logic instead

### Modifiers -80, -81, -82, -AS, -62, -66 (Surgeon Role)
- Only offer when context supports it
- Ask: "What was the surgeon's role in this case?"
  - Primary surgeon (default) → no role modifier
  - Assistant surgeon → -80
  - Minimum assistant → -81  
  - Assistant (no qualified resident) → -82
  - PA/NP assistant → -AS
  - Co-surgeon → -62
  - Team surgery → -66
- Calculate wRVU adjustment: -80 = 16%, -81 = 16%, -62 = 62.5%
- Check `assistant_allowed` flag — some codes don't allow assistants

### Modifiers -58, -76, -77, -78, -79 (Repeat/Return/Staged)
- Only trigger with structured prompts:
  - -76: "Is this a repeat of the same procedure by the same physician?"
  - -77: "Same procedure, different physician?"
  - -78: "Unplanned return to OR for complication during global period?"
  - -79: "Unrelated procedure during global period?"
  - -58: "Planned/staged procedure during global period?"
- Show these ONLY when user indicates return/staged context

### Modifiers -24, -25, -57 (E&M Related)
- Build architecture hooks now, don't fully implement yet
- -25: Significant, separately identifiable E/M on same day as procedure
- -57: Decision for surgery on same day as major procedure
- -24: Unrelated E/M during global period

### Modifier -22 (Increased Procedural Services)
- Never auto-apply
- Make available as manual override with warning: "Requires documentation of significantly increased complexity"

## UI INTEGRATION

### Post-Selection Modifier Panel
After user selects procedure(s), show a "Modifier Intelligence" panel:

```
┌─────────────────────────────────────────────┐
│ 🧠 Modifier Intelligence                    │
│                                             │
│ CPT 49505 — Inguinal hernia repair          │
│ ├─ Rank: PRIMARY (100% wRVU)               │
│ ├─ Modifiers: -RT (right side)             │
│ └─ Why: Laterality confirmed by user        │
│                                             │
│ CPT 44120 — Small bowel resection           │
│ ├─ Rank: SECONDARY (-51)                   │
│ ├─ Modifiers: -51 (multiple procedures)    │
│ ├─ Why: Lower wRVU, same session           │
│ └─ MPPR: 50% reduction applied             │
│                                             │
│ ⚠️ NCCI Alert: 44120 + 49505 may bundle    │
│    Documentation of separate site required  │
│                                             │
│ Total wRVU: 14.82 (adjusted)               │
└─────────────────────────────────────────────┘
```

### Clarification Questions Flow
Show INLINE, not as popups. Stack questions below the case summary:
- "Was this bilateral?" [Yes] [No]
- "Which side?" [Right] [Left]
- "Was an assistant surgeon present?" [Yes] [No]
- "Same session or return to OR?" [Same Session] [Return to OR]

### Override with Warning
User can manually change any modifier. If they override:
- Show yellow warning: "⚠️ You changed -51 to -59. Modifier -59 requires documentation of separate site/incision."
- Log the override in the case summary

### "Why This Modifier?" Tooltip
Each modifier assignment gets an ℹ️ icon that expands to show:
- Rule that triggered it
- CMS reference
- Whether it was auto-assigned or user-confirmed

## INTEGRATION POINTS

### 1. Case Builder (existing)
- After `addProcedureToCase()` runs, call `ModifierEngine.analyze(caseItems)`
- Engine returns modifier assignments for each code
- Update the case display with modifier badges

### 2. Decision Tree Output
- When user reaches a CPT code endpoint, check if modifier questions are needed
- Insert clarification questions before final "Add to Case"

### 3. Manual Search Results
- When user adds a code via search, run it through the engine
- Show "Additional info needed" if modifier decisions depend on context

### 4. wRVU Calculation
- Modifier engine must feed into the wRVU calculator
- -51 → apply MPPR (100%/50%/50%)
- -50 → 150% of base wRVU
- -80 → 16% of base
- -62 → 62.5% of base
- -22 → flag as manually adjusted, don't auto-calculate

## TEST SCENARIOS (must pass)

1. **Exploratory lap + splenectomy + wound VAC**: 49000 + 38100 + 97606. Rank by wRVU. -51 on secondary. No -59 needed.
2. **Bilateral inguinal hernia**: 49505-50. Single line, 150% wRVU. NOT two line items.
3. **Unilateral vs bilateral sinus**: 31256 alone = no modifier. Bilateral = 31256-50.
4. **Colon resection + stoma**: 44140 + 44320. Check NCCI bundle. -51 on secondary. May need -59 if truly separate.
5. **Return to OR for bleeding**: Same procedure = -76 or -78. Must ask structured questions.
6. **Staged second-look**: -58. Requires planned/staged confirmation.
7. **Co-surgeon case**: Both surgeons bill -62. 62.5% each.
8. **Assistant surgeon**: -80 on all codes. 16% wRVU.
9. **Bundled pair — NO modifier**: 49505 + 49568 (mesh). Mesh is add-on. No -51, no -59.
10. **Bundled pair — MAY get -59**: Two separate hernia repairs at different sites. Prompt for confirmation.

## FILES TO CREATE/MODIFY

1. **CREATE**: `/modifier_engine.js` — Core rules engine
2. **CREATE**: `/modifier_rules.json` — CPT code modifier metadata (cover all codes in rvu_database.json and decision tree)
3. **CREATE**: `/ncci_bundles.json` — Common bundling pairs
4. **MODIFY**: `/index.html` — Integrate engine into case builder UI, add modifier panel, add clarification questions
5. **CREATE**: `/modifier_tests.html` — Test page that runs all 10 scenarios and shows pass/fail

## CRITICAL GUARDRAILS
- NEVER auto-append modifiers just because multiple codes exist — check the rules first
- NEVER apply -50 to inherently bilateral codes
- NEVER apply -51 to add-on codes
- NEVER apply -59 without user confirmation
- Default to CONSERVATIVE — when uncertain, prompt user
- Mark documentation-dependent decisions as "⚠️ Requires documentation confirmation"
- Every modifier must have an explainable reason
