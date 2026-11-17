# R489 — Clean-exit POSIX source-test descendant custody

**Status: DRAFT / INTERNAL / QD HOLD.** Issue #73. Stacked on R488 draft PR #2825, exact base `af2168e4abdc37218ab26cea7616174ade2c7f5e`; not production `main`.

## Risk and fix

R488 isolates the direct test subprocess in a POSIX process session and kills its process group when output overflows, the test times out, or a grandchild keeps stdout open. A test could instead launch a same-process-group grandchild with stdin/stdout/stderr redirected to DEVNULL and then exit cleanly. The parent source gate could return PASS while the unseen grandchild continued touching financial files. This matters even with no network or telemetry because the source gate's tests run on an operator's local checkout.

R489 retains bounded output (1 MiB), fixed-label redacted evidence, closed stdin, strict unittest receipts, and `release_authorized=false`. In the `_bounded_child` finalizer, POSIX source-test process groups are now sent SIGKILL even after the direct parent exits cleanly. Normal, optimized and failed receipts get the same cleanup; the direct exit code and captured evidence are preserved.

**Scope limits:** A child that deliberately calls setsid/creates a detached process group can escape; this is not a sandbox for arbitrary subprocesses or file writes. Windows retains direct-child-only cleanup; this change does **not** provide native Windows descendant containment or count as Windows packaging validation. Never run untrusted financial files or adversarial test code assuming isolation.

## Exact-blob evidence (local Linux CPython 3.13.5)

- Updated runner blob `8648ca806ebd27cf366691831619a762cde731ad`.
- New regression module blob `b47d29dc7f32751d7adbc10b800cf65b15940c83`.
- **5/5** R489 tests PASS normal; **5/5** PASS Python `-OO`, exact committed file bytes, including actual subprocesses and actual unittest discovery.
- Reverting only the new clean-exit cleanup condition produced **4 FAIL / 5 tests** against the same regression file (negative control). The failed cases were normal/optimized successful unittest receipts and successful/invalid direct child receipts; all had quiet grandchildren with a start handshake and a delayed marker.
- Python compile check passed. On Windows, four POSIX-specific cases skip, and the fifth static receipt contract test remains executable. Windows effect is not claimed.
- Complete six-app source suite, inherited R485–R488 regression suite, native Windows executable builds/Defender/accessibility and premium distribution were **not executed in this local run**.
- Source workflow `.github/workflows/desktop-source-evidence-r385.yml` invokes the new regression in normal and `-OO` mode on Ubuntu and Windows; hosted results must be checked independently.

Reproduction on a trusted checkout:

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_offline_source_success_descendant_r489.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_offline_source_success_descendant_r489.py
```

## Release and next gate

Keep both premium downloads private, all executables unpublished, and production/WordPress unchanged. Independent QD review and explicit founder approval remain mandatory. Previously observed R488 hosted source and Windows workflows failed **before any test steps** (four jobs with `steps=null`), not as application-test failures.

**Next highest-impact step:** Repo administrator identifies why hosted runners receive no steps (Actions job annotations, billing/spend limits, permissions, runner availability), reruns the exact-commit workflow after a runner is assigned, then executes the complete six-app regression matrix and verifies native x64 executable smoke, Defender, checksums, accessibility and gated premium delivery. Do not merge or release while these are unverified.
