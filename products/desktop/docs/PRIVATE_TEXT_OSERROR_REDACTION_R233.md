# R233 — private text report I/O error-custody

**Status:** DRAFT / independent QD + founder HARD HOLD. Issue #73. Stacked exclusively on R232 draft PR #1250; **no main/WordPress edits and no downloads published**.

## Problem and working remedy

`publish_text` is shared by Policy Delta Desk's local change reports and GrantAudit Studio Pro's private evidence manifests. R232 removed customer names from temporary file prefixes, but native `PermissionError`, `OSError`, and late `FileExistsError` still could expose absolute destination folders, client identifiers and arbitrary OS-provided error text through `str(exc)` and ordinary tracebacks. This includes failed `lstat`, staging creation, `fdopen`, `fsync`, hard-link/rename publication and cleanup.

R233 funnels native OS exceptions through `_private_io_failure` before they reach a GUI/status layer. It preserves a valid integer `errno` (so ENOSPC, EIO, EACCES and corresponding built-in permission classification remain observable), uses EIO for unclassified failures, removes path-bearing `filename`/`filename2` and OS error strings, and maps destination collisions to the existing fixed `FileExistsError` text. Ordinary Python tracebacks suppress the original exception chain. Invalid text/schema errors continue to be rejected before staging.

**Not a blanket guarantee against deliberate exception introspection:** Python still allows privileged code to inspect an exception's `__context__`; software must not log exception objects recursively or log source paths independently.

No network access/telemetry, source-file edits, financial Decimal operations, audit calculation, premium entitlement logic, or human compliance authorization changes. The 64 MiB UTF-8 ceiling, fsync-before-publish, staged file cleanup, non-overwrite, and exact LF/CRLF/no-BOM bytes remain intact. This is not a multi-file or power-loss transaction.

## Measured local test evidence

- Source baseline: R232 private publisher Git blob `30427bd47fdc734c92580a18dbc7cc54df041287`.
- R233 patched publisher Git blob `d0a3cd5238c55606418e861cb708827a6ae1d376`.
- R233 12-case test suite Git blob `f34025755a4899792d2d9dcab150b7d8e25dc18b`.
- Before fix: newly added tests **7/9 failed**, reproducing pathname and OS error-text leaks on Linux. The final suite was expanded to 12 cases.
- After fix: `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_atomic_text_io_privacy_r233.py'`: **12/12 PASS**. Same with `python -OO -W error`: **12/12 PASS**; **24 local methods executed** (Linux CPython with real temporary files and synthetic injected I/O faults). `compileall` passed.
- Tests cover original-file collision, dangling links, preflight permission fault, staging disk-full fault, descriptor closure, fsync disk faults, late publish collisions, unclassified errno fallback, traceback redaction, UTF-8 byte identity. No secrets are used.
- Existing R28/R231/R232 suites and full six-app integration **were not executed in this local checkout**. No Windows CI or real Windows x64 executable acceptance has occurred.

## CI and release constraints

A mandatory R233 prepackaging step has been added to both Ubuntu and Windows build jobs, normal and `-OO` Python, **not asserted executed**. Hosted GitHub Actions has repeatedly produced `steps:null` before any tests on both jobs, which cannot be counted as pass or fail of this change. Owner needs to inspect billing/runner allocation/workflow policy and rerun the **unchanged exact PR commit**.

**Next highest-impact gate:** restore hosted runners, run the entire inherited six-app source suite, build Windows x64 private candidates, and complete SHA-256, malware/Defender, Windows 11 usability/DPI/accessibility, and protected premium distribution verification. Independent QD and founder release approval are mandatory. All six apps remain **UNRELEASED**.
