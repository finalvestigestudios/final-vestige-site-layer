# R240 — private PE stream error custody (issue #73)

**Scope:** Six unpublished Windows x64 candidates (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, ProcureGuard Studio Pro). Draft engineering artifact only; **QD + founder HOLD**. No production edits, binaries, payment access changes, uploads, or release authority.

## Defect and correction

The inherited R238 verifier, `products/desktop/pe_image_guard.py`, sanitized `os.open`, `os.fstat`, and `os.fdopen` failures **before** stream handoff, but after handoff its `with stream:` body could propagate raw `seek`, `read`, `__enter__`, `__exit__`, or parsing exceptions containing private filesystem paths or customer messages. A failing stream `__enter__` could also strand the file descriptor because Python does not run that context manager's `__exit__`.

R240 uses a small `_private_pe_stream` context manager around the existing PE32+ parser. It preserves intentional `PEFormatError` diagnostics, replaces all other ordinary `Exception` messages with **`PEFormatError("Cannot inspect candidate file")`** and suppresses the exception cause in user-facing tracebacks. The stream's own context manager retains ownership after successful entry, and if entry itself fails, R240 explicitly attempts `stream.close()`. `KeyboardInterrupt` and `SystemExit` still propagate after cleanup. No parser acceptance criteria, input data, monetary calculations, compliance adjudication, offline privacy settings, or premium entitlement logic were changed. A failed underlying `close()` cannot guarantee OS-handle release; this fix makes best-effort cleanup without claiming a filesystem-level guarantee.

## Exact test evidence — synthetic, not Windows release verification

- Source recovered byte-identical from R239 Git blob **`43ecafe1e33cc6ac3ef629dfe2421bb47cba79f0`**. Running the **16 new R240 methods against original source**: **1 failure + 11 errors** (16 executed), reproducing path leaks and entry-custody defects.
- Fixed source Git blob **`6c703277119215cc134563cf9bf3d39bc490ef99`**; new tests blob **`49af2bae2112bf11a2d3b3670e514ef6d25e2a08`**. Those Git blobs are byte-identical to the files executed locally.
- **R240: 16/16 PASS** normal and **16/16 PASS** `python -OO`; R238 inherited 14/14 PASS per mode. Combined **30/30 PASS normal; 30/30 PASS -OO = 60/60** executed tests; Python compilation PASS.
- Environment: **Linux x86_64, CPython 3.13.5**; synthetic PE32+ header, real temporary file descriptors, injected exceptions during reads/seeks, stream entry/exit, all four header reads, non-OS errors, and interrupts. Verified unchanged candidate input bytes and closed descriptors on tested failure paths.
- Reproduce inside complete checkout: `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_pe_*.py'` and same command with `python -OO -W error`. The CI workflow separately mandates the R240 tests in both Ubuntu and Windows jobs **before Windows packaging**.
- **Not demonstrated:** full inherited six-app regression suite, successful hosted CI, executable build, PE candidate acceptance on real binaries, malware scanning, native Windows 11 x64 launch/accessibility/scale tests, or independent QD/founder sign-off.

## Governance, hold, and next release gate

Draft PR is stacked **only** on R239 head `60ec553c1faff75592bd5d873c62f9ea77a41e81`, never on `main`/production. No merge or website publication is authorized. Previous R239 Ubuntu and Windows jobs at [Actions run 42275515844](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42275515844) failed with zero published steps; runner/billing/permission root cause remains unconfirmed. Restore the GitHub Actions runners; rerun unchanged R240 head and obtain complete six-engine regression evidence. Then privately build and verify six Win11 x64 executables, SHA256, Defender scan, smoke/accessibility, protected premium transfer and QD review. Four free and two premium programs remain **UNRELEASED**.
