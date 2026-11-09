# Labs R298 — CSV pathname preflight exception privacy (DRAFT / HARD HOLD)

## Real defect and narrow correction

The shared financial importer fvs_suite.engine.table checked Path(path).is_file() before invoking the hardened read_csv_snapshot. When the filesystem check raised an OSError (or malformed input raised a TypeError or ValueError), the raw exception could include an absolute customer path and escape the otherwise sanitized CSV import boundary. This is separate from the R296 descriptor/snapshot handlers and R297 Unicode/parser error-chain custody.

R298 replaces the unprotected preflight expression with checked_csv_path in fvs_suite.csv_path_privacy. That helper retains the existing extension, existence and regular-file preference, but translates expected construction/probe failures to the existing allowlisted "Select an existing CSV input" error **after leaving the exception handler**. The raised error contains no hidden private __context__ or __cause__. It does not log or inspect file contents. csv_snapshot.read_csv_snapshot remains the authoritative check for descriptor identity, regular-file/symlink restrictions, bounded byte reading and mutation detection. **Preflight is not a security authorization or a lock.**

## Contracts and release boundary

- No financial inputs altered; valid lowercase/uppercase CSV filenames, path-like values, physical row citations, source hashes, exact Decimal lexemes and explicit column mapping remain intact.
- Missing/wrong-extension inputs keep the same stable diagnostic; no raw exception, full path or CSV cell is echoed on preflight failure.
- KeyboardInterrupt, SystemExit and MemoryError still propagate, not silently swallowed.
- Applies through the shared financial importer to LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, GrantAudit Studio Pro and ProcureGuard Studio Pro. Policy Delta Desk's independent policy text reader is untouched.
- Does not relax entitlements, audit trails, human review or QD/founder hold. No executables built or distributed.

## Reproduction and evidence levels

Isolated runnable helper tests with unchanged fvs_suite.csv_diagnostics:

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_csv_path_privacy_r298.py' -v
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_csv_path_privacy_r298.py' -v

**Full checkout required** to run eight new real engine.table integration tests, which must pass on hosted Ubuntu and Windows:

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_csv_path_engine_integration_r298.py' -v
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_csv_path_engine_integration_r298.py' -v

Follow with the existing entire offline regression suite and six-app portable Windows x64 private build/smoke, source SHA-256/checksum, Defender, native accessibility and protected premium entitlement/download verification. R297 Actions #42564847698 failed before recorded steps, so it is not code execution evidence; owner must inspect Actions billing/spend cap, workflow enablement and runner provisioning and rerun the exact new commit. Independent QD review and founder approval remain required before merge, public download or release.
