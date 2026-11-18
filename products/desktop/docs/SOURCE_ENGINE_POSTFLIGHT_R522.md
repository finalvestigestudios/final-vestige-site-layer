# Final Vestige Labs R522 — shared financial-engine source postflight

**Status: DRAFT / QD HARD HOLD.** This is a source-test evidence improvement,
not proof of a Windows x64 build, app acceptance or release readiness.
Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73)
and is stacked on the R521 draft branch, **not production `main`**.

## Reproduced gap and implementation

R521 verified each manifest-listed test/script before launch and again after
the last command. However, successful tests could rewrite or add a module
under `products/desktop/fvs_suite/` without altering any manifest-listed
test/script file. R521's postflight did not inspect shared app engine modules.

R522 adds `scripts/source_engine_custody_r522.py`. Production `main()`
snapshots the **112 reviewed, flat package `.py` modules** before running
the 416 source commands, using the existing bounded descriptor-verified
SHA-256 source fingerprint helper. After the existing test/script and exact
manifest checks, `execute()` re-enumerates the Python modules and requires
the same deterministic module set and matching digests. A modified, removed
or added source module, invalid module name, symlink, missing core file,
nonregular file or untrusted snapshot produces a generic HOLD with no source
content or private path in the diagnostic. Each file is independently
limited by the existing 1 MiB source-reader bound.

The 112 count and largest source file (32,880 bytes) were inspected through
the exact R521 GitHub package directory listing. They are repository source
inventory facts, not an executed full-tree runtime result. The bound is 256
modules; changing it needs review. This inventory is only the top-level
`fvs_suite/*.py` Python package, **not** a checksum of imports, resources,
wheel files, build inputs or the entire checkout.

## Evidence and limits

- 15 new committed regression methods appended to the already pinned
  `test_source_evidence_runner_r509.py` (no manifest edit).
- Focused local isolated Linux helper harness: **12/12 standard CPython**
  and **12/12 optimized CPython `-OO`**, zero skips, plus `py_compile` PASS.
  The helper under test is text-identical to the proposed R522 implementation,
  using a local test stub for the existing descriptor fingerprint dependency;
  this **does not** verify the full committed 15 integration methods.
- The 12 cases cover unchanged, mutation, addition, removal, bad filenames,
  symlinks, forged digest, missing core file, directory substitution,
  relative checkout, empty snapshot and deterministic source order.
- The committed 15 tests additionally cover `execute()` HOLD/PASS wiring,
  manifest-free refusal and `main()` passing the real source receipt.
- Preserves the 416-command, 43,737-byte immutable manifest, the R521 test
  source and manifest controls, no-silent-compliance rule and existing
  QD/founder approval gates. A restored-before-observation modification
  remains outside this non-atomic evidence boundary.

## Required release gates

The exact-head Linux and Windows CI jobs must actually start, pass the full
pinned normal and `-OO` source matrix, then produce native six-app Windows
x64 artifacts and actual executable smoke/Defender/accessibility/checksum
and entitlement evidence. GitHub Actions has previously failed **before any
job steps**, tracked by [infrastructure issue #75](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/75).
Ask the repository/account administrator to review Actions billing/spend
limits, policy and runner eligibility; rerun the exact R522 commit after
fixing the underlying startup restriction.

No Windows executable has been validated or published by R522. No WordPress
publication, premium public link or license entitlement changes are
authorized. Local financial data stays local; exact Decimal money math,
auditable source rows, human compliance decisions and the four-free/two-Pro
catalog distinctions are unchanged. No merge or production deployment
without independent QD review and explicit founder approval.
