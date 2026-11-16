# Final Vestige Labs R462 — reject ambiguous source-check receipts

**Status: DRAFT / SOURCE ONLY / HARD RELEASE HOLD** · Issue [#73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R461 draft [#2684](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2684), exact parent `17fdddd84542b2d6d6981cb0184c7c625a9946cc`, not main.

## Defect and behavioral contract

Python's default `json.loads` silently resolves repeated JSON object keys by taking the last value. A child receipt such as `{"release_authorized":true,"release_authorized":false}`, `{"tests":0,"tests":13}` or nested `{"normal":"fail","normal":"pass"}` can appear unambiguous after parsing even though its raw record contains contradictory assertions. This is unacceptable evidence custody for local-first financial tools.

R462 adds a shared strict decoder using `object_pairs_hook` at **all nesting levels**, rejecting duplicate decoded keys, nonstandard non-finite constants, invalid JSON and wrong input types. Errors use fixed private-data-free text and never replay untrusted receipt content. The decoder is wired into the R459 regression receipt, R460 six-application/two-mode smoke receipt and R461 child-to-full-source-digest binding. Existing length limits, integer-count guards, exact source SHA-256 equality, return-code/source-continuity checks and `release_authorized=false` remain. This does not parse customer financial CSVs and does not change Decimal arithmetic or compliance approvals.

## Artifacts / reproducibility

- `products/desktop/offline_json_receipt_r462.py`: strict JSON decoder.
- `products/desktop/tests/test_private_json_receipt_r462.py`: **25 methods** including duplicate root/nested/escaped keys, disputed success flags/counts/digests, nonfinite/malformed values, fixed redaction, valid backwards compatibility and R459/R460/R461 consumer integrations.
- `offline_regression_gate_r459.py`: R462 as the **sixth** source regression module (6 modules × normal and `-OO` = 12 subprocess test-mode runs), strict decoder in the source fingerprint. No source-only receipt can authorize an executable.
- Adjusted R459 and R461 historical synthetic test expectations from 10 to 12 modes.
- Ubuntu/Windows source CI workflows run R462 methods normal and optimized; Ubuntu prebuild job adds previously missing R461 test step. No deployment or upload-permission changes.

## Local execution evidence, limited scope

On Linux Python, the exact new strict decoder logic and 25-method test source ran with **locally reconstructed** R459 regression parser, R460 smoke parser and R461 digest binding: **25/25 normal PASS plus 25/25 `-OO` PASS = 50 passing focused test executions**, with `-W error`. Python compilation passed. This is NOT a full checkout, native Windows, or proof that the new committed tests pass against all original repository modules. Repeat on an authorized complete checkout:

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p test_private_json_receipt_r462.py
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p test_private_json_receipt_r462.py
python -B products/desktop/offline_regression_gate_r459.py
```

Full fallback should require 12/12 actual regression-mode runs and 12/12 six-launcher smoke statuses against a stable full-source digest; it has **not** been executed here.

## Release gates and next highest-impact step

Prior R461 hosted Ubuntu/Windows Actions both failed before their first test step. Inspect the exact R462 runs; a zero-step job is NOT a pass. Owner to inspect Actions failure annotations, billing/spending limits, repo runner permissions/eligibility and restore execution. Then perform complete six-app regression tests, genuine Windows x64 builds, installed launchers/keyboard/accessibility checks, Defender scans, checksum custody and protected premium download validation. Independent QD review and explicit founder approval remain mandatory before merge/site update/license issuance/publishing. No premium file or download URL was published.
