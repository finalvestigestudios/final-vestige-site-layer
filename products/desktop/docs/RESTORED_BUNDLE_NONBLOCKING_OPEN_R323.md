# Labs R323 — nonblocking open custody for offline premium evidence

**DRAFT — QD and founder HARD HOLD.** Tracks issue #73. Branch based on R322 draft PR #1852, never `main`. No application release, premium entitlement changes, public download links, or production edits.

## Reproduced failure / narrow fix

The read-only restored-evidence verifier checks a file with `lstat()` and then opens it by pathname. A concurrent writer can replace a checked regular file with a POSIX named pipe (FIFO) between these two calls. A normal `O_RDONLY` FIFO open **blocks indefinitely** if no writer connects; the intended descriptor identity checks cannot execute, and a locally launched verification can hang. The attack requires write access to the evidence directory; it does not bypass encrypted vault authentication.

R323 adds `O_NONBLOCK` when the OS provides that flag to *every* descriptor open (manifest, report, and review journal), while retaining binary / no-follow flags, pre-open `lstat`, `fstat` identity, size/digest budgets, second-pass checks, manifest integrity, and private-path-free HOLD errors. On POSIX, a raced FIFO now opens promptly, fails descriptor identity/type custody, and returns a fixed HOLD rather than hanging. Regular-file reads and the independent SHA-256 witness retain their prior semantics. On Windows, `O_NONBLOCK` is used only if exposed by the platform; this change is **not** a Windows-specific kernel handle guarantee.

This is a race-hang defense in depth, **not** an OS filesystem lock or proof against an attacker with write privilege after verification. The SHA-256 witness remains meaningful only if obtained independently from a trusted record. Source authentication, reviewer identity, payment/compliance approval, and release authorization remain explicitly false.

## Reproduce safely (synthetic local data)

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_restored_bundle_open_race_r323.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_restored_bundle_open_race_r323.py'
python -m py_compile products/desktop/scripts/verify_restored_bundle_r320.py products/desktop/tests/test_restored_bundle_open_race_r323.py
```

The adversarial tests spawn killable child processes with a hard timeout. In a POSIX temporary directory, a test-controlled hook swaps a regular manifest, report, or journal for a FIFO **after `lstat()` and immediately before the real `os.open`**. On an unpatched build, the child would block until its timeout. With R323, the child exits promptly with a private-path-free HOLD. Tests also cover both premium products, present and absent journals, nonblocking flags on all reads, the unchanged external-witness API, and no evidence writes on successful inspection. FIFO-specific cases skip where unavailable, but the normal-path regression runs on both Ubuntu and Windows.

Local Linux focused evidence: **9/9 normal and 9/9 optimized, 18/18 executions PASS**, `py_compile` PASS. These are synthetic temporary directory tests; not genuine AES-GCM integration or Windows EXE acceptance. The full repository suite and hosted CI have not passed in this sprint because GitHub Actions runners have been failing before running steps.

## Mandatory next acceptance

Restore GitHub Actions runner scheduling / billing eligibility; rerun all desktop source tests and the 22 real AES-GCM integration cases, then privately build and smoke-test all six Windows 11 x64 executables, collect SHA-256 and Microsoft Defender evidence, and verify keyboard/screen-reader accessibility. Premium download entitlement must be verified before any release. Independent QD and founder approval are required for merge and publication.
