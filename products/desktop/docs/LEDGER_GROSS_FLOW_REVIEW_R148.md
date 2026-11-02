# Final Vestige Labs R148 — LedgerDiff gross transaction flows (DRAFT / RELEASE HOLD)

## The reconciler's former blind spot
Net-only matching can conceal economically meaningful movements. A left-hand
ledger containing a $150 charge and a $140 credit appears to have the same $10
net as a right-hand ledger with one $10 charge. Pre-R148 the per-key report
exposed the net and duplicate-ID review status, but not gross flow magnitudes.

## Exact implementation contract
The LedgerDiff Lite report adds four fields without removing legacy columns:

| Column | Meaning |
| --- | --- |
| left_gross_charges | Sum of positive imported left amounts (exact cents) |
| left_gross_credits | Magnitude of negative imported left amounts (exact cents) |
| right_gross_charges | Sum of positive imported right amounts (exact cents) |
| right_gross_credits | Magnitude of negative imported right amounts (exact cents) |

The existing left/right net amounts are computed from those exact flows:
gross charges minus gross credits. Signed zero is neutral. Inputs remain
independently byte-snapshot-verified before parsing. Reports retain selected
source headers, physical source rows, original labels, both source SHA-256
digests, and the input identity review flag.

For keys present on BOTH sides, if net totals are exactly equal but EITHER
gross amount differs, add status 'gross_flow_mismatch_review'. A formerly
'matched' status becomes only 'gross_flow_mismatch_review' (never a
contradictory matched-and-flagged status). Duplicate-ID and normalized-ID
flags remain. Missing-side and unequal-net statuses remain unchanged; those
already identify absent sources and variances. Gross columns are also emitted
for those cases, without fabricating original source rows.

### Synthetic worked example

| side | charges | credits | net |
| --- | ---: | ---: | ---: |
| Left: +150, -140 | 150.00 | 140.00 | 10.00 |
| Right: +10 | 10.00 | 0.00 | 10.00 |

Result: status = duplicate_id_review;gross_flow_mismatch_review.
This is a HUMAN REVIEW signal, not evidence of fraud, eligibility,
correct allocation, transaction legitimacy, or payment authorization.
Even perfectly matching gross amounts do not prove transaction-level
reconciliation or source completeness.

### Source privacy, money and safety
All arithmetic is Python Decimal under the suite's private precision-64
context, existing input bounds and exact cents. No floats, cloud APIs,
accounts, telemetry, edits to original source CSV, premium entitlement change,
payment authorization, or automatic review clearance. Exports retain
spreadsheet formula neutralization and non-overwriting atomic publication.
Human reviewers must inspect cited physical rows and original SHA-256 data.

### Regression / CI
The synthetic regression file tests/test_ledger_gross_flow_r148.py defines
28 exact named methods. Source-owned scripts/safe_unittest_r148.py pins names
and class, rejects failures/errors/skips/unexpected successes, and exposes
only aggregate PASS/FAIL diagnostics. Required CI:

- Ubuntu: ordinary Python and optimized python -OO strict runner.
- Windows: ordinary Python and optimized python -OO in PowerShell.
- Total planned = 28 methods x 2 modes x 2 platforms = 112 executions.
- Both inherited source suites, internal native six-EXE candidate builds,
  native access/evidence checks and private packaging gates remain mandatory.

Passing this gate does NOT demonstrate physical Windows 11 accessibility,
46 independently observed checklist items, real Defender/EDR scrutiny,
code signing, protected premium distribution, QD or founder approval.
There is no release, website change, or public download authorized here.
