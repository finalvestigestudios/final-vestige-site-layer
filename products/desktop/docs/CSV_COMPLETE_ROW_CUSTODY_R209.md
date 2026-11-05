# R209 — Complete CSV evidence-row custody (DRAFT / HARD RELEASE HOLD)

Tracks [Final Vestige Labs issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Isolated feature branch `feature/labs-r209-complete-audit-row-schema-20261105`, stacked exclusively on **R208 draft PR #1088** at immutable base `fec9e59f0e80a3ae18842a784bd11d697f98a0eb`. Never target production `main`, modify WordPress, or publish binaries without independent QD and founder approval.

## Observed defect and code change

The existing shared `fvs_suite.atomic_reports.write_csv_report` used `csv.DictWriter` with the default `restval=""`. If any supplied financial report row lacked a declared column key, DictWriter silently wrote an empty cell, making a **missing source reference, amount, identity, or finding** indistinguishable from an explicitly blank value. That undermines reviewer confidence in evidence completeness.

R209 first sanitizes every supplied row value *once* (including ignored extras, preserving R208 protection), then verifies that **every declared source column exists as a mapping key**. A missing key raises the static privacy-safe `ValueError("Incomplete CSV report row schema")`; the inherited staging/finally logic removes the partial CSV. All originally published evidence remains untouched. Explicit empty strings are deliberately **allowed** because optional/unknown values are not the same as omitted fields. Exact Decimal values are not recalculated. This is a schema contract, **not a conclusion about financial accuracy or compliance**.

One inherited R27 symlink-security test used an incomplete example row although it was intended to test destination symlink rejection. The synthetic fixture now supplies an explicit amount so the original symlink security assertion remains meaningful under the stronger row contract.

## Local test execution — Linux CPython 3.13.5

Synthetic temporary financial fixtures only; no source documents, customer data, networks, or premium entitlements.

- **Red-phase (exact R208 writer source blob):** New 13-method suite produced **8 failures + 1 error** before the fix; four positive cases already passed. Old writer Git blob: `b761fa16dada427da99eac5ad952a21b7daf9715`.
- **Green-phase normal:** R209 13 + inherited R208 18 + inherited R207 14 + inherited R27 11 = **56/56 PASS**.
- **Green-phase optimized `python -OO`:** Same four suites **56/56 PASS**.
- **Total:** **112/112 focused local test-method executions**, no skips. `PYTHONWARNINGS=error`; Python compilation passed.
- The tested local copies are **byte-identical Git blobs** to the proposed branch artifacts:
  - Updated production CSV writer: `8057284fa314f4ae0e1008f9f6a84e91fcd5a001`.
  - New 13-method R209 tests: `449166b6cd1661c0f8bef45a080fbaf66dbe942a`.
  - Adjusted R27 tests: `d5b02b5e0be0c1a9d31a6181191b29212d02740a`.
  - Inherited unchanged R207 tests: `42474f9e0649c81651e2874207c2f53909cfaa2e`.
  - Inherited unchanged R208 tests: `26452413760d70b5c296465b6b643d7d99e45b20`.
- Ubuntu and Windows workflow configuration both invoke the R209 suite in normal and `-OO` modes. **This statement confirms workflow editing only; hosted execution must be separately witnessed.**

### Commands executed (isolated reconstruction)

```sh
PYTHONPATH=/mnt/data/labs-r209 PYTHONWARNINGS=error python -m unittest discover -s /mnt/data/labs-r209/tests -p 'test_*.py' -q
PYTHONPATH=/mnt/data/labs-r209 PYTHONWARNINGS=error python -OO -m unittest discover -s /mnt/data/labs-r209/tests -p 'test_*.py' -q
python -m py_compile /mnt/data/labs-r209/fvs_suite/atomic_reports.py /mnt/data/labs-r209/tests/test_*.py
```

**Limitations:** Local testing reconstructed exactly the relevant production writer and four source-controlled test suites, not an authenticated full-repository checkout. Neither the complete inherited financial/policy regression matrix nor end-to-end all-six-app GUI/report flows were executed. The desktop workflows' Ubuntu and Windows runners have repeatedly failed before steps were available, including [R208 run #42023878663](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42023878663); root cause is unknown.

## Independent validation and release gates

1. Owner inspects Actions UI run banner, billing/usage, permissions and hosted-runner availability; restore execution and rerun this exact R209 head on **both OSes**.
2. Run full inherited regression suite, all six end-to-end report flows (including legitimate explicit blanks) and Policy Delta native Windows symlink behavior.
3. Privately build all six Windows x64 apps; verify checksums, malware scan, smoke tests, Windows 11 keyboard/NVDA/high-DPI access, code signing or explicit unsigned labeling, protected premium distribution and human-reviewed entitlement flow.
4. Obtain independent QD acceptance and founder publication approval. No `main` merge or site/CDN release before acceptance.

**Current status:** All six products **UNRELEASED**. No public executables, production deployment, payment automation or unprotected premium files.
