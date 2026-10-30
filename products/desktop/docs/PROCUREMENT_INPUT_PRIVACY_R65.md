# Labs R65 — ProcureGuard policy input and confidential event errors (UNRELEASED)

## Product defect

Before R65, ProcureGuard's optional JSON price policy used Decimal() directly
after stripping text. This silently accepted exponent notation ("1e-2"),
non-ASCII numerals, leading plus signs, padded zeros and arbitrary fractional
precision, despite the product's strict ASCII numeric CSV policy. An invalid
invoice/receipt event_type was also interpolated into an exception message,
potentially displaying private source CSV contents or terminal controls in a
GUI error/reporting workflow.

## Implementation

- New pure, offline fvs_suite/procurement_input.py is the single source of
  validation for both values and event classification.
- price_absolute and price_fraction accept JSON integers or strings with
  canonical ASCII fixed-point notation: "0", "1", "100.00", "0.02",
  "0.00000001". At most eight fractional decimal places, up to three integer
  digits. No exponent, sign, leading zero, whitespace, Unicode digits or
  binary floating point. The documented maxima are preserved: absolute
  **100.00**, fraction **0.10**; both must be nonnegative. Values are parsed
  as exact Decimal, not float, and source SHA-256 binding remains unchanged.
- Existing callers procurement._decimal_field() and procurement.event_kind()
  retain their signatures and delegate to the new module. Valid invoice,
  credit, receipt and return classifications preserve legacy casefolding and
  empty-field defaults. Invalid types report only the stream and a
  parser-generated physical row number, never the confidential field value.
  Untrusted row citations are rejected unless ASCII digits.
- Malformed optional JSON policy is rejected before CSV output staging.
  Invalid movements are rejected before review CSV/manifest publication.
  No automatic compliance decision, payment approval, telemetry or upload.

**Compatibility note:** previously accepted noncanonical price thresholds,
such as "1e-2", "+0.01" or "00.02", now raise a descriptive validation error.
Operators should write "0.01" or "0.02", respectively. This is deliberate
fail-closed behavior, not a silent policy migration.

## Verification

New test_procurement_input_r65.py contains **12 focused test methods** with
parameterized subcases for exact Decimal boundaries, upper limits, invalid
numeric grammars, float/bool rejection, legacy valid event kinds, sanitized
errors and row citations. These were executed on Python 3.13.5 Linux with
warnings-as-errors and also under Python -OO: **12/12 pass in each mode**.
Compilation of the isolated helper and its test file also passed.

New test_procurement_policy_integration_r65.py contains **six additional
full-engine scenarios**: invalid exponent, Unicode numerals, overprecise
tolerance, invalid invoice/receipt type with confidential content (including
no-partial-output assertions), and correct Decimal/custom-policy provenance.
These are committed for full repository CI; they **have not been executed in
the complete private checkout** and must not be counted as verified.

The local harness is a minimal reconstructed helper package, **not** Windows
x64/PyInstaller acceptance or all-six-app testing. The Actions runner-start
failure remains tracked in issue #75. No premium keys, binaries, download
endpoints or production site content are changed.

## Release/approval boundaries and next step

On a trusted full checkout, run the normal and -OO complete suites, then
six Windows 11 x64 build/smoke tests, privacy/accessibility/malware/checksum
verification, independent QD and founder approval. Until server-side paid
downloads and operator license custody are approved, the premium application
must remain distribution-blocked.
