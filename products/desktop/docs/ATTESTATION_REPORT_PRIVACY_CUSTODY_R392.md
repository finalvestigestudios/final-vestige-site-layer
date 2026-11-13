# R392 — Offline release-attestation report privacy and ancestry custody

**Status: DRAFT only. HARD HOLD on every Windows x64 executable, free and premium.**
**Base:** R391 draft PR #2281, *not* main.
**Scope:** report_attestation.py (read-only retained candidate report verifier); no financial rules, licensing, production website, or distribution edits.

## Reproduced defect and correction

The previous _validate_report exception translation used 'raise ReportAttestationError(...) from None' *inside* JSON/UTF-8 and timestamp exception handlers. Python suppresses their printed traceback, but retains the originating exception object in __context__. For malformed JSON, JSONDecodeError.doc can retain the complete private JSON source. An isolated Python 3.13.5 reproduction with a synthetic PRIVATE_ACCOUNT marker confirmed the old chain still contained the marker; translating outside the handler yielded __context__ is None.

The report verifier now:
1. Translates malformed JSON, Unicode and invalid calendar timestamp errors **after leaving** their exception handlers, so its public error does not retain lower-level private payloads in __cause__ / __context__.
2. Translates lower-level file, directory and candidate-gate exceptions outside their handlers, with generic, private-path-free messages. Intentional validation errors retain established fail-closed semantics.
3. Rejects a retained report when any lexical parent is an unsafe symlink / Windows reparse junction or when a parent changes during reading; rejects reparse metadata on the report path and descriptor.
4. Closes the raw file descriptor if os.fdopen fails before accepting ownership, including on system interruption.
5. Continues bounded 64-KiB ordinary-file reads, SHA-256 report fingerprints, same-view pre/post file identity checks, exact six-product report schema, and **all authorization flags false**.

There is no telemetry, no upload, and no change to the standalone engines Decimal logic, provenance, human-review rules, AES-GCM, Ed25519 or premium entitlements. Symlinked aliases that previously worked as paths to a valid external report will now intentionally fail; use a real canonical directory.

## Files

- products/desktop/report_attestation.py
- products/desktop/tests/test_report_attestation_custody_r392.py (28 authored methods: 26 portable, 2 native Windows junction-only)
- .github/workflows/desktop-source-evidence-r385.yml (both Ubuntu and Windows normal / -OO test commands)
- This review record

## Local evidence and limitations

On isolated Linux Python **3.13.5**, a reconstruction of the changed attestation reader/parser and helpers passed **26/26 focused tests normally and 26/26 with python -OO -W error** (52 executions), with source compilation succeeding. The earlier decoder behavior was independently reproduced: JSONDecodeError remained accessible as __context__, and its .doc retained the synthetic private marker; the patched construction did not.

**Qualification:** this isolated test harness contains reconstructed copies and stubs, **not** the exact checked-out committed repository. The actual 28-method committed test module, inherited integration suite, hosted Ubuntu/Windows runners, and the **two native NTFS-junction tests** have **not** been executed here. The Windows-only tests do not silently skip on a Windows runner if junction fixture creation fails: they fail closed. No real Windows binary, Defender/EDR scan, signing, installed GUI accessibility checks, or premium download controls were validated.

## CI gate and release blockers

The independent source-evidence workflow now calls:
- python -W error -m unittest discover -s products/desktop/tests -p test_report_attestation_custody_r392.py
- python -OO -W error -m unittest discover -s products/desktop/tests -p test_report_attestation_custody_r392.py

Both run inside the existing Ubuntu 24.04 / Windows-latest matrix; the two junction tests execute only on real Windows. Full six-engine smokes, Decimal/provenance, 22 AES-GCM, genuine Ed25519/SQLite and required review checks remain downstream.

On recent R391 exact-commit CI (source #43349503951 and desktop #43349504024), all jobs failed **before a runner executed a step**. These failures are not evidence of code-test pass or fail. Root cause is not established. Owner should inspect GitHub Actions failed-check annotations, spending/billing limits and hosted-runner eligibility, then rerun the **exact R392 commit** once capacity is restored.

## Next highest-impact step

Recover hosted Ubuntu/Windows CI, run the exact 28-test module and inherited complete six-product source suite on this commit; inspect native NTFS-junction and handle-ownership behavior on Windows. Then proceed with six distinct native x64 EXE production *candidates*, genuine Defender/EDR, 46-observation accessibility review, signed-release plan, protected premium entitlement/download distribution, independent QD and explicit founder approval.

**No executable has been accepted, published or licensed by this change.**
