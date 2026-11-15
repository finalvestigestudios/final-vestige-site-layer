# R440 — premium issuer CLI and registry teardown error custody

Tracking: [Final Vestige Labs issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This is **draft-only**, stacked on R439 draft [PR #2554](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2554) at exact parent `cbeab94457cd1b7dc2e205953c2dcfd69e1c7af2`. Production `main` and the QD gate remain untouched.

## Failure modes

1. The operator-side `IssuanceRegistry._db()` context manager previously called `conn.close()` directly in `finally`. A SQLite/OS teardown fault could escape with private diagnostics (SQL, internal paths) or replace a meaningful, already-issued public refusal. After a successful commit, a failed close is still **ambiguous**, not proof the operation failed: never retry an ID automatically.
2. `license_issuer.main()` previously printed `str(exc)` for arbitrary `OSError` and `ValueError`. Such errors can include private signing-key paths, registry locations, or source diagnostics. It also invoked `argparse.ArgumentParser.exit` *inside* the exception handler, so the resulting outward `SystemExit.__context__` could retain the original private exception. Unhandled `sqlite3.Error` likewise could propagate a raw traceback.

## Implemented code

- `license_registry.py`: close the SQLite connection on either outcome. On any already-failing path, attempt close but **preserve the original exception** if close also fails. On a successful body followed by an SQLite or OS close fault, refuse outside its handler with a generic `RegistryError`; never equate it with a safe retry. Preserve committed reserved/issued records for human inspection.
- `license_issuer.py`: keep informative messages from the three **owned, sanitized** exception classes. Translate unexpected OS, value and SQLite exceptions into a fixed non-private refusal. Call `parser.exit` **after** the handler exits, preventing raw `__context__` retention. Keep confirmation, offline signing, registry reserve-before-key, exact SHA-256, and manual fulfillment controls unchanged.
- `tests/test_premium_issuer_fault_custody_r440.py`: **11 committed regression methods** using synthetic SQLite, injected connection-close faults, CLI mocks and private diagnostic canaries. Tests assert durable reservation/finalization custody, original-refusal preservation, redacted visible messages, cleared public error chains, no false issuer success and unchanged normal operation.
- `.github/workflows/desktop-source-evidence-r385.yml`: run R440 and inherited R439/R12/R13 tests in standard and optimized Python on Ubuntu and Windows, once hosted runners execute.

## Executed evidence and limitations

On isolated Linux Python 3.13.5, a **standalone projection** of the two touched boundaries was executed against real temporary SQLite and synthetic CLI exceptions. `python -W error -m unittest` **11/11 PASS**, `python -OO -W error -m unittest` **11/11 PASS**, `compileall` PASS. A controlled version of this *projection* with the original pre-fix exception handling produced **5 failures and 4 errors out of 11**. The local projection is deliberately not described as a full checkout, exact committed test file or complete production module test. **The 11 committed full-module regressions and inherited suites were not executed locally.**

At R440 implementation start, the exact R439 parent workflows were still red **before test execution**: [source verification #43666015111](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43666015111) and [Windows internal build #43666015175](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43666015175). Four jobs, zero recorded steps and no runner names; underlying infrastructure cause remains unconfirmed. Inspect the new R440 workflow jobs independently rather than inferring a test result from a red job without steps.

## Release and reviewer gates

No real signing keys, customer data or licenses were used. `release_authorized=false`. No release, EXE, installer, premium file, public URL, payment/entitlement issuance, WordPress deployment or merge to `main`. This does not establish Windows compatibility, Defender success, signed binaries, an authenticated premium download service, or financial/compliance approval.

**Next highest-impact step:** Restore GitHub Actions runner startup (Actions permissions, org/account billing and spend limits, hosted runner eligibility). Execute R440 + inherited tests at the **exact R440 commit** with real job-step logs; then the full six-app Decimal, provenance, accessibility and premium authorization regressions. Produce actual Windows x64 builds, smoke tests, Defender scans, SHA-256 receipts and protected premium distribution checks. Require independent QD review and explicit founder approval before release.
