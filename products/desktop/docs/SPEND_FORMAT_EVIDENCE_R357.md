# Labs R357 — SpendMap exact output money evidence

**Status:** DRAFT ONLY. Issue #73; stacks on R356 draft; no merge, distribution, site publication or premium entitlement changes. QD and founder approval remain required.

## Defect and scope

R356 binds incoming amounts to the original native source text, but `spend_analysis.summarize_spend()` still accepted unchecked `format_money` callback results when constructing `amount`, `gross_charges`, `gross_credits`, vendor-month totals and gross flows. A callback can convert a valid exact `Decimal('100.00')` into the string `'9000.00'`. The report then carries a correct source-row/source-hash reference alongside a **false exported financial number**. A nontext or formula-prefixed string also reaches the report writer. Decimal-context isolation from R355 does not solve that semantic mismatch.

R357 adds `fvs_suite.spend_format_custody_r357.verified_spend_money_display()` and applies it to all six `report_money` calls in `spend_analysis`. The validator accepts only bounded, ASCII, exact fixed-point representations with optional conventional dollar currency, grouping, plus/minus sign or accounting parentheses; it disallows subcent strings, exponential notation, locale guessing, nontext callbacks, spreadsheet formula prefixes and changed negative-zero signs. No implicit rounding. Formatter exceptions are replaced by a non-sensitive generic error with no exception chaining. The stored source rows are not rewritten. The native shipping formatter `engine.dollars` is compatible (`format(decimal, '.2f')`). This is a report-evidence safeguard, **not** proof that source bytes are authentic or compliance approval.

## Evidence and gated next steps

- Execute `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_spend_format_custody_r357.py'`, then `python -OO -W error` variant.
- Execute the genuine `test_spend_format_engine_integration_r357.py` on the complete feature checkout under both modes and run all inherited desktop suites.
- GitHub Actions desktop workflow adds these tests to **both Ubuntu and Windows jobs**; native Windows execution remains mandatory.
- Run the 22 AES-GCM genuine integration tests, six Windows x64 builds and smoke/Defender/accessibility checks after runner restoration. Verify premium gating independently before any release; no public binary URLs.

### Release hold

No execution on a native Windows x64 runner, real production files or premium distribution has been authorized. All final compliance/payment decisions require human review. Preserve QD sign-off and founder approval before production merge.
