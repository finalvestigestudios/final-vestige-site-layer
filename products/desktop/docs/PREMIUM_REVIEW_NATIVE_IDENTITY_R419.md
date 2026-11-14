# R419 — fail-closed premium human-review input identities

**Internal source change, DRAFT / HARD RELEASE HOLD.** Issue #73, stacked on R418 draft #2432. This change affects the offline, hash-linked human-review journal used by **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. Four free applications retain existing behavior. It does not authorize payment, approve compliance, publish binaries, expose private reports, change the production site, or grant premium entitlements.

## Defect and fix

The direct Python API in `exception_review.py` accepted subclasses of built-in `str` for the expected report SHA-256, product, case ID, reviewer, rationale and decision. A hostile subclass may override `__eq__` or `__ne__` and pretend that an **outdated source SHA** is equal to the currently loaded report, or override text methods to supply different audit-journal reviewer/rationale text. Dictionary key hooks on a forged case ID also run before the prior implementation validates the source identity.

R419 adds `fvs_suite/review_identity_gate_r419.py` containing small standard-library-only native-choice, native-text and canonical lowercase SHA-256 checks. The premium review API now validates the requested product, decision, expected source hash, and case-ID *type* before accessing files or locks. Reviewer and rationale must be native `str` before Unicode safety inspection or trimming. `read_cases` likewise rejects product string subclasses before reading input. The case-ID content remains checked against exact loaded exception IDs, preserving legacy unknown-case error behavior. All error strings are fixed: no financial data, private filesystem paths or hostile string representation is interpolated.

**Scope caveat:** Python-level guards do not authenticate the operator, make a journal tamper-proof or prove that the human reviewer actually performed the action. The existing source-bound hash-linked journal, decision whitelist (`needs_evidence`, `escalated`, `reviewed`) and separate payment/compliance approval boundaries remain. The journal is not a cryptographic signature.

## Committed artifacts

- `products/desktop/fvs_suite/review_identity_gate_r419.py`: native input and SHA contract
- `products/desktop/fvs_suite/exception_review.py`: direct API integration at report load and journal write
- `products/desktop/tests/test_review_identity_gate_r419.py`: **11** pure standard-library regression methods
- `products/desktop/tests/test_review_identity_integration_r419.py`: **10** synthetic grant/procurement journal integration regression methods
- `.github/workflows/desktop-source-evidence-r385.yml`: four normal/`-OO` commands in the Ubuntu 24.04 + Windows latest matrix

## Test evidence

Local Python 3.13.5 Linux **new helper logic** was executed in a standalone copy with **11/11 standard and 11/11 optimized tests passing (22/22 executions)**, including hostile subclass methods, canonical digest and decision/product allowlist checks. Source compilation passed. This is **not a complete trusted Git checkout**, and the new committed integration test file has **not** run locally. Do not present these as native Windows, six-engine, or full audited journal integration passes.

Exact-commit trusted-checkout test commands:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_review_identity_gate_r419.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_review_identity_gate_r419.py
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_review_identity_integration_r419.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_review_identity_integration_r419.py
```

Run inherited `test_human_review_r7.py`, all journal, SHA-256/provenance, Decimal-safe engine, AES-GCM, Ed25519 and premium entitlement regressions before considering this change accepted.

At R418 HEAD `a96ee045dab1b8058435daa0f939ead9bbf4a90e`, [source CI #43559789100](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43559789100) and [Windows build CI #43559789160](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43559789160) both failed before steps: four jobs show empty steps and no runner name. This does **not** establish a code test failure. Runner/billing explanation has not been verified. Inspect R419 exact-commit runs separately before claiming any hosted test evidence.

## Next high-impact acceptance and unblocking

Repository owner: inspect GitHub Actions plan/billing and runner eligibility, restore a running Windows/Ubuntu matrix or supply a trusted complete checkout; run **the committed tests** and all inherited premium human-review and financial suites. Then build genuine Windows x64 candidates, smoke each of six launchers, scan with Defender, verify keyboard/NVDA/high-DPI behavior and SHA-256 receipts, and prove unauthorized access to premium downloads is denied. Never publish a premium executable at a public unrestricted URL.

**Release remains blocked** pending independent QD review and explicit founder approval. No merge, production change, site publication, binary release, paid order, or premium artifact distribution is authorized by R419.
