# R168 — Invoice Twin Scout plain-field and exact-Decimal custody

Status: **draft engineering change / release HOLD**. Tracks issue #73; stacks
on R167, not production. Offline synthetic tests only. Never interpret a
duplicate candidate as fraud, a payment decision, or a compliance approval.

## Residual defect after R167

R167 correctly copied **stored** dictionary entries rather than calling an
untrusted mapping's overridden methods. However, it accepted subclasses of
`str` for physical CSV rows and normalized vendor/invoice identifiers, and
subclasses of `Decimal` for amounts. A direct engine caller could supply
objects that passed regex/finite/precision checks while redefining Python's
`__hash__` or `__eq__`. These special methods govern invoice grouping and
source-row uniqueness. An attacker could make two visibly different invoice
keys compare equal, or split amounts into misleading candidate buckets.

Stored dictionary keys could themselves be `str` subclasses. Even when the
outer dict was copied safely, an equality-forging field name could impersonate
an audit field during `record.get("row")` or other value lookup.

This is a **direct API boundary** risk; the normal bounded CSV importer
produces built-in `str` and `Decimal` values, not hostile subclasses.
Nonetheless, the engine must refuse contradictory evidence rather than
silently assemble false audit candidates.

## Implemented invariant

Before copying stored entries, reject every source **field name** whose type
is not exactly built-in `str`. Use `dict.keys(record)` to enumerate the
actual stored keys without consulting a dict subclass's overridden `keys`.
Then snapshot through `dict(dict.items(record))` as R167 requires.

Validate source-row citations, normalized vendor and invoice keys with
`type(value) is str`, and exact amounts with `type(value) is Decimal`.
Do not coerce subclasses into strings or decimals: that could invoke their
untrusted hooks, erase original evidence or perform rounding. Reject with
generic private-data-safe errors; no report is emitted. Plain data is still
sorted by canonical physical line, processed with exact Decimal grouping,
and reviewed by a human.

## Tests and evidence discipline

* `tests/test_invoice_exact_primitives_r168.py`: 26 synthetic regression
  methods covering forged equality/hash, benign subclasses, Decimal special
  methods, stored field-name aliases, dict-override bypass, late invalid input,
  private-data-safe failures and standard exact/subcent candidate behavior.
* `scripts/safe_unittest_r168.py`: exact 26-method inventory, no skips,
  no unexpected successes, suppressed private traces on normal failures,
  fail-closed when tests cannot be loaded.
* `.github/workflows/desktop-build.yml`: mandatory R168 normal and
  Python `-OO` tests on **Ubuntu and Windows**, 26 × 2 × 2 = **104**
  focused test executions when all four gates pass, plus the inherited
  six-app source, smoke and private Windows packaging gates.
* Do **not** report a passed hosted CI job or Windows executable build until
  the exact-head Actions run, its complete jobs and artifacts say so.
  Static code inspection is not equivalent to execution.

## Operator and release restrictions

Input and reports remain local, source data is never uploaded as telemetry,
and no writes are made to input records. The fix does not add automated
compliance or payment approvals. Never publish an unsigned/unreviewed EXE,
unrestricted premium bundle, or an invented download link. The site's QD
workflow and founder release decision remain authoritative.

Still required before release: an independent physical Windows 11 acceptance
run with 46 accessibility observations (including keyboard/NVDA/contrast and
scaling), actual Defender/EDR evidence, code-signing acceptance, audited
premium entitlement and protected distribution, QD approval, founder sign-off.

## Next highest-impact engineering step

Verify exact-head Ubuntu and Windows jobs and all six private Windows x64
candidate checks. Fix any true failures **only on the isolated draft
feature branch**. Then hand verified private candidates to the independent
physical Windows 11 reviewer; no automatic promotion to production.
