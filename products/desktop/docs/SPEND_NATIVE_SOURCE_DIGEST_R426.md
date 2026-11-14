# R426 — SpendMap source SHA-256 must be native before financial evidence hashing

**Status:** Draft-only, six-app release on hard hold. This is local-first direct-API input hardening, not evidence of customer exploitation, proof of CSV-source authenticity, or release approval.

## Reproduced boundary

`spend_analysis.summarize_spend(source_sha256=...)` accepted any `isinstance(x, str)` matching the lowercase SHA-256 text pattern. A `str` subclass can pass the regex check yet override `.encode()` and feed different bytes into `_vendor_month_line_digest` than its visible `source_sha256`. That could create a misleading vendor/month evidence fingerprint for a direct Python API caller. The regular CSV intake supplies built-in strings; the weakness is at the reusable direct-call interface. A normal hash is **not** a digital signature.

## Implementation

- `spend_source_digest_r426.require_native_spend_source_sha256`: require exact native `str`, exact 64 ASCII lowercase hexadecimal characters, with fixed private-free failure text. No coercion, normalization, or suspicious callback hooks.
- `spend_analysis.summarize_spend` validates the SHA **before** running source parsing/formatting callbacks or constructing any reports.
- `_vendor_month_line_digest` independently enforces the same boundary, preventing future internal callers from reintroducing an overridden `encode()` hook.
- No changes to source files, report fields, financial Decimal calculations, vendor matching rules, spike thresholds, UI approvals, offline behavior, license entitlements or publication.

## Tests and limitations

- `test_spend_source_digest_r426.py`: 18 pure helper regression methods on synthetic values, including hostile string subclass hooks; run normal and `python -OO -W error`.
- `test_spend_source_digest_integration_r426.py`: 8 tests against actual `summarize_spend` and group fingerprint helper, valid and forged digest, provenance determinism and amount invariance. Must run on a complete repository checkout; do **not** claim these passed on an isolated helper-only filesystem.
- CI workflow additionally invokes inherited `test_spend_source_digest_r61.py`, `test_spend_vendor_month_r152.py`, and `test_spend_engine_integration_r59.py` in normal and optimized modes on Ubuntu and Windows.
- Local isolated validation on Linux: new helper exact source and pure suite **18/18 normal + 18/18 optimized** PASS, syntax compilation PASS. Full source, six engines and Windows x64 builds are not verified until actual CI runs.

## Pending release gates

The upstream GitHub Actions workflows previously failed before assigning runners. Investigate account Actions eligibility/limits/billing or policy, then execute complete committed tests on both OSes. Verify actual six Windows x64 builds, Defender scanning, keyboard and screen-reader access, reproducible hashes, premium license enforcement, protected premium download paths, QD review and founder approval. Never distribute binaries just because source regressions pass.
