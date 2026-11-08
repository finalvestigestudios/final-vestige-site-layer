# R196 — Focus/Dispatch causal subscriber diagnostic (READ-ONLY)

## Evidence reviewed, 2026-11-07 15:37 PT / 23:37 UTC
WordPress /focus/ page 1579, latest stored modified 2026-11-05 17:44:02, includes browser JavaScript which reads `new URLSearchParams(window.location.search).get('subscribe')`, and reveals `#fvf-gift` for any truthy value not in a small hardcoded error array. It separately watches a client-controlled `is-subscriber` CSS class. This is a reproducible **client display logic issue**, not a proven server-side subscription exploit, and not proof that a signup happened. It was already identified in Dispatch R195; this document tightens the **minimum acceptance test and actual owner handoff** rather than pretending to discover it anew.

### High-impact correction for the Claude-owned site (not implemented)
1. Treat the page-level PDF display as `fieldbook_displayed`, not `confirmed_signup`. The PDF can be downloaded independently of the email provider's opt-in state; this is fine if described accurately.
2. Keep the success text explicit: 'You can download the Fieldbook now. Confirm the email sent by WordPress to subscribe; your newsletter subscription is not yet verified on this page.' This text is a candidate, not a production patch.
3. Never generate the marketing lead event from a URL query, CSS class, form submit, PDF click, or thank-you state. Only the authoritative Jetpack/WordPress email-subscription provider's **confirmed subscription transition** may qualify. Confirm whether the provider exposes a webhook, state change history or trustworthy aggregate before proposing instrumentation.
4. Deduplicate within the private provider/backend boundary: stable provider event ID plus a secure, non-reversible pseudonymous internal key; no raw emails, cookie IDs, hashed addresses without appropriate salt/secret, or subscriber counts in public issue comments. A repeated callback is one confirmation, not two.
5. A WordPress.com Reader follower and a recipient with a verified email-subscription status are separate populations. Do not sum `newsletter.confirmed` and `followers.wpcom`. Do not infer `followers.email = 0` means no eligible recipients.
6. Preserve an auditable distinction between 'provider-confirmed and currently eligible', 'unconfirmed request', 'suppressed', 'Reader only', and 'unknown'. A snapshot of counters is not an individual consent audit.
7. The actual sending population is UNKNOWN until the provider-filtered **Email subscription = Subscribed** aggregate is read authoritatively; do not expose email addresses or perform new signups.

### Non-sending acceptance scenarios (no list contact)
- Arbitrary `?subscribe=success` and `?subscribe=foo`: the page may reveal a gift but **must not** emit confirmed_signup. FAIL in current source if anyone equates the visual state with a confirmation.
- Existing subscriber whose browser lacks `is-subscriber`: do not treat absence of the class as an unsubscribe. Provider is source of truth.
- Duplicate provider callback: private idempotency check yields one event, not two.
- Unconfirmed double opt-in: keep in pending status until authoritative transition.
- Suppressed/unsubscribed address: never classified as reachable, even if previously confirmed.
- No authorized provider events: report UNKNOWN, not 0.
- Welcome configured does not prove receipt. A 2026-10-25 Gmail request to confirm subscription is **not** a received final Fieldbook welcome. A true delivery check requires pre-existing authorized receipt or separately approved test; this sprint sent nothing.

### Existing observed WordPress snapshot
At 2026-11-07T23:37:49Z: Newsletter enabled, site_can_send=true, 3 total counted / 3 confirmed-counter / 2 unconfirmed requests / 0 suppressed; the 5 most recent published posts are `never_sent_opted_out`. At 23:37:50Z: `email_new_posts_by_default=false`, `email_content_format=full`, sender name 'Final Vestige Studios', `reply_to=no-reply`; welcome is configured with the 52-page PDF link. Separate followers source reports `wpcom=3`, `email=0`, `partial=false`. These categories **cannot be added**; email-eligible count and received welcome remain unknown.

### Closure proof for #129 and #174
Claude/Site QA should attach: a redacted provider-filtered email-eligibility aggregate; whether double opt-in is required for the actual form; consent source evidence; evidence a known existing authorized account received the configured welcome (with sensitive details removed); and zero new signup/sending actions unless the founder separately authorizes a controlled test. Do not claim the issue fixed until staging QA and independent code review demonstrate no browser-only conversion event. 
