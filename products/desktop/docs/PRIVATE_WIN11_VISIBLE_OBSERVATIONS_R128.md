# Final Vestige Labs R128 — unambiguous private Win11 witness observations

**Issue #73 · DRAFT / HARD RELEASE HOLD · stacked on R127 #557, not main.**

## Why the check is necessary

The original source-bound R110 evidence notes rejected ASCII controls and a narrow group of bidirectional overrides, but accepted C1 control characters, other invisible Unicode formatting, nonstandard whitespace, variation selectors and visually blank filler glyphs. A human reviewing a note could see text that differs materially from its hashed bytes. Rehashing a locally altered witness does not cure ambiguity.

R128 places a conservative display-integrity predicate inside the shared existing witness validator. This catches both new v2 notes and historic v1 notes, even when a modified note carries a newly computed local SHA-256 digest. The R122 one-check recorder calls this validator before writing, so refusal preserves the previous review matrix and creates no accepted witness.

The guard rejects Unicode control/format/surrogate/line-separator categories except ordinary tab/newline; nonstandard whitespace; variation selectors; and explicit known blank/filler code points. Ordinary multilingual letters, combining accents, spaces, tabs and line breaks remain valid. This guard is not a full confusable-text detector. Some joined emoji/complex-script sequences need to be described in plain text rather than using invisible joining characters. Do **not** silently rewrite previously recorded evidence that now fails; retain it for human review and establish a new authorized session.

## Exact test contract

The new source-owned test file has **14 synthetic test methods** covering both witness versions, visible multilingual and ASCII layout, C1/bidi/zero-width/variation/blank/space/tag/surrogate rejection, actual R122 writer fail-closed and private cleanup, premium-locked check parity, rehashed witness rejection, redacted CLI output, and assertion-free production logic. A dedicated runner rejects missing, extra, skipped and unexpected methods while suppressing private exception details.

Mandatory Linux and Windows CI run the same 14 methods under normal Python and optimized `-OO` (56 method executions total if all four runs succeed). Existing source, native six-Windows-EXE packaging, encrypted transfer, four-free/two-premium-locked GUI preflight and artifact allowlist remain unchanged. **Only exact-head Actions completion can verify CI success.**

The new predicate cannot attest that a reviewer actually performed an accessibility test, that a timestamp is independently trusted, or that an AV/EDR scan detected all threats. **All 46 physical Windows 11 checks, QD-approved secure custody and independent R9 fingerprint, actual Defender/EDR, code signing, gated premium distribution, independent QD approval and founder authorization are still required. All six apps remain unreleased.**
