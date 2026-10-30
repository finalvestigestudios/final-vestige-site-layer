# R49 — Verify premium human-review commit after disk sync

**Pre-release engineering safeguard; not distribution approval.** Applies only to the human exception-review journals of **GrantAudit Studio Pro** and **ProcureGuard Studio Pro**. The four free utilities, original financial calculations, premium entitlement rules, and Final Vestige site/QD workflow are unchanged.

## Failure mode closed

R47 verified the source CSV and existing hash-linked JSONL history **before** writing, and R48 added descriptor-owned exclusive writer locks. A successful `os.write` and `os.fsync`, however, did not by itself establish that the expected new human decision remained readable and intact afterward. A local filesystem change, partial/ambiguous write, or observed journal mutation after the append could have left `append_review` returning an event that no longer matched the stored journal.

R49 makes acknowledgment conditional on **read-after-write confirmation while the writer lock is held**:

1. Require the R48 writer-lock ownership check before reopening anything.
2. Re-read and validate the entire original source report, including its SHA-256-bound cases, and require equality with the pre-append `ReportBatch`.
3. Re-read the **full** JSONL journal through the existing bounded, descriptor-checked reader. That reader checks the complete hash chain, CSV source binding, timestamps, case references, event schema and event hashes.
4. Require the complete resulting sequence to equal **every previously verified event plus exactly the newly written human event** (no omissions, edits, reorderings, duplicate or extra entries).
5. Re-check writer-lock ownership before reporting the operation successful.

Any failed check raises instead of returning success. The verifier itself is read-only: it does not repair, delete, retry, publish, or upload financial records. `reviewed` is merely a recorded human workflow state; **it does not authorize grant eligibility, disbursement, purchase approval or payment**.

## Operator response to post-write errors

**A failure after append is an indeterminate outcome, not proof that no human decision was recorded.** Do not blindly click Review again. Stop all app instances, preserve source CSV, JSONL journal and any lock file in an access-controlled local location, record independent SHA-256 fingerprints, and validate the exact source/journal pair. Check whether the intended event is already present exactly once, whether the journal is truncated, or whether the report changed. If validation fails, escalate to a human reviewer or administrator; do not silently truncate a journal or remove an unexpected lock. Resume only after documenting the recovery decision. No automatic spending/compliance approval is ever permitted.

This is **observed local consistency**, not an immutable audit log, digital signature, privileged-adversary defense, encrypted-at-rest solution, durable-storage guarantee or protection against post-confirmation changes. The source size (64 MiB), journal size (16 MiB) and event count (20,000) limits still apply. Re-reading adds bounded local I/O, not cloud traffic or telemetry.

## Test evidence and open gates

Focused local Linux Python 3.13.5 tests on a reconstructed **helper+unit-test-only** subset: **16/16 pass normally and 16/16 under `python -OO`**; `compileall` passed. The exact local Git blob SHA-1 values are `d2196e67acc81cb6fd86174fb8943c7afa57805d` for `review_commit.py` and `779f64c08d57f87e91928c69a283cf87df4ab434` for `test_review_commit_r49.py`, matching committed GitHub blobs. The unit tests use synthetic local CSV/JSONL evidence and injected readers.

Four additional **committed but not yet locally executed** end-to-end tests exercise both premium products, consecutive human decisions, changed decision text after fsync, an alleged append that wrote nothing, and source mutation after fsync. Run them in a trusted complete checkout:

```sh
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p test_review_commit_r49.py -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -m unittest discover -s products/desktop/tests -p test_review_commit_integration_r49.py -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p test_review_commit_r49.py -v
PYTHONPATH=products/desktop PYTHONWARNINGS=error python -OO -m unittest discover -s products/desktop/tests -p test_review_commit_integration_r49.py -v
```

The Linux/Windows workflow adds both R49 test modules under optimized Python and retains the full regression suite. **CI has repeatedly failed before any recorded steps**, so neither hosted full-suite results nor actual Windows x64 executable tests, malware scans, premium-access checks or human QD acceptance have been established. Do not publish free or premium executables until all release gates are independently met.
