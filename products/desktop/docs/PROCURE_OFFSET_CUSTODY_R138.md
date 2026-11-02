# R138 — ProcureGuard Studio Pro: source custody and offset-row candidate trail

**Status:** DRAFT / RELEASE HOLD. This is not an approved payment, automated compliance ruling, customer binary, or released product.

## New private report fields

The existing ProcureGuard three-way CSV retains its original column order and matching/price/credit/return flags. Five appended columns provide reviewer navigation:

- `po_source_sha256`, `invoice_source_sha256`, `receipt_source_sha256`: lowercase SHA-256 of the **exact CSV snapshot bytes parsed in this run**. Each per-PO/line output repeats the three byte digests, including an empty-but-valid imported CSV. They can be checked against the separately published two-file evidence bundle inventory.
- `credit_source_line_links`: JSON array (possibly `[]`) with one object per credit memo event: `{"offset_row":"3","target_rows":["2"]}`.
- `return_source_line_links`: same structure for a return and candidate original receiving rows.

Row numbers are **physical CSV starting lines**, not logical record ordinals. Quoted embedded newlines and a UTF-8 BOM are handled by the pre-existing snapshot parser. Only physical row references appear in the nested JSON; source document IDs and financial text are *not* repeated there.

Candidate targets are computed using exactly the existing normalized matching key, scoped to one **purchase-order + line** group and original invoice/receipt event type. A missing/unmatched reference gets an explicit empty array. More than one candidate stays visible, in deterministic input order, rather than silently selecting a supposed true match. Existing `unlinked_*`, `normalized_*_link_review`, repeated-document, and amount-variance flags remain authoritative **review cues only**.

### Threat model and limitations

These are **navigation and chain-of-custody aids**, not signed attestations or authorization decisions. Unicode/case/punctuation normalization can produce ambiguous candidates; the original review flags remain and humans must confirm original documents. SHA-256 binds bytes but an attacker able to replace an entire bundle could replace both CSV and its inventory. For independent authenticity, the reviewer should retain an externally authenticated inventory SHA-256 pin and use the existing `fvs_suite.procurement_verify` offline verifier before accepting evidence. Original inputs stay local, unmodified and absent from public artifacts. No account, telemetry, network calls, changes to monetary Decimal logic, payment approval or premium unlocking were added.

## Reproduction / acceptance gates

The 22 synthetic integration tests in `products/desktop/tests/test_procurement_offset_custody_r138.py` open real temporary CSV files, run the shipping `engine.procure_guard` entrypoint and inspect the actual staged/published reports. They cover all three SHA-256s against parsed snapshots and the inventory, ordinary and ambiguous credit/return links, unlinked offsets, normalization review flags, source order, quoted multiline physical citations, BOM, missing inputs, custom policy, repeat export determinism, source immutability, mutation-before-manifest failure without package publication, malformed quantity, Decimal context isolation, and cross-PO isolation.

The zero-skip inventory runner `products/desktop/scripts/safe_unittest_r138.py` requires **exactly 22 named real tests**, suppresses private sample data in CI logs, and returns nonzero on skips/failures/missing coverage. Required workflows run the runner in both default and `python -OO` modes on Ubuntu and Windows (88 targeted test executions if both jobs complete). Existing full-suite, Windows x64 native executable, locked premium UI, accessibility and sealed transfer gates remain unchanged.

## Release blockers

Physical Windows 11 reviewer custody and all 46 hands-on accessibility observations, genuine Defender/EDR scan, code signing, customer-facing premium license/payment and protected download flow, independent QD validation, and founder approval. Never publish premium EXEs or private financial evidence. PR is draft and stacked on R137, **not main**.
