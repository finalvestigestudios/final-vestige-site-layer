# R102 — Windows descriptor/path identity parity without weakening release gates

**2026-10-31 (PT) / 2026-11-01 (UTC). DRAFT. RELEASE HOLD.** Tracks issue #73; stacked on R101 PR #406, isolated in draft PR #412. No production merge, desktop distribution, premium entitlement activation, WordPress change, or QD approval.

## Actual Windows evidence that motivated this change

Hosted Windows Python 3.12 reported an `st_ctime_ns` disagreement **between pathname `lstat` and open-descriptor `fstat`** for unchanged source and test files (R101 [Actions #41275007459](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41275007459), `START_MASK_64`). On Windows this field describes creation time and need not coincide between the two API representations; on Linux it is the metadata-change timestamp. R101 handled this **only** for source fingerprints. Other independent readers still made the same seven-/five-field cross-API equality assumption.

With the full inventory repaired, the R101 Windows mandatory R57 source suite had **80 failures and 315 errors**; Linux normal/-OO and six Python engine smokes passed. This is a symptom count, not 395 independently diagnosed engine defects. R102 targets one cross-cutting platform condition without suppressing source tests.

## Code changes and protection retained

- `fvs_suite/csv_snapshot.py`: exact snapshot for all six financial engines, with Windows cross-API ctime parity; complete pathname-to-pathname and descriptor-to-descriptor checks remain.
- `candidate_guard.py`: independent SHA-256 stream for six staged binary candidates and the checksum manifest. Symlinks, hardlinks, size limits and before/after metadata checks remain.
- `fvs_suite/manifest_guard.py`: evidence inventory hashes and whole-inventory recheck use **path-view identity**; descriptor bytes/timestamps remain independently checked.
- `scripts/build_input_guard.py`: private signed-build-input custody manifest is read with separate cross-view and full within-view identity comparisons, never treating the manifest as release approval.
- `fvs_suite/review_lock.py`: the two premium apps' exclusive human-decision writer lock captures separate pathname and descriptor baselines, maintains complete per-view ctime tests, refuses replacements/aliases and never removes someone else's lock.
- `fvs_suite/journal_io.py`: the two premium human-decision journals preserve full pathname and fd identity across reads and append verification; no decision is appended until the human-review verification callback succeeds.
- `report_attestation.py`: private Windows build evidence report read retains full within-view identity checks and exact content SHA256.

These changes do **not** change Decimal parsing/arithmetic, financial matching scores, permission decisions, local-first retention, offline Ed25519 issuer trust, release permissions or independent QD governance. None permits a Windows executable to bypass the mandatory normal/-OO Python source tests.

## Regression coverage

`tests/test_windows_fd_ctime_parity_r102.py` adds synthetic and real-file tests for allowed **Windows-only cross-API ctime** differences, Linux strict ctime, other dev/inode/size/mtime rejection, same-view tampering, offline CSV source snapshot, candidate and evidence SHA-256, private license/build manifest custody, exclusive lock, journal append and failed validation, and report attestation. Three existing regression modules use Windows-legal bidi source filenames to preserve their adversarial Unicode rendering test instead of attempting POSIX-only tab/LF file names.

Run the full committed R57 gate on **both** hosted platforms at the exact final PR head:

```bash
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p 'test_windows_fd_ctime_parity_r102.py' -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_windows_fd_ctime_parity_r102.py' -v
PYTHONPATH=products/desktop python products/desktop/scripts/offline_source_gate.py
```

The diagnostic-only R100/R101 probes **cannot** authorize packaging or downloads.

## Measured intermediate CI (nonfinal heads; do not treat as final proof)

- R101 Windows: 80 failures / 315 errors; Linux PASS; no binary packaging.
- [R102 Actions #41278742164](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41278742164): Windows 35 failures / 257 errors; Linux full source PASS. Partial initial correction.
- [R102 Actions #41278890022](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41278890022): Windows 17 failures / 124 errors; Linux full source PASS. Additional inventory+custody correction.
- [R102 Actions #41278971744](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41278971744): Windows 19 failures / 119 errors; Linux full source PASS. Further fail-closed review-lock changes.
- Later heads add the journal, exact report reader, regression fixture corrections and source/rights documentation; their *own* exact-head CI must pass before reporting success.

## Next highest-impact gate

1. Inspect final-head Windows R57 failure markers **without displaying private fixtures**; reproduce failing methods on trusted Windows 11 x64, fix remaining shared platform causes on a draft PR, rerun both full Python modes and six source smokes.
2. Only after source gate passes: build all six Windows x64 executable candidates in the private CI job, verify PE architecture, actual start/GUI/keyboard/screen-reader paths, SHA-256, AV and license/premium entitlement access. Keep paid binaries off unrestricted URLs.
3. Submit independent QD exact-head review and founder release approval. Nothing is released and no real download URL is claimed until those controls pass.
