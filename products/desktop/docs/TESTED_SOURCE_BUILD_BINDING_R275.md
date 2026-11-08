# R275 — Bind private Windows candidates to the bytes actually source-tested

**Issue:** #73 · **Status:** draft/QD/founder HOLD · **Scope:** the private Windows x64 six-utility candidate runner only. No production merge, executable release, premium distribution or authorization.

## Gap addressed

The R270–R274 pipeline preserved a passing, SHA-256-pinned source-suite receipt and independently captured build inputs, but **did not compare those two snapshots**. A source or test file changed in the interval *after* `offline_source_gate.py` exited successfully and *before* `build_input_guard.py capture` could be captured as a fresh build input and packaged, although that altered file had not passed the source suite.

The receipt already contains full `source_smoke.source_inventory` and `test_inventory` relative-path/SHA-256 pairs. R275 binds them to the **current** complete checkout via the existing descriptor-custody readers `source_smoke_gate.source_inventory` and `offline_source_gate._test_inventory`. The check independently enumerates both whole trees (including newly added/deleted files), rejects malformed inventories and refuses a mismatch with a fixed, path-free diagnostic.

## Enforcement

- After source suite success, **before** toolchain/build manifests are captured.
- Immediately **after** both manifests are captured, closing the test-to-capture gap.
- At the final success gate alongside the retained source-receipt SHA-256 pin, after six build attempts, native release gate and report attestation.

The real `build_candidate()` CLI always uses `_run_child` and activates these additional snapshots. Existing synthetic `_execute_plan(..., runner=fake)` tests explicitly do not claim they ran real source tests or built candidates, and keep their 40 planned subprocess commands. All original build-input guard checks and human-review/release restrictions are unchanged.

**Threat-model boundary:** These checks detect observed changed source/test bytes and tree membership in a trusted local checkout. They are not signing, a hostile-operator defense, an atomic full-build snapshot, a Windows PE acceptance test, or authorization to distribute. Arbitrary privileged processes or malware on the builder remain outside this integrity claim.

## Local evidence for this sprint

Standalone `source_build_binding_r275.py` with synthetic disk-backed source/test files and injectable inventory readers:

```text
python -m unittest discover -s /mnt/data/r275/tests -p test_source_build_binding_r275.py -q
Ran 18 tests — OK
python -OO -m unittest discover -s /mnt/data/r275/tests -p test_source_build_binding_r275.py -q
Ran 18 tests — OK
python -m compileall -q /mnt/data/r275
PASS
```

The 18 tests exercise unchanged input, source/test rewrites, added/deleted files, mismatched digests, duplicate/oversized inventory, traversal/Windows-slash names, invalid digest characters, unsupported record structures and private-path-safe exception behavior. The synthetic reader hashes real temporary files, but **does not use the production descriptor-custody implementation**. Tests were run on Linux Python 3.13; **entire inherited repository/real runner integration and native Windows builds were not run here**. GitHub Actions runners have repeatedly failed before recording steps; exact R275 CI status must be checked separately.

## Required trusted-checkout verification

1. Run the R275 new tests under Python 3.12 normal and `-OO` on Ubuntu and Windows hosted runners, followed by the **entire** `products/desktop/tests` suite.
2. Reproduce a source-change-after-test/before-capture attempt against a **private synthetic checkout** with the actual `source_smoke_gate`/`offline_source_gate` readers; verify the runner rejects before PyInstaller.
3. Run `python -I products/desktop/scripts/offline_windows_candidate_r269.py --workspace <existing-access-controlled-outside-checkout-directory>` on a trusted Windows 11 x64 machine with audited preinstalled Python, PyInstaller and cryptography. Preserve private source, toolchain, Windows evidence, checksums and PE/executable smoke reports.
4. Check Defender results, hardware keyboard/screen-reader/high-DPI accessibility and premium download/entitlement controls. Complete independent QD and founder approval before any production merge or public release.

**Six unreleased utilities:** LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk (free); GrantAudit Studio Pro and ProcureGuard Studio Pro (premium). No executable artifacts or verified download URLs were produced in this sprint.
