# R527 — Invoice Twin Scout clean-review label custody and bounded raw identities

**Status: DRAFT / internal only / QD and founder HARD HOLD.**
This increment is stacked exclusively on R526 (draft #3023), not production `main`.

## Failure mode

The direct Python `review_flags()` interface could previously accept two raw
vendor/invoice labels unrelated to their asserted normalized `v`/`inv`
keys. For instance, both records could say vendor `Acme`, both assert
`v="UNRELATED"`, and return an **empty review string**. A near-candidate
could also assert differing invoice keys for two identical raw invoice labels.
That is misleading audit provenance even if `candidate_pairs()` ordinarily
receives correctly normalized CSV importer records.

Raw labels were also only checked for native `str` type, not length; a direct
caller could force unbounded case translation in `review_flags()`.

## Implemented guard

1. `_owned_review_evidence()` now enforces the existing 1,048,576-character
   source-identity ceiling on both raw fields, after copying native dict
   storage and before any label translation. This does not truncate private
   values and uses constant, redacted rejection text.
2. After the R526 candidate predicate and original independent review flags,
   a would-be **clean** result must prove all four raw labels normalize using
   the **same `identity_inputs.normalize_key()` function as the importer** to
   their asserted `v` and `inv` values. Mismatches fail closed rather than
   silently returning an empty review string.
3. Existing nonempty warnings for lossy-label collisions and exact-key
   amount/date/signed movements remain visible and unchanged. This narrower
   change does **not** assert that a warned identity is genuine or that a
   source CSV is independently authentic.

The guard is read-only; it does not affect Decimal calculations, candidate
ranking/window behavior, input files, output schema, premium entitlements or
site publishing. No data is transmitted, and no duplicate is automatically
declared fraudulent or approved for payment.

## Regression contract

17 synthetic methods were added to the **already inventoried**
`products/desktop/tests/test_invoice_review_custody_r444.py` (no new source
command or manifest change). Cases include clean exact/near candidates,
both-side forged keys, false near uniqueness on identical invoice text,
punctuation and Unicode case-expansion, empty raw labels, raw-field upper
limits even when a collision would be flagged, boundary-size acceptance,
private-error and traceback suppression, and nonmutation.

Validation must execute this full committed test module under **standard and
optimized (`-OO`) Python** on both Ubuntu and Windows, then run the existing
416-command pinned source matrix. Standalone recreated or static checks are
not substitutes for those source-owned gates.

## Release and operational HOLD

The six native Windows x64 applications (LedgerDiff Lite, Invoice Twin
Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and
ProcureGuard Studio Pro) remain **unreleased**.

The expected mandatory gates remain: GitHub Actions startup restored
([#75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75));
complete source tests; six Windows builds and real executable smoke tests;
physical Windows 11 accessibility witness checks; actual Defender/EDR;
per-binary SHA-256 and provenance; access-controlled premium distribution;
independent QD approval; and explicit founder authorization before any
production change or live download.

### Highest-impact next action

Ask an account/repository administrator to determine the GitHub Actions
pre-step failure (billing, spending cap, runner eligibility and workflow
policy) and prove that one minimal hosted job can **execute a step**. Then
rerun the exact R527 commit's source and native Windows matrices; never
relabel pre-step failure as a passing test.
