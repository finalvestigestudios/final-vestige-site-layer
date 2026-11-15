# R444 — Invoice Twin Scout direct review-flag evidence custody

Issue: [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). **Draft only / release_authorized=false.** Strict stack: parent R443 `759d98671a0c16962a33b40c8832e697ff2cc3c5`; never target production `main` or bypass independent QD and founder approval.

## Why this matters

The standalone `review_flags(a, b, status)` API can be called independently of `candidate_pairs`. Before this sprint it read `a["vendor"]`, `a["invoice_number"]`, `a["amt"]` and `a["dt"]` directly. Python `dict` subclasses can override `__getitem__`, returning fabricated financial audit values or raising exceptions that include sensitive client information. Unknown statuses silently yielded plausible empty flags; invalid `window_days` types could make date-review thresholds misleading or crash. This is an in-process source-trust boundary, **not** evidence that the default CSV importer was vulnerable.

## Production change

- `_owned_review_evidence` reads underlying `dict.items` and `dict.keys` descriptors, not subclass `get`, `keys`, `items` or `__getitem__` hooks. It validates native field-key strings, native visible source-label strings, exact finite `Decimal` money inside the existing candidate envelope, and plain calendar `date`. It never edits the originals.
- `review_flags` now requires a native recognized status (`exact_invoice_key` / `review_possible_duplicate`) and a native integer `window_days` in `0..365`; invalid calls fail with fixed-text `ValueError`. A fake source object cannot silently suppress required review flags.
- The original deterministic flags and precedence are unchanged for valid inputs: normalized vendor/invoice ambiguity, amount variance, distant dates, and opposing signed amounts all remain **human-review signals**, never automated fraud judgments or payment decisions. Negative zero remains non-credit; Decimal money stays exact and offline.

## Evidence actually run locally

This environment cannot clone the private checkout; therefore the executed tests used a **manually mirrored isolated projection** of the added production helper, amended `review_flags`, existing amount-bound validator and ASCII-case routine. This is **not** a full-module or exact Git-blob test result.

- CPython, `python -W error /tmp/labs_r444_projection_test.py -v`: **20/20 PASS**.
- CPython, `python -OO -W error /tmp/labs_r444_projection_test.py -v`: **20/20 PASS**.
- `python -m py_compile /tmp/labs_r444_projection_test.py`: PASS.
- Independent controlled pre-fix demonstration: a subclass `__getitem__` surfaced a synthetic private canary, and an unknown status returned an empty flag string. These are demonstrations of the old control-flow pattern, **not executions of a full pre-fix checkout**.

## Committed but not verified locally

- `products/desktop/tests/test_invoice_review_custody_r444.py`: **21 new full-module regression methods**. Includes actual `candidate_pairs` integration, spoofing, non-native evidence, unrecognized status, date thresholds, exact money, signed credit, deterministic originals and hostile Decimal context. These new methods were **not run** against the entire committed module in this environment.
- `.github/workflows/desktop-source-evidence-r385.yml`: schedules the 21 tests, and inherited R67/R93 direct-engine suites, under normal and `-OO` Python on the workflow's supported Ubuntu and Windows runners. Scheduling is not execution.
- Prior R443 exact SHA workflows [source #43683455462](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43683455462) and [internal build #43683455450](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43683455450) had two failed jobs each and no recorded steps. Root cause undetermined. Reinspect R444 exact-head workflows after draft PR creation; they may be equally blocked.

## Review and release gates

Owner: inspect GitHub Actions failure banners and annotations, account billing/usage, workflow permission and hosted-runner policy. Restore test execution, then run **this exact commit** with full six-engine source, full suite, genuine Windows x64 packaging/smoke test, malware scanning and signature/checksum evidence. Independently review QD and premium file access controls before any public catalog or executable links. Never publish an untested or unrestricted premium binary. No financial data leaves the desktop, and all compliance choices remain with people.
