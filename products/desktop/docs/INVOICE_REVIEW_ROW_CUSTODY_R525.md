# R525 — Invoice Twin Scout direct review evidence custody (DRAFT / QD HOLD)

## Scope and defect

The public `fvs_suite.invoice_match.review_flags(a, b, status)` entrypoint accepted a pair with the **same physical CSV source row**, and accepted missing, malformed or subclassed `row`, `v` and `inv` fields. Even though `candidate_pairs` correctly validates these fields, integrations that call review_flags directly could receive a plausible empty review-flag string from evidence that cannot be tied to two real source rows.

## Implementation

- `_owned_review_evidence` snapshots native `dict.items` before accessing source fields. Require a native, canonical decimal physical line number from 2 through 9,999,999,999 (no leading zeroes), plus native uppercase ASCII-alphanumeric vendor and invoice matching keys. Reject absent, forged, non-ASCII, subclassed and ambiguous values before invoking caller hooks.
- `review_flags` requires two **distinct** physical CSV lines. This does not claim any two records are fraud, compliance evidence, or approved payments.
- Preserve the existing exact-invoice flags, near-candidate review classifications, bounded Decimal behavior, original raw display identities and nonmutation of input records. No policy auto-approval, telemetry, network calls or upload.

## Validation and limits (2026-11-18)

- 15 added committed regression methods in the **already inventoried** `tests/test_invoice_review_custody_r444.py`. Cases cover same-line exact/near, absent/header/noncanonical/overlong rows, native-type/subclass custody, missing and noncanonical `v`/`inv`, adversarial dictionary overrides, independent right-hand validation, valid exact/near behavior, real candidate lineage, privacy and nonmutation.
- Offline Linux CPython isolated **reconstructed function-level harness** (no complete private repo): `py_compile` passed; 15/15 normal and 15/15 `-OO` tests passed. Removing the R525 row/key protections from that harness yielded **11 failing cases**. These are **representative tests, not executions of the committed test module or full suite**.
- Actual committed R525 test code, the full 416-command source matrix, native Windows binary/GUI tests, Defender scan, distribution checks and QD have **not** been validated locally. GitHub Actions evidence must be checked against the exact PR commit.
- No immutable source-command manifest edit, source release authority, signed installer, versioned downloadable EXE, site publication, premium access-flow change or production merge is implied.

## Release checklist / next highest impact

1. Resolve GitHub Actions pre-run failures tracked in [#75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75): inspect account billing limits, Actions policy, runner eligibility; do not equate `steps=null` with source-test failures.
2. Run the exact R525 HEAD's committed full `test_invoice_review_custody_r444.py` and **416-command** source matrix (normal and `-OO`) on a trusted full checkout, then Windows 11 x64 builds and six-EXE smoke, keyboard accessibility, Defender scan, SHA-256 and premium-entitlement verification.
3. Independent QD review and explicit founder approval before merging or releasing. The four free and two premium apps remain **UNRELEASED**, with private premium binaries gated.
