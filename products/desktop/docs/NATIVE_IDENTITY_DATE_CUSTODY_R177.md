# R177 — Native identity/date parsing custody (DRAFT / RELEASE HOLD)

## Working change
Five offline financial engines reuse `engine.key()` and `engine.parse_date()`. Both previously called `str(value)` on untrusted direct Python API inputs, permitting a user-defined `__str__`, `upper` or `strip` method to forge identity/date evidence or execute side effects before validation. The new `fvs_suite.identity_inputs` requires exact built-in strings **before conversion**, and `engine` delegates to it.

Original native CSV behavior remains: lossy ASCII uppercase key matching, ISO/US dates with calendar validation and whitespace trimming. This is **not proof of vendor identity or compliance**. Source SHA-256/physical row citations, private offline processing, Decimal money, immutable originals, and human review remain unchanged.

## Verification and limitations
- Source-only local unit target: `PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r177.py`
- Optimized target: `PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r177.py`
- Pinned 30-method test inventory: 24 rejection adversaries, 6 backwards-compatibility cases. Ubuntu/Windows normal and -OO require 120 executed focused method instances in CI, **not yet a CI pass claim**.
- Synthetic direct-API inputs only, no customer financial records; errors do not include attacker strings. The isolated local module tests do not establish full inherited repository tests, native Windows runtime, installed binaries or release approval.

## Hard release hold
All six Windows x64 apps remain UNRELEASED. Physical Windows 11 accessibility (46 observations), Defender/EDR, code signing, authenticated premium distribution, independent QD and founder approval are still required. CI runner-allocation failure is not a source-test pass or failure. No public download URLs, no premium exposure, no production changes.
