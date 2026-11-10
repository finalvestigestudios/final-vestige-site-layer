# R327 — Reject incomplete or inconsistent premium journal reads

**Status: DRAFT / QD and founder HARD HOLD; issue #73. NO RELEASE.**

## Defect and impact

The shared `fvs_suite.journal_io.read_regular_bytes` reader in **GrantAudit Studio Pro** and **ProcureGuard Studio Pro** verified its pinned file descriptor, file type, length bound, path identity and pre/post filesystem metadata but did not require the bytes returned by `stream.read(limit + 1)` to equal the observed ordinary-file size. A shortened read (or extra bytes below the configured maximum) could be returned as complete even when `fstat` and `lstat` remained unchanged. For a premium review journal, interpreting an incomplete read as a complete set of records risks an incorrect audit-history interpretation. This is a consistency gap, **not** evidence that ordinary Windows or POSIX disk reads spontaneously truncate or that any customer data was affected.

The R327 fix adds an **exact byte-count equality** with the pinned descriptor's pre-read `st_size`, in addition to the existing upper bound and metadata checks. Empty and exact-sized files remain valid. On disagreement, reading HOLDs with the existing fixed, path-free ValueError. The caller must not proceed to a compliance decision. Existing no-follow, hardlink/alias, FIFO-swap, identity and read/append protections are preserved. No change to Decimal money rules, journal hash-chain algorithms, financial data, premium credentials, site, or downloadable artifacts.

## Reproducible, focused local evidence (2026-11-10)

Test scope: Linux Python **3.13.5**, synthetic temporary files and injected file-stream outcomes. The production `journal_io.py` source was locally copied from the **exact GitHub R326 blob `8b88ebd90877c8e69599fe3bfd1d1cae25b1c22e`** and the updated local file matches the committed R327 Git blob `75eab0c8a2ea352e8d15469a077b544bef2c79b8`. The new regression module matches Git blob `c1fff46f594c2e8822ab454a505bbf0ef5d71ecb` byte-for-byte. The final local rerun used the **exact GitHub `csv_snapshot.py` dependency blob `a695123f1adc133dfac2cc38726540fe373618fe`**, byte-for-byte verified with `git hash-object` (no stub), as well as the exact committed source and regression blobs. This remains a **focused isolated source test, not a complete repository checkout**.

* **Before patch:** 13 methods executed; **5 expected FAIL** (zero-byte, one-byte, half-length, one-byte-short, and extra-byte responses returned instead of rejecting), 8 PASS. Underlying file metadata was unchanged in the injected scenarios.
* **After patch:** **13/13 PASS** under normal Python, **13/13 PASS** under Python `-OO`; zero skips; 26 passing focused method executions. Python `compileall` PASS.
* Includes successful ordinary and empty file reads, exact byte limit, size-bound rejection, unchanged append and callback, and path-free permission-error redaction.
* No real premium customer evidence, untrusted input, network service, installer, Windows host, AES-GCM integration, release or entitlement test was exercised.

Replay on **trusted complete checkout**:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_exact_length_r327.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_exact_length_r327.py'
python products/desktop/scripts/offline_source_gate.py
```

The existing Ubuntu/Windows `desktop-build.yml` workflow already runs full normal / optimized source discovery and six source smokes **before** Windows packaging, so this test is automatically included without changing CI policy. Source-only success cannot replace real Windows EXE acceptance.

## Release and QD hold

R327 is a stacked draft branch based solely on draft R326, not `main`. Production, WordPress, downloads, premium licensing and automated compliance decisions are untouched. The original source files remain read-only for the application. The prior work's POSIX FIFO race defenses and independent external SHA-256 evidence witness remain in force. All six products remain **UNRELEASED**.

**Next highest-impact action:** The repository owner must resolve GitHub Actions' pre-run scheduling/billing/runner failure (or provide a trusted full private checkout plus a native Windows 11 x64 host). Then execute the complete desktop test suite, the **22 genuine mandatory AES-GCM integration cases**, all six private Windows EXE builds and smokes, Defender scan, checksum, screen-reader/keyboard/accessibility review, premium access-control verification, independent QD and founder release approval. Do not publish any binary before these gates.
