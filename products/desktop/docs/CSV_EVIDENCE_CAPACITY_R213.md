# R213 — bounded financial CSV evidence publication

**Status: DRAFT / HARD RELEASE HOLD.** Tracks [Labs issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on the exact R212 commit `2512f24058e34b8c58e7fa073d98efb2103a8509` (draft PR #1113), never on production `main`.

## Reproduced defect and impact

The shared CSV exporter accepted an arbitrary `fields` iterable, iterated arbitrary `Mapping.items()`, and streamed rows until source exhaustion. A malformed or unbounded header or items generator could exhaust process memory; an endless row generator could fill the export disk without publishing usable evidence. This matters for local-first financial review, where incomplete output must never be mistaken for an audit artifact.

Using the **exact R212 writer blob** `ad9e1aec5f89bd1ebebc8ae20ea18e6a88806e4a` and synthetic local data, **257 unique headers** were published when all keys were present; a row with **257 keys** was accepted and the extra data ignored; **200,001 report rows** were published. The baseline had no finite cap. We did not run truly infinite iterables against the baseline.

## Production change

`fvs_suite.atomic_reports.write_csv_report` now enforces:

- **256 columns maximum** for report schema and each row mapping (including extra ignored keys).
- **200,000 rows maximum** per report, matching the existing source-import row ceiling.
- Bounded `itertools.islice(..., LIMIT + 1)` iteration, so infinite schema or custom `Mapping.items()` generators cannot force unbounded accumulation. Limits are checked before rendering more untrusted values.
- The 200,001st row is rejected **before** value conversion; staged files are removed, and previously published reports remain untouched.
- Static `ValueError` messages containing no supplied financial values. R212 private callback/iterator exception redaction, CSV formula protections, native-string mapping keys, atomic non-overwriting publication, UTF-8 BOM, exact Decimal string values and human review are preserved.

The limit applies to the direct shared-export API even when called outside the six application import engines. For genuine reports exceeding these limits, the correct response is to stop and design reviewed, verified partitioning and a manifest — **not** silently truncate or raise the cap without a tested policy.

## Actual locally executed verification — 2026-11-05 UTC

Environment: Linux x86_64 / CPython 3.13.5; isolated test folder with the **exact upstream R212 writer** as baseline, then byte-identical proposed R213 writer, new tests, inherited R212 tests and inherited R27 tests. Only synthetic financial rows, no internet or actual customer data.

Source-control blob custody:
- R212 baseline writer: `ad9e1aec5f89bd1ebebc8ae20ea18e6a88806e4a`
- R213 proposed writer: `b266cc29ae5e3186e3804d78c2593880ae02d044`
- R213 new 15-case test file: `e1abe29b44291ca08a2840255d45a632290bf31d`
- Inherited R212 tests: `5faf96f3cf779305e57f91e526db47cf0fb3a2f0`
- Inherited R27 tests: `251bb8a94141135cfd8f1b9bc1d5b1198e59359a`

Command, from the isolated folder:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_atomic_*.py' -q
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_atomic_*.py' -q
python -m py_compile products/desktop/fvs_suite/atomic_reports.py
```

Results: R213 new **15/15**, R212 inherited **16/16**, R27 inherited **11/11** = **42/42 PASS normal** and **42/42 PASS `-OO`**, **84/84 method executions total**, no local skips; Python compilation PASS. Normal and optimized modes treated warnings as errors. 200,000-row positive boundary, 200,001-row negative boundary, infinite generator short-circuit, 256/257 schema and row-key boundaries, safe private errors, rollback after late failure, existing evidence protection, Decimal 0.10 roundtrip, BOM, interruption propagation, symlink and POSIX private-permission tests were covered.

The red-phase observations against R212 were bounded, finite reproductions (257 columns; 200,001 rows), not a full red test-suite run. R213 tests intentionally import newly introduced limit constants, so they do **not** import unchanged against R212.

Both Ubuntu and Windows `.github/workflows/desktop-build.yml` jobs have a dedicated **15-case** R213 step in standard and optimized Python. Windows guards each exit status. Tests suppress output rather than exposing financial fixture data in hosted logs.

## Limitations and exact next gate

- This was **not** a full-repository integration run or native Windows x64 build. The 42-case targeted run used an isolated, source-identical reconstruction; GitHub-hosted CI must execute on both OSes before any production/release claim.
- Most recent R212 hosted Actions [#42061912268](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42061912268) failed with Ubuntu and Windows jobs exposing **no verifiable steps**; the account/runner cause has not been established.
- No executables were built, scanned, signed, accessibility-tested or published. Protected Pro entitlement and download controls, independent QD approval and founder authorization are still required.

**Smallest owner unblock:** inspect the GitHub Actions run failure banner, billing/usage and runner availability, restore execution, and rerun the **unchanged R213 commit** on Ubuntu/Windows. Then run the complete inherited six-app suite, validate source-to-export flows, build/scan/checksum six private Windows x64 artifacts, perform physical Windows 11 accessibility and premium entitlement acceptance, obtain independent QD review, then request founder approval. **Do not merge or distribute until gates pass.**
