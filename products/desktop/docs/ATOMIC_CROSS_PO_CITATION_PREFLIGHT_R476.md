# Labs R476 — atomic citation preflight for ProcureGuard (DRAFT / QD HOLD)

## Customer-visible risk and improvement

R475 bounds total materialized cross-PO citations at 1,000,000, but its original loop expands a type immediately after checking that type. If the invoice stream fits while a later credit, receipt or return stream overflows, the review is rejected **after** allocating earlier, doomed cross-order source-row sets. The same issue arises when the second document in one typed stream exceeds the budget.

R476 separates **reservation** from **materialization**:

1. Scan validated invoice and receipt groups once each to classify rows into four typed namespaces.
2. The new reserve helper computes distinct PO/line groups × unique physical CSV rows for **every typed stream**, deducting from a shared budget. It fails with a fixed, private-data-free ValueError if a later document exceeds the remaining budget; expanded citation sets have not yet been created.
3. Only when all four streams fit, expand and numerically sort the citations. Legacy single-kind wrappers reserve first too.
4. Never truncate evidence or silently auto-approve a payment.

**Scope:** This avoids allocation of doomed **expanded audit citations**, not of bounded input groups or the existing occurrence indices. It is not a total-process memory-use guarantee. No originals, exact Decimal financial values, provenance, human-review semantics, local-first processing or telemetry settings are changed.

## Exact artifacts

- Source: products/desktop/fvs_suite/procurement_cross_po_r471.py — Git blob fde2ebb484deec129415095b936a8ebdabfc1fa0
- New eight-method unit suite: products/desktop/tests/test_procurement_cross_po_atomic_r476.py — Git blob e5d51efa9153ee463d27b3ea595f9ba837d59ec5
- CI gate: .github/workflows/desktop-source-evidence-r385.yml — new normal and optimized Python invocations.

## Actual local evidence (2026-11-16)

Both source and test files used locally matched their exact committed Git blobs via git hash-object. Isolated local Python 3.13.5 executed:

- PYTHONPATH=. python -W error -m unittest discover -s tests -p test_procurement_cross_po_atomic_r476.py — **8/8 PASS**.
- PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p test_procurement_cross_po_atomic_r476.py — **8/8 PASS**.
- python -m py_compile for both files — **PASS**.

The eight methods cover late-type failure without any materialization calls, second-document same-type failure, exact four-type budget acceptance, one-below-budget rejection, privacy-safe errors, same-PO exclusion, direct typed-API preflight, and **250 seeded scenarios × four typed streams**, checked against an independent R475 output oracle in each Python mode.

**Limit:** These are 16 executions of the exact committed module/tests in an **isolated package tree**, not a full repository checkout. Full actual 38-method ProcureGuard CSV integration, six-engine regression matrix, installed Windows packaging, Defender, accessibility and premium entitlement tests **have not run**.

## CI infrastructure blocker and smallest action

R475 exact-commit source workflow https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43905135758 and Windows internal build https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43905136318 both concluded failure with all four jobs reporting steps=null. No application test steps were observable. Root cause unconfirmed.

A repository/org GitHub Actions administrator should inspect job failure annotations, billing and spending eligibility, workflow permissions and runner assignment. Restore execution and run the exact R476 PR head before any release classification.

## Release governance

Stacked on R475 draft #2757, never production main. **DRAFT / QD HARD HOLD** until independent QD review plus explicit founder approval, full six-app tests, native Windows x64 scans and installed smoke/accessibility, cryptographic release checksums and protected premium licensing/download validation. No executables, payment workflow, public download URL or WordPress publication are authorized.
