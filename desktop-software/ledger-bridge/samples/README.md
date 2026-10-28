# Ledger Bridge — safe sample reconciliation

These examples contain **fictional transactions only**, no actual personal or
financial information. They illustrate why reconciliation must fail closed
when evidence does not support a unique, confirmed pairing.

## Run from source (Python 3.11+)

From the repository root:

```shell
python desktop-software/ledger-bridge/ledger_bridge.py desktop-software/ledger-bridge/samples/ledger-a.csv desktop-software/ledger-bridge/samples/ledger-b.csv --report ledger-review.json
```

The process should exit with code **1** because a human review is required.
The sample is not intended to appear fully reconciled. It must not modify the
CSV inputs. The desktop GUI lets you select the files and export an HTML report.

## Expected results

- 6 parsed input transactions on **each** side.
- 2 unique reference/amount matches (the two invoices).
- 1 suggested amount/date match (the $17 service charge / bank fee).
- 2 duplicated $75 reference/amount entries on **each** side, not paired.
- 1 unmatched $99 left-side item and 1 unmatched $24 right-side item.
- **3 matched pairs** total, of which **1 is only a suggestion**.
- 3 unmatched rows on each side.
- An `ambiguous_reference_groups` entry identifies the duplicate REF-X
  identity, with the precise row numbers on both sides.
- Overall `status: REVIEW` with an `AMOUNT_DATE_SUGGESTIONS` warning.

## Acceptance criteria

Verify that every ambiguous or suggested pair can be traced to both original
CSV row numbers and that the application does not claim `RECONCILED` for
these examples. Inspect the exported report for discrepancies and warnings.
Manually cross-reference original bank/vendor records before approval.
For debit/credit-separated CSVs, the tool treats a blank individual debit or
credit cell as zero but rejects a row where both are blank. A standalone
`amount` column must explicitly contain a number, including zero if intended.

**Important:** This utility is decision support, not professional assurance,
fraud detection, or a substitute for source-document verification. The sample
is safe to share; private customer CSVs and premium installer artifacts are not.
