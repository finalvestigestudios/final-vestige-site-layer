# R315 — packaged premium vault denial custody (DRAFT / QD + founder HOLD)

Tracks [Labs desktop issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on [R314 draft PR #1802](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1802), head `5cd12aee50001bad3f2e00fbaf2b3d444c9e7395`, never `main`.

## Acceptance defect

The R314 packaged premium smoke verified a correct product-bound restore, then that the opposite product was rejected and the restored manifest *fields*, report/journal bytes and root filename set remained acceptable. But a denial that changed only manifest formatting or a nonvalidated timestamp, or substituted a new file/directory containing **identical bytes**, still passed the smoke gate. That fails the negative authorization path's custody invariant even though the data appears intact.

## Change

The shared packaged smoke helper now keeps the **exact manifest bytes** witnessed after a valid restore and requires them unchanged after cross-product denial. It additionally records `lstat()` metadata (device, inode, mode, size, nanosecond mtime/ctime) for the synthetic root, restored directory, encrypted archive, source report and journal, and every restored member. Metadata must remain identical across the denied restore. Symlink checks, complete member inventory, source-byte checks, archive checks, strict manifest structure, original product binding and no-extra-plaintext tests remain.

No change to the actual production AES-GCM vault implementation, encryption key derivation, pricing, entitlements, any of the four free engines, Decimal-safe money handling, deterministic financial evidence, or human-only review decisions.

## Executed local verification

Reconstructed exact R314 helper source from GitHub; source Git blob hash `28eb76cdb623674fffc730d70fb06d67320f98ec`. On Linux CPython 3.13.5, using only synthetic report/journal and test doubles in a temporary directory:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_smoke_custody_r315.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_smoke_custody_r315.py'
python -m py_compile products/desktop/fvs_suite/vault_smoke_scope.py products/desktop/tests/test_vault_smoke_custody_r315.py
```

Locally executed with the exact file bytes committed to this branch, under a minimal **test-only** `fvs_suite/__init__.py` stub not committed:
- Normal CPython: **10/10 PASS**.
- Optimized `-OO`: **10/10 PASS**; total **20/20 test-method executions**, two product variants each.
- Python compilation: **PASS**.
- Exact Git blob hashes: helper `6450cd8d54962035a3e4c81ad144f6a620b9056d`; new test `8b7f5d0c376b1758c08187621f91919ae7dd04bf`.
- Against the byte-verified unmodified R314 predecessor, the new test module produced **18 failing product-specific subtests** across 9 adversarial methods; unchanged success case passed. This validates the regression tests detect the prior acceptance gap.

The new CI steps run this test module under normal and optimized Python on **both Ubuntu and Windows**. Previously existing R313/R314 regression tests remain in the workflow.

## Limits and release blockers

This is a **smoke-test witness**, not a filesystem lock or an immutable evidence format. A malicious same-user process may still exploit a time-of-check/time-of-use race, and metadata identity is not sufficient for forensic attestation. Platform-specific NTFS behavior, real AES-GCM integration, full inherited test suite, actual packaged Windows binaries, AV, keyboard/screen-reader testing, license and protected premium delivery are **not locally verified**. No historical CI failure should be characterized as passing tests.

Actions on R314 [run #42707540827](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42707540827) failed Ubuntu and Windows before any recorded steps. Investigate this branch's newly triggered CI independently; do not assume infrastructure root cause.

**Next highest-impact:** Owner resolves GitHub Actions runner/billing/permissions restriction, completes the full Ubuntu/Windows normal + optimized + AES-GCM integration suite, then privately builds and accepts all six distinct Windows 11 x64 executables (PE architecture, smoke, SHA-256, Defender, accessibility), with entitlement-gated premium distribution. Independent QD + founder approval is required before merging or releasing. **No binaries, website publication, production changes, or public premium files in R315.**
