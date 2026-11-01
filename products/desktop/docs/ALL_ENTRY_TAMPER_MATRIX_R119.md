# Labs R119 — all-eight-record native sealed-transfer tamper matrix (DRAFT / HOLD)

Tracks [Issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Feature branch `feature/labs-all-entry-tamper-matrix-r119`, stacked exclusively on R118 [draft PR #494](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/494), not on production. **This is an internal regression test, not authorization to distribute executables.**

## Why this increment exists

R118 tested actual six Windows x64 executable bytes through encrypted sealing and successful unsealing, but its mandatory tamper test flipped **only the first executable's ciphertext**. An implementation that incorrectly bypassed authentication for the other five executables, the SHA256 inventory, the R9 report, or GCM tags could have escaped that specific negative check.

R119 additionally checks **16 separately induced authentication failures** after a fresh R9-approved private seal: for each of the **eight fixed records** (six internal EXEs, SHA256SUMS.txt, R9 JSON), flip a byte in *ciphertext* and then a byte in the corresponding *GCM tag*. Every case must refuse unsealing and leave **no published reviewer intake**. After each case, the test restores the original byte, fsyncs, and verifies that the SHA256 of the entire encrypted archive equals its original value. A failure stops the CI job; no positive transfer/release result may be produced.

`sealed_tamper_matrix_r119.py` parses the canonical sealed framing and validates the record layout against the pinned R9 fingerprint and bounded metadata before selecting offsets. It refuses an altered record boundary, missing entry, substituted bundle file, out-of-bounds mutation, changed source candidate or unsafe runner scratch. The R9 fingerprint used in CI is **computed within the same run**, so this proves local consistency, **not independent cross-machine custody**.

## Reproduce privately

Prerequisites: Python 3.12, pinned `cryptography==46.0.4`, six locally and natively R9-smoked Windows x64 candidate executables in `dist/`, matching `dist/SHA256SUMS.txt`, and `build/offline-candidate-evidence.json`. Use a disposable private Windows build environment. Do not copy premiums or keys into publicly accessible storage.

```powershell
$env:PYTHONPATH = "products/desktop"
python -m unittest discover -s products/desktop/tests -p 'test_sealed_tamper_matrix_r119.py'
python -OO -m unittest discover -s products/desktop/tests -p 'test_sealed_tamper_matrix_r119.py'
$scratch = Join-Path $env:RUNNER_TEMP "fvs-r119-native-private"
New-Item -ItemType Directory -Path $scratch -ErrorAction Stop | Out-Null
try {
  python products/desktop/scripts/sealed_tamper_matrix_r119.py dist build/offline-candidate-evidence.json $scratch
  if ($LASTEXITCODE -ne 0) { throw "R119 HOLD" }
} finally {
  Remove-Item -LiteralPath $scratch -Recurse -Force -ErrorAction SilentlyContinue
}
```

CI runs both focused modes on Linux and Windows, then builds and native-smokes six internal AMD64 EXEs. The **real-byte matrix** runs only after R9 custody and the successful R118 integration. No runner key, encrypted archive, extracted executable or premium file enters GitHub artifact uploads. Only the existing internal source/checksum/R9 report allowlist remains.

## Evidence limitations / QD release hold

- Synthetic unit regressions do not establish that the native binaries are safe. A green Actions step shows only that the runner-restricted matrix passed on the exact tested commit.
- No approved independent Windows 11 x64 workstation, reviewer transfer, physical NVDA/high-contrast/keyboard/scaling acceptance (46 checks), actual offline Defender/EDR assessment, malware remediation review, code signing/SmartScreen clearance, or independently saved cross-device R9 checksum anchor has been provided.
- Premium files remain entitlement-locked and must never be uploaded to unrestricted CI artifacts or hosted at public download URLs. Nothing is published on WordPress and no production branch is touched.
- Unverified decrypted plaintext may temporarily exist inside **runner-private** staging during attempted GCM unseal; cleanup is best-effort deletion, not forensic secure erase. A passed test is not a privacy/access-control certification.
- Independent **QD exact-commit review** and **founder release approval** are mandatory prior to merging any production-affecting or distribution changes.

**Next highest-impact step:** arrange a genuinely controlled handoff of six checksum-pinned, privately held Windows candidates to an independently approved Windows 11 reviewer, complete real malware and 46 accessibility observations, and capture witnessed SHA256 evidence. Until then **all six applications remain UNRELEASED**.
