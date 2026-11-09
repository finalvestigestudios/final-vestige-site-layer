# R301 — Authenticated premium evidence restore: exception-chain privacy

**Issue #73 | DRAFT | independent QD and founder HARD HOLD.** No changes to `main`, no executables or unrestricted premium downloads, no automated compliance approval.

## Verified defect

Both premium apps use `fvs_suite.evidence_vault.restore_evidence` to authenticate local AES-256-GCM encrypted audit records. An authenticated archive may still contain malformed UTF-8, malformed JSON or malformed base64. The pre-R301 restore code raised fixed-looking `ValueError` messages **from** `UnicodeDecodeError` or `JSONDecodeError` inside their handlers. The attached `__cause__`/`__context__` retained the original exception: `UnicodeDecodeError.object` or `JSONDecodeError.doc` can contain private *decrypted* grant/procurement records. Downstream exception collectors could read them even when UI text appeared safe. Invalid authentication tags and invalid base64 also chained internal diagnostic objects.

A synthetic previous-style JSON failure was independently reproduced: `exception.__cause__.doc` included `PRIVATE-GRANT-ACCOUNT-2026`.

## Implemented

- Added `fvs_suite/vault_decode_privacy.py`: `decrypt_evidence`, `parse_evidence_json`, and `decode_evidence_b64` convert expected faults into fixed-message failures **after the original handler exits**, so both `__context__` and `__cause__` are absent on those failure paths.
- Updated `evidence_vault.restore_evidence` to invoke these tested boundaries; preserved existing AES-256-GCM, Scrypt KDF parameters, authentication of the original binary prefix, strict duplicate-field rejection, size/digest checks, exclusive restore folders, zero-telemetry policy and human review.
- Committed 18 focused synthetic regressions, including genuine cryptography roundtrips and corrupt tags, plaintext-containing malformed JSON/UTF-8, invalid base64 and valid domain rejection cases.
- Committed 4 full-checkout encrypted-archive restore integration tests to assert sanitized errors and no plaintext output. **These integration tests were NOT executed locally:** this runtime cannot clone the private repository; hosted CI was previously failing before job execution.

## Evidence ACTUALLY executed (isolated Linux CPython 3.13.5)

The locally executed helper and 18-test source are Git-blob-identical to GitHub commits:
- Helper `eb1b7c9f5e3830bbda04c71b8a21c060c8b9ad96`
- Focused tests `4312e1e7b5e0bd19e7af5d0f25215afdb9681c06`

From `products/desktop`:
```sh
python -W error -m unittest discover -s tests -p 'test_vault_decode_privacy_r301.py'
python -OO -W error -m unittest discover -s tests -p 'test_vault_decode_privacy_r301.py'
python -m py_compile fvs_suite/vault_decode_privacy.py tests/test_vault_decode_privacy_r301.py tests/test_vault_restore_privacy_integration_r301.py
```

Results: **18/18 PASS normal, 18/18 PASS optimized, 36 focused executions**, compilation PASS (the integration file compiled but was not run). Prior-style parser negative control reproduced the leaked decrypted string.

## Release gates / next action

Restore actual GitHub-hosted runners (verify Actions billing, spending controls, enabled workflows and runner provisioning; exact infrastructure cause not yet confirmed), then run both 18-test focused modes **and** four full-checkout restore integration methods, inherited evidence-vault tests, and complete desktop suite. Record native Windows 11 x64 private six-EXE packaging/smoke results, SHA-256, Defender, accessibility and access-controlled premium distribution evidence. Independent QD/founder approval remains required before merge/release.

This increment is only an exception-privacy hardening change; **not proof** that the six Windows apps are release-ready.
