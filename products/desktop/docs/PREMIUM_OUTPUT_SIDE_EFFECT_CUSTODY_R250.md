# R250 — Premium output side-effect custody and inspection hold

**Issue #73 | feature branch stacked only on R249 | DRAFT | independent QD + founder HOLD**  
Applies to the shared review workbench for **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. The four free utilities, financial matching/Decimal calculations, entitlement validator, and audit evidence formats are unchanged.

## Failure mode and correction

At R249, the export-register, seal-backup and restore-backup Tk callbacks only handled expected `ValueError`, `OSError` and `UnicodeError`. Other exceptions from the underlying code could escape the GUI callback (potentially exposing private path/record diagnostics in a traceback) while the previously loaded exception queue remained selected. Even expected errors might happen *after* an output file or restored folder was created. An error is not proof that the destination is empty.

R250 adds `review_io.perform_custodied_output(action, revoke)`. It validates both callbacks *before* any side effect, requires the existing engines' `Path` return contract, and uses a success-flagged `finally` to revoke the in-memory report/row selection after any unsuccessful action, including unexpected exceptions and `KeyboardInterrupt`/`SystemExit`. The source exception still propagates to the caller; this guard never claims to roll back the filesystem. A broken view-scrub is not silently hidden.

The three Tk output callbacks now run through this guard, retain the existing entitlement checks and pre-operation evidence verification, and catch unexpected `Exception` with constant, non-sensitive dialogs. Expected errors continue to use the existing fixed-text `safe_error_message`. **Both failure paths explicitly direct the operator to inspect the chosen destination before retrying**; after a restore failure, incomplete plaintext may exist. No automatic retry, deletion, upload, audit approval or payment approval is performed. The existing successful-output paths and plaintext-original warnings are preserved.

## Committed source and tests

- `products/desktop/fvs_suite/review_io.py`: shared fail-closed output custody helper.
- `products/desktop/fvs_suite/review_ui.py`: export/backup/restore guarded actions, expected/unexpected redacted dialogs and inspection holds.
- `products/desktop/tests/test_review_output_custody_r250.py`: **15** synthetic helper tests: valid/malformed outputs, callback validation, expected/unexpected error families, interrupts and scrub failures.
- `products/desktop/tests/test_review_ui_output_fault_r250.py`: **12** displayless tests that compile nested callbacks from the *real* GUI source in the checkout. Success, expected error, unexpected error and malformed-return cases for all three output actions. These tests require the full checked-out repository.
- `.github/workflows/desktop-build.yml`: normal and optimized `-OO -W error` executions of both test modules on Ubuntu and Windows, before the existing full suite and packaging gates.

## Actual reproducible local evidence and limits

Linux CPython local isolated reconstruction: the 15 pure helper regression methods ran **15/15 PASS** with `python -W error -m unittest discover -s tests -p 'test_review_output_custody_r250.py'` and **15/15 PASS** with `python -OO -W error ...`; **30 focused test executions**, zero skips; `compileall` PASS. Exact helper and test bytes verified against GitHub blobs using `git hash-object`: helper `b2444b209ad3820f16c7a1b57f0d2ed3e907fd5c`; test `bef989830af85379e64a6131f40d6654485641fa`. GUI source integration was statically inspected in GitHub, and the 12 GUI tests were committed, but **the complete repository and real Tk source were not executable in the local container**. Those 12 GUI tests, full inherited regression, Ubuntu/Windows hosted runs, native Windows GUI, and all six EXE builds remain **unverified**.

No public or premium executable is released, no premium URL was published, and no production/main branch was changed.

## QD / native Windows requirements

1. Restore GitHub Actions runner execution (previous runs failed with zero job steps; root cause not confirmed) and run the unchanged R250 SHA on Ubuntu and Windows, including 15 + 12 R250 methods in normal and optimized modes and full source/engine gates.
2. In a native Windows 11 x64 Tk workbench with **synthetic, authorized premium** evidence, inject post-write exceptions and malformed engine returns separately into export, backup and restore; verify the visible queue and source path clear, raw customer paths never appear in dialogs/console, and the chosen destination is manually inspected before any retry.
3. Confirm permission-denied/corrupted-archive flows preserve original files; ensure an expired entitlement blocks side effects even after modal pickers. Complete keyboard, NVDA and high-DPI checks.
4. Only after independent QD and founder signoff: build the six executables privately, verify hashes, malware/SmartScreen results, launch/smoke tests, and protected premium distribution. Do **not** merge or publish this draft as a release.

**Next high-impact engineering action:** trusted full-source normal/-OO integration on working GitHub runners and native Windows 11 GUI acceptance; it is not enough to have isolated Linux helper tests.
