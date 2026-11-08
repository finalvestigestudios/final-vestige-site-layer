# Dispatch R43 — Jetpack 350-character source-of-truth correction

**Date inspected:** November 1, 2026 (official documentation updated October 28; WordPress excerpt documentation reviewed October 6).  
**Scope:** source-only, UNSENT editorial quality correction, stacked on [draft PR #454](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/454). Master [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); companion [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171); original campaign [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175); independent release gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201).

## Material correction to R39: generic post excerpts ≠ Jetpack email excerpts

The earlier R39 offline docket modeled **55 words** of an article as a default excerpt. That count is grounded in [WordPress.com's generic excerpts help](https://wordpress.com/support/excerpts/), reviewed October 6, 2026. But [Jetpack's newsletter-specific customization help](https://jetpack.com/support/newsletter/customize-the-newsletter-experience/), updated October 28, 2026, says that when **no custom post excerpt exists**, the email's excerpt uses **the first 350 characters of the post**. These are different documented surfaces. The R39 text expressly characterized 55 words as illustrative, but **using its output to predict Jetpack's inbox presentation would select the wrong provider-specific rule**.

This dossier does not silently edit or delete R39, rewrite the canonical newsletters or falsely claim that the first 350 characters of a Markdown source are exactly what the subscriber sees. WordPress's block handling, featured image, native heading, post date, custom excerpt, possible More block, and client truncation remain unobserved. We retain BOTH estimates for comparison and explicitly label them nonauthoritative models. If documentation changes or a received email contradicts the documentation, live evidence must take precedence.

## Authenticated production truth, read-only 2026-11-01 13:37 UTC

Jetpack Newsletter: enabled; `email_new_posts_by_default=false`; `email_content_format=excerpt`; featured image ON; post date ON; sender display 'Final Vestige'; reply-to `no-reply`; the complete 52-page Seven Day Focus Fieldbook welcome text remains configured. `recent_sends=[]` means **no reported recent sends** only, not proof of zero lifetime sending. WordPress returned `total=2 / confirmed=2 / unconfirmed=2`: counters are **not additive** and cannot establish a deduplicated, opted-in reachable list. No individual subscriber information was retrieved or stored. No final welcome-email receipt was verified.

The six optional custom excerpts in `delivery/wordpress_excerpt_copy.json` are **source-controlled proposals only**. Their product-related editions mention possible affiliate earnings within the first 350 displayed characters, but none is installed in an approved WordPress post or verified in an inbox. The proposed subject can become the native WP post title; a separately programmable native preheader is **not verified**.

## The actionable delivery pathway

The native WordPress.com/Jetpack preview is a distinct artifact from (1) Markdown authorship, (2) static standalone HTML, (3) an illustrative excerpt. Jetpack's [October 28 Newsletter documentation](https://jetpack.com/support/newsletter/) describes the unpublished-post Email preview and a separate **Send test email** control. There is **NO** founder authorization to create a WordPress post, toggle per-post send settings, send a test message, or email anyone. A preview or received test must only be performed after separate explicit permission for the specific unpublished post and test procedure; final campaign approval to send remains an additional, independent requirement.

With proper authorization later: inspect a safely unpublished native post, verify title / proposed excerpt / featured image / email preview across desktop and mobile, compare the preview with a specifically authorized received test file, check business mailing address, visible opt-out link and unsubscribe function, then separately obtain final send approval. Merely seeing the phrase "Unsubscribe anytime" on `/dispatch/` or a WordPress.com address in a subscription confirmation does not prove the required Final Vestige commercial mailing address or working unsubscribe in an actual campaign email.

## Merchant and FTC truth not altered by the 350-character finding

- Issues **01, 02, 04 and 06** remain historical/editorial. Issues **03 and 05** remain commercial-review-pending; neither approved buyer guide is published. Public product pages do not prove affiliate acceptance or specific permission for email marketing, affiliate URL format, product-effect outcomes, current checkout price, refund applicability or media licensing.
- Commercial disclosure: the optional excerpt tells readers a qualified guide may earn Final Vestige a commission; the *actual* email and published content must carry appropriately close disclosure if a live recommendation qualifies.
- Issue 03 canonical copy still contains direct merchant citations that could circumvent the intended buyer-guide journey. An optional seller-link-free correction exists in draft PR #416, **not approved for substitution**.
- FTC [CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires valid business postal information and a functioning opt-out for commercial messages, plus truthful sender/subject. Safest release QA checks actual delivered footer and opt-out in **all six**; editorial labels alone cannot establish exemptions.
- These are **compliance checks, not a declaration of legal compliance**; the site's own [Editorial Standards](https://finalvestige.com/editorial-standards/) require distinguishing records, inference, and uncertainty.

## Reproduction and decision evidence

Run `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v` at **the exact PR head** and `python dispatch/campaign-2026-mind/r43-jetpack-excerpt-contract/excerpt_contract.py` to produce the privacy-safe, six-edition dual-model report. The generated reviewer board is a **static offline illustration**; it is not Jetpack-generated HTML. The tests fail closed on changed approval states, missing legal sentinels, seller-link drift, missing commercial excerpt disclosures and misleading footer/approval claims. No fake open/click/ROI metrics or subscriber identities are present.

**Hard stop:** all six HOLD_UNSENT, #03/#05 additionally HOLD_MERCHANT. No WordPress write, post creation, email/test-email, subscriber contact/import, new platform, marketing expense, affiliate activation or homepage PR #49 change. Explicit final founder approval is still required.
