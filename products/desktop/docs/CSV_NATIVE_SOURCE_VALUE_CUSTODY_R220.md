# Final Vestige Labs R220 — native CSV source-cell custody

Status: **DRAFT, QD HARD HOLD, NOT RELEASED**. Tracks #73; stacked on R219 draft #1164 at `86185f8fc2230161520a13b76a76224a86b1afa3`, not `main`. No production/public-site edits.

## Reproduced threat

The R219 `engine.safe_cell` implementation used `str(value)` before
checking spreadsheet formula prefixes. A direct-API caller could supply an
arbitrary object or a `str` subclass with malicious `__str__`. A local
reproducer returned `AUDIT-APPROVED-2026` for a non-string object, and
`PAID-IN-FULL` when the underlying `str` subclass actually contained
`=SUM(A1)`. Such a value would look like ordinary source evidence after
sanitization. This is a **local API evidence-spoofing risk**, not an assertion
of an actual exploit in distributed builds or an existing customer incident.

## Exact code contract

`fvs_suite.csv_native_cell.native_report_text` is called by the default
`engine.safe_cell` *before* formula inspection:

- Accept only **exact built-in** `str`, `int` (up to 269 bits) and finite
  `Decimal` instances. Subclasses are not silently coerced.
- Reject floats, bools, None, bytes, arbitrary objects, nonfinite Decimal,
  giant integers and cells over the writer's 1,048,576-character limit.
- Never invoke untrusted `__str__`, `__format__` or custom numeric hooks.
- Preserve exact Decimal strings including trailing zeroes and signed zero.
- Reject with fixed errors; the existing writer redacts callback failures,
  atomically rolls back staged data and preserves earlier report files.

This is the **default engine.save sanitizer** boundary. Standalone
`atomic_reports.write_csv_report` callers that pass their own callbacks
retain responsibility for their own conversion policies.

## Evidence and verification boundaries

- Exact newly committed production module was locally tested: **18/18 PASS**
  under normal Python and **18/18 PASS** under `python -OO`; **36/36**
  focused method executions. Synthetic fixtures only.
- Module local/Git blob SHA: `1030e18d445a62f4afbde0f74e1796094fbc138d`
  (byte-identical at verification).
- Reproducer confirmed both forged conversion outcomes against the previous
  logic, then the new helper blocked the same unsafe object types.
- Seven additional real `engine.save`/atomic-writer integration regressions
  are **committed but not verified locally**, because the full private repo
  dependency tree could not be mounted in the local execution environment.
- The desktop CI workflow requires all **25 R220 tests** on Ubuntu and Windows
  under normal and optimized Python. Hosted result is not claimed successful.
- Full inherited suite, six Windows x64 packages, native GUI/accessibility,
  antivirus scans, signed/checksummed binaries, protected premium access and
  independent QD approval remain **unverified**.

## Release/compatibility concerns

The stricter default writer intentionally rejects custom objects, subclasses,
floats, dates and None instead of representing them as arbitrary text. Any
legitimate integration previously relying on implicit `str()` must explicitly
validate, then pass an owned native string (or exact int/finite Decimal).
Review all six engines and their real workflow exports under the full test suite
before merge. No payment/compliance auto-approvals, customer data uploads,
telemetry, download URLs, or premium exposure were introduced.

## Next highest-impact action

Restore GitHub Actions runner execution (inspect the run's pre-start banner,
usage/billing/permissions/runner allocation); rerun **unchanged** R220 commit
on Ubuntu/Windows and collect the full inherited test results. Next privately
build/scan/checksum/smoke six Windows x64 EXEs, complete Windows 11 keyboard and
screen-reader acceptance, then obtain independent QD and founder approval.
