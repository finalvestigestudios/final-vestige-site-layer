# Jetpack native-email / CAN-SPAM acceptance — founder-gated, no send

**Date/source:** authenticated newsletter status & settings read 2026-11-16 10:35 UTC; WordPress.com [email appearance](https://wordpress.com/support/newsletter/email-appearance/), [email defaults](https://wordpress.com/support/newsletter/disable-newsletter-emails/), [subscriber status](https://wordpress.com/support/subscribers/) (reviewed 2026-11-04); FTC [CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business). Current source-only sprint never entered the native post editor.

## Verified provider configuration (read-only)

- Newsletter `subscriptions=true`, `site_can_send=true`; **this is platform capability, NOT authorization**. `email_new_posts_by_default=false`; the last five WordPress posts each report `never_sent_opted_out`, not a campaign send.
- `email_content_format=full` (**not historical excerpt-mode baseline**), `from_name="Final Vestige Studios"`, `reply_to="no-reply"`, date included, featured image included, author/gravatar excluded, newsletter categories not constrained.
- Welcome text includes a 52-page Fieldbook PDF URL; receipt of that welcome in an eligible email inbox remains **unknown**.
- Counts `total=3`, `confirmed=3`, `unconfirmed=2`, `suppressed=0`. They are not added. **Unique opted-in and deliverable inbox denominator unknown**. WordPress.com Reader subscriptions are not equivalent to receiving emails.
- WordPress official appearance docs say sender address is WordPress-controlled. Site-display `from_name` is not verified publisher header compliance; preview sender cannot be inferred from offline HTML.

## Per-issue true-native Preview proof (all UNVERIFIED)

1. **Only after founder authorizes a private WP draft/editor access path**, place exactly one approved post-shaped issue in a non-public editor state. Keep `Send this post to subscribers` disabled and its automatic-default off. Do not Publish, Schedule, or choose **Send test email**. Preview email is non-sending; if unavailable in connector, record **NOT TESTED**, do not substitute browser screenshot of static HTML.
2. Inspect editor's **Newsletter → Email → Preview email** at desktop, tablet and mobile, preserving test screenshots privately. Record sender/from display, **actual subject from the WordPress post title**, preview text if supported (the planning-file preheader is NOT guaranteed to be used), content length, images, alt text, 320px wrap, keyboard links and source list.
3. Capture genuine rendered footer in preview: qualifying **Final Vestige publisher** postal mailing address and a distinct unsubscribe mechanism. The postal address in an Automattic confirmation or on a merchant sales page does not automatically satisfy this. Footer placeholder strings `[[VALID_POSTAL_ADDRESS_REQUIRED]]` and `[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]` must never reach an inbox.
4. A preview can verify link visibility but cannot itself demonstrate an unsubscribe link **works** or prove email delivery. Functional opt-out must be independently verified by authorized, privacy-safe means; no list contact or test email without explicit founder approval.
5. Confirm consent and audience: private Jetpack Subscribers filter by **Email subscription = Subscribed** and handle Bounced/Paused/Not Sending. Preserve no personal addresses in GitHub, comments, logs or artifacts; only aggregated counts and opaque proof reference.
6. Verify CTA: editorial issues have one primary approved live historical/Fieldbook destination; commercial Issues 03 and 05 must use **published, approved, accessible Mind warm-up guides**, not vendor direct links, while email promotion and actual SKU earning rights remain blocked until authenticated merchant evidence.
7. FTC commercial-purpose assessment is required **even when a newsletter includes original historical reporting**. Honest headers/subjects, clear identification, valid sender postal address, effective unsubscribe and honoring opt-outs are release conditions. Affiliate disclosure **beside** qualifying offers and within issue is also mandatory. Avoid implying a product's effectiveness is independently proven.
8. Re-test after any content/settings/plugin/template change. Report `BUILT`, `OFFLINE_TESTED`, `NATIVE_PREVIEW_VERIFIED`, `RECEIVED_EMAIL_VERIFIED`, `SENT` separately; no one status implies another.

## Proof ledger — current

| Acceptance evidence | Observed | Proof needed | Owner |
|---|---|---|---|
| Provider newsletter enabled / default sends off | PASS (read-only API) | Re-check before authorized draft | Dispatch |
| Six source drafts + original Python checks | PASS, source-locked #175 | Native source suite 6/6 this sprint | Dispatch |
| Actual subscriber email eligibility | UNKNOWN | Private provider eligible-email filter + dedup | Focus/Claude |
| Fieldbook **received** welcome | UNKNOWN | Existing authorized received-email evidence | Focus/Founder |
| WordPress native **Preview email** | NOT PERFORMED | Actual editor preview screenshots without a send | Founder/Dispatch |
| Footer publisher postal address | UNVERIFIED | Qualifying FV mailing address visibly rendered | Founder |
| Footer opt-out present and functional | UNVERIFIED | Privacy-safe real provider/received-message verification | Founder |
| Named partner EMAIL rights and live guides | UNVERIFIED | Merchant acceptance, product/SKU grant and Mind page QA | Mind/Commerce |
| Final founder send approval | NOT GIVEN | Explicit separate go-live authorization | Founder |

**Decision:** all six canonical issues remain HOLD_UNSENT, not ready for native dispatch. The "Preview email" action is distinct from "Send test email" in official WordPress docs. Nothing was emailed or scheduled.
