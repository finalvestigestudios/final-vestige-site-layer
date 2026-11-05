# R201 — No test tracebacks or fixture data in desktop CI logs (DRAFT / HOLD)

Tracking: issue #73. Parent: R200 draft PR #1035; no main/production changes. The six Windows x64 applications are not released.

## Risk and fix

R200's fail-closed R194–R199 runner used `unittest.TextTestRunner`, which prints failing assertion values, exception messages and Python tracebacks to job logs. Even though audited tests use synthetic fixtures, paths and locally generated financial values must not be copied into Actions output by a failing test. Module-level imports and test bodies also print to Python stdout/stderr.

R201 swaps the text reporter for a non-rendering `unittest.TestResult`, discards Python-level stdout/stderr while importing and executing each audited test module, and logs only a validated static test filename and aggregate executed/skipped count or static HOLD reason. Missing files, low test counts, exceptions, all-skips, and failures still HOLD. R197's platform-specific partial skip remains visible as a number, never counted as a pass; individual skipped test details never print. The R194–R199 matrix and its minimum 148 tests per Python mode are unchanged.

New `test_recent_regression_privacy_r201.py` exercises 17 synthetic cases including assertion and exception text, import-time output, `setUpClass`/`tearDownClass`, subtests, skip reasons, zero discovery and partial skip. CI invokes it normal and `-OO` on Ubuntu and Windows *before* the inherited audit matrix. R200's original 16 regressions must still pass.

## Boundaries

This suppresses Python `print`, Python `sys.stderr.write`, and unittest exception rendering from the audited runner. It does not promise isolation from untrusted native extensions writing directly to OS-level file descriptors, detached subprocesses, or tests that transmit data themselves. Run only approved synthetic tests on CI with no customer datasets or credentials. It is not a native Windows EXE check, malware clearance, QD approval, or permission to publish any of the six products.

## Release gates

Confirm tests on both hosted systems after Actions runner provisioning recovers, run the entire inherited desktop suite, privately build and smoke six Windows x64 candidates, independently verify checksum and Defender/EDR evidence on actual Win11, perform keyboard/Narrator/NVDA/high-DPI acceptance, protect premium deliveries, and obtain independent QD/founder approvals. No production deployment or public downloads from this sprint.
