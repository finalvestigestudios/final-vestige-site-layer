# Labs R320 — Independent, read-only premium restored-bundle consistency check

**Issue #73; draft/QD + founder HARD HOLD.** Parent is R319 draft PR #1832 at `1e3055ffaa4c1eed613ab2888e349ea7a0358ad9`; no main, site, WordPress, entitlements, release or customer-data change.

## Value

GrantAudit Studio Pro and ProcureGuard Studio Pro write a plaintext evidence bundle after an authenticated AES-GCM restore. The existing R311 checks execute *inside* restoration; there was no operator-run, read-only consistency recheck of an already-restored bundle. R320 adds `scripts/verify_restored_bundle_r320.py` as a local, standalone CLI and importable function.

On a private existing restored folder, the tool checks the exact product-specific manifest schema and expected 2- or 3-file inventory; valid source filename metadata; UTC-aware timestamp; product identity (`grants`/`procurement`); strict SHA-256 digests of report and optional journal; hardlinks, symlinks, unexpected files, path substitutions, filesystem identity and observable mid-read changes; max 64 MiB report, 16 MiB journal and 64 KiB manifest; and a **second full read** of all files. The tool never modifies files, invokes a network service or processes real customer data during CI. CLI output has no file paths or financial values. All malformed inputs yield a fixed, private-path-free HOLD without chained exceptions.

Usage on an **owner-controlled offline workstation**, after a genuine premium restore:

```bash
python -I products/desktop/scripts/verify_restored_bundle_r320.py <PRIVATE_RESTORED_FOLDER>
```

Exit `0`: **internally consistent at observation time**, NOT authenticated or approved. Exit `1`: HOLD. Python callers receive a report with the two local SHA-256 values and explicit `source_authenticated: false`, `compliance_approved: false`, `release_authorized: false`, `review_required: true`.

**Security limit:** A plaintext manifest is NOT a cryptographic signature. Someone able to rewrite the manifest and every file can forge a consistent package. This is also not an atomic snapshot against a privileged concurrent writer, a substitute for authenticating the original AES-GCM archive or paid entitlement, a ledger compliance decision, or a release gate. Always use the authenticated restore and independent human review.

## Exact local evidence — Nov 9, 2026 PST

Linux CPython **3.13.5**, real temporary filesystem operations with synthetic report and journal, no encryption, external services, source checkout or Windows executable:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_restored_bundle_inspector_r320.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_restored_bundle_inspector_r320.py'
python -m py_compile products/desktop/scripts/verify_restored_bundle_r320.py products/desktop/tests/test_restored_bundle_inspector_r320.py
```

**22/22 PASS normal + 22/22 PASS optimized = 44 focused executions; compile PASS.** Valid grant without journal, procurement with journal, unchanged files and real isolated CLI paths were tested; adversarial cases cover digest mismatches, missing/extra files, duplicates/nonfinite manifest JSON, link/identity hazards, mid-check alteration, invalid product/metadata and private exception sanitization. Symlink assertions use a deterministic `lstat` fallback when Windows symlink privileges are unavailable; no test skips are required.

The executed test-file Git blob is `24e776f4f2b5c5eeadf98f29cc9acc9cd5bc1b3f`; tool Git blob is `b6297deba7fcdff30a8379314c413f54b0cf42ee` (verify these correspond to the final PR).

`.github/workflows/desktop-build.yml` runs these 22 methods **both normal and optimized on both Ubuntu source and Windows packaging jobs**, before the existing source/Windows candidate gates. This is code placement, not a claim of hosted execution.

## Blockers and next action

Current R319 Actions [#42746518585](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42746518585) completed failed before either runner recorded a step. No hosted CI, full private checkout, 22 genuine AES-GCM integration cases, Windows 11 x64 binaries, Defender, keyboard/visual QA or protected premium delivery are verified. Restore Actions billing/runner eligibility and re-run the draft PR; or use a trusted complete private checkout with `cryptography` to run the full offline source/crypto gates, then private Windows candidate builds and independent QD review. No files are published; all six applications remain **UNRELEASED** until QD + founder approval.
