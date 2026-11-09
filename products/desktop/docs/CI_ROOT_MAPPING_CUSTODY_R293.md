# Labs R293 — desktop CI root-mapping custody

**Status: DRAFT / NO RELEASE.** Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on the unmerged R292 head `c36a65804fd6fdaac0bb458977c6fac4fe019398`, **not production `main`**. Independent QD review and founder approval remain required before merge, site changes, or distribution.

## Reproducible policy gap

The R292 `ci_source_contract._jobs()` required one textual `jobs:` and parsed only the block after it. It **stopped scanning on a later unindented line** and ignored earlier top-level mappings. A second YAML-equivalent `jobs :` or `"jobs":` root mapping, an appended `permissions:` / `env:`, or an additional YAML document could therefore coexist with a passing *lexical* source-contract check. Real GitHub Actions YAML evaluation of conflicting document/root mappings is not asserted here; the security defect is the scanner's failure to reject ambiguity before CI.

## Implemented

- Fail closed unless **noncomment, nonindented root lines** appear in exactly one reviewed canonical sequence: `name: Desktop suite build (internal)`, `on:`, optional `permissions:`, and `jobs:`. This preserves the minimal R57 fixture and the actual six-app CI workflow, without adding a general YAML parser.
- Reject shadowing root mappings **before and after** the canonical jobs tree, alternate/quoted jobs keys, appended permissions/environment, document separators, alternate root event-key spelling, and changed workflow names.
- Add **13 R293 unittest methods** (12 local runnable plus one full-checkout integration assertion) and mandatory normal and `-OO -W error` gates on both Ubuntu source and Windows build jobs.
- The actual workflow remains **153,907 UTF-8 bytes**, below the R292 reviewed **196,608-byte** ceiling. Its root sequence remains exactly `name:`, `on:`, `permissions:`, `jobs:`. No action SHA or artifact scope changed.
- This lexical check **does not** validate nested trigger/event definitions, arbitrary YAML semantics, runner integrity, customer-side Windows execution, premium licensing, or QD signoff.

## Executed evidence (isolated local source reproduction, not full checkout)

On Linux, reconstructed source files were verified using Git's blob hashing against the **exact committed GitHub contents**:
- `ci_source_contract.py` candidate blob `a619f0e37574d96f635facca335b72718d1da857`
- R293 test file blob `6eb176c08aaed639423481fe5932a8eaa3b68d07`
- Unchanged source dependencies: `ci_action_pin_guard.py` `e672e67401026dd6c50192907d7e79b708897755`, `ci_action_key_guard_r164.py` `772ac3d81f1ed8bf3aa3bd2a4601b4d0a91478d3`, `ci_gate_step_contract.py` `373fbd65ade984ae202cf5fd6695f3feccdf222e`, `ci_workflow_budget_r292.py` `8f50f300feb3ebfc06409398e446466b0a069aee`.
- Existing `GOOD` fixture was reproduced verbatim from `test_ci_source_contract_r57.py`. Its enclosing pre-existing test module was **not** reproduced byte-for-byte, and the *actual* 153,907-byte workflow was inspected through the GitHub connector rather than cloned locally.
- `python -W error -m unittest -v test_ci_root_mapping_custody_r293`: **12 passed, 1 skipped** (full-checkout assertion).
- `python -OO -W error -m unittest -v test_ci_root_mapping_custody_r293`: **12 passed, 1 skipped**. **24 passing method executions**, two explicit skips.
- `py_compile` of exact R293 implementation/test: **PASS**.
- **Negative control:** restoring the exact unchanged R292 `ci_source_contract.py` blob `47c85b99ebd139dc3822dbf3b754a7c5619bd82f` produced **10 test failures / 13 methods (1 skip)**, demonstrating new tests detect the previous lexical bypass. Restore R293 blob returns green.
- The committed full-checkout assertion, inherited full suite, hosted Ubuntu/Windows CI and six native Windows x64 executable validations **have not executed here**. Do not represent the isolated tests as full integration.

## Reproduce after full Git checkout

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_ci_root_mapping_custody_r293.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_ci_root_mapping_custody_r293.py' -v
python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml
```

## CI and next release gate

R292's [Actions run #42537998583](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42537998583) recorded completed **failure** for both `windows-build` and `source-tests`, each with `steps: null`; this does **not** demonstrate a code-test failure. Owner should inspect Actions billing/spending restrictions, permissions and runner availability, then rerun **unchanged R293** in hosted Ubuntu and Windows and collect unabridged source provenance.

Next: complete the full repo regression suite and native Windows 11 x64 private six-app EXE build/smoke, SHA-256/PE integrity, Microsoft Defender, physical keyboard/screen-reader and gated premium distribution evidence. No binaries, public download links, premium entitlements, website changes, compliance approvals, or release authorizations were delivered.
