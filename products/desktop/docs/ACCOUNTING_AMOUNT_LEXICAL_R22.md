# R22 — strict accounting amount lexical integrity

## Defect and consequence

Earlier `engine._exact_amount` removed **every** `(`, `)`, `$` and comma via `strip("()").replace(...)`. An unclosed negative such as `(100.00` therefore parsed as **positive 100.00**, and `1,2,3` parsed as **123**. These are audit-relevant changes of sign or magnitude, not harmless formatting changes. R22 replaces lossy punctuation removal with validation of the complete source lexeme **before** creating a `Decimal`.

## Supported input grammar

- Plain decimal digits, optional leading `+`/`-`, and fractions: `1000`, `1000.50`, `.50`, `1.`.
- Optional **leading** `$` currency marker: `$1000.50`, `-$10`, `$-10`.
- Proper three-digit comma groups only: `1,234.56`, `1,000,000`.
- Matched accounting parentheses for negative amounts: `(123.45)`, `($1,234.56)`.
- Surrounding whitespace is ignored; extra internal whitespace, broken parentheses, mixed signs, misplaced currency symbols, incorrect comma groups, exponent notation and nonfinite values **fail closed**.
- Existing numeric bound of 1,000,000,000,000 is retained. A maximum 80-character input lexeme avoids unbounded conversion work. Values are parsed exactly as `Decimal`; `money()` still rounds to cents using `ROUND_HALF_UP`, while `unit_cost()` retains up to eight fractional places.

If a source financial system exports exponent notation or another unsupported convention, normalize the CSV explicitly in a **separate reviewed preprocessing step** and retain the original file. Never infer the intended sign or grouping silently.

## Coverage and privacy

The shared parser is used by **LedgerDiff Lite**, **Invoice Twin Scout**, **SpendMap Lite**, **GrantAudit Studio Pro**, and **ProcureGuard Studio Pro**. **Policy Delta Desk** performs textual comparisons and does not parse money. New regression tests cover valid notation, rejection of 26 malformed forms, precision and bounds, redacted validation errors, and early failure without reports across each of the five financial products.

On validation errors, the parser does not echo raw rejected values. Financial files remain local; no telemetry, upload, automatic compliance decision, or changes to originals are introduced.

## Evidence and release gates

- Isolated implementation tested on Linux Python 3.13.5: **4/4 focused test methods passed** under both normal interpreter and `python -OO`; `compileall` passed. This tests the exact proposed parser body, **not** the full checked-out GitHub repository.
- The committed `test_amount_lexical_integrity_r22.py` defines **nine repository test methods**, including five engine-integration cases. These **have not yet been executed against the complete repository** because hosted runners are currently failing before their first step.
- CI workflow includes the R22 tests under `-OO`, in addition to existing full-suite discovery; actual successful CI execution is still required.
- All native Windows x64 executable builds and clean-host smoke tests, antivirus/security verification, premium distribution authorization, and site QD approval remain **unverified and blocked for release**.

**Next:** Recover GitHub Actions runner execution, then execute full repository regression and source-level smoke; separately run `products/desktop/scripts/verify-windows-candidate.ps1 -Build` on a trusted Windows x64 workstation. Inspect failed imports/fixtures and update tests/code until all pass, then proceed with independent review. No executable or download is authorized by this sprint.
