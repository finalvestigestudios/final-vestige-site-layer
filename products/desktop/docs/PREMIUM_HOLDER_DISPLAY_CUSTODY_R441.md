# R441: Premium entitlement holder display custody

**DRAFT / RELEASE HARD HOLD.** Scope: GrantAudit Studio Pro and ProcureGuard Studio Pro offline entitlement issuance and client verification. Issue #73. Stacked on R440 draft PR #2560, never production main.

## Failure reproduced

R440's issuer and client holder predicates both accepted five synthetic examples: U+202E bidi override, U+200B zero-width space, U+2028 line separator, U+0085 C1 control and U+D800 unpaired surrogate. R441 refuses all five. This is a display/evidence custody problem, not evidence that licenses were forged or customers impersonated.

## Implemented source changes

- A new pure fvs_suite/holder_identity.py accepts exact native Unicode strings of 1–120 codepoints, without leading/trailing whitespace, and refuses Unicode categories Cc, Cf, Cs, Zl and Zp. No locale, network, normalization rewrite, financial arithmetic, telemetry or I/O.
- license_issuer._validate_text refuses unsafe holder input before signing-key read or output creation, including hostile str subclasses.
- offline_entitlement.verify_license applies the same predicate to decoded JSON before Ed25519 signature verification. Visible non-ASCII names (e.g. French, Arabic, Japanese) remain eligible.
- The holder is human-facing audit metadata, not legal identity verification. Any genuine names requiring format controls must be handled by human review; never bypass or silently rewrite.
- No changes to Decimal logic, audits, privileged key configuration, trusted keys, product IDs or premium distribution controls.

## Evidence and committed tests

Exact committed Git blobs:
- fvs_suite/holder_identity.py — 23bea5b0401b8525ebb83c58e007b6335620b251
- tests/test_holder_identity_pure_r441.py — 61e797f01c9be771a9b581a4179ac3f10d2b1343

These blobs were independently matched by git hash-object in an isolated Linux Python 3.13.5 environment. **Actually executed against exact committed sources**: 4/4 unittest methods PASS in normal mode; 4/4 PASS under -OO -W error; compileall PASS. A controlled reproduction of R440's predicates returned accepted/accepted for all five unsafe samples, whereas the R441 predicate refused all five.

Five additional production integration methods were committed to tests/test_premium_holder_custody_r441.py but **have not been executed**. They cover real synthetic ephemeral Ed25519 signatures for both premium products, international holder names, unsafe control names, pre-key early refusal and shared-validator identity. The source-evidence workflow now calls both new test files in normal and optimized modes on Ubuntu and Windows.

There is no claim of full-checkout integration, native Windows execution, Defender health, working executable, entitlement deployment or public distribution.

## Blocker and next high-impact action

Parent R440 hosted CI [source #43671498872](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43671498872) and [build #43671498843](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43671498843) recorded 2 failed jobs apiece and zero steps/no assigned runner. Cause unconfirmed; those are not observed test failures.

First unblock: authorized owner reviews Actions billing/spending limits, policy and runner assignment. Rerun exact R441 commit and record job steps. Then execute inherited R11/R12/R13 and six-engine tests, genuine Windows x64 build/smoke, Defender, keyboard accessibility, SHA-256 verification and premium gated delivery checks.

**release_authorized=false.** No merge, signing keys, actual license issuance, downloads, premium file exposure, site publication or automated compliance decisions. Independent QD review and explicit founder approval remain mandatory.
