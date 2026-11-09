# R312 — bind premium vault restoration to the entitled review product

**DRAFT / independent QD and founder hard hold.** No production merge, public downloads, binaries, WordPress changes or releases.

## Defect and fix

GrantAudit Studio Pro and ProcureGuard Studio Pro revalidate their own signed entitlement before opening the restore dialog. However, the common `restore_evidence` API previously accepted **either** authenticated archive product without comparing it to the active entitled window. A user entitled to one product could restore an archive of the other product if they also possessed its ciphertext and passphrase.

R312 introduces `fvs_suite/vault_product_gate.py`: exact-native-string, fail-closed product-scope validation with fixed, path-free errors. The real `review_ui.restore_archive` call now passes its already-authorized `product` into `evidence_vault.restore_evidence(..., expected_product=product)`. The comparison occurs **after AES-GCM authentication, before any plaintext restore directory is created**. Existing trusted direct API callers retaining the optional unscoped argument preserve compatibility; this is **not DRM** and is **not** an entitlement substitute.

## Reproduction

Run these from the complete GitHub checkout; the AES-GCM integration requires `cryptography==46.0.4`.

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_product_gate_r312.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_product_gate_r312.py' -v
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_vault_product_integration_r312.py' -v
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_vault_product_integration_r312.py' -v
```

**Locally executed isolated evidence:** 20/20 focused guard tests passed on CPython with `-W error`; 20/20 with `-OO -W error` (40 method executions), and `py_compile` passed for the helper and both test files. This does **not** prove the two GUI call sites' full integration or the genuine AES-GCM test cases executed. The latter are committed for both hosted runner jobs; hosted CI currently fails before running steps.

**Unexecuted but committed integration acceptance:** For both products, mismatched archives must be rejected without creating any plaintext directory; same-product restores must succeed; ciphertext must stay unchanged; invalid scopes must be rejected.

## Scope, limitations and gates

Only premium vault restore product binding was changed. The four free utilities, encryption scheme, Decimal money, deterministic audit history, review decisions, entitlement logic and local-first privacy remain unchanged. Archive authentication proves ciphertext integrity for a passphrase, not a product license. Running Python directly on owned files remains possible; the GUI entitlement gate is separate and still required.

Windows 11 x64/NTFS acceptance, complete repository tests, actual packaged executables, Defender/QA, premium download gating and source CI are still pending. No merge or release without independent QD and founder approval.
