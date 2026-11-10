# R340 — release-report runtime fault privacy and R337 regression reconciliation

**2026-11-10 · DRAFT / independent QD + founder HARD HOLD.** Scoped to the shared offline release-report verification path for the four free and two premium Final Vestige Labs Windows x64 utilities. Stacked on R339 draft PR #1954 at `17faa9f2a7c32e61951bbaab054af57fde4d978d`; **not main, not live**.

## Reproduced defects

1. **Unhandled report-publisher RuntimeError:** R339 `publish_report` caught `OSError`, `TypeError`, `ValueError` and `OverflowError`, but a `RuntimeError` from a file-creation wrapper, hardlink operation or post-link witness escaped as a raw exception. The release-gate CLI catches `ReportEvidenceError`, not `RuntimeError`; an unexpected exception could therefore expose a local private path in traceback output and bypass the standard fail-closed reporting contract. The new handler includes `RuntimeError`, always raises the generic private `ReportEvidenceError` without exception chaining, and does **not** catch `KeyboardInterrupt`. It never auto-deletes a stage or ambiguous final pathname.
2. **Five deterministic R337 test errors:** Three legacy assertions in `test_report_evidence_exact_stage_r337.py` referred to undefined `stage_created` outside the parameterized helper, triggering `NameError` in five tests even when the R339 writer was working properly (the descriptor fault helper was used by three tests). The three assertions now require exactly one retained private stage; the actual parameterized assertion used to assert *zero* stages for invalid JSON is preserved unchanged. This restores the intended R339 evidence-retention contract.

## Executable source and regression evidence

- `products/desktop/report_evidence.py`: error-classification change only; exact tested Git blob `0310ec3df5a6b5d1e03d8180cb7818497b7207fb`.
- `products/desktop/tests/test_report_evidence_exact_stage_r337.py`: fixes three out-of-scope variables; exact tested Git blob `428c8a4eb4cc6c4996ded95728ab09c8f62ae54d`.
- `products/desktop/tests/test_report_runtime_fault_r340.py`: 18 new synthetic fault-injection tests; exact tested Git blob `3cd2654646a8119e1655a723a87de5fd25a01e64`.
- Existing R339 stage-retention regression `test_report_stage_retention_r339.py`, exact verified Git blob `224e7c5d036d9b407035d44a4e6a47e08e953b35`, also executed without modifications.
- `.github/workflows/desktop-build.yml`: enforces the R340 suite in Ubuntu and Windows jobs, normal and optimized, before private Windows packaging.

**Actual local execution:** Linux CPython 3.13.5, genuine local private temporary files and hardlinks, synthetic JSON, no EXEs, no financial files. `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_report_*r3*.py'` ran **54/54 PASS** (18 repaired R337 + 18 existing R339 + 18 new R340) and `python -OO -W error` likewise **54/54 PASS**. Total **108/108 focused executions**, zero skips; Python compilation passed. Local source and all three test files were byte-identical to their committed Git blobs.

**Pre-fix reproduction:** Exact R339 `report_evidence.py` blob `4a0608e10b108c15c34854206c55b7502369ffea` generated **7 errors / 18 cases** in the new R340 tests; exact pre-fix R337 test blob `0c33d7cafc6c42f48a63d5efe84e840b2b06efed` generated **5 errors / 18 cases** against R339 source. Both failures were fixed without executing or distributing binaries.

The full private repository suite, 22 genuine AES-GCM tests, Windows native ACL checks, all six EXEs, Defender and GUI/accessibility acceptance were **not** executed locally. Synthetic evidence is never release authorization. Report stage paths remain retained by design; operators must review and safely clean up only after retention requirements are satisfied.

## Hosted CI and next acceptance

R340 [GitHub Actions run #42919549976](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42919549976) concluded **failure** on 2026-11-10 at head `35b9bb9d67616e18c32756faf68e84afdd8738cb`; Ubuntu `source-tests` job `130190648708` and Windows `windows-build` job `130190649162` both had **zero recorded steps and no job logs**. This repeats parent [R339 run #42910279490](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42910279490), also zero-step failure. R339 check-run annotations exist, but the GitHub connection cannot fetch annotation details. Root cause remains **unconfirmed**; no hosted test claims. Check GitHub Actions billing/spend authorization, workflow permission/eligibility and runner allocation; obtain actual job logs.

**Next:** unblock real Ubuntu/Windows runners; run the complete desktop normal/`-OO` suite including the 22 genuine AES-GCM cases and all R38/R337/R338/R339/R340 report suites; then private Windows 11 x64 PE/Defender/SHA/smoke/NTFS-ACL/accessibility and premium-entitlement review. Do **not** merge or release until independent QD review and founder authorization. No WordPress, billing, production branch, public downloads or premium gates were modified.
