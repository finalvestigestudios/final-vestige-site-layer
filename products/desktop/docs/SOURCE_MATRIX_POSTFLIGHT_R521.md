# R521 — source matrix postflight custody (DRAFT / QD HARD HOLD)

Tracks [desktop suite #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This change stacks **only** on R520 [draft #2992](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2992), not production `main`.

## Reproduced logic gap

Before R521, `source_evidence_runner_r509.execute()` captured source-file SHA-256 fingerprints before launching the pinned checks and verified each immediately before launching it. **It did not verify the source inventory after the last subprocess returned zero.** The final check could mutate its own source or a previously executed test file, return zero, and the runner would print an unqualified source-matrix PASS. Separately, the immutable 416-command manifest was read and verified once before the matrix, not reread when the matrix finished. These are custody gaps, **not evidence of a bypass of the pinned manifest SHA-1**.

## Changes

- New `products/desktop/scripts/source_postflight_r521.py` verifies every previously captured source-file fingerprint again **after** all subprocesses have exited with zero. Any missing, linked, modified or replaced tested source makes the matrix return nonzero before its success line.
- `source_evidence_runner_r509.py` now passes the exact original descriptor-read manifest bytes through `main()` and rereads the same manifest with the existing R520 bounded, descriptor-bound reader after the matrix. The content must be byte-for-byte unchanged. A missing/unsafe/modified manifest or custody exception is a generic privacy-redacted HOLD.
- Existing direct isolated `execute(verify_source_snapshots=True)` tests may omit a manifest snapshot, but then only the source-file postflight applies; the **production `main()` always enables both checks**. Providing a manifest snapshot without enabled source custody is explicitly rejected.
- Eleven regression methods are added to the existing pinned `test_source_evidence_runner_r509.py` module. Two inherited mock expectations are updated for the new `manifest_snapshot` argument; the original 416-command manifest **remains unchanged**.

## Verification and evidence limits

The new standalone postflight helper was exercised locally on Linux under regular Python and `-OO` with warning-as-error mode: **13/13 PASS each, 26/26 focused method executions**, no skips; `py_compile` passed. This is **not** a checkout-wide run, the 11 committed integrated regression methods were **not** executed in the complete repository, and native Windows behavior and six EXEs are **not** verified. Run the exact full module and original 416 commands in both modes on supported Ubuntu and Windows runners before treating the source gate as validated.

The previous local controls only exercised the focused standalone verifier, not the complete committed runner. This change increases read-only test-evidence confidence; it does not guarantee atomic tree state, track unlisted imported modules, or detect an adversary who changes and restores a file between observations. Do not equate the output with runtime app, Defender, accessibility, signing, protected premium distribution or site verification.

## QD and founder hard hold

All six applications remain **UNRELEASED**: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro. No production branch, WordPress catalog, payment flow, entitlement key, private customer data or public download was changed. Continue local-first processing, exact Decimal accounting, immutable source references, deterministic audit logs, and human review; the helper never approves a financial or compliance decision.

**Next highest-impact gate:** Resolve [Actions pre-step failure #75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75): repository/account admin checks the failing run's GitHub UI banners, Actions billing/spending ceiling, workflow policy, and hosted-runner allocation, then reruns the **exact R521 commit**. Require all 416 pinned source commands, committed R521 regressions and six native Windows x64 executable smoke/security/GUI/keyboard checks. Obtain independent QD review and founder release approval before any merge, packaging distribution or premium access.
