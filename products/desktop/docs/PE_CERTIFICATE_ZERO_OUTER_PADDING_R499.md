# R499 — zero-only outer WIN_CERTIFICATE alignment padding

**Status: DRAFT / QD HARD HOLD.** Tracks issue #73. Stacked on R498's exact draft head, never on production main. No merge, binary, installer, website link or premium download authorized.

## Defect and correction

The shared six-app PE32+ candidate verifier accepted arbitrary bytes between a WIN_CERTIFICATE record's declared dwLength and its next eight-byte boundary. R496 even tested acceptance of seven Z bytes in that gap. This is too permissive for the suite's conservative executable format policy: the PE/COFF specification requires that the alignment padding outside dwLength be zero-filled.

R499 reads **at most seven extra bytes per record** on the *same unbuffered descriptor* used for PE parsing and the digest. It rejects nonzero padding, short reads and I/O errors with fixed diagnostics that do not retain private exception context. It never reads or executes the PKCS#7 payload. Unsigned images, aligned records and properly zero-padded records remain supported.

**Not Authenticode:** This only checks outer record alignment padding, not extra data inside PKCS#7 SignedData. It cannot prove cryptographic signature validity, chain trust, malware safety, or the effect of Windows EnableCertPaddingCheck. Some legacy binaries may be incompatible with this conservative policy. Review, do not silently bypass it.

Official background: https://learn.microsoft.com/en-us/windows/win32/debug/pe-format and https://learn.microsoft.com/en-us/windows/win32/secbp/understanding-pe-signatures .

## Changed artifacts

- products/desktop/pe_certificate_guard_r496.py — real six-app candidate guard
- products/desktop/tests/test_pe_certificate_outer_padding_r499.py — 11 additive tests covering seven dirty byte positions, every valid gap length, multi-record cases, short reads, private error handling and bounded reads
- products/desktop/tests/test_pe_certificate_guard_r496.py — update one inherited acceptance test to match the stricter policy
- .github/workflows/desktop-source-evidence-r385.yml and .github/workflows/desktop-build.yml — add normal and -OO regression steps

## Test commands from trusted checkout

    python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_outer_padding_r499.py
    python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_outer_padding_r499.py
    python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_guard_r496.py
    python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_guard_r496.py
    python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_binding_r496.py
    python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_binding_r496.py

## Evidence, blockers and next gate

2026-11-17, local Linux CPython 3.13.5, exact committed source/test bytes verified by Git blob digest:

- New focused test suite: 11/11 PASS standard, 11/11 PASS optimized, both -W error; py_compile PASS.
- Parent negative control: removing R499's padding check caused 12 assertions to fail across 11 test methods (seven subtests plus five other failures).
- Inherited R496 and real parser integrations, six-app financial matrix, native Windows executable tests, AV, signing, keyboard accessibility and premium download access controls: **not executed locally**.
- Previously observed R498 source Actions #44099131795 and Windows internal #44099132039: four jobs failed before steps (steps=null, no assigned runner). Infrastructure root cause is unconfirmed.

**Next:** Restore GitHub Actions runner eligibility, or run the exact commit on a trusted Windows x64 checkout. Execute inherited tests plus the complete six-engine regression and native packaging/Defender/checksum/accessibility/entitlement matrix. Independent QD review and explicit founder approval remain mandatory before any distribution.
