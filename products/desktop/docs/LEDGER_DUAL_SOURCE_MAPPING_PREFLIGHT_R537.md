# Labs R537 — Dual-ledger mapping preflight before private CSV access

**Issue:** #73. **Branch:** `feature/labs-r537-ledger-dual-source-mapping-preflight-20261118`. **Scope:** LedgerDiff Lite source validation only; no changes to any other product's financial formulas, human compliance decisions, licensing or packaging.

## Defect and behavior

Before R537, `ledger_diff()` loaded and parsed the **left** customer's ledger before checking some malformed **right-side** header overrides. `table()` validates each source's explicit match/amount column, but LedgerDiff invoked it sequentially. A malformed right-side configuration could unnecessarily open private left-side data before raising an error.

R537 adds a pure, bounded `preflight_ledger_overrides()` function and invokes it at the very start of `ledger_diff()` (before either `table()` call). It validates **all four** independent optional overrides: left/right match columns and left/right amount columns. It uses exact native strings, the same space/trim/lowercase normalization and ASCII 128-character schema as `table()`, does not stringify adversarial objects, rejects normalized match/amount collisions on the **same** source, and never echoes entered header names in errors. Same-name headers on opposite sources remain valid. Header **existence** and collisions with an *implicitly inferred* header still require the verified CSV importer's checks.

This is configuration validation, not a new compliance rule; the existing table parser, Decimal context, audit provenance, human review and atomic save remain authoritative.

## Test matrix and reproducibility

- **Committed:** `products/desktop/tests/test_ledger_mapping_preflight_r537.py`: **17 unittest methods** in two groups (13 no-I/O pure contract cases; 4 full-engine routing/negative-I/O cases).
- **Executed locally:** Python CPython on Linux, isolated `fvs_suite.ledger_mapping_preflight_r537` with the **exact committed Git blob** `af1c9c5247430b596856212d7d2e209259b35c9e` and exact committed test module Git blob `b1bb6ce09ee19654daa1510348b8ed582d7d7e9f` (local `git hash-object` matched remote readback). `LedgerMappingPreflightPureTests` **13/13 PASS**, and `python -OO` **13/13 PASS**; bytecode compilation **PASS**. This totals **26 executed pure test methods**; parameterized subtests are not counted as extra methods.
- **Not executed:** the **4** full-engine integration methods, full committed repository test suite/416-command offline source gate, six-app Windows 11 x64 packaging, GUI/screen reader/scale tests, Defender, artifact SHA256/distribution and premium entitlement tests. The isolated directory has no full private repository checkout; executing the whole test module there yields import errors for `fvs_suite.engine`. No fake-engine passing claim is made.
- Local reproduction commands from a full checkout (no customer data):
  ```sh
  cd products/desktop
  python -m unittest tests.test_ledger_mapping_preflight_r537 -v
  python -OO -m unittest tests.test_ledger_mapping_preflight_r537 -v
  python scripts/offline_source_gate.py --help
  ```
- R537 creates no executable, installer, download or output containing financial inputs. No uploaded customer records; no files opened by the new pure policy.

## CI infrastructure and release gates

R536 parent exact HEAD `605fe05e0b33508ee24c0696ec317c1e19d85166`: three GitHub Actions runs [Windows build #44449384979](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44449384979), [six-engine source #44449384973](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44449384973), [image-identity #44449384961](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/44449384961) had six failure jobs with `steps=null`. A cause has not been proven; #75 tracks this. Check R537 exact-head runs separately.

**Next highest-value unblock:** Repo/account administrator restores one Actions runner capable of executing a step, with startup banner/log and billing/spending/hosted runner policy evidence. Run all 17 committed R537 tests in both interpreter modes, complete the six-source gate, then independent native Windows six-EXE build/smoke, Defender, NVDA/Narrator, checksum and premium entitlement/protected distribution checks. Do not approve or publish based on source-only tests.

**QD + founder HARD HOLD:** This feature branch must remain a draft PR stacked on R536, not `main`. Independent QD review and explicit founder approval are mandatory before any merge, WordPress catalog publication or release. The four free and two premium apps remain unreleased.
