# R10: fail-closed Windows smoke integrity and optimization-safe checks

**Scope:** the separate six-product Final Vestige Labs Windows x64 desktop suite tracked in issue #73. This change is stacked on R9 and does **not** merge, publish, charge, license, or deploy anything.

## Threats addressed

1. **Assertion optimization:** Prior packaged self-tests used 30 Python `assert` statements. Python `-O` or `-OO` removes assertions, so a future optimized PyInstaller build could report success despite broken reconciliation/export checks. All 30 checks now use an explicit raising function `_check(...)`. Its behavior is tested in compiled `optimize=2` mode and source AST is checked to contain no `ast.Assert` nodes.
2. **Executable mutation during smoke:** A candidate binary (or another process) could change one executable or `SHA256SUMS.txt` after the initial hashes were verified, while the verifier continued to report success. R10 revalidates all six executables and the checksum inventory immediately before and after **each** synthetic executable smoke invocation, plus a final comparison. Any mismatch, deleted file or symlink substitution fails closed. The original pre-execution all-six hash gate remains intact.
3. **Unbounded output capture:** Previously, `subprocess.run(capture_output=True)` buffered arbitrary stdout/stderr from each executable, potentially exhausting verifier memory or retaining diagnostic data. R10 redirects executable smoke output to `DEVNULL` and records only exit status/duration. For debugging, explicitly execute a trusted candidate in a disposable Windows test VM; avoid entering customer data.

## Tests

`products/desktop/tests/test_release_hardening_r10.py` adds eight regression tests:

- clean six-binary synthetic gate and output redirection;
- executable self-modification despite zero exit;
- modification of another executable before it launches;
- checksum inventory mutation;
- symlink replacement;
- integrity-only evidence remains explicitly non-authoritative;
- `_check` survives `optimize=2`, without `ast.Assert`;
- Python-level synthetic workflows for **all six** applications (includes premium human review and AES-GCM backup).

The workflow also runs R10 tests under `python -O`. Existing R9 tests remain part of the primary suite.

From a *trusted* checkout with Python 3.12+ and `cryptography==46.0.4`:

```bash
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_release_hardening_r10.py -v
PYTHONPATH=products/desktop python -O -m unittest discover -s products/desktop/tests -p test_release_hardening_r10.py -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
```

On a real Windows x64 host, after a clean release candidate has been built and checked:

```powershell
.\products\desktop\scripts\verify-windows-candidate.ps1 -Build
```

## Remaining release limits

- Python-level synthetic tests and mocked PE headers do **not** prove packaged EXE functionality. A passing exit code plus hashes does not establish that software is benign, signed or suitable for customer files.
- Hashing before/after execution detects persistent modification but does not prevent an actively malicious process from manipulating its own files and restoring them between checks. Never run untrusted candidate binaries; use isolated test machines.
- GitHub-hosted Windows jobs repeatedly failed before starting any steps as of October 28, 2026; runner eligibility/account setup must be investigated. Do not interpret pre-step failures as product test failures.
- Actual Windows 11 x64 clean-machine GUI/keyboard tests, source SHA provenance, signing, AV scans, premium entitlement/payment gating, customer pilot acceptance and **QD authorization** remain mandatory.

No product has been released or approved for release by this change.
