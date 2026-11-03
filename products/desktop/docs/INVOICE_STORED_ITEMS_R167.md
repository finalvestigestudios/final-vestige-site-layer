# R167 — Invoice Twin underlying-dict storage custody (DRAFT/HOLD)

Tracks issue #73; depends on draft R166 PR #824. This is an internal engineering sprint, **not a distribution approval**.

## Root cause

R166 moved validation before matching and copied each input using a normal dict constructor, protecting against dict subclasses that override get(). However, Python can consult an input dict subclass's overridden keys() and __getitem__() when copying an object that also overrides __iter__(). Such a subclass can falsely advertise a valid physical source row, canonical vendor/invoice identifiers, a parsed date and an exact Decimal amount while the underlying dict stores different, invalid data. That advertised view becomes the record used in the resulting audit evidence.

R167 invokes the built-in descriptor dict.items(record) to enumerate actual underlying dict storage and then copies those pairs to a new ordinary dict. This avoids dispatching through untrusted subclass keys(), __iter__(), __getitem__(), get() or items() implementations. Existing source validation and canonical physical-row sorting operate on the owned copy. No records are sent to a network service; source files are not modified.

## Security and privacy contract

- Bound direct input to 200,000 source records; unique, canonical physical CSV row identifiers remain mandatory.
- Dates must be actual calendar date objects (not datetime); money must be bounded, finite exact Decimal. No floats or automatic compliance approvals.
- Normalized vendor and invoice identifiers must be ASCII. Malformed inputs stop candidate generation before saving.
- Diagnostic errors must not include private source values.
- This change closes dict-subclass view spoofing; it does not assert protection against arbitrary hostile Python object execution, concurrent threads modifying a mapping, or compromised source code. Normal user imports are bounded CSV snapshots.

## Tests and CI

26 deterministic synthetic regressions cover forged source rows, dates, money, normalized keys, duplicate rows, wrong exact/near candidate labels, source-order anchoring, signed-credit review, result mutation isolation, fail-closed validation, no value leakage and plain-dict compatibility. A strict source-owned runner fails on missing, duplicate, skipped or unexpected methods.

The desktop-build workflow executes the inventory under normal and optimized Python on Ubuntu and Windows. This is **26 methods x 2 Python modes x 2 operating systems = 104 required focused test executions**, in addition to inherited six-engine source and Windows candidate gates. The tests are only claimed as passed after exact-head CI evidence confirms them.

## QD and distribution hold

This branch is draft-only and stacked on PR #824. No production merge, public binaries, unrestricted premium links or automated compliance approvals. Keep independent QD review and founder authorization mandatory. Physical Windows 11 accessibility verification (46 observations), genuine Defender/EDR assessment, signing and protected premium distribution remain separate release blockers.

## Next

Verify exact-head CI and native Windows six-app candidate build; correct any regressions here. Then prioritize real physical Windows 11 acceptance and entitlement custody before public distribution.
