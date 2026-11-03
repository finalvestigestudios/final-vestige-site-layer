# R82 — Four-snapshot citation/source/safety-state drift (PRIVATE HOLD)

**Issue:** #136. **Exact parent:** R81 draft PR #697 at e803a7520cd0954c393d692d80bfb37113d4559f. **Separate RC:** PR #584 at ddb3528ba6494dada1fa1c3a142ce746e3a67706, untouched. **Scoped inventory:** seven original Claude contributors / 29 specifically contributor-authored article bodies and metadata / seven source fragments; this is NOT a claim of covering the full 35-article slate. R80 still independently holds 35 articles, six tools, 244 original readings, 2,173 citations, 2,359 source-origin edges, and 4,070 unabridged text blocks.

## Why this lift is necessary

A Git SHA difference alone does not explain which source readings, URLs, citation anchors, wording or safety metadata have changed. Five contributor branches have advanced beyond frozen R14. Apparently unchanged citations may accompany changed guidance. A repeated source ID or URL is not a substitute for evidence review. This new custody layer makes drift examinable while leaving all human approvals at zero.

The read-only tool at preparedness/tools/r82_four_snapshot_citation_custody.py uses the strict R81 manifest and Git SHA validation, then reconstructs complete versions from four historical states: **frozen contributor, historical integrated tree, current contributor, separate RC**. It preserves all 28 complete source fragment JSON snapshots and all 116 complete article HTML + 116 metadata snapshots, with exact bytes represented as UTF-8 strings, digest, citation-token sequence, byte offsets, line positions and all distinct source-origin candidates within each snapshot. Historical source records and actual RC source readings remain separate; zero URL or ID aliasing.

A deterministic crosswalk classifies source IDs added/removed, literal URL/record changes, citations added/removed/reordered and consequential **wording changed without citation sequence changing** for mandatory human review. Source references outside the seven contributor fragments are explicitly **OUTSIDE_SEVEN_FRAGMENT_SCOPE**, not automatically invalid, because the larger R80 full-research corpus contains additional sources. The complete private report is hash sealed; the verifier independently reconstructs the source and article records and drift classifications to detect omissions or altered safety states. CSV reviewer queues escape spreadsheet formulas. SHA-256 detects accidental mutations; it is NOT authentication or substantive source validation.

RC fragments must retain human_link_check=false. Candidate article metadata may not declare publication or safety clearance. Every original source, claim, qualified-safety and QD approval remains NOT_REVIEWED or zero, and may_publish=false.

## Exact trusted checkout commands (private only, Python 3.12 + full Git history)

    python -I preparedness/tools/r82_four_snapshot_citation_custody.py
    python -I preparedness/tools/r82_four_snapshot_citation_custody.py --csv-stdout > /tmp/r82-PRIVATE-REVIEW.csv
    python -I preparedness/tools/r82_four_snapshot_citation_custody.py --json-stdout > /tmp/r82-PRIVATE-UNABRIDGED.json
    python -I -m unittest discover -s preparedness/tests -p test_r82_four_snapshot_citation_custody.py -v
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

Exported private ledgers are nonpublishable; delete after review. The workflow never uploads them, invokes CMS credentials or publishes content. Four ADD-only paths are enforced against the immutable R81 head, with native validation/build and full tests.

## Independent coordination and unresolved release gates

Independent QA PR #157 head 7d1ae6b8ef93d10cfb6810987672360885e9c1aa and fixture PR #169 head e9cd7766dac59d47ab467d8945269b9146c2aef5 remain draft/unmerged. Do not blindly cherry-pick older QA language over different RC wording; PR #169 still contains one shared-working-tree _dup_test.json fixture. Homepage PR #49 head 10495883299d53596992c26a8987f629b2904670 and flagship PR #604 head bdf01b4a3e13fd6179ae9e847c9d4429bbe16176 remain untouched. Separate RC #584 is untouched.

**Mandatory release HOLD:** the 13-stage release-integrity workflow has never passed. On exact R81 head, full 6,632 Python tests passed independently but took 194.4 seconds, exceeding the separate mandatory native_unit_suite 180-second gate. Five frozen contributor divergences remain unresolved. Human source URL/claim support, duplicate URL/alias and fallback decisions, 15 safety exceptions, 22 editorial decisions, qualified high-consequence emergency-guidance review, actual WordPress/browser/assistive QA, independent QD and founder authorization still required. NO medical-safety claim, QD PASS, merges, WordPress/CMS writes, public website edits or navigation deployment.
