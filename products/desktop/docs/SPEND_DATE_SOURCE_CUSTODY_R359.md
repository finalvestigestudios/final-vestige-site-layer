# R359 — SpendMap Original-Calendar Source Custody

**Status:** DRAFT / NO DISTRIBUTION / QD + founder release hold. Issue #73. Based only on R358 draft PR #2073; no production `main` edits.

## Why this was necessary

The source-bound SpendMap engine already independently verified money (R356), formatted money (R357) and vendor labels (R358). Its direct `summarize_spend(... parse_date=...)` callback boundary, however, accepted **any** native `datetime.date` returned by a caller, even when it described a different day from the original source CSV cell. A callback could therefore transform `2026-11-01` into `2026-12-01` while keeping exact monetary values, physical row references and a syntactically valid source SHA. This changes vendor-month totals, apparent trends and the periods used by spike-review rules. That SHA binds bytes; it is not proof that an unverified callback interpreted them faithfully.

## Exact implementation

- `fvs_suite/spend_date_custody_r359.py`: independently interpret original native date text using the shared supported calendar parser (ISO `YYYY-M-D`, US `M/D/YYYY`, `M/D/YY`). Reject str subclasses, invalid Gregorian dates, formula-like text and unsupported syntaxes without echoing private cells. Compare exact built-in `date` objects, not string representations or a mutable callback policy.
- `fvs_suite/spend_input.py`: preflight **all** frozen original source dates alongside source amounts **before any external callback**, and verify each callback's resulting day equals the independently parsed original. If dates differ, fail closed before any report is returned or saved. The existing input snapshot, 200k-row cap, Decimal context, source coordinates, signed-zero money protection and immutable row mapping remain in effect.
- New `test_spend_date_custody_r359.py` (21 methods) and `test_spend_date_engine_integration_r359.py` (12 methods) cover ISO and US formats, invalid calendar days, hostile input subclasses, callback month/day rewriting, future-row preflight, cross-format equivalence, full summarizer rejection and actual CSV-to-SpendMap preservation.
- `.github/workflows/desktop-build.yml`: eight mandatory normal and optimized Python command invocations (four Ubuntu + four Windows), gating both test modules before internal packaging.

## Verification and explicit limitations

- **Locally executed:** 21 focused helper tests PASS with standard Python 3.13.5, and 21 PASS with `python -OO` (42 method executions), using synthetic calendar values and a minimal local copy of the repository's native date parser. Both new test files and the helper passed Python syntax compilation.
- **Not executed locally:** the 12 new full-engine integration methods, the changed `spend_input.py` inside a complete private checkout, the entire inherited regression suite, AES-GCM integration cases and Windows executables. The integration methods are source-controlled awaiting an actual repository check. Do **not** describe the focused helper run as full-engine validation.
- **Hosted CI:** prior R358 run #43064611563 failed before steps began; source-tests and windows-build had no assigned runner. R359's own run/check status must be inspected separately after pushing; a failed or queued check does not count as test execution. Exact infrastructure root cause remains unconfirmed.

## Safety, boundaries, and release gate

All processing remains offline/local-first, with no telemetry, private-data upload, payment approval, automated compliance decisions, or alteration of originals. No EXE, premium asset, unrestricted download or site change is published. Independent QD review, founder release authorization, green exact-head CI, native Windows x64 builds/smoke, checksums, Defender, accessibility and protected premium fulfillment remain mandatory.

## Highest-impact next step

Restore hosted CI runner allocation (investigate check annotations, Actions spending/billing, runner eligibility and workflow permissions), execute **both** R359 test modules in the complete checkout on Ubuntu/Windows, rerun inherited desktop tests and the 22 genuine AES-GCM integration cases, and resolve any regressions before touching actual Windows distribution.
