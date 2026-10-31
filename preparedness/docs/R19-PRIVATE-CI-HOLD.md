# R19 — private PR machine execution, never publication clearance

Tracking: Issue #136. This change is isolated to one Preparedness-only GitHub Actions workflow, one read-only contract tool and its synthetic adversarial tests, plus this runbook. All existing 35 articles, their reading/source records, taxonomy, and unpublished water tool are unchanged.

## Objective

R18 exposed 11 native gates but could not run all of them locally because the working environment cannot resolve the private GitHub repository. R19 provisions an isolated *pull-request-only* hosted check whose checkout contains the repository's real files and complete Git history. It uses a read-only `GITHUB_TOKEN` permission (`contents: read`), does not persist checkout credentials, does not call WordPress/CMS, does not upload artifacts, does not deploy, and never enables publication. The `pull_request` trigger is filtered to Preparedness files and the R19 workflow itself. Its GitHub-hosted checkout includes remote contributor branches so the R15 Git-object parity gate can find the seven contributor refs.

The workflow pins both official GitHub Actions to immutable public SHAs (`checkout` v4.2.2, `setup-python` v5.6.0), and executes the R18 complete checkout and native-build preflight against the actual `$GITHUB_SHA` merge commit. The R19 tool checks the workflow file byte-for-byte to prevent permission, event, checkout-depth, shell command or publishing-related drift. It independently validates the complete 11-step R18 receipt, including the count of >=36 successful tests, exact checkout SHA, all eight HOLD custody reports, no release authority, and the canonical SHA-256 receipt fingerprint.

## How to review

1. Inspect the workflow and R19 tool in this **draft, unmerged** PR. Do not interpret a green GitHub Actions job as independent QA approval.
2. On the PR Checks tab, confirm a runner was dispatched and executed; if no workflow run appears, record `RUNNER_NOT_DISPATCHED`, not `PASS`.
3. If executed, inspect each of the 11 R18 native results. Any gate failure is a machine HOLD; investigate and amend only in a new reviewed draft branch.
4. A successful hosted run proves deterministic source/citation/build custody on that exact checkout only. It does **not** validate that source claims are accurate, that linked pages were actually human-read, or that consequential instructions are medically safe.
5. Maintain publication HOLD until the 30 shared-URL groups are human-reconciled, 1,959 citation occurrences are independently reviewed at claim level, qualified reviewers assess the emergency/medical guidance, and an independent QD approves a separately governed release.

## Local repeatable checks

```sh
python -I -B -m unittest discover -s preparedness/tests -p 'test_workflow_contract_gate.py' -v
python -I -B preparedness/tools/workflow_contract_gate.py --repo-root .
python -I -B preparedness/tools/private_release_preflight.py --repo-root . --expected-head "$(git rev-parse HEAD)"
```

The actual 35-article native validator, build and hosted run are not claimed until the full checkout runs. The R19 tests are synthetic/adversarial; they are not source review.

**Non-actions:** No merge; no public navigation; no articles published; no WordPress writes; no fabricated source verification or QD PASS.
