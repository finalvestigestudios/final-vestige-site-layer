# R75 — preserve original procurement credit/return document identities

**Draft, unreleased and subject to independent QD/founder review.** This work is
stacked on R74, not the production branch.

## Defect and impact

ProcureGuard Studio Pro compares credit-memo and return references against the
original invoice/receipt documents. Candidate linking is intentionally tolerant
of punctuation and Unicode transformations, but the secondary source-spelling
review previously used Python's `.casefold()`. When a source document was `ß1`
and a credit related to `SS1`, both folded to `ss1`: the result could omit the
`normalized_credit_link_review` flag. The analogous issue affected return
links. These are not necessarily invalid links; they are **ambiguous links
that require a human reviewer**.

## Patch

- `fvs_suite/procurement_reference.py` snapshots original document spellings
  using R74's `ascii_case_identity` comparator (ASCII case ignored, Unicode
  spelling preserved), with no external I/O, network calls or amounts.
- `fvs_suite/procurement.py` uses the immutable source set when deciding
  whether to append `normalized_credit_link_review` and
  `normalized_return_link_review`. Its existing lossy candidate linking,
  unlinked/duplicate flags, quantities, prices and Decimal arithmetic stay
  unchanged. The raw identifiers and row provenance remain in the report.
- `tests/test_procurement_reference_r75.py`: 25 focused pure-source tests.
- `tests/test_procurement_credit_return_r75.py`: 16 full-review-line tests
  covering invoice credits, receipt returns, Unicode expansions, punctuation,
  ASCII casing, wrong references and Decimal total continuity.

## Release and verification

A successful local helper-unit test does **not** certify the integrated engine,
actual Windows binary, or catalog. Test all 41 new regressions plus the legacy
ProcureGuard tests in a complete repository checkout; run normal and Python
`-OO` modes. Build, hash, malware-check and natively execute six Windows 11
x64 binaries; verify entitlement controls for the two premium apps; complete
independent QD and founder approval before any publication.

The currently observed GitHub Actions runner-start failure is independently
tracked in issue #75. Until runner steps actually execute, Actions failures
are not app-test results. No production merges, installer uploads or public
premium download endpoints are authorized by this PR.
