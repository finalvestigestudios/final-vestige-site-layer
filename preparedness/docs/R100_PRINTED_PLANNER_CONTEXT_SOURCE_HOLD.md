# R100 Preparedness-only print assumption and source custody — PRIVATE HOLD

Issue [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136). Branch `review/preparedness-r100-planner-print-assumptions-hold-20261103`, directly based on immutable R99 commit `dcbe4a736fbf36b9a33741ea23df29634952a2f2`. No changes to original articles, CSS, tool, source readings, taxonomy, homepage, navigation, WordPress or CMS.

## Concrete finding (unapproved human review item)

The authored water planner offers “Print the result” and “Printing is the only way to keep a copy.” The existing **unchanged** print stylesheet contains `.pa-tool {display:none !important}`; all **eight** user-controlled fields live inside the hidden `#wp-form.pa-tool`. The dynamic results container `#wp-out.pa-tool-out` is a separate sibling outside that form, so it is not hidden by this exact selector. Thus the printed result **may lack the inputs/assumptions behind the calculated total** (household size, number of days, very-hot-weather selection, stored gallons, fill date, pets, pet allowance, and medical/other allowance). This is a document-interpretation risk candidate, not proof that the rendered print is wrong or that guidance is unsafe.

R100 creates a read-only `r100_printed_planner_context_custody.py` inspector. It structurally parses the *original* tool HTML; checks form and output placement, all eight labeled fields, source IDs and author-scoped `source_use`, private draft and pending safety states, print entrypoint and generated-output boundary, and requires the successful R99 CSS/source-print custody gate. It produces a stable SHA-256 sealed reviewer workorder and remains `HOLD`, `may_publish=false`, `NOT_REVIEWED` for human source/claim, qualified water/medical review, browser print, and independent QD. A change in form, citation, CSS, source reading, or review state fails closed until a new independent audit.

### Reviewer requirements, not automated approvals

1. Conduct **actual browser print preview**, with and without JavaScript, with customized heat/pets/medical inputs, across desktop/mobile and offline. Confirm whether computed totals and relevant assumptions, source citations, uncertainty caveats, and review record survive printing; do not rely on a CSS-only assertion.
2. Decide whether a read-only printable assumptions summary must be included beside the result. The current draft supplies no approved replacement or untested UI change. Do not “fix” by weakening `.pa-tool` print hiding without full accessibility/print QA.
3. Independently verify CDC / Ready.gov source identity, applicable version, original reading scope, and human link status. A surviving `{{cite:...}}` token does **not** establish claim support or currency.
4. Obtain qualified emergency-water/medical safety review and independent QD only through authorized human processes. Preserve 15 safety exceptions, 22 editorial decisions, 30 unresolved shared-source URL groups, historical-contributor drift and the five missing tool drafts. Mandatory 13-stage integrity remains unpassed.
5. Do not merge, publish, import WordPress drafts, touch homepage or site navigation, assert QD PASS, or mark unreviewed emergency guidance safe.

## Test and execution contract

`python -I -m unittest discover -s preparedness/tests -p test_r100_printed_planner_context_custody.py -v` exercises 55 in-memory isolated cases, including adversarial missing/duplicate/escaped form fields, label loss, source/citation changes, source-reading removal, premature publication state, dynamic-output ambiguity, and deterministic report sealing.

`python -I preparedness/tools/r100_printed_planner_context_custody.py --private-json-stdout` re-runs the inherited full R93–R99 **35 article + 1 actual tool** draft custody chain before recording its own workorder; it makes no filesystem changes. Also require `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, and complete `python -I -m unittest discover -s preparedness/tests -v`. Offline draft build is not a CMS action. Run against exact PR head, compare SHA pins, and keep mandatory integrity independent. No passing claim is made until actual hosted execution is inspected.

## Independent lane custody

Seven Claude contributor heads + separate Preparedness release-candidate pin must be checked against current Git references on each run. Independently reviewed [QA PR #157](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/157) and [synthetic-fixture PR #169](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/169) remain draft/unmerged. PR #169's *separate* duplicate-source test still writes `_dup_test.json` in a shared source-tree path. Neither PR is merged or treated as qualified safety approval. Homepage #49 and flagship #604 remain untouched.

**RELEASE STATUS: HOLD** — integrity/citation preservation ≠ factual correctness, actual browser print verification, qualified safety review or permission to publish.
