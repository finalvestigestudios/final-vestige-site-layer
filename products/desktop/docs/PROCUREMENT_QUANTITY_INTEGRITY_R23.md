# R23 — exact procurement quantity grammar and audit-safe failures

**Scope:** Final Vestige Labs, ProcureGuard Studio Pro (pre-release), issue #73.
This document describes source behavior, **not** a verified Windows x64 binary,
payment authorization, compliance certification, or a QD publication approval.

## Financial correctness failure removed

The previous `engine.qty` called `Decimal(text.replace(",", ""))`.
Consequently `1,2,3` was accepted as quantity **123**, `1e3` as **1000**,
and exceptions could echo the customer's raw input. Unlike a clear input error,
this could produce plausible but false three-way quantities, net totals,
threshold flags, and audit evidence. R23 uses a whole-string ASCII grammar,
then converts to `Decimal` only after validating punctuation.

## Supported quantities

- Unsigned ordinary decimals: `0`, `12`, `12.5`, `.5`, `1.`.
- Explicit positive prefix: `+12`; surrounding whitespace is ignored.
- Correct thousands groups: `1,000`, `1,234,567.125`.
- Maximum numeric quantity `1,000,000,000`; at most **8 meaningful
  fractional decimal places** (trailing zeros do not add precision).
- No binary float inputs to the Python API. CSV input values are strings.
  Every accepted value is represented by `Decimal`, never binary float.

## Rejected rather than silently transformed

Examples: `1,2,3`, `1,00`, `1,,000`, `12,34.50`, `1e3`, `NaN`,
`Infinity`, `-1`, `-0`, currency signs, non-ASCII digits, more than
8 meaningful fractional places, or input text longer than 80 characters.
Errors do **not** reproduce the raw value in exception messages.

ProcureGuard's PO, invoice, and receipt import paths all call the common
parser through `review_line`. Credit and return movements **remain explicit**
`event_type` values, not a negative quantity convention. Malformed
quantities must stop review generation before a report or evidence manifest
is written. This does not imply that otherwise matched rows approve payment.

## Backwards compatibility and release limitations

Previously accepted exports containing scientific notation, malformed comma
groups, or quantities more precise than eight decimal places must be corrected
**at the originating system with human verification**; do not auto-rewrite or
assume a desired numeric interpretation. Keep source originals, compare new
provenance before acting on reports, and never treat pre-release report output
as a compliance or payment decision.

## Tests and next evidence needed

New regression module:
`products/desktop/tests/test_quantity_lexical_integrity_r23.py`
(12 test methods: exact parser, malformed lexemes, privacy errors, three-way
file imports, no partial outputs and typed credit/return review).

Run locally in a trusted full checkout:

```bash
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p 'test_quantity_lexical_integrity_r23.py' -v
```

On trusted Windows 11 x64 also run
`products/desktop/scripts/verify-windows-candidate.ps1 -Build`; retain six
actual executable hashes, native smoke evidence, AV/signing results, and gated
premium fulfillment evidence. The existing GitHub Actions runner failures
must be resolved or independently verified builds supplied for review.
No release until QD approves the website and every binary release gate passes.
