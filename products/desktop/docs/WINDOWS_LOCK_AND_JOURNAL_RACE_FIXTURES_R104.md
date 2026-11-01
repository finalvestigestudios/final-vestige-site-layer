# R104 — Windows-safe premium journal and review-lock race verification

**2026-11-01 UTC · DRAFT / RELEASE HOLD · Issue #73.** Based solely on R103 draft PR #419 at `822cb96c1c245ede2fb3918788470debb95bb866`, never production `main`.

## Why

The exact-head R103 Windows source gate reported **3 test failures and 22 errors across six modules** ([Actions #41283140839](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41283140839)); Linux normal/optimized gates and all six source smokes passed. Several adversarial tests attempt `unlink()`, rewrite or replace while `os.open` descriptors and exclusive human-review locks are held. These scenarios are valid on POSIX but may be rejected by Windows sharing rules before the application's custody check is reached. That is a test-fixture portability hypothesis; the precise causes of every Windows error were not available in privacy-suppressed logs.

## Change set and security conditions

- New `tests/synthetic_windows_fs_r104.py`: target-scoped **test-only** stat identity changes or missing-path observations, activated *after* initial validation. The underlying file is never changed. Production modules remain unchanged.
- New `tests/test_windows_race_fixture_r104.py`: six focused fixture regressions: inode, size, invalid fields, inactive observation, target isolation/file byte preservation and missing-path simulation.
- `tests/test_review_lock_r48.py`: four Windows-held-lock adversarial cases now simulate pathname disappearance, replacement, size mutation and implicit exit-time rejection, while POSIX cases retain actual unlink/mutation. The real `exclusive_review_lock` must still reject wrong identity and leave suspect locks for human inspection.
- `tests/test_review_lock_integration_r48.py`: simulate a competitor's observed lock identity change while a real premium grant-review append is underway, preserving the actual `exception_review` and `review_lock` logic and zero-auto-approval requirement.
- `tests/test_journal_io_r47.py`: three Windows races now simulate descriptor-size and pathname-inode drift *during* actual journal read/append routines, requiring the real validator to reject and leaving financial fixture bytes untouched. The POSIX tests still modify actual file paths.
- `tests/test_source_smoke_integrity_r42.py`: Windows source-file substitution and concurrent modification tests simulate FD inode/mtime drift while exercising the actual source inventory; POSIX retains destructive synthetic fixtures.
- `tests/test_release_report_r38.py`: compare the **existing parent directory's actual identity** with `os.path.samefile` rather than exact spelling of Windows resolved temporary paths. Still demand a new, nonexistent output file outside the distribution directory.

No matching, monetary, Decimal, invoice classification, procurement approval, license entitlement, premium encryption, source-file guard implementation, WordPress, website, deployment or production branch is modified. **These changes do not grant release authority.**

## Reproduce with Python 3.12+ in an exact Git checkout

```bash
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_windows_race_fixture_r104.py' -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_windows_race_fixture_r104.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -v
```

Do not publish complete private test traces or customer file paths. Mandatory `offline_source_gate.py` R57 runs these complete suites plus all six source smokes on both Linux and Windows. **As of this draft, tests were committed but exact-head CI results must be inspected before recording any passing claim.** A synthetic passing test never substitutes for native Windows verification.


## Confirmed R56 Windows runtime-file discrepancy and constrained production repair

[Actual Windows Actions #41288159038](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41288159038) confirmed a specific native Windows/Python 3.12 fixture anomaly: for the **synthetic runtime file named `python.exe`**, `Path.lstat()` versus `os.fstat(open_fd)` differed in **st_mode only**. The same probe reported dev/inode/nlink/size/mtime/ctime all **PASS**, and the synthetic distribution package files and manifest exclusive publication separately **PASS**. `runtime_file`, `snapshot` and `capture` were blocked, explaining all 15 remaining R56 errors. The complete Windows suite was **0 failures / 15 errors in one module** at that pre-repair head; Linux source suite remained green. No assumption that raw mode values or genuine production binaries were verified.

The follow-up code change to `scripts/toolchain_guard.py` permits only differences in `S_IXUSR|S_IXGRP|S_IXOTH` when comparing **Windows regular .exe pathname metadata to its opened descriptor**. No .py, JSON manifest, non-regular file, symlink, hardlink, changed write permissions or file-identity substitution is admitted. All same-view before/after path/FD metadata checks (including full mode and ctime), hash and byte bounds remain unchanged. Added `test_toolchain_executable_mode_r104.py` with 12 synthetic normal/-OO-compatible mutations to preserve this boundary. **This is an evidence-backed narrow hypothesis until real exact-head CI passes**; the next Windows run must establish `runtime_file=PASS`, `capture=PASS`, mandatory normal/-OO suite PASS and six engine smokes before packaging proceeds. Never construe successful synthetic .exe reading as native Windows EXE launch verification.

## Release / next action

On hosted Windows runner, count remaining privacy-safe source-owned failures; fix actual production problems if found, but do not relax pre/post custody comparisons, lock validation, human-review gates or SHA-256 checks. After Linux/Windows complete normal and `-OO` suites are green, build six x64 executables and verify PE, hashes, AV, keyboard/GUI, offline handling and premium access-controlled delivery in independent QD/founder review. **All four free and two premium utilities remain unreleased; no public executable or unprotected premium URL.**
