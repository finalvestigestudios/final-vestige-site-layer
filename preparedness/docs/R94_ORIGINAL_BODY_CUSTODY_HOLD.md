# R94 — Unabridged original editorial reading-to-WordPress body custody (PRIVATE HOLD)

**Issue #136.** Parent: R93 draft PR #769, exact SHA `84eb6fa8f7de20d4e7737769d2052e55c722131a`. This is an **additive, isolated, unmerged draft**. No original article, source, citation, taxonomy, homepage, WordPress, navigation, or public-site edit.

## The failure mode

R93 verifies that the literal source IDs, citations, source titles, use scopes, URLs, warnings and rendered footnote anchors survive conversion into WordPress HTML. It does not independently compare **all the original author-written editorial passages** with the text that appears inside the final `.pa-body` after rendering. A change in a number, warning, paragraph, quotation or historical caveat could leave citations perfectly intact while materially changing the meaning of an instruction.

R94 adds a separate, independent **ordered editorial witness**. It parses the contributor's unabridged original body, removes only source-citation tokens, retains the author-visible text of cross-article link tokens, expands local inline JavaScript through its exact trusted relative file, and compares ordered block text and emphasis across the actual rendered WordPress `.pa-body`. The comparison includes headings, paragraphs, list items, blockquotes, table cells/captions and embedded strong/em emphasis. Literal scripts must also preserve byte-equivalent script content (SHA-256 witness); they are never executed as part of this check. The comparison is an explicit **transport/integrity claim only**: it is *not* proof that a sentence is supported by its citation, that an article is correct, or that any emergency advice is safe.

The R94 report records per-document block count, script count, a SHA-256 digest for the original ordered block witness, the exact script hashes, and the R93 cross-check of every actual rendered citation. All report rows are `HOLD`, `NOT_REVIEWED`, `may_publish=false`. The complete author text and source evidence remain in their original files; R94 never abridges or rewrites them.

## Inventory, collisions and parallel branches

R94 uses the **real file-pair inventory** from `build.Library`: the full 35-article slate and only tools that possess actual metadata/body draft files. **Six taxonomy tool plans do not equal six importable tool files**. As of the frozen R93 parent: 35 real articles + 1 real tool = 36 actual draft-file pairs; five tools are planned but lack files (`checklists`, `kit-builder`, `offline-reference`, `pantry-worksheet`, `reunification-plan`). The historical 41-document/2,173-citation reviewer packet set is a distinct evidence universe, never conflated with the real current 36-draft/1,959-citation HTML set.

R94 calls R93's independent author-scoped source/citation renderer gate for every actual WordPress draft. Existing 30 unresolved source-URL collision groups and separate source-ID variants remain unchanged and require manual resolution; no two matching URLs establish the same claim support. The R92 PR #766 historical/current citation-rank disagreement, including `family-communication-plan` occurrence 16, remains on its separate draft branch and is **not** automatically merged or represented as resolved. All seven Claude contributor SHA refs and the separate release candidate must remain pinned during CI diagnostics.

## Checks and stop rules

1. `python -I -m unittest discover -s preparedness/tests -p test_r94_body_custody.py -v` (42 separately discoverable synthetic corruption cases, 18 additional synthetic baseline/negative cases, and 1 native-library integration test).
2. `python -I preparedness/tools/r94_body_custody.py` (actual original-body/read-order/parser/script witness and R93 citation gate).
3. `python -I preparedness/tools/r94_body_custody.py --private-json-stdout` (never publish raw private evidence).
4. `python -I preparedness/tools/validate.py` (all warnings retained), then `python -I preparedness/tools/build.py` (offline DRAFT files only).
5. `python -I -m unittest discover -s preparedness/tests -v` (full Python suite).
6. Separately, the **mandatory 13-stage machine release-integrity workflow must pass on the final exact head**; this isolated diagnostic is not a substitute.

**Release verdict: HARD HOLD.** The mandatory release-integrity stage has repeatedly failed closed; five contributor historical-provenance deviations, 30 URL-collision groups, 15 safety exceptions, 22 editorial decisions, qualified emergency guidance review, human link/claim/source review, WordPress/browser accessibility QA, five missing tool draft files, founder release authorization, and independent QD PASS remain unfulfilled. Metadata safety labels are not qualified medical or food-safety determinations. The new gate does not authorize a CMS write, navigation change, merge, publication or claim of safety.

Independent QA PR #157 and fixture PR #169 were inspected. PR #169 at SHA `e9cd7766dac59d47ab467d8945269b9146c2aef5` still has a separate `test_register_fragments_cannot_duplicate_ids` test writing `sources/fragments/_dup_test.json` in a shared working tree; integration requires fixture isolation or an independent guaranteed exclusive checkout. Do **not** modify their PR branches here. Homepage PR #49 and flagship PR #604 are also out of scope.

## Diagnostics

Enter the final exact SHA, successful/failed run URL, numbered test results, native validator warning, preserved article count, block/script counts, R93 citation count, and complete remaining blockers in Issue #136 **only after actually executing them**. Do not describe a pending run as successful.
