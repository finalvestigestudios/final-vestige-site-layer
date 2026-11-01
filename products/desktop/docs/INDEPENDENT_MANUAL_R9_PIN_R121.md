# Final Vestige Labs R121 — external R9 evidence pin for physical Windows 11 manual QA

**DRAFT / HARD RELEASE HOLD · Issue #73 · branch stacked on R120 draft PR #507, not production.** This change is an intake safeguard, **not** proof that any reviewer has run the six applications or inspected them independently.

## Gap addressed

The R109/R110 witness tool checked six current executables and the SHA-256 of the R9 report, but generated its local template from that **same local R9 file**. An operator accidentally using an unrelated yet internally consistent six-EXE/R9 set could obtain a 46-check template, fill notes and produce `MANUAL_MATRIX_COMPLETE_UNCERTIFIED` without ever comparing the R9 evidence to an independently retained known-good digest. Cryptographic self-consistency is not independent provenance.

R121 makes `--expected-r9-sha256` **mandatory for both** the `template` and `verify` actions. It accepts **exactly 64 lowercase ASCII hexadecimal characters**, checks the SHA-256 of the exact bounded, descriptor-verified **R9 report bytes**, and fails before calling the local six-executable verifier on a mismatch. It will not derive, autofill, normalize, or print the independent digest. This is not a signature; matching a caller-supplied hash does not prove the caller obtained it independently.

The existing R109 witness schema, all **46 required physical checks**, original source-row audit integrity, human-only decision handling, six names and four-free/two-premium separation remain unchanged. Both commands continue to write local evidence only, with no upload, telemetry, or release authorization.

## Operator handoff (authorized reviewer only)

1. Have a QD-approved build custodian retain the **exact previously R9-smoked six executable bytes** and their `SHA256SUMS.txt` and `offline-candidate-evidence.json` privately; the ordinary GitHub Actions evidence artifact **does not** contain EXE bytes. Do not claim candidate custody if the runner deleted them. Reproducing a build creates different candidate bytes and requires **a new R9 pin**.
2. The custodian must independently preserve the SHA-256 **of the exact raw `offline-candidate-evidence.json` file**, not the `SHA256SUMS.txt`, executable digest, Git commit, CI artifact zip digest, or a JSON reserialization. Send this report pin to the reviewer through a separately authenticated, QD-approved channel. Do not simply run a hash command over the received reviewer copy and paste that as the purported external pin. Authenticate both the source and the receiver; SHA-256 alone authenticates neither.
3. The reviewer must compare the separately obtained pin against the retained R9 report **before** generating a template or accepting witness evidence. Keep binaries and private observations on an authorized, access-controlled Windows 11 x64 workstation; never publish premium binaries or keys in public GitHub, website media, or chat.
4. Use the existing tools and genuine observed evidence: 32 free-app and 14 premium-locked-surface checks = **46** physical tests (keyboard, NVDA, high contrast, 200/400% scaling and locks). The `verify` action requires a native Windows 11 workstation. All fields and witness hashes are reviewer assertions, not an independently established certification.
5. A syntactically valid pin that matches does **not** establish historical R9 build trust, binary signature, malware clearance, code-signing validity, reviewer independence, or authorization. Independent Defender/EDR detection and remediation-history review, signing, entitlement, QD and founder approval remain separate hold points.

Example syntax (no actual path, digest or URL supplied here):

```powershell
$pin = "<externally authenticated 64 lowercase hexadecimal R9 report SHA256>"
python products/desktop/scripts/windows11_manual_acceptance_r109.py template --dist "C:\PRIVATE\six-exes" --r9-report "C:\PRIVATE\evidence\offline-candidate-evidence.json" --expected-r9-sha256 $pin --review "C:\PRIVATE\review\matrix.json"
python products/desktop/scripts/windows11_manual_acceptance_r109.py verify --dist "C:\PRIVATE\six-exes" --r9-report "C:\PRIVATE\evidence\offline-candidate-evidence.json" --expected-r9-sha256 $pin --review "C:\PRIVATE\review\matrix.json" --witnesses "C:\PRIVATE\review\witnesses"
```

A missing, uppercase, padded, malformed, altered or unrelated pin results in the existing **privacy-redacted HOLD**, with no generated template or release clearance. A report that differs only by JSON whitespace still hashes differently and is rejected. The exact R9 report must be preserved byte-for-byte.

## Test contract and evidence boundary

The existing R109/R110 Python source test runner now insists on all **15 new R121 regression methods** and **at least 70 total** source-owned methods, including canonical/invalid pins, report-byte tampering, source candidate and checksum drift, both CLI actions missing the pin, and exact pin forwarding to the local-only template. It continues to run in both standard Python and optimized `-OO`, on both Linux and Windows CI jobs, with exception details withheld from output. R121 is not a claim of a completed reviewer acceptance test.

**Remaining release blockers:** independently retained real six-EXE custody and authenticated out-of-band R9 provenance; actual reviewer transfer; **46 physical Windows 11 tests still NOT_RUN**; actual AV/EDR/remediation-history review; signing/SmartScreen; real premium paid-license/access-gated delivery; independent QD exact-head review and founder approval. **All six utilities are UNRELEASED. Production/site unchanged.**
