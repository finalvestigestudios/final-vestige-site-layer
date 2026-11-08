# R277 — restore inherited receipt compatibility and enforce outer source-smoke schema

**Scope:** issue #73, internal six-app Windows x64 candidate pipeline. **Release posture:** DRAFT / founder and independent QD hard hold. No public binaries, publishing, privileged download links or compliance authorization.

## Defect and immediate impact

R276 correctly tightened each source-smoke application record to canonical engine IDs: `ledger`, `invoices`, `spend`, `policy`, `grants`, `procurement`. But the shared R270 synthetic receipt fixture (imported by R269, R270 and R273 integration tests) still set `engine=name.lower()`, yielding `ledgerdifflite`, `invoicetwinscout`, etc. R276's helper demonstrably returns `False` for that fixture, even though these tests previously relied on its being a valid baseline. Hosted CI has never reached tests, so this is **static source/isolated regression reproduction**, not an observed hosted CI failure. The fixture is now aligned with the actual six-engine producer and includes the producer's `commit` field.

A second defect: the Windows candidate runner accepted extra unexpected keys in the surrounding `source_smoke` JSON object even though the root receipt and per-app records were exact-schema. That could let unreviewed, potentially sensitive fields (such as a customer path) become part of accepted private evidence. The runner now requires the exact eight fields of `source_smoke_gate.report_data`, verifies the release/QD flags are literally false, and accepts only an empty local commit marker or a lowercase 40/64-character hexadecimal commit ID. It still hashes the original untouched evidence bytes and performs the existing source-file binding checks before native builds.

## Change inventory

- `products/desktop/tests/test_offline_windows_candidate_r270.py`: repair central inherited synthetic receipt fixture; do not weaken R276 production validation.
- `products/desktop/scripts/offline_windows_candidate_r269.py`: enforce an exact producer-consistent outer smoke receipt; reject unexpected/private metadata and unsafe commit IDs.
- `products/desktop/tests/test_source_smoke_runner_integration_r277.py`: integration of the **actual candidate** receipt validator with its central inherited fixture, including negatives for extra secrets, missing fields, invalid commit markers, false release claims, contradictory engine identities and tampering.
- `.github/workflows/desktop-build.yml`: run R277 integration methods on Ubuntu and Windows, normal and `-OO`.

## Verification boundaries

Focused isolated check against a transcription of the R276 helper reproduced the R270 fixture failure and confirmed that the canonical six-engine mapping passes. An independently reconstructed outer-validator probe on Linux ran **15/15 PASS normal + 15/15 PASS `-OO` = 30/30 isolated checks**, with Python `compileall` passing. **These probes are NOT repository integration runs and are not proof that the newly committed test module passed**; the repository-integrated R277 tests remain pending on a complete checkout. This does not prove the full R269/R270/R273 inherited suite or new R277 integration has executed: those require a complete trusted checkout and runnable Python. Run `python -W error -m unittest discover -s products/desktop/tests -p 'test_source_smoke_runner_integration_r277.py'` and the same with `-OO -W error`, then the whole desktop suite.

### Release gate

No Windows PE was created, signed, Defender-scanned, smoke-tested, accessibility-validated, made available for download, or QD/founder-approved. First restore runnable Actions or use the already committed trusted Windows 11 x64 offline candidate pipeline, collect six native executable attestations and hashes in a private access-controlled directory, perform manual screen-reader/keyboard/high-DPI checks and gated premium entitlement verification. **Never merge to production or publish until independent QD and founder approval.**


## Additional executed extracted-runner integration (Linux)

After the initial commit, the **committed** R277 integration test module was re-created locally with its exact Git blob SHA `3d75c288fb7bcbfb9c6592576f78903b79844126`. The R276 validator helper was also byte-exact to Git blob `364c35f0d7ede1b16653fe0fb0b565221fb1a09f`, and the strict R273/R274 JSON decoder to `9de54dd6b6d9f0f2f07298fe90ebeaa77bf0ade4`. The private candidate runner's `_source_receipt_sha256` function and the corrected fixture were **extracted/transcribed** from the connected source; the local runner is **not** the complete GitHub file, and the full source binding hook was replaced by a test-only stub that intentionally cannot run (the 13 tests call without `checkout_root`).

In that explicit partial checkout: **13/13 R277 integration methods PASS normal**, **13/13 PASS optimized `-OO`**, with warnings-as-errors and Python `compileall` PASS. The test file and two helper files match their committed Git blob hashes; the extracted runner and fixture do not claim full-file hash identity. Combined with the separately executed 15 normal/15 optimized isolated schema probes, **56 local method executions passed** across two differently scoped harnesses. **Neither represents a full-repository source suite or native Windows executable validation.**
