# Final Vestige Labs R384 — Premium entitlement payload exception-chain privacy

**DRAFT / HARD HOLD — issue #73.** Stacked on R383 PR #2232, not on production main. Requires independent QD review and founder approval; does not authorize distribution, license issuance, compliance decisions, changes to WordPress, or deployment.

## Reproduced defect

The offline client verifier for **GrantAudit Studio Pro** and **ProcureGuard Studio Pro** translated malformed license JSON, invalid UTF-8, invalid UTC timestamps, signature decoding errors, and Ed25519 verification failures using exception chaining. The wrapped low-level exception remained accessible via __cause__/__context__; in particular, json.JSONDecodeError.doc stores the **entire local license document** and UnicodeDecodeError.object may contain the **complete input bytes**, including customer/holder metadata.

This was distinct from R383's file-reader error redaction. The four free desktop applications' engines and all financial calculations are untouched.

## Implemented scope

The module products/desktop/fvs_suite/offline_entitlement.py now translates four categories of expected low-level faults *after leaving their handlers*, preserving existing public messages and exception types while dropping original exception objects and their private nested data. The categories are UTC parse, document parse/decode, signature decode, and Ed25519 public-key/signature verification. Unexpected programming faults remain visible rather than being silently classified as bad entitlements.

No signature schema, trust authority, permission, expiry policy, product binding, canonical data, input size limit, or local file I/O mechanism changed. No private keys were stored. Test-generated Ed25519 keys are ephemeral and must never be pinned or distributed.

## Executed, bounded evidence — 2026-11-12

**Local Linux Python 3.13.5, cryptography 46.0.4:** 22 regression methods in test_entitlement_payload_privacy_r384.py. Against the pre-fix verifier logic, **14 of 22 failed** (the failing checks required an absent raw cause/context). After the fix, **22/22 passed** in normal warning-as-error mode, and **22/22 passed** in optimized warning-as-error mode = **44 focused passing method executions**. Python compileall passed.

Tests use genuine generated Ed25519 signatures and verification for **both premium product bindings**, plus genuine signature mismatch, expired/wrong-product/no-key fail-closed checks, malformed JSON with sensitive canary, malformed UTF-8 including retained byte objects, invalid times, base64/cryptography fault injection, duplicate-field/NaN rejection, single mocked read, stdout/stderr silence, and propagation of unexpected TypeError.

**Integrity qualification:** The new test file locally executed is byte-identical to committed Git blob ee319f2bf5f5d1f2d347bf15d7fc73e86271ab0c. Its locally tested verifier module is a **reconstructed functional copy of the GitHub source** with an isolated journal_io I/O stub (the tests patch _read_signed_entitlement), **not** an exact-HEAD repository checkout. Do not treat this as complete repository integration, exact-head unit test, native Windows x64, original-file custody, installed GUI acceptance, or authenticated premium distribution.

## Requested hosted gates

The internal .github/workflows/desktop-build.yml now adds this test module to Ubuntu and Windows **normal and optimized** prepackaging steps (four invocations). Total workflow content is 225,491 bytes, below the reviewed 229,376-byte ceiling. Presence of a CI step does **not** prove it ran.

Prior R383 [Actions #43275884822](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43275884822) returned failure for source-tests and windows-build, each with no steps. Underlying infrastructure issue/annotation is unverified. Owner should inspect the GitHub UI job annotations, Actions billing/spending limits, and runner eligibility, then rerun on this PR exact SHA.

**Next highest-impact gate:** Restore real hosted CI, run existing R11/R12/R13/R50 entitlement tests and the full six-app suite including 22 genuine AES-GCM cases; independently validate Windows x64 build, Defender scan, accessibility, signed/unsigned installer messages, checksum and gated premium entitlement/download flow. Do not merge or distribute until QD and founder approval.
