# Final Vestige Labs R237 — private CSV publication and FD custody

**Issue #73 · DRAFT / independent QD + founder HARD HOLD · all six Windows x64 applications UNRELEASED**

## Problem and scope

The shared `atomic_reports.write_csv_report` CSV export path is used by the offline financial suite. On the R236 parent it staged a file before checking whether the final destination was already occupied; raw OS exceptions from `mkstemp`, `fdopen`, `fsync` and exclusive publication could expose customer-selected report paths. If `os.fdopen` failed before taking ownership of the `mkstemp` descriptor, the staging directory entry was removed but the raw descriptor remained open. These are data-custody and resource-exhaustion risks, not changes to financial matching behavior.

## Proposed change — source-only, no downloads

- `fvs_suite/csv_publish_guard.py`: `require_free_destination` checks occupied files, directories and dangling symlinks *before* staging. This early check cannot prevent a race, so the existing exclusive POSIX hardlink / Windows non-replacing rename remains mandatory.
- `adopt_csv_descriptor` closes the original `mkstemp` FD even if `fdopen` raises or interrupts before ownership transfer.
- `raise_private_csv_failure` maps OS failures to fixed-text errors (preserving positive native errno, and FileExistsError class), removing filename fields and the original OS message from the usual display/traceback.
- The existing CSV writer is retained as `_write_csv_report`; its public `write_csv_report` wrapper protects its OS-error boundary. Original CSV UTF-8-BOM serialization, SHA-256 staged-byte witness, 64 MiB export cap, formula checks, exact money semantics, row provenance and exclusive publication are unchanged.

**Important privacy limitation:** `raise ... from None` hides usual traceback context, but hostile code can deliberately inspect Python `__context__`; never recursively log original exception objects. This change is not disk encryption, a digital signature, an all-files atomic transaction, or legal/compliance approval.

## Actual verification evidence

2026-11-06: exact Git-blob-matched `csv_publish_guard.py` and `test_csv_publish_guard_r237.py` executed against a locally created mini-package containing those exact files, on Linux native filesystem, with **14/14 PASS standard Python and 14/14 PASS Python -OO** (= 28 method executions), zero skips, `-W error`. `compileall` also passed for those files. The tests use real `mkstemp` FDs, `fdopen` failures and interruption, Unicode BOM evidence, dangling symlinks, existing targets, sanitized errno/path failures. This is **NOT a full repository checkout**: the updated full `atomic_reports.py` integration, seven added end-to-end integration cases, all inherited source/financial-engine tests, and Windows 11 acceptance are **not locally verified**.

New required regression commands, from a complete repository checkout:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_csv_publish_guard_r237.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_csv_publish_guard_r237.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_csv_publication_integration_r237.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_csv_publication_integration_r237.py'
```

Both Ubuntu source-tests and Windows pre-packaging CI now run these four commands, in addition to the inherited mandatory gates. The separate seven-case integration suite covers real final report/BOM, pre-stage collision, dangling symlink, failed `fdopen` descriptor cleanup, `fsync` and `mkstemp` privacy, and a concurrent destination collision. **Do not count those seven cases as passed** until complete checkout CI or local integration executes.

## QD/release holds and next step

Stack this draft only on R236 at exact `31c8cce241d23e8e08d5ef6f091a7f54b375dd1f`; never main. The R236 Actions run #42248796962 had Ubuntu and Windows failures with zero recorded steps; runner/account cause not yet confirmed. Owner should inspect the top-level failed-run banner, billing/spend limits, workflow policy and runner provisioning; restore scheduling and re-run an unchanged R237 SHA.

Then execute the **entire inherited six-app regression suite on Ubuntu and Windows**, Windows 11 native tests (GUI, paths, offline operation, DPI/NVDA), private six-executable packaging and SHA256, malware scans, deterministic export/Decimal acceptance, and premium-gated transfer. Independent QD review and explicit founder approval are required before merge, site publication, or any release. Neither public nor premium binaries were produced.
