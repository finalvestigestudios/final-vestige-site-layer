# R40 — deterministic candidate inventory publisher (pre-release only)

**Scope:** All six Windows x64 apps. No app is released, certified or automatically approved by this change. Production, WordPress and the QD approval procedure are unchanged.

## Why this matters

The R39 Windows CI recipe enumerated any `*.exe` discovered in `dist` and appended SHA-256 entries to a text file. The local Windows operator script separately generated the inventory using different formatting. Extra executables, leftover manifests, noncanonical ordering and partial writes could create ambiguous evidence before the strict R37 release gate ran.

R40 routes both workflows through the same `products/desktop/build_inventory.py` tool. The release gate imports its exact six-program allowlist so names cannot drift independently.

## What it guarantees (within the stated filesystem threat model)

- The **initial** folder must contain **exactly six approved distinct ordinary files**, without links, zero-byte placeholders, subdirectories, hidden evidence, extra DLLs or private licensing assets. Any pre-existing `SHA256SUMS.txt` blocks another write.
- All six candidates are hashed with the existing descriptor-checked, bounded R37 SHA-256 reader (512 MiB per candidate), in canonical allowlist order. Results are ASCII text with lowercase digests, two spaces, exact basename and LF newlines.
- The tool stages a private file on the same volume, flushes and fsyncs it, rechecks the six candidates, and **publishes exclusively through an atomic hardlink**. It never silently truncates or overwrites an existing inventory.
- After removing its staging link, it applies the existing seven-file allowlist and re-reads the published manifest and all six executable digests. If verification fails, it attempts to remove **only the manifest inode it just published**. No candidate image is deleted.
- Errors do not print unknown private candidate filenames. All checks are performed locally, without telemetry, uploading financial data, executing any candidate, or issuing approval.

**Limits:** This detects observed changes, not every adversarial filesystem race or a compromised build workstation. SHA-256 inventories cannot authenticate the identity or source of the compiled code. Exclusive hardlinks require local filesystem support; a volume without working hardlinks fails closed. Do not confuse synthetic-test files with real Windows PE images.

## Operator workflow

From a trusted, clean source checkout after all six real Windows x64 executables have been built into an initially clean `dist` folder:

```powershell
$env:PYTHONPATH = "products/desktop"
python products/desktop/build_inventory.py dist
python products/desktop/release_gate.py dist --smoke --report build/offline-candidate-evidence.json
python products/desktop/report_attestation.py build/offline-candidate-evidence.json dist
```

Or use `products/desktop/scripts/verify-windows-candidate.ps1 -Build` on a Windows 11 x64 machine with installed Python, PyInstaller, cryptography and a complete checkout. Run tests first. Reports remain outside `dist` and cannot be overwritten. Failed builds must be inspected and restaged manually rather than cleaned automatically.

Do **not** place private license keys, purchaser records, premium installer secrets, financial documents, the evidence report or an additional README in `dist`. No direct links or public distributions are created.

## Regressions and remaining release gates

```bash
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_build_inventory_r40.py -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p test_build_inventory_r40.py -v
```

23 R40 tests exercise canonical byte layout, rerun determinism, no-clobber, missing/extra binaries, symlink/hardlink, truncation/oversize, source drift before/after publication, fsync errors, concurrent link collisions, error sanitization and read-only input custody. Local Linux tests use synthetic data, **not** executable PE validation.

R40 is not a substitute for complete repository regressions; actual Windows x64 PyInstaller builds and native smoke; AV scanning, signing/checksum review, clean-machine GUI accessibility, premium purchase/entitlement protection, and independent QD approval. **HOLD all six releases.**
