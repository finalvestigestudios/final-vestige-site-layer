# R74 — require review for Unicode-folded financial identities

**DRAFT / UNRELEASED.** Independent QD/founder approval required.

## Defect

Python Unicode uppercase and casefold can expand distinct original identifiers
into the same matching key: long s (ſ1) and S1, sharp s (ß) and SS,
the ff ligature (ﬀ) and FF. The suite intentionally groups such
identifiers for candidate detection, but the existing reviewer collision
check used Unicode casefold and therefore called them *identical*, sometimes
returning a matched status with no normalization warning.

SpendMap also displayed only one vendor label variant for two different
source spellings. Invoice Twin Scout could omit vendor and invoice review flags.

## Implementation

- Shared review.ascii_case_identity converts only ASCII uppercase A-Z to a-z.
  Normalized financial identity collisions now require review when non-ASCII
  spellings differ, while ordinary ASCII case-insensitive matches remain.
- invoice_match.review_flags uses the same comparator for source vendor and
  invoice-number labels.
- spend_analysis.summarize_spend uses the same comparator when counting
  raw vendor variants, keeping its variant count consistent with its
  normalized_vendor_collision_review flag.
- LedgerDiff Lite, GrantAudit Studio Pro, and ProcureGuard Studio Pro inherit
  the shared conservative collision behavior. Policy Delta Desk is unchanged.

No matching candidate is suppressed, no payment is approved, no compliance
decision is automated, and no financial amount arithmetic is modified.
Original source spellings, physical row numbers, Decimal calculations, and
snapshot SHA-256 provenance remain preserved. All processing stays local.

## Verification

Synthetic regression tests cover sharp s, long s, ligatures, ASCII-case
controls, punctuation collisions, duplicate invoice review, SpendMap variant
counting, row provenance, and numeric continuity. Full CSV-to-report
integration tests cover five financial desktop products on a complete checkout.

Isolated Linux Python tests are **not** equivalent to full-repository or
native Windows x64 verification. Package smoke, accessibility, anti-malware,
signing, premium access controls, and independent QD/founder review remain
mandatory for any release.

## Known remaining risk

Procurement credit and return event raw document-reference comparisons
still use Unicode casefold and may under-report normalized link review.
Audit that separate behavior next, without automatically authorizing a link.

**Highest release priority:** resolve Actions runner-start problem #75 and
execute full source plus native Windows test gates. Never publish untested
free or unprotected premium EXEs.
