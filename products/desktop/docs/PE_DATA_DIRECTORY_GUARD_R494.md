# Labs R494 — bounded PE32+ data-directory references (six Windows x64 utilities)

**Status: DRAFT · QD / founder HARD HOLD · NOT a release.** Tracks issue #73. R494 is stacked on [R493 draft #2851](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2851), commit `b83718dd0f2fed4579942fb90573ca4b865c78d8`; never production `main`.

## Safety gap addressed

The existing release gate checked the AMD64 PE header, mapped sections, manifest digest and smoke. It did not validate PE32+ `NumberOfRvaAndSizes` or the data-directory entries. A malformed PE could declare a truncated directory table, unmapped resource/import regions, or an Authenticode certificate table overlapping executable section bytes while passing the header-level shape checks. This matters for **all six** candidate images, including two premium applications; it does not decide whether any image is safe, signed or releasable.

R494 adds `pe_directory_guard_r494.validate_pe_directories` to `pe_image_guard.verify_amd64_pe` **after** section bounds and overlap validation and **before** R493 digest binding. The new validator:

- Reads PE32+ directory count from optional-header offset 108; rejects counts above the 16 defined entries and any truncated table.
- Rejects half-empty address/size pairs.
- Requires every nonempty RVA directory to fit entirely in PE headers or a single mapped virtual section, without crossing headers, section gaps or image bounds.
- Handles security/certificate entry **4 as a raw file offset**, requiring 8-byte alignment, location beyond the headers, full extent within the file and no overlap with mapped raw sections. Valid appended certificate overlays remain accepted as **structure only**, never as cryptographic verification.
- Emits fixed diagnostic labels. Existing R493 same-descriptor SHA256 binding and six-candidate release gates remain mandatory.

This is a conservative prepublication structural policy. Any legitimate Windows/PyInstaller image that fails requires documented review rather than weakening the validator silently. Windows loader acceptance, Authenticode validity, malware scanning and signed-certificate chain verification are explicitly outside the validator.

## Verifiable engineering and test evidence — 2026-11-17

- `products/desktop/pe_directory_guard_r494.py`: dedicated bounded directory validator; locally executed file Git blob `92c5fcc648785602c5fd0aebc7081930b7ca0230`.
- `products/desktop/tests/test_pe_directory_guard_r494.py`: **16** synthetic unit methods covering valid headers, mapped import entries, appended certificates, malformed counts/lengths, unmapped/cross-section references and certificate overlap/overruns; locally executed file Git blob `9f875ecef29fa5abf6faa2591eb8454f86c4a314`.
- Local Linux Python: **16/16 PASS** normal `-B -W error`; **16/16 PASS** optimized `-OO -B -W error`, **32 executed methods, 0 skips**. Both Python files compiled successfully. Exact committed Git file blobs matched the files executed locally. Test data is inert bytes; no PE executable was executed.
- Updated `products/desktop/pe_image_guard.py`: validates data directories before digest custody.
- `products/desktop/tests/test_pe_directory_binding_r494.py`: **six additional integration regressions committed but not locally executed**. They check parser acceptance/rejection and end-to-end six-candidate failure when an invalid import directory is present.
- `.github/workflows/desktop-source-evidence-r385.yml` and `.github/workflows/desktop-build.yml`: both run the unit and integration modules in normal and optimized Python; the internal Windows job requires successful PowerShell exit-code checks.

### Trusted complete-checkout acceptance commands

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_directory_guard_r494.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_directory_guard_r494.py
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_directory_binding_r494.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_directory_binding_r494.py
```

## Blocker, next acceptance and no-release controls

As verified on the R493 parent commit, [source CI #44051986703](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44051986703) and [Windows internal build #44051986643](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44051986643) failed **before any job steps** (four jobs `steps=null`, no logs), not during application tests. A repository owner must inspect GitHub Actions failure annotations, billing/runner eligibility and workflow permissions or use an authorized native Windows x64 full checkout. Check R494 **exact-head** CI separately after the PR is opened.

Only after this and inherited regression suites run successfully: build each actual Windows x64 executable, perform native `--smoke-test`, Defender/AV checks, signing provenance, checksum identity, keyboard accessibility and authenticated premium access-control tests. Preserve reviewer evidence, then obtain **independent QD review and explicit founder approval**. The four Lite apps remain free, the two Pro apps remain access-controlled, and financial processing stays offline/local-first with Decimal-safe logic, deterministic audit provenance and human compliance decisions. **Do not merge, publish, enable auto-approval or expose unrestricted premium binaries on R494 evidence.**
