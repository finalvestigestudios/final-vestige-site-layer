# R98 — Dispatch/Focus consent and email-footer decisions

**PROPOSALS ONLY — no live page or newsletter setting changed.** Reviewed authenticated WordPress pages 523 (/dispatch/) and 1579 (/focus/) on Nov 3, 2026.

## Specific discrepancy
Published /dispatch/ describes historical investigations, archive finds, one Fieldbook welcome download, email confirmation and "Unsubscribe anytime", but omits future affiliate-recommendation consent explanation. Published /focus/ explicitly says: "Some emails may include recommendations that earn us a commission." Both routes use **the existing single Jetpack list**. This is a real, source-visible marketing expectation mismatch, but does not by itself prove a legal violation.

## Copy proposed near /dispatch/ native Jetpack block — NOT DEPLOYED

> Join The Dispatch for evidence-led investigations, historical discoveries and occasional Mind & Perception field notes, sent when there's something worth sharing—not every day. Your welcome message includes the free 52-page Seven Day Focus Fieldbook. Some editions may include optional product recommendations that earn Final Vestige a commission if you buy through a qualifying link. Recommendations don't determine our historical conclusions. One newsletter list. Unsubscribe anytime. Privacy Policy.

Retain WordPress native Subscribe block, no new list, no additional signup service or analytics. Keep the separate link to /focus/. Founder approval plus visitor-browser accessibility and functioning native form QA would be required before any actual page edit.

## Why this is not just a footer text change
Jetpack settings show email_content_format=excerpt, reply_to=no-reply, and email_new_posts_by_default=false. A full WordPress post containing a disclosure does NOT establish that a truncated email excerpt includes it. A no-reply sender does not create a functioning reply-based opt-out route. A browser/static HTML preview cannot establish the real outgoing MIME or the success of an unsubscribe action.

Current /dispatch/ REST-rendered subscriptions markup contains a same-page Subscribe link; this might correspond to a working dynamic modal, NOT proof that signup is broken. Test the actual visitor interaction in an authorized browser before diagnosing it.

## Real commercial-message release evidence — all unavailable

1. **Business postal**: founder privately verifies a Final Vestige-controlled qualifying street/registered USPS PO box/registered commercial mailbox; no home address in GitHub. Never substitute Automattic or merchant addresses. Mark NOT VERIFIED.
2. **Opt-out**: privately review an authorized genuine received Jetpack email and test actual unsubscribe operation; link presence alone not enough. Mark NOT VERIFIED.
3. **Recipient**: reconcile eligible active Email Subscription status privately, without putting identities into PR/Issue/analytics. Total=2,confirmed=2,unconfirmed=2 plus email-followers=0/wpcom-followers=2 does not resolve audience. Mark UNKNOWN.
4. **Welcome**: distinguish received final 52-page Fieldbook welcome from October 25 subscription CONFIRMATION. Receipt NOT VERIFIED.
5. **Email rendering**: establish subject, excerpt, disclosure, source links, footer, accessibility in actual Jetpack output; native preheader field NOT VERIFIED. Don't turn on per-post send toggle or send even a test without founder approval.
6. **Merchant**: named SKU-specific written email marketing rights, approved links/creative, current checkout/refund, no identifiable affiliate buyer data arrangement, and two approved published warm-up pages. NONE VERIFIED.
7. **Founder**: explicit separate final campaign/audience/send approval NOT GRANTED.

Official:
https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
https://wordpress.com/support/newsletter/email-appearance/
https://wordpress.com/support/newsletter-settings/
https://wordpress.com/support/subscribers/

Priority: make the existing signup consent truthful and acquire authorized native received-email evidence before collecting more subject variants. Do not modify homepage flagship or frozen #49.
