# The Dispatch — Mind & Perception pilot (UNSENT)

Owner: **FV Dispatch Campaign Studio**, Issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Companion Mind & Affiliate issue [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171).

## Verified current configuration, October 30, 2026

WordPress.com site `finalvestige.com` has Jetpack Newsletter **enabled** with `site_can_send: true` and `email_new_posts_by_default: false`; welcome copy already points to the **52-page Focus Fieldbook**. The site reports **no recent newsletter sends**. Subscriber diagnostics were internally inconsistent: `total: 2`, `confirmed: 2`, `unconfirmed: 2`. Do not invent a clean count or send before reconciling.

**This repository package is NOT an email blast** and requires no new paid platform. Everything remains draft. Publishing a WordPress post as a newsletter is a distinct, explicit user-approved action.

## Offer and evidence alignment

The first six editions preserve the core promise of historical investigations and evidence. **Four are purely editorial, two are product-guide opportunities.** Published and verified internal destinations: /focus/, /free-resources/puysegurs-animal-magnetism-files/, /2026/08/20/the-hatch-opened-inward-apollo-1/. The future Zen12 and Hypnosis Live warm-up guides do not have live published URLs and are deliberately replaced by **hard-stop placeholder tokens**.

Source for vendor positioning: https://inspire3.com/. Vendor catalog descriptions and commercial guarantees are NOT independent proof. Actual sales-page claims, up-to-date price, refund/terms, product format, user benefits and approved affiliate tracking must be confirmed product-by-product before the relevant email is eligible to send. Review approved product swipe materials for audience language/objections only; do not lift the merchant's ad copy or misleading testimonials.

Original copy structure: *specific curiosity → a record or practical question → a useful explanation/exercise → honest limitations → one contextually relevant CTA → disclosure if commercial*. No invented claims of hour-equivalence, verified clinical outcomes, guaranteed income, fake scarcity, false user anecdotes or buyer pressure. Do not disguise an affiliate promo as an independent editorial finding.

## Delivery and legal gates

Every issue contains hard-stop placeholders `[[VALID_POSTAL_ADDRESS_REQUIRED]]` and `[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]` until a QA reviewer verifies exactly what the WordPress-generated email footer will render and that it meets the requirements. The sender's actual business postal address is not stored here. Do not place a made-up address in any email.

**No sends, scheduling, publishing, importing subscribers, changing Jetpack settings or purchasing a mail platform** without the user's explicit approval. Ad-feature issues must clearly identify the promotional relationship and disclose near the specific recommendation; the pre-sell page must repeat disclosure next to any actual earning link. Affiliate URL remains null in manifest until verified.

Important FTC reading: [CAN-SPAM compliance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).

## Release workflow

1. Copyedit, source-check and mobile/email preview each issue. Show complete creative to founder.
2. Coordinate with Mind Studio (Issue #171) on **approved, LIVE** Zen12 and Hypnosis Live warm-up destinations. Do not add nonexisting paths to send-ready mail.
3. Check current subscriber/consent data, merchant email-promotion terms, footer/unsubscribe behavior, physical mailing address and deliverability.
4. Obtain explicit approval for which editions, exact schedule and target audience. WordPress's automatic emails for new posts remain off.
5. Only then create draft WordPress newsletter-post content using the approved process; sending is separately authorized.

Possible **measurement after actual sending**: unique delivered messages, CTA clicks (privacy-respecting), landing-page completion, outbound product clicks, affiliate purchases only when independently verified in the merchant's dashboard, unsubscribes and complaint rates. Never infer sales from clicks, or run a statistically presented A/B test on a list of two.

## Offline linter

`python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v` checks the campaign manifest and draft guards. A test run has to be actually executed on the exact PR head before QD sign-off; no claims merely because this file exists.
