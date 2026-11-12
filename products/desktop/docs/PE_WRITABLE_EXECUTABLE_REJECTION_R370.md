# R370 — Reject writable-executable PE sections (DRAFT; QD/founder HOLD)

## Threat and correction

The existing `pe_image_guard.verify_amd64_pe` validated the Windows AMD64 machine type, PE32+ headers, bounded section extents, backed executable entry point, and file layout. However, the checker did **not reject sections simultaneously carrying `IMAGE_SCN_MEM_WRITE` (0x80000000) and `IMAGE_SCN_MEM_EXECUTE` (0x20000000)**. A crafted file with an ordinary RX `.text` entry point and a separate RWX `.data` section passed the earlier static format inspection.

R370 rejects **every mapped section** with both flags, including non-entry, unbacked/zero-fill, and non-code sections, **before** any smoke execution. RO, RW non-executable, RX and execute-only synthetic section forms remain accepted when the original structural conditions are satisfied. The check uses only the trusted PE header's native integer flag word; it does not read, log, transform, execute, or upload financial data.

This conservative internal candidate policy does not claim to prevent malicious code execution, replace Defender/EDR, detect all loader tricks, or validate Authenticode. An unusual bootloader requiring RWX must be investigated and reviewed; **do not bypass or weaken the guard merely to make a build pass**.

## Reproduction and local test evidence (Linux Python 3.13.5)

- Reconstructed **exact previous Git blob** `6c703277119215cc134563cf9bf3d39bc490ef99` in a local isolated work directory. A physically inert 2-section synthetic PE32+ image with RX entry `.text` plus RWX non-entry section **passed the old guard**. No real executable was run.
- Applied the R370 change to the exact baseline. Implementation blob SHA-1: `c01c2756327f4f1613dc240986616c356803c4fc`.
- `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_pe_section_wx_r370.py'`: **20/20 passed** (local path adjusted to reconstructed module in an isolated directory).
- `PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_pe_section_wx_r370.py'`: **20/20 passed**, 40 focused method executions total.
- Committed test source blob `748aaad4093ee11d4db7914dbdb62f0d1a528dfe` is byte-for-byte identical to executed local fixture. All 20 cases use inert synthetic PE header bytes written to temporary files; fixtures are not runnable Windows applications and are destroyed after each test.
- Cases include valid RX/RW/RO layouts, 1–4 sections, unbacked sections, RWX entry and non-entry sections, RWX without a code bit/read bit, non-AMD64 and missing-executable-entry rejection. Each successful/failed fixture checks unchanged SHA256 and negative cases check that failure diagnostics do not expose the private local fixture path.

Two required invocations per OS (normal / `-OO`) are added to `.github/workflows/desktop-build.yml` ahead of source provenance and Windows packaging. They were **not executed on GitHub-hosted runners**.

## Boundaries and outstanding gates

This is a **candidate-verifier safety regression only**, affecting the shared Windows x64 release-check path used for all six standalone app names: four free (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and two gated premium (GrantAudit Studio Pro, ProcureGuard Studio Pro). There is no financial engine, Decimal calculation, source CSV, encryption, premium entitlement, WordPress production, or distribution change.

**Unverified:** complete inherited six-app tests; 22 real AES-GCM cases; exact-head hosted Ubuntu/Windows validation; PyInstaller output section compatibility; native Win11 x64 PE/smoke/Defender/keyboard/accessibility and scan evidence; code signing; protected premium delivery; independent QD and founder approval. No executable has been built, uploaded, or released by this sprint.

**CI history:** R369 Actions run [#43152104161](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43152104161) had Ubuntu and Windows jobs `steps=null` and job logs `404 BlobNotFound`. This does **not** establish a code failure. The cause is unconfirmed. Inspect GitHub Actions failed-check annotations and billing/spending limits/runner eligibility, then rerun the exact candidate head after restoring dispatch.

**Next highest-impact action:** restore real job-step execution; run the entire inherited suite and authentic AES-GCM cases on exact head; inspect the six genuine PyInstaller section tables (especially the W^X rule) before any distribution, then native Windows acceptance. Maintain QD/founder HARD HOLD and premium restrictions.
