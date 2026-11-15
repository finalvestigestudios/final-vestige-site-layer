# Final Vestige Labs R454 — exact CSV dialect preflight before allocation

**Issue:** #73 · **Parent:** R453 draft PR #2640 at pinned commit d79874b04bb2c535181c8ead141dfb97c5523cef · **Status:** stacked DRAFT / **QD RELEASE HOLD**.

## Defect and change

The R453 report publisher checked a lower bound of UTF-8 source bytes before invoking CPython's CSV writer, then enforced the exact 64 MiB serialized-file limit afterward. A legal 1 MiB string filled with double quotes could nearly double during CSV escaping, and a 256-column direct API row could allocate substantially more than the remaining output budget **before** the sink rejected it.

R454 computes the **exact serialized byte requirement** of each sanitized default csv.excel row ahead of DictWriter.writerow(), including:

- Each cell's UTF-8 bytes, with every embedded double quote doubled.
- Two enclosing quote bytes for fields containing a quote, comma, CR, or LF under QUOTE_MINIMAL.
- A comma between fields and a CRLF record terminator.
- Python's special case that quotes a single empty field as two double quotes to distinguish it from an empty record.
- UTF-8 BOM cost remains reserved in the sink constructor, as in R453.

This tracks **the dialect actually used by the six-app report writer** (DictWriter default excel). The preflight is a calculation, not serialization: it never mutates the budget or the input. The original write-time exact encoded-byte check, staging SHA-256 witness, fsync, no-overwrite publication, and fail-closed partial cleanup remain authoritative. If the writer dialect is changed, the preflight and real-writer parity regression must change together.

This is an allocation-order safeguard, **not** proof of a specific customer exploit or an all-platform memory ceiling. It does not modify any app's Decimal financial decisions, deterministic evidence lineage, premium license controls or requirement for human compliance review. All six standalone Windows x64 apps share this publisher.

## Committed scope

- products/desktop/fvs_suite/atomic_reports.py: exact csv.excel preflight.
- products/desktop/tests/test_csv_serialization_preflight_r453.py: inherited quote-expansion expectation updated to enforce refusal **before** serialization.
- products/desktop/tests/test_csv_exact_dialect_preflight_r454.py: **12 new unittest methods** covering deterministic native CSV parity, quote doubling, multibyte UTF-8, CR/LF/comma quoting, single empty field, remaining bytes, no partial outputs, no overwrite, ignored-extra formula sanitization and exact-byte success/failure boundaries.
- .github/workflows/desktop-source-evidence-r385.yml: R454 tests standard and optimized on Linux and Windows matrix.
- .github/workflows/desktop-build.yml: R454 and inherited R453 tests standard and optimized **before** Windows x64 packaging.

## Evidence and limitations — 2026-11-15

The isolated local CPython csv.writer parity prototype compared the proposed dialect formula to real UTF-8 encoded writer output for **51,000 seeded synthetic rows** (1–34 columns; mixed quotes, commas, CR/LF, tabs, whitespace, Unicode and empty strings): **51,000/51,000 parity checks passed**. This is **not** execution of the production Python module or committed R454 unittest file. The 12 committed methods and complete inherited six-app suite **require CI**. No actual Windows x64 binaries were compiled, installed, Defender-scanned, accessibility-tested or verified for distribution.

Last inspected parent R453 exact-commit CI runs:
- [Six-engine source #43733659378](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43733659378): failed, two jobs with no recorded steps.
- [Windows internal build #43733659395](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43733659395): failed, two jobs with no recorded steps.

These observations **do not establish why the hosted runners did not execute**, and cannot substitute for CI passing. Inspect Actions failure banners, job annotations, owner billing/spending and runner policy, then rerun exact-head CI. The next development priority after runner recovery is full import/integration tests (especially inherited R453), real Windows x64 builds and Defender/GUI/keyboard/accessibility checks, checksum and controlled premium delivery verification.

**Release remains held:** no production merge, public EXE/download, premium artifact/license exposure, payment, WordPress publication or telemetry. Independent QD signoff and explicit founder approval are mandatory. Four free: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk. Two gated premium: GrantAudit Studio Pro, ProcureGuard Studio Pro.
