# R61 operational decision memo — close the evidence gap rather than add simulated certainty
**2026-11-02 07:35–07:45 UTC · isolated stacked draft · no send authority.**

## What was actually read
Authenticated GitHub Issue #174 (136 comments at check), Issue #171 including Mind Studio R63/R64 handoffs, master draft PR #175, companion PR #201, latest Dispatch #574 head `06f8703ff02d9d0c89d26c9ba1b458a14d6bf5d9`, manifest and canonical Issues 03/05, source standards, and live WordPress pages **/dispatch/** (id 523), **/focus/** (id 1579), **/editorial-standards/** (id 17). The authentic WordPress settings and status calls returned values recorded in the separate `wordpress-readonly-snapshot.json`. No WordPress write or subscriber enumeration occurred.

## Critical new operational clarification
The platform itself **supports custom excerpts**. In the existing excerpt mode, publishing a post with an intentional custom excerpt is a plausible way to surface a transparent early commercial notice without switching the entire site to full-text email. That does **not** authorize installing these excerpts or prove they will appear unchanged in a recipient's mailbox. These six `excerpt_packet.json` entries are a proposed **post metadata treatment**, not email HTML or a mail merge. The **post title** is the documented native email subject. The separately written **preheader** may not be controllable through Jetpack and must be checked against actual rendering rather than promised. Native preview requires temporarily enabling the post-level send toggle; the setting may remain dangerous if the post is later published. Do not touch it without separate founder authorization and a reviewed rollback step.

WordPress support: https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter-settings/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ .

## Freshly verified status / privacy interpretation
At 07:35 UTC on November 2, WordPress returned newsletter `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `reply_to=no-reply`, sender name Final Vestige, and a configured welcome text explicitly linking the existing 52-page Focus Fieldbook. `site_can_send=true` is **technical capability**, not authorization. `recent_sends=[]` is only an empty returned window, not a provable all-time zero. Counters are 2 total / 2 confirmed / 2 unconfirmed / 0 suppressed. The unconfirmed bucket can be excluded from total; do not sum them or claim exact distinct eligible recipient count. Keep any consent audit within authorized WordPress admin, not GitHub or a public issue.

**/dispatch/** gives the historical investigations-and-archive promise and no corresponding near-form disclosure of future commission-earning recommendations. **/focus/** explicitly mentions that some dispatches may contain commission-earning recommendations. These are two entrances to the same list, creating a real expectation mismatch but not by itself proving unlawful consent. R52 PR #517 already provides remediation options; do not duplicate or quietly deploy its wording. The configured welcome gift should not be changed just to solve this gap.

## Merchant-source contradiction sharpened by this run
The current 2026-11-02 retrieval of the **named Total Focus** page described **33 minutes / 47 MB** and displayed **$24.44 from $29.95**, while the previous R60 source review recorded a **$2 promotional presentation**, and an older search-engine snapshot showed **$17.95 from $22.95**. Same-product public presentations differ materially; whether that reflects visitor targeting, elapsed offers, geography or indexing cannot be inferred. Therefore **no newsletter price, 'today only' promotion, bargain percentage or refund guarantee can be independently promised**. Fresh source URL: https://hypnosislive.com/mental-skills/total-focus . Zen12 named https://zen12.com/hnp advertises hour-equivalent meditation and other substantial outcomes, but its vendor sales copy is not a product-specific independent experiment. Inspire3's https://affiliates.inspire3.com/ sign-up/recruiting is not Final Vestige-specific enrollment or email marketing permission. Claims are vendor representations; don't import their testimonials as independent support.

## Before any final founder approval, what actually must change
1. **Identity/legal:** Identify an actual Final Vestige Studios valid physical postal address (a qualifying USPS PO box or registered commercial mailbox may be acceptable under FTC guidance), verify it in the bytes of a received commercial email, and verify the real business identity shown to a recipient. Do not copy the merchant's London or Automattic footer as Final Vestige's.
2. **Unsubscribe:** Acquire an original authorized received email with its headers and MIME parts, confirm visible opt-out works and policies honor opt-outs. The Oct 25 subscription confirmation is **not** a newsletter or completed welcome. No simulated email proves this.
3. **Subscriber eligibility:** Check privately whether the two confirmed registrations match independently consented mail-receiving preferences; resolve double-opt-in and digests without exporting or posting addresses. Do not present 2 confirmed as 2 currently reachable.
4. **Merchant eligibility:** Obtain a written account-specific approval for **Zen12 and Total Focus separately**, permitted commercial **email** channel, source of approved affiliate creative, earning URL structure, and exact checkout/refund privacy claims. A general catalog and public recruiting page are insufficient.
5. **Destinations:** Wait for Mind Studio #171 to obtain founder-approved, published and tested first-party guide URLs. PRs #570/#578 are **unpublished drafts**, not permissible outbound destinations. The commercial CTA remains disabled.
6. **Actual Jetpack QA:** Only after separate explicit authorization, use an isolated non-subscriber post and an approved recipient for native preview and a real received email. Preserve auto-send OFF; explicitly restore any per-post send toggle to OFF before leaving the editor, and prove the state. Check subject, excerpt, sender, commercial notice near CTA, actual postal footer and functioning unsubscribe, mobile rendering, and welcome delivery. A preview screenshot alone is not a received message.
7. **Final explicit founder signoff:** Exact body, subject, audience, delivery time, published guide link and any personally-identifying mail artifacts must be privately reviewed before any send. There is no blanket authority for a six-week calendar.

## Analytics, launch-readiness and consent protections
Only count what a platform actually returns: messages accepted/delivered vs opens (imperfect proxies) vs unique clicks (if available). A website pageview is not a buyer conversion; an affiliate click is not a commission. Use read-only aggregate reports, no tracking pixels, PII query parameters, synthetic successes, or A/B significance with a tiny list. Hold any tagging/tracking change until a separately approved privacy and implementation plan. Existing Jetpack and website are the only approved stack.

This is an **editorial-preparation decision package**. No manuscript, production site, WordPress post, subscriber record, newsletter setting, merchant campaign or homepage PR #49 is changed.

## Primary source links / authority
- FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- FTC material connection: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- WP original-email preview and custom excerpt: https://wordpress.com/support/newsletter/email-appearance/
- WP exact settings: https://wordpress.com/support/newsletter-settings/
- WP sending mechanics: https://wordpress.com/support/newsletter/send-newsletter-emails/
- Product sales: https://zen12.com/hnp ; https://zen12.com/getstarted ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq
- Public affiliate recruiting (not permission): https://affiliates.inspire3.com/
- Mind #171 and Dispatch #174 original internal evidence.
