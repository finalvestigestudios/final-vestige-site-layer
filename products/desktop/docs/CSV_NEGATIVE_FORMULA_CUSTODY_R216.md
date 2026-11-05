# Labs R216 — negative-formula and Unicode-prefix CSV custody

**2026-11-05 UTC — DRAFT / QD HOLD / NOT RELEASE-APPROVED.** Stacked on immutable R215 commit 874a05a193d32a2f00a8dd145a894d08964f2b51 (draft PR #1135), not on production/main. Changes shared report validation, tests and CI only. No deployed WordPress changes, binaries, premium URLs, license exposure or automatic compliance approvals.

## Finding

R215's formula guard checked =, + and @ after whitespace or selected invisible prefix marks but did not guard leading minus when an API caller forgot to sanitize. Strings such as -SUM(A1), -HYPERLINK(...), -A1 and -2+2 might be interpreted as formulas by some spreadsheet importers. It also failed to scan past leading bidi, combining and control characters such as U+2066, U+034F, U+00AD, U+20DD and U+001B. Specific spreadsheet exploitation has **not** been demonstrated.

The existing shared publisher's _render_cell already calls this guard for rendered headers, values and ignored extra fields. Changing the guard strengthens that existing integration for all six applications even for direct callers using cell=str. The normal engine safe_cell sanitizer remains mandatory.

## Implementation

- Skip leading Unicode whitespace and categories **Cf, Cc, Mn, Me** for inspection only; preserve original evidence and retain the intentional leading-apostrophe escape.
- Reject minus-prefixed cells unless the remainder is a canonical ASCII negative decimal matched by minus followed by ASCII digits and an optional dot plus ASCII digits, consistent with the existing engine safe_cell exception. -23.10 remains unchanged; -1E+2, -.5, -$12 and hyphen-prefixed prose require escaping before publication.
- Preserve Decimal roundtrips, deterministic output bytes, exclusive/atomic publication, evidence rollback, no later source-row consumption and private-value-free exceptions.
- No telemetry/uploads, source file modifications, money rounding, compliance determinations or changes to premium entitlement policy.

## Exact-source local verification (synthetic values only)

Reconstructed unchanged R215 shared writer, formula guard and R215 tests from their immutable GitHub file contents, checked their Git hashes with git hash-object.

| Artifact | Git blob |
| --- | --- |
| Inherited fvs_suite/atomic_reports.py | 4d08b277b063fbf77d924e8e0dc71c0d25fb5c5b |
| R215 guard (baseline RED) | 9600f6f1b9cbd6c47fda9d2a2b8473763b02275e |
| R216 guard (GREEN) | 6819a16c8a65d597a800837dd65a9e2e680cf626 |
| New 21-case R216 test | 2efd5588417dd5cfa00fef5a56124376bc1ad602 |
| Unchanged inherited R215 test | 250ba2fd49eeac7898904757b6de7fdea7896cf6 |

Against unchanged R215, the 21 new tests yielded **34 assertion failures and one error**, including unsafe negative formula publication, Unicode-prefix bypass and attempted exclusive publication of invalid evidence. The 34 failures include subtest assertions, not 34 individual methods.

With the R216 guard applied, Linux CPython 3.13.5:
- cd products/desktop
- PYTHONPATH=. python -W error -m unittest discover -s tests -p 'test_atomic_*r21*.py' -q — **38/38 PASS** (R216 21 and inherited R215 17)
- PYTHONPATH=. python -OO -W error -m unittest discover -s tests -p 'test_atomic_*r21*.py' -q — **38/38 PASS**
- python -m compileall -q fvs_suite tests — PASS
- **76/76 focused local test-method executions**, 0 skips or errors in the passing cases.

**Scope limitation:** The locally reconstructed directory contained only two exact-source modules, an empty package initializer and R215/R216 tests. It was not the whole repository or six-app regression matrix and did not execute on Windows. Existing exact-source atomic_reports._render_cell calls this guard; its integration did not need a separate source change. The two new workflow steps require actual hosted execution to count as CI evidence.

## CI and release hard HOLD

Prior [R215 Actions #42089549704](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/42089549704) concluded **failure**; windows-build and source-tests returned steps:null. Cause remains unverified. The smallest owner action is to inspect the Actions failure banner, usage/billing policy and runner provisioning and rerun unchanged R216 HEAD once runners work.

Before any merge/release: all inherited six-engine regression tests on Ubuntu/Windows, six GUI-to-CSV smokes, privately built/checksummed/Defender-scanned Windows x64 portable EXEs, native Windows 11 keyboard/NVDA/high-DPI acceptance, code-signing decision, controlled premium download entitlements, independent QD verification and founder authorization. Do not publish public untested EXEs or unrestricted premium artifacts.
