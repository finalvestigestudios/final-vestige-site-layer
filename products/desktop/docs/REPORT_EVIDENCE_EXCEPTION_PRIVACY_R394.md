# R394 — Private release-evidence error boundaries (six-app desktop suite)

**Status: DRAFT / NOT RELEASED / QD + FOUNDER HARD HOLD.** This is source-level custody/privacy work only. It neither approves a Windows executable nor verifies malware, Authenticode, premium licensing, download controls, financial correctness, or actual user-facing accessibility.

## Scope and threat

All six launchers share `release_gate.main` → `report_evidence.prepare_report_path` / `publish_report` → `report_link_witness_r338.verify_published_link`. An unexpected failure from resolving a local private path, adopting a staging file descriptor, filesystem sync, JSON encoding, hardlink publication, or hardlink readback could be caught by a handler that raised `ReportEvidenceError(... ) from None` (or `LinkWitnessError(... ) from None`). In Python that suppresses displayed traceback chaining but **retains the original exception object in `__context__`**. The public message may have been generic, while callers or aggregators could still inspect the private underlying error. No real customer data was used in this sprint.

R394 now records the failure in the handler, allows the original exception handler and owned descriptor cleanup to finish, then constructs a fixed, path-free public exception **outside** the handler. Preserves deliberate `KeyboardInterrupt` / `SystemExit` propagation; does not turn failed custody checks into success.

## Code

- `products/desktop/report_evidence.py`: redact destination-preflight faults, fdopen adoption errors, staging read/write/sync faults, JSON/temporary-file/hardlink failures and witness failures without retained exception chaining.
- `products/desktop/report_link_witness_r338.py`: redact unexpected `os.stat`, `os.open`, `os.fstat` and `os.read` failures outside their handler; retain descriptor cleanup and rejection semantics.
- `products/desktop/tests/test_report_private_exception_custody_r394.py`: 19 self-contained synthetic and temporary-filesystem tests for failure privacy, exact-byte report publishing, no overwrite, kept forensic stage, file-descriptor cleanup, and interruption semantics. Test never executes an EXE.
- `.github/workflows/desktop-source-evidence-r385.yml`: require normal and `-OO` R394 suite on independent Ubuntu and Windows jobs before source evidence can be considered green.

**Known limitations:** The stage and destination remain on disk after a late witness failure by design for manual custody review; this is NOT permission to publish them. This patch does not claim atomic security against every malicious same-user filesystem race, nor does it validate native Windows hardlinks/junctions until a genuine runner executes. All data stays local, with no telemetry and no customer uploads.

## Executed evidence (2026-11-12 PT)

Local Linux Python, `PYTHONPATH=.` from `products/desktop`:
```sh
python -W error -m unittest discover -s tests -p test_report_private_exception_custody_r394.py
python -OO -W error -m unittest discover -s tests -p test_report_private_exception_custody_r394.py
python -m compileall -q report_evidence.py report_link_witness_r338.py tests/test_report_private_exception_custody_r394.py
```

**19/19 normal + 19/19 optimized = 38/38 PASS**, source compilation PASS. The three locally executed Python files were independently SHA-verified against the Git blob IDs on the R394 branch: `report_evidence.py` `9be470188b37897043c018c83efa4b9d12ca49e0`; `report_link_witness_r338.py` `1b8b3338d88205ed0c364e15ed5f57230f257dae`; `test_report_private_exception_custody_r394.py` `8a7dd7732fde43ce4a60fb5ecbb25d8d06109d2b`. The local three-file execution is **not** a full repository test, complete inherited-suite pass, native Windows test or packaged-executable scan.

## CI, approvals, and next step

R393 exact-commit independent source run [#43363048854](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43363048854) and desktop build run [#43363048844](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43363048844) failed before recording test steps. The cause is **unknown**; owner must inspect Actions check annotations, billing/spending caps and runner allocation. R394 hosted test status must be independently checked against the R394 exact commit; no local pass is a substitute.

Next highest-impact action: restore hosted Windows/Ubuntu runners and execute the exact R394 commit against the full six-engine, Decimal/provenance, authentic AES-GCM, Ed25519/SQLite, and release-candidate test suites. Follow with actual Windows x64 EXE/install smoke, Defender/EDR, keyboard/screenreader, checksums, and authenticated premium delivery. **No merge into `main`, website publishing, license issuance, binary release or unrestricted premium download** without independent QD review and explicit founder approval.
