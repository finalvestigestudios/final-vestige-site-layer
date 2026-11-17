# Labs R488 — offline source subprocess descendants and stdin custody

**Status:** DRAFT / QD HARD HOLD. Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). R488 is stacked on R487 draft #2820, **not production main**. This is an operator-run, source-only fallback, never executable release approval.

## Gap and functional change

R487 killed its **direct** Python test child on an output flood or timeout, but a child could launch a grandchild that inherited the source-test stdout/stderr pipe. If the original child exited first, a lingering grandchild could keep that pipe open and outlive a reported BLOCKED result. R487 also inherited the operator's stdin by default, permitting test scripts to consume piped local private data or block on input.

The R488 modification to products/desktop/offline_source_gate_r485.py:

- Passes stdin=subprocess.DEVNULL to every source-check child. Unattended tests receive immediate EOF instead of inheriting local operator input.
- On POSIX, starts every test child in a new session/process group. On timeout, log overflow, reader failure, or inherited-pipe stall, sends SIGKILL to that process group before final reaping. A pipe still held by a grandchild remains **BLOCKED**, never PASS.
- Preserves R487's 1,048,576-byte combined output cap, canonical unittest footer validation, two Python modes, credential scrubbing, private-path-free JSON evidence, and release_authorized=false.
- On Windows, only the direct-child kill fallback is implemented. **Do not claim Windows descendant teardown or Windows x64 distribution acceptance.** Detached child sessions/processes are not contained on POSIX either. This is not a security sandbox or network isolation.

## Local execution evidence, scope and provenance

Locally executed on **Linux, CPython 3.13.5**, using source and new test bytes confirmed against the GitHub blobs:

- Source file blob SHA: 39ddda3024baae962d3e28a39a6a6e73a2060375.
- New regression test file blob SHA: d5e62ceb323bcef757a2aa0e2c0a2237312c9b54.
- Standard: python -B -W error -m unittest discover -s products/desktop/tests -p test_offline_source_descendant_custody_r488.py — **8/8 PASS**, ~21.5s.
- Optimized: python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_offline_source_descendant_custody_r488.py — **8/8 PASS**, ~21.2s.
- Both Python files compiled successfully.

The new tests use real spawned Python child and grandchild processes with synthetic data: no inherited stdin, unchanged canonical stderr receipt, isolated POSIX process group, orphaned stdout pipe treated as BLOCKED, grandchild stopped on overflow and timeout (checked with delayed marker files), no private error disclosure, and no release approval. Five POSIX-specific methods are intentionally skipped on Windows; Windows child-tree termination needs separately reviewed implementation and native validation.

**Limitations:** These 16 method executions do **not** test all four selected production test modules in a complete trusted checkout, do not run the inherited R485–R487 test files, and do not establish passing GitHub Actions, Windows EXEs, Windows Defender, package checksums, accessibility, licensed downloads, or QD approval.

## Operator/CI follow-up

The source-evidence workflow now requests this new module in standard and optimized modes on Ubuntu and Windows. The pre-existing GitHub Actions blocker must be resolved before hosted evidence can count. Repo owner should inspect job failure annotations, billing/spend limits, runner eligibility and workflow permissions. Then run source regression suites from a complete trusted checkout, all six application engines, native Windows x64 packages and smoke/Defender/SHA-256 checks.

No deploy, merge, website publication, unrestricted premium artifact, automated compliance decision, or founder approval is implied.
