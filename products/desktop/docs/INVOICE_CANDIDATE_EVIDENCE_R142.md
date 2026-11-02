# Labs R142 — Invoice Twin Scout audit measurements (DRAFT / RELEASE HOLD)

**Status:** source-only engineering candidate. No executable, premium file, or public
download is authorized. Based on R141 draft PR #648, not the production branch.

## Problem and contract

An exact vendor/invoice-number match may involve a normal invoice, a revised charge,
or a credit memo. An existing candidate report exposes the original amounts and dates
but requires the reviewer to calculate the *signed* amount change and date distance.
It also labels opposite-signed exact-key entries only as an amount variance, which can
lead to the mistaken assumption that a credit is another charge.

The R142 CSV adds **two descriptive fields** immediately after `amount_b`:

- `amount_delta_b_minus_a`: exact cent-valued **B minus A**, including sign.
  For 100.00 followed by -100.00, the delta is -200.00, **not** a duplicated
  200.00 payment. The value is computed from the same independently cent-rounded
  Decimal inputs printed as `amount_a` and `amount_b`, under a private
  64-digit Decimal context (immune to hostile ambient precision and traps).
- `date_gap_days`: nonnegative absolute calendar-day separation between the
  original source dates. Exact-key anchors are still found regardless of the
  user-selected 0–365-day *near-match window*; this field does not impose a
  new filter or change the displayed candidate count.

For **exact invoice-key candidates only**, if one *nonzero* amount is negative
and the other is positive, `review_flags` additionally includes
`opposing_signed_amounts_review`. This means **human interpretation required**:
the pair could be a credit/reversal, not a duplicate or fraud. Signed zero never
triggers it. Existing `amount_variance_review`, distant-date,
normalized-vendor/invoice flags and near-match classification are preserved.

No matching algorithms, thresholds, candidate IDs, export filenames,
physical source-row references, SHA-256 import custody, or source files change.
A candidate identifier is only a reproducible locator, not a cryptographic
signature, payment approval or determination of a compliance violation.

## Verification

Synthetic tests are in `tests/test_invoice_candidate_evidence_r142.py`.
The zero-skip, exact-method gate `scripts/safe_unittest_r142.py` requires
**28 distinct methods × 2 Python modes (normal, -OO) × 2 OSes
(Ubuntu and Windows) = 112 named executions**, in addition to the complete
source suite, Windows portable x64 builds, private encrypted artifact transfer,
locked premium windows and native accessibility probes. Run locally:

```sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r142.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r142.py
```

The tests cover opposite signs and zero, signed deltas and half-cent rounding,
leap-day and window boundaries, maximum values and hostile Decimal contexts,
multiline physical CSV citations, SHA-256 / candidate ID stability,
spreadsheet formula-escaping, privacy-safe failures and no-partial reports.

## Release hold

Tested *source* is not a tested signed EXE. All six Windows x64 apps remain
UNRELEASED. No distribution or production merge until independent physical
Win11 acceptance (46 hands-on accessibility observations), trusted candidate
custody, genuine Defender/EDR, signing, authenticated premium delivery,
independent QD approval, and explicit founder authorization.
