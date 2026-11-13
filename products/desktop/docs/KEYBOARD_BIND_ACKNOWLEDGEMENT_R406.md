# R406 — Refuse unacknowledged Tk callback registration

**Status:** DRAFT / issue #73 / independent QD and founder approval required. This branch stacks only on R405 draft #2362; it is not a release or a change to `main`.

## Defect and scope

R405 makes callbacks inert until all `root.bind(..., add="+")` calls return, but previously accepted a silent `None`, empty string, or other non-ID result as a successful callback registration. An abnormal Tk or UI-adapter implementation could therefore activate a shortcut map without a reliable way to identify/unbind every callback. A subsequent failure could leave unidentified registered handlers. There is **no evidence of this occurring to a user**; it was demonstrated with synthetic adapters.

Tkinter's Python-handler binding implementation returns a newly registered Tcl callback command ID (a nonempty `str`). R406 treats any other acknowledgement as a failure *inside the existing transactional binding loop*. The prior R404 same-root retry hard hold remains set, the R405 pending callbacks remain inert, and every earlier callback with a known ID is unbound best-effort without removing unrelated bindings. On a failed registration, the operator must recreate the application window.

This shared helper serves **LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro**. Financial data, Decimal calculation rules, SHA-256 evidence, local storage, premium entitlement enforcement and human compliance approval logic are unchanged.

## Code and tests

- `fvs_suite/keyboard_access.py`: require `type(callback_id) is str` and a nonempty value before counting the binding as installed.
- `tests/test_keyboard_bind_ack_r406.py`: **16 new methods** covering six product shapes, first/second/last callback ID omissions, empty/nonstring/hostile string subclass acknowledgements, reentrancy, cleanup errors, inert orphans, retry hold, legacy app bindings, Generate and gated Review.
- Update R44 synthetic root to model real Tk's returned ID rather than `None`. Update two inherited R404/R405 missing-ID expectations to reflect the deliberate earlier failure.
- Source evidence workflow runs the new tests on Ubuntu and Windows under standard and `-OO -W error` modes **only after hosted runners actually execute**.

## Scoped local verification (2026-11-13)

A **partial isolated Linux reconstruction** using Python and a reconstructed portion of the R405 synthetic test fixture executed the exact Git-blob-matched R406 patched installer `6dabd38ad65cc6c1e47a18dd78aa73edde644670`, target preflight `a1e41291fa32ed52d6f972c681bab11f6ffacf9e`, and R406 regression file `a9be28274197e7598f68b0878884bf3509c44404`.

- Normal CPython: **16/16 PASS**.
- Optimized `-OO -W error`: **16/16 PASS**.
- Compilation of the shared source: **PASS**.
- A prepatch comparison with the original R405 installer Git blob `e32e4b816f1083942bcdbaccd29950664effc4f0` produced **27 failing assertions/subtests** across the new 16-method suite. This is synthetic defect reproduction, **not** a customer incident.
- R405 fixture definitions were recreated locally from the repository test; this was **not** a full checkout. All inherited tests, genuine Windows Tk UI automation, six financial/cryptographic engines and executable artifacts still require complete integration execution.

## Release holds / smallest unblock

Hosted source and Windows build runs for R405 (IDs `43458069097`, `43458069042`) failed with all four jobs showing no executed steps. Their log endpoint returned 404 for a missing blob; the underlying infrastructure cause remains unverified. Inspect GitHub Actions' run-level warnings, billing/spending/hosted-runner eligibility, then rerun exact R406 head. Test genuine Windows x64 binary launches, Defender, screen-reader/high-DPI accessibility, checksums and premium access controls before any publication.

**Never merge/deploy without independent QD + explicit founder approval. No binaries, downloads or premium files are published by this sprint.**
