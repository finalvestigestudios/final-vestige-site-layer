# Labs R103 — Windows toolchain custody and SQLite test-connection portability

**2026-11-01 UTC — DRAFT / RELEASE HOLD.** Stacked on R102 PR #412; no production, WordPress, payment, packaging policy, entitlement or artifact-publication change. All four free and two premium utilities remain **unreleased**.

## Exact-head predecessor evidence

[Actions #41279389788](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41279389788) at R102 commit `c337d9960e373be41d10da5d2ad8b73b487674d3`: Linux complete normal/`-OO` source gate **PASS**; Windows source inventory **135/135 tests and 71/71 source fingerprints PASS**. Windows mandatory normal-mode full unittest gate **FAILED: 3 assertion failures, 51 errors** in 11 source-owned test modules; optimized mode, packaging and six native EXE smoke were not reached. The diagnostics hide raw exceptions by design. No assumptions about each failure's cause are justified.

## R103 implementation

1. `scripts/toolchain_guard.py`: cross-view `Path.lstat()` versus `os.fstat()` intentionally ignores **only Windows creation-time metadata** (`st_ctime_ns`), the precise API mismatch confirmed in R101. Before/after **path-to-path** and **descriptor-to-descriptor** identities continue comparing **all seven** stat fields, including ctime. Cross-view comparisons still enforce device, inode, mode, nlink, size and mtime, alongside no-follow, ordinary singleton file, byte limits and SHA-256. This protects both installed toolchain fingerprints and toolchain manifest reads.
2. `tests/test_toolchain_windows_ctime_r103.py`: ten synthetic tests for Windows/Linux parity, retained field checks, cross-view/within-view mutations, verified file bytes, manifest reading and invalid input. Tests use temporary fake packaging inputs only; no real installer or entitlement is produced.
3. Four older license-registry test modules replace bare SQLite connection context managers with `closing(connect(...)) as db, db`, retaining transaction commit/rollback semantics but closing DB handles before Windows `TemporaryDirectory` removal. SQLite connections stay local and synthetic. This is a hypothesis-driven fix for Windows cleanup errors, **not a confirmed root cause** until exact-head CI.
4. A Policy Delta Desk test now checks backslash-escaped filenames via the actual diff formatter on Windows, which does not permit literal backslashes inside one file name; its original POSIX real-file test remains. No policy diff engine logic changed.

## Verification plan and release gates

Run `PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_toolchain_windows_ctime_r103.py' -v` and `python -OO` equivalent, plus existing R13–R16, R38, R47–R48, R56 and R76 tests. **Do not mark passing until actually executed.** Then require exact R57 **whole-suite normal and optimized on Linux and Windows**, all six engine source smokes, a Windows 11 x64 executable build, PE/AV/checksum/keyboard GUI and restricted premium entitlement verification, QD independent review and founder signoff. No public URL or distribution allowed before all gates.

Diagnostic caution: do not publish SQLite paths, private failure traces, fixture strings or customer financial records in CI. The release status must remain **HOLD** if a gate fails. Never merge directly to main; keep this PR draft on the R102 feature branch.
