# LedgerDiff Lite R131 — explicit per-export match keys (DRAFT / RELEASE HOLD)

LedgerDiff Lite previously selected an ID using its known CSV header aliases only (e.g. `id`, `transaction_id`, `reference`). Exports with a legitimate custom ID header could not be reconciled without editing originals; files containing two recognized aliases could be rejected as ambiguous.

## Working pre-release functionality

The local-first GUI now has **Left match-key CSV header (optional)** and **Right match-key CSV header (optional)** fields. These are independent. Leave a field blank to retain the existing automatic alias selection. To reconcile a left export with header `Payment Reference` and a right export with header `pay_ref`, enter these exact column labels respectively; ASCII case and surrounding spaces are normalized just as with imported CSV headers. The override chooses a single existing source column; it does **not** rewrite files or synthesize identifiers. For direct library clients:

```python
ledger_diff(left_csv, right_csv, output_folder,
            left_match_column="Payment Reference",
            right_match_column="pay_ref")
```

The CSV still requires an unambiguous `amount` alias on **both** sides. An explicitly selected match header must exist on that side and cannot also be the selected amount column. The optional override accepts at most 128 normalized characters, ASCII letters, digits or underscores, starting with a letter or underscore. Other header styles (for example `Reference #`) are not yet supported by the explicit override and remain a UX follow-up, not a claim of full export compatibility. A source with duplicate normalized headers fails closed.

Each report now includes `left_match_column` and `right_match_column` immediately before the existing three provenance fields. These show the *actual original CSV header strings*, including when automatic alias mapping was used. Existing `left_ids`/`right_ids`, physical line references, source byte SHA-256 fingerprints, Decimal-safe totals and review statuses remain. The report itself is **not** a legal finding, audit certification or payment authorization. Human review of normalized key collisions, duplicate IDs and variances remains required.

## Threat model and limits

- The explicit header value is used only to select a column from the already verified local CSV snapshot. No network calls, telemetry, customer uploads, entitlement changes or automatic approvals were introduced.
- No direct use of the selected header as a monetary value is permitted: identity and amount must resolve to distinct physical columns.
- Invalid overrides and absent headers fail before creating an output report. Error text is generic and must not echo the entered private header or financial cells.
- The same source can still be chosen twice, but its identical byte SHA-256 evidence must remain flagged for review.
- A CSV SHA-256 identifies the read snapshot; it is not a signature, proof of correctness or independent custody attestation.
- Normalized matching may group distinct original strings; the source labels and collision/review flags remain necessary. This MVP does not claim fuzzy, one-to-many or probabilistic matching.
- User changes to GUI key fields do not change originals; exported reports are saved only into a user-selected local folder.

## Measurable verification

[Source tests](../tests/test_ledger_custom_match_r131.py): 15 synthetic end-to-end test methods covering default behavior, two different custom header mappings, independent per-side selection, ambiguous automatic aliases, absent/duplicated headers, blank/invalid/private injected header values, money-as-identity refusal, physical multiline citations, unmatched keys, no partial reports, source immutability, report schema and existing importer return signatures.

[Privacy-redacted strict gate](../scripts/safe_unittest_r131.py): verifies exactly those 15 source-owned test methods, zero skipped tests, no unexpected successes, normal and optimized `-OO` mode. Mandatory Linux and Windows CI gates target **15 × 2 modes × 2 OS = 60 executions**, plus the inherited full six-application source and Windows x64 packaging gates. A green CI result is only automated evidence for the exact commit checked; no physical Windows 11 acceptance is implied.

## Release controls

**DRAFT / HARD HOLD.** No production branch, live site, public download, premium file, license or QD approval was touched by this feature. The six applications still require private exact-commit executable custody, 46 independent physical Windows 11 accessibility checks, actual Defender/EDR assessment, signing, authenticated premium delivery, QD approval and founder authorization before release.
