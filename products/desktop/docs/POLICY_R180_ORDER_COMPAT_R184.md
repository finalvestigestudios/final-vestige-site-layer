# R184 — R180 test compatibility with Policy Delta physical-line custody

**Draft / HARD RELEASE HOLD.** Tracks issue #73. Feature branch stacked on R183 draft PR #929, not production.

## Confirmed inherited regression

The older R180 test named test_deterministic_sorted_physical_lines supplied physical source rows in the sequence L9, L2 on both document sides. R182/R183 deliberately made that input invalid: a source-owned unified diff emits strictly increasing physical positions. The code correctly returns no supplemental citations rather than fabricating an order.

In an isolated Linux workspace, using the exact upstream R183 engine blob 4348d9bd59f2e9455fc2505270a71182386068d3 and original R180 test blob 185cf6a5e7957fe32c6af21b051dc9db85665e7c, all 27 R180 unit methods were executed: **26 passed, 1 error**. The specific failing test raised ValueError: substring not found while looking for an intentionally suppressed L2 citation. This would fail inherited CI whenever runners resume.

## Implemented

Reordered only that one synthetic R180 fixture to genuine physical order L2, L9 on both sides. Preserved its original deterministic citation-order assertion. No application engine, existing source SHA256, monetary parser, premium license, or compliance decision changed.

Added 20 separate synthetic regression methods covering valid sorted pairs/hunks; reverse rows; duplicate or descending coordinates across hunks; oversized rows that cannot conceal collisions; one-sided source checkpoint tracking; 50,000-line boundary; ambiguous source skeleton suppression; malicious dict/tuple subclasses; private-text-free accessible Unicode metadata; and deterministic human-review cues.

Added a strict exact-inventory R184 runner (20 named tests, no skips) and Ubuntu/Windows normal and optimized Python CI steps. Inherited R180 strict 34-method runner (27 unit + 7 integration) remains in CI.

## Actual Linux isolated verification on 2026-11-04

| Scope | Normal Python | Optimized Python (-OO) |
| --- | --- | --- |
| Corrected R180 unit methods | 27/27 pass | 27/27 pass |
| New R184 strict runner | 20/20 pass | 20/20 pass |
| Total | 47/47 pass | 47/47 pass |

**94/94 focused method executions passed**, zero skips/errors/failures after correction; Python compilation passed. Exactly matched the source/test/runner Git blobs from the feature branch:
- Unchanged engine: 4348d9bd59f2e9455fc2505270a71182386068d3
- Corrected R180 tests: 948edc2d0898e72df0688c963d8044fcfdea4c02
- New R184 tests: 785d8ad299a40142f1ab6f05ee7a30c4158cb896
- New strict runner: 5fe88f82f96317bcfbbf2fd62a28a8c9509e9581

This local scope does **not** include the R180 seven real-file integration methods, the R178 seven integration methods, entire repository, Ubuntu CI, Windows CI, native Windows binaries, physical accessibility acceptance, or Defender.

## CI and next action

The predecessor R183 GitHub Actions run https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41818306117 failed *before* either runner was allocated, with zero steps. The root cause remains unconfirmed. Owner should inspect the Actions failure banner, repo Actions enablement, billing/usage allowances and hosted runner provisioning. Once fixed, rerun this R184 exact commit and execute the inherited integration suite plus six private Windows x64 build/integrity/smoke tests.

**HARD RELEASE HOLD: all six apps remain unreleased.** Physical Windows 11 accessibility observations, genuine EDR assessment, signing, entitlement-protected premium distribution, independent QD and explicit founder approval are still required. No production merge, website edits, public EXEs, or unrestricted premium links.
