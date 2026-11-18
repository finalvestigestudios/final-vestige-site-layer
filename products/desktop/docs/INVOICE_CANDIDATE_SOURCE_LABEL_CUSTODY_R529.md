# R529 — Invoice Twin Scout: original label custody during candidate discovery

**Status:** SOURCE ONLY / DRAFT / QD AND FOUNDER RELEASE HARD HOLD.  
**Date:** 2026-11-18. **Issue:** #73. **Parent:** R528 draft PR #3034 at `da735c02f715c1a8c4acfaee8f5cdb729d40f37a`, not production `main`.

## Defect and scoped correction

The public `candidate_pairs()` discovery API accepted normalized vendor (`v`) and invoice (`inv`) keys that were syntactically valid but contradicted accompanying original `vendor` and `invoice_number` labels. It could then classify a fabricated exact-key match or near match as a candidate **before** the downstream `review_flags()` human-review guard ran. This is a source-custody defect in the direct Python integration API, **not** evidence of an actual fraudulent payment or an observed vulnerability in normal CSV processing. `engine.invoice_twins()` already derives its keys directly from the imported source labels.

R529 checks **each provided** original label against its asserted key inside `_validated_records()`, after taking an owned native dictionary snapshot and validating canonical row, date, Decimal and normalized-key types, but **before** grouping, sorting, or producing candidates. Labels must be exact native strings within the existing importer limit; mismatched keys fail closed with fixed, financial-value-free errors. `normalize_key()` retains its independent Unicode expansion bound.

**Compatibility:** The historical low-level API accepts records containing only `row`, `v`, `inv`, `amt`, and `dt`; those **key-only** records still work but are not proof of source-label authenticity. Partially supplied labels are checked individually. Valid punctuation/whitespace normalization, ASCII case, Unicode uppercase expansion, same-vendor exact Decimal amount comparisons, deterministic source-row order, and seven-day near matches remain supported. This deliberately does not change R528's `review_flags()` behavior for **manually provided** flagged evidence: there, mismatches remain explicit human-review warnings.

## Artifacts and focused evidence

- Production: `products/desktop/fvs_suite/invoice_match.py` (candidate source-label guard).
- Synthetic regression class: **17 new `InvoiceCandidateRawLabelCustodyR529` methods** in already-inventoried `products/desktop/tests/test_invoice_review_custody_r444.py` (forged exact/near keys, native/bounded labels, key-only compatibility, punctuation/Unicode collisions, snapshot, nonmutation, private-text-free failures).
- No new Python source/test module or immutable command was added: the **416-command source inventory remains unchanged**.
- **Executed, but weaker than repository tests:** a reconstructed Linux CPython 3.13.5 focused behavior probe at `/tmp/invoice_r529_probe.py`, not the actual committed repository module, passed **17/17 standard** and **17/17 `-OO`** (34 focused executions). An intentionally disabled label-validation negative control failed **11/17**; remaining six were compatibility/positive cases. This confirms the probe can distinguish old vs proposed behavior, **not** that the committed test class or full engine has passed.
- **Not executed:** the complete committed R444 regression module, the pinned 416-source-command matrix, native Windows x64 executable packaging/smoke/Defender/accessibility/entitlement and checksum validation, and independent QD review.

## Required reproducible verification

```text
cd products/desktop
python -m unittest discover -s tests -p test_invoice_review_custody_r444.py -v
python -OO -m unittest discover -s tests -p test_invoice_review_custody_r444.py -v
```

Then run `python -B -W error products/desktop/scripts/source_evidence_runner_r509.py` from repository root with the pinned cryptography dependency, followed by Windows x64 build, six-app smoke, Defender, accessibility, native file/installer signature and SHA-256 verification. Any break in inherited tests is a hard HOLD until the exact committed code and tests pass.

## Distribution and approval

All four free utilities (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and both premium utilities (GrantAudit Studio Pro, ProcureGuard Studio Pro) remain **unreleased**. No WordPress changes, downloads, EXEs, pricing, entitlements, license controls or raw customer data were created. Source processing remains local; money remains Decimal-safe; flags never approve payment, claim fraud or certify compliance.

Existing GitHub Actions blocker #75 records six jobs on R528 failing before step start; root cause remains unconfirmed. **Smallest unblock:** repository administrator verify hosted Actions billing/spending limits, workflow permissions and runner eligibility; demonstrate one actual job step log before consuming full Windows build minutes. Independent QD plus explicit founder release approval remain required. Do not merge, publish or expose premium files under this sprint.
