# R332 — Restore legacy regression expectations for preserved premium review evidence

**Status:** DRAFT / issue #73 / independent QD + founder approval HARD HOLD. This branch is stacked **only** on R331 (PR #1913; `c227cf853c8d627826a86d9b281bcc67570a02f6`), **not** on `main`. No executables, releases, production merges, or entitlement changes.

## Confirmed regression against R331

R331 deliberately removes rollback deletion of a newly-created review journal after validation failure, retaining a zero-byte private custody artifact for explicit inspection and retry. Two earlier tests still asserted that the file **must not exist**:

- `test_journal_io_r47.py::test_failed_verification_does_not_leave_empty_journal`.
- `test_journal_io_privacy_r290.py::test_verified_callback_oserror_is_sanitized_and_empty_file_removed`.

Those two assertions contradict R331's shipped behavior. They are not evidence of a writer bug; if CI is restored with those expectations intact, the full regression suite will report failures even if R331 works as designed.

## R332 changes

1. Update both historical regression methods to expect **an existing empty file** after post-open validation rejection, with byte-exact `b""` checks. Preserve the original privacy-safe `ValueError`, pre-open failure, and non-destructive history checks.
2. Add `test_journal_failure_contract_r332.py` with **10 focused synthetic tests** covering rejection retention, redacted `PermissionError` and detached exception chains, no `unlink`, explicitly retried empty-file append, existing history, pre-open invalid-input and permission-denied noncreation, ambiguous `fsync` failure, successful append and private POSIX mode.
3. No production Python modules changed. The four free applications remain untouched; the two premium applications retain local-first, deterministic human-only exception custody. No ledger Decimal operations or financial outcomes changed.

## Reproduced and executed local evidence (2026-11-10; Linux, Python 3.13.5)

Executed four exact source Git blobs in an **isolated reconstruction** of the premium journal I/O dependency slice, verified using `git hash-object`:

| Source file | Exact Git blob |
| --- | --- |
| `fvs_suite/journal_io.py` | `abeeeecc8a5da1790cacf62ae93c5092e81b6fb4` |
| `fvs_suite/journal_write_receipt.py` | `06ec7187c9d883e4a3e5910ebf8b512a83008087` |
| `fvs_suite/journal_fd_read.py` | `2140c15d6d14b92afa0036dff32512a7706a301f` |
| `fvs_suite/csv_snapshot.py` | `a695123f1adc133dfac2cc38726540fe373618fe` |

- **Old expectations reproduced:** 2 out of 2 obsolete `assertFalse(path.exists())` assertions failed against the exact current R331 source (expected before the test correction).
- **New committed R332 regression file:** `6e3f1fbe176fed5a1823b7c5b8f1414f9942efef`, identical to the locally executed file.
- **New focused regressions:** `10/10 PASS` with `-W error` and `10/10 PASS` with `-OO -W error` = **20/20 successful focused executions**, 0 skipped.
- Python compilation of the isolated copied modules and new test: PASS.
- **Not executed:** the actual amended complete R47/R290 test modules, the complete private checkout test suite, genuine AES-GCM integration cases, or native Windows x64 acceptance. The local reconstruction contained the exact four Git source blobs, but is **not** end-to-end repository verification.

## Reproduce in a full checkout (mandatory before merge)

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_io_r47.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_io_privacy_r290.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_failure_contract_r332.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_failure_contract_r332.py'
python products/desktop/scripts/offline_source_gate.py
```

These commands must be run against the full checked-out PR head. If any fail, this PR remains held.

## Release/QD hold and highest-value next action

The latest inspected [R331 Actions run #42839745383](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42839745383) failed with `source-tests` and `windows-build` jobs showing no recorded steps/logs; exact infrastructure cause was not established. Owner: examine GitHub Actions billing and spending limits, workflow permissions, and runner eligibility, then rerun this branch's complete source suite in normal and optimized Python, including all **22 genuine AES-GCM integration cases**. Native Windows 11 x64 acceptance for each of the six privately built executables, SHA-256 verification, Defender and accessibility reviews, protected premium distribution, independent QD, and founder signoff remain mandatory. **All six products unreleased.**
