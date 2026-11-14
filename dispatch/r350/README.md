# Final Vestige Dispatch R350 — Consent-to-customer evidence sprint

**REVIEW ONLY. No sends, tests to live inboxes, WordPress changes, affiliate activation, approvals or merges.**

Stacked on draft PR #2444 (exact parent ae9905051efd56379e90f694607b36ebe2a19bc9), references original #175 and Issues #174 (Dispatch), #171 (Mind), #129 (Focus), #820 (revenue). Original 4 editorial / 2 conditional commercial draft preserved; existing #49 homepage release and other teams' branches untouched.

This sprint stops adding competing editorial alternatives and tackles the real bottleneck: trusted subscriber eligibility, delivery and conversion. It introduces a provider-count reconciliation, staged single confirmed_signup event, exact first-party email CTA destination plan, account-specific merchant permission intake, offline reviewer, fail-closed code plus tests and a concrete Focus copy fix proposal.

Verified read-only 2026-11-14 08:31 UTC: WP subscriptions ON, automatic new-post emails OFF, format full, welcome PDF configured; newsletter total 3/confirmed 3/unconfirmed 2 and followers WP.com 3/email 0 overlap. Eligible actual inbox recipients UNKNOWN. No genuine welcome receipt, native received-email, FV publisher address, opt-out functionality, partner email permission, approved live guide, settled paid outcomes or qualified sessions verified. Existing Gmail confirmation request is not welcome.

Primary source links: https://finalvestige.com/editorial-standards/ · https://finalvestige.com/dispatch/ · https://finalvestige.com/focus/ · https://wordpress.com/support/newsletter/email-appearance/ · https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business · https://zen12.com/ · https://hypnosislive.com/mental-skills/total-focus · https://hypnosislive.com/faq

Run only locally against source checkout: python -m unittest discover -v -s dispatch/r350 -p test_gate.py. These tests cannot authorize sending and have no API calls, credentials or subscriber IDs.
