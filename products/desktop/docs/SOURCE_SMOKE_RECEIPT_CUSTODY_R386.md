# R386 — Six-engine source-smoke output receipt custody (ISSUE #73)

**Status:** DRAFT / HARD HOLD. Stacked on R385 #2243; not on production main. No executable, release URL, public download, private license key, payment action, or WordPress publication is authorized. QD and founder reviews remain mandatory.

## Defect and severity

Prior to R386, source_smoke_gate.verify_smokes() trusted truthiness of the returned value, then converted any iterable to Path values. An empty generator is truthy, so it became an empty list and yielded a PASS source-smoke record with synthetic_output_count=0. A plain string could be split into character filenames; duplicate paths could inflate the count. Such a record is not proof that the source engine produced any report. The separate R276 receipt parser already rejects zero counts, but this earlier gate could still mark an app PASS; the producer and consumer must independently fail closed.

## Changes

- scripts/smoke_result_custody_r386.py: accept only a native Python list, 1–32 distinct native Path basename references, ASCII-safe and free of traversal, drive letters, alternate data streams, control characters, and forged subclasses. Use fixed privacy-safe failures, no coercion, iteration of unknown values, network, or subprocess.
- scripts/source_smoke_gate.py: validate each of all six synthetic engine result lists before adding a PASS row. Preserve the real smoke engine's own temporary-file integrity and content checks, and the source inventory's before-and-after SHA-256 checks.
- tests/test_smoke_result_custody_r386.py: 18 focused cases, including empty/populated generators, strings, list and Path subclasses, duplicates, cross-platform paths, cap, and private exception text.
- .github/workflows/desktop-source-evidence-r385.yml: run the new tests in normal and -OO Python on both Ubuntu and Windows before the six actual engine smoke passes. No new credentials, artifact publishing, approvals, or privilege elevation.

## Local evidence and limits (2026-11-12)

Exact byte-identical helper blob 939eb0ec39920f98b55413e8c5ab95c2306476cd and test blob 7b1d2d48c5174500f385004eb9a71f1b37525a93 were executed from a local isolated Python 3.13.5 copy:

- PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_smoke_result_custody_r386.py: **18/18 PASS**.
- Same invocation with python -OO -W error: **18/18 PASS**.
- Total: **36/36 focused executions**, tests only. No full repository checkout, old regression integration, native Windows smoke, EXE inspection, Defender scan, or QD run executed locally.

Hosted CI inherited the known runner-allocation blocker from R385. Runs #43297199259 and #43297199124 had failed with runner_id=0, steps=[] on both Windows and Ubuntu. Do not infer the same outcome for R386 without checking its own run.

## Next required action

1. Inspect failed Actions check annotations, billing/spending limits, hosted-runner eligibility, and repository Actions configuration; confirm the cause and restore a runner.
2. Re-run the exact R386 PR HEAD: R386 tests + existing R21/R42/R276 integrity and source smoke tests, full six-engine financial/Decimal cases, genuine 22 AES-GCM cases, offline Ed25519 and SQLite licensing on both platforms.
3. Only after all source and CI gates pass, build six distinct native Windows x64 EXEs and complete installs, Defender scans, keyboard/screen-reader acceptance, hashes, premium entitlement distribution control, QD review and founder signoff.

**Interpretation:** This is stronger source-only receipt integrity. It is not a claim of shipped apps or proof of genuine Windows runtime behavior.
