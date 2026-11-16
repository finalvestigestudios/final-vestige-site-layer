# R401 — Jetpack effective subject/preheader gap (2026-11-16 UTC) — HARD HOLD

## NEW substantive renderer finding
The canonical six-issue PR #175 has polished `**Subject:**` and `**Preheader:**` lines in Markdown. These are editorial proposals, **not proof of the actual MIME Subject or inbox preview snippet.**

WordPress's current official guide, reviewed 2026-11-13, says: *the post title is used in the subject line of the email*. The Newsletter preview uses the actual post inside the WordPress block editor. **A Markdown preheader label is not an authenticated Jetpack preheader feature.** Do not imply that a preheader renders as independently configured metadata until a native preview or received message proves it.

- Official post/email subject guide: https://wordpress.com/support/newsletter/send-newsletter-emails/
- Official renderer and per-device native Preview email (not the Send test email action): https://wordpress.com/support/newsletter/email-appearance/
- Email Design official guide (last reviewed 2026-10-30, staged rollout): https://wordpress.com/support/newsletter-email-design/
- Newsletter setting documentation / double opt-in and welcome: https://wordpress.com/support/newsletter-settings/
- FTC CAN-SPAM guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## Read-only authenticated site facts at 2026-11-16 13:44 UTC
Site ID 256784396, newsletters enabled; `email_new_posts_by_default=false`; `email_content_format=full`; `from_name=Final Vestige Studios`; `reply_to=no-reply`; `featured_image_in_email=true`. Five latest post notifications: never_sent_opted_out. Total=3, confirmed=3, unconfirmed=2, suppressed=0, imported_last_24h=0. WP.com followers=3, direct email followers=0. **These category counts are not additive and do not establish three unique reachable inboxes.** Welcome message text links the free 52-page PDF; receipt is unknown.

`site_can_send=true` reflects a technical capability, **not authority**. Post email default is OFF. No WordPress config was altered.

## How to get the actual proof without sending
1. After founder authorizes a *draft-only WordPress editor preview*, create/inspect a private unsent post draft with newsletter Send toggle **off**. Do not publish or schedule. Use the site's existing post editing workflow and never turn ON Send.
2. Set WordPress **post title** to the separately approved email subject; inspect Newsletter → Preview email on desktop/tablet/mobile. Compare rendered headline, subject, intro snippet, CTA, link labeling, mobile wrapping, featured image and source links. Record real screenshots and editor URL privately. **Do not click Send test email.**
3. Determine whether Appearance → Email Design exists for this site; its rollout is staged and the current account's availability is unverified. Do not modify design settings.
4. Confirm the actual legal footer including Final Vestige's valid business postal address and its functional unsubscribe URL in an *authorized, privately retained received email* or the provider's authoritative controls. A visual footer hyperlink alone does NOT prove live opt-out; approved test of opt-out requires separate founder authorization and must not damage the only tiny subscriber list.
5. Confirm the verified provider-level email-recipient eligibility list and actual *welcome* receipt (not a confirmation request). Keep addresses and tokens private. A `?subscribe=` page parameter or `after_signup` download click is not an opt-in confirmation.
6. Record: issue number, exact reviewed post title, real preview screenshot reference, what preview text actually appears, business-address verification method, unsubscribe-operation proof and reviewer/date. No customer PII in GitHub.

## Failure modes to test
- An approved draft headline is not the actual WordPress post title; WordPress email subject differs.
- Markdown `Preheader:` is put in body text; reader sees editorial metadata or an unplanned leading snippet.
- A beautiful offline table-based HTML fixture does not match the WordPress-generated email.
- A site's new Email Design is assumed live when rollout is incomplete.
- `reply_to=no-reply` means replies cannot be treated as reliable unsub requests; do not treat this as opt-out evidence.
- Newsletter sample size of three confirmed accounts is not permission to call all three deliverable email inboxes or to claim A/B significance.

## Decision
**All original 1–6 HOLD_UNSENT.** Issues 03/05 also HOLD_MERCHANT; Issue 04 HOLD_COPY. R401 Issue02 alternative NOT_ADOPTED. Founder final approval for sending remains a separate unperformed action. Reconcile with Issues #174, #171, #129, #820; frozen homepage PR #49 untouched.