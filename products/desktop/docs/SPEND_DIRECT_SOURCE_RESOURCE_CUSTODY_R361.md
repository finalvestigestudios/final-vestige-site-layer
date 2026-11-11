# R361 — SpendMap direct-source resource custody

**Status:** DRAFT ONLY. No release, site change, entitlement change or financial/compliance approval.

## Threat / acceptance gap

The standalone CSV reader rejects imports larger than 64 MiB, but the reusable
`validated_spend_rows` / `summarize_spend` direct-Python interface receives
already-materialized dictionaries and could accept arbitrarily large `vendor`,
`category`, or even unused extra values. These are later retained, normalized,
indexed and rendered as financial evidence. The 200,000-row count cap alone
cannot bound text memory, CPU or output amplification. Python lone surrogates
can also survive the direct API, even though a real UTF-8 CSV cannot contain
those Unicode codepoints. The legacy full-report writer eventually checks
serialized bytes but this is **too late** to prevent heavy aggregation and
callback effects.

## Implemented

- New `SpendSourceBudget` checks **every retained dict key and value** in a
  detached native row, before **any** user-supplied vendor/date/money callback.
- Limits: **64 columns per row**, **1,048,576 Unicode codepoints per key/value**,
  and **64 MiB aggregate UTF-8 key/value text plus two bytes of framing per
  field** across the entire direct report. The total is intentionally not a
  reconstruction of original CSV bytes; the actual file importer separately
  validates and hashes its descriptor-owned snapshot.
- Unicode source distinctions including NBSP survive unchanged. Invalid
  surrogate sequences and custom string/dict behavior are rejected; failure
  messages contain no source cells or hidden exception context.
- Existing frozen-row, Decimal, calendar, vendor-session, provenance,
  no-partial-row and human-review behavior is preserved. Normal small CSV
  imports are unchanged. No customer data, telemetry or network calls added.

## Verification ledger

Focused `test_spend_source_budget_r361.py`: 25 `unittest` methods covering
exact limit edges, multibyte UTF-8 expansion, aggregate budget, category and
unused fields, native types, surrogates, secret redaction and source immutability.
The 10 new full-engine / actual CSV workflow tests
`test_spend_source_budget_engine_integration_r361.py` require the complete
repository and must **not** be described as executed until a genuine run is
recorded. Hosted Ubuntu + Windows gating commands are required before merge.

## Remaining release gates

GitHub Actions runners currently fail before steps begin (upstream CI blocker;
root cause not verified). Full repository regressions, 22 authentic AES-GCM
cases, native Windows 11 x64 acceptance, Defender, SHA-256, accessible GUI
smoke checks and protected premium download/payment/license gates remain
pending. No production/WordPress publication without independent QD and
founder authorization.
