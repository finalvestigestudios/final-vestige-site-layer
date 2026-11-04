# Labs R173 — ProcureGuard threshold/stream native primitive custody (DRAFT / RELEASE HOLD)

## Defect and observed exploit shape

ProcureGuard's `exact_policy_limit` previously accepted `isinstance(value, (str, int))` and then called `str(value)`. A Python API caller could pass a `str` or `int` subclass with an overridden `__str__` to make the stored threshold appear different when parsed (for example, native numeric 9999 represented as `"0"`). Such subclasses can also run unexpected hooks during error handling. The ordinary on-disk JSON policy parser produces genuine built-in primitives; this is a **direct-call integrity** correction.

The procurement stream classifier also previously consulted the `_EVENT_TYPES` dictionary before establishing that `source` was a built-in `str`. A hostile direct caller could supply a `str` subclass with custom hashing/comparison hooks.

## Change

- Require **exact built-in `str` or `int` type** for a direct price threshold before any string conversion. This preserves all valid JSON strings and integer limits, rejects booleans/floats/Decimal objects as before, and adds subclass rejection.
- Require **exact built-in `str`** for `source` before membership tests. Ordinary `invoice` and `receipt` stream behavior remains unchanged.
- Keep bounded ASCII fixed-point syntax (up to eight fractional places), Decimal parsing, maximum ranges, private source-value redaction, and human-review-only price exceptions. No financial data is uploaded, edited or published. The grant claim parser and both premium entitlement locks are untouched.

## Regression and CI contract

`tests/test_procure_policy_primitive_r173.py` defines exactly **31 methods** with synthetic values: deceptive string/int subclasses, explosive formatting/equality/hash hooks, numeric bounds, valid JSON primitive compatibility, privacy-safe errors, genuine credit/return classification, and unaffected grant claim classification.

`scripts/safe_unittest_r173.py` enforces the exact static inventory and rejects skipped/missing/failed tests, with privacy-redacted summaries. Required gates execute **normal Python and `-OO`** on both Ubuntu and Windows for **124 expected focused method executions** (31 × 2 interpreters × 2 OSes). They supplement, not replace, the complete inherited tests and the six private Windows x64 executable integrity/smoke checks. Never claim these checks green until the **exact feature-branch SHA**'s CI completes and logs confirm it.

Local check (from repo root, with `PYTHONPATH=products/desktop` set on Windows): `PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r173.py` and `PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r173.py` on POSIX.

## Governance / acceptance limits

**OPEN DRAFT ONLY.** Stack R173 on R172 draft PR #861, not `main`. This work closes an input-identity issue, not any Windows release acceptance gate. No arbitrary Python object is considered authenticated financial evidence; review remains a human decision.

All six products remain **UNRELEASED**. Independent real Windows 11 witness acceptance (46 observations), genuine Defender/EDR review, code signing, authenticated premium distribution, independent QD assessment, and founder signoff are still required. Never publish public binaries, premium packages or download links based on this sprint's synthetic CI.

Next highest-impact external step: independent physical Win11/QD reviewer runs the private, SHA-256-pinned candidate acceptance process, captures the 46-observation audit, and performs genuine Defender/EDR checks before release approval.
