# R46 — Atomic, source-checked premium human-review registers

**Status:** Engineering-only, unreleased. Applies to **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. No site, pricing, licensing, issuer keys, production branch or QD approval changes.

## Why this matters

Previously `exception_review.export_register` wrote a final `review-register-*.csv` directly. An interrupted/disk-full write could leave a plausible-looking **partial human decision register**. The exporter also did not verify that its source exception CSV and hash-linked JSONL journal remained unchanged during export. These records concern human review, **not** eligibility, fraud, payment authorization or compliance determinations.

## Behavior after R46

1. Re-validate the selected product's exception report with `read_cases` and the **entire** review-event journal with `read_journal`. A changed report or broken journal fails closed.
2. Use the existing premium CSV header order, original source row references, and latest manually recorded review state. No new automated decisions.
3. Stage the complete sanitized UTF-8-BOM CSV in the **chosen local directory**, using the shared `atomic_reports.write_csv_report` writer. Preserve existing `_csv_cell` spreadsheet-formula protection.
4. Before staging can be published, **re-read the complete source report and journal**. If any report digest/case ordering or any event history differs from the initial snapshots, reject the export.
5. Flush/sync the staged CSV and atomically publish it without replacing a prior output. On failures, leave no final partial register and remove the temporary file. On POSIX the existing shared writer publishes by exclusive hardlink; on Windows by non-replacing rename.

This does **not** provide a continuous filesystem lock or authenticated anti-rollback: an actor may change the files again **after the final check**. A malicious administrator controlling source, journal and historical anchor can still rewrite evidence consistently. Operators should retain independently trusted evidence hashes and use access-controlled local folders. Output CSVs and source JSONL journals remain **unencrypted plaintext** unless separately protected/archived by approved procedures.

## What changed

- `fvs_suite/review_register.py`: focused snapshot-consistency and atomic publication helper.
- `fvs_suite/exception_review.py`: both premium products' existing `export_register` delegate to the helper; `read_cases`, `read_journal`, `CSV_FIELDS`, and `_csv_cell` retain authority.
- `tests/test_review_register_r46.py`: 20 synthetic regression cases for source/journal mutation, all-history comparison, collision/no-clobber, symlink handling, incomplete writes, UTF-8 BOM, Excel formula neutralization delegation, pending human states and POSIX permissions.
- `.github/workflows/desktop-build.yml`: dedicated Python `-OO` regression invocation on Ubuntu and Windows. Complete desktop regression remains in the existing CI steps.

## Operator checks — trusted full checkout

```bash
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_review_register_r46.py' -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_review_register_r46.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_premium_review_csv_r20.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
```

Then repeat the complete suite on **trusted Windows 11 x64** and manually inspect both premium review queues/exported registers (keyboard focus, Narrator/NVDA, source row references). Use **synthetic data** for development. **Do not** upload customer reports, journals, screenshots containing customer financial data or premium executables as public CI artifacts. Until native EXE build/smoke, malware scan, SHA-256, entitlement-controlled premium fulfillment and separate **human QD approval**, all six downloads remain on **release HOLD**.

## Known verification boundary

R46 focused source tests can execute on a reconstructed Python subset; they do **not** by themselves prove full `exception_review.export_register` integration, all existing premium journal semantics, an actual Windows filesystem, native x64 packaging, or Windows UI usability. The R20 real module integration and full suite must run in a complete checkout. If GitHub Actions jobs again fail before step 1 with `404 BlobNotFound`, capture run/job IDs and ask the repository owner to troubleshoot runner provisioning, billing/usage and GitHub Support; do not mistake this for a passing or failing application test.
