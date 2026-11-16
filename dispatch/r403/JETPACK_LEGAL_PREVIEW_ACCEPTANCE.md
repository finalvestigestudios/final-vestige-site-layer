# R403 · Genuine Jetpack Preview and CAN-SPAM acceptance (non-sending)

## Current provider state (read-only, 2026-11-16 16:38 UTC)

Site 256784396: `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=full`, reply-to `no-reply`, from-name `Final Vestige Studios`. `total=3 / confirmed=3 / unconfirmed=2 / suppressed=0`. Jetpack Stats reports `wpcom_followers=3 / direct_email_followers=0`, not a deliverable-audience count. Five latest post notifications are `never_sent_opted_out` with no dispatched timestamp; this is desired, not a failed campaign. Welcome message contains direct public PDF to the 52-page Focus Fieldbook but **configuration ≠ receipt**.

## Exact non-sending native UI inspection needed

Open a **nonpublished draft** only under explicit approval to enter CMS, with `Send this post to subscribers` OFF. Editor's paper-airplane Newsletter pane → **Preview email** (not `Send test email`) → inspect desktop/tablet/mobile. The 2026-11-09 updated WordPress support states the preview works with email toggle off. Capture screenshots of actual subject, full-body content, CTA destinations, advertising identification, near-link disclosure, image alt text, mobile reading, click target, sender display and footer. DO NOT publish/schedule/press Send test email. An offline HTML page is not a Jetpack preview. Current connector has **no Preview email action**, so this acceptance step remains **NOT_PERFORMED**.

Check actual email subject equals intended WordPress post title. Planned preheader is *editorial metadata*, not a verified platform feature. Include a human-readable textual first sentence if a preview snippet is desired; do not claim independent `Preheader` setting. Current full content mode may expose more of the proposed editorial text than earlier excerpt-mode specs; rerun parity QA after site has approved draft.

## Footer and opt-out

Commercial content may trigger CAN-SPAM even on a research-oriented site. Verify Final Vestige's **actual valid physical postal address** in the *rendered sender email*; do not use Automattic or Inspire3's mailing address as FV's. Verify a recognizable functioning unsubscribe (including single-page completion/no additional PII), suppression honored, opt-out processing within 10 business days, accessible text and business identity. No synthetic unsub URLs or untested placeholders can be counted as a pass. FTC requirements: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## Screenshot-proof record fields, never real subscriber PII

`inspector_name`, `UTC_datetime`, `draft_post_id`, `preview_capture_id`, `subject_matches_post_title`, `preheader_visibility`, `full_or_excerpt`, `body_visible_mobile`, `valid_FV_postal_present`, `unsubscribe_visible`, `unsubscribe_operational_authorized_test`, `near_offer_disclosure_adjacent`, `all_links_approved`, `all_claims_checked`. Each field needs source reference, outcome PASS/FAIL/NOT_TESTED and owner acceptance. Do not collect name/email/address of a subscriber; FV's business contact address is separately owner-approved.

## Release verdict

CURRENT: `HOLD_UNSENT`, all six. `HOLD_MERCHANT` issues 03/05. `HOLD_COPY` canonical Issue04. No email tests or preview tests were performed. All booleans in a synthetic QA fixture must never be construed as real proof or sender approval. Founder final campaign approval is an independent requirement even after all QA passes.

Source: https://wordpress.com/support/newsletter/email-appearance/ (reviewed November 9, 2026); https://wordpress.com/support/newsletter/send-newsletter-emails/ (reviewed November 13, 2026); https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
