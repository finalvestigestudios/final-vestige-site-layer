# R501 — repair inherited PE certificate tests after zero-padding policy

**DRAFT / QD HARD HOLD.** Tracks #73. Stacked strictly on R500 draft #2889, never production main. No binary, license or download release.

## Reproduced regression (2026-11-17)

R499 correctly began rejecting **nonzero outer WIN_CERTIFICATE alignment padding**, but an inherited R497 positive test still expected seven ASCII z padding bytes after a one-byte payload to PASS. Both internal Actions workflows run this R497 suite, so restoring runners alone would not produce a clean run.

Linux CPython 3.13.5, using exact Git blobs of the R500 certificate guard (2a52e6d5812af3d111b1134d070c04e434ef5892) and original R497 test (1497f041e48302b15685db70c1682caa256be8f5): **11 passed, 1 error** across 12 methods. The error was the expected PECertificateError on the obsolete success fixture. Inert BytesIO data only; no actual executable.

## Remediation

1. Replace the obsolete inherited R497 positive with seven **zero** padding bytes; add an explicit negative test for the formerly accepted seven nonzero z bytes. New test-file Git blob: 8b6ba5d96a84b975e1bc8b830dbf780de0e76aea.
2. Add eight-method test_pe_certificate_compat_r501.py (Git blob 17b2329995cbd97f4c7c9b6202f151902af42caa): positive padding lengths 1–7, all 28 dirty padding positions, multi-record images, 128-record limit, short tails, redacted private I/O errors.
3. Add normal and optimized mode invocations of the R501 module in BOTH internal GitHub Actions workflows. The existing R497 and R500 coverage stays enabled, and no artifact-upload or QD gate changes.

## Exact-blob local verification

From a trusted checkout, run:

    PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_tail_r497.py
    PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_compat_r501.py
    PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_tail_r497.py
    PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_compat_r501.py

Executed locally with exact Git blob byte matches: R497 **13/13 PASS** normal and **13/13 PASS** optimized; R501 **8/8 PASS** normal and **8/8 PASS** optimized; **42/42 method executions**, no skips. Python compilation passed for guard and both test modules. Original R497 R500-parent fixture reproduced one error (negative control).

This is isolated Linux test evidence, NOT full repository or Windows integration evidence. R496, R498–R500 inherited modules, full six-app engine, native Windows packaging, Defender/EDR, keyboard smoke, real SHA256 manifest and premium gated distribution are NOT verified here.

## Blocker and next highest-value gate

R500 exact-head [source run #44121802738](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44121802738) and [Windows internal run #44121803729](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44121803729) both failed before any steps. Four Linux/Windows jobs report steps=null; infrastructure cause is unconfirmed. Owner: check GitHub Actions billing/quota, runner eligibility and workflow policy, or run the exact branch on a trusted Windows x64 checkout. Then execute inherited R496–R500, R501, the full six-app regression suite and EXE security/accessibility/premium entitlement gates.

No financial algorithms, Decimal behavior, local-first data processing, audit provenance, human compliance decisions, executable artifact, premium entitlement or live site changes. Independent QD review and explicit founder approval still mandatory.
