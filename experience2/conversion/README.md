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
