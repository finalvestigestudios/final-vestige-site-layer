# R155 — independently verify SpendMap source-line evidence membership (DRAFT / HOLD)

R154 added a complete SHA-256 fingerprint for all physical CSV start lines contributing to each normalized vendor/month, even when the visible 32-line preview is truncated. This sprint adds a **read-only, local, independently computed membership checker** that checks a selected original SpendMap source against an existing exported report. It does **not** call the report generator, use the report generator's fingerprint helper, alter source bytes, contact an API, or access premium material.

## Operator command (developer source tree)

Run with Python 3.12, from the repository root, with `PYTHONPATH=products/desktop`:

```sh
python -m fvs_suite.spend_evidence_verify --source "spend.csv" --report "spend-map-report.csv"
```

On success the tool reports a local source SHA-256, report SHA-256, number of vendor/month groups and category buckets. It prints **no vendor names, amounts, source lines or file paths**. Any invalid argument, changed source, tampered fingerprint, missing group, duplicate bucket, mismatched category citation or malformed CSV produces one generic **HOLD** line without confidential values. The report and source are descriptor-checked bounded ordinary files, verified against byte snapshots; a private temporary source copy is parsed; metadata and hashes are rechecked at completion. Original data is never modified. Missing or header-only source records are a HOLD because a header-only financial report has no source-bound row fingerprint.

## Trust boundary and important limits

- Every normalized vendor/month must appear in the report under all its expected category buckets, once each. The verifier recomputes the documented R154 ASCII domain-separated SHA-256 using every actual physical source CSV record-start line, the exact source-byte SHA-256, vendor and month. It checks all repeated full hashes, counts, omitted counts, earliest 32 line previews, and each category's legacy `source_rows`. Multiline CSV source fields use physical start lines, not data-row ordinals.
- Source validation uses the shared strict local SpendMap CSV/Decimal/date parser, including cent precision, while fingerprint construction is a **separate implementation**, not a call to `spend_analysis._vendor_month_line_digest`. This protects against accidental export evidence drift, *not* malicious simultaneous source+report re-creation.
- **This does NOT verify money totals, outlier logic, missing transactions that were never in the selected original, historical application identity, report authenticity, or legal/compliance correctness.** For whole-report exact monetary/output reproducibility use `python -m fvs_suite.replay_verify --kind spend-map --report ... --source ...` with the current trusted engine. Even both checks together are not an approval or digital signature. Retain the original source securely.
- Report labels may be spreadsheet-escaped. The verifier uses the same local safe label display contract when identifying report category buckets. Privacy-preserving exceptions and a nonzero exit code are required on rejection.
- Tests use **26 synthetic named methods** including 33/200-line truncated membership, cross-category credits, Unicode/newline CSV provenance, tampered count/hash/rows/preview, dropped/duplicated group buckets, source mutation, readonly checks, argument redaction, and Windows-compatible symlink restrictions. The fixed-inventory runner forbids silently skipped tests; Ubuntu and Windows CI each execute normal and optimized (`-OO`) Python, for **26 × 2 × 2 = 104 planned targeted executions**, plus inherited source, smoke and executable build gates. A red CI check is a HOLD.

All six desktop programs remain **UNRELEASED**. R155 does not generate, sign, publish, unlock, or host binaries. Physical Windows 11 accessibility observations, genuine Defender/EDR, code signing, protected premium distribution, independent QD review and explicit founder approval remain mandatory.
