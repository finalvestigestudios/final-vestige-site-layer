# R158 — independent SpendMap source-vendor display custody (DRAFT / HOLD)

## Risk and boundary

R157 independently validated financial, source-membership and historical-review
fields, but did not check the human-facing source_vendor_labels field. An
altered CSV could retain valid SHA-bound source rows, exact Decimal totals and
review flags while hiding, reordering or forging displayed original vendor
spellings. Reviewers could then overlook a lossy normalization collision.
R158 adds an independent fail-closed check of this previously unchecked field.

This change does **not** identify fraud, approve a payment, establish the
authenticity of an original source file, or provide a digital signature.

## Implementation

- fvs_suite/spend_label_verify.py: a separate source-label renderer that
  imports none of the production source-label, Unicode-display or spreadsheet
  sanitizer helpers. It independently reproduces the documented export display
  format: raw source-vendor labels trimmed and deduplicated within each
  vendor/month/category bucket, sorted by (Unicode casefold key, exact text)
  for deterministic ordering only (not Unicode identity equivalence). Literal
  semicolons become escaped U+003B; backslashes are doubled; invisible controls,
  format characters, special blank fillers and variation selectors are written
  as explicit Unicode escapes.
- fvs_suite/spend_evidence_verify.py: carries the untouched raw vendor from
  the existing strict, pinned-source CSV import and requires the displayed
  source_vendor_labels to match each independently rendered expected cell.
  This includes existing spreadsheet formula-prefix apostrophe protection for
  equals, plus, at-sign, nonnumeric minus and leading invisible/combining characters.
  Missing display columns, forged rows, misleading separators, dropped
  spellings, and changed Unicode encodings fail closed.
- No new mandatory account, telemetry, network calls, source edits, download,
  premium licensing bypass or compliance decision. This is a local CSV audit
  verification operation and leaves both original files intact.

## Tests and reproducibility

From the repository root, with PYTHONPATH=products/desktop:

1. python products/desktop/scripts/safe_unittest_r158.py
2. python -OO products/desktop/scripts/safe_unittest_r158.py
3. python -m fvs_suite.spend_evidence_verify --source original.csv --report spend-map.csv

Strict inventory: **33 synthetic test methods** with zero skipped-test tolerance.
Tests exercise normal labels, case variants, source-preserving punctuation,
per-bucket scoping, CSV multiline physical rows, bidi and zero-width marks,
non-breaking spaces, variation selectors, Hangul blank glyphs, escaped source
backslashes and semicolons, spreadsheet-formula prefixes, tampering, omitted
columns, unchanged source/report bytes, and CLI error redaction. CI registers
normal and optimized Python checks on both Ubuntu and Windows: **132 planned
targeted method executions** in total. Actual passes must be read from the
exact-head workflow run, not inferred from registration.

The independent checker deliberately shares the validated source parser,
source digest and normalized bucket key with the exporter; it is an independent
display-field verifier, not a wholly independent CSV engine or third-party
authentication of the import. Its escape table documents the currently
supported Unicode subset; it is not a complete confusable-text analyzer.

## Release gate remains HARD HOLD

The four free applications (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite,
Policy Delta Desk) and two premium applications (GrantAudit Studio Pro,
ProcureGuard Studio Pro) remain **UNRELEASED**. Internal Windows x64 CI builds
do not constitute shipped software. Physical Windows 11 46-observation
accessibility acceptance, genuine Defender/EDR health and binary scan,
signing, protected premium distribution, independent QD approval and founder
authorization are separately required. Do not merge into production or publish
a website download based on this source-test increment.
