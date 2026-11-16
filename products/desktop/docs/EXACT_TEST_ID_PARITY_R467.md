# R467 — Bind offline regression receipts to exact test identities

**Status: DRAFT / QD HARD HOLD.** This is source-only verification of six desktop applications. It does not authorize binary publication, premium downloads, payment/licensing changes, or production deployment.

## Defect

R466 required a floor of **9 LedgerDiff Lite, 10 Invoice Twin Scout, 7 SpendMap Lite, 4 Policy Delta Desk, 5 GrantAudit Studio Pro, and 10 ProcureGuard Studio Pro** discovered test methods in *each* of standard and optimized Python modes. R466 compared only counts, however: `-OO` could discover a *different set of test methods with the same count* and still satisfy the acceptance gate. That is an avoidable blind spot for release-adjacent verification.

## Change

The local, isolated `unittest` child now enumerates each discovered `TestCase.id()` **before** running its suite. It rejects missing, duplicate, non-string, empty, or overlong test names, and computes a SHA-256 over sorted UTF-8 test IDs with two-byte big-endian length prefixes. The child sends only the 64-character lowercase `test_ids_sha256` in its small, owner-private JSON receipt, **never customer financial data or raw test names**.

The parent requires the new exact six-field JSON schema, native integer counts, zero failures/errors/skips, full method floors, and *identical counts and test-ID digests for the same module* in standard and `-OO` Python. Added tests are allowed when both modes agree; a legacy five-field receipt fails closed.

The fingerprint of tested sources, 28 required module/mode subprocesses, twelve six-app smoke statuses, source continuity checks, and `release_authorized: false` remain intact. No changes to Decimal money logic, vendor data, approvals, premium authentication, human compliance review, or external connectivity.

## Reproducibility and evidence

New regression methods in `tests/test_offline_regression_gate_r459.py` cover missing/invalid digests, same-count/different-ID rejection, additional matching coverage, **real optimized Python child discovery** with deliberately altered IDs, and duplicate unittest IDs. Existing tests now include the digest in their child receipt fixtures.

The implementation's child algorithm was independently projected into a small isolated Python fixture on Linux and actually executed with standard and `-OO` interpreters: **4/4 focused projection tests passed**, covering stable names, equal-count name changes, duplicate discovered names and skipped tests. This is **not** a full GitHub-checkout or six-engine test run and is not native Windows evidence. The five committed regression methods still need to be executed against the full checkout.

Once an authorized checkout/runner is working:

```shell
python -W error -m unittest discover -s products/desktop/tests -p test_offline_regression_gate_r459.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_offline_regression_gate_r459.py
python -B products/desktop/offline_regression_gate_r459.py
```

Verify both Python runs, the twenty-eight actual child receipts, the twelve launcher statuses, and source hashes before considering native Windows packaging. Never treat a method floor as a passing run.

## Release hold / next highest-impact work

CI runners previously failed with zero job steps, leaving the current real Windows x64 verification blocked. Inspect GitHub Actions job annotations, billing/spending limits and runner eligibility, restore an authorized full-checkout worker, execute the full offline regression matrix, then test true Windows x64 builds, installed applications, accessibility, Defender, checksums and **authenticated** premium distribution. Independent QD review and explicit founder approval remain required. No binaries or live download links are included in this sprint.
