# R51 — Premium human-review chronology guard (pre-release)

This sprint adds UTC temporal consistency checks to the hash-linked, local-only
human-review journals used by **GrantAudit Studio Pro** and **ProcureGuard Studio
Pro**. The existing journal hash chain detected changed bytes but did not reject
backdated events when the hash chain remained internally consistent. A changed
computer clock could also cause a fresh reviewer action to be recorded earlier
than the previous decision.

## Behavior

- Every recorded review UTC timestamp must be parseable, explicitly UTC,
  finite and no longer than 64 characters. All existing ISO-8601 `+00:00`
  timestamps remain valid; `Z` is also accepted.
- `read_journal` verifies **nondecreasing** recorded instants across the entire
  review history. Events in the same second remain permitted; an earlier
  timestamp fails closed even if the event SHA-256 was recomputed.
- `append_review` checks the current UTC clock before constructing/writing the
  next reviewer event. If the clock is behind the last recorded decision, no
  new event is appended. Investigate the machine clock and journal manually;
  never silently rewrite, reorder, or replay decisions.
- `export_register` inherits the complete journal validation, so backdated
  records cannot be silently exported as a normal audit register.
- No automated eligibility findings, procurement/payment approvals, telemetry,
  customer uploads, secrets, or license bypasses. Original reports are never
  edited. Reviewer names, rationales, and source filenames are not logged in
  the new chronology errors.

## Evidence and test boundary

- `test_review_chronology_r51.py`: 23 focused unit tests, including malformed
  inputs, time zones, UTC offsets, equal timestamps, microsecond rollback,
  explicit clock rollback, and privacy-safe errors.
- `test_review_chronology_integration_r51.py`: four real-workflow tests for both
  premium apps, covering a backdated SHA-valid history, a future-dated last
  record, same-second reviews, and refusal to export a tampered journal.
- The optimized-Python CI lanes cover both files once GitHub Actions executes.
  The integration tests require the complete repository and are not established
  as passing by isolated helper tests.

## Security boundary and release controls

A local operating-system clock is not a trusted independent time source. A
SHA-256-only journal is not a digital signature or tamper-proof storage. An
attacker who controls both journal and clock may rewrite history. This guard
checks observed consistency and rejects clock rollback, not author identity.
All six Windows x64 candidates remain unreleased pending actual complete
regressions, native binary smoke/security checks, premium delivery controls,
and independent QD review. This sprint does not publish or authorize binaries.
