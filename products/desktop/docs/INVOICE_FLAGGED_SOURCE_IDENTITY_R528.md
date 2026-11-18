# R528 — Invoice Twin Scout: flagged source-key disagreement custody

**Status:** SOURCE ONLY / DRAFT PR / INDEPENDENT QD HARD HOLD.  
**Date:** 2026-11-18. **Issue:** #73. **Parent:** R527 draft PR #3029 at `72a2d940d62b365613d984cad5383af3b4b95ed5`, never production `main`.

## Real defect and correction

`review_flags()` previously checked whether raw vendor/invoice labels actually normalize to their asserted `v` / `inv` keys **only when no other review flag existed**. A direct caller could therefore fabricate a mismatched vendor or invoice source label and receive an ordinary-looking `normalized_vendor_key_review`, `normalized_invoice_key_review`, or amount variance **without a warning that the normalized key contradicted the original label**. This was a provenance gap, not evidence of fraudulent payments.

R528 compares all four bounded native raw labels with their validated normalized keys for **both** clean and flagged candidates, using the existing `identity_inputs.normalize_key()`. If the mismatch would otherwise produce a *clean* result, the existing fail-closed `ValueError` remains. If other human-review concerns already exist, the result retains them in original order and adds exactly one deterministic `source_identity_key_mismatch_review` flag. No raw financial details are interpolated into flags or exceptions. Already-valid lossy punctuation, ASCII-case, and Unicode uppercase-collision review behavior is preserved. No source mappings are mutated.

**Scope limits:** The new flag is an explicit **human-review warning**, not proof of fraud, identity, compliance or invoice duplication; labels alone cannot authenticate a physical source file. No money arithmetic, candidate matching, telemetry, networking, customer data, WordPress, site checkout, license/entitlement policy, or premium access control was changed.

## Focused evidence

- Production code: `products/desktop/fvs_suite/invoice_match.py`.
- Tests: **16 new** `InvoiceFlaggedSourceIdentityR528` synthetic regression methods in the existing already-allowlisted `products/desktop/tests/test_invoice_review_custody_r444.py`; the prior R527 assertion is updated to require the additional independent review signal.
- Local **reconstructed behavior probe**, not the committed repository module: `python /tmp/invoice_r528_probe.py` **16/16 passed** and `python -OO /tmp/invoice_r528_probe.py` **16/16 passed**; a negative control removing the new append behavior produced **6 failing tests**. The probe reused the inspected R527 matching and R528 flag logic with synthetic records and is weaker evidence than committed-module execution.
- **Not run:** newly committed 16 regressions, full pinned 416-command source matrix, native Windows x64 packaging/launch/accessibility tests, independent Windows/Defender signing checks, SHA-256 hosted distribution validation, premium entitlement tests. Never claim these as passing without exact-commit evidence.
- The immutable 416-command source manifest is **not edited**.

## Commands to run once a trusted runner is available

```text
cd products/desktop
python -m unittest discover -s tests -p test_invoice_review_custody_r444.py -v
python -OO -m unittest discover -s tests -p test_invoice_review_custody_r444.py -v
```

Then execute the pinned full source command matrix and native Windows 11 acceptance workflow, record the exact commit SHA, source integrity, runner/job step logs, signed/unsigned status, Defender scan and executable SHA-256. Do not substitute a reconstructed probe for those gates.

## QD / release HOLD

GitHub Actions workflows for R527 previously failed **before job steps** (`steps=null`); issue #75 tracks the unresolved runner-start blocker. Only a repository administrator can verify billing/spending limits, workflow policies and runner eligibility; the reason is not yet confirmed. **Smallest next action:** restore one minimal hosted test job and capture an actual step log; then run the full exact-commit source/Windows matrix.

All four free (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and two premium (GrantAudit Studio Pro, ProcureGuard Studio Pro) downloads remain on HOLD. No merge, publish, executable, unrestricted premium URL or release assertion. Independent QD approval and explicit founder authorization are mandatory before production changes or distribution.
