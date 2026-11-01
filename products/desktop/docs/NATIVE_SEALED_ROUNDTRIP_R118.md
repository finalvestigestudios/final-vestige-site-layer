# R118 — real six-executable ephemeral Windows CI encrypted roundtrip

**DRAFT / RELEASE HOLD.** This native integration gate resolves one R117 test gap: the 32 earlier crypto regression methods used synthetic PE bytes and mocked R9 attestation. R118 exercises the unchanged production-candidate R117 seal/unseal code against all **six freshly built, R9-native-smoked Windows x64 executable candidates** inside a disposable Windows hosted CI runner.

## Concrete verification

- The R118 job runs **after** R9 PE architecture, SHA256 inventory, six native EXE smoke tests, report consistency, and the existing evidence-only artifact upload.
- New native integration entry point: products/desktop/scripts/native_sealed_roundtrip_r118.py.
- New tests: products/desktop/tests/test_native_sealed_roundtrip_r118.py (15 source tests in normal and Python -OO modes on both Linux and Windows).
- The entry point requires all six exact EXE paths, checksum inventory, and the R9 native smoke report. It hashes and authenticates inputs, creates an ephemeral 32-byte AES key, encrypts all eight entries with R117 AES-256-GCM, decrypts them to runner-private staging, and verifies **all eight exact lengths and hashes** against the unchanged originals.
- It also flips one real executable ciphertext byte, requires GCM tag rejection with **no published intake directory**, and re-verifies unchanged source images.
- Both Python temporary directory cleanup and the PowerShell finally clause purge local key, bundle and plaintext staging. Any failed check exits nonzero. No key or private path is printed to normal CI logs.
- Existing Actions artifact allowlist stays limited to the Linux source verification JSON and Windows SHA256SUMS.txt/R9 evidence JSON. **No EXE, key, sealed bundle, premium file or plain reviewer output is uploaded.**

### Reproduction on a trusted Windows x64 host (internal only)

First build and verify the six private Windows x64 candidates through the R9 native smoke gate. Provide a **new private** scratch directory outside the repository, then invoke:

    python products/desktop/scripts/native_sealed_roundtrip_r118.py dist build/offline-candidate-evidence.json C:\PRIVATE\EMPTY-R118-SCRATCH

Use an empty, private directory with appropriate NTFS ACLs and encrypted local storage. Delete that scratch directory afterward. This is not an external transfer command.

### Security limitations

This is a **same-runner** integration check; the R9 SHA-256 is calculated from the report during this run and is **not independently established**. It does not prove independent historical smoke authenticity, human security review, true Windows 11 compatibility, endpoint ACL isolation, on-disk deletion guarantees, or secret protection against a compromised host. Plaintext is briefly staged within the runner (never uploaded); filesystem backups, forensic recovery and snapshots are outside the check's guarantee.

Actual QD-approved transfer to a separate, trusted physical Windows 11 x64 workstation remains unperformed. All **46 physical NVDA, keyboard, high-contrast and scaling checks**, actual Defender/EDR scanning and detection-history review, independently retained hashes, signing/SmartScreen, genuine premium entitlement and authenticated distribution, QD exact-commit review, and founder approval remain mandatory.

This integration gate grants **no release or distribution authorization**, does not modify financial calculations or human compliance decisions, and does not bypass premium locks. **All six products are UNRELEASED; production is unchanged.**
