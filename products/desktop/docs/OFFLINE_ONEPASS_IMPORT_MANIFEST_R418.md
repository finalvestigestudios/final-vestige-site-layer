# R418 — one-pass bounded import manifest for six-app source evidence

**Internal source-evidence fix; release HOLD.** Stacked on R417 draft #2425; issue #73. No executable, license, customer data, website or premium download changed. Independent QD review and explicit founder approval are still necessary.

## Bug and fix

Before R418, `source_digest()` performed `_verify_source_directories()` to enforce 512-file / 128-directory / 16,000,000-byte import inventory limits, **then independently materialized an unrestricted `Path.rglob("*")` result**. Files inserted between those passes could evade the previous preflight budget. The second recursive enumeration also duplicated filesystem work and weakened the relationship between the inspected inventory and what was hashed.

R418 returns the validated `Path` manifest from `_verify_source_directories()` and hashes only that manifest (plus the required runner file). The same bounded walk now defines both the inventory budget and the hashed filename set. Each file is still reopened through the R417 verified descriptor path; sorting, SHA-256 labels, launcher AST route checks, source mutation checks before/after each child, and `release_authorized=false` are unchanged.

**Limits of this hardening:** It is not an OS sandbox, an immutable source snapshot, a code signature, native Windows binary evidence or a release authorization. A hostile actor who can alter directories concurrently still requires a trusted/isolated checkout; individually checked file descriptors cannot freeze their ancestor directories. CI runner availability and genuine Windows acceptance remain separate blockers.

## Artifact list

- `products/desktop/offline_source_smoke_r408.py`: one checked, bounded import enumeration reused for the SHA inventory
- `products/desktop/tests/test_single_inventory_r418.py`: 12 synthetic/adversarial regression methods; verifies absence of `Path.rglob`, both import roots, asset mutation, deterministic digest, 513-file limit, 129-directory limit, total-byte limit, compiled import rejection, symlink/hardlink refusals, and six dual-mode synthetic launcher exits
- `.github/workflows/desktop-source-evidence-r385.yml`: run R418 regressions under normal Python and `-OO`, on Ubuntu 24.04 and Windows latest

## Test evidence and reproducibility

**Local Linux Python 3.13.5:** A separately authored *extracted scanner model* exercised ten targeted cases in standard `-W error` and `-OO -W error` mode: **10/10 + 10/10 PASS (20 focused executions)**. The model is not the complete committed runner, and its tests are not the exact new committed R418 test module. Do not represent these passes as exact-checkout validation.

**Committed-code gates still required from a trusted complete checkout:**

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_single_inventory_r418.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_single_inventory_r418.py
python -I products/desktop/offline_source_smoke_r408.py
```

The source CI workflow requests the first two commands on both Windows and Ubuntu. The R408 gate command is already in its earlier workflow step. All six real financial engines, release candidate Windows x64 EXEs and native desktop GUI remain **unverified** by local R418 tests.

At R417 HEAD `f4480dd692f95bfdf0bbef6519f651fa436da364`, [source CI #43554272032](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43554272032) and [desktop build #43554271993](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43554271993) failed before any recorded job steps (all four `steps=null`, `logs_url=null`). Runner allocation/billing cause is **not confirmed**. Inspect exact R418 commit runs; an all-red pre-run status is not a code test failure.

## Next highest-impact acceptance

Restore GitHub Actions runner eligibility or run the exact committed checkout on a trusted Windows/Ubuntu machine; execute *all inherited financial Decimal/provenance, cryptographic and entitlement suites* before acceptance. Only then build and smoke each of the six real Windows x64 executables, scan with Defender, complete keyboard/NVDA/high-DPI tests, verify SHA-256 release receipts and prove premium gated downloads deny unauthorized access. Require independent QD and explicit founder approval before merge, distribution or site publication.
