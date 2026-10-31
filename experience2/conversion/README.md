# Conversion workstream — DRAFT / HOLD
Base: the existing unified homepage review (PR #342). No production deployment, WordPress edits, purchase links, or changes to frozen PR #49.

## Focus CTA
`focus-popup.html` is a Gutenberg-oriented editorial block prototype; it uses the **existing** WordPress Jetpack subscriptions block syntax. No new provider, keys, popup plugin, network calls or custom email endpoint. It fails closed: if Jetpack does not render a native form, `focus-popup.js` leaves the accessible /focus/ link visible. The modal requires an explicit visitor click (never automatic or exit-intent), returns focus when dismissed, respects Escape via native dialog, and leaves all existing content and signup untouched. Check real Jetpack rendering, delivery to confirmed subscribers, privacy copy and duplicate form behavior in isolated WordPress staging before inserting into the homepage. **The popup is not live and is not proven to deliver the book automatically.** Confirm the actual Fieldbook delivery flow before claiming it does.

## Warm-up
`mind-tools-warmup.html` is a standalone editorial draft for a future /mind/tools/ route. It is an independent reading guide, not a product testimonial. It includes no unapproved Inspire3 outbound tracking or efficacy/wealth claims. No affiliate link until acceptance, current terms, independent review and nearby FTC disclosure are verified. Avoid adding /mind/ to navigation without review.

## Editorial and release gates
- Founder visual/editorial review; no frozen PR #49 modification.
- Native WordPress form rendered, keyboard and screen-reader tested; popup focus return, no-JS fallback, responsive reflow at 320–1920 and 200% zoom.
- Verify Jetpack double opt-in, privacy, rate limits, Fieldbook fulfillment and abuse protection in safe test account; do not copy subscriber data to isolated staging.
- Run axe WCAG 2.2 AA and Lighthouse; don't call unmeasured results passed.
- Preserve 72 Margins entries, published /focus/ page and existing Jetpack signup; historical archive remains primary.
- No merge, deployment, production CMS settings or subscription service additions without release authorization.

## Oct 31 exact-source QA refinement

- Confirmed published `/focus/` (WordPress page 1579) has the **existing** `wp:jetpack/subscriptions` form, a direct 52-page PDF download path, newsletter consent and a welcome-email confirmation message. No subscriber account was used, no email delivery was verified.
- Added consent adjacent to popup form: joining The Dispatch, confirmation requirement, unsubscribe and privacy link. Preserved `/focus/` if native Jetpack rendering or JavaScript is unavailable.
- Prevent duplicate shortcode invocations from producing duplicate dialog IDs. Checked PHP lint and a local API-double contract (not real WordPress).
- Corrected **Simons & Rensink (2005)** DOI to `10.1016/j.tics.2004.11.006`, grounded in PubMed PMID 15639436. Replaced nested `<main>` with an `<article>` to avoid duplicate main landmarks inside WordPress page templates.
- Real isolated Chromium with the **exact GitHub popup HTML/CSS/JS blob IDs** passed 7-width keyboard modal, Escape, focus return, overlay fit and three fallback cases; separate simulated 200%-CSS-zoom reflow passed. Browser form is a synthetic stand-in; it does **not** validate WordPress Gutenberg block rendering, Jetpack subscription confirmation, actual PDF delivery, Safari, axe or CWV.
- Coordinated with separate independent QA PR #355 and Mind/Perception editorial Issue #171; do not merge this stacked PR standalone. Release HOLD.

## WordPress.com 2026 plan compatibility and CSS timing

Official WordPress.com documentation (last reviewed October 22, 2026) states Personal supports plugin ZIP uploads, while hosted staging remains a Business-plan feature: `https://wordpress.com/support/plugins/install-a-plugin/`. **This does not approve production installation.** The shortcode plugin can be packaged for later approval without a new subscription.

WordPress Core runs `wp_enqueue_scripts` in `wp_head` before page content: `https://developer.wordpress.org/reference/hooks/wp_enqueue_scripts/`. Previous shortcode-only CSS could enqueue after the head and render unstyled; revision 0.1.1 adds a shortcode-aware early enqueue when `[fv_focus_popup]` appears in the queried singular post, with a fallback enqueue on shortcode render. **Do not put this shortcode only in a template part**, because early CSS detection isn't assured there. PHP lint and isolated WordPress API-double hook tests pass, not genuine host rendering.
