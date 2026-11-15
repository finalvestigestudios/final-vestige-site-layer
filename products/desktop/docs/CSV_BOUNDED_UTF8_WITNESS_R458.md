# R458 — Bounded UTF-8 counting and staged CSV witness (DRAFT / release HOLD)

## Scope and security objective

Issue [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73): the shared local-first CSV evidence publisher serving **LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro**. No financial arithmetic, source import, entitlement, compliance status, human-review workflow or GUI policy is changed.

The existing R454/R457 exact `csv.excel` preflight and R237 staged SHA-256 witness previously made a **second full UTF-8 allocation** for every CSV field in `_excel_field_bytes`, and a third full encoded copy of the entire serialized row in `_BudgetedCSVTextSink.write`. A worst-case accepted 1,048,576-character astral text field can require 4 MiB of transient encoded allocation *just for size accounting*, even after the CSV serializer already holds the text. Row writes could allocate up to the 64 MiB CSV byte limit once again. This is a local memory-efficiency and availability issue, **not** evidence of remote data exfiltration.

## Code and invariants

- `fvs_suite/atomic_reports.py`: `_utf8_chunks` encodes **16,384 Python characters per slice** (at most **65,536 UTF-8 bytes** for valid Unicode). Both exact-dialect preflight paths now sum per-chunk encoded lengths rather than materializing `value.encode("utf-8")`. The source text is never normalized or reinterpreted.
- The stage sink independently counts chunks and enforces the unchanged **64 MiB including UTF-8 BOM** cap *before* calling the underlying text stream. After a successful full-character write, it records the same UTF-8 chunks into the existing SHA-256 witness. Counting and attestation require two encoding passes, a deliberate CPU-for-peak-memory tradeoff.
- Real staging verification continues to hash the descriptor bytes, checking both byte count and SHA-256 against the expected stream before `fsync` and exclusive no-overwrite publication. Short writes are not attested; failed byte budgets never write.
- CSV quoting (including CRLF, commas, embedded quotes, and singleton empty fields), Decimal textual precision, synthetic source references, UTF-8 BOM, redacted errors, tamper detection, ignored-extra sanitization and all six-app privacy boundaries remain in place. No auto-approval or automated compliance decisions are added.

## Test coverage

`tests/test_csv_bounded_utf8_witness_r458.py` adds **13 methods**: deterministic 3,000-case Unicode/quoted-field arithmetic parity; multi-byte/chunk-boundary parity; the 4 MiB 1,048,576-emoji field; zero-length writes; genuine temporary-file witness descriptor verification; direct sink budget refusal without staging; short-write fail-closed; 400 native `csv.writer` parity cases and SHA-256 equality; a large-field peak-allocation bound; end-to-end Unicode/Decimal BOM output; one-byte-short cleanup; existing-evidence no-overwrite; and unsanitized spreadsheet-formula rejection.

These tests are registered in the independent Ubuntu/Windows source workflow and in *both* the Linux source and Windows pre-packaging jobs of `.github/workflows/desktop-build.yml`. Both `python -W error` and `python -OO -W error` are required in CI.

### Actually executed in the local isolated projection

Executed on **Linux Python 3.13.5** with the same chunking, preflight and witness logic in a reconstructed standalone test harness, **not** the complete repository or the 13 committed tests:

- **7/7 unittest methods PASS** in standard mode, **7/7 PASS** in `-OO` optimized mode, with `-W error`; `py_compile` passed.
- **5,000 seeded** Unicode byte-cost/quote comparisons and **1,000 seeded** real `csv.writer` stream and SHA parity comparisons per interpreter mode, plus multibyte chunk boundaries, real 16,384-character crossover, one-byte budget failure, short writes and rollback.
- In a synthetic 300,000-emoji / 1,200,000-byte input, `tracemalloc` observed **197,902 bytes** peak while chunk-counting, versus **1,200,557 bytes** for a one-shot UTF-8 encoded-copy projection (about **6.1x lower measured peak** for that isolated operation). This is **not** a Windows application peak-memory benchmark.

**Important limitation:** full-module 13-method committed regressions, inherited six-app tests and native Windows x64 builds have NOT run locally. R457 parent CI runs failed before first steps; check the current R458 head workflows for fresh evidence before considering any release.

## Release restrictions and next step

1. Restore GitHub Actions runner execution, beginning with job failure annotations, account Actions billing/spending policy and runner availability; confirm root cause rather than assuming it.
2. Execute the complete 13-method R458 source suite in normal and optimized modes, inherited CSV/witness/regression gates, six-app smoke tests, genuine Windows x64 builds, signature/Defender review, native keyboard/a11y checks, installed smoke, SHA-256 receipts and premium entitlement/distribution verification.
3. Obtain independent QD review and explicit founder approval before any production merge, WordPress publication, release artifact, license grant or premium download.

**HARD HOLD:** This is a feature branch stacked on R457, **not** production `main`. No executable, download, premium file, license or site change is published.
