# R174 — SpendMap Lite native stored source-record custody

**Status:** draft engineering increment only. No release or QD approval.

## Defect and boundary

The public \`validated_spend_rows\` direct Python helper formerly used
\`isinstance(record, dict)\` and then \`record.get(...)\`, iterating \`records\`
and invoking caller-provided \`normalize_vendor\`/\`parse_money\` callbacks.
A dictionary subclass could present physical row 99, amount 0.00 and vendor
FORGED through \`.get()\` while actually storing row 2, amount 10.25 and
vendor ACME. That mixes forged provenance with a caller-provided source
SHA-256. Other Python subclasses could inject custom hash/equality/Decimal
operations into report grouping. No ordinary CSV user can construct these
Python subclasses; this hardening is for direct API use and tests.

## Implementation

- Require an actual built-in \`list\` so overridden list iteration or length
  cannot substitute arbitrary records.
- Require dictionary storage, and reject any dictionary key whose **exact**
  type is not the built-in \`str\`, before copying.
- Copy each source row from bound \`dict.keys\`/\`dict.items\` native storage,
  never from overridable subclass \`.get\`, \`.items\`, \`.keys\`, \`__iter__\`,
  or \`__getitem__\`. Validate and return this owned copy, not the caller's row.
- Require exact built-in \`str\` for source row, vendor, date, amount and
  category cells and for the normalized vendor key. Reject Decimal subclasses
  before arithmetic. This does not coerce floats or round away subcents.
- Keep existing 200,000-record limit, canonical physical start lines,
  cent precision, bounded Decimal representation, privacy-safe errors,
  original row ordering, SHA-256 source association, and review-only signals.

One row is copied at a time; a callback cannot retroactively change that
row's parsed evidence. As before, this is **not** source authentication and
does not freeze or authenticate later rows or a caller-supplied digest.
Production file import already uses descriptor-verified immutable bytes.

## Reproducible verification contract

Only synthetic values are present in the new test file:

\`PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r174.py\`

\`PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r174.py\`

Runner inventories **27 distinct test methods** and returns nonzero if a
method disappears, gets skipped, fails, or cannot be discovered. The desktop
GitHub Actions workflow invokes this runner twice on Ubuntu and twice on
Windows, for **108 expected focused executions**, if runners allocate.
Independent full-source tests and all six source smokes remain in CI.

Tests cover forged mapping views, user-controlled string/hash/Decimal hooks,
callback mutation of current source record, actual source-row and money
custody, category fallback, credits, precision traps, duplicate physical
references and private error messages. No real financial data is used.

## Remaining release HOLD

Physical Windows 11 accessibility witness (46 independent observations),
actual Defender/EDR scan, code signing, protected premium distribution,
independent QD exact-head review and founder release authorization.
A green CI job is **not** a Windows 11 physical witness or approval.
Do not publish executables, update production, or expose premium artifacts.
