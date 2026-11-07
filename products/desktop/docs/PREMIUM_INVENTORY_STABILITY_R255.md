# R255 — Premium inventory verification stability and Windows descriptor compatibility

**Scope:** issue #73; GrantAudit Studio Pro and ProcureGuard Studio Pro only. Stacked on immutable R254 head `638f0d0d47fde7a32029df453e7eb2547fb6ea14`, not `main`. **DRAFT; independent QD and founder release hard hold.**

## Risk and fix

R254 compared manifest `Path.lstat()` and opened descriptor `os.fstat()` using the complete `st_ctime_ns` value. On Windows, these independent API views can disagree about creation time for the same file, giving a false failure for an otherwise valid evidence package. The existing `csv_snapshot._same_path_descriptor_signature` explicitly handles this: cross-view comparisons omit ctime **only on Windows**, while pathname-to-pathname and descriptor-to-descriptor snapshots continue to enforce the complete signature, including ctime.

R254 also read the manifest once, then hashed up to 256 MiB per report. A report or manifest edited after its initial check, or an unexpected file added after the directory scan, could survive the original point-in-time sequence.

R255 changes only `fvs_suite/premium_manifest_completion.py`:

1. Reuses the existing Windows-aware descriptor/path comparison on manifest open and final recheck, with unchanged bounded 128 KiB manifest reads and strict non-symlink regular-file validation.
2. Retains each report's returned **real descriptor-safe** hash snapshot; after every report hash, rereads the manifest and requires identical contents, rechecks all report pathname signatures, and rescans the package directory.
3. Fails closed on late changes without altering, deleting, uploading, logging, automatically approving, or retrying evidence. These are point-in-time checks, **not locks**, tamper-proof signatures, source revalidation, or compliance decisions.

No change to free app engines, money/Decimal logic, premium entitlement flow, encrypted evidence, historical journals, or the site's release workflow.

## Reproducible focused verification (2026-11-07 UTC)

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_premium_inventory_stability_r255.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_premium_inventory_stability_r255.py' -v
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_premium_manifest_completion_r254.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_premium_manifest_completion_r254.py' -v
```

A local isolated Linux CPython 3.13.5 workspace assembled the **exact Git blob contents** of `premium_manifest_completion.py`, `manifest_guard.py`, `csv_snapshot.py`, inherited `test_premium_manifest_completion_r254.py`, and new `test_premium_inventory_stability_r255.py`. The four dependency/test blob SHAs match the GitHub source at R254/R255; after committing R255, source/test Git blob identities were checked against GitHub. Only the small `__init__.py` package marker was locally synthesized; there is **no mocked hashing dependency** in this run. Synthetic local files only; no customer data.

**Actual local result:** 16 new + 13 inherited = **29/29 PASS normal and 29/29 PASS -OO**, 58 successful executions, 0 skips. Compileall passed. New regressions cover stable Grant/Procurement (with optional policy), read-only success, manifest edit/deletion/symlink during hash, earlier report edit/deletion during later hash, unexpected files/folders appearing late, wrong report/product rejection, and synthetic Windows vs POSIX cross-view ctime behavior. The Windows ctime case is simulated, **not tested on Windows**.

## Still blocked / mandatory gate

The complete repository source suite, inherited GUI integration, true native Windows 11 x64 descriptor behavior, six portable EXEs, smoke tests, Windows Defender/EDR, signed artifacts, screen-reader/keyboard acceptance, checksum records, protected premium distribution and QD/founder approval are **not verified**.

GitHub Actions R254 run [#42362298928](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42362298928) showed Ubuntu and Windows jobs failing with no steps/logs; infrastructure root cause remains unconfirmed. Owner's smallest action: check GitHub Actions billing/spending/runner availability and permissions, restore execution, then rerun R255's unchanged head. The pre-existing `offline_source_gate.py` full normal/optimized suite remains the CI gate for both platforms.

**QD review requested:** scrutinize Windows path/descriptor metadata, file replacement races outside the bounded snapshot interval, error privacy and compatible publisher output. **Do not merge, deploy to WordPress, release EXEs, claim availability, or expose premium files.**