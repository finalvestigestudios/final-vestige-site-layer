# R147 — exact offline replay arguments and human-review custody

**Status:** DRAFT / RELEASE HOLD · six Windows x64 apps remain unreleased.
**Scope:** The existing local replay verifier for the four free products only.
**Parent:** R146 draft #682; do not merge, retarget or publish without independent QD and founder authorization.

## Reproduced source risk

Before R147, the R144 replay CLI redacted malformed argparse messages but used
argparse's default *last-one-wins* behavior for repeated singleton options.
For example, an operator could paste two `--report` arguments and receive a
successful verification of the *second* report, even while believing the first
report was in scope. Abbreviations such as `--rep` and `--left-amount` were
also accepted, making the exact meaning dependent on the available options.
This is a review-custody ambiguity, not a demonstrated exploit of SHA-256.

## Contract implemented

- `--kind`, `--report`, `--window-days`, both LedgerDiff match-key options,
  and both LedgerDiff amount options are each allowed **once only**. Their
  `--flag=value` and `--flag value` forms count as the same option.
- `--source` deliberately remains repeatable: one input for Invoice Twin
  Scout and SpendMap Lite; two inputs for LedgerDiff Lite and Policy Delta
  Desk. The existing verifier validates source count *before any input read*.
- No long-option abbreviations; all option names must be explicit.
- `--help` / `-h` are valid **only as a standalone argument**. The `--`
  separator is rejected because this command accepts no positional arguments.
- Invalid, duplicated, abbreviated or mixed commands fail **before**
  `verify_report` when detected by the parser. The CLI returns exit code 1
  with the existing single fixed `REPLAY HOLD` line, no echo of filenames,
  rejected cells, or options. No source/report files are edited on failure.
- Valid full-spelling invocations, exact-byte SHA-256 receipts, existing source
  snapshot custody, deterministic report replays, exact Decimal arithmetic,
  privacy controls and premium entitlements are unchanged.

## Safe invocation examples (illustrative paths; NOT release URLs)

```text
python -m fvs_suite.replay_verify --kind spend-map --report C:\\review\\spend-map.csv --source C:\\review\\spend.csv
python -m fvs_suite.replay_verify --kind ledger-diff --report C:\\review\\ledger-diff.csv --source C:\\review\\bank.csv --source C:\\review\\books.csv
```

Do not put confidential account identifiers, license keys, customer names or
secrets in shell arguments: upstream shell history, process listings, terminal
recording and screen sharing are **outside** this CLI's privacy boundary.
Use approved, locally protected sample/source paths. The VERIFIED receipt
proves reproducibility under the current source and software version, **not**
authenticity, fraud, an approved payment, or legal compliance.

## Test / CI contract

`products/desktop/tests/test_replay_argv_custody_r147.py` contains **33
named, synthetic tests** for singleton duplicate/equals variants, explicit
source multiplicity, abbreviations, help interactions, `--`, invalid argument
types, redaction, no file mutation, no source access on rejected selections,
native Python subprocess execution and real local replay continuity for
SpendMap, LedgerDiff and Policy Delta.

`products/desktop/scripts/safe_unittest_r147.py` requires the exact 33 named
methods with no missing/skipped/extra tests, failing closed if the inventory
changes. CI must run it on **Ubuntu and Windows** using normal Python and
`python -OO` (**132 scheduled named method executions**). The full inherited
desktop source and six-app Windows packaging gates remain mandatory.

To reproduce locally from a full trusted checkout:

```text
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r147.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r147.py
```

These commands prove synthetic source behavior only. They cannot replace
Windows 11 physical keyboard/scale/screen-reader checks, authentic Defender/
EDR assessment, code signing, premium download access controls, independent
QD review or founder release approval. **Do not publish executables** from a
source-only pass.
