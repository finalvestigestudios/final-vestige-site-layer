# Final Vestige Labs R8 — Encrypted evidence backup and authenticated restore

**Pre-release security increment for GrantAudit Studio Pro and ProcureGuard Studio Pro only.** These are opt-in AES-256-GCM encrypted **copies** of existing exception CSV reports and their local JSONL human review journals. This is not encrypted primary storage, a login system, verified reviewer identity, regulatory certification, secure erasure or payment authorization. The original report and journal remain **plaintext** and unmodified.

## User workflow

1. Generate a premium exception report and record optional human review actions in the review workbench.
2. Choose **Seal encrypted copy…**, select an existing destination folder, and enter/confirm a unique passphrase (16–1024 characters).
3. A new, never-overwritten \`.fvault\` file is written. **Retain the passphrase separately; it is not stored and there is no password reset.**
4. Choose **Restore encrypted copy…** to authenticate/decrypt into a new exclusive \`fvs-evidence-restored-*\` subfolder. On success, this folder contains \`exception-report.csv\`, optional \`exception-report.review.jsonl\` (the naming convention expected by the review GUI), and \`sealed-evidence-manifest.json\`.
5. Restored files are **plaintext**. Handle them as confidential; follow retention and secure-erasure policies. Do not use prerelease builds with sensitive real-world production data.

Both controls are available in each premium application's review window. Keyboard shortcuts are Ctrl+Shift+S and Ctrl+Shift+O. No cloud services, telemetry, user accounts or network endpoints are called.

## Format and integrity

- Versioned \`FVS-EVIDENCE-VAULT-v1\` magic prefix, random 16-byte salt, random 12-byte AES-GCM nonce, followed by authenticated ciphertext and tag.
- Python \`cryptography==46.0.4\`; \`Scrypt(n=32768, r=8, p=1, length=32)\` derives the AES-256 key from the passphrase and random salt. Neither passphrase nor derived key is saved to the vault.
- AES-GCM additional authenticated data binds the format header, salt and nonce. Ciphertext corruption and wrong passphrases reject **before any plaintext file is created**.
- Ciphertext encapsulates canonical UTF-8 JSON containing base64-encoded original report and optional journal bytes, product identity, UTC seal time, original basename labels, report/journal SHA-256, and event count.
- Sealing validates source report and all human review events using the R7 snapshot-bound journal verifier. Report/journal file byte snapshots are rechecked before sealing; changes fail closed.
- Restore requires strict schema and duplicate-key validation, enforces size limits, compares embedded hashes, and re-runs R7 \`read_cases\` / \`read_journal\` verification before declaring success. Any validation failure removes only files/folders created by that restore attempt.
- No archive, source report, existing output directory, prior restored folder, or unrelated file is overwritten. Vault writes use exclusive creation with fsync. Restore creates an exclusive new directory and outputs.
- Maximum sizes: 64 MiB report, 16 MiB journal, 120 MiB sealed vault. Unsupported or symlink input files are rejected.

## Code use

After installing the pinned dependency:

    python -m pip install "cryptography==46.0.4"

For trusted synthetic test evidence:

    from fvs_suite.evidence_vault import seal_evidence, restore_evidence

    archive = seal_evidence(
        "example-exceptions.csv", "grants",
        "example-exceptions.review.jsonl", ".", "unique-long-passphrase")
    restored_dir = restore_evidence(archive, ".", "unique-long-passphrase")

These calls do not delete source files, modify review decisions, authorize spending or change an exception's disposition. For procurement use \`"procurement"\`.

## Security limitations and release status

- **Existing plaintext reports and human journals are NOT encrypted at rest.** R8 secures a copy made on demand, not an active working directory. Copying a vault elsewhere does not remove or secure its unencrypted sources or restored copies.
- Users are responsible for strong unique passphrases and backups. Password recovery is intentionally impossible. Disk caches, backups, swap, external processes, temporary logs outside this component, and live process memory are not under this vault's control. Do not assume secure deletion or cryptographic memory erasure.
- The archive authenticates ciphertext against its passphrase, **not reviewer identity**. An authorized user with the passphrase can create a different valid archive. Existing unkeyed R7 journals remain rewritable by an attacker with filesystem write access; R8 does not provide externally anchored signatures.
- Desktop executables and UI need clean-machine Windows 11 tests, antivirus/reputation checks, accessibility evaluation, independent cryptographic review, premium entitlement gating and distribution controls before public release.
- R8 adds **12 synthetic archive regression tests**, including authenticated round trips for both premium products, no-journal backups, wrong passphrases, ciphertext/header tampering, stale evidence, corrupted journals, symlinks, collisions and non-overwriting restores. The new module's core tests **passed locally using an isolated compatibility harness**, not the full repository's R7 source. Full R7 integration, both packaged Windows smoke paths, and the complete repository suite remain **UNVERIFIED** until runnable CI or a clean Windows runner becomes available.
- Existing Final Vestige QD review, branch protections and production deployment approval remain mandatory. No public releases or premium download links are authorized by this increment.

Development tracker: [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73).
