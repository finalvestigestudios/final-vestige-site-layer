# R232 — Private TXT evidence staging and descriptor custody

**Scope:** issue #73, `products/desktop/fvs_suite/atomic_text.py`. Draft engineering change, **QD/founder HARD HOLD**; no production merge, site publication, binaries, or download links.

## Functional problem fixed
Policy Delta Desk's change reports and GrantAudit Studio Pro's evidence manifests share `publish_text`. Previously:
1. A destination that already existed would still create and fsync an unpublished temporary copy (up to the existing 64 MiB UTF-8 budget) before exclusive publication rejected the collision. This wasted disk I/O and opened an avoidable transient file.
2. The staging prefix embedded the report's file stem, potentially exposing customer/account names as temporary directory-entry metadata.
3. If `os.fdopen` failed before acquiring ownership of the raw `mkstemp` descriptor (including interruption), the `finally` removed the pathname but left the descriptor open.

R232 first uses `lstat` to reject occupied destination names, including **dangling symlinks** and directories, with a generic `FileExistsError` message. This is an **optimization and privacy defense**, not the overwrite guard: the existing POSIX exclusive `link` and Windows nonreplacing `rename` remain mandatory to reject races after `lstat`. Unpublished staging names now use a constant `.fvs-text-` prefix independent of customer names. An explicit `fdopen` failure handler closes the raw descriptor even on `BaseException`, without suppressing the original failure; the existing outer cleanup removes the temporary pathname.

The 64 MiB **actual UTF-8 byte** cap, rejection of NUL/surrogates and custom string types, precise LF/CRLF/BOM behavior, `fsync`, POSIX 0600 staging permissions, no replacement, and local-only publication remain unchanged. No source-file edits, network calls, telemetry, financial Decimal changes, automated compliance approvals, or premium entitlement alterations.

## Verification executed (2026-11-06, Linux CPython 3.13.5)
Locally reconstructed all **three Python files byte-identically** to Git object contents before running tests:
- Updated publisher: Git blob `30427bd47fdc734c92580a18dbc7cc54df041287`.
- Newly committed 15-method R232 real-file suite: Git blob `ce5de90a39dbab3109451178094fff0ee705a7cf`.
- Inherited R28 (12 methods): Git blob `30f8c2dc63760b9ec16150c5460b5a93176bbea6`.
- Inherited R231 (16 methods): Git blob `8ebe2bc40b112577b129df13f6bd06fe043802c2`.

**Before patch:** the 15 new tests against the exact R231 publisher produced **10 failures**, demonstrating the prior collision/staging, filename-leak, and raw-FD-leak behavior. **After patch:** `PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_atomic_text*.py'` passed **43/43** (15+12+16), with the same **43/43** under `python -OO -W error`; **86 method executions, zero skips**, `compileall` PASS. All evidence was synthetic and offline. The R232 tests create actual temporary files and use real OS descriptors; the collision race is simulated deterministically. On Windows symlink tests can skip where unprivileged link creation is disabled; do not call native Windows acceptance complete.

Both Ubuntu and Windows workflow jobs now explicitly register the 15-method R232 tests in normal and optimized Python **before** candidate packaging, and retain full suite gates. These workflow steps are configured, **not claimed executed** while hosted Actions jobs fail before steps.

## Release and remaining work
- This is **not** full six-engine integration, Windows 11 x64 GUI/DPI/NVDA testing, PE certification, malware scan, code signing, evidence signing, encrypted-at-rest proof, or a cross-file transaction.
- GitHub Actions has repeatedly reported failed Ubuntu/Windows jobs with `steps:null`. Inspect the new run and restore scheduling via GitHub owner billing/usage, workflow policies, and runner provisioning. Rerun the **unchanged exact commit**.
- Next highest impact: execute entire inherited six-app source suite against the checkout and native Windows build/smoke/Defender/SHA-256 accessibility/PE tests; keep both Pro downloads access-controlled. Require independent QD review and founder release approval.

**Release status:** all six standalone Windows x64 applications **UNRELEASED**.