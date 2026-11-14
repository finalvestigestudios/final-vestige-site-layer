# Final Vestige Labs R433 — bounded private inventory read boundary

**Status: DRAFT / NO RELEASE.** Issue #73. Strictly stacked on R432 draft #2514, not production `main`. `release_authorized=false`. Independent QD review and explicit founder approval are mandatory before merge, packaging, deployment, or site publication. No downloadable binaries, WordPress changes, entitlements, paid downloads, or license changes are included.

## Source problem and security scope

The shared `fvs_suite.manifest_guard._hash_regular(path, maximum)` descriptor-based inventory SHA-256 helper accepted caller-supplied unbounded and nonnative `maximum` values. `float("inf")` and an oversized integer could bypass the intended internal 256 MiB report ceiling when the helper was called directly, regardless of the normal 64 MiB source / 256 MiB report caps used by `inventory_text`. A `bool`, `int` subclass, NaN, negative and other malformed values also lacked predictable fail-closed validation. **This is a direct Python API hardening issue; no customer exploitation is asserted.**

The same inventory module sanitized displayed filesystem errors by raising `... from None` **inside** `except` blocks. Python can still retain the private pathname or OS error object in `__context__`, even though formatted tracebacks suppress it. The patch raises sanitized errors **after** leaving the handlers on missing/failed `lstat`, open and read paths, without modifying the successful descriptor identity, same-byte hashes, reporting order, or retry/close behavior.

## Implemented controls

- Enforce a native, exact `int` byte budget from **0 through 268,435,456** before any private path inspection or file opening. This is an absolute safety ceiling, **not** permission to import source CSVs above the separately enforced 64 MiB cap.
- Keep normal SHA-256 fingerprints, exact file-size checks, descriptor/path identity checks, source digest pinning, synthetic failure handling and file closure intact.
- Ensure the intended public `ValueError` and `FileNotFoundError` paths for inventory metadata, descriptor opening, and read errors have no hidden `__cause__` or `__context__` holding financial filenames or text. No private file contents enter logs or network requests.
- Add 10 `unittest` regression methods (including nine invalid-bound subcases), covering pre-path rejection, missing/permission/read failures, empty-file zero bound, exact digest success, file-size failure, and source+report pinned inventory.
- Add new Ubuntu 24.04 + Windows source-evidence workflow step for the new tests in standard and `-OO -W error` modes, plus inherited R29/R31/R425 inventory custody suites.

## Actually executed local verification — synthetic, Linux only

Exact repository source and test blob IDs were reconstructed into an isolated local package. `manifest_guard.py` source blob is `1623f0be8ba58a17b2497194362aed28934211f0`, and `test_manifest_private_read_budget_r433.py` is `b8c2d9608a903c19b1d4f25192cdc300491b9c30`. The two *unchanged* imports `csv_snapshot._same_path_descriptor_signature` and `premium_link_custody.open_inventory_stream` were simplified local substitutes; therefore these tests cannot establish whole-repository or native Windows integration.

```sh
PYTHONPATH=. python -W error -m unittest discover -s tests -p test_manifest_private_read_budget_r433.py
PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p test_manifest_private_read_budget_r433.py
python -m py_compile fvs_suite/manifest_guard.py tests/test_manifest_private_read_budget_r433.py
```

**Observed:** standard **10/10 PASS**; optimized **10/10 PASS**; **20/20 total focused method executions**, source/test compilation PASS. Controlled baseline on exact pre-fix blob `fa6ed4ab09fd2e229a0e0a4339c2a8fb1a2a5491`: **14 failing assertions/subtests across 10 methods**; the failing checks exposed hidden exception contexts and unbounded/invalid size arguments. Local tests used only synthetic CSV bytes.

**Not executed/verified:** full repository dependency integration, inherited R29/R31/R425 suite commands, full six-app tests, hosted Ubuntu/Windows jobs, actual Windows x64 portable executables, Defender, signing, keyboard access, premium download/payment/entitlement flow.

## Release blockers and smallest unblocking action

As of 2026-11-14, R432 [Ubuntu/Windows source evidence run #43629824743](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43629824743) and [Windows build run #43629824897](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43629824897) failed before executing any recorded steps. Confirm account/org Actions billing, spending limits, runner allocation and Actions policy. Then trigger exact R433 HEAD CI and require genuine Windows/Ubuntu passes including all inherited manifest, financial and premium entitlement suites. Native six-executable build, offline launch, checksums, Defender, accessibility and access-controlled premium distribution remain separate release gates. Do not publish or merge without independent QD and explicit founder signoff.

Money remains exact Decimal-based; inventories are non-authenticating SHA-256 descriptions and never constitute payment, procurement or compliance approval.
