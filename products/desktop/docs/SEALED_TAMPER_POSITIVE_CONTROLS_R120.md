# Labs R120 — require real clean-decrypt controls around all 16 tamper cases

**DRAFT / RELEASE HOLD · Issue #73 · Stacked on R119 draft PR #501 only.** This is private CI engineering, not independent Windows 11 reviewer acceptance, malware clearance, entitlement authorization, QD approval, or release approval.

## Defect demonstrated and fixed

R119's sixteen ciphertext/tag mutations were correctly rejected, but the test could report success if *every* decrypt attempt rejected an already-unusable archive or key. Negative tests alone did not establish that valid plaintext could ever be recovered in that same matrix run. R118's earlier separate roundtrip lowers this risk, but does not prove the state of the R119 runner at the moment of all sixteen rejections.

R120 adds **two mandatory positive controls** inside R119's real six-EXE private matrix: one before the sixteen mutations and one afterward. Each must unseal the original archive successfully with the exact private key and pinned R9 record, and return the strict uncertified/unreleased result. Each recovered intake must contain **exactly** the six named EXEs plus the R9 report and checksum inventory, with no extra entries. All eight size/SHA-256 pairs must match independently captured source snapshots; original candidates are hashed again at the end. Both clean-decrypt staging directories are removed immediately, even if verification fails. The sealed archive SHA-256 must remain unchanged across both controls and all mutations.

**An always-rejecting decryptor, a forged success response without plaintext, altered decrypted EXE, unexpected extracted file, failed final unseal, or source candidate drift now fails the private CI gate.** The old sixteen independent authentication-failure challenges remain intact.

## Verification contract and scope

- Updated `scripts/sealed_tamper_matrix_r119.py`: requires **2 valid full eight-record decrypt controls + 16 negative tamper rejections**; explicitly returns `positive_controls_verified=2`, `release_authorized=false`, `independent_r9_pin=false`, and `physical_windows11_acceptance=false`.
- Extended `tests/test_sealed_tamper_matrix_r119.py`: **26** synthetic source-owned tests (19 prior + 7 R120), including a broken-always-denying decryptor, failed final clean decrypt, forged non-extraction, corrupt extracted binary, added extracted entry, candidate drift and call-order checks.
- Updated `scripts/safe_unittest_r119.py` method inventory to **26**, retaining privacy-redacted stdout/stderr, method-only diagnostics, and no private file paths or customer data in CI logs.
- Existing mandatory Linux/Windows source regression gate exercises that exact module in both standard Python and `-OO`. The existing actual-six-EXE native Windows matrix executes the updated implementation **after** the six binaries' R9 evidence is established. Artifact upload allowlist is unchanged and contains **no executables, keys, encrypted archives, or premium payloads**.

Local focused command (synthetic only):

```bash
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r119.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r119.py
```

Native Windows builds and R9-integrated testing must be verified with exact-head GitHub Actions results; passing synthetic tests does not prove actual Windows 11 acceptance or authorize publishing.

## Privacy and release barriers

The test uses only already-private R9-smoked candidates and ephemerally generated keys on an Actions runner. It performs no telemetry and changes no monetary or compliance calculations. The R9 SHA used within hosted CI is **same-runner**, not an independently transmitted reviewer trust anchor. The **46 physical Windows 11 witness checks** have not been completed. Actual Defender/EDR and remediation review, code signing and SmartScreen, secure purchase/license verification, authenticated premium downloads, independent QD exact-head review and founder approval remain required. No six-app release is authorized.

**Next highest-impact step:** obtain QD-authorized private candidate custody and a truly independent R9 trust anchor, then perform witnessed physical Windows 11 and AV/EDR review. Keep all six EXEs and customer data out of publicly downloadable artifacts.
