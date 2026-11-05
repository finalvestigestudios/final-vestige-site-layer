# R217 — native CSV mapping-pair custody (draft / QD hard hold)

**Scope:** Shared offline `fvs_suite.atomic_reports.write_csv_report` CSV publication boundary used by the Final Vestige Labs desktop suite. This is a source-only change; it does not release any app or weaken premium license/download gates.

## Defect reproduced on exact R216 source

The R216 writer capped the number of records emitted by `Mapping.items()` but assumed each yielded item could be unpacked safely with `for name, value in entries`. An arbitrary direct-API `Mapping` can yield a short or long tuple, string, list, generator, object with a hostile `__iter__`, or a tuple subclass that returns **different pairs** from its stored contents. This could raise unredacted exceptions or forge source identifiers before CSV evidence is committed.

The R217 regression suite against **unmodified** R216 committed blobs (`atomic_reports.py` `4d08b277b063fbf77d924e8e0dc71c0d25fb5c5b` and `csv_formula_guard.py` `6819a16c8a65d597a800837dd65a9e2e680cf626`) gave **10 failing methods, 3 errors, 4 passes**. The forged-tuple test demonstrated a CSV was **successfully published with a forged transaction ID** using a custom `Mapping.items()` pair's overridden `__iter__`.

## Fix and compatibility

After bounded item collection and before any unpacking/cell sanitization, require that every pair has `type(entry) is tuple` and `len(entry) == 2`. Both checks are safe on exact built-in tuple and do not invoke attacker-defined `__iter__`, `__len__`, or `__repr__`. Malformed items reject with a constant message, without private exception context; a failed export removes the staged partial and does not replace any existing report.

Native `dict`, `collections.UserDict`, `MappingProxyType`, extra-column sanitization, 0.10 `Decimal` round-trips, UTF-8 BOM, deterministic bytes and existing formula/size rules remain supported. Non-native pair objects yielded by custom mappings are intentionally rejected: callers should yield **built-in, two-element tuples**. Mapping implementations themselves may remain custom.

No money arithmetic or compliance classification changed; local-only operation, exact Decimal values, original source preservation, and mandatory human decision making remain.

## Local test evidence (2026-11-05; Linux x86_64 CPython 3.13.5)

Only the **exact Git-blob** writer/guard files, R217 tests and two inherited test files were reconstructed locally; SHA-1 Git blob hashes were compared against the repository to establish byte equality:

| File | Git blob |
| --- | --- |
| R217 `atomic_reports.py` | `085cf2ffb7db7b9efb6c750feea28034de6cd6c7` |
| Unchanged `csv_formula_guard.py` | `6819a16c8a65d597a800837dd65a9e2e680cf626` |
| R217 `test_atomic_pair_shape_r217.py` | `fca500d3bca5c68803fa974e5ef2907ee616a5da` |
| Inherited `test_atomic_negative_formula_r216.py` | `2efd5588417dd5cfa00fef5a56124376bc1ad602` |
| Inherited `test_atomic_reports_r27.py` | `251bb8a94141135cfd8f1b9bc1d5b1198e59359a` |

- R217 new: **17 / 17 pass** in normal mode and **17 / 17 pass** in optimized `-OO`.
- Combined R217 + R216 (21) + R27 (11): **49 / 49 pass** each in normal and `-OO`, **98 successful test-method executions**, zero failures/skips locally.
- `PYTHONWARNINGS=error`, `python -m compileall -q`: **pass**.
- Runs use synthetic data in disposable temporary directories. Tests cover hostile `__iter__` and exception payloads; incomplete or overlong tuples; string/list/generator pair inputs; rollback after 60 good rows; preserved signed report; uninvoked sanitizer; mapping-proxy/UserDict; UTF-8 BOM and deterministic Decimal evidence.
- CI workflow now calls R217 tests in normal and `-OO` on **both Ubuntu and Windows**; GitHub-hosted CI is **not** proof until both runners execute successfully. Full inherited repository suite and six-app end-to-end tests have **not** run locally.

## Release/QD hold

**Do not merge to production, publish executables, or un-gate premium files.** Before any public release: restore working GitHub Actions, run full repository test suite on Ubuntu/Windows, privately build six Windows x64 candidates, verify SHA-256, native Windows/Defender/EDR and Windows 11 keyboard/screen-reader/scaling acceptance, code signing/accurate unsigned disclosure, protected premium fulfillment, independent QD and founder approval.

The next highest-value action is repairing pre-step GitHub Actions failure (inspect run banner, billing/usage/policy, and runner allocation) and rerunning **this exact R217 head**, then executing full six-engine integration before any binaries are considered. No production or website changes in R217.
