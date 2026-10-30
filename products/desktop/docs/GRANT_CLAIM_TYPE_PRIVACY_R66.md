# R66 — GrantAudit claim-type privacy gate (UNRELEASED)

## Defect and scope

In linked grant reconciliation, an invalid `claim_type` cell was included
verbatim in the `ValueError` message. Values from a financial CSV may contain
beneficiary names, invoice identifiers, account information, line breaks, or
terminal control sequences. Such exceptions may escape through diagnostics,
support transcripts, or local logs even when the GUI itself is redacted.
The optional `claim_rows` path could also supply an unsafe row citation.

## Implementation

- `fvs_suite/grant_input.py::claim_kind` accepts the established `claim` and
  `credit` values using the existing casefold/strip behavior. Missing or empty
  values still default to `claim`; whitespace-only values remain invalid.
- An invalid classification reports only a fixed error and a canonical,
  positive, ASCII physical CSV row reference (or `?` if untrusted). It never
  interpolates the original cell or a malformed row label.
- `grant_allocations._claim_kind` now delegates to the shared helper. The
  money and reimbursement logic, exact Decimal allocation totals, linked
  credit behavior, human-only review flags, evidence hashes, and offline
  privacy boundaries are unchanged.
- The synthetic packaged GrantAudit smoke now asserts that an invalid claim
  type fails before publishing any files, without exposing its private value.

## Test evidence and limits

The 17 helper unit tests are runnable without the rest of the private
repository and cover valid classifications, compatibility defaults, private
values, newline/control payloads, spoofed/Unicode/noncanonical row citations,
and direct non-string inputs. Full-engine tests verify physical CSV line numbers,
credit arithmetic, default claim handling, and no partial reports on rejection.

Only count tests as **passed** after actual execution. A local isolated helper
run is not a complete suite, source-verified Windows PyInstaller run, or
binary acceptance. The five full-engine integration tests and packaged smoke
must run in the authoritative repository checkout/CI.

## Release boundaries

No release, public premium executable, premium access bypass, source CSV
upload, payment approval, or legal/compliance conclusion is authorized.
Windows 11 x64 smoke, malware scanning, accessibility verification, SHA-256
release custody, gated premium distribution, and independent QD/founder review
remain mandatory before publication.
