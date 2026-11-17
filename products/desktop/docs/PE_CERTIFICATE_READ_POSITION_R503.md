# R503 — exact PE certificate post-read position receipts

**Status:** DRAFT; QD hard hold; not a Windows distribution approval.

## Scope and observed problem

The R502 certificate preflight checked the native return from `seek()` and
native byte length from `read()`, but did not verify that a purportedly
successful read actually moved its descriptor position. An injected stream
could report plausible bytes while leaving its position unchanged, or return
a forged post-read offset. R503 makes each of the three bounded certificate
reads (8-byte header, 1-byte final tail, 0–7-byte outer padding) require a
native `int` from `tell()` equal to `offset + size`. Native `FileIO`
and `BytesIO` remain accepted. Ordinary errors fail with the fixed,
unchained `PECertificateError`; KeyboardInterrupt continues to propagate.

The improvement applies to the shared *preflight* used for all six Windows
x64 release candidates: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite,
Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro. It does
not change their CSV calculations, premium rights, inputs or compliance
decisions.

## Source and independently executed local evidence

- Updated module: `products/desktop/pe_certificate_guard_r496.py`,
  Git blob `25addf8939de4adea4c73cb1eae7fcf513b058ac`.
- New tests: `products/desktop/tests/test_pe_certificate_read_position_r503.py`,
  Git blob `41c17a7346c9fe1b9cea91718bf4d81cb4e57063`.
- Local Linux CPython focused tests using *exact identical Git blob bytes*:
  14/14 PASS with `-B -W error` and 14/14 PASS with
  `-OO -B -W error`; 28 executions total; `py_compile` PASS.
- Negative control using a behavior-equivalent R502 read helper, rather than
  an exact R502 source blob: 11 expected failures / 14 tests. This verifies
  that the new suite discriminates the missing post-read position check.
- New test includes real unbuffered tempfile reads and synthetic malformed
  receipts. It does not execute real EXEs or inspect authentic signatures.
- The existing independent source and internal Windows-build CI workflows
  each schedule the new suite in both Python modes; successful CI is **not**
  asserted until GitHub executes the jobs.

Run locally from the repository root:

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_read_position_r503.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_read_position_r503.py
```

## Release holds

This is structural file-shape checking, **not** Microsoft WinVerifyTrust,
Authenticode signature validity, malware scanning or binary identity proof
without the higher-level SHA-256 check. Reading the position is also not a
lock against concurrent modification. No Windows binary was built or
published; no premium entitlement flow was exercised. Full inherited tests,
Windows x64 packaging, smoke tests, Defender, keyboard/screen reader
accessibility, checksum verification, premium access controls, independent
QD review and explicit founder approval remain mandatory.

**Next highest-impact action:** restore GitHub Actions job execution (check
Actions billing, spending cap, runner eligibility and policies), then run
the inherited six-app source and Windows packaging matrix on this exact
commit. Do not merge the stacked drafts to `main` or distribute files
while QD is on hold.
