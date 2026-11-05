# Final Vestige Labs R203 — preflight entire audit module manifest before execution

**Status: DRAFT / HARD RELEASE HOLD.** Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R202 draft [#1046](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1046) at immutable parent `0fed83f6c9bc69659260252dc1880f81ec831c0a`. Never commit or merge to `main` without independent QD and founder approval.

## Reproduced defect and repair

Before R203, `run_matrix` checked each contracted test source immediately before executing it. If the first module passed but a **later** audited module was absent, a directory, a symlink, duplicated, or an invalid selector, the runner failed *after* already importing and executing the earlier module. Those imports can create local outputs or mutate process state even when the overall audit matrix is known to be structurally invalid.

R203 performs a complete **structural** manifest preflight before importing **any** audited module. It checks six fixed audited names, native minimum counts, permitted filename syntax, duplicates, file presence and symlinks, and only then invokes the existing private Python `unittest` runner. It retains the strict R202 fail-on-skips/expected-failures/interruption gate, Python-level stdout/stderr suppression, and the 148-method minimum R194–R199 contract.

This is **not** a claim of transactional test execution: imports/tests can still fail after another valid test has executed; this change specifically prevents work from starting when a *known structural failure* exists later in the selector manifest.

## Exact local executed evidence

Synthetic tests run on Linux CPython using the **byte-identical Git blob** of the committed updated runner (`1311625a800da219d2c95ca9dd4718ef69bbf0da`) and new R203 tests (`972fa46afcc30981b85a63c19d133a8b8c863995`).

- Before repair: the R203 tests detect **7/11 failures** against the original execute-as-you-go semantics (sentinel fixture imported when later source was malformed).
- After repair: **11/11 PASS** with standard Python, **11/11 PASS** with `python -OO`; **22/22 total local focused executions**, no skips.
- Python `py_compile` passes for the runner and added test module.
- The self-tests use disposable temporary test modules and a local sentinel file, not any customer data. The symlink rejection is tested by mocking the file metadata guard, without assuming Windows symlink privileges.
- Both Ubuntu and Windows GitHub Actions job definitions now invoke R203 self-tests in normal and optimized Python before the audited matrix. Windows checks each PowerShell `$LASTEXITCODE`.
- The **full inherited suite**, Windows-hosted execution, native Windows x64 builds and app smoke tests were **not** run locally. Structural CI wiring is not evidence of hosted CI execution.

## Remaining release gates / owners

GitHub Actions has repeatedly failed before reporting any worker steps, including R202 [run #41977762516](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41977762516); cause **unconfirmed**. GitHub repo owner must open the failed-run banner, inspect Actions billing/allowance, workflow permissions and runner provisioning, restore hosted execution, and rerun this exact branch head.

**Next highest-impact engineering target:** investigate R197's `test_source_symlink_cannot_be_published` test, which can issue a platform-dependent `skipTest` if creating a native symlink is denied. R202's strict 148-test matrix will correctly HOLD on any such skip. Preserve native Windows acceptance and add an explicitly labeled deterministic fallback/independent platform witness rather than silently weakening the gate.

After runner recovery, run inherited app tests on both OSes and privately build, checksum, Defender-scan, launch/smoke and accessibility-test six Windows x64 candidates. Protect GrantAudit Studio Pro and ProcureGuard Studio Pro with payment/license controls before distribution. Require independent QD and founder review.

**RELEASE HARD HOLD:** LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro remain **unreleased**. No production mutation, public binary, invented download URL, unrestricted premium asset, telemetry or automated compliance decisions were introduced.
