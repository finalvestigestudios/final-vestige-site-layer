# R325 — reconcile premium journal framing and FIFO-safe restored-evidence reads

**Status: DRAFT / independent QD and founder HARD HOLD. No release approval.**

## Why this branch exists

Issue #73 developed two independent changes from the R322 witness base
(`ba1f93842d4405ffb0e81b2381a3e3725891eb79`):

* #1857 (R323 canonical JSONL) and stacked #1861 (R324 authenticated
  source-bound journal reader) reject ambiguous bare-CR journal boundaries.
* #1864 (R323 nonblocking member opens), separately stacked on #1852,
  prevents a raced POSIX FIFO substitution from indefinitely blocking
  read-only restored-bundle verification.

The changes were on divergent draft branches; neither alone contained
both defenses. R325 starts at **exact R324 head
`ee49bb2d0aea848bb81006505a450b8f4064dce3`**, not `main`,
and ports only the FIFO mitigation, nine test methods and the internal
Ubuntu/Windows CI gate. The R323 canonical parser and the R324 source-bound
reader are retained, not overwritten.

## Actual code boundary

`products/desktop/scripts/verify_restored_bundle_r320.py` uses
`os.O_NONBLOCK` when available in the existing bounded, read-only
`os.open` path for known manifest/report/journal members. No source
paths, reports or journal contents are logged. Existing `lstat`,
`fstat`, descriptor identity, regular-file/type, no-follow,
single-link, size budget, SHA-256, second-pass and trusted-witness checks
remain in force.

On POSIX, this prevents a regular-file-to-FIFO swap in the gap between
`lstat` and `os.open` from hanging on a writer. It is **not** an
OS-level lock, and no Windows kernel-level promise is made.

No change to financial calculations, Decimal-safe money, AI, licensing,
entitlement, vault authentication, WordPress, or production. Independent
SHA-256 witness receipt remains an operator-supplied trusted-custody
check, *not* source authentication or a compliance decision.

## Reproduction and proof requirements

On a complete private checkout of this branch, with project dependencies
installed, run:

```sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_restored_bundle_open_race_r323.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_restored_bundle_open_race_r323.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_restored_journal_canonical_r323.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_line_framing_r324.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_review_line_framing_integration_r324.py'
```

Run optimized `-OO` for each suite; enforce all existing 22 mandatory
genuine AES-GCM integration tests without skips, then the complete source
suite and Windows private packaging/acceptance. The R323 FIFO suite
uses killable child processes with a 4-second timeout for race cases on
POSIX; Windows only executes available portable cases and cannot be
claimed to provide POSIX FIFO guarantees.

The earlier isolated R323 branch demonstrated 9/9 normal and 9/9
optimized methods on Linux; the earlier isolated R324 helper had 23/23
normal and 23/23 optimized methods locally, but its six new full reader
integration methods had not executed. **Those predecessor executions
are not a substitute for a full combined R325 run**. Hosted Actions has
repeatedly failed before a runner executed any steps; describe it as
pre-execution infrastructure failure, not a failing unit test.

## Review and release boundaries

All six desktop apps (LedgerDiff Lite, Invoice Twin Scout, SpendMap Lite,
Policy Delta Desk, GrantAudit Studio Pro, ProcureGuard Studio Pro)
remain **unreleased**. No binary/download claim, unsigned installer
distribution, premium unrestricted file link, automatic payment approval,
or compliance recommendation. Require completed native Windows 11 x64
build/launch, malware checks, SHA-256, accessibility/keyboard validation,
protected premium entitlement and independent QD plus founder sign-off.
Do not merge this stacked draft directly to production.

**Next highest-impact step:** owner restore Actions billing/spend and runner
eligibility (or provide trusted complete private checkout and Windows 11 x64
machine), execute combined source/regression/AES-GCM gates, and record
physical Windows acceptance before any QD review or deployment.
