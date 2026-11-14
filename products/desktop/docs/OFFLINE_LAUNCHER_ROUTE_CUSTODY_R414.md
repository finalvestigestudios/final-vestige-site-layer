# R414 — Six-app source smoke launcher-route custody

**Scope:** Internal, offline, source-only development evidence for [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). This does **not** authorize release or certify any Windows executable.

## Why this matters

The existing R408–R413 offline source runner reported a launcher smoke as a pass whenever its subprocess returned status zero. A launcher that merely imported nothing (or a LedgerDiff launcher accidentally wired to the GrantAudit app ID) could therefore produce a passing green entry without ever running the intended product. Whole-source SHA-256 hashing only measured the wrong bytes; it did not verify the intended launcher-to-product mapping.

## R414 behavior

Before starting **any** of the 12 child processes, source inventory checks parse each of the six named launcher Python files using the standard-library `ast` parser, without importing or executing the file. A permitted launcher has an optional module docstring, exactly one `from fvs_suite.launcher import launch`, and one `launch("<expected-app-id>")` expression, either at module scope (synthetic tests) or inside a standard `if __name__ == "__main__":` guard (real launchers). The expected mapping is fixed by the six-product `PRODUCTS` table. Syntax errors, wrong app IDs (including free/premium swaps), absent calls, dynamic IDs, multiple calls, aliases, fake local functions and extraneous statements fail closed before any smoke subprocess starts. No private launcher code or path appears in the rejection text.

After that preflight, R413's full-import-root SHA-256 inventory, before/after-child digest continuity, Python `-I -B` isolation, restricted subprocess environment, stdout/stderr to `DEVNULL`, and 12 normal/optimized smoke checks remain unchanged. The developer result retains `release_authorized: false` regardless of source test success.

**Security boundary:** AST shape checking is not source authentication or a malicious-code sandbox. The imported shared launch function or underlying financial engine could itself be modified; only a trusted full Git checkout with independent CI can establish product behavior. A successful local source smoke does not prove a Windows x64 executable was built, installed, antivirus scanned, keyboard/NVDA tested, or that premium access controls deny unauthorized downloads.

## Reproduction (full trusted checkout)

```powershell
$env:PYTHONPATH = 'products/desktop'
python -W error -m unittest discover -s products/desktop/tests -p test_launcher_route_r414.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_launcher_route_r414.py
python -I products/desktop/offline_source_smoke_r408.py
```

On Linux use `PYTHONPATH=products/desktop` before each command. Do not interpret synthetic fixture checks as proof that the real engines or released EXEs passed. GitHub Actions runner failures before job execution must be fixed independently.

**Next release gates:** complete suite regressions against the trusted checkout on Windows and Ubuntu; genuine Windows x64 portable builds, launch/smoke tests, Windows Defender and NVDA/high-DPI checks; SHA-256 checksums, premium entitlement/download denial; independent QD and explicit founder approval. No artifact promotion or site publication in R414.
