# R438 — native premium issuance identity (DRAFT, HARD RELEASE HOLD)

Tracking: [Final Vestige Labs issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
Parent: [R437 draft #2542](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2542), pinned to `b1839d8adfbe36c8665bd4e4f9d83080e8a13188`.
Branch: `feature/labs-r438-issuer-product-identity-20261114` (not `main`).

## Defect and production repair

The offline **client** had already been hardened in R422 to reject Python `str` subclasses as product IDs. The **operator-side issuance** and **SQLite reservation/finalization** APIs, however, still used bare membership against `frozenset({'grants', 'procurement'})`. Python subclasses can override `__hash__` and `__eq__`, creating ambiguous or side-effecting product selection in direct programmatic calls. A string subclass with precisely the same characters as a valid product was also accepted as a native ID.

Three boundaries now check `type(product) is str` *before* membership or any private-key loading, output-file creation, reserved-ID write or signed-file fingerprinting:

1. `license_issuer.issue_entitlement`: reject forged or non-string product objects before identifiers, clocks, output and key processing.
2. `license_registry.IssuanceRegistry.reserve`: reject before SQLite reservation or output access.
3. `license_registry.IssuanceRegistry.finalize`: reject before issued-file hashing and SQLite state transition.

Only exact built-in `"grants"` and `"procurement"` remain eligible. This is a local API data-boundary improvement, not a claim that the unconfigured production authority can issue licenses or that premium distribution is approved. Existing issuance receipts, Ed25519 signatures, deterministic SHA-256 evidence, local-first financial handling, and manual human compliance decisions remain unchanged.

## Tests and evidence

- New test module: `products/desktop/tests/test_issuer_registry_native_product_r438.py` — **13 committed regression methods**. Covers both premium native IDs, equal-text subclasses, poison hash/equality hooks, forged-equality subclass, unhashable/non-string data, rejection before key/DB/hash IO, successful synthetic reserve/finalize, and wrong-digest rejection. Uses no real customer data or signing keys.
- The CI source-evidence workflow now invokes the 13 methods on Ubuntu and Windows in standard and `-OO` Python, followed by inherited R12 real ephemeral Ed25519 issuer, R13 registry and R422 client product identity suites, also both modes.
- **Actually executed locally:** a four-method isolated Python guard-logic projection on Linux, both `python -W error` and `python -OO -W error`: **4/4 PASS in each mode (8 method executions)**, with 39 invalid product/function combinations per mode and six valid combinations per mode. Controlled pre-fix comparison verified equal-text subclasses were accepted and a poison subclass invoked `__hash__`. `compileall` on that projection passed.
- **Not yet executed:** the 13 new committed tests against the full production modules, inherited cryptographic tests, the source-evidence workflow, native Windows builds or UI smoke tests. The projection is *not* a full checkout or committed-source integration pass.

## Blockers and QA/QD release gates

At R438 creation, the latest parent R437 source run [#43655816873](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43655816873) and Windows build run [#43655816935](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43655816935) failed before any recorded job steps. Their root infrastructure cause is not confirmed. The smallest operator action is to inspect repository/organization Actions policy, hosted runner availability and billing/spending limits, then rerun the **exact R438 head** source and Windows workflows.

No `main` changes, production deployments, downloads, premium executable distribution, real license issuance or authorization. `release_authorized=false`, with independent QD review and explicit founder approval required. No unsigned executable is presented as verified.

Next highest-impact step: get exact-head hosted tests running, run new 13 plus inherited R12/R13/R422 and all six-engine regressions, verify actual Windows x64 builds, Defender and accessibility, then independently audit premium access controls before any release decision.
