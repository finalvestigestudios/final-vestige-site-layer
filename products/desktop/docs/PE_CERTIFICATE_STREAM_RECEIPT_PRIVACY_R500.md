# R500 — fail-closed WIN_CERTIFICATE stream receipts and private fault handling

**Status: DRAFT / QD HARD HOLD.** Issue #73. Stack strictly on R499 draft PR #2883, not on production `main`.

## Scope and reason
The shared Windows PE32+ certificate parser (used by the six-candidate internal release preflight) previously caught only `OSError` during header, tail and zero-padding seeks/reads. Direct callers or unusual file wrappers could instead raise an ordinary `RuntimeError`, `ValueError` or `UnicodeError` carrying private filename/ledger context. Header and tail reads also trusted a non-native bytes subclass or bytearray, potentially invoking caller-defined `__len__` hooks.

R500 now rejects any ordinary seek/read exception at those three phases by raising a fixed `PECertificateError` **after** the handler has exited. It requires exact native `bytes` for 8-byte headers and 1-byte record tails, consistent with R499's outer-padding native receipt rule. Failures do not preserve a private `__context__` or `__cause__`. `SystemExit` and `KeyboardInterrupt` still propagate; no process exception is silently treated as a valid certificate. Raw `FileIO` already returns built-in bytes, so this is defense in depth for direct API/wrapper paths, **not a claim of an exploit in actual Windows FileIO**.

The existing record count (128), table size (8 MiB), zero-padding policy, R493 descriptor digest, R498 unbuffered reads, and four-free/two-premium inventory remain unchanged. This still **does not** verify Authenticode, trust, malware, Windows startup, signing or entitlement.

## Changed source and tests
- `products/desktop/pe_certificate_guard_r496.py`: fixed redacted exception paths and native header/tail read receipts.
- `products/desktop/tests/test_pe_certificate_receipt_privacy_r500.py`: 11 test methods with subtests for 24 ordinary seek/read failure scenarios, forged byte receipts, short reads, zero/nonzero padding, valid one/two-record framing and unswallowed process interrupts.
- `.github/workflows/desktop-source-evidence-r385.yml` and `.github/workflows/desktop-build.yml`: new normal and optimized Python regression commands.

From a trusted checkout:

```sh
python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_receipt_privacy_r500.py
python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_receipt_privacy_r500.py
python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_guard_r496.py
python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_guard_r496.py
python -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_binding_r496.py
python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_pe_certificate_binding_r496.py
```

## Observed evidence and limits (2026-11-17)
Locally exercised on Linux CPython 3.13.5 with synthetic BytesIO fixtures: **11/11 PASS** normal `-W error`, **11/11 PASS** optimized `-OO -W error`; `py_compile` PASS. The new test module matches the committed Git blob, `14d35e7dc12da8ae2f81c0372501e568e5848292`. The local helper was behavior-equivalent, but not byte-identical to the committed helper because commentary differed: **do not characterize the complete test as exact-commit proof**. A reconstructed R499 behavior negative control raised **20 errors and 2 failed assertions** across the new suite, demonstrating failures that R500 addresses.

Native Windows, inherited parser tests, full six-engine regression, packaging, Defender, checksum verification of real binaries, accessibility, cryptographic signature validity and private premium delivery were **not run** locally.

Latest inspected R499 GitHub Actions source #44110435145 and Windows internal #44110435455 completed as failures before executing job steps (four jobs, `steps=null`, `runner_id=0`), with root cause **unconfirmed**. GitHub Actions billing/quota, organization runner eligibility and policy need owner inspection; rerun the R500 exact head after restoration.

## Next gate
1. Restore runner execution or use a trusted full Windows x64 checkout.
2. Run the focused R500 suite, inherited R496–R499/parser regressions, complete six-engine Decimal/provenance test matrix, true Windows packaged executable smoke tests and Defender/EDR.
3. Confirm checksum manifest, keyboard accessibility, premium gated payment/license download, then independent QD review and explicit founder approval.

**Never merge, publish, distribute, or expose premium binaries from this draft.** Compliance findings are human-reviewed; no user financial data or live systems were used.
