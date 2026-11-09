# Dispatch R231 — independent received-email verification kit

**Status: DRAFT ONLY. All six HOLD_UNSENT; commercial 03/05 HOLD_MERCHANT.**

New capability: offline RFC 5322/MIME inspection of an already received, explicitly authorized Jetpack email, if one eventually exists. R201/R223 previews never established actual receipt or footer compliance. R229/R230 handle subscriber status and misleading Focus gift UI—not delivered-message legal evidence. This is not a send-ready campaign.

- received_email_gate.py: no external dependencies, network, sending, list access, cookies or tracking. Emits only boolean review checks, never identities, real addresses, body, link tokens or actual opt-out URLs. Returns HOLD even when a synthetic message looks complete.
- tests/test_received_email_gate.py: 25 synthetic unit tests on fictional example.invalid addresses and a fictional postal address, including privacy, missing address, unsubscribe, subject, sender and HTML/plaintext cases.
- RECEIVED_EMAIL_RELEASE_PROTOCOL.md: privacy-safe genuine inbox evidence procedure, conditioned on separate explicit founder authorization.
- CLAIM_AND_CONVERSION_AUDIT.md: actual six-edition subjects/CTAs, merchant claim/rights restrictions and read-only WordPress diagnostics.
- OWNER_DECISION_MATRIX.md: P0 commercial permission, recipient consent/actual inbox verification, revenue reconciliation.

Run native tests: python -I -m unittest discover -s dispatch/r231/tests -v. **25/25 local native Python 3.13 tests passed**, and test/code Git blob IDs were checked against committed GitHub source.

The original #175 Python suite was inspected at the exact original commit but not natively rerun on a complete private checkout because local container DNS cannot resolve GitHub. Earlier JS assertions do not count as executing the original Python suite.

No emails, tests through real inboxes, WordPress changes, subscriber contacts/exports/imports, affiliate links, merchant contacts, new services, payment activity, homepage PR #49 edits, merges or live analytics changes. Revenue/1,000 qualified human sessions remains NOT COMPUTABLE.
