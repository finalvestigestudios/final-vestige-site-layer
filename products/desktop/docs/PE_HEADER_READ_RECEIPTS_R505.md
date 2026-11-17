# R505 — Exact PE header/section read receipts (DRAFT / QD HARD HOLD)

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Depends on the R504 branch, **never** production `main`.

## Why

The six-app Windows release verifier already checked certificate record seek/read/post-read positions, but the earlier `pe_image_guard._read_at` accepted any stream `seek()` return and arbitrary byte-like receipts. A wrapper could return the requested bytes without advancing the held position, and the DOS/NT/optional/section-table parser would still consume them. This sprint closes that structural inspection gap.

## Change

- `pe_header_receipt_r505.read_exact_at` requires native exact integer start/length boundaries, exact native integer seek receipt, **plain `bytes`** of the requested length, and exact native integer post-read `tell()` receipt.
- `pe_image_guard._read_at` now delegates **every DOS, NT, optional header and section-table read** through that helper, preserving fixed `PEFormatError` messages and excluding private exception chains.
- Ordinary `Exception`-derived stream failures are sanitized; `KeyboardInterrupt` and `SystemExit` are not suppressed.
- The helper does not load/execute code or claim AV, Authenticode or signature trust. The existing same-descriptor SHA-256 check and the R496–R504 certificate guards remain separate.
- No source financial data, money math, audit journal, compliance decisions, WordPress publication, entitlement or download endpoint is modified.

## Test evidence — local (Linux CPython 3.13.5)

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_header_receipt_r505.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_header_receipt_r505.py
python -m py_compile products/desktop/pe_header_receipt_r505.py products/desktop/tests/test_pe_header_receipt_r505.py
```

All **22/22 helper cases passed** in each mode (**44 method executions**). The helper and its test match the committed Git blobs `22c7032f8fb23c7b849234158ba7c1ca78efe88c` and `0b1da5a5ab28d6c29b4a4c9efd9556071981a0b0`. Inert `BytesIO` plus a real unbuffered local file covered good reads, bounds, false/missing seek receipts, false post-read receipts, bytearray/subclass rejection, detached reads, short reads, private seek/read/tell exception redaction, and interrupt propagation.

The **eight** added parser-binding tests also passed twice (**16 method executions**) against a local minimal adapter reproducing the committed `_read_at` wrapper, with test file Git blob `c200146def16f27533745b91b003db954a9a0edc`. **Those are not full real-module or exact-checkout integration proof.** Hosted CI is configured to run both test files against the complete repository in both modes.

Local focused total: **60/60 executions** over 30 distinct tests in normal and optimized mode. No hosted CI or native Windows release test is claimed to pass.

## Remaining hard gates

The previous R503 hosted [Windows build run](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44154483329) and [source evidence run](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44154483569) failed before any steps ran (`steps=null` on four jobs). Cause unresolved; inspect repository/org Actions runner policies, billing and spending limits. Run R505 exact-commit CI after runner restoration.

Then require a full six-engine regression, native Windows x64 packaging and smoke, Defender scans, executable SHA-256/checksum manifests, keyboard accessibility, and verified premium entitlement/download controls. No merge, releases, public premium URLs or production/WordPress deployment until independent QD review and explicit founder authorization.
