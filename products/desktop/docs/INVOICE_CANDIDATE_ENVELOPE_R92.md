# R92 — Invoice Twin Scout candidate envelope and audit-pair custody

**Status: draft only; never a release approval.** Issue #73. Parent review branch: feature/labs-policy-blank-filler-custody-r91 (draft PR #341). Four free/two premium product boundaries, local-first processing and independent QD/founder review are unchanged.

## Risk and concrete predecessors

1. The public candidate_pairs(max_candidates=...) accepted arbitrary positive integers. A direct caller could disable the default 100,000-review-candidate ceiling and allocate quadratic output for dense 200,000-record sources. The default UI path was already bounded; this was a direct API gap.
2. The public attach_invoice_provenance allowed two same-class candidates referencing identical source lines in reverse order. Because the fingerprint intentionally includes direction, the two entries received different IDs. This could exaggerate review volume; it does not prove fraud.
3. The provenance physical-line regex allowed arbitrarily long integers; a 5,000-digit value could reach int() and trigger an interpreter-specific conversion error.

## Scoped correction

- Enforce 1 <= max_candidates <= MAX_CANDIDATES for direct matcher calls. Invalid booleans/floats and zero/negative limits still reject with compatible diagnostics. Over-cap requests fail **before consuming an iterator**. Lower positive limits still work.
- Accept list reports only and reject more than 100,000 candidates before building hashes or output copies. Reuse the matcher's existing cap constant rather than defining a conflicting limit.
- Require physical rows to be canonical ASCII digits of 1 to 10 places, with row >= 2, matching the candidate matcher. No private values enter errors.
- Reject a duplicated **unordered source-line pair and same review classification** within one report. Keep the original direction-sensitive candidate_ref SHA-256 input for backward compatibility and preserve two different classifications for one pair (R63 regression contract).
- Keep local source digests, original input bytes, exact Decimal values, date logic, report formatting and human-only review; no automated fraud, eligibility, compliance or payment decisions.

## Synthetic verification

Run:
  PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_invoice_candidate_envelope_r92.py' -v

Also run under Python -OO. Existing R63 provenance tests, R4 scale tests, full repository source gate and six app smoke tests must pass. An isolated source-bound local test is NOT whole-repository or Windows EXE verification.

New tests cover absurd caps without iterator consumption, the cap boundary, smaller limits, untrusted types, reversed exact/near duplication, direction-sensitive fingerprints, cross-status compatibility, overlong rows, private diagnostics, source hashing, nonmutation and hostile Decimal context.

## Release boundary and next step

GitHub-hosted jobs currently fail before executing source-tests or windows-build (incident #75). Pending real CI, full native Windows 11 x64 packaging and six-app smoke checks, scanning, checksums, signing/unsigned disclosure, premium entitlement validation, distribution and independent QD/founder approval, **all six executables remain unreleased.** Never publish premium artifacts without server-side entitlement.

Highest-impact next action: repository/admin owner resolves Actions runner startup; obtain a full source gate PASS, then native Windows build and six executable smoke evidence. Keep R92 stacked as a draft for independent review.
