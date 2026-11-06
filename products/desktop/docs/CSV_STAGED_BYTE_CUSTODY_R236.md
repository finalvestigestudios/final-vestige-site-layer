# Labs R236 — bounded byte-exact CSV report custody

**Status: DRAFT / independent QD and founder HARD HOLD. Issue #73. All six Windows x64 applications remain UNRELEASED.**

## Defect and impact

The common CSV publisher, fvs_suite.atomic_reports.write_csv_report, supports financial exports throughout the six-app suite. Before R236, its _BudgetedCSVTextSink.write accepted the underlying stream's return without validating that all requested characters were accepted. Furthermore, flush and fsync alone did not establish that staged bytes still matched the intended UTF-8-BOM CSV. A short/interposed write or equal-size mutation could create a misleading audit export.

## Implementation

- New fvs_suite.csv_stage_integrity.CSVStagingWitness tracks SHA-256 over **serialized CSV bytes**, including the three-byte UTF-8 BOM. It uses incremental hashing rather than retaining full reports in RAM.
- _BudgetedCSVTextSink rejects partial/boolean/non-integer write return values before recording a chunk; the 64 MiB serialized-CSV and per-cell caps are preserved.
- After flush, the caller checks the original staged descriptor size, rereads in chunks of at most 256 KiB, and compares actual bytes by SHA-256, exact length and EOF **before fsync and exclusive publication**.
- Verification failures abort, remove the staging file, and emit generic verification errors. Staging names now have generic .fvs-csv- prefixes without customer-derived report names.
- Decimal-safe engine logic, deterministic ordering, original source files, CSV formula guard, offline-first processing, premium entitlements and human-only approval remain unchanged.

This protects **one staged report at one instant**; it is not a digital signature, a multi-file transaction, or defense against malicious filesystem changes *after* the verification checkpoint.

## Reproduction / verification

The exact new helper source matched Git blob **2b468b6b5f55612d8ce1080acc933e18872cbe8c** on Linux Python 3.13.5. The new 18-case regression logic was executed locally with an **isolated integration replay** of the affected sink and report-writer region, with simplified formula/UserDict dependencies; the replay is **not the exact full GitHub repository**.

- 18/18 focused replay tests PASS with python -W error.
- 18/18 PASS with python -OO -W error: **36 method executions**, zero skips.
- compileall for the helper and test modules PASS.
- Covered real-byte agreement, same-length first/last/amount corruption, missing BOM, truncation, expansion, short reads, EOF, read/fstat privacy errors, bool/short writes, Unicode CSV/BOM, zero data rows, staging corruption and cleanup.

Repository verification commands (run from repository root on Linux and Windows):

    python -W error -m unittest discover -s products/desktop/tests -p 'test_csv_stage_integrity_r236.py'
    python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_csv_stage_integrity_r236.py'
    python -W error -m unittest discover -s products/desktop/tests -p 'test_atomic_reports_r27.py'
    python products/desktop/scripts/offline_source_gate.py

The first two are mandatory prepackaging gates in BOTH Ubuntu source-tests and Windows windows-build CI jobs. The full inherited suite and native Windows acceptance are **not verified**; the local replay is not a substitute for hosted CI.

## Release and QD hold

No production branch, WordPress site, public download URL, executable, payment gate, or premium artifact changed. This branch is stacked on the unmerged R235 draft branch only. Independent QD review must inspect the entire inherited chain; final founder approval is required.

**Known infrastructure blocker:** On prior R235 SHA, [Actions #42240332142](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42240332142) had failed Ubuntu and Windows jobs with no recorded execution steps. Cause unknown. Owner action: inspect the Actions failure banner, account billing/usage, permissions and runner allocation, restore runner execution and rerun the unchanged R236 head.

**Next highest-impact step:** Run full inherited regression and native Windows 11 acceptance, then privately build, checksum, Defender-scan and smoke six x64 candidates. Validate premium-gated transfer, accessible UI, independent QD and founder approval before ANY release.
