# R231 — Bounded local TXT evidence publication (issue #73)

**Status: source-level engineering only. Draft / QD review / founder release HOLD. No Windows executable or public download.**

## Fault and scope

The shared `fvs_suite.atomic_text.publish_text` is the final local publication boundary for Policy Delta Desk change reports and GrantAudit Studio Pro evidence manifests. Unlike the CSV publisher, it previously accepted unbounded text, embedded NUL bytes, and `str` subclasses, and let malformed Unicode raise a `UnicodeEncodeError` containing caller-controlled evidence. The staging cleanup prevented partially published reports but did not bound disk exposure or provide a fixed private error.

R231 validates **before creating any staging file**: exact built-in `str` only, no NUL, no lone UTF-16 surrogate code points, and at most **64 MiB of serialized UTF-8 bytes**, not code points. Exact existing newline/BOM behavior remains unchanged. The implementation writes prevalidated bytes to a private same-directory staging file, `fsync`s, and retains nonreplacing POSIX hard-link / Windows rename publication. The whole byte buffer is bounded by the validated size; no network upload or telemetry is introduced. A batch above 64 MiB must be split and reviewed, never silently truncated.

This boundary changes neither Decimal money computation nor provenance rules, grant/PO approval, premium licensing, or human review. It is *not* a multi-report transaction, an encrypted-at-rest store, tamper-proof signing, or Windows certification.

## Test evidence — 2026-11-06

Reconstructed the exact R230 `atomic_text.py` Git blob (`05513accbc7f76ddc9481b8644402aacbd7d8cec`) locally. Before patching, the new R231 test set showed **3 assertion failures and 8 errors in 16 tests**, proving missing NUL/str-subclass/Unicode and byte-budget protections (other tests passed).

After patching, the production module Git blob was checked against the locally executed source (`f526fb4ac2ac37b858f7fe147284d54a8ee869ba`); the committed 16-test file likewise matched the tested file (`8ebe2bc40b112577b129df13f6bd06fe043802c2`). **16/16 new tests PASS**, normal Python and `-OO`, including exact UTF-8 boundaries, multibyte expansion, invalid content, subclass hooks, collision/symlink non-overwrite, failed `fsync` cleanup and byte identity. **12/12 inherited R28 equivalent tests PASS** in both modes with the surrogate exception expectation updated to a fixed-text `ValueError`. **28/28 per mode = 56/56 local test-method executions; 0 skips; Python compilation PASS.** Linux CPython 3.13, synthetic data, temporary directories. The inherited R28 local file was reconstructed from repository text, not byte-identical; its updated committed Git version awaits hosted execution. No whole-engine or native Windows tests are claimed.

Both Ubuntu and Windows prepackaging workflows now explicitly run the 16 new and 12 inherited methods in normal and `-OO` modes; Windows commands stop on nonzero exits. **These gates are configured, NOT yet hosted-passing.**

## Release holds and next step

GitHub Actions previously failed before executing any job steps; inspect the new commit's workflow runs. The owner must restore Actions job scheduling (billing/usage, permissions, runner provisioning, pre-run banner), then rerun this unchanged R231 SHA. Run the *entire inherited suite* and native Windows 11 x64 report and privacy/permissions tests, build six candidates privately, verify PE/Defender/EDR/SHA256 and accessibility, keep Pro binaries access-controlled, and obtain independent QD plus founder authorization before any merge or publication.
