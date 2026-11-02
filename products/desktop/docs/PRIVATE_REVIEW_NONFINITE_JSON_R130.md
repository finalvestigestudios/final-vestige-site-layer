# Labs R130 — strict finite-only private review evidence intake

**Issue #73 · draft engineering changes · RELEASE HOLD · stacked only on R129 draft PR #564.**

## Defect and correction

Python's default `json.loads` accepts nonstandard `NaN`, `Infinity`, and `-Infinity` tokens. It also turns a syntactically valid, huge exponent such as `1e9999` into floating-point infinity. That means even an R9 report pinned by a purported SHA-256 could contain a nonfinite smoke-duration claim; `verify_r9` formerly checked the type and `seconds < 0`, so `float("nan")` and positive infinity passed that particular validation. A hash proves the bytes did not change after pinning; it does not prove the value is meaningful.

The private R109 custody module now invokes `json.loads` with **reject-on-constant** and **finite-only parse_float** hooks. This applies to R9 raw reports, review matrices, and all versioned reviewer witness records received through the shared strict parser, including JSON with nested invalid numbers. The direct `verify_r9` API additionally rejects programmatically constructed nonfinite float durations, so it cannot be bypassed by callers that never parse JSON. Finite nonnegative integer and float durations remain valid. Duplicate JSON keys remain rejected.

This is deliberately scoped to the Windows 11 private acceptance evidence boundary; the six Decimal-safe financial engines, input CSVs, original documents, premium entitlement logic, and site are unchanged. No value is silently repaired, rounded, or rewritten.

## Test contract

- `tests/test_windows11_nonfinite_intake_r130.py`: **18 named source-owned synthetic test methods** covering good six-EXE R9 reports, valid finite floats, explicit NaN/positive/negative Infinity, positive/negative exponent overflow, nested payloads, invalid review matrices, duplicate keys, direct in-memory nonfinite smoke durations, altered/rehashed witness files, four-free/two-premium pending states, redacted errors, and optimized-Python assert-bypass prevention.
- `scripts/safe_unittest_r130.py`: checks **exact 18-method inventory**, rejects errors/failures/skips, and suppresses traceback, paths and private witness content. Only safe aggregate counts and source-owned test-method names appear.
- `.github/workflows/desktop-build.yml`: source-owned mandatory Linux and Windows normal/`-OO` runs, **72 focused test executions** if both OS jobs complete; inherited full suites, six native Windows x64 builds, native smoke, sealed-transfer and privacy-safe evidence artifact gates remain required.
- Private review witness contents, customer data, executable candidates, encryption keys and premium app files must **never** appear in public CI logs, downloadable artifacts, or website pages.

## Threat model and release gates

Rejecting nonfinite JSON prevents non-portable representations and removes one way to counterfeit smoke elapsed-time evidence. It does **not** prove the physical Windows 11 assessment occurred, prove independence of an out-of-band R9 pin, provide trusted timestamps, defeat an administrator, make actual malware/EDR assessments, or validate commercial licensing.

**All six applications remain UNRELEASED.** Independent QD-approved private reviewer custody of exact six binaries with authenticated external R9 pin, **46 physical accessibility checks**, actual Defender/EDR assessment, code signing, authenticated premium delivery, independent QD approval and founder authorization are still required. No changes may be merged into production without the repository's existing QD gates.
