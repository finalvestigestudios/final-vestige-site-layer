# R18 — PE entrypoint-to-code mapping gate (internal pre-release)

## Defect and impact

R17 correctly rejected many malformed PE32+ images but only required a
nonzero AddressOfEntryPoint *somewhere* plus a backed executable section
*somewhere else*. A checksum-matched synthetic image with an entry point in
its DOS header, outside SizeOfImage, in an unbacked zero-fill range, or in a
non-executable data section could pass R17. Overlapping sections also escaped
validation. This could produce false-positive release-candidate evidence before
real Windows smoke testing.

## New fail-closed behavior

The existing `products/desktop/release_gate.py` calls
`pe_image_guard.verify_amd64_pe` for **all six EXEs before launching any**.
R18 validates:

- PE32+ AddressOfEntryPoint is in SizeOfImage and within a section flagged
  executable, with entry bytes actually backed by that section's raw payload
  and not only by alignment padding or virtual zero-fill.
- Section RVAs and raw offsets/lengths are aligned, mapped section extents
  remain inside SizeOfImage, and SizeOfImage/SizeOfHeaders respect alignment.
- No two sections claim overlapping virtual ranges or overlapping file-backed
  raw byte ranges. The overlay beyond PE section data stays allowed for
  PyInstaller one-file packaging.

This is a narrow *syntactic* acceptance improvement. It is **not** a malware
scanner, cryptographic signature validator, sandbox, or proof of runnable code.
Do not infer trusted provenance from a self-generated SHA256SUMS inventory.

## Executed, scoped test evidence

Local Python 3.13.5 on Linux, using **exact R17 fetched source** for
`pe_image_guard.py`, `pe_fixture_r17.py`,
`test_pe_structure_r17.py`, and `release_gate.py`
before applying R18 changes:

- 13/13 R18 unit tests passed, including two-section positive control and
  synthetic one-file overlay preservation.
- 3/3 R18 full-catalog integration tests passed. The last-candidate rejection
  happens before a mock smoke runner is invoked.
- 13/13 existing R17 adversarial tests passed against R18 changes.
- All 26 PE unit tests passed again with Python `-OO`.
- `compileall` passed for these Python sources.
- Test data are **inert synthetic PE bytes, never executable binaries**.
  `platform_name="nt"` in the mock-runner test exercises gate control flow;
  it does **not** constitute a Windows smoke run.

Reproduce in the actual repository checkout:

```bash
PYTHONPATH=products/desktop:products/desktop/tests python -m unittest discover -s products/desktop/tests -p 'test_pe*' -v
PYTHONPATH=products/desktop:products/desktop/tests python -m unittest discover -s products/desktop/tests -p 'test_gate_preflight_r18.py' -v
PYTHONPATH=products/desktop:products/desktop/tests python -OO -m unittest discover -s products/desktop/tests -p 'test_pe*' -v
PYTHONPATH=products/desktop:products/desktop/tests python -OO -m unittest discover -s products/desktop/tests -p 'test_gate_preflight_r18.py' -v
```

## Remaining release requirements

A clean trusted Windows 11 x64 checkout must run the full repository suite and
`powershell -ExecutionPolicy Bypass -File products/desktop/scripts/verify-windows-candidate.ps1 -Build`.
Capture six actual executable hashes, generated evidence JSON, true packaged
`--smoke-test` outcomes, malware checks, signing status, and documented
accessibility checks. Any packaging incompatibility requires a test-backed
adjustment, not disabling fail-closed checks.

No release is approved by R18. WordPress production changes still require QD
review. All four free apps remain unreleased; both premium products require
protected licensing/downloads. Nothing here authorizes a public link.
