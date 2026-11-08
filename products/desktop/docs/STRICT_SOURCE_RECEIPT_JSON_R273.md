# R273 — Strict private source-suite receipt JSON custody

**Issue #73. DRAFT STACKED PR ONLY. Independent QD + founder approval required for merge/release.** Six Windows x64 utilities remain unreleased (four free, two premium). No binaries or premium URLs are produced by this change.

## Gap addressed

The R270/R271 private candidate runner checked source-suite receipts through `json.loads(data)`. The default CPython decoder silently accepts duplicate object fields (last value wins) and nonstandard `NaN` / `Infinity` numeric values. Therefore ambiguous receipts with conflicting success/approval values could pass JSON decoding before later schema and checksum gates. This is not proof of an actual exploitation or altered candidate; it is a concrete ambiguity in an audit-evidence parser.

Examples reproduced with the actual Python JSON library locally:

- `{"released":true,"released":false}` decodes to `{"released":false}`.
- `{"source_smoke":{"all_six_passed":false,"all_six_passed":true}}` decodes with `all_six_passed: true`.
- `{"synthetic_output_count":NaN}` decodes despite not being strict JSON.

## Code change

- `products/desktop/scripts/strict_source_receipt_r273.py`: private, data-independent decoder with unique-key enforcement at **every JSON object depth**, nonstandard constant rejection, invalid input rejection and a fixed error diagnostic, without retaining a customer path in a chained exception.
- `products/desktop/scripts/offline_windows_candidate_r269.py`: uses the strict decoder **before** checking the existing source receipt's exact schema, test provenance, six smoke results and file/checksum custody. Trusts only the script directory resolved from its own `__file__` under `python -I`, not cwd or `PYTHONPATH`. All existing 40 child commands and Windows acceptance requirements remain intact.
- `products/desktop/tests/test_strict_source_receipt_r273.py`: **16 focused decoder tests** covering valid receipts, nested/escaped duplicates, NaN/Infinity, malformed input, path-private failure, and optimized interpreter semantics.
- `products/desktop/tests/test_source_receipt_integration_r273.py`: **8 repository integration tests** against the actual R269–R273 runner and existing R270 receipt fixture, including an isolated CLI import preflight. These need an actual checkout/CI to execute and are NOT represented as locally passed.
- `.github/workflows/desktop-build.yml`: new explicit normal and `-OO` gates for both modules on **Ubuntu source-tests** and **Windows build** jobs, without uploading or publishing premium artifacts.

The new decoder is **not** a digital signature, release gate by itself, or a substitute for trusted filesystem/producer custody. It does not change any money math, offline financial engine, report decisions, or entitlement validation.

## Evidence — 2026-11-08 UTC

- Environment: Linux, CPython **3.13.5**, synthetic JSON only.
- Baseline Python decoder ambiguity: **3/3 examples reproduced** above.
- Exact committed decoder blob SHA-1: `5e3b7c5d978d6b3df2881f6f026ac7a519a120f4`.
- Exact committed test blob SHA-1: `19381fdc4c9878ed8e46b759f8254f1b84763354`.
- Local commands on those exact files: `python -W error -m unittest discover -s products/desktop/tests -p 'test_strict_source_receipt_r273.py'` = **16/16 PASS**; `python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_strict_source_receipt_r273.py'` = **16/16 PASS**; **32/32 focused decoder method executions**, compileall PASS.
- **Not executed locally:** the 8 added runner integration tests, the inherited full repository suite, hosted Ubuntu/Windows jobs, native six EXE builds, Defender or GUI/accessibility inspection. The GitHub repository is private and not network-cloneable in the Linux execution sandbox; running synthetic decoder tests is not equivalent to running the full committed runner.
- Previous R272 Actions run #42445253471 (2026-11-08 UTC) reported both jobs failed with **zero recorded steps**. A new run for R273 must be checked separately; do not interpret workflow creation as execution.

## Next release-critical step

**Owner unblock:** inspect GitHub Actions billing/spending restrictions, workflow permissions and runner provisioning; restore a runnable Ubuntu/Windows job and rerun the **unchanged R273 branch**. Or execute the private runner in a verified checkout on trusted Windows 11 x64 with audited, preinstalled dependencies and a restricted workspace outside the checkout. Obtain six genuine portable EXE build/smoke records and SHA-256 evidence, Defender results, keyboard/screen-reader/high-DPI checks, protected premium distribution checks and independent QD/founder approval. Do **not** merge to `main`, publish binaries or advertise premium downloads before those gates.
