# R484 — Six-app pre-publication staging ancestry custody (DRAFT / QD HOLD)

**Issue:** [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73)
**Parent:** R483 draft [#2797](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2797), exact parent `5be10494614e30d6a01c10950b8af914197aa5b1`.
**Scope:** Only internal six-EXE checksum inventory. No production main, WordPress, public downloads, premium issuance or release authorization.

## Concrete staging defect and fix

The prior `build_inventory._membership` verified a candidate folder with `root.lstat()` and six ordinary file entries, but did **not** inspect the lexical ancestry of the folder. A real directory reached through an intermediate symlink passes this check. The builder could therefore create, hardlink/publish and leave `SHA256SUMS.txt` in an unsafe alias before the later release-gate/candidate directory ancestry check rejected it. Similarly, Windows reparse/junction attributes were checked by the downstream candidate reader, not before checksum staging.

R484 adds `inventory_staging_ancestry_r484.preflight_inventory_stage` to the actual `build_inventory.build_inventory` path:
1. **Before `mkstemp`**, check the complete lexical ancestor chain without resolving links, the root and exact six payload names, six distinct ordinary nonempty non-reparse files, safe size bounds and no surplus payload.
2. **After writing/flushing the private staged checksum file, before `os.link`**, recheck original parent identity, current stage filename/inode type and exact seven-entry directory membership. Changed ancestry, reparse root, reparse file, unapproved stage name or private stage replacement fails closed.
3. Return a fixed private-path-free error; do not include customer filenames, path details or original exceptions. Never delete input candidates. On rejection before publication, the temporary stage is cleaned up by the inherited writer.

This is defense-in-depth against unsafe persistent parents/links and observed changes, **not a guarantee against all concurrent filesystem race conditions**, executable authenticity, code signing, malware clearance, premium entitlement, or QD approval.

## Local test evidence (2026-11-16)

- Verified new standalone helper bytes with Git blob SHA **`2b3236e9b7c3a8de50019b957cc60ad0ba9c177b`** (same as committed GitHub file).
- Linux Python normal `-W error`: **17/17 PASS** actual standalone helper tests; 5 full repository integration methods **SKIPPED** because the private repository and actual `build_inventory` imports are not mounted in the isolated local environment.
- Optimized `-OO -W error`: **17/17 PASS**, same 5 integration skips.
- Focused negative control: with six synthetic files under a real directory accessed via an intermediate symlink, the legacy membership condition **accepted** the folder; R484 preflight **rejected** it before writing any manifest.
- `py_compile` PASS locally. Tests use synthetic short bytes named `.exe`; **no executable was built, launched, published or scanned**.
- The newly committed native test module contains **22 methods** (17 preflight + 5 actual `build_inventory` integrations), wired to `.github/workflows/desktop-source-evidence-r385.yml` in both standard and optimized mode on **Ubuntu and Windows**. These **have not executed against the complete repository** pending GitHub Actions runner restoration.
- The full six-app engine matrix, real Windows x64 packaging, native smoke/accessibility, Defender, signatures, SHA256 candidate attestation and premium access checks remain UNVERIFIED.

## Release hard hold and smallest unblock

Recent R483 workflow runs [source #43975055835](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43975055835) and [Windows internal #43975055745](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43975055745) each failed before any job step (`steps=null` across four jobs). Root cause is not confirmed.

**Next step:** Repository owner inspects the GitHub Actions check-run annotations, billing/usage status, and runner eligibility; restores job execution. Then run the R484 22-method native tests in both modes on Windows and Ubuntu, all inherited six-app checks and full pre-release Windows/custody pipeline. Require independent QD review and explicit founder approval before any merge or release. All four free and both premium apps remain **UNRELEASED**.
