# R450 — Six-app CSV publisher exception-chain privacy

**Draft / NOT authorized for release.** Issue #73. Strict parent: R449 draft PR #2616, pinned commit 48fba59e64b8e2897c94e53391ce87877e826e3a. No edits to production main.

## Defect and pre-fix reproduction

All six local-first utilities use the shared CSV publication boundary. On a filesystem report failure, the publisher caught an OSError and invoked its sanitizer while the original handler was still active. Even with `raise ... from None`, a client pathname in the original OS diagnostic could be recovered through the public exception's `__context__`. The staged-byte integrity verifier had the same behavior on filesystem read errors. A controlled synthetic pre-fix example reproduced the hidden private context.

## Concrete change

- `csv_publish_guard.private_csv_failure()` now **returns** a fixed diagnostic object; it does not raise beneath an active private handler.
- `atomic_reports.write_csv_report()` raises that fixed error after exiting the handler. Native errno, existing destination collision, no-overwrite guarantees and deterministic financial export semantics remain.
- `csv_stage_integrity.CSVStagingWitness.verify()` raises its fixed failure only after leaving the handler; actual SHA-256 and exact serialized-length checks remain unchanged.
- No original source file, report money, SHA value, compliance conclusion or approval is rewritten or uploaded.

## Evidence and limitations

On a locally reconstructed **targeted three-module projection**, the same R450 test source passed 12/12 standard and 12/12 Python `-OO -W error` (24 focused executions). The stage witness tests use actual synthetic local temporary files. The publisher wrapper was tested with a stand-in for full `_write_csv_report`; the two helpers were reconstructed from the proposed source. Python compileall passed. This is **not** complete-repository compatibility or native Windows validation.

Full checkout commands (required before merge):

    PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_csv_private_context_r450.py
    PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_csv_private_context_r450.py

Parent R449 GitHub Actions source [#43711559262](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43711559262) and Windows build [#43711559258](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43711559258) both failed before recorded steps. Runner root cause is **unconfirmed**; there was one check annotation per job, unavailable through the present connector.

**Next highest-impact step:** inspect GitHub Actions failure banners/annotations, account spending limits, enabled hosted-runner policies and workflow permissions. Restore runner assignment; run R450, inherited writer/stage regressions and all six engine suites in Linux and Windows; then run genuine Windows x64 packaging, smoke, accessibility, Defender, hash and access-controlled premium distribution checks.

**Hard release hold:** no binaries, licenses, payment flows, publicly accessible premium files, fabricated download URLs, WordPress changes or production merges. Independent QD approval and explicit founder approval remain mandatory. `release_authorized=false`.
