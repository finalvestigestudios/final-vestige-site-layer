# R221 — Native dictionary-storage custody for local CSV audit evidence

**Status: DRAFT — QD / founder HARD HOLD.** Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Based on R220 [draft PR #1172](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1172) at immutable head `25735edf535986ebb80422e54a22b85ef3d0a05d`, not `main`. No production merge, binary upload, public download, or unprotected premium publication.

## Reproduced issue

The shared `write_csv_report` copied `row.items()` from any `Mapping`, including a Python `dict` subclass. Such a subclass can override `.items()` to **fabricate the transaction identifier and Decimal amount** even though its actual built-in dictionary storage holds different values; it can also conceal a missing mandatory source-reference column or a dangerous ignored extra cell. R217's native two-tuple validation did not detect *well-formed, but forged* tuples.

A synthetic direct-API reproducer on byte-exact R220 sources successfully published a fake row ID and amount. No exploitation in real customer records is asserted; the normal CSV importer already produces native dictionaries.

## Implementation

For `dict` and subclasses, the writer uses the built-in `dict.items(row)` descriptor, which accesses actual native stored entries instead of virtual subclass overrides. Other `Mapping` implementations retain their R217 pair-shape checks and backward compatibility (including `UserDict` and `MappingProxyType`). The existing **256-key/200,000-row/64 MiB** caps, formula checks, native `str`/`int`/`Decimal` sanitizer, UTF-8 BOM, no-overwrite atomic staging, cleanup and exception privacy remain unchanged. This is evidence rendering, **not** a fraud/compliance decision.

### Source and test artifacts

- `products/desktop/fvs_suite/atomic_reports.py` — real producer correction, Git blob `63909a4535f6a47af18fc01c1e1da8344a0b35b9`.
- `products/desktop/tests/test_atomic_native_dict_snapshot_r221.py` — **20 new regression methods**, Git blob `e601abd446fe53e2274b9d78a034e2f116066fc7`. Cases cover forged identifiers and money, hidden formula/oversized extras, missing source references, private malicious hooks, late-row rollback, pre-existing evidence, Decimal scale and deterministic output.
- `.github/workflows/desktop-build.yml` — adds explicit R221 normal and `-OO` test steps in **both** the Ubuntu `source-tests` job and Windows `windows-build` job; private test diagnostics remain suppressed in hosted logs.

## Local test evidence (reproducible, **not full-repository CI**)

On **Linux x86_64, CPython 3.13.5**, a private reconstructed package used byte-for-byte exact GitHub source blobs for the R220 `atomic_reports.py` (`085cf2ffb7db7b9efb6c750feea28034de6cd6c7`), `csv_formula_guard.py` (`79e49395947db9bf5f2ea26a323243c73968a1b1`), and `csv_native_cell.py` (`1030e18d445a62f4afbde0f74e1796094fbc138d`). Its new R221 source and test files also matched the actual committed Git blobs. Test fixtures are synthetic, created in OS temporary directories.

Before patch, the new 20-case test suite: **9 failures, 6 errors, 5 passes**. In particular, the forged transaction ID and currency value were emitted by the original publisher. After the patch:

| Source-owned tests exercised locally | Normal mode | `python -OO` |
| --- | ---: | ---: |
| New R221 (`test_atomic_native_dict_snapshot_r221.py`) | 20 / 20 PASS | 20 / 20 PASS |
| Inherited byte-exact R217 (`test_atomic_pair_shape_r217.py`) | 17 / 17 PASS | 17 / 17 PASS |
| Inherited byte-exact R27 (`test_atomic_reports_r27.py`) | 11 / 11 PASS | 11 / 11 PASS |
| R220 **18 isolated native-module test methods**, manually transcribed from original 25-case suite | 18 / 18 PASS | 18 / 18 PASS |
| **Focused total** | **66 / 66 PASS** | **66 / 66 PASS** |

**132/132 method executions**, zero skips, `PYTHONWARNINGS=error`, Python `compileall` PASS. The R220 integration section (7 tests) was **not** executed locally; the manually copied R220 unit test subset is **not** byte-identical to its original full test file. There is **no** intact-checkout full inherited six-engine integration result, hosted Ubuntu/Windows pass, real native Windows executable validation, GUI accessibility observation, live premium entitlement test, or Windows Defender acceptance. These are explicit unresolved release gates.

## Review / remaining limitations

The guard covers `dict` and its subclasses in this direct writer. Non-`dict` custom `Mapping.items()` can still supply values through a virtual view, subject to R217 structural validation; changing that public contract requires a separate compatibility review and fail-closed design. Re-run the **complete inherited regression suite on actual Ubuntu and Windows checkouts**, especially the seven R220 integration methods plus LedgerDiff/Invoice Twin/SpendMap/Policy/GrantAudit/ProcureGuard end-to-end export paths.

If hosted jobs again have `steps:null`, the repository owner must inspect the run page's pre-start banner, Actions usage/billing/policy/runner provisioning and restore runner allocation; rerun the unchanged PR HEAD. Then private Windows x64 six-launcher builds, hashes, malware scan, smoke and accessibility review, protected premium entitlement verification, independent QD, and founder release authorization. Do not release or merge ahead of those gates.
