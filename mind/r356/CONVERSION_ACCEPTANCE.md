# R356 — Revenue-first Mind and Affiliate Acceptance

**2026-11-13 · STATUS DRAFT / UNPUBLISHED / HARD HOLD · Issue #171 + #820**

## Offer selection: permission before pixels

**Lead high-intent audience hypothesis:** A reader arriving from a documented social clip about attentional blink or concentration who is actively researching a practical audio routine. **Primary hypothetical merchant product:** Zen12 Premium. Official page describes 12 levels and 48 MP3 tracks in multiple styles. Exact checkout pricing, actual refund conditions, and a Final Vestige publisher-specific link/authorization must be privately authenticated; public program percentages are not our terms. Until then the CTA is **disabled, not linked, not event-bearing**.

**Fallback:** Only consider an FV-owned Payhip digital product after Commerce validates exact rights-cleared SKU, active price, checkout/delivery, refund rules and transaction custody. Public search and targeted partner-email review did not establish a verified paid Mind SKU. Do not swap in an arbitrary unverified product to force a purchase funnel.

**Actual sales this sprint:** none verified. **Qualified human sessions:** unavailable. **Realized net revenue per 1000 qualified human sessions:** NOT COMPUTABLE.

## Offer → funnel step → blocker → proposed change / experiment → acceptance evidence → owner

| Priority | Offer → funnel | Blocker | Change or experiment | Pass evidence | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → accepted paid commission | FV approval/channel/link/terms unavailable | Private permission audit, sanitized attestation | Exact account + relevant rights + issued URL, no secrets in issue | Founder / Commerce |
| P0 | FV-owned Mind SKU → paid order | Rights, delivery, checkout, refunds unverified | Verify existing Payhip SKU under owner account | Public exact product checkout + owner rights + test delivery | Commerce |
| P0 | Any paid offer → net revenue | Merchant-confirmed orders and settlement data absent | Reconcile order IDs in private merchant custody, aggregate only publicly | Paid order, settlement, fees, refunds, denominator | Commerce / Claude |
| P1 | Grok asset → Mind article | Exact asset IDs, URLs, posted CTA unknown | Praxxis/Grok read-only TASK-008 crosswalk | Verified three real social IDs and final allowed landing route | Praxxis / Grok |
| P1 | Mind article → free Fieldbook | Consent attribution incomplete | Reuse existing Jetpack/Focus; no duplicate forms | Provider-confirmed lead with compliant attribution | Claude / Dispatch |
| P2 | Zen12 A/B → buyer | Partner & film staging unavailable | A text vs B identical text plus original optional 42s film; no autoplay | Randomized eligible humans, verified order economics, accessible real browser | Site QA / Claude |

## Controlled hypothesis and honest KPI

**Hypothesis, not a claim:** Among comparable buyer-intent visitors, an optional original explanatory 42-second film might increase confirmed paid orders relative to an otherwise identical text-only, source-grounded guide. Because visitors may abandon slow pages, measure image/media bytes, LCP, CLS, video opt-in, keyboard/no-JS experience and bounce as guardrails. Film never autoplays.

Hold audience, offer, price snapshot, disclosure wording, source notes, navigation, mobile CTAs and traffic composition constant. Randomize server-side or via an already-approved first-party mechanism only after release approval; do not add a new analytics stack or consentless fingerprinting. Draft B currently has poster, captions and transcript **without encoded/hosted playable media**; not trial-ready.

**Events:** (1) qualified human social asset session with `utm_source`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<real-asset-id>`; (2) landing view; (3) relevant CTA click; (4) optional provider-confirmed Focus signup; (5) confirmed paid merchant order or authenticated affiliate commission; (6) settlement, refunds, fees. An `affiliate_click` event is *not* a paid order. Treat unattributed/unknown separately, not as zero.

**Primary KPI:** realized net USD / qualified-human sessions × 1000 in 7- and 30-day cohorts, using authenticated net (settled receipt or commission minus refunds, platform and processing fees and reversal adjustments). Denominator requires consent-respecting first-party human-quality criteria; exclude provable bot traffic and internal QA without tracking personal identity. Report valid denominators, cohort assignment and tiny-sample warnings. Paid conversion = confirmed paid orders / qualified-human sessions; leads → paid customer = matched verified customers / confirmed consented leads if lawful matching exists. Otherwise NOT COMPUTABLE.

**Privacy:** no fingerprint IDs, user-level advertising profiles, IP addresses, email/phone, hidden cross-site cookies, merchant credentials, arbitrary campaign params or row-level customer data in GitHub. Do not activate any new script. No link cloaking. Approved affiliate link, when acquired, should be transparent and disclosed immediately before and after as required by QA.

## Three candidate creator paths — never invent IDs

| Creator source & hook to align with Grok | Actual media ID / route | Source article | Lead or optional commercial step |
|---|---|---|---|
| Attentional blink: “You saw the first target. Did you see the second?” | UNKNOWN / UNKNOWN | This R356 research draft, requires publication approval | Live /focus/ → optional authorized Zen12 guide |
| Change blindness: “The stranger behind the door changed.” | UNKNOWN / UNKNOWN | https://finalvestige.com/2026/11/02/change-blindness/ | Live /focus/ → optional authorized buyer guide |
| Hypnosis history: “Franklin tested what people believed they felt.” | UNKNOWN / UNKNOWN | https://finalvestige.com/2026/11/02/mesmerism/ + Puységur archive | Live /focus/ → separate disclosed Tools review |

Praxxis and Grok retain the existing TASK-008 queue and will resolve actual videos/hooks/asset IDs. Mind editorial does **not** produce or post social content, edit newsletters, or replace the welcome message.

## QA and release

Static HTML draft checks are defined in `verify_r356.cjs`; native Node, CI, 360/390/768/1440/1920 real browser, WCAG 2.2 AA, mobile checkout, WordPress sanitizer, video encoding, merchant settlement and actual revenue **are not represented as run or passed** unless backed by execution evidence.

No edits to PR #49, PR #172, Issue #150, Jetpack, live CMS/menu, Dispatch newsletter, Grok production queue or existing measurement code. No spend, deployment, merge, sending or affiliate activation. Signoff: Founder (release and commerce), Site QA (a11y/security/claims), Claude (engineering), Dispatch (existing email), Praxxis/Grok (verified assets).
