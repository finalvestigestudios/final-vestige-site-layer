# Final Vestige Labs R122 — one-check private Windows 11 manual witness writer

**DRAFT / HARD RELEASE HOLD · Issue #73 · stacked on R121 draft #513, NOT main.**

## Why this exists

R121 verifies an externally supplied raw-R9 evidence digest before a reviewer can create or verify the 46-check acceptance matrix. But R109/R110 required a human to manually compose every versioned witness JSON file, compute its SHA-256, and edit a matching manifest entry. That repetitive, error-prone work made independent physical acceptance harder.

R122 supplies `windows11_witness_writer_r122.py`, a **local-only, one-check-at-a-time recorder**. It creates exactly one source-bound JSON witness from a human-written local observation text file and updates exactly the matching `NOT_RUN` matrix slot. It does **not** automate, simulate, or pass any physical test. Every PASS or FAIL is still human-declared; the tool never adds an approval bit.

## Prerequisites

1. An authorized **physical Windows 11 x64 workstation** (not Windows Server/hosted Linux CI). R122 calls the existing native Windows 11 workstation gate *before* reading private candidate custody.
2. QD-approved custody of the exact six R9-smoked EXEs, original `SHA256SUMS.txt`, raw `offline-candidate-evidence.json`, and **separately authenticated** SHA-256 of that raw R9 report. A hash read from the same received copy is not independent.
3. Run the existing R121 `template` command once, outside the candidate EXE directory. In the generated review JSON, the human reviewer fills `reviewer_id`, the actual `windows11_build`, and `observed_utc` for the session; all 46 slots begin `NOT_RUN`.
4. Create an empty ordinary private `witnesses` directory outside candidate custody. Store the human's meaningful observation in a **separate local UTF-8 text file** (80–4096 visible characters, no control or bidi override characters). Record what was actually tried and observed; do not paste financial records, client identifiers, passwords or screenshots. R122 will not print that text.
5. Each call explicitly records **one** of the 46 named checks for one of six fixed products, with a human-selected `PASS` or `FAIL`. The app and check names must match the R109 schema. A prior PASS/FAIL may not be overwritten; correction requires a new QD-governed review session, not a silent amendment.

Example with *illustrative placeholder paths only*:

```powershell
$pin = "<independently authenticated lowercase SHA256 of exact R9 JSON bytes>"
python products/desktop/scripts/windows11_witness_writer_r122.py `
  --dist "C:\PRIVATE\six-exes" `
  --r9-report "C:\PRIVATE\custody\offline-candidate-evidence.json" `
  --expected-r9-sha256 $pin `
  --review "C:\PRIVATE\review\matrix.json" `
  --witnesses "C:\PRIVATE\review\witnesses" `
  --app LedgerDiffLite.exe `
  --check physical_tab_shift_tab `
  --state PASS `
  --observation-file "C:\PRIVATE\review\notes\ledger-tab.txt"

# After human review of ALL checks:
python products/desktop/scripts/windows11_manual_acceptance_r109.py verify `
  --dist "C:\PRIVATE\six-exes" `
  --r9-report "C:\PRIVATE\custody\offline-candidate-evidence.json" `
  --expected-r9-sha256 $pin `
  --review "C:\PRIVATE\review\matrix.json" `
  --witnesses "C:\PRIVATE\review\witnesses"
```

## Fail-closed behaviors and boundaries

- **No automatic PASS:** this writer never launches a test, reads a screen reader, or certifies physical accessibility, antivirus, malware clearance, entitlement, or reviewer independence. All initial entries remain `NOT_RUN` until explicitly recorded by a human.
- Requires the R121 external R9 pin, native Windows 11 x64 build, actual six-candidate checksum verification, intact existing matrix, and a valid, non-empty human observation before changing evidence.
- Uses exclusive new witness files, a per-matrix cooperative `.r122.lock`, a private temporary review copy, `fsync`, and an atomic matrix replacement. If recording fails, it removes its unchanged fresh witness; unexplained locks or preexisting evidence cause a HOLD. A crash may leave an unreferenced witness or lock requiring **manual investigation**. Locking is cooperative, not a defense against an adversarial privileged process.
- Rejects symlink/junction/reparse ancestors for review directories and forbids review/witness/observation paths inside the six executable directory. Does not alter executable bytes, source ledgers or premium licensing.
- Every previous recorded witness is rechecked against exact review identity and SHA-256 on subsequent calls. Manual editing of an existing witness invalidates that review. Private observations and paths are not echoed on error.
- `MANUAL_MATRIX_COMPLETE_UNCERTIFIED` after all 46 evidence-bound PASS assertions is **not release clearance**. Independent QA, genuine security review, code signing, authenticated premium delivery, QD exact-head approval and founder authorization remain distinct required gates.

## Regression evidence

The dedicated `safe_unittest_r122.py` runner requires **24 named synthetic regression tests**, refuses skips and duplicated/missing methods, and redacts exception details. Both normal and `-OO` interpreter runs are mandatory in Linux source and Windows build CI. Tests use **synthetic identities and no real EXEs**; CI alone cannot perform 46 physical checks. A successful hosted build remains **unreleased**.

**Next highest impact:** secure QD-approved *independent* Windows 11 x64 reviewer and authenticated off-runner custody of exact signed/unsigned candidate bytes and R9 pin; use this writer for all 46 actual physical checks, perform real Defender/EDR and remediation-history review, then independent QD/founder release evaluation. No site or production changes.
