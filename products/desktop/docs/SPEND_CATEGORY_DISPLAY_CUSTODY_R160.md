# R160 — fail-closed SpendMap CSV category display identity (DRAFT / HOLD)

## Risk

The source SpendMap aggregation keys categories by **raw source text**, but its CSV
export protects spreadsheet users by prefixing formula-like cells with an
apostrophe. That display transformation is not one-to-one: source categories
`=A1` and `'=A1` become the same visible CSV category `'=A1`.
Without a preflight, the generator can create two distinct financial category
rows that appear to have the *same* category. Downstream pivots or reviewers
could silently conflate them. The R159 independent verifier would refuse
duplicate visible buckets, but the producer still created an unusable report.

## Solution

- **Generator:** before creating any report file, inspect all summarized
  (normalized vendor, month, raw category) buckets. Reject when two
  different raw categories under the same vendor/month yield an identical
  spreadsheet-safe category. The error is generic, reveals no client values
  or file paths, and does not write an output. Different vendors or months
  remain independent; repeated *identical* categories aggregate normally.
- **Independent verifier:** perform an explicit source-pinned collision check
  before comparing native exported report rows. It never approves a
  CSV whose source has ambiguous display-category identity, including one
  produced by an older generator that lacked the preflight.
- **Evidence:** input SHA-256, vendor-month line membership, source CSV line
  citations, original files, Decimal cent precision, and the R159 exact
  25-field native report schema remain unchanged.
- **Privacy / compliance:** all processing is offline. These controls only
  distinguish source categories. They do not detect fraud, certify an
  organization's accounting policy, or approve invoices or payments.

## Reproduce with synthetic data

Use a CSV with headers `vendor,amount,date,category,note` and two rows for
the same vendor and month, one with category `=A1`, another with category
`'=A1`. A direct `engine.spend_map` call MUST raise a category ambiguity
error **before writing a report**. Use a different vendor or month and both
rows may be exported separately. If separate same-key categories legitimately
exist, an operator must resolve the categorization in an **independent copy**
of the input; never silently overwrite or normalize source originals.

The R160 strict gate has **30 synthetic methods** and is wired to Ubuntu and
native Windows, normal and optimized Python (`-OO`): **120 planned targeted
method executions**. From repo root:

```sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r160.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r160.py
```

Method count, names, class, skips and unexpected passes are enforced; the
runner prints a bounded summary rather than confidential input.

## Release boundary

This is a **stacked draft feature** targeting R159 draft PR #771, not main
or production. **No Windows download, distribution, WordPress or premium
entitlement edits are authorized**. Windows 11 physical human accessibility
acceptance (46 observations), actual Defender/EDR inspection, code signing,
authenticated premium delivery, independent QD approval and founder release
authorization remain outstanding. CI passing does not equal distribution.
