# Labs R171 — Invoice Twin report display-value custody

**Status: DRAFT / HARD RELEASE HOLD.** This source-only sprint does not release
an executable, certify any invoice, or authorize a payment or compliance action.

## Defect and scope

R169/R170 enforce trustworthy source identity, unique row pairs and review
classifications. A second boundary remained: `attach_invoice_provenance`
accepted arbitrary Python objects in **non-identity report columns** (such as
`vendor`, `amount_a`, `review_flags` or optional caller-defined columns)
and returned them in its report. An extra `list`/`dict` value could be mutated
after return; custom objects or `str` subclasses could execute attacker-defined
formatting/equality hooks during a later CSV serialization. The declared API
contract was `list[dict[str, str]]`, so this was not a supported use case.
The package must not derive an apparently stable, SHA-bound audit locator
while exposing mutable/hostile unvalidated display data.

## Implemented contract

* Copy each candidate from **native dictionary storage**, as before. Check
  every extra review/display field, including optional fields, is **exactly**
  built-in `str` — not bool, number, Decimal, mutable collection, Python object
  or string subclass. Reject non-string values with a single customer-data-free
  error before any report is returned.
* Identity columns `row_a`, `row_b`, `status` retain their existing stricter
  canonical checks and their existing field-specific error messages.
* Discarded untrusted `candidate_ref` and `source_sha256` placeholders are
  not required to be valid and are always overwritten with internally derived
  primitive strings; an invalid placeholder cannot be laundered into output.
* Keep valid opaque **plain-text** columns intact, including Unicode, newlines
  and existing money *display strings*. No numeric coercion or hidden rounding.
  SHA-256 source binding, R170 unordered-pair uniqueness, candidate orientation,
  classification sensitivity and human review are unchanged.
* This does **not** attest to authenticity of a source invoice, prevent a
  malicious *text-only* input, or sign the output. Treat references as local
  navigation locators, never payments, fraud findings or compliance approvals.

## Automated evidence contract

`products/desktop/tests/test_invoice_report_value_custody_r171.py` contains
**29 exact synthetic tests** for primitive types, hostile formatting/equality,
late-report fail-closed behavior, customer-data-free error handling, native
dict-subclass custody, valid opaque text and unchanged deterministic references.

`products/desktop/scripts/safe_unittest_r171.py` is a strict 29-case inventory:
missing/renamed/skipped/unexpected-success tests make the gate fail, and
all test stdout/stderr is suppressed to avoid leaking synthetic/private data.

From the repository root:

```sh
PYTHONPATH=products/desktop python products/desktop/scripts/safe_unittest_r171.py
PYTHONPATH=products/desktop python -OO products/desktop/scripts/safe_unittest_r171.py
```

The private internal workflow runs both commands on **Ubuntu 24.04** and
**native Windows**. Planned focused inventory executions: **29 × 2 × 2 = 116**.
These are targets until the *exact-head* CI job confirms passing status.
The inherited six-engine suite, six candidate packaging/GUI smoke checks,
private premium locks and supply-chain gates remain mandatory.

## Distribution and governance

The feature branch is stacked only on draft **R170 PR #848**, not `main`.
No changes to WordPress, revenue settings, premium access, telemetry, input
files, or public download URLs. No runnable binary is published by CI.

Physical Windows 11 independent **46-observation** accessibility acceptance,
real Defender/EDR assessment, code signing, protected premium distribution,
independent QD review and founder approval are required before release.
