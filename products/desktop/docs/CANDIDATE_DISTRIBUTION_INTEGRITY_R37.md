# R37 — six-application candidate directory and checksum custody

**Internal development / NOT a release authorization.** Applies to all four
free and two premium Windows x64 candidate EXEs. No new binaries or public
download links are produced by this sprint.

## Why this matters

The earlier release gate checked that the expected six `.exe` files were
present, structurally plausible and checksum-matched, but **did not reject
other files** in the same output folder. An accidentally included
premium-license key, stray script, malicious DLL, archived evidence file,
nested folder or hidden file could have been swept into a distribution
archive despite successful EXE checks.

R37 makes the candidate folder fail closed unless it contains **exactly
seven distinct ordinary files**:

- LedgerDiffLite.exe
- InvoiceTwinScout.exe
- SpendMapLite.exe
- PolicyDeltaDesk.exe
- GrantAuditStudioPro.exe
- ProcureGuardStudioPro.exe
- SHA256SUMS.txt

No other entries are accepted. Names are case-sensitive in the contract;
symlinks, hardlink aliases and directory entries are rejected. Every EXE
has a 512 MiB upper bound; the ASCII checksum inventory is capped at
4 KiB. Checksum bytes are read from a verified descriptor rather than
an unchecked pathname. Each binary is hashed with bounded streaming
and pre/post file identity checks. The seven-file allowlist is rechecked
at every existing pre-smoke/post-smoke integrity checkpoint, including
after the final smoke. No filesystem cleanup or deletion is performed.

This addresses accidental packaging of unrelated private files and
detects observed source changes during verification. It **does not** make
files immutable, guarantee prevention of all filesystem races, authenticate
a software publisher, replace malware scanning, or validate packaged
Windows executables without actually running the Windows gate.

## Operator workflow

From a trusted, clean Windows 11 x64 checkout, with dependencies
already installed:

```powershell
pwsh -File products/desktop/scripts/verify-windows-candidate.ps1 -Build
```

The script refuses a preexisting `dist` with `-Build` and builds six
candidate launchers. It runs the complete source regression suite,
creates the seven-file `dist`, executes the Windows candidate smoke
gate, then writes the **internal** JSON evidence to
`build/candidate-evidence/`, outside `dist`.

To check an already-built candidate, omit `-Build`, making sure `dist`
has only the six named EXEs and the checksum file. Do **not** copy
`offline-gate-*.json` or any licensing files into `dist`. GitHub Actions
similarly stores candidate evidence in `build/offline-candidate-evidence.json`
outside `dist`.

Run synthetic regression tests without Windows binaries:

```text
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_candidate_guard_r37.py' -v
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_candidate_gate_integration_r37.py' -v
```

The second suite uses synthetic PE structure and **mocked** Windows smoke
execution, never real EXEs. Windows handles cannot reliably be renamed or
written while open on all volumes; three injection tests explicitly skip
on Windows, rather than interpreting an OS file-sharing restriction as
proof of race resistance.

## Gates still outstanding

A passing source test or checksum verifier does **not** authorize release.
Before publication: full trusted Windows x64 source suite, six real native
EXE builds and smoke tests, malware and code-signing checks as applicable,
independent checksum verification, premium payment/entitlement/access checks,
site download verification, and explicit QD/human approval. These are
separate gates; do not publish the internal Actions artifacts.
