# R336 — six-app private Windows smoke-runner custody (2026-11-10)

**Scope:** All four free (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite, Policy Delta Desk) and both premium (GrantAudit Studio Pro, ProcureGuard Studio Pro) executables. **DRAFT, NOT A RELEASE.** This change is stacked on R335 draft PR #1933; neither PR targets production main. QD and founder authorization remain mandatory.

## Reproduced predecessor gaps

1. The R335 release gate selected `runner or subprocess.run`, even though smoke provenance used `runner is not None`. An injected callable with `__bool__() == False` was unexpectedly replaced with the real native subprocess runner. A synthetic reproduction confirmed the selection discrepancy; no real EXE was executed.
2. The R335 smoke check accepted a forged `returncode=False` because `False == 0`. It also accepted coercible/mock exit values in some cases. The new boundary requires **type(code) is int** and exactly zero.
3. Unexpected `subprocess.SubprocessError`, runtime errors, and broken/missing result attributes bypassed the previous narrow `TimeoutExpired` / `OSError` catch and could leak a private path in diagnostic exception chains. R336 maps ordinary execution faults to stable privacy-safe messages and suppresses private causes. `KeyboardInterrupt` and `SystemExit` still propagate.

## Changes

- `smoke_runner_r336.py`: `select_smoke_runner` uses **identity**, not truthiness, so a falsy injected runner can never become a real executable launch. `run_smoke_checked` preserves the existing `--smoke-test`, DEVNULL stdin/stdout/stderr, timeout and no-shell argv contract; rejects noninteger/boolean result codes and unexpected runner failures.
- `release_gate.py`: uses the new isolated smoke boundary after existing preflight / SHA / PE verification and before existing post-smoke artifact rechecks. Explicit integer timeout validation fails closed. Nothing creates native Windows evidence from synthetic tests.
- `tests/test_smoke_runner_r336.py`: 21 focused tests: falsy/truthiness-trap injection, exact subprocess options, invalid return codes, private error redaction, bounded timeouts, exception propagation and normal/negative exit codes.
- `.github/workflows/desktop-build.yml`: explicit normal and optimized tests in **Ubuntu source-tests** and **private Windows packaging** jobs. Full `offline_source_gate.py` discovery also sees the test file.

## Executed tests and provenance

**Local Linux runner; synthetic runner results only.** Against the exact committed Git blobs:
- `smoke_runner_r336.py` blob `7f98ced387071016fb17c409cae72cb0289d2d0b`.
- `test_smoke_runner_r336.py` blob `92cc9973f5a347696c5fbeb670fbf5afeb730432`.

Commands from repo root:

```bash
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_smoke_runner_r336.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_smoke_runner_r336.py'
python -m py_compile products/desktop/smoke_runner_r336.py products/desktop/tests/test_smoke_runner_r336.py
```

Result: **21/21 PASS normal + 21/21 PASS optimized = 42/42 focused test executions; zero skips; compile PASS.** The original falsy-runner expression and false-boolean result acceptance were reproduced separately against R335 semantics. The complete private repository suite, native Windows verifier invocation, actual PE binaries, antivirus scanning, signed packaging and 22 genuine AES-GCM integration cases were **not** executed locally. The new `release_gate.py` integration and full CI remain unverified by hosted execution.

## Release holds

Do **not** merge, publish, attach, or distribute binaries as a consequence of this PR. The release gate continues to set `release_authorized=False`, `premium_entitlement_verified=False`, `codesigning_verified=False`, and `malware_scan_verified=False`. No customer data, telemetry, cloud processing, financial arithmetic, compliance approvals, entitlement or WordPress site state changed.

At sprint start, R335 [run #42872624968](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42872624968) was **FAILURE**: Ubuntu `source-tests` and Windows `windows-build` each reported zero recorded steps. Root cause unconfirmed. Inspect Actions billing/spending cap, runner availability and permissions; retrieve an actual executed step log. **Next priority:** full source regression including the **22 genuine AES-GCM** tests, followed by all-six Windows 11 x64 private build, smoke, SHA, Defender, accessibility, premium access-control checks and independent QD/founder approval.
