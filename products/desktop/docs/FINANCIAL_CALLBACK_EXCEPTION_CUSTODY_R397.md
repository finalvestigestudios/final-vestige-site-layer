# R397 — Private financial callback exception custody (2026-11-13)

**Issue:** [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73)  
**Change type:** source-only, draft branch stacked on R396 draft #2310, **not** a Windows release.  
**Affected:** SpendMap Lite (free) and ProcureGuard Studio Pro (premium).

## Failure mode / concrete reproduction

Python's `raise ValueError("redacted") from None` from **inside** an `except`
hides a traceback in ordinary display, but retains the originating exception in
`ValueError.__context__`. An injected financial parser/formatter exception
can carry the original private CSV bytes, source field or path on its instance.
A caller inspecting/serializing the exception graph could recover it.

An isolated Linux CPython 3.13.5 comparison with a synthetic
financial exception carrying a confidential byte marker showed:
- Previous in-handler translator: `__context__ is not None`, including
  reachable `UnicodeDecodeError.object` / `JSONDecodeError.doc`.
- Translator executed **after** the handler: `__context__ is None`,
  `__cause__ is None`, generic message retained.
- Local *standalone control-flow rehearsal*, NOT a repository test:
  10/10 synthetic tests passed in normal Python and 10/10 in `-OO -W error`
  (20/20 test executions). It tested the error-translation pattern, private
  payload/JSON/OS exceptions, Decimal return identity, and context restoration.

This is an in-process potential disclosure mechanism, not proof of a
customer-data breach. Synthetic inputs only.

## Implemented on isolated branch

- `fvs_suite/procurement_numeric_result_r345.py`: quantity/unit-price
  callback failures now exit `localcontext()` and the originating handler
  before a generic `ValueError`. Parser input bounds, exact Decimal equality,
  signed-zero checking, permitted negative unit prices, and callback context
  restoration are unchanged.
- `fvs_suite/spend_input.py`: same translation for original source money/date
  validation, vendor normalization, date parser, money parser, and cent-check
  exceptions. Existing physical-row diagnostics, preflight of all rows,
  source-backed dates/money and source row non-mutation remain unchanged.
- `fvs_suite/spend_analysis.py`: report-money formatter callback failures now
  translate after the originating handler. Numeric format custody still checks
  the displayed amount against the exact Decimal original.

There are **eight** deliberately scoped exception-boundary changes. None
enables automatic compliance decisions or modifies the source, report or
premium licensing flow.

## New committed tests and CI

`tests/test_financial_callback_exception_custody_r397.py` contains **22
synthetic regression test methods** for both apps. Cases include nested private
exception payloads, UTF-8 and JSON parser failures, non-callable callbacks,
invalid originals, normal exact Decimal output and changed Decimal contexts.
The tests require `__context__ is None`, `__cause__ is None`, a generic
diagnostic, and preserved exact-money behavior.

Added normal and `-OO -W error` test commands to independent Ubuntu/Windows
source evidence workflow `.github/workflows/desktop-source-evidence-r385.yml`,
before source smokes, Decimal/provenance, AES-GCM, and Ed25519/SQLite gates.

**Evidence limits:** isolated Python reproduction above was executed locally;
the **22 committed real-import test methods were not executed in the complete
checkout locally**, because the runtime lacks a repository clone and cannot
connect directly to GitHub. Native Windows testing, source integration,
cryptography, real EXEs, malware scanning, accessibility and premium delivery
remain unverified. Do not infer passing CI from green source code.

## Independent release and QD hard hold

Current parent R396 workflow runs:
- [six-app source workflow #43382853096](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43382853096)
- [desktop build workflow #43382853145](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43382853145)

Both were marked failed **before recorded steps or runner assignments**.
The exact underlying reason remains unconfirmed; check-run annotation bodies
are not exposed via available connector access.

**Smallest unblock:** owner reviews the failure annotations, GitHub Actions
billing/spending limit and hosted-runner eligibility, then reruns exact R397
HEAD and executes all 22 new tests on actual Ubuntu and Windows checkouts.

**Next highest-impact gate:** restore hosted CI, run inherited R345/R355/R396
and full six-app Decimal/crypto tests, then real Windows x64 packaging,
Defender scan, accessibility, license gating and human QD/founder approval.

No push to `main`, no merge, production site change, EXE release, open
premium download URL or compliance automation is authorized.
