# R258 — CSV import descriptor custody and privacy-safe adoption (draft/QD hard hold)

Issue: #73. Branch: `feature/labs-r258-csv-snapshot-fd-adoption-20261107`, stacked exclusively on R257 draft PR #1414 (parent `73748d89df098e5fb23b0d0719406e7d6f1dfe86`); **not main**.

## Defect reproduced

The six-app suite's `fvs_suite.csv_snapshot.read_csv_snapshot` opens an input descriptor with `os.open` and then adopts it using `os.fdopen`. Before R258, its adoption exception handler handled only `OSError`. Other adoption failures left the descriptor open and ordinary unexpected exceptions exposed text from private source paths. A failed `os.open` with a non-`OSError` could also reveal paths. This is a local process resource/privacy safeguard, not a claim of a remotely exploitable vulnerability.

## Scope of change

- On **any** `os.fdopen` failure including `KeyboardInterrupt`, `SystemExit`, `MemoryError`, `GeneratorExit`, close the raw descriptor, preserving the original nonroutine interrupt/fatal exception.
- On ordinary `fdopen` failures, surface a fixed `ValueError("Cannot read CSV input")` without private path data. On ordinary `os.open` failure, surface a fixed `ValueError("Cannot safely open CSV input")`.
- Preserve exact CSV source bytes and provenance, the existing import size boundary, non-following open, metadata race checks, and the R30 public error contract. No engine arithmetic, Decimal precision, entitlement, upload, telemetry, source deletion, or compliance-approval change.

## Local reproducible evidence (2026-11-07 UTC)

Linux CPython 3.13, synthetic temporary CSV only. The unmodified R257 source and inherited R30 tests were copied byte-for-byte from GitHub and verified by `git hash-object` against GitHub blob IDs:
- Original `csv_snapshot.py` = `108f330c46c536debff0b0303c5f7dc8f8c3f88d`
- Inherited `test_csv_snapshot_r30.py` = `db7e752fb04ef6a2419f22898c258f7732779042`

Pre-fix execution of **15 new tests** reproduced **4 failures and 3 errors**; 8 passed. Failing conditions included leaked open descriptors under interrupts, leaked descriptor + private path under `RuntimeError`/`TypeError`, and raw private path disclosure from unexpected `os.open` error. After the fix, the two actual files plus 15 new regressions gave:
```sh
cd products/desktop
python -W error -m unittest discover -s tests -p 'test_csv_*r*.py'
python -OO -W error -m unittest discover -s tests -p 'test_csv_*r*.py'
python -m compileall -q fvs_suite/csv_snapshot.py tests/test_csv_descriptor_custody_r258.py tests/test_csv_snapshot_r30.py
```
**29/29 normal PASS + 29/29 optimized PASS = 58 focused test-method executions, 0 skips; compilation PASS.** Hashes of locally tested patched files: source `08c08598ac3575e3baf53ee3275db9aadc315f4d`, new tests `d2a4dbc4223be680531bb167f246d8c1be57356f`. The existing 14 R30 tests remain green. Tests use real OS descriptors and temporary files, not a mock of the snapshot implementation.

## Remaining release gates

The full repository, all six connected GUI/engine integration paths, native Windows 11 x64, actual EXE packaging, accessibility, Defender/EDR, signing/checksums and protected premium download are **not verified** by this local subset. GitHub Actions R257 #42375240861: Ubuntu and Windows jobs failed before recording any steps/logs; cause unconfirmed. Verify R258 hosted CI independently after writing the branch and PR. Owner should check GitHub Actions billing/usage limits, workflow permissions and runner provisioning, then rerun unchanged R258 SHA and supply execution logs.

**All six desktop apps UNRELEASED.** This draft may not be merged, released, placed on the live WordPress site, or offered as an unrestricted premium download without independent QD and founder approval. Next: complete normal/-OO entire source suite, Windows 11 private six-EXE build/smoke, inventory SHA256, AV, keyboard/NVDA, and paywall/license-gated delivery.
