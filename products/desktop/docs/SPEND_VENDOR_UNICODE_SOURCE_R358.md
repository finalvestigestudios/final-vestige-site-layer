# Labs R358 — SpendMap Unicode original-vendor evidence integrity

**HOLD / DRAFT ONLY:** Issue #73. Stacked on R357 (PR #2066), not production main. No executable or premium distribution is authorized; independent QD review and founder approval are still required.

## Reproduced defect

SpendMap's normalized vendor matching key deliberately discards non-ASCII/format characters. The shared table importer and review.raw_values() each used Python's broad str.strip(), which removes original Unicode boundary characters such as U+00A0 NO-BREAK SPACE, U+2007 FIGURE SPACE and U+202F NARROW NO-BREAK SPACE. Consequently the distinct source cells ACME and an NBSP-prefixed ACME could both be treated as exactly the same original vendor label: no normalized_vendor_collision_review, variant count 1, and no visible evidence for reviewers, despite both rows contributing to one normalized bucket. This is an identity-custody problem, **not** a disagreement about the exact monetary total.

## Implementation

- engine.table() takes new optional preserve_spend_vendor_source=False. Only engine.spend_map() opts in. This preserves Unicode original vendor boundary characters while continuing to trim ordinary ASCII boundary whitespace; all other app import pathways retain their previous behavior.
- spend_vendor_evidence_r358.spend_vendor_evidence() compares original labels using ASCII-only case-insensitive identity. It retains significant Unicode differences, produces an unambiguous escaped display (including literal backslashes and semicolons), counts variants and flags a review collision.
- spend_analysis.summarize_spend() now uses that single consistent source-evidence result for normalized_vendor_collision_review, vendor_label_variants, and source_vendor_labels, both for real CSV imports and the direct API.
- No new source uploads, telemetry, float arithmetic, changed accounting totals, payment approvals, or compliance decisions. The file SHA/source row and deterministic vendor-month line evidence remain bound to the imported snapshot.

## Executed and outstanding evidence

- Linux Python 3.13.5 isolated source-helper harness using contract-equivalent local stubs for shared visible_source_text and ascii_case_identity dependencies: normal **16/16 PASS**; optimized -OO **16/16 PASS**; 32 focused executions total.
- Exact helper and unit-test local Git object hashes equal the committed GitHub blob SHAs: a26fa14f4d5624cf36c5e82b40a1be705d1ba392 and fa2cd629ade64d1c8a8cb287e0edaed0b9492f88.
- Nine full-engine tests added in test_spend_vendor_integration_r358.py; Python source compilation succeeded. **NOT executed** against a complete private checkout. The actual modified importer and SpendMap report writer have **NOT** been integration-tested in this environment.
- Ubuntu and Windows x64 CI workflow must run both test files under normal and -OO modes. Hosted runners on R357 failed **before executing steps**, so no CI, Windows build/smoke, AES-GCM, Defender, accessibility, signing, premium entitlement or site publication gate can be declared passed.

## Highest-impact next action

Restore GitHub Actions runner assignment/billing/eligibility, inspect failed-check annotations, and run R358 unit + genuine CSV/report integration tests **plus all R342–R357 regressions and the 22 genuine AES-GCM integration cases** on this exact head. Resolve failures. Then perform each of the six native Windows x64 EXE build/smoke, SHA-256, Defender and accessibility acceptance gates; verify gated premium fulfillment and obtain independent QD/founder signoff. No unrestricted premium binaries or speculative download URLs.
