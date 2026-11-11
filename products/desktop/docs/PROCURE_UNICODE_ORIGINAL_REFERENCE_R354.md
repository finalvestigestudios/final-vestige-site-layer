# ProcureGuard R354 — Unicode original-document boundary custody

**2026-11-11 • engineering draft • Issue #73 • QD/founder release HOLD**

## Reproduced audit-evidence defect

The original credit/return reference comparison used `str.strip()`, which removes *Unicode* whitespace such as U+00A0 NO-BREAK SPACE, U+2007 FIGURE SPACE, U+202F NARROW NO-BREAK SPACE, and U+3000 IDEOGRAPHIC SPACE. For the same normalized candidate key, a source label `\u00a0INV1` could compare as the same *original* spelling as `INV1`, suppressing `normalized_credit_link_review` / `normalized_return_link_review`. This was an identity-evidence classification error, **not** permission to pay or a proven fraudulent document.

In addition, the actual CSV importer previously removed the same leading/trailing Unicode whitespace before the ProcureGuard review had a chance to compare original document spellings.

## Changes

- `fvs_suite/procurement_reference.py`: trim only the six ASCII boundary whitespace characters for the **original-spelling snapshot/comparison**; preserve non-ASCII boundary markers. Keep native text validation and existing ASCII case/edge whitespace behavior.
- `fvs_suite/engine.py`: preserve non-ASCII boundary whitespace only for imported `document_id` and `related_document` columns. All other imported fields retain their prior normalization.
- `tests/test_procurement_unicode_original_r354.py`: **20 source-level unit methods** with nine Unicode separators, both orientations, exact match controls, ASCII compatibility, native-int compatibility, source immutability, deterministic snapshots, and hostile subclass rejection.
- `tests/test_procurement_unicode_original_integration_r354.py`: **12 full-engine integration methods** covering credit/return review flags, unchanged exact totals, physical candidate source rows, and actual CSV import. These require the complete repository.
- `.github/workflows/desktop-build.yml`: mandatory Ubuntu and Windows R354 test commands for normal and `-OO` Python; Windows has explicit nonzero-exit guards.

## Evidence and limitations

- **Local isolated test harness** with GitHub-exact `procurement_reference.py` and GitHub-exact R354 unit-test contents; `fvs_suite.review.ascii_case_identity` dependency was replaced by a minimal contract-equivalent local stub, not the actual full module.
- **20/20 PASS** normal Python `-W error`; **20/20 PASS** Python `-OO -W error`; **40 focused unit executions**.
- Removing the R354 trim restriction in the same isolated harness reproduced **48 subtest failures in 20 test methods** (as reported by unittest). This is reproducible counterfactual evidence, not a full checkout test.
- Genuine `engine.table`, `review_line`, bundled-app operations, all 12 new full-engine integration tests, complete repository regressions, and native Windows x64 executables were **not locally executed**.
- The CSV fix intentionally affects **only document-related procurement fields**; no other application matching criteria, money math, source SHA256, or approval decisions are relaxed.
- CI is configured, but prior R353 GitHub Actions run [#43017331821](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43017331821) failed on Ubuntu and Windows with `runner_id=0`, no runner name, and zero recorded steps. Billing/runner availability is a **suspected**, not established, root cause.

## Exit requirements and highest-impact next action

Restore hosted runner execution by inspecting the **failed GitHub Actions check annotations and repository Actions billing/limits/runner eligibility**, then execute R354 full-engine tests and inherited R342–R353 plus genuine AES-GCM regression cases **on the exact PR head** on Ubuntu and Windows. Only afterward run signed/unsigned-is-clearly-labeled Windows 11 x64 candidate builds, six-launcher UI/accessibility smoke, SHA-256 and Defender evidence, protected premium entitlement distribution tests, independent QD, and founder release approval.

**HOLD**: No executable or premium file distribution; no WordPress changes; no production merge; no payment authorization or automatic compliance decision.
