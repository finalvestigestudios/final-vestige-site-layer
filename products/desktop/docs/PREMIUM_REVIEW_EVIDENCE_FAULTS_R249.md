# R249 — Fail-closed premium review evidence faults

**Issue #73 · source-only feature branch stacked on R248 · DRAFT · QD + founder HARD HOLD**  
**Scope:** GrantAudit Studio Pro and ProcureGuard Studio Pro (shared human-review workbench). The four free applications and all six financial engines are unchanged.

## Defect and correction

On R248, `ReviewQueue.verify_current` cleared its loaded report, journal and exception batch only for `ValueError`, `OSError` and `UnicodeError`. A bug in a report parser, state reader, or filesystem fingerprint helper raising another exception (such as `RuntimeError` or `TypeError`) left the previous batch selected. The Tk review window likewise caught only those three exception families. An unexpected failure could leave stale financial rows visible and allow a later operator action against the old queue. A malformed/incomplete queue failed its initial check **before** the cleanup handler.

R249 changes `verify_current` to a success-flagged `try/finally`: any unsuccessful validation — including incomplete queue state, callback bugs and `BaseException` interrupts — clears all four actionable fields. **Exceptions are still raised unchanged from the queue layer; it does not hide software faults or claim compliance approval.** Valid evidence retains its selection and the exact report/journal consistency checks.

The premium GUI now clears the loaded selection and visible report rows for unexpected failures during source/journal verification, report loading or rendering; it shows fixed, customer-path-safe errors rather than reflecting raw exception text. The post-append catch similarly clears the queue and tells the operator to **inspect the local journal before retrying**, because a write may have committed before a subsequent unexpected error. This is an ambiguity hold, **not** a claim of rollback. No original report or journal is deleted or modified by these error handlers.

## Artifacts

- `products/desktop/fvs_suite/review_queue_load.py` — success-flagged fail-closed `finally` after any unsuccessful revalidation.
- `products/desktop/fvs_suite/review_ui.py` — redacted unexpected-fault handlers for validation, initial load/display, and ambiguous post-review refresh.
- `products/desktop/tests/test_review_evidence_fault_r249.py` — 17 synthetic queue regression methods (expected/unexpected faults, both journal fingerprints, missing fields, valid path, `KeyboardInterrupt`, `SystemExit`).
- `products/desktop/tests/test_review_ui_fault_wiring_r249.py` — 7 displayless tests that compile the actual nested Tk callback AST; they check catch/scrub/redaction and post-append journal-inspection language.
- `.github/workflows/desktop-build.yml` — Ubuntu and Windows normal + `-OO -W error` R249 jobs before complete suite/packaging.

## Measured local evidence and limits

**Reproduction:** The unmodified R248 `review_queue_load.py` (blob `5573cb05e6672dbe864f6bcf062033fbe53e22b9`) was copied byte-for-byte into a local minimal Python package. New 17-case suite yielded **11 failures**, exposing retained queue state after unexpected exceptions, incomplete queue, and interrupts.

**Patch test:** Patched module hash `d30334e9f37bf78feae0d5949f09f70811fadaf0` matches the committed GitHub source blob. New queue test blob `b27565c87e1d930ce7660ebf9ed4d45d3a33c02f` matches the committed GitHub test blob. Local Python 3.13 environment ran **17/17 PASS** (`python -W error`) and **17/17 PASS** (`python -OO -W error`): **34/34 method executions**; `compileall` PASS. Synthetic in-memory batch data; `review_identity` was a local stub and `journal_snapshot_identity` was explicitly mocked. The real journal implementation, GUI and full repository were **not executed locally**.

**Important:** The 7 GUI AST callback tests are committed to the repository but **not locally executed against the real full GUI**. The real source was inspected and patched directly via GitHub. Hosted CI on Ubuntu/Windows is required to establish integration. No Windows 11 x64 native Tk checks, built EXEs, antivirus scan, access-controlled premium download validation or full suite results are claimed.

## Next high-impact verification and release gates

1. Restore GitHub Actions if both runner jobs continue failing before any steps (owner to inspect Actions billing/spend controls, workflow permissions and runner provisioning). Rerun **exact R249 SHA** unchanged.
2. Execute 17 queue + 7 GUI callbacks in both Python modes on Ubuntu/Windows, then R247–R249 inheritance, full six-app source and smoke regression gates. Independently exercise real Windows 11 x64 Tk cases with synthetic signed premium entitlements.
3. Only after green QD: privately build six Windows x64 EXEs; checksum, malware-scan, smoke-test and keyboard/NVDA/high-DPI verify. Test protected payment/license distribution for GrantAudit Studio Pro and ProcureGuard Studio Pro. Obtain independent QD/founder authorization before release.

**Release HOLD:** No publishing, `main` changes, website deployment, premium file exposure, signing private keys, telemetry, real customer files, auto-approved payments or compliance findings.
