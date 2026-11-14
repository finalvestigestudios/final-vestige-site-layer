# R428 — SpendMap original vendor-label custody (source only / release hold)

**Issue:** #73. **Scope:** SpendMap Lite's human-review label evidence, *not* financial matching policy. No release, binary, distribution, or WordPress changes.

## Defect, minimal fix, and exact invariants

Before R428, `spend_vendor_evidence` called `strip(" \\t\\r\\n\\v\\f")` on each original vendor **before saving the label for display**. Thus a financial CSV containing `" ACME"`, `"ACME "`, and `"ACME"` could produce the same `source_vendor_labels="ACME"`. Normalizing these as one vendor key is intentional, but hiding the actual original boundary bytes from human review was not. A source physical row / SHA could locate the records, yet the visible summary silently erased that specific evidence.

R428 preserves each distinct original native source label for human display. It uses the already audited `visible_identity_label` renderer: leading/trailing ASCII spaces become literal `\\u0020`, source tabs/control characters are escaped, semicolons cannot forge list separators, and literal backslash sequences stay visibly distinct. It **does not** change normalization/collision semantics: only ASCII boundary whitespace is still ignored for identity comparison; non-ASCII boundary characters remain significant. Empty/ASCII-blank labels are not added. Duplicate originals are displayed once; rendering is deterministic for any input row order.

The change intentionally makes `source_vendor_labels` contain **more faithful original text**. Users who compare this CSV field byte-for-byte should account for the explicit boundary markers. `vendor_label_variants` is still the number of ASCII-case/ASCII-boundary normalized identities, not the raw spelling count. Labels are review/navigation evidence, not verification of source authenticity or supplier identity.

**Unchanged:** `source_sha256`, physical row coordinates, vendor/month full-membership digests, exact Decimal amounts, category/month grouping, source input bytes, source no-overwrite protections, mixed-sign review flags, human approval requirements, and CSV formula handling by the existing shared export writer. Other five apps are unchanged.

## Artifacts

- `fvs_suite/spend_vendor_evidence_r358.py`: preserve original labels for visible review.
- `tests/test_spend_vendor_evidence_r358.py`: adapt one intentional legacy compatibility assertion without changing the collision count.
- `tests/test_spend_source_label_custody_r428.py`: 18 independent offline unit methods covering spaces, tabs, Unicode, literal escapes, semicolons, deterministic order, and private-input rejection.
- `tests/test_spend_source_label_integration_r428.py`: five committed actual-`summarize_spend` integration methods covering reports, amounts, source rows, provenance, collisions and permutations.
- `.github/workflows/desktop-source-evidence-r385.yml`: both Ubuntu and Windows run new tests, inherited R358 tests and real-engine tests in normal and `-OO -W error` modes.

## Local execution and limitations

The local isolated Linux Python runtime ran **18/18 R428 focused unit tests in standard mode** and **18/18 in `-OO -W error` mode (36/36 executions)**; source compilation passed. The tested production helper and new unit-test file were **exact Git blob matches**:

- source: `90315804775e092d3a2b42280c2783bb4bddb6f2`
- unit tests: `442692dfd28e30de0529e8c0e1b9f7347fe03d63`

The local harness used compact stand-ins for the helper's `audit_display` and `review` dependencies, not a complete repository checkout. The **five committed real-engine integration methods, inherited R358 tests, full suite and native Windows build have not been executed** as part of this local run. Do not claim they pass based on the isolated evidence. Hosted CI status must be recorded from the exact draft head, not assumed from the workflow configuration.

## Required verification and release hold

1. Restore GitHub Actions runner eligibility (source Ubuntu/Windows and Windows desktop build). Run **this exact head**; record complete test logs, output artifacts, SHA, timestamps, and whether any inherited historical fixtures require deliberate migration.
2. Run full six-engine regression including Decimal, audit provenance, cryptography, entitlement, and the source-smoke gate in a complete checkout.
3. Physically test six portable Windows x64 candidates on clean Windows 11, keyboard/screen-reader accessibility, actual Defender/EDR and unsigned SmartScreen behavior. Validate independent provenance and checksums for each.
4. Confirm premium products are accessible **only via authenticated, entitlement-controlled** distribution; no public raw download path.
5. QD independent review and explicit founder approval **before merge/release**. `release_authorized=false`; no financial compliance determination or automated payment decision.

**Next highest-impact step:** unstick hosted runner allocation, then execute the full exact-commit integration and release evidence gates; further source patches alone cannot substitute for Windows evidence.
