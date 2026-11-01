# Labs R98 - privacy-safe failing source-suite triage

Issue #73. This source-only change is stacked on R97 draft PR #381 and is NOT a release approval.

## Why it matters

On 2026-11-01 both hosted runners actually executed, but the complete normal/-OO source suite exited nonzero before Windows packaging. Its privacy-safe gate suppresses individual errors. R98 makes failures actionable without showing financial fixtures, customer paths, private assertions, exception text, stack traces, dynamic subtest values or source documents.

When a source-test module fails, the runner emits exactly one short FVS_TEST_DIAG: JSON stdout line and still exits NONZERO. The parent revalidates and reserializes it, then prints the safe marker followed by the ORIGINAL generic rejection. The marker is restricted to fixed phase (discovery/execution), bounded error and failure counts, a maximum of 12 sorted unique source-controlled test module basenames matching test_[a-z0-9_]{1,90}, omitted module count, and a fixed schema. All other child output is discarded. Child stderr STILL routes to DEVNULL. Success manifests and exact normal/-OO parity checks stay unchanged; all six synthetic engine smokes remain required.

This diagnostic is not itself source test success. It does not authorize Windows packaging, premium distribution, QD review or founder launch approval.

## Verification and operator next step

New regression file test_private_suite_diagnostics_r98.py exercises real synthetic failed tests (normal and -OO), discovery errors, subtest-data redaction, malformed and forged stdout, schema bounds and strict test-module names, parent stderr suppression, unchanged successful provenance and failure propagation. Isolated equivalent helper preflight passed 10/10 normal and 10/10 -OO under Linux Python. The committed full repository regression needs hosted CI.

Read the first FVS_TEST_DIAG: marker in the next failed Actions source gate. Reproduce any listed module privately in a trusted full checkout with PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v, and repeat with python -OO. Only synthetic fixtures and code-owned names belong in CI logs.

Four free and two premium apps remain unreleased. No Windows EXEs, unprotected premium downloads, payment links, production merge or WordPress writes. Independent QD/founder approval remains mandatory.
