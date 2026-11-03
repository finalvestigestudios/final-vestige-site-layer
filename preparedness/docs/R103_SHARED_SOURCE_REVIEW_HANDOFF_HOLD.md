# R103 — Private source/citation reviewer handoff (HOLD)

Issue: #136. This is an **offline reviewer aid**, not a WordPress page and not an approved evidence database. Its only permissible release state is **HOLD**. No merge, CMS write, publication, navigation mutation, independent QD PASS or clinical/emergency-safety certification.

## What was added

R102 conserves 30 literal shared-URL groups from all seven Claude contributors, with original origin-specific variants, source-reading notes, original body checksum and author-bound citation occurrences. R103 independently replays that workorder against a second fresh Library instance before exporting review formats. An altered report with a recomputed SHA-256 seal is rejected if its data no longer match the independently reconstructed corpus; a SHA-256 checksum alone is **not a signed attestation**.

The export is three views of the **same unapproved data**, never an automatic deduplication or approval: printable, static HTML containing 30 complete per-group workorders; one CSV row per original source variant; and one CSV row per cited occurrence of a shared URL. Original author-scoped source-use text, full original recorded variant and occurrence JSON, their SHA-256 digests, exact literal URL and their origin identities travel together. Historical documentation of an earlier approval in author metadata is NOT interpreted as R103 source verification, qualified medical review or independent QD approval.

HTML uses escaped text, no external links, no scripts or forms, a restrictive Content Security Policy and printable review prompts. CSV uses **quoted cells and spreadsheet formula-prefix neutralization**, including dangerous leading whitespace and Unicode invisibles, while preserving the unmodified original JSON in the source of truth. A leading apostrophe in exported CSV is an intentional display mitigation, not a change to the original research record.

Generate these **outside the repository**, e.g.:

```sh
python -I preparedness/tools/r103_collision_offline_reviewer_handoff.py --format summary-json
python -I preparedness/tools/r103_collision_offline_reviewer_handoff.py --format html > /tmp/r103-human-review-HOLD.html
python -I preparedness/tools/r103_collision_offline_reviewer_handoff.py --format variants-csv > /tmp/r103-source-variants-NOT-VERIFIED.csv
python -I preparedness/tools/r103_collision_offline_reviewer_handoff.py --format citations-csv > /tmp/r103-source-uses-NOT-VERIFIED.csv
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

Neither the engineering script nor its tests write into the shared source-fragment directory. No web fetching is performed. Output has no sign-off input fields to reduce the possibility of mistaken approval.

## Independent human review still required

For **each source variant in each of 30 groups**, open the real URL separately, record the date and exact edition/section/page actually read, check original and current claims separately, document contradictory or superseded regulator guidance, and retain the original author reading notes. For **each citation occurrence**, inspect the complete authored paragraph and surrounding qualifications in the original document, ensure the correct source variant and claim scope, and identify high-consequence food, water, health, medical, fire/CO or other instructions for qualified review. A nearby R102 excerpt only orients reviewers; it is not proof that a source supports the sentence. Same URL does not mean same source variant, applicability, or safety status.

## Integration / governance barriers

Preserve all 35 authored articles and the single currently complete tool. Five proposed tools have no buildable draft, and 41 historical reviewer packets are **not** 41 ready WordPress pages. Do not reconcile the five historical contributor-provenance discrepancies by silently changing crosswalk commit SHA values. The source URL groups remain human-**unreviewed**, as do the standing safety exceptions, editorial decisions, cross-browser print and accessibility checks. The independent QA PR #157 and synthetic-fixture PR #169 are unmerged and cannot be treated as passed. The mandatory 13-stage machine release integrity pipeline must pass independently of this additive diagnostic workflow.

## Mandatory validation

Only an exact-head hosted run executing the new tests, the original validator and build, and the complete regression suite may establish R103 engineering diagnostics. Test success does **not** approve source credibility, claim support, qualified medical/emergency safety, QD or publication. Read and report the mandatory integrity workflow separately. If any step fails, preserve the candidate as an unmerged draft and report the exact error in Issue #136.
