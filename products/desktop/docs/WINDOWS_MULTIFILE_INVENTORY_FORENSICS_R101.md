# R101 — Windows multi-file inventory diagnosis (source-only, no release)

**Status: DRAFT / RELEASE HOLD.** Parent R100 exact head `114ad40a96c0a4e84b3f65dc1fbb962e3cf67173`, PR #401. No changes to the production branch, binary build inputs, app algorithms, money handling, privacy controls, paid distribution, or independent QD approval.

## Why this sprint

R100 CI #41272202979 passed the complete Linux source suite in normal and optimized `-OO` modes and all six source smokes. Its native Windows runner passed single-file fingerprint tests and scanning the test directory, but **both whole-tree source and test inventory** were blocked. The mandatory R57 source gate therefore refused Windows packaging. The precise cause had not been verified.

## Concrete additions

- `scripts/diagnose_windows_inventory_r101.py`: read-only per-file source- and test-inventory diagnostics, using the **unchanged production `_fingerprint` function as first authority**. Failures are examined independently for a fixed category (regular file, unexpected hardlinks, confinement, length, descriptor identity, read, etc.). Never reclassifies an original failed fingerprint as passing, and never changes gate results.
- `tests/test_windows_inventory_forensics_r101.py`: 21 synthetic tests for source-authority preservation, symlink/hardlink classification, missing/outside/oversized input, bounded metadata bitmasks, privacy-safe counters, invalid labels, and fail-closed semantics.
- `.github/workflows/desktop-build.yml`: run two-mode synthetic tests and source-only probe **before the unchanged R57 Windows gate**; run synthetic tests on Linux too. The probe reports only static category counts with a fixed prefix and releases no file paths, personal data, exceptions, input bytes, or test fixtures.

## Reproduce

```
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_windows_inventory_forensics_r101.py' -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_windows_inventory_forensics_r101.py' -v
PYTHONPATH=products/desktop python products/desktop/scripts/diagnose_windows_inventory_r101.py
PYTHONPATH=products/desktop python products/desktop/scripts/offline_source_gate.py
```

The diagnostic returning process status zero is **NOT proof the inventory is sound**; only the last mandatory command gates packaging. CI may show `FVS_R101_SOURCES:...` and `FVS_R101_TESTS:...` with known counters, no private paths. The `UNKNOWN` category explicitly remains a refusal to infer safe metadata. Full source and Windows packaging status must be checked from the actual Actions run; never infer success from unexecuted committed tests.

## Next action

Inspect GitHub Actions run for R101 exact branch head. If a common Windows-specific descriptor identity or file-link condition is demonstrated, correct it with adversarial regressions **without weakening** symlink, hardlink, same-byte-rewrite, metadata, source path or multi-pass inventory guards. Rerun complete normal/-OO suite, six source smokes and native Windows x64 candidate build/smoke. Check SHA256, AV, accessibility and controlled premium entitlement. Keep all six apps UNRELEASED until independent QD and founder signoff.

## Executed CI observation (first diagnostic iteration)

R101 early CI run [#41274890357](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41274890357) executed the Python synthetic tests on both hosted platforms in normal and `-OO` modes. Both passed. The Windows read-only probe reported **71 source files: 70 pass, 1 descriptor START identity mismatch; 134 tests: 132 pass, 2 START mismatches**, confirming three concrete Windows path-versus-open-file metadata discrepancies. The unchanged R57 Windows source gate continued to fail and packaging was skipped; the Linux full source gate finished green. These numbers include any new probe and test source files (not claims of a binary build).

The next probe now records a *bounded seven-bit identity-field mask* (device, inode, mode, link count, size, mtime, ctime) for these mismatch categories without disclosing filenames, paths, timestamps or file values. **A mismatch remains a failure, not a bypass.** Pending exact-head CI evidence for this follow-on change.

## Verified Windows-specific root cause and guarded implementation

[Hosted Actions #41275007459](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41275007459) established the precise seven-field mismatch on Windows Python 3.12: **START_MASK_64**, meaning `st_ctime_ns` (the Windows creation-time field) alone disagrees between `Path.lstat()` and `os.fstat(open_fd)`, although device, inode, mode, nlink, size and mtime matched. The 71 inventoried sources showed 66 stable + 5 ctime-only differences; 134 tests showed 128 stable + 6 ctime-only differences. Diagnostic R100 still reported both inventories blocked; R57 correctly prevented packaging. Linux normal/-OO full suite and six source smokes passed.

Source fix in `scripts/source_smoke_gate.py` treats the two Windows stat API views as distinct, because their creation-time readings are inconsistent even for a single Git-tracked source file. **Only** the path-versus-descriptor comparison on `os.name == 'nt'` excludes the inconsistent seventh field. Linux still compares all seven. The hash routine still validates full *seven-field* equality of the descriptor **before versus after read**, and independent full *seven-field* equality of the path **before versus after read**, including creation time on both. Cross-view dev/inode/mode/nlink/size/mtime checks remain mandatory, plus single-link, symlink rejection, confinement, bounded byte reads, SHA-256 and the unchanged full-inventory snapshot before/after every test pass and source smoke. It is not a blanket removal of `st_ctime_ns` integrity checks.

Five new cross-view/same-view adversarial regression methods test the Windows ctime discrepancy and strict rejection of other metadata differences, mid-read descriptor ctime tampering and inode swap. They are added to the privacy-safe focused R101 runner in **both** normal and `-OO` modes before the unchanged R57 full source gate.

**Evidence pending:** final exact-head hosted CI must demonstrate full Windows source suite in normal/-OO and all six engine smokes, then actual Windows executables and R9 offline candidate report. No asset may be labeled released until real Windows binary/AV/checksum/GUI/accessibility/premium entitlement and QD/founder validation are complete.
