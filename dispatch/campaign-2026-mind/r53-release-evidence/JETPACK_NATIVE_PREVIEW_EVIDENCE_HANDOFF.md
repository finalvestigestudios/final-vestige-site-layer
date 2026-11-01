# R53 — Native Jetpack email preview and received MIME evidence protocol

**No action authorized or performed.** As of **2026-11-01 23:35 UTC**, authenticated read-only WordPress site 256784396 reports Jetpack Newsletter enabled/technically sendable, **new-post email default OFF**, global **excerpt** delivery, featured image/date ON, sender display **Final Vestige**, reply-to **no-reply**, configured 52-page Focus Fieldbook welcome, and **no reported recent sends**. Subscriber diagnostic counters: **total=2, confirmed=2, unconfirmed=2**. They are nonadditive; the distinct consent-eligible count is UNKNOWN.

## Crucial manual-send hazard (verified against official provider guidance)

WordPress's [Email Appearance](https://wordpress.com/support/newsletter/email-appearance/) guidance states that a post's individual **Send this post to subscribers** toggle must be ON to expose the native **Preview email** and **Send test email** controls. Its [send guide, last reviewed October 19, 2026](https://wordpress.com/support/newsletter/send-newsletter-emails/), describes changing that per-post option independently of the default. Therefore arming a preview can also arm a newsletter send if the post is subsequently published. The global default-off state is NOT an absolute send interlock.

**Founder has not approved creating a WordPress draft newsletter post, arming the per-post email toggle, sending a real test, scheduling, or publishing. None of those actions is executed here.** An offline HTML preview or passing Python suite cannot stand in for native Jetpack evidence.

## Founder-controlled procedure for a future SEPARATELY authorized preview

1. Record exact founder-approved issue/source commit and confirm that no affiliate or direct merchant checkout link is present. Capture the current newsletter defaults, including excerpt mode and the per-post switch, before an editor is touched. Preserve canonical PR #175 and all gates.
2. Obtain separate written permission for a **preview-only draft** workflow, including how to temporarily expose WordPress's native preview without mailing anyone. Preview permission is not test-send, publish, or send permission.
3. Use the native WordPress **Preview email** on desktop, tablet and mobile if and only if permitted. Check whether the post title becomes the actual subject, what appears as any generated preheader, the literal custom excerpt or fallback, the view-post destination, source links, accessible text, image weight and disclosures. A Markdown preheader is **not an established Jetpack native control**.
4. Verify that both commercial issues still display disabled first-party guide CTA placeholders while Mind #171 lacks an approved **published** guide and named-product EMAIL rights. The original Issue 03 has directly clickable seller citations; optional R50 quarantine copy is not approved for substitution.
5. Before leaving the editor, explicitly restore **Send this post to subscribers OFF** on the draft, confirm unpublished/no schedule, and preserve evidence of the returned OFF state. If that state cannot be confirmed, stop; do not publish.
6. Only after a **different explicit founder approval** may a genuinely **sent test** reach an authorized recipient. Never email the subscriber list for testing. Retain the received original RFC 5322/MIME privately and run the pre-existing R45 independent MIME inspector on both text/plain and HTML. Store only redacted pass/fail evidence and receipt metadata without recipient identifiers.
7. Independently verify actual commercial footer with a **valid Final Vestige business mailing address**, clear functional unsubscribe, accurate sender and honest subject. The October 25 Automattic subscription-confirmation message proves neither the Fieldbook welcome's successful delivery nor Final Vestige's address/opt-out in a commercial email. Test one issue/format does not automatically validate other commercial issues.

## Required evidence, all incomplete

| Requirement | Acceptance evidence | Status |
|---|---|---|
| Native preview | WordPress-generated desktop and mobile previews, switch returned OFF, exact source version | NOT VERIFIED |
| Received MIME | Real separate authorized test, original RFC 5322, redacted independent review | NOT VERIFIED |
| Subject / preheader | Native actual title, preview text and excerpt in each format | NOT VERIFIED |
| Excerpt / CTA | Native delivered excerpt, landing-link routing, early affiliate disclosure as applicable | NOT VERIFIED |
| Unsubscribe | Actual clear functioning opt-out mechanism in commercial received email | NOT VERIFIED |
| Postal address | Actual valid Final Vestige physical publisher address in commercial received email | NOT VERIFIED |
| Welcome receipt | Actual received final 52-page Fieldbook welcome (not just confirmation) | NOT VERIFIED |
| Unique eligible audience | Private deduplicated confirmed/suppressed consent audit | NOT VERIFIED |
| Merchant authorization | Named product, publisher, channel=EMAIL, creative and earning URL rights | NOT VERIFIED |
| Commercial buyer guides | Approved and actually published first-party URLs | NOT VERIFIED |
| Founder final permission | Exact content, recipients, send dates and approvals | NOT GIVEN |

## Private aggregate subscriber reconciliation

The connector exposes conflicting **total=2 / confirmed=2 / unconfirmed=2**, not recipient-level eligibility. Do not add those figures to infer four people or claim exactly two distinct eligible addresses. A separately authorized WordPress admin should inspect the provider's status categories and confirmed/suppressed eligibility **privately and without export**, preserve only derived aggregate figures, explain their denominator definitions, and re-check the audience immediately before any authorized dispatch. If a safe administrator view is unavailable, leave eligibility UNKNOWN. No subscriber email addresses or confirmation tokens should be written to GitHub.

**Legal boundary:** [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) commercial-primary-purpose analysis considers actual subject/body layout, postal identity and opt-out. [FTC material-connection disclosure guidance](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) applies where relevant commercial endorsement exists. A source-based QA check does not certify legal compliance.

**END STATE:** All six HOLD_UNSENT, Issues 03/05 HOLD_MERCHANT, zero test sends or production writes.
