# Labs R265 — path-private unexpected Tkinter callback handling

**Issue #73 · DRAFT / independent QD + founder HARD HOLD · 2026-11-07**

Stacked solely on R264 draft PR #1468 (parent `e92b65ba4e0dd670d2b5bedd67cf763cedf5f554`), not production `main`. Six distinct launchers remain *unreleased*: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro.

## Defect and fix

R264 protected synchronous GUI imports and startup, but Tkinter's built-in `Tk.report_callback_exception` still prints unhandled button/after/variable callback exceptions and their entire traceback to stderr. A file dialog or UI callback can raise an `OSError`, `ValueError`, or chained exception containing a confidential path after the GUI has started. The launcher cannot catch these errors because Tkinter catches and reports them internally.

- `fvs_suite.ui_callback_privacy.install_callback_privacy` replaces the handler **on the individual root**, before user callbacks are registered. It never formats, inspects, prints, logs, or stores exception objects/tracebacks.
- Unexpected callback failure invalidates the implicit last premium report selection first, then shows a fixed accessible native error dialog emphasizing human inspection of output files and **no automated compliance decision**.
- A failed review invalidator or error dialog cannot reveal its private exception; an entirely fixed path-free stderr message is emitted if the dialog fails. If stderr itself fails, the handler declines to print an exception.
- A normal successful callback remains unchanged, as do entitlement validation, file handling, deterministic audit evidence, Decimal-safe money calculations, offline security audit hooks and human approval requirements.
- The handler covers callbacks dispatched through the shared root's `tkinter.CallWrapper`, including root-bound widgets. It is **not** an operating-system sandbox, proof about native DLLs/background threads, or proof of no data leakage through separately created Tk roots. It does not replace explicit, user-friendly field-validation errors.

## Measured local verification

Linux CPython 3.13.5, synthetic private paths, headless real standard-library `tkinter.CallWrapper` and `tkinter.Misc._report_exception` with minimal widget doubles. The unmodified default `Tk.report_callback_exception` was **observed printing** the synthetic private path and a traceback.

The focused regression module contains 12 methods, including a six-app-id subtest matrix; it covers default disclosure, redaction, nested exceptions, unsafe exception string conversion, denial of stale premium report selection, dialog/invalidator/stderr failures, normal callback, per-root installation and exception-argument noninspection.

```sh
cd products/desktop
python -W error -m unittest discover -s tests -p 'test_tk_callback_privacy_r265.py' -v
python -OO -W error -m unittest discover -s tests -p 'test_tk_callback_privacy_r265.py' -q
python -m compileall -q fvs_suite tests
```

Observed results: **12/12 standard PASS; 12/12 optimized (-OO) PASS = 24/24 method executions; compileall PASS**. Local executed files were byte-identical to committed GitHub source blobs, `ui_callback_privacy.py` `115ed82e1baf9a4548a65af77dc796b47008cfef`, and `test_tk_callback_privacy_r265.py` `24c10d2e38bddc6eea3436d9bdecafd8554c9c74`. The `app.py` production wiring was verified by inspecting the committed remote source and call order; **it was not run against a real window on Windows**.

## Remaining gates (do not publish)

GitHub Actions R264 run [#42408928589](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42408928589) reported `source-tests` and `windows-build` failed without recorded steps, logs or runners; the reason is unconfirmed. Owner should verify billing/usage, permissions and hosted-runner provisioning, restore CI, then rerun the unchanged R265 head. Full repo regressions, real Windows 11 x64 UI event callbacks (including screen-reader behavior), private six-binary builds, signed/unsigned release review, actual Defender/EDR scan, SHA-256 checksum verification and protected premium distribution remain outstanding.

**No merge, production branch or WordPress change, executable publication, licensing bypass or unrestricted premium delivery.** Independent QD and founder sign-off are required before any release.
