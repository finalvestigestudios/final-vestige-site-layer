# R502 — PE certificate seek-position receipt custody

**Scope:** Six Windows x64 release-candidate preflights only. LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro and ProcureGuard Studio Pro retain their current money, CSV, offline privacy, review and premium authorization behavior. This is a source validation increment, **not release approval**.

## Fixed behavior

R501's structural `WIN_CERTIFICATE` reader requested absolute seek offsets for each 8-byte record header, last-byte tail probe and up-to-7-byte outer padding check. It checked the returned bytes but ignored the native `seek()` receipt. A direct-call injected stream could return a plausible byte sequence after reporting an incorrect or non-native seek position, and the shape preflight could accept it. Real `FileIO` returns an exact native integer and is unaffected.

R502 factors those three reads through `_read_exact_at` in `pe_certificate_guard_r496.py`. Only a native `int` seek result matching the requested offset and native `bytes` of the exact requested length are accepted. Boolean, subclassed, absent and wrong-position receipts fail closed. Ordinary seek/read faults result in the existing fixed `PECertificateError` *outside* the caught exception handler; private exception context/cause is not retained. `KeyboardInterrupt` and `SystemExit` are not swallowed.

The existing maximum 8 MiB certificate table, 128-record cap, PKCS revision/type checks, physical tail availability, zero-only outer padding, descriptor-owned stream and SHA-256 manifest binding remain unchanged. No binary execution, PKCS#7 authentication, AV scan or cryptographic Authenticode validation is performed.

## Exact source and test evidence

- Parent source blob: `2a52e6d5812af3d111b1134d070c04e434ef5892` (R501).
- Patched source blob: `6d3da7a1f189cb530a340d74a97d4e54729f1308`.
- New 13-method regression blob: `5707eb54c78c775024c99d6167155586fd6c3cdf`.
- Local Linux Python, `PYTHONPATH=.`: `python -B -W error -m unittest discover -s tests -p test_pe_certificate_seek_receipt_r502.py` **13/13 PASS**.
- Optimized Python: `python -OO -B -W error -m unittest discover -s tests -p test_pe_certificate_seek_receipt_r502.py` **13/13 PASS** (26 test executions, no skips).
- `python -B -m py_compile` on the production helper and new test module: **PASS**.
- Negative control: same tests against reconstructed and exact Git-blob-verified R501 helper: **seven expected failing methods** (13 attempted); tests reject the original bad seek receipts.
- Cases include native `BytesIO` and actual unbuffered `FileIO`, all three certificate read positions, second record, type-confused seek receipts, private error redaction and process interruption.
- Both internal source and Windows-build workflow YAML files now invoke R502 tests in standard and optimized Python. Adding workflow steps is not evidence that hosted CI ran.

## Limitations and next release gate

Only these isolated source tests executed locally. A complete repository checkout, inherited R496–R501 integration suites, native Windows x64 builds, signed-code validation, real executable smoke, Defender, accessibility and premium distribution entitlements **have not** been verified in R502. Local tests used inert bytes and do not establish signature trust or prove a race-free filesystem snapshot.

The last observed R501 GitHub Actions runs [source #44131792602](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44131792602) and [build #44131792673](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44131792673) failed with jobs showing `steps=null` and no runner. Root cause remains undetermined; check Actions eligibility, billing/spending limits and repository policies, then retry on a trusted Windows x64 runner and execute full six-app gating.

**QD HARD HOLD:** Branch/PR remain drafts and stacked on R501, not production main. Never merge, deploy, sign, distribute or expose premium downloads without independent QD and explicit founder approval.
