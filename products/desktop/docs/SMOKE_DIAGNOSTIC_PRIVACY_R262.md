# Labs R262 — privacy-safe packaged smoke failures (Issue #73)

**DRAFT / QD + founder HARD HOLD.** This feature branch is stacked **only** on R261 draft PR #1444 at immutable parent `a81afbe3578795488215acd4e5d6e256a7c72bc3`; it does **not** modify `main`, the WordPress site, signed artifacts, premium distribution, or release status.

## Reproduced exposure and limited correction

The shared `fvs_suite.launcher.launch` entry point runs `--smoke-test` for each of the six utilities. Before R262, an ordinary exception from `run_smoke()` triggered `traceback.print_exc()`: an `OSError` path, source filename, custom exception message or chained exception could disclose customer financial details directly to the terminal and CI logs. That behavior was reproduced against the unmodified R261 launcher.

R262 keeps the existing pre-GUI offline guard, zero/nonzero smoke-success contract, all six app IDs, and allowed `--version` path. It **does not** print the exception or its traceback. Instead, routine smoke faults and empty results return nonzero with exactly `Final Vestige Labs smoke test failed; no private diagnostics printed`. The fixed failure is raised **outside** the exception handler, so it has no private `__context__` or `__cause__`. Explicit `KeyboardInterrupt` and `SystemExit` remain outside the routine-fault handler. No financial calculations, entitlement decisions, human review logic or input documents are changed.

This guards only launcher-generated smoke diagnostics. A smoke routine that explicitly prints secrets or a guard initialization exception that escapes before smoke dispatch remains a separate concern. No claims of full crash-report redaction or an OS network sandbox are made.

## Local source evidence — 2026-11-07

Reconstructed a minimal test harness using **Git-blob-identical** source from the latest R261 draft head:
- `fvs_suite/offline_network.py` unchanged R261 blob `977740eca1b7273823cfe776dbf1257636d4a9a4`
- `fvs_suite/__init__.py` unchanged blob `a3e3f9fdeaf0f74f10077a7299f29f505dbe991f`
- Updated `fvs_suite/launcher.py` blob `c3144bcfdfcb4cb5f941495e525872f25d03cbe0`
- New `tests/test_launcher_smoke_privacy_r262.py` blob `451f9c6c84020755b0e13554ffbf84595c559925`

Using Linux CPython 3.13.5 with purely synthetic paths/data, the 15-method regression suite **failed 14 assertions** against the original R261 launcher (the first test also exercised all six product IDs), proving customer-source path disclosure and exception chaining. After the modification:

```sh
cd products/desktop
python -W error -m unittest discover -s tests -p 'test_launcher_smoke_privacy_r262.py' -q
# Ran 15 tests — OK
python -OO -W error -m unittest discover -s tests -p 'test_launcher_smoke_privacy_r262.py' -q
# Ran 15 tests — OK
python -m compileall -q fvs_suite tests
# PASS (focused reconstructed package)
```

**30/30 passing focused local test executions.** Scenarios include all six launcher IDs, OSError source paths, UnicodeError, chained exceptions, empty/None outputs, failing `__bool__`, missing smoke import, success, still-blocked child-process audit event, public version reporting, unsupported arguments, interrupt propagation, explicit exit and no retained exception context. The tests use subprocess isolation to avoid leaking global CPython audit hooks between cases.

This proof **is not** the full repository suite, native Windows 11 x64 behavior, a packaged-EXE smoke, a malware scan, accessibility evidence or evidence of protected premium delivery.

## Acceptance hold and next work

GitHub Actions for the earlier R261 head [#42394412945](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42394412945) failed before verifiable Ubuntu/Windows steps according to the last inspection; underlying runner/billing/policy cause is unconfirmed. Reinspect the workflow checks on this PR. The smallest owner-side unblock is restoring the Actions runner/usage/permissions path and rerunning this **unchanged** head for actual step logs.

**Next highest-impact step:** full repository-wide normal and optimized regression on Ubuntu + real Windows 11 x64, six genuine offline smoke launches, source-file path/log privacy inspection, private unsigned candidate checksum/Defender verification, keyboard/NVDA accessibility, and access-controlled premium distribution checks. No releases without independent QD review and founder approval.

**All six products remain UNRELEASED.** No production branch, website, executable, license gate, download URL, or premium file changed.
