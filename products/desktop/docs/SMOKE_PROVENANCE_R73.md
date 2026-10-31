# R73 — native Windows smoke provenance (draft; unreleased)

## Risk and corrected contract

The `release_gate.verify(smoke=True)` API accepted an injected runner and
`platform_name="nt"` for inert regression fixtures. Those tests correctly
checked ordering, failure handling, and checksum drift, but the returned
`status` was indistinguishable from actual packaged Windows execution:
`windows_smoke_passed`. Such a JSON result could be mistakenly used as
Windows release evidence, despite no executable being launched.

A new pure `smoke_provenance.classify_smoke` guard now returns:

| Status | Conditions | Can claim native Windows EXE smoke? |
| --- | --- | --- |
| `integrity_only` | `smoke=False` | **No** |
| `synthetic_smoke_only` | Tests inject a runner or platform override; the test's nominal platform is `nt` | **No** |
| `windows_smoke_passed` | Real `os.name == "nt"`, native host machine `AMD64` or `x86_64`, no injected runner/override; all six EXE `--smoke-test` calls exit 0 and artifacts remain stable | **Yes, limited to native smoke only** |

On an actual non-Windows host, simply setting
`platform_name="nt"` without injecting a runner now raises
`GateFailure` before candidate execution. Unsupported native host
architectures (e.g., ARM64, 32-bit x86) also fail closed in genuine mode.
Mocked runs get `smoke="simulated"` per executable, and the evidence fields
`windows_executables_verified=False`, `smoke_simulated=True`. A native
successful run gets `smoke="passed"` per executable,
`windows_executables_verified=True`, `smoke_simulated=False`.

The CLI cannot inject a runner or platform override and therefore cannot
produce synthetic success through those test-only API arguments.

The independent `report_attestation.py` schema accepts the new two boolean
fields only when they agree with the status. It deliberately **rejects**
`synthetic_smoke_only` evidence even if the six inert fixtures returned zero,
and rejects forged/missing/loosely typed provenance flags. R39 evidence
regressions now include six new methods for this boundary.

## Regression verification

```bash
cd products/desktop
PYTHONPATH=. python -W error -m unittest discover -s tests -p test_smoke_provenance_r73.py -v
PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p test_smoke_provenance_r73.py -v
python -m compileall -q smoke_provenance.py tests/test_smoke_provenance_r73.py
```

17 locally executed pure-function tests cover genuine/mock/no-smoke classification, Linux
override attempts, ARM64/x86 rejection and malformed flags. R9, R10 and R37
existing mock-runner expectations have been updated to the explicit synthetic
status and flags. The six additional attestation tests are committed but require
full-repository execution before they can be counted as passed. The complete repository integration suite and true Windows
packaged execution remain separate required tests, not asserted by the local
pure-module results.

## Operational release hold

This prevents a misleading *label* in release candidate evidence; it is not
Authenticode verification, malware scanning, secure licensing, payment access
control, or a test that the six executable products function on fresh Windows
11 x64 installations. Even a genuine `windows_smoke_passed` report retains
`release_authorized=False`, `premium_entitlement_verified=False`,
`codesigning_verified=False`, and `malware_scan_verified=False`.

Resolve hosted runner-start incident #75, execute complete source tests and
all six native Windows executable smoke tests, then carry out human-led
GUI/accessibility, AV/SmartScreen and premium entitlement/distribution
reviews. Independent QD/founder approval is required before a production
merge, WordPress download links or any executable distribution.
