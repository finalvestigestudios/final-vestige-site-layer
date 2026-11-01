# R53 — High-consequence qualitative source-scope review work orders (HOLD)

**Issue:** #136. **Baseline:** R52 draft PR #503, exact head SHA 892c015277dfe44b6c4a1513d0705a9e2fa5b358.
**Scope:** new, private, read-only source/claim/safety custody; no article, source register, approved taxonomy, build, CI, homepage, CMS, navigation, WordPress, public route or release-authority change.

## Why this matters

R48 directly sampled numbers in 186 claim blocks, but that cannot verify the remaining **542 cited high-consequence visible action blocks** nor the **237 high-consequence blocks without a citation in their own visible block**.
R13 independently classified a total of **779** visible action blocks. An article containing many citations does not imply the particular action is supported by the particular cited source. A global source ID can select an unrelated contributor's reading note with a different scope.

R53 prepares *individual work orders* for those 779 heuristic flags, keyed to the original article HTML SHA-256, semantic block ordinal, R13 flag SHA-256 and every original citation ID occurrence (including repeated IDs). Each cited action's source record is selected through the original Library.source_for(article, sid), never the global register.
An order includes original contributor origin, source origin, URL, original reading-scope notes, source-use notes and SHA-256 of the original selected source record. It identifies base fallbacks, shared URL groups and historical machine-access failures as **pending human review**, not as proof of verified support or current source inaccessibility.

All 15 R48 open exceptions and 25 original historical machine source failures are included in the same deterministic work-order report. R53 rejects repinned input status, missing/reordered/deduplicated action rows, changed article bodies, manipulated citation counts, missing source-use notes, different source variants, falsified historical reviewer clearance and attempts to promote a heuristic triage to qualified safety/QD approval.

The native production census additionally pins **36 draft items, 224 original source variant records, 186 original URLs, 30 shared URL groups, 1,959 visible citations, 367 article-source relationships and 43 base fallback relationships**, alongside **779 flags = 542 cited + 237 uncited**, 15 OPEN safety incidents and 25 historical source-access failures.

## Execute after checking exact SHAs

From repository root, in an isolated checkout:

    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I preparedness/tools/r53_qualitative_source_scope_gate.py --summary
    python -I -m unittest discover -s preparedness/tests -v

The standalone R53 CLI emits deterministic, JSON-only, unapproved review work orders to stdout by default. The --summary flag excludes individual work orders.
No file is written by this new tool. Its real-corpus test re-derives R13 and R50 input reports from original archived source data. The repository's existing 13 mandatory private stages remain intact; do not change the hosted workflow to call this an official 14th mandatory stage.

## Independent safety/QA boundaries

- PR #157 (head 7d1ae6b8ef93d10cfb6810987672360885e9c1aa) contains separate editorial safety proposals including safer simulated power drills and medicine language. Do not silently graft old wording onto the newer original integration or claim it passed a qualified review.
- PR #169 (head e9cd7766dac59d47ab467d8945269b9146c2aef5) isolates synthetic food-source fixtures. It remains independent and unmerged.
- Homepage #49, flagship #254 and Gutenberg #414 remain independently owned; no change to their branches, homepage page 6 or live /focus/ subscriber flow.
- R52's 45-page/225-viewport rendered report is historic local-preview machine QA. Six documented open defects and all qualified human-review obligations remain open. R53 does not claim to fix them.
- The 25 historically inaccessible source IDs are not equivalent to the seven unavailable URLs among R48's numeric-source sampling. No present-day availability inference is made.
- R48 Appendix A has 28 evaluated AI-assisted cases; B09 remains an unevaluated placeholder, not a 29th reviewed instruction.
- The R13 classifier is heuristic. It may miss hazardous content, flag innocuous language and record a citation in a block without verifying source accuracy. Source mapping and hash custody do not constitute reviewer identity or human attestation.

## Remaining genuine release blockers

0/206 recorded independent human URL checks; all 30 shared-URL groups and 43 fallback relationships need human reconciliation; all 15 safety exceptions remain open; source-access and scope limitations need review; 542 cited and 237 uncited high-consequence heuristic flags require further contextual triage; qualified water/food/fire/infant/medical/evacuation guidance review, current citation verification, actual WordPress/Assembler rendered QA, independent accessibility/visual review and independent exact-final-SHA QD remain outstanding.

**Release state: HOLD.** Passing tests is NOT factual verification, medical or emergency safety clearance, publication eligibility or QD PASS. Do not merge, write WordPress, modify navigation or publicly publish anything under this R53 PR.
