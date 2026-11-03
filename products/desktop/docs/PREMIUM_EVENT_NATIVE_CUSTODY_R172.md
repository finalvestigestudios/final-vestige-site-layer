# R172 — Native-stored financial event classification (DRAFT / RELEASE HOLD)

## Threat model and observed behavior

Two premium, locally executed review engines distinguish incoming claims from credits
(GrantAudit Studio Pro) and invoices/receipts from explicit credit/return movements
(ProcureGuard Studio Pro). Their separately callable Python classifiers previously read
`row.get(...)` and coerced arbitrary objects with `str(...)`. A caller-supplied
`dict` subclass could store `claim_type="credit"` while returning `"claim"` from
`.get()`, or store `event_type="return"` while returning `"receipt"`.
The stored reversing movement could then enter the wrong gross/credit calculation.
Even absent malice, arbitrary objects could invoke formatting hooks when classified.
The ordinary CSV importer creates native dictionaries and was not the source of this
specialized direct-API attack.

## Implemented contract

- Both classifiers now copy physical `dict.keys`/`dict.items` storage using
  `snapshot_event_record` before classifying, instead of consulting overridden
  `get`, `keys`, `items`, `__getitem__`, or iteration views.
- `dict` subclasses with genuine built-in `str` keys are allowed, but non-dict
  mappings or forged/subclassed field names fail closed. Values must be exact
  built-in `str` (or `None`/empty as the established default), not a custom
  object or `str` subclass with hidden hooks.
- Case/whitespace normalization and `None`/missing/empty defaults remain the
  same. Whitespace-only or unsupported event/claim types still fail.
- Invalid types and unsupported values never appear in error messages.
  Only canonical ASCII CSV physical lines >=2 appear in diagnostics; all other
  citation values yield `?` without invoking arbitrary `__str__`.
- Only the classification boundary changes; no source files, payment states,
  review history, report schema, Decimal values, premium entitlement gates,
  private package handling or network settings change.

## Verification

27 synthetic `unittest` methods in
`tests/test_premium_event_custody_r172.py` cover forged mapping views,
str subclasses, non-dict mappings, private hooks, source-citation poisoning,
normalization/default compatibility, source immutability, and direct
`review_line` / `_parse_claims` financial classification integration.
`scripts/safe_unittest_r172.py` checks the **exact** method inventory,
runs with stdout/stderr redacted, fails on missing/skipped/failing methods,
and reports no source customer data. The mandatory desktop CI workflow invokes
it under standard Python and `-OO` on both Ubuntu and native Windows.
Expected strict coverage: **27 × 2 modes × 2 OS = 108 executions**.

This is not a proof that arbitrary Python objects or caller-supplied claim
digest strings are independently authenticated. Other direct APIs may need
their own input-custody validation. Classification is review-only; no finding
constitutes eligibility, authorization or payment approval.

## Release blockers (unchanged)

Six executable candidates remain **UNRELEASED**. A green Actions run is internal
source/build evidence only and does not replace independent physical Windows 11
acceptance with 46 accessibility observations, actual Defender/EDR assessment,
code signing, secured premium distribution, independent QD exact-head approval
or founder authorization. Never publish a premium binary without access control.
