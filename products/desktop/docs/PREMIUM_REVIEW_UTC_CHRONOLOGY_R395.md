# R395 — Premium human-review UTC chronology custody (DRAFT / HARD HOLD)

Owner: [Labs suite #73](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/73). Scope: GrantAudit Studio Pro and ProcureGuard Studio Pro human-review journals. This is not authorization to distribute, pay, or decide compliance.

## Reproduced prepatch defect

The original review_chronology.parse_review_utc and the separate exception_review._validate_event relied on Python datetime.fromisoformat, which accepts alternate UTC notations and silently truncates sub-microsecond precision. Against a locally reconstructed prepatch chronology parser using Python 3.13.5, all four test inputs were accepted: 2026-11-13X05:01:02Z (arbitrary separator); 2026-11-13T05:01:02.1234567Z (seventh fractional digit truncated); 2026-11-13T05:01:02+00:00:00 (offset seconds); and 20261113T050102Z (compact format). All four are now rejected. A prepatch invalid-calendar error also retained its parser exception in __cause__. These are audit chronology and privacy gaps, not evidence that customer data was compromised.

## Engineering delivered

1. Shared ASCII UTC grammar requires YYYY-MM-DDTHH:MM:SS, optionally 1–6 fractional digits, followed by Z, +00:00, or legacy -00:00. Calendar validation follows lexical validation. The existing writer's whole-second +00:00 format is unchanged.
2. Both premium event schema validation and chronological order / clock-rollback checks now use the same parser. Hash-valid but ambiguous journal timestamps fail closed before a human review append or review-register export. No migration or silent repair occurs.
3. Malformed calendar translation raises outside the original exception handler, eliminating retained private parser exception references.
4. The independent Ubuntu/Windows source workflow now includes normal and optimized Python checks for the new unit and both-premium integration suites.

## Executed local evidence (not full checkout integration)

Linux Python 3.13.5: 24/24 focused portable methods PASS normal; 24/24 PASS -OO; total **48/48 executions**. Source and test files compile. Local executed source/test files exactly match the committed Git blobs:

- Chronology source: a837df908cc4f5d40da7d05cd1d81d51a816eb20
- 24-test unit suite: f7a814c340f59df91e5562455a63146755a28f83
- 5-method both-premium integration suite: f96d16dc2ac718e063769c3f351353b373682984

The five integration tests were committed but **NOT locally executed** because a full repository checkout was unavailable. They exercise actual report/journal reads for both premium products, hash-valid noncanonical timestamps, refused append/export, and compatible historical UTC. The inherited R51 chronology tests and the complete six-engine, Decimal, AES-GCM, Ed25519/SQLite suites were not run locally. Native Windows execution was not performed.

## Full-checkout reproduction commands

- PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_review_utc_canonical_r395.py
- PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_review_utc_canonical_r395.py
- PYTHONPATH=products/desktop python -W error -m unittest discover -s products/desktop/tests -p test_premium_review_utc_integration_r395.py
- PYTHONPATH=products/desktop python -OO -W error -m unittest discover -s products/desktop/tests -p test_premium_review_utc_integration_r395.py
- PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_review_chronology_r51.py
- PYTHONPATH=products/desktop python -m unittest discover -s products/desktop/tests -p test_review_chronology_integration_r51.py

## Blockers / release hold

On the previous R394 exact head, source Actions run #43369473786 and desktop build run #43369473856 failed before any steps were assigned; root cause remains unconfirmed. The owner should inspect failed-check annotations, Actions spending/billing caps, hosted runner eligibility, repository settings and rerun the exact R395 SHA.

Highest next priority: run actual Ubuntu and native Windows CI with old/new chronology and both-premium integration, then the full six-app financial/crypto suites, six native x64 packaged smokes, Defender checks, accessibility acceptance and authenticated premium distribution review. No real journals, customer data, site pages, production branch, downloads, EXEs, licenses or premium URLs were changed. Independent QD review and founder approval remain required.
