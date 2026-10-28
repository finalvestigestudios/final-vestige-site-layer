# R9: runner-independent six-app Windows x64 candidate verification

**Scope:** six-app Final Vestige Labs suite only (four free + two premium). Branch `feature/labs-offline-exe-verifier-r9` is stacked on R8 and remains a **draft**. These checks never publish, merge, sell or license software.

## Why this exists

GitHub-hosted Actions jobs have repeatedly failed **before any steps**. A local verification path is needed so Windows x64 binary testing can proceed with evidence, without representing unreachable CI as a pass.

## Verification contract

`products/desktop/release_gate.py` is a standalone Python 3.12+ verifier requiring no external modules. Before any executable launches it:

1. Requires **exactly six** expected EXE basenames; rejects extra/missing binaries and symlinked binaries.
2. Requires strictly formatted `SHA256SUMS.txt`, exactly one lowercase 64-character SHA-256 digest for each named EXE; disallows paths, duplicate entries and unknown entries.
3. Validates each candidate's Windows `MZ` / `PE\0\0` header, AMD64 machine type and PE32+ format to reject mislabeled 32-bit, ARM and non-PE files.
4. Hashes the complete file and matches its inventory entry.
5. If and only if `--smoke` is requested **on actual Windows**, invokes every executable with `--smoke-test`, with a per-process timeout; any nonzero exit or timeout fails the gate.
6. Optionally writes a **new**, never-overwritten JSON report with the six verified checksums, smoke results and explicitly false release/signing/licensing flags.

The gate is deliberately not a code signature validator, malware scanner, customer-privacy certification, sandbox escape test, clean-machine GUI/keyboard test, premium entitlement system or deployment approval.

## Run from a local Windows x64 clone

Requirements: Python 3.12+, Tkinter, `cryptography==46.0.4` and `pyinstaller>=6.12,<7` already installed in a trusted environment (install dependencies only after independent package review). Use PowerShell from repo root:

```powershell
# First run engine tests and build the six portable binaries, then smoke them.
.\products\desktop\scripts\verify-windows-candidate.ps1 -Build

# To verify an existing dist folder without rebuilding:
.\products\desktop\scripts\verify-windows-candidate.ps1

# Run cross-platform integrity checks only (NO executable execution):
python products/desktop/release_gate.py dist --report candidate-integrity.json

# Run the synthetic verifier tests on any Python 3.12+ host:
python -m unittest discover -s products/desktop/tests -p 'test_release_gate_r9.py' -v
```

The local script rejects an existing `dist` directory when `-Build` is requested to avoid silently deleting or reusing prior artifacts. Candidate files are **not** automatically copied to any public folder. The JSON report can be reviewed as CI-independent evidence, but it does not prove clean Windows security/AV or QD approval.

## Residual release gates

- Full actual suite integration on a clean Windows x64 host; inspect report and separately assess GUI accessibility, file permissions, antivirus/SmartScreen and signed-file provenance.
- Premium purchase/entitlement-controlled distribution and legal terms.
- QD review of the exact chain of stacked PRs, candidate source SHA, outputs and tests; **no merge to main or production** until approval.
- No customer confidential data in pre-release test fixtures.

For tracked releases, archive candidate source commit, report SHA-256, exact external Windows environment and final binary hashes separately. A passing R9 verifier is **not** permission to publish.
