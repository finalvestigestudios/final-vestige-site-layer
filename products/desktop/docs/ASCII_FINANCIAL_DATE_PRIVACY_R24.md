# R24 — ASCII financial/date lexemes and confidential parsing errors

**Status:** development draft only; no application, installer, premium entitlement, or website release is authorized. All accounting and procurement findings require human review.

## Problem and scope

Previously, the R22 accounting amount expression used Python regular-expression `\\d` and the date parser handed unrestricted text to `datetime.strptime`. Python's Unicode digit matching can interpret non-ASCII numeric characters that visually resemble ASCII digits. Invalid date errors also included the **entire original cell**, potentially displaying customer-provided sensitive text in desktop errors or copied logs.

R24 deliberately enforces ASCII numeric characters (`0` through `9`) in the shared amount and date lexemes. It refuses Python binary floats and booleans passed to amount helpers, avoiding conversion of inexact programmatic inputs through `str()`. Invalid date exceptions no longer echo their source value.

Impacted app intake:
- **LedgerDiff Lite:** amount values.
- **Invoice Twin Scout:** amount values and invoice dates.
- **SpendMap Lite:** amount values and spend dates.
- **GrantAudit Studio Pro:** claim, ledger and budget amounts (including linked allocation paths through the shared parser).
- **ProcureGuard Studio Pro:** unit prices and amount paths through the shared parser; R23 quantity grammar already required ASCII digits.
- **Policy Delta Desk:** text-only comparison remains unchanged and is not a financial parser.

## Accepted formats

- Currency/money: plain or correctly comma-grouped ASCII numerals, optional conventional dollar prefix and sign, or matched negative accounting parentheses; cent rounding remains Decimal `ROUND_HALF_UP`. R22 magnitude, grouping and precision bounds remain enforced.
- Unit price: exact Decimal with no more than eight meaningful decimal places.
- Dates: ASCII `YYYY-M-D`, `M/D/YYYY` or legacy `M/D/YY` (zero-padded equivalents accepted); calendar validity is checked. Leading/trailing whitespace is stripped.
- **Legacy two-digit years remain accepted for compatibility** using Python's `%y` interpretation (00–68 → 2000–2068, 69–99 → 1969–1999). Financial exports should **prefer four-digit years** to eliminate century ambiguity. The parser does not infer locale-specific day/month layouts.

Rejected examples: Arabic-Indic or fullwidth numerals; malformed comma grouping; nonfinite/exponential amounts; binary-float direct API values; dates containing non-ASCII digits, timestamps, invalid calendar days or unrecognized separators. No automatic transliteration or locale conversion occurs. Operators must review and explicitly re-export ambiguous input from the source system rather than allowing silent normalization.

## Deterministic and privacy requirements

- Source financial CSVs are not modified; invalid input must fail before an analysis report is saved.
- Invalid date/amount errors must not contain the original cell text; existing filename/source-row messages can still identify input locations.
- No uploads, telemetry, cloud analysis, automatic compliance outcomes, payment approvals or license changes.
- Human review is required for all review flags, ambiguous identifiers, credit/return events and compliance findings.

## Executable evidence and remaining gates

The isolated R24 Python harness passed **9/9 tests normally and 9/9 under `python -OO`** and compiled successfully on the local Linux interpreter. It duplicates the exact amended amount/date parser logic and tests only that logic; it **does not execute the connected GitHub repository, the 14 committed repository tests, or real Windows x64 executables**. Full regression and Windows release verification remain outstanding.

From a trusted checkout, run:

```sh
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_ascii_data_privacy_r24.py' -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_ascii_data_privacy_r24.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
```

On a trusted Windows 11 x64 machine, also use `products/desktop/scripts/verify-windows-candidate.ps1 -Build` and retain six executable hashes, native smoke outputs, malware/signing evidence and protected premium entitlement verification. **Independent QD approval remains mandatory; do not publish from draft development branches.**
