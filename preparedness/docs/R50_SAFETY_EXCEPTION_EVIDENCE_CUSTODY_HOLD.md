# R50 — safety exception and original source-evidence custody (PRIVATE / HOLD)

Issue: #136. This documentation describes a machine-only reviewer worklist; it is **not** clinical, food-safety, water-treatment, legal, QD, or publication approval.

## Why the additional gate is needed

R48 generated a high-consequence safety exception register. Its core evidence has three overlapping but distinct inventories:

- **15 OPEN incidents**: SX-01 through SX-15 (5 HIGH, 7 MEDIUM, 3 LOW).
- **25 historically inaccessible cited source IDs** in Appendix B. This is a different, wider census than the 7 unavailable URLs among the 89-source *quantified-claim-only* sampling.
- **29 JSON candidate rows but only 28 evaluated candidates in Appendix A**: A01–A20 and B01–B08 are the 28; B09 is explicitly a placeholder with no source excerpt and no valid article line. Its machine status must never count as a reviewed fact or source-supported instruction.

R48's "found keywords" and R49's "found numeric tokens" are *not* verification that the same source supports the full claim, correct units, limits, qualification, local jurisdiction, current standards, or medical safety.

## Isolated changes

- New read-only tool: preparedness/tools/safety_exception_custody_gate.py.
- New synthetic and real-corpus tests: preparedness/tests/test_r50_safety_exception_custody.py.
- This documentation only. No edits to original 35 article bodies, water-planner files, taxonomy, citation/source registers, URLs, reviewer trust settings, WordPress, homepage, production CI, or navigation.
- The gate preserves all original individual source record variants, including separate contributor reading scopes for one URL. It never writes a review decision or alters inputs.
- Safety IDs, original severity levels, Appendix A identities, 25 blocked IDs/URLs, and 29 candidate-row identities are cross-checked; removal or silent downgrade is rejected.
- The output remains HOLD with no verified claims, qualified human reviews or approvals; it explicitly identifies B09 as a missing excerpt/placeholder and preserves all blocked sources as unresolved.
- Run: python -I preparedness/tools/safety_exception_custody_gate.py --format summary
- Run: python -I preparedness/tools/safety_exception_custody_gate.py --format json
- Native tests: python -I -m unittest discover -s preparedness/tests -p test_r50_safety_exception_custody.py -v
- Full mandatory: python -I preparedness/tools/validate.py ; python -I preparedness/tools/build.py ; python -I -m unittest discover -s preparedness/tests -v
- The full native suite is expected to include the new tests via discovery. A CI success demonstrates mechanical integrity only.

## Integration state / branch discipline

This branch is intentionally stacked on the **latest independently revised R48 head** (PR #483) because it contains the subsequent safety-register appendices. R49 PR #484 was created earlier on the *older* R48 head; R49 remains independently open and unchanged. Both branches must be reconciled without squashing away the later safety-register evidence or the R49 claim-context checks. No merges are authorized by this work. Verify exact PR heads before reviewing.

Independent PR #157 contains still-unmerged wording/taxonomy safety changes; PR #169 contains synthetic food source test isolation. Neither is automatically applied or treated as human safety signoff.

## Remaining real blockers

Qualified human review of each consequential exception, current direct-source/citation verification (0/206 human link checks), the 25 previously inaccessible sources via authorized route or human retrieval, reconciliation of 30 duplicate-URL groups and 43 fallback relationships, the 542 unexamined qualitative cited action blocks, Windows test-fixture portability, full rendered mobile/desktop/print QA, and independent exact-SHA QD approval.

Do not publish, create navigation, write to CMS, merge these draft branches, or assert that unreviewed emergency guidance is safe. Do not silently close SX incidents by asserting that keyword or number matching proves the advice correct.
