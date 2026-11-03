# Labs R169 — Invoice Twin report-provenance source custody

**Status: DRAFT / RELEASE HARD HOLD.** This is an internal source change, not a
released Windows executable, an invoice-fraud determination, or a compliance
approval. It must remain in a stacked draft PR pending independent QD review.

## Defect and scope

R165–R168 hardened the `candidate_pairs` *discovery* API. The separate public
`attach_invoice_provenance` *report* API still accepted caller-supplied dict
subclasses, subclassed audit strings and list subclasses. In particular,
`row.get("row_a")`, `row.get("row_b")` and `row.get("status")` could be
overridden to show values unlike actual dictionary storage. Subclassed `str`
values may override hashing/equality before the duplicate-pair check. A
malicious direct caller could therefore attach source-line references and
candidate identifiers to misleading records.

## Behavior after R169

* Require an exact built-in `list` for the collection, and a dict record;
  accept ordinary dict subclasses only when their *underlying* values pass.
* Reject any non-builtin-str stored field name before copying. Read actual
  `dict.items(row)` and `dict.keys(row)` through Python's built-in
  descriptors; never trust override hooks. Own an ordinary dict snapshot.
* Require exact builtin `str` for the source SHA, both physical-line
  citations and candidate status. Existing lowercase SHA, canonical row
  number, duplicate undirected pair, status-enumeration and max-count rules
  remain unchanged.
* Derive candidate references exclusively from the validated owned snapshot,
  and overwrite any caller-supplied `candidate_ref` / `source_sha256`.
  Preserve other report columns unchanged. No private values in errors.
* The identifiers remain deterministic source locators, **not signatures or
  proof of source authenticity, payment authorization or fraud**.

This closes the post-discovery gap without changing ordinary engine
`invoice_twins` output, CSV schema, Decimal calculation, money rounding,
local-only processing, premium locks or the original input files.

## Validation contract

`products/desktop/tests/test_invoice_report_snapshot_r169.py` contains **28
synthetic methods** exercising trusted primitive snapshots, forged dict
getters/iterators/items, hash/equality impostors, late invalid fields, duplicate
undirected pairs, privacy and deterministic SHA-bound review IDs.

Run locally from the repo root:

```sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r169.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r169.py
```

The strict runner verifies the exact 28-case inventory and fails on errors,
skips, missing cases or unexpected successes. CI repeats both modes on Ubuntu
24.04 and native Windows (planned **112 focused executions**, not a passed
result until actual job evidence is collected). The inherited six-engine
source suite, native six-candidate packaging, offline smoke/integrity checks
and private premium-lock gates are still mandatory; no CI job may publish
public EXEs or unrestricted premium artifacts.

## Release blockers and next action

After exact-head Linux/Windows verification, the highest priority remains
independent physical Windows 11 accessibility acceptance (**46 human
observations**), actual Defender/EDR, signing, authenticated premium
distribution, QD review and explicit founder approval. Internal CI candidate
smokes do not substitute for those steps. No changes to production/WordPress.
