# Final Vestige Labs R286 — atomic single-flight custody (DRAFT / QD HOLD)

**Issue:** #73. **Base:** immutable R285 commit `89496ff51c7a955af058c4e2425d8e3188971fe0`. All six Windows x64 utilities remain unreleased; no production change or public/premium binary distribution.

## Failure mode actually reproduced

The R285 per-window `ActionGate` used `if self._active: return False` followed by `self._active = True`. This check-then-set protects nested synchronous Tk events, but it is **not atomic across worker threads**. Under a deliberately synchronized two-thread read of the original flag, *both* commands can enter while the window is supposed to be single-flight. This can create competing report or Review operations if future asynchronous integration calls the same gate.

R286 replaces check-then-set admission with a per-window `threading.Lock` acquired **nonblocking** for the complete command. A second caller returns `False` immediately: no blocking queue, no delayed export, no review authorization, no global cross-window lock. The existing `_active` diagnostic flag is preserved, but it is no longer the admission authority. The lock is released in `finally` even when a callback raises. Tk controls themselves must still be used on the Tk owner thread; this change does not authorize background Tk widget access.

## Local evidence (Linux Python 3.13.5)

- Added `tests/test_action_gate_threads_r286.py`: **18 methods** across all **6 named app configurations** (4 free, 2 premium). Standard `python -W error -m unittest ...`: **18/18 PASS**. Optimized `python -OO -W error -m unittest ...`: **18/18 PASS**. Total **36/36 new focused executions**.
- **Negative control:** run unchanged R285 `action_gate.py` (Git blob `d654d60da5791002a7bcb71877babbe7c55e74f1`) against the R286 suite: **6/18 fail**, precisely the six forced check-then-set races. The R286 implementation returns **18/18 passing** in each Python mode.
- Prior R285 native Tk behavior was additionally checked with a local reconstruction of its 24-method source test under Xvfb: **24/24 normal, 24/24 -OO PASS**. That reconstruction is **not byte-identical** to the upstream R285 test file; count as supplementary compatibility evidence, not a complete upstream regression pass.
- `python -m py_compile` for the changed helper and the new test: **PASS**.
- Synthetic callbacks only: no financial data, real ledger output, approval, network use, packaged executable, Defender scan, or premium license assertions.
- Git SHA-1 blobs for the locally executed new implementation/test are recorded in the PR; compare against the committed Git blobs before treating them as identical artifacts.

## CI gates and release constraints

`.github/workflows/desktop-build.yml` adds normal and `-OO` tests in both Ubuntu source-tests and native Windows jobs. Hosted jobs can still fail before runner assignment; a workflow definition is **not** evidence that they ran.

**Required independent acceptance:** Restore GitHub Actions execution; run complete inherited desktop regression suite (including R285/R286), then trusted Windows 11 x64 native builds of all six programs; collect real EXE smoke outputs, SHA-256 hashes and nonremediating Defender results; verify physical keyboard/screen-reader accessibility and protected premium distribution. Preserve mandatory QD review plus founder approval prior to merge or publication. Do not expose signing keys or premium payloads.
