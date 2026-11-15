# Labs R451 — six-app CSV guard import compatibility

**Issue:** #73. **Release:** HARD HOLD. **Parent:** R450 draft PR #2622, pinned at `513c5902d549c0585ca6f2c4e63537db53de490f`. This is a stacked draft, never a production-main edit.

## Real regression caught before CI execution

R450 correctly moved shared CSV filesystem error sanitization from the raising
`raise_private_csv_failure` helper to the non-raising
`private_csv_failure` builder. But the inherited
`products/desktop/tests/test_csv_publish_guard_r237.py` still imports the
removed helper. A direct import against the R450 module reproduces
`ImportError` before any test method can run. The legacy R237 tests are also
referenced by `.github/workflows/desktop-build.yml`; they would fail on a
working hosted runner and conceal later packaging results.

## Changes

1. **Migrated real R237 regression coverage** to the non-raising builder:
   destination collision, errno preservation, masked/private path absence,
   descriptor ownership, UTF-8 BOM and existing-destination safety. No
   compatibility raising alias was added: raising a fresh error inside an
   active private exception handler can leak the original via `__context__`.
2. **Added one nested private-cause test** to the inherited suite. All returned
   errors are checked for absent `__cause__`, `__context__` and filename
   attributes rather than expecting the unsafe old helper to raise.
3. **Added a read-only static import contract check** for Python sources under
   `products/desktop/`. It inspects AST imports from the shared guard without
   importing application modules or processing private data; stale references
   fail before packaging.
4. **Registered R451 plus inherited R237 guard and actual writer integration**
   in the Ubuntu/Windows source-evidence workflow, normal and optimized mode.
   The full native Windows build already references the inherited R237 suite.

## Local reproducible evidence (2026-11-15)

Environment: isolated Linux Python 3.13.5, no user financial files, no
network, no installer. The **actual fetched production guard source** and
**the committed updated R237 / R451 test source** were copied into a minimal
package, with Git blob IDs checked against the exact GitHub files:

- `csv_publish_guard.py` blob `c65132e51fad3b5c24fee69bf80f4f547622c772`
- updated `test_csv_publish_guard_r237.py` blob `9f0fc1e3acb976fe3c441ac018a51e253b132541`
- new `test_csv_guard_import_contract_r451.py` blob `150387f2d76e7ca6c26d8802af9cbf38fea2844e`
- R237: **15/15 PASS** in standard mode and **15/15 PASS** with `-OO -W error`
- R451: **3/3 PASS** in standard mode and **3/3 PASS** with `-OO -W error`
- **36/36 focused executions PASS;** `compileall` PASS
- Pre-fix import was explicitly reproduced as `ImportError`.

These local tests prove only the exact two test files against the exact shared
helper in a minimal source package. The R451 AST scan ran over that *minimal
package*, **not the entire repository**. Inherited full-writer integration,
actual Windows x64, and the complete six-engine suites are **not** verified.

## Required source/Windows follow-up

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_csv_guard_import_contract_r451.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_csv_guard_import_contract_r451.py
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_csv_publish_guard_r237.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_csv_publish_guard_r237.py
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_csv_publication_integration_r237.py
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_csv_publication_integration_r237.py
```

At parent R450, [source workflow #43716974231](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43716974231) and [Windows workflow #43716974218](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43716974218) failed with no recorded steps. Runner eligibility, billing/policy and job annotations need owner review; the exact infrastructure root cause is unconfirmed. After restoring runners, require complete six-engine regressions, genuine Windows x64 packaging, SHA-256, Defender/accessibility smoke, and access-controlled premium download review.

**Invariant release boundary:** local-only finance, Decimal-safe money, deterministic
provenance, human compliance review, no telemetry, no source overwrites; no
binaries, public premium files, fabricated download URLs, WordPress publication,
merge or release without independent QD and explicit founder approval.
`release_authorized=false`.
