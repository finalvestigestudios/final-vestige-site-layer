# R109 — checksum-bound **private** Windows 11 manual accessibility acceptance

**2026-11-01 · Issue #73 · Draft / RELEASE HOLD.** Stacked on R108 draft PR #436 at exact parent `58226816d56b23bab277d755487f0f810865fb3c`. This adds a human-review evidence workflow; it is not a code-signing, manual-test, malware-clearance, publishing, licensed-premium, or release authorization feature. No site/CMS/production change.

## The missing gate

R105 proves the six real Windows x64 EXE windows/locked dialogs open on a hosted Windows runner; R106–R108 prove source-Tk keyboard, scaling and synthetic accelerator behavior. None establishes **physical Windows 11** keyboard, NVDA, high-contrast or DPI behavior. Worse, informal manual checklists can accidentally be attached to **the wrong build**. R109 makes the internal human-review checklist reproducible and binds it cryptographically to one actual set of six candidate executables **without uploading binaries or customer data**.

## Executed scope

- `scripts/windows11_manual_acceptance_r109.py` independently re-runs the existing `release_gate.verify(dist, smoke=False)` PE/checksum verifier against actual on-disk candidates; rejects wrong/missing/extra binaries and hash changes. Separately validates an **R9 report with real native Windows AMD64 smoke status and all six passed smoke records**; rejects simulated or unverified smoke claims. It cryptographically binds review JSON to the exact R9 report **bytes**, `SHA256SUMS.txt` digest, and each executable's SHA-256.
- It emits a **new-file-only** UTF-8 review template, initially **46/46 NOT_RUN**, not a faux certificate. Four free tools have 8 Win11 manual checks each (packaged window; physical Tab/Shift+Tab; physical shortcuts; native picker cancellation; NVDA accessible name/reading order; high contrast; real 200% and 400% scaling). The two **still-locked** premium products have 7 checks each (no-entitlement lock; no editor/files; keyboard-accessible lock; NVDA locked dialog; contrast; real 200%/400% scaling). It **never launches/unlocks** premium editors.
- Independent reviewer records `reviewer_id` (nonidentifying operator handle), actual Windows 11 build number >=22000, observed UTC in last 30 days, and PASS/FAIL/NOT_RUN for each named check. Each reported PASS **or FAIL** requires a distinct existing local UTF-8 witness note (64–32768 bytes) named `<ProductWithoutExe>--<check>.txt`, with the note's SHA-256 recorded in the review JSON. Read-only validator rejects missing/altered/linked/hardlinked notes, duplicate JSON keys, unexpected apps/checks, stale observations, fake WinServer build, malformed digests, synthetic smoke, and swapped candidate hashes.
- Output is only **counts**, never customer paths, witness contents or screen-reader transcripts. A complete 46/46 score means only `MANUAL_MATRIX_COMPLETE_UNCERTIFIED`, with `release_authorized: false` and `premium_editor_licensed: false`. **Reviewer declarations and witness-note hashes cannot prove independent human observation**, so this can never bypass QD or issue licensing authority.
- `tests/test_windows11_manual_acceptance_r109.py`: **33 synthetic adversarial test cases**, executed with normal Python and optimized `-OO`; all fixtures are synthetic, not actual product GUI or human reviews. Two-platform focused tests are mandatory in desktop CI. No R41 artifact upload paths changed; no executables/evidence notes uploaded.

## Reproduce on an authorized, trusted Windows 11 x64 machine only

Use a **private** exact-head source checkout and **locally generated six-EXE R9-smoke-passing artifact directory and report**; never assume the hosted CI's unuploaded EXE bytes are accessible. Fresh local rebuilds have their **own** candidate hashes and must be reviewed with their **own** R9 report. Keep witness notes **outside** the build directory, offline, nonidentifying, containing no customer statements, financial data, secrets or private screenshots.

```powershell
$env:PYTHONPATH = "products/desktop"
python -m unittest discover -s products/desktop/tests -p 'test_windows11_manual_acceptance_r109.py' -v
python -OO -m unittest discover -s products/desktop/tests -p 'test_windows11_manual_acceptance_r109.py' -v
# After the 6 private x64 candidates and exact R9 smoke report exist:
python products/desktop/scripts/windows11_manual_acceptance_r109.py template `
  --dist dist --r9-report build/offline-candidate-evidence.json `
  --review C:\PrivateQA\win11-review.json
# Reviewer independently performs the actual tests and fills the template and
# private note hashes. A check's witness filename uses the exact check key.
python products/desktop/scripts/windows11_manual_acceptance_r109.py verify `
  --dist dist --r9-report build/offline-candidate-evidence.json `
  --review C:\PrivateQA\win11-review.json --witnesses C:\PrivateQA\witnesses
```

**Interpretation:** a missing witness, a changed candidate, a modified R9 source report, wrong OS/version or invalid data results in `HOLD`, never a release certificate. A valid but incomplete or failed checklist emits `REVIEW_HOLD_INCOMPLETE_OR_FAILED` and exit 2. A declared complete checklist emits `MANUAL_MATRIX_COMPLETE_UNCERTIFIED`; even this requires independent manual QD confirmation, separate AV/EDR scan, code-signing/SmartScreen resolution, authentic premium entitlement issuance and restricted paid distribution tests, and explicit founder approval. Do **not** include generated review records or witness notes in CI artifacts or source control.

## Test evidence and remaining blockers

Before PR: locally executed synthetic checks **33/33 normal PASS, 33/33 optimized `-OO` PASS** in isolated Linux Python 3.13. This **is not** a Windows 11 runtime test or an actual R9 source-verified executable review. Exact-head GitHub Actions must independently confirm source tests on Linux and Windows. Windows 11 private QA + AV + premium commerce and QD approvals remain separate **HOLD** gates. The production site, all six premium/public downloads and source-of-truth data remain untouched.

**Smallest unblock for actual manual validation:** an independent reviewer with one trusted, isolated **Windows 11 x64** QA system and the six private checksum-pinned EXEs plus matching local R9 evidence. They run the 46 checks, retain only private source-safe notes and return a redacted status/count summary and hash attestation for independent QD signoff.
