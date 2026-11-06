# Labs R228 — Win32 high-resolution wheel accumulation (DRAFT / QD HOLD)

Issue: #73. Parent: R227 draft PR #1218 at `4e97fce1a5f822dd60c4a7ff0ad25f61ab24c184`. Feature branch: `feature/labs-r228-win32-precision-wheel-20261106`. Not production `main`.

## Practical problem and change

All six Windows x64 Tk utility front ends use the same `ScrollableForm`. R227 scrolls the common viewport correctly for ordinary 120-unit Windows wheel events, but interpreted each partial wheel delta (e.g. four -30 events from a precision device) as a separate full notch. That over-amplifies high-resolution wheel input fourfold. R228 introduces `precise_windows_wheel_units(delta, remainder)` and a **per-form** signed residual for the Win32 Tk backend.

* Four same-direction 30-unit events trigger one 3-unit Tk scroll, not four.
* Reversed partial motion cancels before scrolling. A single event is capped at four notches/12 Tk units, with only the fractional residual retained; arbitrary hostile native primitives are rejected before any conversion hooks run.
* A separate Tk dialog cannot scroll or change the parent viewport's accumulated state. Non-scrollable forms do not accumulate wheel movement.
* Complete +/-120-unit wheel notches retain the R227 behavior, including immediate +/-3-unit scrolling. X11 Button-4/5 and macOS/Aqua wheel events retain the existing R227 path, so low-delta Mac events are not suppressed.
* Inherited R227 tests construct a synthetic form via `__new__`. An explicit compatibility guard preserves those legacy synthetic invocations without altering real Win32 initialization.
* No input path, text entry value, customer ledger, report, entitlement, or financial callback is read. No network traffic or telemetry. The two premium programs remain entitlement-gated; human compliance review is unchanged.

## Test evidence and limits

Executed on **Linux CPython 3.13.5** in an isolated source-extracted harness with exactly matching Git blob SHA-1 values:

| Artifact | Verified blob |
| --- | --- |
| `fvs_suite/scroll_access.py` | `7c0b322edc50374b0cc0acf75283bd3eb65850a7` |
| `tests/test_precision_wheel_r228.py` | `a4185a44ec1b22877902a4c8b8e45577212c25dc` |
| `scripts/native_precision_wheel_r228.py` | `390415b485579b84c2363cd88a29e764bc9281fc` |

* `python -W error -m unittest discover -s products/desktop/tests -p 'test_precision_wheel_r228.py'`: **17/17 PASS** (isolated harness with matching Python import path).
* `python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_precision_wheel_r228.py'`: **17/17 PASS**.
* `xvfb-run -a python -W error products/desktop/scripts/native_precision_wheel_r228.py`: **PASS**; the first three -30 events do not move the real Tk viewport, the fourth does, and dialog wheel input has no parent effect.
* Optimized `-OO` native Xvfb test: **PASS**.
* Both hosted CI jobs now enforce the exact 17-test file in normal and optimized Python; Ubuntu additionally enforces actual native Tk/Xvfb event delivery in both modes.

**Not proven:** The repository-wide inherited suite has not been run locally against the whole private repo. Host GitHub Actions may still fail before any steps. Xvfb simulates Win32 wheel deltas inside a real Linux Tk event loop; it is **not** a physical Windows precision-touchpad or 100/200/400% DPI acceptance test. No Windows x64 PE, Defender/EDR, Authenticode signing, QD/founder approval or public binary availability is claimed.

## Next acceptance gate

Restore hosted runner execution and run unchanged R228 head in Ubuntu + Windows. Then inspect all six actual Windows 11 Tk interfaces with a physical precision wheel/touchpad at 100%, 200% and 400% scale, keyboard and NVDA accessibility, followed by private six-EXE build, PE/SHA-256 checks, malware scan, and protected premium distribution verification. Independent QD and founder sign-off are mandatory before any merge/publication.
