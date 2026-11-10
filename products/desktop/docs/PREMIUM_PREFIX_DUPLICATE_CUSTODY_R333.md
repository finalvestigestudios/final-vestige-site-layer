# R333 — Premium review-journal prefix reader FD ownership

**2026-11-10 | Draft / issue #73 | QD + founder HARD HOLD.** Based exactly on R332 draft PR #1919 (head `262c2be3379655243c9fe97fe6d1cdb32564b77b`), not production `main`. Applies to the shared custody path used by GrantAudit Studio Pro and ProcureGuard Studio Pro. The other four standalone free apps are unchanged.

## Demonstrated defect and correction

The R329 `digest_pinned_prefix()` helper duplicates the pinned review-journal descriptor so that it can hash prior human-review history before and after an append. Its old `os.fdopen(...)` exception handler closed a duplicate only when `fdopen` itself raised. If `fdopen` returned a stream whose context manager **raised in `__enter__`**, Python never invoked `__exit__`, and the duplicate remained open. This orphaned a private audit-evidence handle. A synthetic `PermissionError` and a `KeyboardInterrupt` injected during context entry reproduce this exact leak against the R332 predecessor.

R333 keeps the duplicate owned by the hash helper until *successful* context entry. Its `finally` closes an untransferred duplicate on fdopen failure, context-entry failure, or interruption; successful context entry transfers ownership to the stream's context manager. Duplicate closure never intentionally closes the caller's original pinned descriptor. Existing bounded SHA-256 chunking, exact append readback, no-path-reopen behavior and human-review requirements are unchanged.

This protects against setup faults; it does **not** prove immutability under privileged filesystem attack, nor is it a signature, compliance approval, Windows execution test, or protection for premium downloads. The outer journal API remains responsible for redacting OS-error detail before showing it to end users.

## Locally executed evidence

- Linux CPython **3.13.5**, synthetic temporary review data only. Exact committed R333 source/test Git blobs were copied into an isolated test slice and checked by `git hash-object`: source `a78a2b3b62150576f1f5ad4d41b969da8693dced`; tests `654d813a5ebade133eebbb1658fb1f867aabbd45`.
- New focused module: **15/15 PASS** with `-W error` and **15/15 PASS** under `-OO -W error` = **30 passing method executions, 0 skips**; `py_compile` PASS.
- Also replayed the **exact existing R329 10-case prefix-witness regression module** (Git blob `97aca985b6839d4e57c2f8ceb26d3503ea0cc61b`) alongside R333: **25/25 PASS** normal and **25/25 PASS** optimized = **50 total focused method executions**, zero skips. R329 unchanged and not re-committed.
- Synthetic regression against the unmodified predecessor: **2/15 FAIL** (descriptor still valid after injected `__enter__` `PermissionError` and `KeyboardInterrupt`), as expected before fix. All other methods passed.
- Cases cover duplicate creation/open/enter/exit/interrupt/hash failures, original-descriptor preservation, empty/multi-chunk/truncated prefix hashing, unchanged postappend prefix, exact append readback and no path reopen.
- **Not executed:** whole private repository suite, 22 genuine AES-GCM integrations, hosted CI test steps, Windows 11 x64 builds/smokes, malware scans, native accessibility or premium entitlement verification.

Local exact-blob replay:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_prefix_fd_ownership_r333.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_prefix_fd_ownership_r333.py'
python -m py_compile products/desktop/fvs_suite/journal_write_receipt.py products/desktop/tests/test_journal_prefix_fd_ownership_r333.py
```

Both CI jobs' existing source discovery invokes `products/desktop/scripts/offline_source_gate.py`; this new `test_*.py` module is discoverable there, but **the full gate has not run**.

## Release hold and next highest-impact action

Hosted Actions previously failed before recording a single step. Inspect billing/spending limits, Actions workflow permissions and available Ubuntu/Windows runners; repair the scheduling block and rerun the **complete** private checkout source gate in normal and optimized modes, including **22 genuine AES-GCM** integrations and the R333 test. Then build and privately smoke all **six** Windows 11 x64 candidates, verify checksums/Defender/accessibility and protect premium distribution. Do not merge any stacked PR until independent QD review and explicit founder approval. No EXEs or customer files were published.
