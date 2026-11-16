# Labs R477 — deterministic cross-purchase-order audit citations (DRAFT / QD HARD HOLD)

## Product risk and implemented change

The cross-PO reuse evidence materializer used `set` iteration to construct its returned PO/line mapping and `sorted(rows, key=int)` for row citations. Across independent processes with different Python hash seeds, two distinct row labels representing the same numeric row (e.g., `2` and `02`) can swap places, and the affected PO/line mapping can be emitted in different orders. The ordinary CSV loader emits canonical physical row numbers, so the row-tie example is a **defense-in-depth direct-helper case**, not proof that normal CSV ingestion has exhibited it.

R477 makes audit evidence byte-order stable:
- Return PO/line mapping keys in lexicographic tuple order, irrespective of hash-seed, source group insertion order or document expansion order.
- Sort physical row citations by `(int(row), len(row), row)`: numeric ordering with a stable shortest-spelling-first and lexical final tie-breaker. Identical numeric row references preserve their original strings; no rows are silently discarded beyond the existing set deduplication.
- Apply this through the shared `_materialize_index` so invoice, credit, receipt, return and legacy typed wrappers all use the same ordering.
- Preserve R475/R476 **combined** one-million-citation budget, up-front all-type reservation, hard failure without partial evidence, local-only sources, exact Decimal calculations, original row citations and human-only compliance decisions. No payment approvals or fraud assertions.

## Tracked artifacts

- `products/desktop/fvs_suite/procurement_cross_po_r471.py`: canonical ordering inside existing materializer (Git blob `82e2cba446602c75a989fbfe3a482e6aaf999c18`).
- `products/desktop/tests/test_procurement_cross_po_canonical_r477.py`: **8 committed methods**, Git blob `fadb587ef2c1fb3f8e4ea0e31bcedf5fd0dee972`. Tests cover numeric-equivalent row ties, merged-document rows, four typed streams, legacy wrappers, 125 shuffled source-input permutations, 8 independent `PYTHONHASHSEED` processes, same-PO exclusion, and private-data-free atomic budget errors.
- `.github/workflows/desktop-source-evidence-r385.yml`: both `python -W error` and `python -OO -W error` executions added to the independent six-engine source-evidence workflow (Git blob `908b71db5ec64930baf32b177ef55d80aaf9e0d4`).

## Actually executed verification (Linux Python 3.13.5)

A local **isolated functional reconstruction of the modified cross-PO module** ran the exact committed eight-method test file; its local `git hash-object` equals the GitHub blob SHA `fadb587ef2c1fb3f8e4ea0e31bcedf5fd0dee972`.

- `PYTHONPATH=. python -W error -m unittest discover -s tests -p test_procurement_cross_po_canonical_r477.py`: **8/8 PASS**.
- `PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p test_procurement_cross_po_canonical_r477.py`: **8/8 PASS**.
- `python -m py_compile` for the reconstructed helper and exact committed test: **PASS**.
- A controlled negative-control switch back to the **legacy ordering expression** yielded **6 failing methods of eight** in normal mode; restoring canonical ordering returned **8/8 PASS**. The test covers 125 permuted event sequences and eight fresh hash-seed interpreters per mode.

**Evidence limitation:** the local helper was reconstructed from the committed business logic, **not byte-identical to the complete 7.8 KB GitHub helper module**. These are isolated focused contract tests, **not** execution of the complete GitHub checkout, the actual 38-method ProcureGuard CSV integration suite or the six-application regression matrix. GitHub's exact source blob and test blob have been read back and verified, but the corresponding full native CI tests and Windows x64 builds remain pending. Do not treat local success as a release certificate.

## Known CI blocker and release gates

The parent R476 workflows finished `failure` with all four jobs having `steps=null`: [six-engine source workflow](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43915082144) and [internal Windows build](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43915082019). No application test steps ran; underlying account/runner cause not confirmed.

**Smallest unblock:** A GitHub repository/org administrator checks check-run failure annotations, billing/spending eligibility, Actions permissions and runner assignment, restores a runner, then runs R477 exact-head source tests (both modes), ProcureGuard full CSV integration, all six source engines and Windows packaging before any release decision.

**QD governance:** Draft stacked PR, never directly modify `main`. No binary, download URL, premium license, entitlement, WordPress publication, merge or release authorization. Independent QD review, founder approval, Defender checks, installed keyboard/screen-reader testing, SHA256 and premium access controls are still outstanding.
