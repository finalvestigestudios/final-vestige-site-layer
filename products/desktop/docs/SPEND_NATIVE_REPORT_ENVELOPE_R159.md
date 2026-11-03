# R159 — native SpendMap evidence report envelope validation (DRAFT / HOLD)

## Audit risk and change

The R158 independent verifier authenticated transaction membership, original
vendor labels, 8 exact-Decimal money fields and seven historical review fields.
However, it accepted *arbitrary additional CSV columns* and could accept the
same rows reordered. A third party could append `payment_approved=yes` or
`compliance_approved=true`, leave the financial evidence unchanged, then
advertise a successful source verification as approval of the unvalidated
claim. This is an audit-presentation and report-authenticity ambiguity.

R159 **fails closed** unless the report has exactly the 25 native SpendMap
headers, in their documented canonical order, with no extras, omissions,
case aliases, blank headers or disguised Unicode names. The header tuple lives
in the independent `spend_report_envelope.py`, **not** imported from the
report generator: changes to the generator require explicit verifier review.

The source snapshot already contains validated source categories. R159 also
checks that every output bucket occurs in the native sorted source-bucket
order *before CSV spreadsheet escaping*, preventing presentation reorder
while preserving valid formula-safe source categories. It does not infer
authorizations or attest that an original source CSV was genuine.

## Artifacts

- `fvs_suite/spend_report_envelope.py`: fixed independent native CSV header
  contract. No network or report-generator dependency.
- `fvs_suite/spend_evidence_verify.py`: reject nonnative header shape and
  source/category report-order changes before declaring the evidence verified.
- `tests/test_spend_report_envelope_r159.py`: 26 synthetic methods using
  actual local SpendMap reports. Includes positive gross/credit/category
  cases, quoted multiline original records, header spoofing, fake approval
  columns, Unicode lookalikes, inserted BOM, row reorder, unchanged originals
  and private CLI error redaction.
- `scripts/safe_unittest_r159.py`: fixed 26-method strict zero-skip runner.
- `.github/workflows/desktop-build.yml`: run ordinary and optimized `-OO`
  suites on Ubuntu and native Windows: **104 planned method executions**.

## Local reproducibility

From repository root set `PYTHONPATH=products/desktop` and run:

```sh
python products/desktop/scripts/safe_unittest_r159.py
python -OO products/desktop/scripts/safe_unittest_r159.py
```

Run the end-user independent verifier with its existing read-only interface:

```sh
python -m fvs_suite.spend_evidence_verify --source original.csv --report spend-map.csv
```

Always inspect the **exact PR head** CI results before claiming any passes.
A successful check verifies that this local report agrees with this local
source under the documented checks. It is **not** a digital signature, a
payment authorization, a fraud finding, or a claim that any particular
person approved the report.

## Distribution is still HARD HOLD

All four free applications and both premium applications remain unreleased.
CI may build only internal Windows x64 candidates. Physical Windows 11
46-observation accessibility acceptance, genuine Defender/EDR, code signing,
authenticated premium distribution, independent QD approval and explicit
founder authorization are required before any public release. Do not merge
directly to `main`, modify WordPress production, or publish executable links.
