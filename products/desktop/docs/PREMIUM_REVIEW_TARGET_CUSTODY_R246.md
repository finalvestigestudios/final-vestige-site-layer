# R246 — Premium exception-review target custody (issue #73)

**DRAFT / independent QD and founder HARD HOLD.** This patch is a source-only human-review safety improvement for the two gated premium Windows x64 applications. It does **not** authorize release or certify either executable.

## Reproduced code-path risk

In `fvs_suite/app.py`, the premium **Review exceptions** command passes `last_report[0]` to the entitlement-checked review window. Previously, after generating report A, changing source paths / output destination / procurement policy did **not** reset that automatically selected target. A subsequent rejected or failed generation also left A selected. A reviewer could click Review and silently be shown an older exception queue rather than the newly intended data set. This is not a claim that a payment was approved or that the review journal was corrupted.

## Change

- New `fvs_suite/review_target.py` performs idempotent fail-closed clearing of the implicit latest-report pointer, with no access to the report bytes or filesystem.
- `app.run` registers Tcl `StringVar` write traces for **all** required input files, output folder, optional policy path, optional LedgerDiff mapping headers, and optional invoice day window when present. Premium-specific state clearing runs only for GrantAudit Studio Pro and ProcureGuard Studio Pro.
- Every Generate button attempt clears the old auto-selection **before** entitlement, missing-input or generation validation can fail. On an actual success, and only then, the new generated report path becomes the auto-selection.
- Historical local reports are not deleted, edited, transmitted, or silently reapproved. The operator can explicitly browse for one in the review window, with existing entitlement verification, evidence-custody checks, and human approval semantics unchanged.

## Tests and limitations

Local Linux CPython 3.13.5 isolated, **exact Git-blob-matched** `review_target.py` and `test_review_target_r246.py`: **12/12 normal**, **12/12 `-OO -W error`** PASS; 0 skips (**24 method executions**). Fake Tk variable traces prove independent edit invalidation, failure retry cleanup, preexisting target cleanup, idempotence, explicit success rebinding, path redaction, and fail-closed bad slots; no network or customer data.

The integration edit to the actual `app.py` was committed on the R246 feature branch and explicit normal/optimized test steps were added in both Ubuntu and Windows source jobs. **The full exact repository, GUI window, hosted CI, Windows x64 binaries and premium licenses were NOT executed locally.** These 24 focused tests do **not** constitute native GUI verification.

### Native Windows QD reproduction checklist

1. With a **test** signed entitlement (never publish a key or license), generate synthetic premium report A.
2. Change any input/output/policy field and click **Review exceptions**. The workbench must not auto-load A; choosing A requires explicit Browse.
3. Generate A, introduce malformed second input, try Generate again, and then open Review. No silent A selection is allowed.
4. Generate a valid synthetic report B. Review may auto-load only B.
5. Repeat entirely by keyboard and with Windows high DPI / screen reader; ensure no private path or customer data appears in logs.
6. Re-run the full source suite normal and optimized, private Windows packaging, SHA-256 checks, AV scan, and six-app smoke; obtain independent QD and founder approval separately.

## Release and distribution

All **six** apps remain unreleased. No production branch, site, files, premium entitlement, public binary, downloadable URL or payment approval was modified. The existing Ed25519 premium entitlement checks and human-only review controls remain mandatory. The GitHub Actions job allocation failure (zero steps reported on R245) remains a separate blocker; inspect Actions billing/usage, workflow permission and runner provisioning, then rerun the unchanged R246 head. Do not infer Windows readiness from these source-only tests.
