# R331 — No automatic deletion of premium review journal on failed custody validation

**Status:** DRAFT; issue #73; independent QD and founder HARD HOLD. No executable release, entitlement changes, claims approval, or production modifications.

## Defect and correction

Previously, the common premium journal append routine closed a newly created journal on failure, checked its pathname metadata, and conditionally used os.unlink() if still empty. A cooperating or rival process can replace the pathname **between** the final lstat() and unlink(), resulting in deletion of another file. Even without an attacker, the cleanup erased a zero-byte artifact following a rejected review.

R331 removes post-failure rollback/unlink entirely. A newly created journal is retained for explicit human inspection even if empty or if the first write fails. A subsequent, separately reviewed retry can append to a verified empty journal. Pre-open input validation still creates nothing.

Only the existing journal module changes; pinned-descriptor checks, no-follow and nonblocking open flags, prefix SHA-256 witness, exact appended-byte verification, privacy-safe errors, size limits and cooperative writer locking remain. This is not filesystem immutability or evidence authenticity. No network calls, telemetry, Decimal calculations or automated compliance decisions.

## Files

- products/desktop/fvs_suite/journal_io.py — removes the post-close unlink race and no-longer-used write flag.
- products/desktop/tests/test_journal_failed_create_preservation_r331.py — 17 focused synthetic regressions covering healthy creation/existing append, errors before and after write, adversarial unlink simulation, fail-closed and privacy-safe handling, explicit reviewer retry, invalid input and preservation of prior records.

## Executed on 2026-11-10 (isolated Linux Python 3.13.5)

- 17/17 new R331 tests PASS normal and 17/17 PASS optimized (-OO).
- 6/6 R329 and 3/3 R330 replayed integration tests PASS normal and optimized.
- **26/26 PASS normal + 26/26 PASS -OO = 52 passing focused executions**, zero skips; Python compilation PASS.
- On the exact R330 predecessor, 16 new tests produced 3 failures and 4 errors (including evidence deletion on rejected validation and unsafe unlink hook invocation); green on patched code.
- Verified Git blob identity: original journal_io.py 4a20ecfb2252a7174790983686941eee70f71fb2; patched abeeeecc8a5da1790cacf62ae93c5092e81b6fb4; R331 test 1bd7b7e0577df2c2e922cbe9716f896767a803a8; replayed R329 and R330 tests 4f0878e13c53cbf311323e884a6424939b4e43ef and 0c844721f90c7128556e3f7df6076f44c2d069af.

**Test topology limitation:** Exact Git-matched journal module and regression test files were executed within a reconstructed local environment using equivalent small dependency helpers. It was not the full private checkout. Hosted CI, all 22 genuine AES-GCM integration cases and Windows executable tests were not executed.

## Full checkout replay

~~~sh
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_journal_failed_create_preservation_r331.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_journal_failed_create_preservation_r331.py'
PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p 'test_*.py'
PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p 'test_*.py'
python products/desktop/scripts/offline_source_gate.py
~~~

## Highest impact next step and release hold

Owner must inspect GitHub Actions billing / spending limit / workflow permissions / runner eligibility and restore pre-run scheduling. Then run the full source suite in normal and optimized Python, all 22 real AES-GCM cases, and private Windows 11 x64 executable acceptance on all six applications with SHA-256, Defender, keyboard/screen-reader accessibility and premium gated-download verification.

All six apps remain unreleased. Independent QD review and founder signoff are required before merge or distribution.
