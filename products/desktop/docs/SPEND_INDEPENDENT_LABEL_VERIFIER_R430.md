# R430 — Restore independent SpendMap source-label evidence verification

**Issue:** #73. **Product:** SpendMap Lite (free standalone Windows x64 utility). **Status:** draft/source only, release unauthorized. No change to financial matching, original CSV bytes, Decimal totals, compliance decisions, pricing, licenses or premium delivery.

## Broken invariant

R428 changed the producer from trimmed per-category/month labels to exact original vendor-wide labels, including visible ASCII boundary whitespace. R429 then bounded displays to 32 labels / 8,192 report characters and added a SHA-256 commitment to the complete distinct original-label set. The independent spend_label_verify.expected_vendor_labels used by spend_evidence_verify.verify_membership still implemented the old per-category/month, trimmed, unbounded interpretation. It could incorrectly **reject legitimate exported reports** and did not independently check the R429 full-label digest. The historical review verifier also used Unicode-wide strip() for variant counts, unlike the producer's ASCII-only equivalence. No customer exploit or incident is claimed.

## Implemented source custody contract

- Independently recompute the original-label set across every month/category sharing one normalized vendor; assert the same evidence in every vendor bucket.
- Reproduce the R428 identity display: ASCII boundary spaces explicitly visible, controls and combining Unicode escaped, literal backslashes distinguishable, semicolons escaped.
- Independently reproduce the R429 budget (32 preview labels, 1,024 rendered-character per-label inline limit, 64 original-codepoint clipped prefix, 8,000-character preview assembly, 8,192-character final cap). Check both explicit PREVIEW_ONLY and LABEL_PREFIX_ONLY annotations and independently recompute the full domain-separated SHA-256 from sorted distinct original labels with eight-byte big-endian UTF-8 byte lengths.
- Preserve independent CSV formula-prefix defense and source-confidential exception handling.
- Change independent variant counting to ASCII boundary whitespace rules: NBSP/non-ASCII spaces remain distinct identities and require human review.
- Update stale R158/R358 tests to the R428/R429 exact vendor-wide source-label contract; preserve tamper and privacy checks.
- This remains report-display verification: actual source bytes, source SHA, row membership, money sums and final canonical CSV are checked by existing separate verifier code. A label digest is not a digital signature or approval.

## Exact artifacts and local execution

- products/desktop/fvs_suite/spend_label_verify.py — independent verifier; does not import report generator, audit_display or network modules.
- products/desktop/fvs_suite/spend_review_verify.py — ASCII-boundary historical variant count correction.
- products/desktop/tests/test_spend_vendor_label_independent_r430.py — **20 new offline unit methods** for Unicode, boundaries, formulas, multiple buckets, 32/33 labels, framed full digest, order invariance, 2,000 labels, clipping, and error privacy.
- products/desktop/tests/test_spend_vendor_verification_integration_r430.py — **9 committed, NOT locally executed real-engine integration methods** for actual CSV export and source-bound verification, 41 labels, long labels, digest tampering, immutability and NBSP counts.
- Updated products/desktop/tests/test_spend_visible_labels_r158.py and products/desktop/tests/test_spend_vendor_integration_r358.py.
- .github/workflows/desktop-source-evidence-r385.yml now invokes R430 and inherited R158/R358/R157 suites in normal and optimized Python on Ubuntu 24.04 + Windows latest.

**Actually executed locally:** isolated Linux Python with locally tested Git-blob-matched R430 verifier and unit tests: **20/20 PASS normal; 20/20 PASS Python -OO -W error; compilation PASS.** The fetched GitHub verifier blob SHA cbc3eae2451dc1e7378651ffe51e9f5161623648 and unit test blob SHA 44c12f2fa80ec80ed34084c2e506fff8eeadda87 match local Git object hashes. This was **not** the full repository, actual membership verifier end-to-end, a complete inherited suite or native Windows x64 test. The nine integration tests and updated inherited tests are committed but **not verified locally**.

## Release hold and next steps

1. Restore GitHub Actions hosted runner execution: inspect billing/spend limits, account runner eligibility and org/repo Actions policy. Prior exact-head runs failed with zero recorded job steps; root cause unconfirmed.
2. Run exact-head R430 source CI on both OSes, review all nine new integration tests plus inherited R158/R358/R157, and then full six-engine financial/cryptographic/entitlement tests.
3. Build six real Windows x64 artifacts, smoke test, perform Defender and keyboard/screen-reader checks, verify version/SHA-256 receipts and protected premium distribution.
4. Independent QD review and explicit founder approval **before merge, deployment, website update or publication**. release_authorized=false.

Strictly stacked on R429, not production main. No executables, site publication, unrestricted premium files, or customer-data uploads occurred.
