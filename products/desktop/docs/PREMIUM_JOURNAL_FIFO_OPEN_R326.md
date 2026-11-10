# R326 — Nonblocking premium review journal read AND append

**Status: DRAFT / QD + founder HARD HOLD; issue #73. No release.**

## Actual defect and boundary
`fvs_suite/journal_io.py` uses a pre-open `lstat` and a later `os.open` for both `read_regular_bytes` and `append_verified_event`. Although it rejects a FIFO already present at preflight, a concurrent, noncooperating local writer can exchange the checked regular file for a FIFO *between* those calls. A POSIX `O_RDONLY` FIFO open (no writer) or `O_WRONLY|O_APPEND` FIFO open (no reader) can block indefinitely **before** the existing descriptor-identity, regular-file and pathname checks run. R325 fixed the separate restored-bundle inspector; this is the shared premium journal I/O path used by the two Pro apps.

## Engineering change
The shared `_flags(base)` now includes `getattr(os, "O_NONBLOCK", 0)` alongside the original `O_BINARY`, `O_NOFOLLOW` and `O_CLOEXEC` options. POSIX regular files retain ordinary read/append semantics; a raced FIFO read returns a descriptor that fails existing regular-file checks, while a raced FIFO write with no reader fails promptly (a reader-present FIFO still fails descriptor checks). No privileged filesystem-adversary guarantees; no locking claim. Windows falls back when `O_NONBLOCK` is unavailable and requires native acceptance.

Existing protections remain unchanged: descriptor identity and stat consistency, links/aliases rejection, bounds, verified append callback before writing, fsync/post-write custody, no implicit rollback of ambiguous output, and deliberate privacy-safe OSError translation. No Decimal, financial classification, human-review, encryption, license or network changes.

## Regression proof
New `products/desktop/tests/test_journal_fifo_open_r326.py`: **11 synthetic methods**, including valid read, existing/new append, reject-before-write callback, real `os.open` flag witness, preexisting FIFO refusal, and **two killable 4-second child-process race reproducers** (read and append), with no private path in an accepted HOLD.

Local Linux Python source proof: pre-patch `journal_io.py` is byte-for-byte Git blob `17f8fa651098cbe641d88ae88b8f4e43100bf811`; patched source Git blob `8b88ebd90877c8e69599fe3bfd1d1cae25b1c22e`; test Git blob `4308cc88dcae2a54c478c92beb0b099d5d1af24b`. The local test harness also used the **exact Git blob** `a695123f1adc133dfac2cc38726540fe373618fe` for `csv_snapshot.py` (the only `journal_io` import dependency). Thus the focused test exercised the exact committed production source and dependency, but **was not a full private repository checkout**.

- Before patch: **11 methods executed, 5 failures + 2 errors**, including **both** read/write POSIX FIFO-swap subprocesses timing out after four seconds. The two subprocesses are killable, not permanent CI hangs.
- After patch: **11/11 normal PASS**, **11/11 Python `-OO` PASS**, zero skips on local Linux; all test outcomes use synthetic temporary files.
- No actual premium AES-GCM end-to-end suite, hosted CI or physical Windows 11 x64 binaries were exercised during this sprint.

Re-run on the complete checkout before QD review:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_fifo_open_r326.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_fifo_open_r326.py'
python products/desktop/scripts/offline_source_gate.py
```

The existing workflow's **full source gate** runs source regressions in normal and `-OO` modes for both Ubuntu and Windows before any Windows packaging. New test is automatically discovered; no release-gate weakening or workflow rewrite needed. The hosted Actions blocker (jobs fail before execution) still prevents trusted combined-run evidence.

## Safety and next action
All six apps remain **UNRELEASED**. Do not merge to production, publish binaries, advertise unverified download URLs or give public access to premium artifacts. Require genuine 22-case AES-GCM integration, all normal/optimized desktop source regression suites, real private Windows 11 x64 six-exe build and launch, SHA-256/Defender/accessibility and entitlement validation, then independent QD and founder authorization.

**Highest-impact owner action:** restore GitHub Actions billing/spending and runner eligibility (or provide a trusted full private checkout and Windows 11 x64 validation host), then execute the full gated source/AES and Windows acceptance suites. Keep this PR stacked and draft pending that evidence.
