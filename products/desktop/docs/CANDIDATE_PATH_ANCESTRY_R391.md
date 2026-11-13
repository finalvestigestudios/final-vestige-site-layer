# Labs R391 — lexical candidate ancestry custody (draft; issue #73)

## Reproduced source defect

The R390 reader correctly rejected a symlink/reparse **at the final candidate path** or final staging-root path, but did not inspect the *intermediate parent components*. On Linux Python 3.13.5, an exact copy of the R390 candidate reader (Git blob `1abc758dd235d69b07cf492252af487dc18b1e9d`) accepted both:
- `sha256_candidate(alias/stage/LedgerDiff-Lite.exe)` with an ordinary final file reached through symlinked `alias`;
- `check_candidate_directory(alias/stage, ...)` with an ordinary final staging directory reached through that same symlink.

This is a **pathname custody weakness**, not proof of malicious code or a successful bypass in any distributed executable. All demonstrations use temporary synthetic non-executable data.

## Implemented boundaries

- New `candidate_path_ancestry_r391.py` walks all lexical parent directory components with `lstat`, never `resolve`; rejects symlinks, non-directories, missing metadata, `..` traversal and (on actual Windows) any ancestor with `FILE_ATTRIBUTE_REPARSE_POINT` or unknown attributes.
- Snapshot includes directory identities and timestamps. Shared `candidate_guard._inspect` compares ancestry both before opening and after finishing the descriptor read for **every** candidate EXE and SHA256 inventory read.
- `check_candidate_directory` validates ancestry before enumerating and after verifying all staged members, and rechecks the staging directory's identity itself. A changed or redirected parent cannot silently yield a successful result.
- Errors use fixed, non-sensitive messages; no originating filesystem exception is retained in the public exception chain. No files are deleted or modified by the guard.
- Existing SHA-256, size limits, no-hardlink, seven-file allowlist, R390 reparse guard, and no automatic product/compliance approval remain unchanged.

These checks are path-based snapshots, not an atomic filesystem transaction: a sufficiently privileged attacker could attempt an unobserved rename/replacement between inspections. Windows native junction/reparse testing and externally controlled staging directory hardening are still needed.

## Executed verification (local, not hosted)

Environment: Linux CPython 3.13, synthetic files and temporary directories. Test modules: `test_candidate_path_ancestry_r391.py` (**20** methods), `test_candidate_path_integration_r391.py` (**13** methods). The existing R390 candidate reader and reparse helper were reconstructed to their **exact** Git blob SHAs `1abc758dd235d69b07cf492252af487dc18b1e9d` and `fb2dc7106489e35f2ae12239878ed15bfc862f08`, then the R391 integration patch was applied locally.

Commands:
```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_candidate_*r391.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_candidate_*r391.py'
python -m compileall -q products/desktop/candidate_path_ancestry_r391.py products/desktop/candidate_guard.py products/desktop/tests/test_candidate_path_ancestry_r391.py products/desktop/tests/test_candidate_path_integration_r391.py
```

Result: **33/33 PASS** in normal mode, **33/33 PASS** optimized, **66/66 executions** total; compilation PASS. Executed source Git blobs, verified after push: `candidate_guard.py` `6c7040cf7a14bb2bec0c1face172053ca2630772`, ancestry helper `bb1c092cca980c31f141e25ab56e007951574b4e`, 20 tests `9793dcd9f6917da7e5a35458fe6a4a6e7e6378f8`, 13 integration tests `d5aaede1a4a6a351219332638a22af9da9a2f78f`.

The separate read-only Ubuntu/Windows source workflow now requires both test modules in normal and optimized Python before running its existing synthetic six-engine, Decimal/provenance, AES-GCM and Ed25519 gates. **CI running was not verified locally**.

## Release/approval hold

The six apps — LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, ProcureGuard Studio Pro — remain unreleased. This PR is stacked on R390, not production `main`; no Windows EXE was built or scanned here, no premium file uploaded, no licensing changes, no WordPress publishing. Full checkout integration, genuine Windows x64 filesystem/junction and executable acceptance, Defender scan, accessibility, protected premium distribution and independent QD/founder signoff remain mandatory.

**Highest-impact next action:** inspect GitHub Actions check annotations, billing/spending/runners to restore pre-job runner assignment, then execute exact R391 Windows/Ubuntu CI and a native Windows x64 junction fixture before any merge or distribution.
