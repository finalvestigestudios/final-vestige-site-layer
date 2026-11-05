# Labs R205 — OS-level privacy boundary for the strict audited regression matrix

**State:** draft proposal; QD/founder HARD RELEASE HOLD. Tracks [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Branch `feature/labs-r205-os-fd-private-audit-20261105` descends from immutable R204 draft [#1061](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1061) at `b538cb7ca2dabd57bd4e13bfe6be3a6e524f90ef`. Never targets main; no site or premium distribution changes.

## Reproduced defect and fix

The R201–R204 `safe_recent_regressions_r200.py` runner uses `contextlib.redirect_stdout`/`redirect_stderr`. These only replace Python stream objects; a test/import or child process can write directly to operating-system file descriptor 1 or 2 or to `sys.__stderr__`, bypassing that protection and leaking a sensitive financial fixture into hosted Actions logs. The defect was reproduced on Linux CPython 3.13.5 using two **synthetic** FD canaries: both appeared in subprocess-captured stdout/stderr while Python-level redirects were active. No customer data was used.

The new `scripts/safe_audit_subprocess_r205.py` launches the **unchanged** strict R200 matrix as a dedicated child Python process with `stdin`, `stdout`, and `stderr` all bound to `subprocess.DEVNULL` at process creation. The child runs in Python isolated mode (`-I`) without bytecode emission (`-B`), and inherits `-OO` for the optimized CI pass. The parent outputs only fixed PASS/HOLD strings, never exception text, paths, sample financial data, or child output. A missing/nonregular/linked runner, invalid timeout, child nonzero exit, interruption, or timeout fails closed. The R200 child still enforces the six original R194–R199 selectors with a minimum of 148 cases, no skips or expected failures. This wrapper does **not** turn arbitrary untrusted test Python into a sandbox, and it does not replace the source/evidence provenance gates.

**Both Ubuntu `source-tests` and Windows `windows-build`** use the wrapper for their normal and optimized R194–R199 regression matrices. Both run the 14 new R205 tests in normal and optimized mode before the strict matrix. The Windows job checks every Python exit code.

## Locally executed evidence (2026-11-05 UTC)

- CPython 3.13.5 Linux, local source files byte-for-byte identical to committed GitHub blobs: `python -m unittest discover -s tests -p test_audit_subprocess_privacy_r205.py -v` with `PYTHONPATH=.`: **14/14 PASS**.
- Same 14 cases under `python -OO`: **14/14 PASS**, **28 total method executions**.
- `python -m compileall -q`: PASS.
- Real `subprocess.run` children used for FD1/FD2 `os.write`, `sys.__stderr__`, an inherited grandchild, private exception failure, nonzero exit, real timeout, `-I` Python-path isolation, and valid PASS. Additional synthetic cases cover missing/nonregular/linked runner, invalid timeouts, spawn exception sanitization, and DEVNULL handle contracts.
- Confirmed source blobs: wrapper `9ea0bc99f2631bfa77c6460571efaa2e7e647c75`; 14-test file `07d6b38c05222590c74a3cc4431b5b5fbaee4b59`.
- Workflow edit replaces **four** old R200 direct-command invocations with isolated wrapper commands and adds **two** R205 test steps.

**Fidelity:** These are real Linux child-process tests against exactly committed R205 code and tests, **not** a checkout or execution of the entire private six-engine repository. The inherited R194–R199 148-case matrix, Windows PowerShell/Windows native behavior, six packaged Windows x64 files, malware scanning, accessibility, code signing, premium access control, and the full release gates are still unverified.

## Independent CI / acceptance blockers

The preceding R204 GitHub Actions [run #41992095260](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41992095260) ended in failure on 2026-11-05, with both Ubuntu and Windows jobs reporting **zero available execution steps**; the root infrastructure cause remains **unconfirmed**. The owner needs to inspect the run's Actions banner, billing/usage policy, permissions and runner allocation, then rerun the unchanged R205 HEAD on both operating systems. Capture actual job logs and privately execute the inherited full integration suite and package smoke tests.

**No release authorization:** All six applications remain unreleased. No production changes, public EXEs, payment integrations, or unrestricted premium files. Preserve independent QD review and founder authorization. The next highest-impact task after runners work is to capture complete inherited source-suite results, followed by private Windows 11 x64 build/Defender/checksum/smoke/accessibility acceptance and authenticated premium distribution verification.
