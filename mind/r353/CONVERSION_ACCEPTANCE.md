# R353 — Conversion-first acceptance, creator-topic fit and ethical release dossier
**13 November 2026 PT | Draft only | Owner: Mind & Perception commercial/editorial lane**
**STATUS: HARD HOLD, not live, not approved, not paid; source-controlled proposed implementation, no CMS or analytic deployment**

## Decision before production
**Primary audience:** viewers or search visitors specifically interested in a manageable twelve-minute focus/meditation audio routine, who can distinguish a practical product format from proof of its benefits.
**Primary hypothesized offer:** Zen12 **Premium**, because the exact official page describes the twelve-level/48-MP3 complete course and a single purchase-oriented comparison can be made without inventing efficacy. Public display $87.99 was observed on 2026-11-13 but final checkout/taxes/refund operations are not verified.
**Commercial eligibility:** neither Final Vestige-specific Inspire3 account acceptance, approved domains/placement channels, the earning link, payout ledger nor creative permissions were authenticated. Public registration at https://affiliates.inspire3.com/ is NOT acceptance. Targeted Gmail search found ordinary Inspire3 marketing newsletters but no authenticated partner acceptance in the searched results; absence of an email does not prove rejection.
**Alternative owned offer:** existing Focus Fieldbook at https://finalvestige.com/focus/ is FREE, and Payhip catalog ownership/deliverability of any paid FV Mind SKU remains unverified. Do not invent a payable owned fallback or divert to an unowned Payhip listing.
**Immediate viable outcome:** protect direct-audience trust and an actual existing Focus opt-in route while the merchant eligibility issue is resolved. No sale or lead is claimed for this run.

## Exact creator topic → research route → capture → optional commerce fit matrix
| Existing thematic creative candidate (Grok owns assets) | SOURCE-GROUNDED currently live destination | Qualified visitor intent | First-party next step | Optional product only if approved | Asset evidence |
|---|---|---|---|---|---|
| Change blindness / door-swap or flicker | https://finalvestige.com/2026/11/02/change-blindness/ | “Why did I miss the obvious change?” | Free Focus Fieldbook after reader understands attention; never a forced modal | Zen12 only if they separately seek a twelve-minute audio structure | Exact genuine Grok posted video ID, date, mobile link **NOT VERIFIED** |
| Animal magnetism / Franklin / Puységur | https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ and https://finalvestige.com/2026/11/02/mesmerism/ | “What is the evidence for hypnosis history?” | Existing Dispatch/Focus, entirely optional | Hypnosis Live specific audio only after official exact-product review and permissions | Exact authentic media ID **NOT VERIFIED** |
| Attentional blink / selective attention | https://finalvestige.com/archive/ (specific future approved article required) | “Can my attention miss a second target?” | Existing Focus, no added list | Zen12 only after independent product-claim and publisher authorization review | No fabricated blog article route or asset_id; **NOT VERIFIED** |

Do not put an actual YouTube/TikTok video ID, immutable `asset_id`, campaign name or UTM on this matrix until Praxxis validates a published original asset against Grok's existing TASK-008 handoff. The prior unrelated Roman dodecahedron and Etruscan alphabet Shorts are NOT mind/perception campaign matches. Do not ask Grok to publish or change their queue.

## One landing, one measurable buyer CTA, no commissioned click yet
- Proposed pilot URL after separate release approval: `/mind/zen12-evidence-guide/`. This URL is hypothetical, NOT live.
- **Variant A:** `ZEN12_A_TEXT_GUIDE.html` — full source guide with all six buyer-information sections.
- **Variant B:** `ZEN12_B_OPTIONAL_FILM_GUIDE.html` — identical six-section substantive buyer copy, original SVG poster, complete 42-second script and six-cue VTT. Current version **storyboard only, not a playable hosted video**; no autoplay and zero forced media load. Real playable film staging and WebVTT synchronization still required.
- Actual buyer control remains **disabled**, after an adjacent understandable prospective affiliate disclosure and explicit no-issued-link explanation. No seller buttons, checkout redirects, seller gift/newsletter anchors, new newsletter form, tracking script, pixel or iframe.
- No traffic/purchase A/B is active. The hypotheses are: (H1) optional short improves comprehension and qualified merchant-click intent; (H0) text alone performs as well or better. Random assignment only after authorization, accessibility, staging QA and first-party instrumentation approval. Report genuine attribution, 7/30-day cohorts and tiny-sample uncertainty; do not imply causation from a handful of purchases.
- Keep a separate, completely optional way to visit `/focus/` without commerce or requiring signup.

## Seller fact / pricing / return / objection checklist
- Zen12 actual page: https://zen12.com/ (checked 13 Nov) describes Premium twelve levels, 48 MP3s, displayed $87.99 and promotional one-year refund promise. This **does not** verify final checkout, charge receipt, taxes, refund eligibility or fulfillment.
- Introductory and advanced six-level packages should not be conflated with the Premium whole sequence.
- https://zen12.com/gift introduces a separate merchant newsletter; do not silently enroll a Final Vestige subscriber or treat merchant consent as Dispatch consent.
- https://hypnosislive.com/ and https://brainwaveshots.com/ are other seller catalogs; neither is the same exact offer and neither scientific literature nor merchant claims substitute for a specific product audit.
- Buyer objections explicitly answered: available time, free no-audio alternative, uncertain scientific efficacy, medical use (not claimed), refund conditions and additional seller marketing.
- No fabricated personal reviews, proof-of-benefit, scarcity, commissions or earnings. Source facts are documented in `CLAIMS_AND_RELEASE_GATES.json` (30 claims, 18 URLs, 28 HOLD release gates).

## First-party attribution — interface specification only, no new script
Claude owns the current existing site analytics. Reuse those events, not a second script or third-party SaaS. Where consent and policy allow, events are:
1. `qualified_human_landing`: timestamp bucket UTC, immutable **verified** Grok `asset_id`, `utm_campaign`, canonical approved destination, anonymous cohort key, bot-filter classification; never an IP/email/name.
2. `guide_variant_exposed`: variant A/B and experiment version only; exclude bots and repeat exposures from first-touch allocation.
3. `focus_cta_click`: site-to-existing `/focus/` navigation, **not** confirmed lead.
4. `focus_confirmed_subscriber`: ONLY if existing Jetpack/Dispatch provider explicitly confirms permission and can attribute a consent-respecting campaign. A PDF download or unconfirmed email request is NOT an accepted subscription.
5. `affiliate_click`: ONLY after approved issued link and founder release, with known click ID under approved partner rules. Event not a sale.
6. `merchant_paid_order` / `affiliate_commission_confirmed`: ONLY order/partner reports with order ID safely reconciled privately. These must never be inferred from a click or public affiliate rates.
7. `settlement_adjustment`: refunds, returns, chargebacks, commissions, fees, tax liability where applicable and timing of actual settled net revenue.

Analytics payload denylist: email, phone, postal address, name, IP, device fingerprint, health description, hypnosis susceptibility, raw query, payment credential, `gclid` if not specifically consented/permitted. Event values should be coarse, minimized and governed by retention policy. Do not append identity tokens or raw buyer answers to UTM parameters.

**Numerator:** verified realized net business revenue from reconciled paid orders/settled commissions within a cohort, after merchant refunds, chargebacks and applicable fees (and subject to explicit accounting treatment for taxes). **Denominator:** distinct consent-respecting **qualified human** landing sessions within the same cohort and source parameters. Never substitute views, raw pageviews, reported visitors or outbound clicks. 
**KPI:** `net_realized_revenue_per_1000 = 1000 * verified_net_revenue / qualified_human_sessions`. If numerator evidence or denominator is missing or zero, return **NOT COMPUTABLE**, not zero. Also report paid conversion rate, confirmed orders, gross/net, and lead-to-customer rate only if all respective confirmed data exist. Roll by 7 and 30 completed days, with sample sizes and qualitative uncertainty.

## QA evidence gates & ownership
| Offer → step | Blocker | Change / experiment | Pass/fail evidence today | Owner |
|---|---|---|---|---|
| Zen12 → payable commission | FV partner and placement rights unverified | Authenticate account, channel rights and exact issued link privately | HOLD: public portal and generic promotional emails do not prove acceptance | Founder / Commerce |
| FV Mind owned product → paid order | No verified rights-cleared active Mind Payhip checkout | Audit exact owned SKU and purchase/delivery/refund privately | UNKNOWN: not declared saleable | Commerce |
| Grok Mind short → article | Matching exact published media IDs unresolved | Praxxis cross-check original URL, asset, publication and allowed mobile path | HOLD: no immutable topic-match proof | Praxxis / Grok |
| Article → existing Focus subscription | Provider-confirmed consent attribution unproven | Audit existing Jetpack confirmation + welcome message, no replacement | HOLD: page exists, confirmed lead not evidenced | Claude / Dispatch |
| Guide A/B → merchant action | Approval, playable film and staging QA missing | Independent source/keyboard/mobile/contrast/no-JS/performance QA | PARTIAL: static checks only; real browser not run | Site QA / Claude |
| Paid order → net revenue | No authenticated settlement/refund/fee report and qualified sessions | Reconcile approved 7/30-day accounting files, never from synthetic clicks | NOT COMPUTABLE; no false zero | Commerce / Claude |

## Safety and release checklist
- [x] Source-controlled separate Mind-only artifacts
- [x] Direct links to actually live primary archives and existing Focus
- [x] Seller claims qualified; health/mental/financial efficacy not endorsed
- [x] Adjacent prospective disclosure and disabled, non-linking CTA
- [x] No extra form, no script, no external video or tracking request
- [ ] Real-browser mobile 360/390/768/1440/1920, tab order, contrast/AA and reduced-motion/no-JS
- [ ] WordPress sanitized Gutenberg block preview and no auto-embed
- [ ] Actual encoded original video, captions, transcript review and hosting performance
- [ ] Real partner and specific product/channel creative authorization, issued earning link
- [ ] Founder/QA publication consent, no PR #49 or #172 interference
- [ ] Revenue verification with merchant orders, fees, refunds and cohort denominator

**HARD HOLD.** All 28 release gates in the matrix stay closed. No live WordPress or navigation writes, Jetpack modifications, social posts, newsletter sends, duplicate analytics deployments, paid services, offer activation, merge or founder release presumed.

### Source register
- Canonical editorial mandate: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171
- Conversion program: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820
- Charter: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818
- FTC endorsements: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- FTC health claims: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- Inspire3 catalog and partner public login: https://inspire3.com/ ; https://affiliates.inspire3.com/
- Actual offer: https://zen12.com/ ; separate merchant consent: https://zen12.com/gift
- Lab proof: https://doi.org/10.1016/j.concog.2025.103948 ; https://pubmed.ncbi.nlm.nih.gov/12470132/ ; https://pubmed.ncbi.nlm.nih.gov/39032268/
- Live archives: https://finalvestige.com/blog/ ; https://finalvestige.com/2026/11/02/change-blindness/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ ; https://finalvestige.com/focus/
