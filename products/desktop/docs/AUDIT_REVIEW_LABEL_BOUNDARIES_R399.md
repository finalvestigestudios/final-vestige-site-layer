# R399 — Unambiguous human-review source label boundaries

**Scope:** Final Vestige Labs issue #73; shared source layer and premium review presentation. **DRAFT / QD + founder HARD HOLD.** Stacked only on R398 draft, not production main. No executable or download published.

## Reproduced defect

The shared audit_display.visible_source_label_list stripped ordinary ASCII spaces before retaining labels. On original R398 Git blob a8e0858fb7fd37caf8daf8a78ab5329678c05895, synthetic values [" PO-1", "PO-1", "  "] rendered as "PO-1". This collapsed distinct original source identities and hid a whitespace-only value. Separately, visible_review_row displayed raw ASCII boundary spaces, difficult to distinguish in premium review queues. R398 review.labels_for_report already escaped these boundaries correctly, but the shared audit display did not.

An inherited R97 regression still expected whitespace-only identifiers to disappear, contradicting R398's lossless identity contract. R399 correctly distinguishes absent/empty fields from literal spaces without relaxing audit gates.

## Changes

- fvs_suite/audit_display.py: visible_identity_label escapes source boundary ASCII spaces as \u0020, semicolons as \u003B, and retains existing Unicode/backslash rendering. Native strings only; untrusted __str__ and subclass methods are not executed. Source-label lists preserve distinct spellings, including whitespace-only values. Premium visible_review_row uses this renderer for source keys.
- fvs_suite/review.py: labels_for_report delegates to the same audited renderer. No change to normalized matching or Decimal arithmetic.
- tests/test_audit_identity_boundaries_r399.py: **22** synthetic offline methods covering preservation, display, determinism, hostile types, premium review rows and source immutability.
- tests/test_source_label_visibility_r97.py: correct obsolete empty/blank assertion by checking absent and whitespace-only separately.
- .github/workflows/desktop-source-evidence-r385.yml: gate new R399 and inherited R81/R97 tests in normal and optimized modes on Ubuntu and Windows.
- No customer financial records, compliance decisions, payments, telemetry, cryptography, signing, binaries, entitlements, website changes or public distribution.

## Test evidence and limitations

Local Linux CPython 3.13.5 executed **22/22** focused methods in standard mode, and **22/22** with python -OO -W error: **44/44 test-method executions PASS**. Python source compilation passed. This was an exact-Git-blob **source subset**, not the full repository checkout. Git blobs byte-identical to executed files:
- audit_display.py: 6438c8aaf3ceecf927534fe8fbb91a019ca8d011
- test_audit_identity_boundaries_r399.py: 7a5146f88a88df1e61003872da144b3c7a5ee295
- unicode_hazards.py: 50801b3f168396b0e2c75e95352e435f7c936588

The revised review.py delegate and inherited R81/R97 tests, full CSV engine imports, six-app integration, Windows native executables, Defender, entitlement and full financial/cryptographic suites have **not** been run against a complete checkout. Passing focused tests do not establish release readiness. Input bytes, provenance and human decisions remain unchanged by this display fix.

R398 exact-commit [source run #43399228809](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43399228809) and [desktop run #43399228810](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43399228810) failed before recorded job steps. This is missing hosted verification, not a Python test failure. Inspect R399 exact-HEAD runs separately.

## Next highest-impact acceptance step

1. Restore GitHub Actions runner eligibility/billing if needed and execute the exact R399 HEAD on Ubuntu and Windows, normal and optimized modes, including inherited R81/R97 and new R399 tests.
2. Execute R398 import integration and complete six-engine Decimal/provenance, premium human review, AES-GCM, Ed25519 and SQLite regressions on full checkout.
3. Validate six native Windows x64 executable smokes, keyboard/screen reader, Defender, checksums/signing disclosure, and gated premium download/payment workflows.
4. Require independent QD and explicit founder approval before any production merge, WordPress publication, or executable release. All six apps remain **UNRELEASED**.
