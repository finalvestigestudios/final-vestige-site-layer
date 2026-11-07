# Labs R263 — offline security bootstrap diagnostic privacy (issue #73)

**DRAFT — QD + founder release HARD HOLD.** Based on R262 at exact commit
`2076e80371214319d8ee7d2bb11c7b86ca1fa5c4`, not on production `main`.
No WordPress, financial source, premium entitlement, Windows release, or public
asset change is authorized by this sprint.

## Reproduced defect

The shared six-product `launch()` ran `install_offline_guard()` outside the
R262 smoke-diagnostic privacy boundary. If `sys.addaudithook()` raised a
runtime exception containing confidential client paths or a previous audit hook
interrupted `sys.audit()` during registration, the bootstrap traceback could
reach the console/CI logs. A direct caller of `install_offline_guard()` could
also receive an uncensored registration exception. The earlier `raise ... from
None` on a failed probe suppressed rendering of context but did *not* clear
`__context__` for callers that inspect the exception.

## Limited change

- `launcher.py` converts **ordinary** guard startup exceptions to a constant,
  nonzero `SystemExit` raised **outside** the original handler (no private
  `__cause__` or `__context__`). All six product IDs fail before GUI or smoke
  dispatch. This also applies to `--version`, which still requires the guard.
- `offline_network.py` translates ordinary registration and probe faults to a
  fixed `RuntimeError` **outside** the handlers. Only a confirmed probe marks
  the offline hook as enabled; silent hook suppression remains a startup error.
- Inherited R260 negative tests now expect privacy-safe `SystemExit`. New
  regression tests exercise six ID paths, actual CPython audit denials,
  fail-stop on missing hooks, direct-call exception provenance, normal
  GUI/smoke/version paths and `KeyboardInterrupt`/`SystemExit` propagation.

No private exception object, audit arguments, URL or financial filename is
printed by the bootstrap. No network access, subprocess creation, monetary
calculation, entitlement or compliance decision is added. This is a CPython
runtime defense, **not** a Windows kernel firewall or complete crash-report
redactor; extensions and native subprocesses need native acceptance testing.

## Local verification (2026-11-07, Linux CPython 3.13.5)

Local synthetic fixtures only, with source files reconstructed from and Git
blob-verified against the exact R262 source. Original R262 + new regression
suite: **14 failing test results from 15 methods** (defect reproduction).
Patched source:

| Command from `products/desktop/` | Result |
| --- | --- |
| `python -W error -m unittest discover -s tests -p 'test_offline_boot_privacy_r263.py' -q` | 15/15 PASS |
| `python -OO -W error -m unittest discover -s tests -p 'test_offline_boot_privacy_r263.py' -q` | 15/15 PASS |
| `python -W error -m unittest discover -s tests -p 'test_offline_network_r260.py' -q` | 10/10 PASS |
| `python -OO -W error -m unittest discover -s tests -p 'test_offline_network_r260.py' -q` | 10/10 PASS |
| `python -m compileall -q fvs_suite tests` | PASS |

**50/50 focused test-method executions PASS**. Some methods loop across all six
IDs using subtests; counts refer to unittest methods, not individual subcases.
Source and tests committed as the same Git blobs exercised locally:

- `launcher.py`: `3664899c70d1e2afb774ba631aebdffaa74673ff`
- `offline_network.py`: `30039ab587cb5a0ce3be305d78d3f919385a2fbf`
- `test_offline_boot_privacy_r263.py`: `620abcba33b57c6e06875e18c9c8f83bef013a00`
- `test_offline_network_r260.py`: `6317888eedc2eda1fc07118769f5f94e292ee899`

The reconstructed local environment contains only the relevant launcher,
security module and focused tests, with a minimal version stub. It is **not**
a full-repository test run, genuine GUI integration, or a Windows 11 x64 binary.

## Open release gates and next step

R262 hosted Actions run #42399375510 has source-tests and windows-build jobs
with failure status and no recorded steps/log URLs. Root cause is unknown;
owner should check Actions usage/billing, workflow permissions and runner
provisioning, then rerun CI at the unchanged R263 head. Next highest-impact
engineering step: run all repository tests and produce **private** Windows 11
x64 executable builds with real GUI/guard denial checks, integrity hashes,
malware/accessibility review, and verified premium-access gates. Do not merge,
publish, expose premium EXEs, or bypass independent QD and founder review.
