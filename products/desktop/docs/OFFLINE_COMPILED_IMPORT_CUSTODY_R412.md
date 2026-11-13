# R412 — Refuse unmeasured compiled imports during six-app source smokes

**Scope:** Final Vestige Labs issue #73, standalone Windows x64 utilities. DRAFT SOURCE-ONLY EVIDENCE. This change is **not** a binary test, distribution approval, premium entitlement grant, safety certification, or permission to publish.

## Reproduced limitation in R411

The R411 offline gate hashes Python `.py` files but does not include bytecode caches or native import artifacts in its source inventory. CPython may execute an existing cache (`__pycache__/*.pyc`) or a compiled import extension instead of the inventoried Python text. The previous gate could therefore produce a source-only receipt without checking all potentially executed import bytes. These are engineering threat scenarios, not assertions of an actual incident.

A second issue surfaced while running R412's real synthetic launcher test: the child uses `python -I`, which ignores `PYTHON*` environment variables, including `PYTHONDONTWRITEBYTECODE=1`. An isolated child can therefore create a new `__pycache__` during the source smoke, even though its inherited environment contains that value.

## Implementation

- Walk the actual `fvs_suite/` and `launchers/` import roots without following linked directories. Reject existing files with case-insensitive suffix `.pyc`, `.pyo`, `.pyd`, `.so`, or `.dll` **before** any of the 12 source-only children start.
- Run all six launchers in both normal and optimized modes with explicit `-I -B`: `-I` isolates imports; `-B` prevents writing source-tree bytecode even when Python ignores its environment.
- R411's before/after-each-child source custody now also rejects compiled import artifacts inserted between subprocesses.
- Retain restricted child environment, `DEVNULL` stdout/stderr, stdin disabled, fixed Python launcher list, SHA-256 source digest, private fixed diagnostic messages and `release_authorized=false`.
- Keep non-executable local assets such as CSV and JSON available; do not alter financial engines, Decimal calculations, provenance exports, premium downloads or human-review controls.

## Verifiable tests

`products/desktop/tests/test_source_import_artifacts_r412.py` has **12 unittest methods** exercising compiled cache generation, nested and uppercase bytecode, sourceless bytecode, legacy bytecode, native DLL/PYD/SO files, both import roots, private error redaction, artifact introduction before or during a child process, `-I -B` invocation, and permitted CSV/JSON data. Its happy-path fixture really runs the six synthetic launchers in both modes: **12 child invocations per suite execution**.

Local isolated Linux reconstruction: source blob `8c30aa8192114fc4a7a66fec8b662423ef79dc20` and test blob `1fd6f03be1e0628955aa9e5ebcc444e26ed20fae`, each independently confirmed by `git hash-object` against GitHub. Executed using the host's `/usr/bin/python3`:

```bash
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -W error -m unittest discover -s tests -p test_source_import_artifacts_r412.py
PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -OO -W error -m unittest discover -s tests -p test_source_import_artifacts_r412.py
```

**12/12 normal PASS + 12/12 optimized PASS = 24/24 focused method executions.** Tests use synthetic launchers, not full genuine financial engines. Source compilation succeeded. No native Windows EXE, Defender/EDR test, NVDA/keyboard acceptance, license-access test, or complete-repository financial/crypto regression is claimed.

The Windows/Ubuntu independent workflow `desktop-source-evidence-r385.yml` adds the same two test modes. CI is still contingent on GitHub Actions runner eligibility: R411 source #43516862499 and desktop-build #43516862689 finished with no recorded execution steps, root cause unknown.

## Remaining caveats and acceptance gates

This is a practical import-custody guard, **not** a filesystem/process sandbox. It does not ensure immutable files between inspections, nor hash every external Python standard-library/native dependency. If a trusted checkout contains compiled modules needed by a legitimate test, investigate that dependency and determine a separately pinned and auditable policy before weakening the guard. Do not silently delete an artifact in response to a failure.

**Next:** Restore GitHub Actions runner execution or use a trusted full checkout to run R408–R412, all six real source smokes, all financial/Decimal/cryptographic regressions, then build and independently verify genuine Windows x64 executables with Defender, accessibility and protected premium distribution. Independent QD review and explicit founder authorization remain mandatory.
