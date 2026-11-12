# R388 — ProcureGuard local price-policy JSON exception privacy

**Issue:** #73. **State:** isolated draft stacked on R387; QD + founder hard hold; no production deploy or release. Scope: **ProcureGuard Studio Pro** local JSON price-tolerance review input; the other five products are unchanged.

## Reproduced gap

`fvs_suite.procurement.load_price_policy` used `raise ValueError("Invalid UTF-8 JSON price policy") from exc` inside its UTF-8/JSON handler. `json.JSONDecodeError.doc` retains full malformed local source data; `UnicodeDecodeError.object` retains the bytes. The public ValueError therefore retained the raw customer document through `__cause__`. The existing stable-file read error likewise used `raise ... from None` *inside* its `except`, suppressing the printed traceback but leaving `__context__` attached.

## Changes

- `fvs_suite/procurement_policy_private_json_r388.py`: strict JSON parser preserving UTF-8 BOM, duplicate-key and nonfinite-value rejection; malformed JSON/Unicode errors are translated **after** the handler. Generic public error strings; no lower-level parser exception chain.
- `fvs_suite/procurement.py`: use parser and translate snapshot-reader failures after their exception handler. Existing stable 8 KiB descriptor read, byte SHA256, version=1, exact Decimal threshold validation, review-only `PricePolicy` behavior, and reject-by-default authorization semantics are unchanged.
- `tests/test_procurement_policy_private_json_r388.py`: 17 source-level unit tests covering valid JSON, invalid UTF-8, malformed documents, duplicates, NaN/Infinity, native-byte-only parsing, and error-chain privacy.
- `tests/test_procurement_policy_privacy_integration_r388.py`: 10 real `load_price_policy` integration regressions for snapshot read errors, malformed input, valid Decimal thresholds, provenance and review-only semantics.
- Independent source-evidence workflow runs both suites under Python normal and `-OO` on Ubuntu and Windows **when runners are available**, without any release, checkout credentials, artifacts or external file sharing.

## Verification boundary (2026-11-12)

- Isolated Linux Python source-level parser tests: **17/17 ordinary PASS + 17/17 optimized PASS = 34/34**.
- Standalone source compilation: PASS for both test files and new helper.
- Genuine full-repository integration: **not yet executed** (must run on exact branch checkout). Native Windows desktop EXE, accessibility, Defender scan and premium download gates: **not verified**.
- No external customer data used; fixtures carry synthetic `CLIENT_PRIVATE` marker only.

## Actions and release hold

Review GitHub Actions runnerless failures for the R387 parent commit (source run #43315883388, desktop run #43315887296). Restore hosted runners (check annotations, organization billing/spending limits, hosted-runner eligibility); execute exact R388 head source + integration tests and real six-engine, AES-GCM, Ed25519/SQLite suites. Independently verify QD and founder approval before merge or release. Never publish untested Windows EXEs or ungated premium downloads.
