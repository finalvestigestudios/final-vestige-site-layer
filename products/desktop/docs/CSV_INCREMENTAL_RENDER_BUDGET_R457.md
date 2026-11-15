# R457 — Incremental CSV render-byte gate (draft only / release HOLD)

**Scope:** Issue #73, shared local-first CSV output for LedgerDiff Lite, Invoice Twin Scout,
SpendMap Lite, Policy Delta Desk, GrantAudit Studio Pro, and ProcureGuard Studio Pro.

## Reproduced resource gap

R454 checks an exact `csv.excel` serialized-row byte budget **after** the caller has
rendered and stored every value in `rendered_row`. The published CSV remains
correctly bounded at 64 MiB, but a direct-API caller with up to 256 columns of
1 MiB source strings can cause the sanitizer to allocate up to hundreds of MiB
of extra escaped strings before the entire row is rejected. This affects local
memory availability; it is **not** evidence of an external breach, and the
source input itself may already occupy memory.

## Implemented in this draft

- `fvs_suite/atomic_reports.py`: reuse a common exact UTF-8/csv.excel field-cost
  function in existing whole-row preflight, and add `preflight_add` to check
  an emitted cell **immediately after sanitization**. Reserve all delimiters,
  CRLF, quote doubling, enclosing quotes and singleton-empty-column syntax.
  The check is order-independent for native mapping entries; unselected extras
  are still sanitized for accepted rows. Early failure intentionally skips
  later row values and never publishes a partial report.
- `tests/test_csv_incremental_render_budget_r457.py`: 13 committed regression
  methods: deterministic seeded native CSV parity; UTF-8 and quotes; singleton
  empty column; narrow bound; first-field early abort in both key orders;
  256-column rejected sanitization count; accepted/unsafe ignored extras;
  exact successful and one-byte-short publication; Decimal lexical fidelity;
  existing evidence never overwritten.
- Both independent source evidence runners (Ubuntu, Windows) and both jobs
  (Ubuntu source-only and Windows pre-packaging) in desktop-build.yml now
  require these 13 tests in standard and Python `-OO` modes.

## Actually executed locally — projection, NOT complete checkout

The isolated Python 3.13 budget arithmetic projection (separate from
committed full-module tests) passed **5/5 standard and 5/5 optimized**
unittest cases with `-W error`. It checked 605 reproducible native
`csv.writer` rows, accepting exact budgets and rejecting one byte below
(**1,210 checks per interpreter mode; 2,420 total**), plus mapping-order,
singleton-empty, early-abort and 256-column scenarios. A synthetic wide row
was rejected after **5/256** 8,000-character sanitized fields.

**Limitations:** The actual committed 13 tests have **not** been executed
inside the complete Git checkout. No real Windows x64 candidate or installed
application was built, tested, signed, scanned or distributed. Python local
projection cannot substitute for a native Windows report or packaging proof.

## Release gates and next action

The R456 parent workflows (source run
[43750378487](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43750378487)
and desktop-build run
[43750378535](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43750378535))
failed before any test steps; the GitHub API reports `runner_id=0`,
empty runner name, and zero steps for all four jobs. Commit check-run
metadata reports one failure annotation per job, but the currently
available repository connector cannot retrieve the annotation text.
**Cause unconfirmed.** The account owner should inspect Actions job
annotations and GitHub billing/spending limit and runner eligibility.
After runner restoration, execute this draft head's 13 tests in both modes,
all inherited six-engine regressions, native Windows x64 packaging and
installed-app smoke tests; then Defender, a11y, checksums and protected
premium license/download validation.

**Hard HOLD:** This remains a stacked draft feature branch, not `main`.
No WordPress/site deployment, binaries, downloads, license grants or premium
uploads. Financial calculations remain Decimal-safe and deterministic, original
source evidence remains unchanged, no telemetry is introduced, and all
compliance decisions require human review. Independent QD review and
explicit founder approval are mandatory before release.
