# R110 — per-check bound private Win11 witness evidence (draft, release HOLD)

**2026-11-01 · Issue #73 · Based on R109 draft PR #437.** This change addresses a concrete gap in the 46-check physical Windows 11 matrix: R109 hashed each witness note but did **not** verify that the note itself named the intended product, check, reviewer, executable hash or conclusion. A generic/reused note could therefore satisfy the digest field of another check after accidental copy-and-paste or manual rehashing. R110 refuses that mismatch. It does **not** prove a human physically completed the checks.

## What changed

`products/desktop/scripts/windows11_manual_acceptance_r109.py` now insists on **one versioned, private, UTF-8 JSON witness per claimed PASS or FAIL**, named `<ProductWithoutExe>--<check>.json`. The witness is matched to its corresponding review record on **all** of these fields: fixed schema, exact app EXE filename, test key, PASS/FAIL state, current executable SHA-256, full R9 report SHA-256, reviewer handle, real Windows 11 build number and declared UTC observation time. The note must also contain a detailed free-text observation (80–4096 non-whitespace characters), without NUL, disallowed control bytes or Unicode bidirectional formatting overrides. Every byte is still covered by the review's per-note SHA-256.

These checks are performed **after** the existing R109 six-executable PE/checksum/R9 custody and private witness file-identity checks. Unexpected keys, wrong schema, duplicate JSON keys, mismatched fields, malformed UTF-8 or missing files cause HOLD without printing paths or notes.

The 46-check matrix remains **initially NOT_RUN**. Complete declared results still report `MANUAL_MATRIX_COMPLETE_UNCERTIFIED`, `release_authorized=false`, and `premium_editor_licensed=false`. Two premium products are **locked-dialog-only**; do not run their paid editor functionality.

## Witness JSON shape (illustrative, NOT an attestation)

Each reviewer must independently observe the **actual packaged candidate**, then privately create the appropriate JSON file. The fields below are illustrative placeholders: **never copy the example's conclusion into a real review**. Use the candidate SHA from the preexisting `review.json` `apps.<exe>.candidate_sha256`; use the exact review-level `r9_report_sha256`, `reviewer_id`, `windows11_build`, and `observed_utc`. Set `state` to the actual PASS or FAIL outcome, and write an observation describing what was tested, what was observed and any deviations, without customer data, paths, screenshots, personal data or secrets:

```json
{
  "schema": "fv-labs-win11-check-witness-r110-v1",
  "app": "LedgerDiffLite.exe",
  "check": "physical_tab_shift_tab",
  "state": "FAIL",
  "candidate_sha256": "<EXACT LOWERCASE 64-HEX CANDIDATE DIGEST>",
  "r9_report_sha256": "<EXACT LOWERCASE 64-HEX R9 REPORT DIGEST>",
  "reviewer_id": "internal-QA1",
  "windows11_build": 26100,
  "observed_utc": "2026-11-01T12:00:00Z",
  "observation": "<AT LEAST 80 CHARACTERS OF THE REVIEWER'S ACTUAL SPECIFIC OBSERVATIONS; NEVER CUSTOMER DATA>"
}
```

The file above should be stored privately as `LedgerDiffLite--physical_tab_shift_tab.json`. Hash its **actual UTF-8 file bytes** using local Windows PowerShell `(Get-FileHash -Algorithm SHA256 -LiteralPath '<PRIVATE FILE>').Hash.ToLowerInvariant()`, then put the lowercase digest in that exact app/check `witness_sha256` field of the corresponding review JSON. A completed or failed check must have both the matching JSON and the matching SHA; leave an unperformed check `NOT_RUN` with null digest. Do not edit the R9 report or the `dist` candidate directory.

R109's legacy generic `.txt` witness notes **will fail closed** with R110: no physical reviews have been claimed or published to migrate. If a private reviewer already recorded work, retain its originals separately and rewrite the notes into the new structured format, with accurate observations and fresh hashes; do not relabel it PASS automatically.

## Security and realistic boundaries

- A binding to review fields and a hash protects against **accidental misassociation** and detectable changes unless a writer also changes both the note and its hash. It is **not** a digital signature, proof of independent human observation or evidence of regulatory compliance.
- The tool does not inspect, upload, transmit, classify or redact private evidence automatically. Reviewers must use synthetic/nonidentifying descriptions, and **never attach** source notes, customer CSVs or executable bytes to CI or the PR. Keep all notes outside the build and source tree, on a trusted offline workstation.
- R9 smoke/PE integrity, Windows 11 x64 workstation checks, actual NVDA/keyboard/contrast/scaling, AV/EDR, code signing and commercial premium entitlement/access-controlled delivery are separate release gates. No code path authorizes release, unlocks premium editors, or changes financial calculations.
- QD independently reviews the **exact PR head**; founder approval is still required. Never publish free or premium downloads before their real distribution verification.

## Executable tests and evidence

```powershell
$env:PYTHONPATH = 'products/desktop'
python -m unittest discover -s products/desktop/tests -p 'test_windows11_manual_acceptance_r109.py' -v
python -OO -m unittest discover -s products/desktop/tests -p 'test_windows11_manual_acceptance_r109.py' -v
```

The expanded R109 test module contains **55 synthetic tests** (36 existing, 19 new R110) including cross-app, cross-check, cross-candidate, cross-reviewer, cross-R9, time/build, conclusion, duplicate keys, invalid JSON, malformed observations, and an adversarial copied-and-rehashed note. The focused R109 suite is already a **mandatory normal/optimized step on both Linux and Windows** in `.github/workflows/desktop-build.yml`; no artifact publication policy or release gate is weakened. Passing synthetic tests does **not** complete the 46 real manual checks.

**Next highest-impact step:** Execute the expanded exact-head two-OS CI; then have an independent trusted Win11 x64 reviewer use **six privately built SHA-pinned executables** and a matching R9 report, recording 46 genuine outcomes and appropriately bound private notes. Separately complete AV/EDR, signing/SmartScreen, premium entitlement issuance and authenticated delivery checks, independent QD and founder approval. **Release HOLD.**
