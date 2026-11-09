# R299 — Policy Delta Desk private-file intake boundary

Status: **DRAFT / not released / independent QD and founder approval required**. Scope: `products/desktop/fvs_suite/policy_diff.py` and new `policy_input_privacy.py`; no finance, entitlement, packaging, site or compliance-decision changes.

## Actual defect

The old `_read_policy` called `Path(path)` and `is_file()` outside its sanitized snapshot logic, so expected OS errors could expose a confidential policy path. It also raised sanitized snapshot `ValueError` *inside* `except ValueError` using `from None`; the previous exception remained accessible at `__context__`, including private filenames. Invalid UTF-8 was raised `from exc`, retaining a `UnicodeDecodeError.object` that can contain the entire private source.

## Implemented

- `checked_policy_path`: bounded TXT/MD/CSV file-selection diagnostic; catches expected PathLike/probe failures and raises only after the handler. Preflight is **not** an authorization, file lock, or TOCTOU defense.
- `read_policy_snapshot`: continues to use the **unchanged** descriptor-owned snapshot with 10 MiB policy cap; maps only the exact known snapshot oversize sentinel to the policy size message. All other routine `ValueError` / `OSError` failures are sanitized outside the handler, with no original `__context__` or `__cause__`.
- `decode_policy_utf8`: preserves `utf-8-sig` and original raw SHA-256 evidence without chaining undecodable confidential bytes. Interrupts and `MemoryError` still propagate.
- Rewired `_read_policy`; text control filtering, physical line citations, diff algorithm, source digest, report publication, and **mandatory human interpretation** remain unchanged.

## Evidence and reproducibility

Executed against **Git SHA-identical local copies** of `policy_input_privacy.py` and its 21-method regression module on Linux CPython 3.13.5:

```sh
cd products/desktop
python -W error -m unittest discover -s tests -p 'test_policy_input_privacy_r299.py'
python -OO -W error -m unittest discover -s tests -p 'test_policy_input_privacy_r299.py'
python -m py_compile fvs_suite/policy_input_privacy.py tests/test_policy_input_privacy_r299.py
```

All **21/21 normal** and **21/21 -OO** methods passed (**42 focused executions**). Tests cover normal paths, TXT/MD/CSV, inaccessible PathLike/probes, hidden exception chains, exact/nonexact oversize messages, OSError filenames, BOM/invalid UTF-8, immutable originals, and interrupt behavior.

An additional **9 full-`policy_diff` integration tests** were committed to `test_policy_reader_integration_r299.py` but **not run** in the isolated environment; those must pass on a complete repository checkout. Prior-pattern negative control independently reproduced two vulnerabilities (explicit UTF-8 cause retained raw bytes; `from None` retained a private `PermissionError.filename`). This is not an end-to-end Windows acceptance claim.

## Open gates / next highest-impact step

The repository's latest R298 GitHub Actions run had Ubuntu and Windows jobs marked failure with no runner or recorded steps. Investigate GitHub Actions billing/spending restrictions, workflow enablement and runner allocation; rerun this unchanged SHA. Run full normal/`-OO` suites and source smoke on Ubuntu and Windows, including 9 new integration tests. Then gated Windows 11 x64 executable smoke, SHA-256, Defender, accessibility, and licensed premium distribution review. **No binaries or public premium URLs authorized.**
