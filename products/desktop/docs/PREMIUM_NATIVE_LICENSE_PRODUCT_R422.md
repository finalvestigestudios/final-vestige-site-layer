# Labs R422 — native premium license product custody

**Draft source-only change. Release HARD HOLD.** Issue #73. Stacked on R421 draft #2446, not production `main`. No Windows executable, signing authority, website download or paid-file access was changed.

## Defect and impact

The two public signed-license entrypoints in `fvs_suite/offline_entitlement.py` previously used `product not in PRODUCTS` on a caller-supplied object. Python `str` subclasses can override `__hash__`, `__eq__` and `__ne__` to make a non-product compare as `grants`. The path helper then formats the same object and can invoke hostile `__format__`, producing a path that differs from the selected product. With injected trusted keys, the verifier could continue to read a license file before identifying an invalid product; a hostile subclass may also manipulate the comparison against signed product text. This is a direct-Python-API identity boundary, not evidence of remotely exploitable license bypass or premium file distribution exposure.

R422 introduces `_require_native_premium_product`, which checks `type(product) is str` **before membership or formatting** and returns the exact built-in `grants` or `procurement` identity. Both `installed_license_path` and `verify_license` call it as their first executable statement. Invalid products raise a fixed `EntitlementError` without invoking hostile text hooks, resolving a path or reading local license data. Normal signed Ed25519 product-specific verification remains unchanged; `TRUSTED_PUBLIC_KEYS` stays empty.

## Artifacts

- `products/desktop/fvs_suite/offline_entitlement.py` — actual product guards at both license entrypoints
- `products/desktop/tests/test_entitlement_native_product_r422.py` — 14 regression methods, including forged equal-hash strings, hostile text hooks, no-read denial, signed synthetic GrantAudit/ProcureGuard positive cases, opposite-product denial and AST callsite checks
- `.github/workflows/desktop-source-evidence-r385.yml` — Windows/Ubuntu Python 3.12 R422 + inherited R11 tests in ordinary and `-OO -W error` modes

## Local testing and limits

A Linux local replica of the R422 entitlement module with **simplified filesystem reader dependencies** (not a trusted full Git checkout) ran the reproduced 14 regression methods:

- Python ordinary `-W error`: **14/14 PASS**
- Python optimized `-OO -W error`: **14/14 PASS**
- Controlled pre-fix guard substitution: **7 failing assertions** including source-path redirection and early-verification regression
- The positive tests exercised *real* ephemeral Ed25519 signatures through `cryptography`, with synthetic documents only; no real license key was used

The local reader stubs do **not** validate the repository's descriptor-bound entitlement reader, the exact committed test blob on Windows, the full six-financial-engine suite, genuine Windows x64 binaries, premium download controls or production signing. Hosted CI evidence must come from the pinned draft head and complete checkout; do not claim these local passes as a release qualification.

## Remediation / next highest-impact gate

Hosted GitHub Actions has been failing at job setup, with zero recorded execution steps and missing job logs; cause **unconfirmed**. Verify the repository/org Actions billing and runner eligibility, then rerun the exact draft commit on Windows and Ubuntu. Require R422/R11 cryptographic tests, R419–R421 reviewer tests and full finance/release gates. Validate genuine six Windows x64 executables, Defender, keyboard/NVDA/high-DPI, SHA-256 receipts and independently verified access-denied premium downloads before any QD or founder release review.

**No merge, publication, downloads, entitlement issuance or release authorization.** Independent QD approval and explicit founder sign-off are mandatory.
