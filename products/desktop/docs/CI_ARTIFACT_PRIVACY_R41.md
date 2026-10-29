# R41 — Evidence-only GitHub Actions artifacts

**Status:** feature-branch safeguard, not release approval. Covers all four free and both premium Windows x64 desktop products in issue #73.

## Problem and change

Previously the Windows job's `actions/upload-artifact@v4` used `dist/*`, making **all six candidate executables** retrievable through the workflow's artifact permissions whenever the build succeeded. Repository access is not the same as a verified paid entitlement or controlled customer distribution. The R41 workflow **no longer uploads executable payloads** to GitHub Actions artifacts. It uploads only:

- `dist/SHA256SUMS.txt` — canonical hashes for six candidates, not the actual EXEs.
- `build/offline-candidate-evidence.json` — local release-gate evidence only, with `release_authorized: false`.
- Separately, the Linux `source-tests` job uploads only `${{ runner.temp }}/fvs-source/source-smoke.json`.

Both upload-artifact steps require `if-no-files-found: error` and `retention-days: 7`. The artifact names and **exact file paths** are checked by `products/desktop/ci_artifact_policy.py`. The policy refuses wildcards, whole directories, extra upload actions, path expressions, duplicate keys, missing evidence, and extended retention. CI calls the policy before packaging and runs the policy regression suite on Linux and Windows, including under optimized Python.

## Operator verification

From a complete trusted checkout:

```shell
python products/desktop/ci_artifact_policy.py .github/workflows/desktop-build.yml
PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_ci_artifact_policy_r41.py -v
PYTHONPATH=products/desktop python -OO -m unittest discover -s products/desktop/tests -p test_ci_artifact_policy_r41.py -v
```

On PowerShell, set `$env:PYTHONPATH = "products/desktop"` before running the unittest commands. A clean workflow policy is **not** evidence that Windows binaries were actually built or executed.

## Limitations and release policy

This is a deliberately narrow static guard against unintended **GitHub upload-artifact input expansion**, not a general solution for all CI exfiltration vectors, malicious workflow edits, GitHub permission mistakes, or insecure external publishing. Workflow changes require independent review. Do not put customer data, financial files, keys, premium license issuer secrets, or premium executables into artifacts.

Keep actual six-binary candidates in a trusted Windows build environment until the whole test suite, Windows x64 smoke tests, security review, SHA-256 comparison, signing decision, premium fulfillment authorization, and **QD approval** are complete. GitHub Actions failures before any recorded steps must not be counted as test passes. No production site or public download URL is changed by R41.
