# R407 — unique, bounded Tk callback receipts (issue #73)

**DRAFT / QD + founder approval required.** This sprint branches from R406 draft #2369, not `main`. It is a source-side keyboard safety change, **not** a Windows executable release, entitlement decision, or website deployment.

## Reproduced synthetic gap

R406 required each `root.bind(sequence, handler, add="+")` acknowledgement to be an exact nonempty Python `str`, but it did not require receipts to be unique or bounded and printable. A defective Tk adapter could report the same ID for distinct registered handlers, or return an invisible / oversized / non-ASCII string. The installer would activate all staged shortcuts after these acknowledgements, even though those IDs could not safely identify a single callback for future targeted cleanup.

There is no evidence of customer incidents or native Tk generating these values; the issue is a deliberately adversarial callback acknowledgement boundary. Native Tkinter's `_register` for the internal `handle` function returns a compact ASCII Tcl command name. Rejecting ambiguous values keeps the platform behavior unchanged while making the failure mode explicit.

## Implementation

- `fvs_suite/keyboard_access.py`: new `_verify_callback_ack` rejects subclassed strings (without invoking their methods), empty IDs, IDs over 128 characters, non-printable/non-ASCII IDs, and IDs already used in the same installation. Only an acknowledged ID is added to the rollback journal. Existing R404 same-root hard hold and R405 staged callback activation remain in force.
- The entire installation aborts on the first invalid receipt; all callbacks stay inert, known callbacks are unbound best-effort, and no retry is allowed on that root. Unrelated existing bindings are not globally cleared.
- `tests/test_keyboard_unique_receipts_r407.py`: 18 new regression methods: six-app duplicate-ID failures at second/final binding, Generate and premium Review orphans, noncanonical ID classes, length limits, reentrant callbacks, rollback failures, legacy bindings, retry holds, and unchanged successful actions.
- `.github/workflows/desktop-source-evidence-r385.yml`: includes the R407 suite under `python -W error` and `python -OO -W error` on Windows/Ubuntu matrices, when runners become available.

**Invariants:** No changed Decimal arithmetic, CSV parsing, financial source files, SHA-256 provenance, private storage, premium entitlement checks, native Tk button commands, or human-only compliance approval. No data upload or telemetry.

## Verification evidence and limits (2026-11-13)

A Linux local isolated probe passed **14/14 standard and 14/14 optimized `-OO -W error` = 28/28 executions**: six receipt-predicate tests plus eight simulated installation/rollback tests covering all six product shapes, duplicate receipts, premium Review, inert orphan shortcuts and error rollback. These are **manually reconstructed synthetic harnesses**, not byte-for-byte Git-sourced application integrations; the 18 newly committed tests and all inherited six-app suites remain **unexecuted against the complete repository** until a full checkout with an equipped runner is available. The local probe is not a release artifact.

The immediate R406 predecessor workflow runs [source #43468540392](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43468540392) and [desktop build #43468540328](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43468540328) ended as failure in ~4 seconds, with **zero recorded job steps** across Windows and Ubuntu. The root infrastructure cause is not proven. Check GitHub Actions run warnings, billing/spending limits, plan and runner eligibility; rerun the exact new PR commit once runner capacity is restored.

## Release and follow-up gate

1. Execute R407 and inherited R403-R406 keyboard suites, six-engine source smokes, Decimal/provenance regressions, vault cryptography and premium entitlement/review tests in a genuine complete repository checkout on Windows and Ubuntu. Record exact SHA, discovered/run/skipped/failure counts.
2. Obtain native Windows x64 builds for all six distinct launchers; perform human/automated launches and input/output smoke cases, Defender scan, NVDA/keyboard/high-DPI acceptance, SHA-256 and provenance verification.
3. Verify premium EXE distribution is actually authenticated and cannot be guessed or downloaded anonymously. Publish no binaries before QD independent review and explicit founder approval.

**No merge, public binaries, premium download, entitlement change, production site edit, or release approval is authorized by R407.**
