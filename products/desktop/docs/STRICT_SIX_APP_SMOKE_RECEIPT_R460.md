# R460 — Verify six actual source-smoke statuses (draft / QD HARD HOLD)

Tracks [issue #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Stacked on R459 draft PR #2671 at `6f8923b43d531e21c7e5869b386a948f80bd3e10`; **not production main**.

## Reproduced logical gap

Before R460, `offline_regression_gate_r459._run_smokes` returned 12/12 whenever the R408 subprocess returned exit code 0, with `stdout=DEVNULL`. It did not inspect the six application outcomes, so a successful exit with a missing or contradictory child receipt could produce a misleading 12/12 claim. The original R408 executable currently computes its exit code from status counts, but the parent should independently verify *actual structured evidence*, not blindly impute it.

## Implementation

- `offline_smoke_receipt_r460.py` checks the exact R408 schema, SHA-256 source fingerprint shape, source-only evidence indicator, explicit `release_authorized=false`, native integer counts 12/12, **all six application IDs in expected order**, and both normal and optimized statuses for every app. Zero, duplicate, missing, skipped, failed, malformed, extra-field and forged evidence are rejected.
- R459 parent runs R408 with stderr discarded and stdout directed to an **owner-private temporary file**, never to an unbounded `PIPE` or operator console. The parent reads at most 4,097 bytes, rejects responses over 4,096 bytes and emits only fixed redacted errors. Exit code zero is necessary but no longer sufficient. Source fingerprints now include the validator and both offline-gate regression files.
- New `test_offline_smoke_receipt_r460.py`: **19 focused unittest methods** for strict records, fabricated success, malformed/oversized output, release claims, and mocked real parent subprocess integration. The inherited R459 mock test now supplies a valid R408 record.
- Register R460 standard and `-OO` tests in the independent Ubuntu/Windows source workflow and both Linux source and Windows pre-packaging jobs. Correct the R459 independent source workflow's POSIX `PYTHONPATH=...` shell prefix, which is invalid under Windows PowerShell; the existing job-level `PYTHONPATH` environment is used instead.

## What was actually tested

A local Linux Python 3.13 isolated reconstruction of the R459 parent and R460 validator ran the **Git-blob-identical R460 production validator and 19-method regression file**:

```sh
PYTHONPATH=products/desktop python -B -W error -m unittest discover -s products/desktop/tests -p 'test_offline_smoke_receipt_r460.py'
PYTHONPATH=products/desktop python -OO -B -W error -m unittest discover -s products/desktop/tests -p 'test_offline_smoke_receipt_r460.py'
```

**19/19 standard PASS; 19/19 optimized PASS (38 method executions).** The tests include four real parent-subprocess integration simulations using a mocked `subprocess.run`, plus actual Python JSON parsing. They **do not** execute R408's real six launchers or the full repository's R455–R458 source integration tests. The R459 parent reproduction was reconstructed, not Git-blob-identical, and Windows PowerShell was not executed locally. `python -m py_compile` succeeded for the reconstructed parent and production validator.

## Actions / blockers / release HOLD

The latest R459 exact-commit workflow runs failed before steps and runner assignment: [source #43767427827](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43767427827) and [Windows build #43767427779](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43767427779); four jobs, each with zero steps, one inaccessible check annotation per job. Root cause **not confirmed**. Next: owner checks Actions job annotations, billing/spending limits, runner allocation and Actions policy, then reruns both workflows at the new R460 head. An engineer with a complete checkout can run `python -B products/desktop/offline_regression_gate_r459.py` and attach the actual private source-only JSON receipt.

**No native Windows x64 EXE, Defender scan, installed smoke, accessibility, signing, checksums, premium entitlement or protected distribution, WordPress publication, release, or compliance approval was executed or authorized.** Six-app release requires independent QD review and explicit founder approval.
