# R389 — six-app synthetic smoke report-role custody (issue #73)

**Status: DRAFT. QD and founder HARD HOLD. Source-level local tests only.**

## Gap and scope

R386 rejected empty, forged and unsafe report references. R387 enforced exact
report **counts**, but a three-item GrantAudit receipt containing three CSVs
could still satisfy that count even when its mandatory SHA-256 provenance
manifest was missing. Likewise, two ProcureGuard CSVs could satisfy its
two-item count without the evidence manifest. Counts cannot prove report roles.

The actual \`fvs_suite.smoke.run_smoke\` already validates synthetic output
contents, provenance and file existence. R389 adds a deterministic, read-only
check at that producer boundary, just before temporary smoke output names are
returned. This prevents a source-only "PASS" when the engine returned the
wrong product's report, a wrong file extension, a misordered premium bundle,
or a missing/replaced premium evidence manifest.

## Contracts (output order is part of the contract)

| Product | Exact output role / filename stem | Format |
| --- | --- | --- |
| LedgerDiff Lite | ledger-diff | CSV |
| Invoice Twin Scout | invoice-twins | CSV |
| SpendMap Lite | spend-map | CSV |
| Policy Delta Desk | policy-delta | TXT |
| GrantAudit Studio Pro | grant-audit-exceptions, grant-budget-check, evidence-manifest | CSV, CSV, TXT |
| ProcureGuard Studio Pro | procurement-three-way, evidence-manifest | CSV, TXT |

Every name also requires the existing \`YYYYMMDD-HHMMSS-microseconds\`
suffix produced by \`engine.outpath\`. This is a shape check, not independent
proof that the timestamp is an authentic UTC time. Real file bytes, their
custody and their application-level tests remain the responsibility of the
existing smoke runner. The helper does **not** read customer files or disclose
raw filenames in errors; it rejects untrusted path subclasses before touching
their properties.

## Files

- \`fvs_suite/smoke_output_roles_r389.py\` — fixed six-product report-role table and privacy-preserving validator
- \`fvs_suite/smoke.py\` — invoke validator after existing file/content checks and before returning the smoke receipt
- \`tests/test_smoke_output_roles_r389.py\` — 29 independent regression tests including missing premium manifests, wrong app, order, extension, fake paths and optimized Python
- \`.github/workflows/desktop-source-evidence-r385.yml\` — run focused suite on Ubuntu and Windows, both normal and \`-OO\`

## Local evidence, not claimed hosted CI

Executed on Linux with Python 3.13 (the local runtime):
- \`PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_smoke_output_roles_r389.py\` — **29/29 PASS**.
- \`PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_smoke_output_roles_r389.py\` — **29/29 PASS**.
- \`python -m py_compile\` on the new validator and test — PASS.

The executed local files were checked against committed Git blob IDs:
- Helper \`c8a0319eff86a5d2ed032acdc77969cb8a47a8cc\`.
- Test \`b1ae15e4dbc5f599158cb1bf4489445e75ef16b6\`.

**Not executed locally:** the full six-engine end-to-end runner, full checkout
integration, hosted Windows and Ubuntu matrix, genuine AES-GCM/Ed25519/SQLite,
native Windows x64 builds, Defender, accessibility or premium access-control
acceptance. No executables/downloads are published and production remains
unchanged. The new gate does not imply binary or QD release readiness.

## Next highest-impact step

Diagnose failed GitHub Actions check annotations, billed hosted-runner
eligibility and spending limits. Re-run the exact branch commit's independent
six-engine and native Windows workflows. After real engines and crypto pass,
build and scan all six Windows x64 executables; verify offline behavior, GUI
accessibility and gated premium delivery. Keep draft/QD/founder approval hold.
