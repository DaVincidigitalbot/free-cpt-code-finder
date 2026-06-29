# CPT Search Selection UX Fix - Regression Report

Branch: `review/search-selection-ux-fix`  
Deployment: not deployed.

## Result

PASS.

## Implementation Summary

- Added explicit selected-CPT view state after autocomplete selection.
- Collapses the autocomplete dropdown immediately after selection.
- Removes unselected CPT rows from the Surgical Specialties viewport.
- Keeps the selected CPT and description visible in the search box.
- Displays a subtle `Viewing CPT #####` indicator above the selected procedure content.
- Renders only the selected procedure row with an `Add to active case` action.
- Preserves keyboard reopening with ArrowDown after a selected view.
- Preserves browser history with `pushState` on selection and `popstate` restoration.
- Preserves screen-reader semantics with combobox/listbox/option ARIA state.
- Improves synonym ranking so `tar` places CPT 15734 first.

## Validation Matrix

| Area | Validation | Result |
|---|---|---|
| CPT number search | `?q=44140 Colon resection` restores selected CPT view | PASS |
| Keyword search | `?q=lap chole` opens searchable result list | PASS |
| Synonym search | `?q=tar` ranks 15734 first | PASS |
| Desktop | Headless Chrome 1440px screenshots | PASS |
| Mobile | Headless Chrome 390px screenshots | PASS |
| Case Builder integration | Selected CPT row still calls existing `addAutocompleteResultToCase`; broad regression suite passed | PASS |
| Specialty filters | Editing search clears selected view and restores specialty filtering | PASS |
| Browser history | Selection uses `pushState`; `popstate` restores selected or unselected state | PASS |
| Keyboard navigation | Existing ArrowUp/ArrowDown/Enter behavior preserved; ArrowDown intentionally reopens selected search | PASS |
| Screen reader accessibility | Input uses `role="combobox"`, result list uses `role="listbox"`, results use `role="option"` | PASS |
| Layout/performance | Selected view renders one row instead of expanded specialty lists; search index logic unchanged except targeted alias score | PASS |

## Commands / Gates

| Gate | Command | Result |
|---|---|---|
| Inline JS syntax | Extract executable `index.html` scripts and parse with `new Function` | PASS |
| Global modifier unit tests | `node test_global_modifier_engine.js` | PASS |
| Specialty global modifier cases | `node validate_global_modifier_cases.js` | PASS |
| Full regression suite | `node kill_test_suite.js` | PASS, 54/54 |
| Validation evidence | `node validation_evidence.js` | PASS |
| Selected-state DOM | Headless Chrome dump verifies `Viewing CPT 44140`, selected view, closed dropdown | PASS |
| Search-state DOM | Headless Chrome dump verifies open dropdown for keyword search | PASS |
| Synonym DOM | Headless Chrome dump verifies `tar` first result is 15734 | PASS |

## Browser Evidence

- Before/search results desktop: `qa_artifacts/search_selection_ux_fix/01_before_search_results_desktop.png`
- After selected CPT desktop: `qa_artifacts/search_selection_ux_fix/02_after_selected_cpt_desktop.png`
- After selected CPT mobile: `qa_artifacts/search_selection_ux_fix/03_after_selected_cpt_mobile.png`
- Keyword search mobile: `qa_artifacts/search_selection_ux_fix/04_keyword_search_mobile.png`
- Browser recording: `qa_artifacts/search_selection_ux_fix/search-selection-ux-recording.mp4`

## Production Recommendation

Ready after review.

Reason: implementation and regression checks are clean, but production remains blocked until reviewed and approved.
