# R292 — evidence protocol: editor preview versus actual delivery

## What cannot substitute for a received email

- Offline HTML (R287 or R292) establishes author-produced markup only.
- Jetpack native **Preview email** establishes WordPress editor rendering only, even if reviewed at desktop/tablet/mobile.
- A subscription confirmation request establishes only a request, not a confirmed eligible recipient or delivered welcome.
- The `site_can_send` diagnostic is a platform capability. It is NOT an approval, nor evidence of current sendable audience.
- WordPress/Automattic mailing address printed on a platform confirmation email does NOT establish the physical business address of Final Vestige Studios.
- A visible unsubscribe *label* is not proof that a recipient can actually opt out.

## Ordered acceptance steps, all held until authorized

1. Freeze the exact issue source SHA, check issue number, official sources and 4:2 allocation; no merge, publication or schedule.
2. Without changing WordPress content, founder or authorized owner may inspect current editor's **Preview email** only if a previewable existing draft is present; verify sending toggle is still OFF. Do not create one as a workaround. Record editor screenshot/hash, captured UTC, subject, preheader, HTML/text rendering, links, accessibility review and measured 320/390px legibility. No sending required for preview according to WordPress support.
3. Independently audit valid *Final Vestige-owned* registered commercial mailing address for commercial emails, check exact rendered postal text, and request separate legal review. Never silently insert Automattic's address.
4. Separately authorized genuine received-email test ONLY upon founder's specific permission: preserve sender identity, raw MIME HTML/plain source, visible footer, actual opt-out procedure test; use owner-controlled dedicated test account and do not contact existing subscribers without permission. No newsletter test sends in this sprint.
5. Reconcile private provider eligibility (confirmed vs unconfirmed vs suppressed vs digest or Reader only), double-opt-in and successful welcome/Fieldbook delivery in a private authorized context. No exposed addresses in issues/PR.
6. Merchant approval separately authenticated from private source-of-truth: partner account acceptance, permitted EMAIL marketing, issued earning URL, live compliant buyer guide, approved creative rights, current checkout product terms, seller vs independent efficacy distinctions.
7. Record founder final campaign approval **after** all gates, exact version and audience, schedule and release method. Until then every outcome is HOLD_UNSENT.

## Applying the offline tool responsibly

Run `node dispatch/r292/test_release_gate.cjs`. Current `observed-evidence.json` is read-only actual diagnostic evidence and intentionally has no native preview, received MIME, address, opt-out, affiliate approval, founder signature or eligible audience proof. The auditor always returns HOLD_UNSENT. It can highlight omitted fields in an authenticated capture report, but cannot verify that a checkbox is truthful, that an opt-out works, or that a real person is eligible; those require independent evidence and human judgment. No private subscriber data should ever be stored in this repository.

Source documents: https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking .
