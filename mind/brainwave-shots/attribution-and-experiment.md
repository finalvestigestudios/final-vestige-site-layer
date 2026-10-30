# Focus Shot: privacy-safe attribution and editorial experiment plan
**Unpublished proposal — 30 October 2026 — no tracking installed**

## Measurement definitions
- Guide page view: use only the site's already-approved aggregate reporting, if available, segmented by referring source *group* (TikTok, search, direct, Dispatch) and proposed variant. Never send email address, IP, full referrer URL or unique device identifier to a new service.
- Free Focus Fieldbook CTA: count as a free editorial resource click, never an affiliate click or purchase.
- Focus Shot merchant outbound CTA: **disabled until account approval and merchant-issued link**. When active, collect only an aggregate outbound count by guide ID, variant and on-page position if permitted by the site privacy policy. The destination must remain a visible direct merchant link; no redirect cloaking or tracking pixel.
- Partner purchase or commission: recognize **only merchant-confirmed aggregate report**, once an actual FV account exists and the terms permit reporting. No purchase data can be inferred from impressions or outbound clicks.

## A/B design, not an uplift claim
A: complete article, attention audit and offer evaluation without video.
B: identical article, audit, CTA and offer disclosure, plus an optional original 35-second explainer with click-to-play, poster, captions, transcript and no sound autoplay.
Outcome: eligible confirmed outbound clicks divided by valid guide page views after both variants are consistently assigned. Secondary: free Fieldbook clicks and landing-page load performance; conversion only on partner-provided completed purchases.
Guardrails: 360/390/768/1440/1920, keyboard, source citations, no-JS content, reduced-motion, no CLS from media, acceptable Core Web Vitals, no intrusive popups, and no privacy-extraneous cookies.
Do not do statistical comparisons or claim superior conversion when traffic is too small. Existing Dispatch subscriber count is not sufficient by itself for an email A/B test.

## Allowed links and safe deployment
Unpaid factual source link to official merchant /focus-shot is a citation and must not be presented as an affiliate CTA. When authorized, the distinct buying CTA can use an actual partner-provided URL with clear nearby commission disclosure, rel=sponsored if appropriate and transparent destination. Do not append affiliate identifiers to readers' email addresses or transmit identifying source data. Keep no-JS routes active and avoid paid SaaS.
Landing page should be independently useful before any merchant link. Live WordPress content, subscription list and tracking settings must not change in the draft.

## Release gates
[ ] Partner approval and exact Focus Shot tracking URL.
[ ] Confirmation that email/social channels are allowed by actual affiliate agreement.
[ ] Merchant checkout/safety/refund and price refreshed at release.
[ ] Clear near-link disclosure and product-specific substantiation review.
[ ] Independent site QD and founder release approval.
[ ] WCAG/browser tests and video copyright/captions checks.
[ ] Merchant data matched to current product.
[ ] No merged PR #49, #172, #180, #188 or live newsletter writes resulting from this sprint.
