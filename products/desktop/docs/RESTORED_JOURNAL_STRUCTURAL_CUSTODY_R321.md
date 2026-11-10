# Labs R321 — restored premium review-journal structural consistency (DRAFT / QD + founder HOLD)

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
Stacked on R320 draft PR #1840 at `fc19345071cd6b0e3284551067f249aeebc1f710`; **never main**. Source/tests/CI/docs only. No release, payment, entitlement, live site, or money-engine changes.

## Problem and remediation

The read-only R320 inspector authenticated neither the original vault nor reviewer decisions, intentionally, but also trusted `review_event_count` as a schema integer without checking whether the restored JSONL contained that number of records. Even with an internally consistent manifest SHA-256 and journal SHA-256, a malformed, newline-incomplete, duplicate-key, non-object, or count-mismatched journal could receive a passing *local consistency* receipt.

R321 closes this narrower correctness gap: during the existing second **descriptor-checked** journal read, materialize only the bounded JSONL bytes (16 MiB maximum), compare the same snapshot digest to the first pass and the manifest, then reject:

- Record count different from the manifest's `review_event_count` (including forged/rehashed manifest metadata).
- Missing final newline, empty records, malformed or non-object JSON, UTF-8 errors and embedded NUL.
- Duplicate JSON keys and non-finite JSON tokens, with strict integer `review_event_count` and 20,000-event cap.

The no-journal path and legitimate empty journal remain supported. Inspection stays local-first, bounded, read-only and private-path-safe with fixed `BundleHold` failure. The existing `-I` standalone CLI remains functional without a new import dependency. Existing receipt fields are preserved for compatibility.

**Trust boundary:** The plaintext manifest is forgeable by anyone with write access. This is structural consistency only, **not** AES-GCM source authentication, review-event SHA-chain authentication, reviewer identity, payment approval, compliance determination, Windows release authorization or protection against a privileged concurrent filesystem writer. The premium authenticated restore performs full product/case/journal-chain checks; independent human review and QD/founder approval are still required.

## Exact reproducible local evidence — November 9, 2026 PST

Tested on local Linux CPython with synthetic files only. The R320 source and original 22-test module were reconstructed byte-for-byte from the actual parent Git blobs; R321 edits and new tests match committed blob hashes.

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_restored*py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_restored*py'
python -m py_compile products/desktop/scripts/verify_restored_bundle_r320.py products/desktop/tests/test_restored_journal_structure_r321.py products/desktop/tests/test_restored_bundle_journal_integration_r321.py
```

**50/50 PASS normal and 50/50 PASS optimized = 100/100 focused method executions** (22 preserved R320 + 28 new R321 in each mode); compile PASS. New tests include 16 structural tests and 12 real-temporary-filesystem/isolated-CLI tests for both premium product names, no-write assertion, malformed rehashed JSONL, inaccurate count and fixed private failure. A reconstructed predecessor implementation produced **7 expected failures in the 12-test R321 integration module**, demonstrating the previously accepted inputs; this comparison was local, not a hosted CI run.

Commit identity checks (Git blob hashes):
- `products/desktop/scripts/verify_restored_bundle_r320.py`: `c63d3d83c375572b9cdb3764f01017d19fef7cc3`.
- `products/desktop/tests/test_restored_journal_structure_r321.py`: `fd2d871500f770fc9484eb076ae5adfae00dd04f`.
- `products/desktop/tests/test_restored_bundle_journal_integration_r321.py`: `d87666b8f80a2c44e2ef76aadf86f233e1ae53a8`.
- Original R320 regression file unchanged, blob `24e776f4f2b5c5eeadf98f29cc9acc9cd5bc1b3f`.

CI workflow adds normal and `-OO` R321 tests inside the existing R320 checks in both the Ubuntu source and Windows packaging jobs. These steps are committed but **not claimed executed on GitHub Actions**.

## Hold and next milestone

As of this sprint, the latest inspected R320 Actions [run #42753290270](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42753290270) failed before runner assignment: both jobs had zero steps, zero assigned runner IDs. The infrastructure cause is still unknown. To unblock: inspect repository Actions billing/spending limits, runner eligibility and workflow permissions; then rerun the draft branch and collect the 22 mandatory genuine AES-GCM tests and six native Windows x64 application evidence. Final binaries must stay private until scan, smoke, SHA-256, accessibility, protected premium access and independent QD/founder approval. No app is released by this change.
