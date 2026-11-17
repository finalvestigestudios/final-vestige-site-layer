# Labs R485 — offline source regression fallback (DRAFT / QD HARD HOLD)

## Purpose

The GitHub-hosted six-engine source and internal Windows workflows repeatedly report **failure before any job steps** (for example R484 [source #43984286637](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43984286637) and [Windows #43984286786](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43984286786)). This source-only fallback provides a reviewable, **local checkout** command while the administrator diagnoses Actions account, billing, runner assignment or policy. The root cause is **unconfirmed**. This code does not fix GitHub Actions scheduling.

## Operator command (trusted full checkout, preinstalled Python dependencies)

From the repository root:

\`\`\`sh
python -I products/desktop/offline_source_gate_r485.py > source-evidence-r485.json
\`\`\`

Exit **0** requires all eight checks to report PASS; any FAIL/BLOCKED exits **1**. The JSON always says \`"release_authorized":false\`. Four fixed pre-existing test modules are run in both ordinary and \`-OO\` mode, each with a 600-second timeout: six-launcher source smoke R408, six-app safety smoke, ProcureGuard R483 hostile-row privacy, and six-EXE inventory R484 staging ancestry. Missing test files, zero discovered tests, skipped tests, failed assertions, subprocess errors and timeouts cannot produce PASS. An isolated copy without the complete repository will fail closed.

The wrapper itself does not request network services, but **does not sandbox or technically prevent network access by test code**. Execute in an administrator-controlled offline machine or isolated environment if network prohibition is required. Its child environment omits credentials, inherited Python injection and proxy settings; only fixed whitelisted environment keys pass. Python test stdout/stderr is placed in a temporary disk-backed file and **not printed**, except a redacted per-check outcome and discovered test count. The disk spool is not size-limited; the per-check timeout bounds runtime, not maximum output bytes. Do not execute untrusted test code in this verifier.

## Local validation performed for this R485 change

The new standalone Python module and eight unit regression methods were actually executed on Python 3.13.5 in an isolated directory:

- \`PYTHONPATH=<local-R485-dir> PYTHONDONTWRITEBYTECODE=1 python -B -W error -m unittest discover -s <local-R485-dir> -p test_offline_source_gate_r485.py\` — **8/8 PASS**.
- Same invocation with \`python -OO -B -W error\` — **8/8 PASS**.
- Tests exercise all eight scheduled invocations with mocked subprocess results, positive and fail-closed cases, missing files, zero/skip counts, timeouts, secret redaction, environment scrubbing and invalid timeout inputs.
- The exact new files matched GitHub blob hashes at commit write: module \`d800d29245d551d0fbb1e2ed07919118e9298244\`, tests \`58a91a012edbabb78624da0410344f6b9d95f5a0\`.

**Limit:** The eight unit tests mock subprocess completion and synthetic checkout file names. The real 8-gate invocation against a complete checked-out repository was **not run** in this environment. There is no genuine Windows executable, packaging verification, Defender scan, accessibility assessment, license/payment entitlement or verified live download from this sprint.

## Release conditions and next step

Retain the exact GitHub Actions failures as evidence, inspect job annotations/account eligibility and restore a job that actually executes steps. Run this source-only fallback on a trusted checkout (and collect output JSON), fix any genuine failures, then run the full six-engine matrix and native Windows x64 smoke/Defender/checksum/accessibility/protected-premium distribution gates. No direct merge to \`main\`, WordPress publish, public binary, premium file exposure or automatic compliance approval. Independent QD review and explicit founder approval remain mandatory.
