# R50 — Descriptor-bound premium entitlement verification (pre-release)

**Scope:** GrantAudit Studio Pro and ProcureGuard Studio Pro local Ed25519 entitlement reads. This safeguard is not license issuance, a payment gateway, DRM, binary signing, malware clearance, or QD release approval.

## Failure mode and implementation

The earlier license verifier separately called `is_symlink()`, `is_file()`, `stat()`, and `open()`. A filesystem substitution between these checks could cause it to parse a different local file from the one inspected. It also did not reject hardlink aliases or track source metadata during the read.

The R50 verifier routes every license read through `fvs_suite.journal_io.read_regular_bytes` with the existing **8,192-byte** bound and a pinned file descriptor. The reader checks that the file is distinct and regular, rejects visible symlinks/hardlinks and size violations, compares device/inode and metadata before and after the read, and verifies the path still points to the opened descriptor. Errors presented by the entitlement layer are fixed and do **not** echo private file paths. The existing canonical JSON, product binding, validity window, Ed25519 trust-key, and signature checks still execute on exactly those read bytes. No network, logging of customer data, or issuer private keys were added.

The bundled `TRUSTED_PUBLIC_KEYS` mapping remains deliberately empty; neither premium product is activated for customers. The four free applications and all Decimal-safe financial calculations are unchanged.

## Tests and commands

The new `tests/test_entitlement_custody_r50.py` has **16 tests**: two products with real ephemeral **test-only** Ed25519 signatures, exact read bytes, missing/empty/directory/oversize inputs, symlinks/hardlink aliases, same-length file substitution, in-place rewrites, sanitized permission failures, trust-anchor absence, wrong product, malformed JSON, and one bounded read. Two filesystem-race tests intentionally skip on Windows where concurrent file writes/replacements may be denied by OS sharing rules.

For developer source checks:

```powershell
$env:PYTHONPATH = "products/desktop"
python -m unittest discover -s products/desktop/tests -p test_offline_entitlement_r11.py -v
python -m unittest discover -s products/desktop/tests -p test_entitlement_custody_r50.py -v
python -OO -m unittest discover -s products/desktop/tests -p test_entitlement_custody_r50.py -v
```

**Local verification (Linux x86_64/Python 3.13.5/cryptography 46.0.4):** the 16 new tests and 15 unchanged R11 tests passed under normal Python **31/31** and optimized Python `-OO` **31/31**, in a reconstructed **three-source-file + two-test-file subset**. The unchanged `journal_io.py` and R11 test match their original GitHub blob hashes. Complete repository integration, native Windows verification, external signature issuance, premium entitlement fulfillment, six binary builds, scanning and release approval remain **unverified**.

## Operational response

A rejected license must not unlock the premium UI or open customer data. Keep the original customer record untouched; do not relink/edit license files, disable checks, or temporarily install test public keys in a release binary. If the file appears damaged or has been substituted, request a legitimate reissue and validate it against the approved production signing authority once that authority exists.

**This change cannot stop an attacker who can patch the installed binary, roll back the system clock, or change a file after validation.** Source verification and successful unit tests never authorize distribution. See issue #73 for native Windows and QD release gates.
