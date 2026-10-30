# SpendMap Lite R61 — source snapshot SHA-256 binding (pre-release)

## Defect addressed

Physical CSV source-row citations and original vendor labels are necessary, but
not sufficient to identify *which version* of a file produced a report. If the
original export is modified after the report is generated, row `4` could now
refer to unrelated financial data. A filename or hash computed from a later
read would not prove report provenance.

## Change

SpendMap Lite now obtains `(parsed_rows, source_sha256)` in **one verified CSV
snapshot** from `engine.table(..., include_digest=True)`. The SHA-256 is of the
exact unmodified bytes that were parsed, including UTF-8 BOM, line endings and
quoted embedded newlines. `summarize_spend` requires a canonical lowercase
64-character digest (no missing, uppercase, whitespace or invalid hashes) and
appends `source_sha256` to each result row. The writer preserves the previous
11 columns in order, followed by the new twelfth column. Existing source-row,
original vendor label, collision and anomaly fields are unchanged. No source
file is overwritten; no bytes are sent to a service.

A reviewer may verify the exact original source file independently, for example:

```powershell
Get-FileHash -Algorithm SHA256 -LiteralPath '.\spend.csv'
```

Compare the 64-hex digest to the `source_sha256` field. **If the file changed,
the hash will not match.** Preserve the original CSV separately. This digest
is not a digital signature, proof of authorship, or evidence of fraud or
compliance. It does not authenticate the reporter, detect an attacker who can
replace both files, or prove what was displayed to an operator. Source filenames
and filesystem paths are intentionally omitted from the hash column.

**Empty import limitation:** An input containing headers and no data generates
an empty summary (header only), so it has no row in which to report its source
hash. Do not treat a header-only report as a complete evidence manifest.

## Test plan and release status

- `python -m unittest -v tests.test_spend_source_digest_r61` — pure analysis
  canonical digest, history/amount preservation, collision flags and repeated
  execution, run normal and `python -OO`.
- `python -m unittest -v tests.test_spend_source_engine_integration_r61` —
  **requires complete checkout**. Tests imported BOM/multiline CSV, exact bytes,
  line-ending changes, path replacement after a verified read, output headers,
  and invalid-source no-partial-report behavior.
- Full normal and `-OO` source gate, Windows 11 x64 packaging, real EXE smoke,
  accessibility, AV, premium controls and independent QD approval remain
  required. The R61 change is **not an executable release authorization**.
