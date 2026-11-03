# R166 — Invoice Twin Scout validation ownership and split-view dictionary custody

## Defect and impact
R165 copied each invoice dictionary after validation, protecting against an ordinary generator reusing a mutable mapping. But the direct `candidate_pairs` API accepts `dict` subclasses. Such a subclass can override `.get()` to present different values to the validator than the values in its backing dictionary. On R165, validation used the overridden `.get()` while `dict(record)` later copied the actual backing values. An attacker, test harness, or defective local integration could therefore cause unvalidated dates, keys, monetary values, or physical source-line identities to enter the candidate engine; the result might suppress genuine matches, fabricate matches, produce confusing exceptions or destabilize provenance. This is a local untrusted-caller issue, **not evidence of remote code execution**.

## Fix
Snapshot the incoming dictionary once, **before the first field lookup**, then validate and subsequently match using only the owned plain dictionary. This binds the validated `row`, `v`, `inv`, `amt` and `dt` to the exact values used for source-row sorting and matching; it does not call the input object's overridden `.get()`. The R165 reused-dictionary safety guarantee continues to hold. No coercion, precision rounding, additional network access, telemetry or new compliance decisions were added. The input is not modified. Extras are preserved for backwards compatibility with existing local report builders.

## Deterministic regression gates
- `products/desktop/tests/test_invoice_validation_custody_r166.py`: 26 synthetic adversarial methods. Malicious `dict.get()` versions conceal bad physical rows (including a duplicate), dates, nonfinite/oversized/overprecise amounts, malformed invoice/vendor keys or missing source fields. Positive tests ensure real stored data wins over forged getters and subclass getter side effects are never invoked. They also verify copied evidence, hostile Decimal contexts, source privacy and no partial result on a late invalid row.
- `products/desktop/scripts/safe_unittest_r166.py`: fails closed on method-inventory drift, skips, unexpected successes, failures or errors, while suppressing untrusted test output.
- `.github/workflows/desktop-build.yml`: mandatory 26 methods × normal/`-OO` × Ubuntu/Windows = **104 planned focused method executions**, in addition to inherited suite and six offline Windows candidate checks. Only successful exact-head CI conclusively certifies these; do not infer a pass solely from the test source.

## Developer reproduction (offline)
From repository root, with `PYTHONPATH=products/desktop`:
```sh
python products/desktop/scripts/safe_unittest_r166.py
python -OO products/desktop/scripts/safe_unittest_r166.py
```
The suite never opens private customer input; all fixtures use invented vendors, invoices and amounts.

## Release and review
Branch stacks on R165 draft PR #814, **not** the production branch. Preserve independent QD review. No direct production changes, downloadable binaries, public premium packages, signature assertions, physical Windows 11 acceptance, or payment authorization. The 46 physical Windows 11 accessibility observations, genuine Defender/EDR, signing, protected premium distribution, QD and founder approval remain held. Next highest-impact release action: conduct independent physical Win11 and protected-distribution acceptance; before that, obtain exact-head green Ubuntu and Windows CI for this PR.
