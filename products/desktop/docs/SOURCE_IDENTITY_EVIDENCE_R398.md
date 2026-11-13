# R398 — Source identity whitespace and human-review evidence custody

**Scope:** issue #73; isolated branch stacked on R397. **DRAFT / NO RELEASE / QD + founder HARD HOLD.**

## Defect reproduced

The shared `raw_values()` helper called `str(row.get(...)).strip()` twice.
Consequently `{"id": " A"}` and `{"id": "A"}` collapsed to one label and
`normalized_collision()` returned false. Whitespace-only source labels were
discarded, and a nonnative value could execute an untrusted `__str__` hook.
The shared CSV importer also trimmed ordinary ASCII identity whitespace
*before* matching or report construction, losing the evidence at ingestion.

Synthetic prepatch reproduction, no customer records:

- source labels `" A"`, `"A"`: old raw values `("A",)`; new raw values retain both;
  new flag `normalized_id_review`; human display `\\u0020A; A`.
- source label NBSP: old raw values empty; new literal original retained, with
  `\\u00A0` in the visible review rendering.
- source label two ASCII spaces: old raw values empty; new visible
  `\\u0020\\u0020`.

This is a potential *false clean-match or missing-review-evidence gap*, not a
reported fraud event, confidentiality breach, or compliance finding.

## Code

1. `fvs_suite/review.py`: preserve exact native source strings; reject
   non-string direct API labels without calling potentially malicious
   `__str__`; preserve empty-versus-whitespace-only distinctions; explicitly
   escape boundary ASCII spaces in human display while retaining interior spaces;
   preserve `\\u003B` escaping for semicolons and existing Unicode escapes.
   The identity comparator still ignores *ASCII letter case only*.
2. `fvs_suite/engine.py`: preserve source spelling for ten review-related CSV
   fields: `id`, `program`, `vendor`, `invoice_number`, `po_number`, `line`,
   `document_id`, `related_document`, `ledger_reference`,
   `related_claim`. Matching key normalization and financial/date/category
   parsing remain separate and unchanged. Original input snapshots and physical
   source line numbers remain authoritative.
3. `tests/test_review_source_identity_r398.py`: **29** synthetic unit
   methods covering provenance-preserving labels, ASCII/Unicode boundaries,
   nonnative/subclass hooks, deterministic report labels, equivalent case,
   reconciliation flags, numeric variance, and caller row immutability.
4. `tests/test_import_identity_integration_r398.py`: **10** full-checkout
   integration methods covering table source hash, original file immutability,
   LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, GrantAudit Studio Pro,
   and ProcureGuard Studio Pro. Policy Delta Desk remains unaffected; no false
   claim of six-app feature testing.
5. `.github/workflows/desktop-source-evidence-r385.yml`: invoke both test
   modules in standard and `python -OO -W error` modes on Ubuntu and Windows.
   No new upload artifacts, network calls, binaries, or release actions.

## Execution evidence (bounded)

- Linux CPython 3.13.5 exact-Git-blob **focused source subset**, not a
  reconstructed parser: **29/29** standard and **29/29** optimized,
  **58/58 method executions PASS**. Python source compilation PASS.
  Four locally executed files were byte-identical to the committed R398 Git blobs:
  `fvs_suite/review.py` = `745a4ed8909b2c256d983b16e031ded7b23a97cb`;
  `fvs_suite/audit_display.py` = `a8e0858fb7fd37caf8daf8a78ab5329678c05895`;
  `fvs_suite/unicode_hazards.py` = `50801b3f168396b0e2c75e95352e435f7c936588`;
  `tests/test_review_source_identity_r398.py` =
  `6472252aa83f358433d631d4bf231068bb0885c0`.
- The locally executed source subset is **not** the entire repository checkout.
  It does not establish actual CSV engine behavior or inherited regressions.
  The changed `engine.py` importer has been committed but not locally executed
  against the whole repository. The **10** committed real-import integration
  cases have **not been executed**. No native Windows execution, packaged EXE,
  Defender scan, AES-GCM, Ed25519/SQLite validation, accessibility certification,
  or distribution authorization was performed.
- Exact R398 initial HEAD `734d90e8cb3881cbfcb7bcbae32df3d737a9a03f`
  source [#43398741172](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43398741172)
  and build [#43398741140](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43398741140)
  failed before runner allocation, both jobs per workflow with no steps.
  The cause is unknown; this is missing verification, not a code-test result.
- Inherited R397 exact HEAD `46fea6c631926b62d11e0b65b0fa13cfa52deeb1`
  source [#43391118236](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43391118236)
  and build [#43391118246](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43391118246)
  failed **before runner/step assignment** (both jobs in each had null steps).
  Root cause not established. Check new R398 exact-commit CI results before
  attributing any failure to code.

## Required reviewer acceptance

1. Restore eligible GitHub-hosted runners / Actions billing allowance and run
   the exact R398 SHA on Windows and Ubuntu. Confirm **39** methods (29 unit +
   10 end-to-end) in both modes and inherited financial/Decimal/provenance,
   premium review, AES-GCM and Ed25519/SQLite suites.
2. Review conservative identity behavior change against representative **synthetic**
   CSV layouts. In particular, source values differing only by boundary
   whitespace must now require *human review*, while unchanged ordinary keys
   and exact Decimal cents continue to reconcile.
3. Perform native six-executable Windows x64 smokes and verified source hash,
   Defender, keyboard/screen-reader accessibility, gated premium download and
   signing/checksum acceptance. No premium or public binaries while blocked.
4. Independent QD review + explicit founder approval are prerequisites for
   merge, deployment, public download, license issuance or release.

**No production `main` changes or WordPress publication. No customer
financial data, auto compliance/payment decisions, paywall changes, or new
download URLs. All six apps remain UNRELEASED.**
