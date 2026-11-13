# R410 — Offline six-app smoke subprocess environment custody

**Status:** SOURCE-ONLY DRAFT. Six apps remain unreleased. Independent QD review and explicit founder approval are required. No production branch, WordPress, financial engine, customer file, premium entitlement, paid access, or distribution operation changed.

## Reproduced exposure / reason for change

The R409 run_gate subprocess invocation passed the entire parent os.environ to every one of the twelve source smoke children. Python isolated mode (-I) limits Python import-path overrides, but it does **not** delete inherited environment variables: a local smoke process could still read credentials such as GITHUB_TOKEN, AWS_SECRET_ACCESS_KEY, OPENAI_API_KEY, proxies or unrelated CI secrets. These were not printed in the evidence JSON, but their unnecessary propagation broke least-privilege financial privacy.

## R410 implementation

- Child processes get an explicit, case-insensitive runtime allowlist of **PATH, PATHEXT, SYSTEMROOT, WINDIR, TEMP, TMP, TMPDIR** plus enforced PYTHONDONTWRITEBYTECODE=1. The original key spelling is preserved for Windows. -I, -W error, -OO as applicable, no shell/stdin, timeout, OS-level stdout/stderr discard, source hashes before/after, and twelve fixed statuses remain.
- Unrelated secrets, proxies, arbitrary Python startup/import variables, preload injections and user identity paths are **not** forwarded. Runtime allowlisted values themselves are not reinterpreted or sanitized; this is environment-variable isolation, not a sandbox or proof against malicious checked-out source.
- Nine R410 regression methods exercise full six-launcher mock cases in standard and optimized Python, exact allowlist contract, real child-process inability to see synthetic secret variables, fail/pass statuses, source inventory determinism and parent-environment immutability.
- The independent Windows + Ubuntu source workflow includes both new modes; no merge, deployment, executable publishing, or premium link is authorized.

## Local execution evidence and limits

On a **partial synthetic Linux checkout** with Python 3.13 and source/test files matching the exact proposed Git blobs:

| Suite | Methods | Result |
| --- | ---: | --- |
| R410 ordinary Python -W error | 9 | 9/9 PASS |
| R410 optimized -OO -W error | 9 | 9/9 PASS |
| **Focused executions** | **18** | **18/18 PASS** |

Source compilation passed. The synthetic harness executes 12 real local Python child processes per applicable test; **it does not import the actual six financial engines**, nor validate real Windows executables, Microsoft Defender, keyboard/NVDA/high-DPI behavior, full inherited Decimal/crypto tests, premium payment gating, or genuine release security.

## Full-checkout validation / owner unblock

From a trusted complete checkout at the exact R410 commit:

~~~sh
export PYTHONPATH=products/desktop
python -W error -m unittest discover -s products/desktop/tests -p test_offline_source_environment_r410.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_offline_source_environment_r410.py
python -W error -m unittest discover -s products/desktop/tests -p test_offline_source_privacy_r409.py
python -OO -W error -m unittest discover -s products/desktop/tests -p test_offline_source_privacy_r409.py
python -I products/desktop/offline_source_smoke_r408.py
~~~

For native Windows use set PYTHONPATH=products/desktop or a PowerShell environment assignment. Treat any missing interpreter dependency or platform behavior as a **failed/unverified** gate until resolved; do not infer success from synthetic fixtures.

If GitHub Actions again records no allocated runners / no steps, inspect the run banner, Actions spending/billing and hosted-runner eligibility. Rerun exact R410 head with both OS jobs and inherited full suite. Do not conflate an infrastructure failure with source-test failure.

## Remaining immutable release holds

Four free: LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk. Two premium: GrantAudit Studio Pro, ProcureGuard Studio Pro. Still required: trusted full-checkout source/Decimal/provenance/crypto regression, **six genuine Windows x64 portable executable** build-and-launch tests, Defender scan, keyboard/NVDA/high-DPI acceptance, version/SHA256 custody, premium anonymous-access denial and controlled download verification, independent QD and explicit founder approval. **No auto-merge or public download links.**
