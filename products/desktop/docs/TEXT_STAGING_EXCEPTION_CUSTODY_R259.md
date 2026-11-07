# R259 — private text/manifest staging error custody

**Issue:** #73. **State:** DRAFT, unmerged, independent QD + founder HARD HOLD.  
**Branch:** `feature/labs-r259-atomic-text-stage-privacy-20261107`.  
**Base:** immutable R258 draft PR #1420 head `6309911bc452f5cff353b4795a174eb227b7af47`, **not production `main`**.  
**Scope:** `products/desktop/fvs_suite/atomic_text.py` and `test_atomic_text_stage_custody_r259.py`; zero live, financial arithmetic, license, or marketing changes.

## Defect and source change

The shared offline `publish_text` pathway stages TXT and manifest evidence using `tempfile.mkstemp`, then `os.fdopen`. Although it already released the raw descriptor on every `fdopen` exception and redacted **OSError** failures, unexpected ordinary `RuntimeError`, `TypeError`, `ValueError`, or `AssertionError` could propagate diagnostics containing private customer filesystem paths. `mkstemp` could expose analogous private error strings. This is a local privacy / failure-diagnostics gap, not a claim of remote exploitation.

The fix sanitizes unexpected ordinary staging-creation errors to `ValueError("Text report staging could not be created")`, and stream-adoption failures to `ValueError("Text report staging could not be opened")`, suppressing ordinary traceback context. If the stream did not adopt the raw descriptor, it is closed before re-raising or translating the exception. Native `OSError` / errno redaction is **preserved** by the preexisting outer translator, and fatal exceptions (`KeyboardInterrupt`, `SystemExit`, `MemoryError`) propagate without being mistaken for successful evidence publication. No retries, deletes of originals, telemetry, or automatic compliance decisions were introduced.

## Reproducible local evidence (2026-11-07 UTC)

Linux CPython **3.13.5**, synthetic temporary TXT only; the full source module was copied exactly from R258 GitHub blob `805f5a5bfa9c9c0024edca5b300b53633c846c62` before the patch (verified with `git hash-object`). The 18 new methods exercise **real OS descriptors** while mocking only `fdopen` / `mkstemp` failure boundaries; they additionally cover empty output directories, destination nonoverwrite, UTF-8 byte fidelity, strict interrupt propagation, and redacted errno preservation.

- **Before fix:** 18-method suite: **3 failures, 4 errors, 11 passes**. Reproduced path-bearing non-OS exceptions.
- **After fix:** 18/18 new tests + 12/12 inherited R233 privacy tests + 17/17 inherited R235 staged-byte tests = **47/47 normal and 47/47 `-OO -W error`, 94 passing method executions, zero skips**; Python `compileall` PASS. Inherited test Git blobs copied byte-for-byte from R258 and hash-verified: R233 `f34025755a4899792d2d9dcab150b7d8e25dc18b`; R235 `ff2f342e62199a8e93f8899162fd6e859b03d1b0`.
- **Committed-source Git blob verification:** patched `atomic_text.py` = `5cfd400417d7f0d4231f6ad2f0fa0cd91323b693`; new test = `748c0527995bbf862fe3d05e68f4a1931764ed8c`. Both match the exact locally tested contents.
- No real customer data used or accessed.

Commands from `products/desktop`:

```sh
python -W error -m unittest discover -s tests -p 'test_atomic_text_stage_custody_r259.py'
python -OO -W error -m unittest discover -s tests -p 'test_atomic_text_stage_custody_r259.py'
# The following two-mode wildcard also exercises inherited R233 + R235.
python -W error -m unittest discover -s tests -p 'test_atomic_text*.py'
python -OO -W error -m unittest discover -s tests -p 'test_atomic_text*.py'
python -m compileall -q fvs_suite/atomic_text.py tests/test_atomic_text_stage_custody_r259.py
```

The existing two-mode `scripts/offline_source_gate.py` discovers `test_*.py`; therefore this regression will participate in its full suite when the repository/hosted runner is available. The **full repository suite was not executed in this isolated local workspace**. The focused inherited R233 privacy and R235 exact-byte suites were executed against the patched Git-blob-identical implementation; these 29 inherited methods give direct compatibility evidence but do not establish complete integration.

## CI/release hard hold and next decisive step

Prior R258 GitHub Actions run [#42379751167](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42379751167) reported `source-tests` and `windows-build` completed failure with **no steps and no runner logs**; precise cause undetermined. Confirm the R259 run separately after PR creation. Smallest owner action is to inspect GitHub Actions usage/billing limits, repository workflow permissions and runner provisioning, restore hosted execution, then rerun the **unchanged R259 SHA**.

Next: run the full source gate (normal + `-OO`, all six engine smokes), native Windows 11 x64 tests and private builds, SHA-256 checksums, malware scan, keyboard/NVDA checks, and authorized premium-download/license verification. No executable or live-site publication until QD and founder explicitly approve.

**All six applications are UNRELEASED.** This memo is engineering verification only, never a release authorization.
