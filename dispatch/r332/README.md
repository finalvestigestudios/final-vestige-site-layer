# Dispatch R332 — alternative original Issue 02 and consent-to-order HOLD harness

Draft source-only stacked branch on R331 #2354; campaign owner Issue #174, original six source manuscripts PR #175 unchanged. Files:
- `02-franklin-orchard.md`: 1784 historical-source original editorial candidate (NOT_ADOPTED).
- `02-franklin-orchard.txt`: same copy as email-style plaintext, explicitly not a received email.
- `02-franklin-orchard.html`: responsive table-based inline-style reviewer, not Jetpack rendering.
- `snapshot.json`: privacy-safe WordPress + commercially unverified snapshot, no PII or real partner URLs.
- `release_check.cjs`: fail-closed, NON-SENDING evaluator, never can_send true.
- `release_check.test.cjs`: synthetic adversarial tests (`node --test dispatch/r332/release_check.test.cjs`).
- `DECISION_AND_SOURCES.md`: primary claims, live WordPress read-only evidence, source links, owner matrix, conversion contract.

To check: `node --test dispatch/r332/release_check.test.cjs` (Node 20+). Original #175 suite: `python -m unittest discover -s dispatch/campaign-2026-mind/tests -v`. No test is legal approval; no test sends email. Source preview contains legal HOLD deliberately.
