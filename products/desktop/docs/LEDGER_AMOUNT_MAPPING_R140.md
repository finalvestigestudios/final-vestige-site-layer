# Labs R140 — independent LedgerDiff amount-header mappings (DRAFT / release HOLD)

**Scope:** LedgerDiff Lite only. Four free / two premium product inventory remains unchanged. No production site edit, public executable, premium unlock, or automatic financial approval.

## Problem and behavior

Bank and accounting exports frequently call the money field different things (e.g. `Debit Value`, `payment_amt`, `Credit Value`), or contain both `amount` and `total`. Previously LedgerDiff let reviewers select independent transaction-ID headers, but could not select per-side money headers. An incorrect auto-selection would be especially dangerous if duplicated aliases were present.

The LedgerDiff desktop form now provides **four blank-by-default optional fields**, ordered for keyboard access: left match-key header, right match-key header, left amount header, right amount header. Each source is mapped independently. A blank header retains existing automatic alias detection; if multiple automatic aliases match, import fails rather than choosing a column silently.

Accepted explicit headers are **ASCII identifiers after trim/lowercase/ASCII-space-to-underscore normalization**, with at most 128 characters and pattern `[a-z_][a-z0-9_]{0,127}`. The importer rejects absent headers, normalized duplicate CSV headers and selection of one physical column as both match key and amount. Error messages never echo private/untrusted candidate header values.

Each nonempty reconciliation row now includes `left_amount_column` and `right_amount_column`, preserving exact imported header spelling, alongside the existing match-header selection, physical CSV line references, original source SHA-256, differences and independent human-review flags. The input digest is computed from the verified descriptor snapshot that supplied the rows, not a later path read. **Empty input exports retain a header-only output and cannot falsely claim a row-level fingerprint.**

## Synthetic operator demonstration (not financial advice)

- Left: `Payment Reference,Debit Value\nX-1,1.25\n`
- Right: `pay_ref,Credit Value\nX-1,1.25\n`
- Select left/right match-key headers `Payment Reference` / `pay_ref`.
- Select left/right amount headers `Debit Value` / `Credit Value`.
- A genuine match has `difference=0.00` with source/amount header evidence. Where normalized source IDs collide, totals differ or duplicated rows appear, the existing review flags continue to apply.

This mapping does **not** perform debit/credit sign conversion, prove a bank transfer occurred, resolve fraud, confirm payment eligibility, or replace a human reviewer. Never import customer material into CI or issue comments. Source files are not modified. CSV output is private and atomic but is not a signed audit attestation.

## Verification and release gates

- Strict test runner: `python products/desktop/scripts/safe_unittest_r140.py`.
- Optimized anti-assert bypass: `python -OO products/desktop/scripts/safe_unittest_r140.py`.
- Exactly **24 synthetic test methods** are required in each mode and on each of Ubuntu/Windows (**96 targeted executions planned**). Full source suites and six candidate binary smoke/premium lock/keyboard/200%-400% scaling checks remain separate required gates.
- The legacy R131/R132/R133 automated keyboard/scroll/match-key tests were updated to the new four-field GUI inventory; the native Windows probes must actually pass, not be waived.
- Passing CI **is not** a physical Windows 11 acceptance or release authorization. Independent six-EXE custody, 46 hands-on observations, real Defender/EDR assessment, code signing, authenticated premium distribution, independent QD review and founder authorization are still **HARD HOLD** requirements. All six apps remain **UNRELEASED**.
