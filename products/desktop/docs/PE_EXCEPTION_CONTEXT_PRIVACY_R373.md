# Labs R373 — PE verifier exception-chain custody (DRAFT / QD + founder HOLD)

## Scope and reproduced defect

The shared Windows x64 candidate verifier for all six desktop tools already redacted text from os.open, os.fstat, os.fdopen, stream enter, exit, read and seek failures, but raised sanitized errors inside an active exception handler using 'raise ... from None'. Python still retained the original exception in PEFormatError.__context__; programmatic diagnostics traversing that object could recover confidential paths or OS messages even though normal tracebacks hid the cause. This is the same class of privacy issue corrected in the separate R372 smoke runner.

A local test of the **exact unchanged R372 PE source** (Git blob c01c2756327f4f1613dc240986616c356803c4fc) reproduced **10 failures among 14 initial adversarial tests**, all for retained private exception chains.

## Implementation and guardrails

- Raise sanitized PEFormatError only **after leaving** the relevant open, metadata, descriptor, and stream fault handler. The stream context manager now focuses on ownership and cleanup; the caller classifies unexpected stream faults outside its active exception handler. Errors thrown into a generator at yield can otherwise remain active in the outer caller.
- Preserve specific PEFormatError messages for malformed PEs, plus KeyboardInterrupt/SystemExit passthrough.
- Preserve raw descriptor closure after failed metadata/fdopen, stream closure after failed enter, existing AMD64/PE32+ and W+X checks, unchanged original bytes, and no candidate execution during static inspection.
- No financial data is uploaded, logged or altered. No Decimal money logic, premium licensing, compliance decision, QD approval or website publishing logic was changed.

## Local test evidence

Exact local Python 3.13.5 source and test files matched committed Git blob hashes, without a full private-repository checkout:

| File | Committed Git blob |
| --- | --- |
| products/desktop/pe_image_guard.py | edb2ca7c493c67b56dc397f888e259b0f912856c |
| products/desktop/tests/test_pe_private_chains_r373.py | d2bcc6a61f868b2eff48122ee6dec5cadc1a9a78 |

Executed against those identical files:
- python -W error -m unittest -q test_pe_private_chains_r373: **17/17 PASS**
- python -OO -W error -m unittest -q test_pe_private_chains_r373: **17/17 PASS**
- python -m compileall -q pe_image_guard.py test_pe_private_chains_r373.py: **PASS**

Adversarial matrix: private open/metadata/fdopen/enter/exit/read/seek exceptions; both __cause__ and __context__ empty; inert PE bytes unchanged; raw descriptors closed; deliberate interrupt propagation; specific structural errors; all six launcher names with inert synthetic fixtures.

**Limits:** 34 local method executions, not a complete inherited regression suite. Local execution was on Linux, not Windows x64. Synthetic PE headers do not prove Defender cleanliness, signing, actual PyInstaller binary execution, premium entitlement or safe distribution.

## CI and release hold

The internal .github/workflows/desktop-build.yml now invokes the new R373 test four times (standard and -OO on Ubuntu and Windows). Its text remains below the inherited 224 KiB ceiling. Hosted CI is **not claimed green**. The preceding R372 run 43172769932 failed without recorded runner steps for source-tests and windows-build; runner/account-level cause is not confirmed.

**Hold:** PR stays draft and stacked only on R372. No merge to production, no website changes, no executables or premium file distribution, and no QD/founder approval bypass.

**Next highest-impact step:** Restore GitHub Actions runner eligibility (inspect billing, spending limits and failed-check annotations), run the complete six-app suite including 22 genuine AES-GCM cases, then conduct Windows 11 x64 acceptance for actual portable EXEs: checksums, smoke, Defender, accessibility and premium entitlement verification.
