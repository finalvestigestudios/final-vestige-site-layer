# R496 — Bounded PE WIN_CERTIFICATE framing (INTERNAL / QD HARD HOLD)

Issue #73. Stacked draft development branch on R495 (PR #2861), **not** production main. No publication, binary upload, distribution change, entitlement change, or QD approval is authorized by this source verification.

## Why

R495's release preflight verifies the security directory's location, file bounds and separation from mapped sections, but it still accepted arbitrary overlay bytes as a certificate table. For example, 64 bytes of "Z" were previously treated as structurally acceptable PE certificate data. This could produce a misleading certificate-directory format verdict, especially because Authenticode trust validation remains an independent, unimplemented release gate.

## What changed

- New pe_certificate_guard_r496.py walks the security directory (#4, an **absolute file offset**, not an RVA) on the exact descriptor that the PE parser subsequently hashes. It validates 8-byte directory alignment, 8-byte WIN_CERTIFICATE headers, bounded record counts and bytes, aligned record strides, and revision 0x0200 / type 0x0002 framing; zero or absent certificates remain valid for unsigned structural inspection.
- Limits: **8 MiB maximum certificate-table length**, **128 maximum certificate records**. The walker reads only record headers (8 bytes at a time) and never executes or parses PKCS#7 payloads. Record payload content and nonzero padding are NOT verified or trusted.
- The PE parser now fails closed with a fixed diagnostic for malformed certificate framing before SHA-256 manifest binding on the **same already-open file descriptor**.
- Corrected one inherited R494 positive certificate fixture from opaque "Z" bytes to a structurally framed record; keeps its intent without weakening the new policy.
- New pure regression module: **22** methods with malformed/valid record, count, revision, type, bound, IO and redaction cases.
- New parser/release integration module: **9** methods, including a six-candidate release-gate rejection test.
- The independent Ubuntu 24.04 + Windows latest source workflow now requests both suites in ordinary and optimized Python modes.

## Actual test evidence for this sprint (not CI evidence)

Using a locally authored source/test copy on Linux CPython, before GitHub publication:

- PYTHONPATH=. python -m unittest -v tests/test_pe_certificate_guard_r496.py → **22 passed**, no skips.
- PYTHONPATH=. python -OO -m unittest -q tests.test_pe_certificate_guard_r496 → **22 passed**, no skips.
- python -m py_compile pe_certificate_guard_r496.py tests/test_pe_certificate_guard_r496.py → **passed**.

Exact Git blob hashes for the two tested files match repository content: helper 8e3658598b51134e43450d17afb8dd30b9d8b7dd; unit tests 006fd6a852ad4a0ae14bef9ab65167bab788b8ae.

The **9 added full-parser/release integration tests are NOT locally executed** because the complete private repository was not accessible to the Linux test container. The production parser modifications are not claimed integration-tested. Previous R495 GitHub workflow runs failed before any steps: [source run 44070207815](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44070207815), [Windows build 44070207886](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44070207886); jobs have steps=null, cause undetermined.

## Verification / next gate

On a trusted full checkout of this exact R496 head:

    PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_guard_r496.py
    PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_binding_r496.py
    PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_directory_binding_r494.py
    PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_binding_r496.py

Restore runner execution or use a trusted Windows x64 host; verify inherited suites, a real unsigned/signed PE sample, six genuine application EXEs, Defender/smoke/checksums/accessibility, premium access controls, and independent QD + explicit founder approval **before any release**. This limited structural policy is not Authenticode signature verification; the latter needs Windows trust-chain validation with a documented certificate/signing policy.

No changes to local-first file handling, Decimal-safe financial calculations, deterministic audit evidence, human compliance decisions, or premium licensing.
