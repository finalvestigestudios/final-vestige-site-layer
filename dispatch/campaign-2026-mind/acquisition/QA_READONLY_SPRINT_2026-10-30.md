# Read-only QA report — Dispatch acquisition sprint, October 30, 2026

**Environment:** all existing newsletter operations read-only; GitHub-only proposed artifacts. No email, send, subscriber import, merchant link activation, WordPress edit, social publish, paid provider, contact export, or schedule.

## Directly observed WordPress facts
- Site `finalvestige.com`, ID 256784396; `/dispatch/` page 523 published, `/focus/` page 1579 published.
- Live newsletter settings: `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `from_name=Final Vestige`, `reply_to=no-reply`.
- Welcome message includes the 52-page free Focus Fieldbook PDF, no paid offer.
- Newsletter status as of `2026-10-30T20:36:24Z`: `recent_sends=[]`, counts `total=2`, `confirmed=2`, `unconfirmed=2` (inconsistent).

## Current references checked
- Official WordPress [newsletter settings](https://wordpress.com/support/newsletter-settings/) confirm the excerpt mode is 55 words without a custom excerpt, and custom excerpt/full text options; [email preview](https://wordpress.com/support/newsletter/email-appearance/) confirms editor Preview and test-send are separate. An offline HTML preview is **not** proof of an actual Jetpack email.
- Inspire3 [Zen12 sales page](https://zen12.com/) asserts 12-minute/hour equivalence. Treat as unverified seller efficacy claim. Hypnosis Live [FAQ](https://hypnosislive.com/faq) lists MP3 duration, access and refund terms. Neither establishes partner account/email-marketing authorization.
- [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires accurate sender/subject, clearly marked promotional relationship, valid business postal address and effective opt-out in commercial email.

## Independent executable QA in this run
- **14/14 Python unittest checks passed** locally in `/mnt/data/fv_dispatch_gate` against the previously staged synthetic release-gate fixture, not the complete current GitHub head. Tests were run with `python -I -m unittest discover -s tests -v`. The original full PR #175/178 suite cannot be truthfully called green; container network DNS cannot resolve github.com for a full checkout.
- This sprint's six-source-creative JSON receives a separate connector-side structured review; check its exact committed content and blob SHA after PR creation. Further real creative/video/email preview, footer, browser/a11y validation are not yet performed.

## Still BLOCKED
- Distinct confirmed deliverable audience and consent reconciliation.
- Merchant approval and permission to promote by email; product-specific earning links and final checkout terms.
- Actual WordPress-received test with commercial footer, postal address, unsub and verified sender headers; founder authorization for test recipient.
- Zen12 and Hypnosis Live live warm-up destinations; final send approval.

**Do not infer a subscriber growth rate, conversion lift, new delivered emails, a public campaign, or sales from these source-controlled drafts.**
