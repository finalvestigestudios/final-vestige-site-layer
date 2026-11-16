# Final Vestige Labs R461 — complete six-app source / child receipt binding

**Issue:** [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73) · **Draft / QD HARD HOLD** · stacked on R460 [draft PR #2677](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2677) at `8f0592e8b7b2026dd5a72847a84b949798624898`, **not production main**.

## Failure fixed

The R459 offline regression gate fingerprints a deliberately narrow set of parent/test sources. R460 verifies all twelve launcher smoke *statuses* and only the **shape** of the child-reported source SHA-256. A valid R408 receipt from another source tree could pass even if its digest did not match the source the parent observed. The parent also did not detect modifications to unlisted imported engine/launcher/asset files made between R455–R458 tests and R408 smokes.

**R461** adds a separate, exact R408 `source_digest()` snapshot immediately before regression tests, checks it again after regressions and after all launcher smokes, and requires the R408 child to report precisely that original digest. R408's existing bounded descriptor-based inventory already includes every `fvs_suite/` and `launchers/` file, including non-Python assets, and rejects symlinks, untrusted compiled imports, malformed launcher routes, and observed replacement during hashing. This does not turn point-in-time source checks into a signed attestation.

## Committed changes

- `offline_source_binding_r461.py`: small privacy-safe adapter to R408 full-source inventory and strict R460 receipt parser, rejecting stale/wrong-checkout child SHA-256.
- `offline_regression_gate_r459.py`: pre-test/after-test/after-smoke full-source check; child receipt must match pinned digest; R461 tests registered as the fifth regression module. **Expected mode runs: 10** (5 actual test modules × normal and `-OO`); **expected launcher source-smoke statuses: 12** (6 applications × 2 modes).
- `test_source_digest_binding_r461.py`: 15 new methods, testing six-launcher source inventory, engine/launcher changes, bytecode/symlink hazards, stale receipt digests, private error scrubbing, and mocked parent control-flow refusals.
- R459/R460 test contract adjustments and independent Ubuntu/Windows source CI plus Windows pre-packaging CI. No changes to prices, Decimal calculations, approval logic, premium entitlements, or production website.

## Local execution evidence, precisely scoped

On **Linux Python**, the R461 *exact committed Git blobs* for the new adapter and 15-method test file were checked via Git SHA-1 and run against **local surrogate versions** of the R408 source collector, R460 receipt parser and R459 parent runner. Results: **15/15 normal PASS + 15/15 optimized PASS (30/30 test-method executions)**, `-W error`, Python compile PASS. The surrogate fixtures exercise source mutation, parser errors and parent branch logic; they do **not** establish that the existing complete GitHub modules, complete repository, or Windows implementation pass. The full 15 committed tests remain pending execution with the actual R408/R459/R460 code. No skipped methods in the local run. A Windows host without symlink privilege does not skip this strict source-only module.

Reproduce **in a full checkout** (from this draft branch, no customer data):

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_source_digest_binding_r461.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_source_digest_binding_r461.py
python -B products/desktop/offline_regression_gate_r459.py
```

The third command must require **10/10 real regression mode executions**, **12/12 real six-app launcher source smokes**, original source-fingerprint continuity and child digest match; its local JSON remains `SOURCE_ONLY_NOT_WINDOWS_BINARY` and `release_authorized=false`. It cannot authorize an executable.

## Blocking release gates

Hosted Actions have failed before their first job step on prior exact commits; investigate the **new R461 run** once GitHub schedules it. Do not infer any source test, native Windows build or Windows Defender pass from a queued/failed-before-steps job. A trusted Windows 11 x64 host must still execute full six-app regression tests, actual six portable EXE packaging, installed-launcher/GUI/keyboard/accessibility tests, Defender scans, deterministic SHA-256 inventories, and protected premium access verification. Independent QD review and explicit founder approval remain mandatory before merge or publication. No premium files may be published at public, unprotected URLs.

**Next action:** obtain actual GitHub Actions job failure annotations (billing/spending limits, runner availability, Actions policy), restore runner execution, and execute the R461 exact-commit source gate plus native Windows packaging verification; attach only redacted, reproducible evidence to #73.
