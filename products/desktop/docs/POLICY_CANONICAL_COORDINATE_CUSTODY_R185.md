# R185 — Policy Delta canonical source-coordinate custody

**DRAFT / HARD RELEASE HOLD; tracks #73.** Branch stacked on R184 draft PR #935 at `2d14f2a`, not production `main`.

## Reproduced issue and correction

The Policy Delta Desk NFC-only supplemental navigator accepted direct-Python-API caller-owned line coordinates without verification. It could cite duplicate/backward-moving physical source rows across separate hunks or process malicious tuple/dict/list/text subclasses. Even an exact native dict could contain a custom key whose hash collided with `removed_sources` and whose `__eq__` executed during a benign string lookup. **Before the fix, that synthetic key reproduced an unexpected RuntimeError** (not a compliance conclusion).

R185 validates **every** native list/dict/tuple/str/int value, exact dictionary key type, physical source coordinate 1–50,000, strictly ascending line positions within and across hunks, and keys on both before/after sides, **before** producing any supplemental NFC-only citation. On invalid provenance it returns no canonical navigation, never partial potentially misleading citations. Valid `deleted`/other text metadata remains compatible. A navigation-only 4096-character source-line bound avoids processing oversized candidate pairs; those lines still contribute to position validation. The primary exact-byte diff and source SHA-256, original files and legal/compliance human-review requirement are unchanged; long lines remain available in the base comparison.

Older R178 and R179 synthetic fixtures had intentionally out-of-order row storage inconsistent with any real unified-diff stream. Fixed **three** fixture row lists so they use genuine ascending physical lines and retain their original ordering/determinism assertions; no engine safety contract weakened.

## Exact code and tests

- [NFC review source](../fvs_suite/policy_canonical.py), Git blob `1e1b047bb3b8a2bb8b77652892e4753b8e2b72a4`.
- [32 synthetic regression methods](../tests/test_policy_canonical_custody_r185.py), Git blob `aed139b1a0ace861915bbb3e4a53a2318ab8b578`.
- [Exact-inventory no-skip gate](../scripts/safe_unittest_r185.py), Git blob `ca6d28d64e5254dcbb1ba61b3698bcc24dce2eb7`.
- Inherited R178 and R179 tests corrected only for impossible physical row ordering.
- [Ubuntu and Windows CI](../../../.github/workflows/desktop-build.yml) runs the R185 32-method gate both normally and with `-OO`; pre-existing suites remain required.

## Evidence from executed local Linux Python 3.13.5

Using exactly Git-blob-matched R185 source, 32-method tests and strict runner in an isolated Python package:

| Check | Observed |
| --- | --- |
| `python scripts/safe_unittest_r185.py` | **32/32 PASS**, 0 skipped |
| `python -OO scripts/safe_unittest_r185.py` | **32/32 PASS**, 0 skipped |
| Combined exact-method executions | **64/64 PASS** |
| `python -m py_compile` source + tests | PASS |
| Reproduced original hostile-key lookup | Raised RuntimeError before fix; now gated by regression |
| Inherited R178/R179 suite and 14 real-file integration tests | **Not executed** in this isolated environment |
| Full Ubuntu/Windows CI, Windows x64 builds | **Not verified** |

Local Python execution **does not** constitute an actual Windows executable build, Windows accessibility inspection, complete repository acceptance, antivirus clearance, QD signoff, or permission to publish.

## Outstanding release gates and next step

GitHub Actions on predecessor R184 [#41825624737](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41825624737) failed before runner allocation (both jobs zero steps); R185 must be checked independently. Owner should inspect the exact workflow error banner and Actions billing/usage permissions, then enable hosted runner execution. Rerun this unchanged R185 branch against the complete inherited suite, including the 14 Policy Delta real-file integration cases, before private Windows x64 smoke builds.

**All six desktop applications UNRELEASED.** No public download URL, no CMS/prod changes, and no unrestricted premium distribution. Physical Win11 accessibility, Defender/EDR assessment, signing, entitlement-gated premium delivery, independent QD approval and explicit founder authorization remain HARD HOLD.
