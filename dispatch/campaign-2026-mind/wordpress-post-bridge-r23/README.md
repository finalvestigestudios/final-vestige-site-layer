# R23 — WordPress Gutenberg post bridge (SOURCE ONLY, DRAFT)

**Master** [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) · **Companion** [Mind & Affiliate #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) · **Original campaign** [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) · **R22 stack parent** [draft PR #318](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/318) at `7d19991eb4310ecbe44ab7a04bd8faf503df24fd`. The homepage flagship and frozen PR #49 are entirely out of scope.

## Why this is a different deliverable

The original six campaign manuscripts and email HTML/plaintext previews were already prepared. This bridge translates their **unchanged, exact GitHub PR #318 source** into six inspectable **WordPress Gutenberg post-body candidates**. It does **not** create a WordPress post or certify a WordPress email, which is the key missing last mile. It preserves the original post-title/subject text, records proposed preheader copy as **not natively verified**, and makes the two non-live product-guide CTA placeholders visibly **inactive text**, not clickable links. Existing source, HTML email previews, and 4 editorial / 2 commercial allocation remain unchanged.

**Why post content rather than page content?** WordPress [documents that only posts send newsletter notifications](https://wordpress.com/support/newsletter/send-newsletter-emails/). Its current [Newsletter Settings](https://wordpress.com/support/newsletter-settings/) say the live setting `email_content_format=excerpt` uses the explicit post excerpt or the first 55 words by default; it will not automatically deliver these full-body candidates. The WordPress [Preview email](https://wordpress.com/support/newsletter/email-appearance/) button requires the per-post “Send this post to subscribers” toggle on in the editor. That preview step remains **unauthorized and not performed** because an accidental Publish/Schedule could then send. No global setting, per-post toggle, or WordPress state was touched.

## What is included

- `build_native_candidates.cjs`: dependency-free, offline, fail-closed Node generator; reads the six original Markdown issues and manifest only; no network/CMS/analytics/email functionality; rejects source/subject changes, missing legal holds, live earning URLs, and missing near-offer commercial disclosures.
- `proofs/issue-01..06.blocks.html`: Gutenberg paragraph/list source proposals preserving the original useful content and citation links, with a **visible DO NOT PUBLISH OR EMAIL** banner. The long proposed merchant-guide tokens become **GUIDE NOT LIVE — NO LINK** (not a real URL).
- `proofs/RELEASE_COMPATIBILITY.json`: no-send ledger with post, preheader, format, merchant, legal, actual-email and cohort evidence all deliberately **false / not established**.
- `proofs/OFFLINE_POST_REVIEW.html`: accessible six-edition browser review, **not** a genuine WordPress sanitization test, inbox preview, or native Jetpack email.
- `tests/test_gutenberg.cjs`: reproducible source, output and adversarial guard suite.

Use `node dispatch/campaign-2026-mind/wordpress-post-bridge-r23/build_native_candidates.cjs --verify` and `node dispatch/campaign-2026-mind/wordpress-post-bridge-r23/tests/test_gutenberg.cjs` on a complete checkout. Do not use this repo package as an importer or to publish anything.

## Exact current operational restrictions (authenticated read, 2026-10-31 16:30 UTC)

WordPress newsletter enabled, automatic new-post emails OFF, `email_content_format=excerpt`, sender “Final Vestige” and no-reply, 52-page Fieldbook configured in welcome; actual welcome receipt unverified; **0 recent sends**; subscriber counters **total 2 / confirmed 2 / unconfirmed 2 / suppressed 0**. WordPress may exclude pending confirmations from its total, so counters need not be mathematically inconsistent, but reachable opt-in audience is not verified. Published `/dispatch/` and `/focus/` retain native Jetpack Subscribe blocks and published Editorial Standards require source fidelity, uncertainty labels, and commercial disclosure. The live site was **read only**.

## Source of truth and hard holds

1. **Platform mode decision:** Founder must separately authorize full text vs intentionally composed excerpts. An HTML post-body candidate does not change the excerpt setting. Verify exact WordPress post-title subject and whether a preheader is separately controllable; never claim native preheader delivery from manifest metadata.
2. **Native rendering:** A separately approved **unsent draft-only** session and safe per-post preview workflow are required before any native WordPress rendering evidence. No post/editor action was undertaken here; no test email authorized.
3. **Real received MIME, welcome and signup:** Require founder-authorized received-email evidence and opt-in audit; compare original HTML/plaintext to received parts, unsubscribe, Final Vestige valid physical postal address, subject, excerpts, images, links. An Automattic/merchant address cannot substitute for the advertiser's mailing address. The [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) applies where the primary purpose is commercial.
4. **Products:** The exact [Zen12 About](https://zen12.com/about)/[Zen12 checkout](https://zen12.com/getstarted) and [Total Focus](https://hypnosislive.com/mental-skills/total-focus) public pages describe 12 levels / 48 MP3s and a 33-min / 47-MB audio respectively. These are **seller-reported specifications**, not independently proven efficacy. Sale prices and refund terms can be volatile and are intentionally not quoted or encoded. Full account-specific Inspire3 acceptance, email rights, exact earning-link format, creative permissions and two LIVE reviewed guide URLs remain **NOT VERIFIED**. Public partner signup is NOT account approval.
5. **Delivery consent:** Release needs per-issue founder final content, recipient and date authorization. No A/B significance or fake conversion data on a list this small. No analytics collection, subscriber export, or tracking links.

**ALL SIX HOLD_UNSENT. Issues 03 and 05 also HOLD_MERCHANT.** No CMS writes, no sends/test sends, no setting updates, no subscriber contact or imports, no affiliate activation, no paid tools, no production release and no homepage modifications.
