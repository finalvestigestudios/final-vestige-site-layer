# R346 — ProcureGuard pre-callback source custody and exact numeral binding

**State: engineering draft only / QD + founder HOLD. Issue #73.** This change
stacks on R345 draft #1994, not production `main`. No executable was published.

## Problem demonstrated

R345 validates *callback outputs*, but not the original native source before
calling a custom parser. A callback could map `"-3"` (an invalid movement),
`"NaN"`, a huge source string, or `Decimal("Infinity")` to a permitted
`Decimal("3")`, hiding original financial evidence. It could also accept
unbounded strings before any data-size check. A numerical result being finite
is not sufficient evidence that the original financial input was valid.

## Correction

`fvs_suite/procurement_numeric_result_r345.py` now validates inputs before
injected callbacks: native types only; at most 80 characters for raw strings;
no ASCII controls, DEL or blank strings; bounded native integer/Decimal
coefficient/exponent/scale/range. All errors are privacy-safe with no raw input
or chained exception. For plain ASCII numeric strings (including scientific
notation), native integer and native Decimal inputs, exact numerical equivalence
is required *after* the callback. Parser outputs still undergo R345 bounded,
finite, exact `Decimal` validation. The original `Decimal` result and inputs
are not modified. Human review retains sole compliance decision authority.

**Scope limitation:** legacy accounting-formatted strings containing currency
symbols, correctly grouped commas or parentheses still defer interpretation
to the existing injected parser, because Python `Decimal` cannot directly parse
those formats. This helper does **not** authenticate source CSV bytes or detect
every malicious callback for accounting-formatted text; SHA-256 import
provenance and independent human review remain required. Existing suite
functions already parse and validate those financial formats for ordinary CSV
imports. Inputs such as scientific notation accepted by the standalone R345
helper remain available to maintain API compatibility, even though the
standard quantity CSV parser has a stricter fixed-point grammar.

## Evidence

Synthetic-only Linux CPython 3.13.5 helper harness, no repo checkout:

- `test_procurement_numeric_source_r346.py`: **31/31** `-W error` and **31/31**
  `-OO -W error`, no skips, using the exact R346 helper module.
- Against the original R345 helper (unchanged test cases): **24/31 failures**,
  demonstrating false acceptance or missing input checks.
- `test_procurement_numeric_source_integration_r346.py`: 12 new full-engine
  integration cases, **compiled but not executed locally**; require the real
  private checkout and CI. The 42 prior R345 helper tests, inherited procurement
  tests and 22 genuine AES-GCM integration cases were not run locally here.
- Native Windows 11 x64 executable builds, GUI/keyboard access, Defender,
  SHA-256, premium-entitlement delivery and live-site downloads: **not tested**.

### CI/owner unblock

The recent R345 desktop workflow run
[#42957363751](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42957363751)
recorded `failure` for both `source-tests` and `windows-build`, with **no
recorded steps**. Infrastructure root cause remains unverified. The existing
full-suite discovery should pick up both R346 files once runners are
provisioned. Owner: inspect failed check annotations, GitHub Actions billing,
spending limits, runner eligibility and workflow permissions; restore actual
Ubuntu/Windows test execution. Independent QD and founder authorization are
required before any merge, site publication or distribution.

## Suggested verification from a genuine repository checkout

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_numeric_source_r346.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_numeric_source_integration_r346.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_numeric_source_r346.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_procurement_numeric_source_integration_r346.py'
```

Then run complete desktop test discovery (including 22 genuine AES-GCM cases)
with strict zero-skip checks, and only then review native Windows acceptance.
No automatic compliance determination or payment authorization is introduced.
