# R526 — Invoice Twin Scout direct candidate-status custody

**Scope:** Final Vestige Labs Invoice Twin Scout; shared Python financial review core.
**Status:** draft only, release HOLD. Stacked on R525, not production `main`.

## Failure mode

`candidate_pairs()` emits two kinds of evidence:

- `exact_invoice_key` when the two rows have identical normalized vendor and invoice keys, regardless of monetary or calendar variance (which are shown as independent human-review flags).
- `review_possible_duplicate` when the vendor and exact Decimal amount match, normalized invoice keys differ, and their dates are within the caller's configured inclusive day window.

The public `review_flags()` API can also be called directly, without `candidate_pairs()`. Before R526, direct callers could label unrelated rows as candidate pairs and receive empty or misleading review flags. This would make audit evidence ambiguous without ever changing the actual source CSV.

## Change

`invoice_match._check_review_candidate_policy()` checks normalized vendor equality for both statuses; exact-key status additionally requires invoice-key equality; near-match status requires differing invoice keys, exact Decimal amount equality, and an inclusive calendar window. It runs **after** the R525 owned-dictionary, plain-native field, finite Decimal, calendar date, physical CSV row and distinct-row checks. No financial values or raw identities are interpolated into errors.

A prior R444 near-match test fixture was corrected from unequal to equal amounts to reflect the actual near-match predicate; its assertion that exact-key-only flags are not invented remains valid.

## Focused regression coverage

14 new methods in the already inventoried `products/desktop/tests/test_invoice_review_custody_r444.py` cover valid exact variance, status forgery of vendor and invoice keys, near-match equality rules, amount/credit mismatches, 7-day boundaries, 0-day override, chronological reversal, equal-Decimal-different-scale semantics, and nonmutation.

The production source manifest's existing **416 commands** have not been changed. The original tests and new tests must execute under standard and optimized Python once runners are available.

## Verification evidence and limits

A **standalone reconstructed** Python function using the exact R526 predicate passed 14/14 standard CPython and 14/14 `-OO` executions; `py_compile` also passed. This is **not** execution of the full committed test module or the repository's 416-command matrix. Hosted CI, native Windows x64 EXE builds and smoke tests, Defender, accessibility, SHA256, premium gating and QD are not yet verified.

## Privacy and release requirements

- Local-first only; no customer data, third-party connections, telemetry or uploads.
- Decimal comparisons are exact, not binary float or rounded.
- Candidate status always remains a human-review aid, never a fraud, compliance or payment decision.
- Both premium utilities remain protected and out of scope; no executable or download URL is published.
- Require independent QD validation and explicit founder authorization before any production merge or release.

## Next high-impact gate

Investigate [GitHub Actions startup issue #75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75). Confirm one smallest hosted job actually receives and executes steps. Rerun exact R526 HEAD through the pinned source matrix, and validate six native Windows x64 builds with installer/smoke, Defender, keyboard accessibility, hashes, and entitlement-controlled premium downloads before production approval.
