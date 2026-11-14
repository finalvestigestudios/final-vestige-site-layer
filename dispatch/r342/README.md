# Dispatch R342 — no-send received-message evidence gate

**DRAFT / NOT ADOPTED / HOLD_UNSENT.** Supplementary QA for existing Dispatch #174 and PR #175. Stacked on #2403; separate readiness #201 remains untouched. No email/post/test email/subscriber outreach/affiliate activation/production merge, and no founder final approval.

## The specific evidence gap solved
Offline HTML, synthetic test mail and Jetpack configuration cannot prove a recipient received a qualifying email with a real Final Vestige postal footer and functioning unsubscribe. WordPress official appearance guide confirms native editor PREVIEW email, distinct from SEND TEST EMAIL; it also explains that sender display name may change but actual post-notification sender remains donotreply@wordpress.com. No verified independent preheader control in current Jetpack configuration.

### New files
- received_email_gate.py: Python standard-library, read-only RFC 822/MIME candidate evidence checker. No network, sends or subscriber data persistence. Returns categorical checks, never addresses/tokens/bodies. Maximum input 1 MB. Checks subject, sender display, HTML/plain, one first-party CTA, candidate unsubscribe, publisher postal form and conditional commercial disclosure. **Always** send_authorized=false: no syntax or human attestation can authorize a send.
- test_received_email_gate.py: ten native Python synthetic-only unit tests, including commercial permission, all-true claimed attestations, false postal placeholders and privacy.
- LIVE_PREVIEW_AND_CONSENT_RELEASE_RUNBOOK.md: specifically ordered proof request, no-send bounds and provider count reconciliation.
- MERCHANT_EVIDENCE_AND_COPY_GATE.md: seller-specific claims, warm-up guide status and partner authorization checklist.
- SIX_ISSUE_EDITORIAL_DECISIONS.md: founder-pending six-edition choices with 4:2 unchanged.
- QA_EVIDENCE.md: source, native execution and limitations.

Reproduction: cd dispatch/r342 && python -m unittest -v test_received_email_gate.py. Synthetic address **123 Example Street, Sample City, CA 00000** in test fixture is deliberately fictional and must never appear in publication. This tool cannot prove authentication, mailbox receipt, address ownership or opt-out endpoint operation.

Source refs: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175 ; https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201 ; https://wordpress.com/support/newsletter/email-appearance/ .

**Release:** all six HOLD_UNSENT; 03 and 05 HOLD_MERCHANT. Mind #171 owns merchant authorization and vetted guides, Focus #129/Claude owns provider confirmation and welcome, Grok/Praxxis own social, Claude owns production analytics, founder owns final release. Homepage #150/frozen PR #49 unaffected.
