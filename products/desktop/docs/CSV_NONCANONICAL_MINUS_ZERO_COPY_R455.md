# Final Vestige Labs R455 — noncanonical minus review safety and zero-copy numeric preflight

**Issue:** #73. **Parent:** R454 draft PR #2644, pinned commit 677c67a90d8c222668d434f07e4fbb4b41e3b1ec. **Status:** stacked DRAFT; **QD / founder release HOLD**.

## Defect and behavior

The shared CSV formula guard deliberately accepts a canonical ASCII negative Decimal such as -42.10 (including after import-ignorable prefix marks), and rejects noncanonical negative expressions. Two visually minus-like characters were not covered: U+2212 MATHEMATICAL MINUS SIGN and U+2796 HEAVY MINUS SIGN. Neither belongs to the canonical ASCII Decimal grammar. A human could confuse them with a real financial negative while some spreadsheet importers could interpret the value as text. R455 makes both signs require spreadsheet-safe escaping/review, like other noncanonical minus tokens. This is an evidence-clarity policy, **not** a claim either character executes formulas.

The normal engine.safe_cell sanitizer calls has_unescaped_formula_prefix and prepends an ASCII apostrophe to such noncanonical signs, preserving their original visible characters; direct lower-level CSV publisher callers must supply sanitized cells. ASCII negative Decimals remain allowed. No source data are normalized or rewritten.

The previous canonical negative-number recognition passed value[index:] to a regular expression, allocating a copy of up to the 1,048,576-character source cell after a leading ignored mark. R455 instead uses Pattern.fullmatch(value, index) to preserve the same anchored ASCII grammar without allocating a substring.

## Artifacts

- products/desktop/fvs_suite/csv_formula_guard.py — production prefix guard and zero-copy match.
- products/desktop/tests/test_csv_negative_decimal_zero_copy_r455.py — eight regression methods, seeded parity cases, memory and content-preservation proof.
- .github/workflows/desktop-source-evidence-r385.yml — normal and optimized regressions for Ubuntu and Windows.
- .github/workflows/desktop-build.yml — R455 normal and optimized tests before Windows x64 packaging.

## Executed evidence (November 15, 2026)

The exact Git-blob-matched production module and test file ran with standard-library unittest in an isolated minimal package on Linux CPython 3.13.5.

- Standard mode: **8/8 PASS**.
- Optimized -OO -W error: **8/8 PASS**.
- Python compileall: **PASS**.
- A parity test generated 100,000 deterministic trial inputs and compared original substring-based and new position-based regex behavior for ASCII negative prefixes.
- Local tracemalloc peak: **1,382 bytes** for a 950,005-character synthetic negative Decimal preceded by a zero-width mark; the test enforces a 100,000-byte ceiling, not a platform-wide memory guarantee.
- Pre-fix source Git blob 79e49395947db9bf5f2ea26a323243c73968a1b1 reproduced **18 failing assertions/subcases** using these new regressions (not 18 failed test methods).

These 16 passing focused executions are **NOT** a full checkout, application-level integration, native Windows x64 execution, full six-app suite, Defender review, accessibility, signing, checksum or protected distribution validation. Hosted CI may still be blocked before tests.

## Scope and release gates

All six apps share this CSV safety boundary: four free (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and two premium (GrantAudit Studio Pro, ProcureGuard Studio Pro). Original financial data stay offline. Decimal-safe calculations, deterministic audit history, premium access controls and mandatory human compliance review are unchanged.

**Release hard hold:** do not merge, deploy, publish an EXE, offer unrestricted premium downloads, modify WordPress or claim approval. Restore Actions runner eligibility and complete source and Windows build tests, then independent QD review and explicit founder sign-off.
