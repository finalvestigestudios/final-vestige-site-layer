# R328 — Byte-exact post-append custody for premium review journals

**Status:** Draft, issue #73, independent QD + founder release **HARD HOLD**. Nothing in this sprint authorizes release, payment approval, automated compliance decisions, premium download distribution, or production/site changes.

## Measurable defect and change

The two premium desktop programs share `fvs_suite.journal_io.append_verified_event`. Prior to R328, it verified a stable original journal, ran the audit-chain callback, appended with `O_APPEND`, called `fsync`, and checked the resulting size/path. However, **a same-length wrong-content write can pass size/metadata checks**. This was reproduced by intercepting `os.write` and writing a modified same-length synthetic review event: the predecessor returned success despite wrong appended bytes.

R328 keeps the descriptor pinned and changes the append open mode from `O_WRONLY | O_APPEND` to `O_RDWR | O_APPEND`. After `fsync` and expected final size validation, new `journal_write_receipt.require_exact_append_readback` seeks to the known append start on the **same descriptor** and reads back up to the event length + 1 byte. It requires **byte-for-byte equality** with the intended event. Empty, short, extra, corrupted, or unreadable readback now HOLDs. `O_APPEND` is retained. Existing symlink/hardlink/FIFO, stat/inode, verified-callback, size-limit, stable-path, private-error, and journal-lock gates remain; no new path reopen, telemetry or financial data transfer is introduced.

**Compatibility consideration:** Journal append now requires read **and** write permission on its existing file. Normal review flows already need to read previous evidence to verify the chain, but write-only journal permissions that previously allowed the low-level writer to open will now fail closed. Windows x64 behavior requires actual Windows acceptance testing. If a check fails **after the bytes have been appended**, evidence is intentionally retained for manual forensic review, not rolled back or silently approved.

This check verifies the intended append bytes **at the observed moment**. It is **not** a cryptographic signature, Windows filesystem adversary guarantee, proof that the journal cannot change later, or authority to make compliance/payment decisions.

## Focused executed evidence — November 10, 2026

Local OS: Linux; CPython 3.13.5. Synthetic temporary files only. Source test rig locally reconstructed the R327 `journal_io.py` and the precise `_same_path_descriptor_signature` helper; **this was not a complete private repository checkout**. The 3 edited/new production/test files run locally match exact committed Git blobs:

| Artifact | Committed blob SHA |
| --- | --- |
| `products/desktop/fvs_suite/journal_io.py` | `d16c86e51b8278d0afb8eb9288ab2ef5ed8a633d` |
| `products/desktop/fvs_suite/journal_write_receipt.py` | `73c2fd14ae8fad5616214c4043a41abfbeae286f` |
| `products/desktop/tests/test_journal_write_receipt_r328.py` | `bb67741ac593c5a3347a5d31dfdfdb65344f242d` |

Focused new regression module: **14/14 PASS** under `python -W error`; **14/14 PASS** under `python -OO -W error` = **28 passing test-method executions**, no skips; `py_compile` PASS. Three integration cases expected to reject post-append corruption, truncated readback, and path-bearing OS errors were observed **FAIL** against a reconstructed R327 predecessor (writer had no readback), and **PASS** with R328. Tests also cover empty/new and existing-file append, precise byte comparison, extra/short/corrupt helper data, failed seek, invalid witness parameters, callback HOLD, and sanitized permission errors. Fault injection is synthetic; it is not evidence of spontaneous disk corruption on a customer machine.

Replay after trusted full checkout:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_write_receipt_r328.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_write_receipt_r328.py'
python products/desktop/scripts/offline_source_gate.py
```

The existing internal `.github/workflows/desktop-build.yml` already performs standard and `-OO` full source discovery and Windows prepackaging checks, so no weakening/replacement of CI is needed. The **complete private checkout suite, all 22 genuine AES-GCM integration cases, and Windows executable acceptance were NOT executed** in this sprint.

## Release gates and blockers

Previous [R327 workflow run](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42805146698) failed on November 10, 2026, before `source-tests` or `windows-build` recorded any runner steps (`steps=null`). That is an **unconfirmed pre-execution CI infrastructure failure**, not a code-test failure and not proof of hosted test success. Inspect Actions billing/spending/runner eligibility and permissions, or provide a trusted full private checkout plus native Windows 11 x64 test runner.

Next highest-value milestone is full source + zero-skip 22-case genuine AES-GCM integration, six **private** Windows x64 binary builds, executable launch/smoke testing, SHA-256, Defender, keyboard/screen-reader accessibility, premium entitlement access-control validation, independent QD review and founder signoff. All six apps remain **UNRELEASED**; premium executables must never be placed at unrestricted public URLs.
