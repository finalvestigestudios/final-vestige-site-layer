# R387 — Six-app source-smoke report multiplicity

**Issue:** #73. **Status:** DRAFT; QD and founder hard hold. R387 stacks on draft R386 (#2249), not on production `main`. No EXE, premium download, WordPress publishing, license issuance or release authorization is part of this sprint.

## Risk and implemented boundary

R386 rejects zero-output, non-list, duplicate and unsafe synthetic output references. It still accepts a *short but nonempty* list: e.g. one `Path("exceptions.csv")` for GrantAudit Studio Pro (the actual smoke contract requires **three** reports) or one for ProcureGuard Studio Pro (requires **two**). Thus the generic validator can emit `PASS` for an incomplete product-specific output set.

R387 adds a product-contract check *after* R386's bounded native-path check and *before* a `PASS` source-smoke receipt is generated. A change to report multiplicity now needs an explicit reviewed change to the source contract and regressions.

| Tier | Product | Engine ID | Required smoke report count |
|---|---|---|---:|
| Free | LedgerDiff Lite | `ledger` | 1 |
| Free | Invoice Twin Scout | `invoices` | 1 |
| Free | SpendMap Lite | `spend` | 1 |
| Free | Policy Delta Desk | `policy` | 1 |
| Premium | GrantAudit Studio Pro | `grants` | 3 |
| Premium | ProcureGuard Studio Pro | `procurement` | 2 |

Counts reflect `fvs_suite.smoke.run_smoke` return paths and called engine contracts at the inspected parent HEAD. No financial rule, compliance decision, entitlement, source file, input import or customer content is modified. The source-smoke receipt is still **not** proof of downloadable, scanned, accessible or signed Windows executables.

## Implementation and regression evidence (2026-11-12)

- `scripts/smoke_receipt_contract_r387.py`: exact six-engine report-count map and a fail-closed validator that composes existing R386 path custody. Unknown engine identifiers, missing/extra reports and forged output containers fail without a source PASS claim.
- `scripts/source_smoke_gate.py`: uses the product-specific validator inside `verify_smokes` before appending a source-only `PASS` row.
- `tests/test_smoke_receipt_contract_r387.py`: 21 focused unit methods including all six valid counts, incomplete premium receipts, surplus reports, bad engine identifiers, generators, duplicated names, Windows paths, subclass objects, snapshot isolation and private-error chains.
- `tests/test_source_smoke_gate_r21.py`: existing all-six fixture now returns the reviewed count for each app, rather than the old one-report-per-app stub.
- `.github/workflows/desktop-source-evidence-r385.yml`: runs R387 and the R21 source gate regressions in both ordinary and optimized Python on Ubuntu and Windows *before* executing six real synthetic engine smokes. Retains read-only checkout, no artifacts or deployment.
- Local isolated Linux Python 3.13: `python -W error -m unittest discover -s products/desktop/tests -p test_smoke_receipt_contract_r387.py` **21/21 PASS**; same with `python -OO -W error` **21/21 PASS**, **42/42 focused executions**. Compileall PASS. Executed R386 dependency's Git blob matched `939eb0ec39920f98b55413e8c5ab95c2306476cd`; R387 helper and tests were checked against their Git blobs after upload. Only the isolated new module, tests and predecessor validator ran locally; the full checked-out repository's R21 / engine suite has not run.

## Outstanding release gates and unblock

R386 independent Actions run [#43305945416](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43305945416) and original desktop run [#43305945456](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43305945456) both failed before jobs recorded execution steps; the cause was not established. Inspect the **new R387 exact-HEAD runs** separately; do not treat workflow presence as test success. The smallest owner step if runnerless failures continue: inspect failed check annotations and Actions billing/spending/runner eligibility and restore hosted runner allocation.

**Next highest-impact step:** Execute full six-engine R21/R42/R276/source smoke, financial Decimal/provenance regressions, all 22 genuine AES-GCM tests and real Ed25519/SQLite issuer tests on the exact R387 checkout, Ubuntu and Windows. Then test six native Windows x64 packaged executables, Defender/AV scanning, accessibility, release hashes and premium gated distribution. Independent QD review and founder approval are mandatory before merging or publishing.
