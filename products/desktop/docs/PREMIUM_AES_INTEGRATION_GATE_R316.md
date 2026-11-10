# R316 — Mandatory executable premium AES-GCM source integration (DRAFT / QD + founder HOLD)

Tracks [desktop suite issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73); stacked on R315 draft [#1809](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1809). No production, catalog, WordPress or distribution edit.

## Why this is needed

The existing source suite can report a successful run with skipped test methods (provided each module has some active tests). R310 and R312's new real AES-GCM integration tests were committed but had never received hosted execution evidence because Actions jobs failed before runners were assigned. A per-method requirement now prevents those critical paths from being accepted merely because test discovery succeeded, or because other cases in those same modules passed.

`products/desktop/scripts/vault_crypto_gate_r316.py` runs **22 named integration methods across four actual source-controlled modules**: original R8 encrypted evidence flow (12), R303 real encrypted-archive publication (3), R310 restored plaintext rollback/error privacy (4), and R312 correct/wrong-product vault restoration (3). It verifies every required case exists, that all source files are present and regular, that test discovery imported no failed module, and that **zero tests skipped, failed, errored, or reported expected/unexpected results**. It preflights all four module paths before executing the first one. All test import/runner Python stdout and stderr are suppressed, and failure messages do not reveal private paths, test data, passwords, or tracebacks.

`products/desktop/tests/test_vault_crypto_gate_r316.py` contains ten independent synthetic contract regressions and **one non-skipping test that exercises all 22 real cases**. The existing full-source `unittest_provenance.py` discovers the new test automatically; as a result the `offline_source_gate.py` source receipt and Windows candidate prerequisite cannot pass when the mandatory AES integration gate fails. The real-integration test has **no mock fallback**. An owner may also directly run the dedicated gate locally.

## Reproducible commands (repository root)

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_crypto_gate_r316.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_crypto_gate_r316.py'
PYTHONPATH=products/desktop python products/desktop/scripts/vault_crypto_gate_r316.py
python products/desktop/scripts/offline_source_gate.py --report /path/to/private/outside-checkout/source-suite.json
```

Keep the report in an existing private directory **outside the checkout** and retain source/runner custody. These commands do not build, sign, publish, or authorize premium executables.

## Actual R316 local evidence and limitations

On Linux CPython 3.13.5, exactly the ten isolated synthetic regression methods passed using normal Python and optimized `-OO -W error`: **10/10 + 10/10 = 20 passing executions**. Test cases reproduce missing methods, skipped methods, failed assertions, import exceptions, symlink substitution, missing later modules, tampered/duplicate selector lists, sensitive output, and `SystemExit`. Both files compile under Python. The eleventh full-checkout method was **NOT** run locally because this execution environment lacks the private source tree; the 22 real AES-GCM cases are **NOT** reported as passing. The new gate therefore remains unproven on the complete checkout and native Windows.

## Next acceptance and gates

Restore Actions runner allocation (inspect billing/spend restrictions/permissions) or execute the documented complete source-only gate on a trusted full local checkout with `cryptography` installed. Collect the actual zero-skip 22-case result, full source regression evidence and six source smokes. Then privately build/verify six Windows 11 x64 candidates and complete Defender, SHA-256, keyboard/screen-reader accessibility, malware, entitlement and gating acceptance. Independent QD review and founder authorization are mandatory before merge, site publishing or release. **All six utilities remain unreleased.**
