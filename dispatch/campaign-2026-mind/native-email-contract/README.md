# Dispatch R10 — native WordPress email delivery parity

**DRAFT / HOLD · October 30, 2026 · Issue #174, companion Mind #171.** Stacked on draft PR #233. Does **not** touch WordPress production, subscribers, merchant links, homepage PR #49, or the original six newsletters.

## Why this is a substantive release issue

Our six approved **draft** newsletter editions are full research-grounded letters, but the authenticated live newsletter at `finalvestige.com` is set to **`email_content_format=excerpt`**. According to official WordPress documentation, when no custom excerpt exists the email contains the beginning ~55 words; a manually supplied custom excerpt can replace that introduction. WordPress post **titles** furnish the displayed subject, while a separately editable preheader has **not** been verified for this native sender.

The earlier full-length HTML preview files and planned standalone preheaders therefore do not establish what a Jetpack recipient would see. This sprint makes that mismatch explicit, without pretending to have sent or received mail.

## Source-controlled deliverables

- `NATIVE_DELIVERY_PARITY.json` — all **six exact-GitHub-source** post subjects, preheader plans, illustrative first-55-word source samples, proposed (not applied) custom excerpts, legal/merchant holds and 8 Git blob identities. All issues remain `HOLD_UNSENT`. Every sample is labeled **NOT** WordPress output.
- `NATIVE_DELIVERY_REVIEW.html` — polished, accessible, local-only side-by-side comparison for editorial review at mobile and desktop widths. It is NOT a WordPress email preview.
- `source_gate.mjs` — read-only Node 20+ gate verifying the original 4:2 split, all six source/excerpt alignment contracts, inactive merchant links, precise commercial disclosures, legal HOLD placeholders and unknown recipient count. It **never** reports release PASS or authorizes sending.
- `source_gate.test.mjs` — 11 committed mutation cases to reject title drift, product-link activation, loss of disclosure/hold, guessed subscriber audience, and false received-email claims.
- `MERCHANT_SOURCE_VOLATILITY.md` — seller-specific formats vs efficacy claims, conflicting checkout prices, and public recruiting material vs private partner approval.

This branch's creation-time live JavaScript source check succeeded on **6/6 original source issues** using GitHub's read-file connector, plus original status/manifest/excerpt comparisons. The parent R9 offline Python received-email auditor reran **72/72 tests passing** locally. The new **11 Node tests are committed but NOT yet executed against an exact checkout**, because direct container GitHub access cannot resolve DNS and GitHub Actions remains unavailable. Do not report them as green.

## How to reproduce (when exact checkout is available)

```bash
node dispatch/campaign-2026-mind/native-email-contract/source_gate.mjs
node --test dispatch/campaign-2026-mind/native-email-contract/source_gate.test.mjs
```

Keep output offline. The source checker reads the local checked-out campaign. It does not connect to WordPress, collect email addresses, send tests, or operate marketing automation.

## Authoritative, read-only site snapshot · 2026-10-31 03:31 UTC

- WordPress blog ID **256784396**, `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `reply_to=no-reply`, sender name **Final Vestige**.
- Welcome message includes the existing **52-page Focus Fieldbook** link. That confirms configuration, **not actual delivery**.
- `recent_sends=[]`. Dashboard counts **total=2, confirmed=2, unconfirmed=2**, so a unique, opted-in, deliverable audience is **not proven**. Never infer four subscribers or treat “confirmed=2” as delivery proof.
- The /dispatch/ (page 523), /focus/ (1579), Editorial Standards (17), and Affiliate Disclosure (14) pages remain published and unchanged. The website's editorial evidence identity remains the controlling standard.

## Real WordPress verification still required

When and ONLY when the founder separately authorizes a test, an authorized WordPress editor can create an unpublished draft, inspect the Newsletter paper-airplane panel and use **Preview email** (no sending) with the send-to-subscribers toggle enabled only for that draft. Return the toggle to OFF afterward. An actual **Send test email** requires independently approved test recipient, and the resulting MIME needs verification of sender identity, excerpt behavior, exact destination, *Final Vestige's* valid physical mailing address, conspicuous and functional unsubscribe, commercial disclosure and mobile rendering. A subscription-confirmation email bearing Automattic's address is not sufficient evidence.

The `newsletter.status` connector's aggregate counters cannot privately deduplicate/verify subscriber records. Reconcile only within authorized WordPress admin screens, with **no subscriber addresses uploaded to GitHub, logs or ChatGPT public artifacts**.

Zen12 and Total Focus first-party buyer-guide destinations are **not published**. We have no verified Final Vestige affiliate acceptance, written email-channel permission, approved earning link, exact live checkout or permission to embed seller creative. Neither commercial issue #03 nor #05 can leave HOLD; editorial issues also require authentic footer/recipient/founder acceptance.

## Source links

- WordPress native mail and excerpts: https://wordpress.com/support/newsletter/email-appearance/ and https://wordpress.com/support/newsletter-settings/
- Disabled newsletter sending default: https://wordpress.com/support/newsletter/disable-newsletter-emails/
- FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Zen12 product: https://zen12.com/about and https://zen12.com/getstarted
- Hypnosis Live Total Focus: https://hypnosislive.com/mental-skills/total-focus and https://hypnosislive.com/faq
- Affiliate public recruiting: https://affiliates.inspire3.com/

**No email sent or scheduled, no test-email sent, no subscriber data changed, no live site/post/settings changed, no affiliate link made live.** Founder must explicitly approve each final issue, audience, date and send before action. Homepage flagship remains the top site priority.
