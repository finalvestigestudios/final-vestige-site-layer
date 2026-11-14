# R425 — premium inventory SHA-256 provenance must use native stored values

**Scope:** GitHub issue #73; shared manifest_guard.inventory_text used for GrantAudit Studio Pro evidence and other inventory callers. Source-only draft stacked strictly on R424, with QD/founder release hold. This does not assert the two premium products are release-ready, and does not change the four free apps.

## Reproduced defect

The optional expected_input_digests binding should refuse inventories when financial CSVs changed after parsing. Before R425, isinstance(digest, str) admitted str subclasses. Python comparison on an actual native SHA-256 versus the provided subclass can invoke its overridden __ne__; a different but canonical-looking 64-hex hash could falsely claim equality. Also a custom mapping's items() could manufacture hash entries different from its stored values. These are direct-Python-API input validation weaknesses, not proof of production exploitation.

## Production change

- Require exact built-in str for each expected SHA-256; retain canonical lowercase 64-hex validation.
- Copy native dictionary storage using dict.items(mapping), bypassing overridden mapping methods; reject virtual non-dict mappings.
- Permit only exact built-in str keys and native Path keys; reject custom __fspath__, string equality and hash hooks in map keys.
- Reject duplicate canonical string/Path representations, and reject unsupported input before hashing customer financial sources.
- Preserve source SHA-256 matching, descriptor integrity, private error handling, escaped report names, human review and unpinned descriptive inventory.

**Compatibility:** plain dictionaries keyed by standard str or Path remain valid. Other Mapping abstractions, subclassed paths and digest subclass strings now fail closed. No financial source modification, telemetry, network access, payment or compliance approval.

## Measured local verification

Linux Python 3.13.5 isolated local checkout, reconstructed from exact connected GitHub repository source blobs. Local git hash-object matched:

| Artifact | Git blob SHA |
| --- | --- |
| patched fvs_suite/manifest_guard.py | fa6ed4ab09fd2e229a0e0a4339c2a8fb1a2a5491 |
| existing fvs_suite/csv_snapshot.py | b0d7dc324800f0d335a17812512b76470eb336ca |
| existing fvs_suite/premium_link_custody.py | 7b66c0cbe4f67f488e6f4d991fc49805a3e74da0 |
| new tests/test_inventory_native_digest_custody_r425.py | 207ef70e09d6e5936627ffc105225d21ca488f04 |

- New committed R425 tests on actual production module and two unchanged source imports: **18/18 PASS** standard Python with -W error; **18/18 PASS** optimized -OO -W error, **36/36 method executions** total.
- Python py_compile of module, two imports and new tests: PASS.
- Controlled pre-fix substitution of original actual module blob 686613719e974d5f0b5029a09780396e76386168: **9/18 R425 tests failed**. Restoring patched exact blob returned 18/18 PASS.
- Tests run with synthetic local files only and check forged comparison, dict subclass virtual items, hostile path hooks, duplicate names, valid native paths, wrong hashes and private-value-free errors.

From a standard checkout run the following; Ubuntu/Windows CI is wired to run all six commands:

    python -W error -m unittest discover -s products/desktop/tests -p test_inventory_native_digest_custody_r425.py
    python -OO -W error -m unittest discover -s products/desktop/tests -p test_inventory_native_digest_custody_r425.py
    python -W error -m unittest discover -s products/desktop/tests -p test_manifest_guard_r29.py
    python -OO -W error -m unittest discover -s products/desktop/tests -p test_manifest_guard_r29.py
    python -W error -m unittest discover -s products/desktop/tests -p test_snapshot_manifest_binding_r31.py
    python -OO -W error -m unittest discover -s products/desktop/tests -p test_snapshot_manifest_binding_r31.py

**Limits:** Minimal isolated directory, not a complete repository, all-six-app engine suite, full premium integration, or native Windows run. Inherited R29 and R31 tests were wired to CI but not executed locally. The prior R424 hosted source/build workflows failed with no recorded execution steps.

## Release gate and next action

No production merges, site edits, binaries, public premium links, executable signing or license changes in this sprint. Existing founder/QD gates remain mandatory. Restore GitHub Actions hosted-runner execution, run all new and inherited regression suites at the exact R425 head on both Ubuntu and Windows, then validate actual six Windows x64 executables, Defender scans, keyboard/accessibility and genuinely access-controlled premium distribution, with reproducible SHA-256 release evidence.

**Smallest unblock:** repository owner checks account/org Actions billing, spending cap, hosted-runner eligibility and repository Actions policy, then reruns the exact R425 source and build workflow; verify that a runner and test steps actually start.
