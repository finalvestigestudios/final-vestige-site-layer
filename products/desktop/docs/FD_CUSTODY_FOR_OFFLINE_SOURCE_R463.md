# Final Vestige Labs R463 — descriptor custody for offline regression source inventory

**Status:** DRAFT / SOURCE-ONLY / HARD RELEASE HOLD. [Issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Strictly stacked on [R462 draft #2690](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2690) at parent `548edf0dc03fe489aaeebb650793f5f2ffe9077a`, not production `main`.

## Gap and fix

The R459 fallback fingerprint used `Path.is_symlink()`, `is_file()`, `stat()` and then `Path.read_bytes()` as separate operations. Hardlinked test files, symlinked **parent** directories, and replacement of the file between check and read could escape its narrow preflight. R461's complete import-tree fingerprint used R408's hardened descriptor custody, but that covered a different inventory; R459's independent test modules and helper scripts still had the weaker reader.

R463 changes the R459 `_source_fingerprint` implementation to reuse R408's `_read_verified_source_bytes` and `_require_real_directory`: checked single descriptor, regular single-link file, no symlink/reparse object, bounded 2,000,000-byte reads, before/open/after path/fd identity, complete read and extra-byte detection. Every source/test parent directory is checked before **and** after reading. A fixed, customer-data-free `LocalGateError` replaces source-specific failures. Valid ordinary files retain the **exact pre-existing fingerprint byte layout** (relative path + NUL, uint64 length, SHA-256 source bytes).

This is an improvement in local integrity and race detection, **not** absolute protection against adversarial swaps of all ancestor components between checks, signed provenance, or independent binary attestation. The R408 reader and directory checks remain the same audited functions; source-only gates still cannot approve releases.

The R459 regression test module gained **13 targeted methods**: legacy digest parity, repeatability/mutation, hardlink, direct symlink, parent symlink, empty/missing/oversized source, relative checkout, all-files descriptor invocation, fixed-error redaction, observable parent swap during read, and nonmutation of sources. An existing Windows symlink-privilege capability branch now returns normally rather than recording a `unittest.skip` that would itself fail the strict no-skips offline gate. Existing normal/`-OO` source CI steps already execute this module (31 total methods in that module after R463).

## Actually executed local focused evidence

- Linux Python 3.13 local **isolated source projection**, using the reconstructed R408 checked-fd read boundary and the R463 fingerprint implementation with synthetic source fixtures: **13/13 native unittest PASS** under normal Python and **13/13 PASS** with `-OO -W error`; **26 method executions**.
- Genuine OS hardlink/symlink tests and a parent substitution after read were exercised on the local Linux filesystem; original digest layout matched.
- The local execution **did not load the exact complete repository**, the original R408 file byte for byte, the complete committed R459 test module, or any of the six application launchers. The 13 new committed test methods remain **unexecuted against their full repository dependencies**. This result must not be misrepresented as CI, full suite, native Windows, or shipping evidence.

## Exact follow-up for checkout owner

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_offline_regression_gate_r459.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_offline_regression_gate_r459.py
python -B products/desktop/offline_regression_gate_r459.py
```

The third command is the full source-only fallback; successful output must show all twelve real regression mode runs, twelve launcher statuses, and `release_authorized=false`. Nothing here is an executable release gate.

## Blocker, next high-impact action and QD safeguards

The R462 exact-head [source #43784766317](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43784766317) and [Windows internal build #43784766316](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43784766316) failed before any test steps in all four jobs. The job-log endpoint returned `404 BlobNotFound`, so a precise infrastructure root cause is **not confirmed**. A repository/account administrator must inspect GitHub Actions UI job annotations, spending limits and hosted-runner eligibility, and restore runners. Then rerun exact-head source tests and real Windows x64 builds, installed executable smoke, Defender/EDR, keyboard and screen-reader accessibility, SHA-256/signature custody, and **entitlement-controlled premium delivery**.

No direct `main` merge, WordPress update, binaries, public premium URLs, licenses or payment changes. Four free utilities and two premium utilities remain in review. Independent QD review and explicit founder release approval are mandatory; all financial/compliance findings require human review.
