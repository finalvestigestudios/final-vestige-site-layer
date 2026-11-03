# R156 — independent exact-money recheck for SpendMap exported evidence (DRAFT / HOLD)

This incremental security/audit improvement extends the R155 read-only local SpendMap evidence verifier. In addition to complete source-line membership custody, it now **independently recomputes eight financial evidence fields** from the SHA-256-pinned original CSV, rather than trusting copied report totals or invoking the SpendMap summary/report generator. This closes a gap in which an attacker could edit an amount or a credit-review flag in an exported CSV without disturbing the earlier R155 membership digest or citations.

## Eight independently checked export fields

- `amount` — net Decimal cents per vendor/month/category.
- `gross_charges` and `gross_credits` — independent positive charge and negative-credit magnitudes per category bucket.
- `vendor_month_total`, `vendor_month_gross_charges`, `vendor_month_gross_credits` — independent vendor/month totals across **all categories**; repeated on each category export row and **never summed again across rows**.
- `credit_offset_review` and `vendor_month_offset_review` — deterministic positive/negative co-occurrence warning flags; **review only**, no fraud or compliance determination.

The independent implementation uses exact `Decimal` amounts from the shared strict source CSV parser, a separate 64-digit local decimal context to isolate hostile caller precision/traps, and ordinary category/group aggregation. It compares canonical two-decimal wire values **exactly**; a altered value, missing required column, forged warning, or tampered second bucket fails closed. It does not call `summarize_spend` or any export-generation financial helper.

## Local developer command

From repository root with `PYTHONPATH=products/desktop`, Python 3.12:

```sh
python -m fvs_suite.spend_evidence_verify --source "spend.csv" --report "spend-report.csv"
```

A successful result reports ONLY source SHA-256, report SHA-256, verified group count and verified bucket count. Rejection prints a fixed **HOLD** message without amounts, customer names, or paths. Original source/report bytes are not written; size and ordinary-file checks, private source snapshot and end-of-check hash pinning are inherited from R155.

## Verification and limitations

```sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r156.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r156.py
```

CI: **25 named synthetic tests**, zero skip/xfail, ordinary and optimized Python on Ubuntu `source-tests` and Windows `windows-build`: **100 planned targeted method executions** across the two OSes. Inherited R155 tests and six-app source/build gates remain. CI result is **pending until the exact new commit is observed**; a red result is HOLD.

This is **NOT** a comprehensive independent report replay: vendor normalization, date and money input parsing remain shared with the existing strict CSV engine; historical median/outlier scoring, vendor-label review, source authenticity, signing, exception workflow and actual payment approval are *not* independently verified here. For whole-report reproducibility use the existing separately gated exact-byte report replay. Neither check is a digital signature or a compliance verdict.

**Six applications remain UNRELEASED.** No public EXE, source evidence upload, premium unrestricted file, production merge or WordPress publication authorized. Physical Windows 11 acceptance (46 observations), genuine Defender/EDR on candidates, code signing, protected premium transfer, independent QD and founder approval remain HARD HOLD.
