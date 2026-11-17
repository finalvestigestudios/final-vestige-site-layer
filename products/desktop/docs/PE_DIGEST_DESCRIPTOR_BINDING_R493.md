# Labs R493 — bind six Windows PE verdicts to exact inventory bytes

**State: DRAFT / independent QD + founder HARD HOLD.** Tracks issue #73. This change is stacked **only** on R492 draft PR #2846 (parent `02c52945643f1bc5f3eac480b21f3b7ab1ecb7ed`), never on production `main`.

## Defect and change

The candidate release gate independently checked Windows AMD64 PE structure and candidate SHA-256. A pathname replacement in the interval between those separate opens could let the structure check examine one file while the checksum/inventory check examined another. The prior independent passes did not prove that *the bytes inspected for PE structure* matched the six-file manifest.

R493 adds `pe_digest_custody_r493.verify_pe_digest_stream`: after the PE parser accepts its headers, hash **the same already-open descriptor** from offset zero, limit it to 512 MiB, and verify a native lowercase 64-character SHA-256 string, exact file length and descriptor identity/size/timestamps before and after reading. It fails with a constant, private-path-free error for malformed digests, changed files, I/O faults and mismatches. `pe_image_guard.verify_amd64_pe` accepts an optional keyword-only `expected_sha256` and invokes this helper within its existing owned file-stream context. The six-candidate `release_gate.verify` now computes the bounded checksum first and passes it to the PE check, which must hash to the **same canonical inventory bytes** before **any** candidate smoke execution.

Legacy standalone `verify_amd64_pe(path)` continues to perform structural checks without an inventory digest; callers intending release verification must supply the expected digest or use `release_gate.verify`. This is static format and provenance verification, **not** proof of executable safety, Authenticode, Defender results or actual Windows x64 execution. The private local-first financial engines, Decimal calculations, human compliance decisions, premium entitlement and QD approval model are unchanged.

## Artifacts and actual evidence — 2026-11-17

- New [digest verifier](../pe_digest_custody_r493.py), [12 focused real-file regression methods](../tests/test_pe_digest_custody_r493.py) and [eight additional PE/whole-six-candidate integration methods](../tests/test_pe_digest_binding_integration_r493.py).
- Updated [PE parser](../pe_image_guard.py), [release gate](../release_gate.py), [independent Ubuntu/Windows source evidence](../../../.github/workflows/desktop-source-evidence-r385.yml), and [prepackaging two-job workflow](../../../.github/workflows/desktop-build.yml).
- **Actually executed locally:** Linux CPython 3.13.5 on exact new helper/test blob bytes; `12/12 PASS` standard `-B -W error`, `12/12 PASS` with `-OO -B -W error`, **24 method executions, 0 skips**, Python compilation PASS. Synthetic inert data and real local file descriptors, not executable PE images. File blob IDs: helper `c02c3192ded832a50d5356042e860bf4154acde8`, focused tests `16ac3602adcd3df290a67ee1a9dbaf6190759e02`.
- **Not executed locally:** eight full-module/integration methods, original PE parser and six-candidate release gate in a complete checkout; inherited full suite, GitHub Actions tests, native Windows packaging, Defender, signing, accessibility and premium distribution.
- CI invokes both new suites with normal and optimized Python on both Ubuntu and Windows. A green GitHub workflow run is required before treating this as production-ready engineering evidence.

## Operator acceptance and blockers

From a **trusted complete checkout** on R493 exact head, run:

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_digest_custody_r493.py
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_digest_binding_integration_r493.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_digest_custody_r493.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_digest_binding_integration_r493.py
```

As of R492, exact-head [six-source CI #44044435749](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44044435749) and [Windows build CI #44044435759](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44044435759) **failed before runner assignment** with four jobs reporting `steps=null`; the underlying owner/billing/runner cause remains unconfirmed. Check R493 exact-head runs separately. Smallest unblock: repository owner opens Actions run annotations, confirms billing/runner eligibility, or runs the above on a trusted Windows x64 checkout. After full regression success, build actual Windows candidates and preserve PE/checksum evidence, native `--smoke-test`, malware scan, accessibility signoff and protected premium entitlement/delivery evidence for **independent QD review and explicit founder approval**.

**No release:** never merge to production or publish any EXE, private premium link or live WordPress catalog on this evidence alone.
