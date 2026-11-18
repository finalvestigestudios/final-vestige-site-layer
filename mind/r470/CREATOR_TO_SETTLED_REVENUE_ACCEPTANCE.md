# R470 Conversion Acceptance: One Authenticated Offer Before More Landing Pages
*Final Vestige Studios · Mind & Perception · November 18, 2026 · DRAFT / HARD HOLD · no production release*

## Commercial decision (highest priority)

The current lead candidate remains **Zen12**, a format-relevant audio product for a reader already interested in trying structured twelve-minute listening. This is a **candidate**, not a sellable Final Vestige referral offer. Public pages at https://zen12.com/about and https://zen12.com/secret/ are materially different: an ordinary product explanation is not the same as the promotional package's actual checkout. Official https://inspire3.com/ identifies related products, not account-specific acceptance.

Connected mailbox check: on **2026-08-24**, an email titled "Your affiliate account is pending" stated that a Refersion application was under review and that a welcome email would follow *if* approved. Targeted follow-up searches through 2026-11-18 did not establish an accepted Final Vestige publisher record, permissible website/TikTok/YouTube/email channels, issued Zen12 earning URL, exact SKU or settlement terms. This is a bounded negative finding, not proof other merchant portals contain no approval.

**Hard rule:** No affiliate earning link, checkout redirect, incentive, coupon code, price or active sales button. Even a non-affiliate seller link on an editorial page should be weighed against the goal of verifying paid conversion. The prototype's inert button deliberately cannot record affiliate_click. No paid owned Mind product is presently authenticated; the existing 52-page Fieldbook at https://finalvestige.com/focus/ is free. Do not misclassify it as a paid owned product.

**Escalation:** Founder/Commerce must supply the merchant acceptance record, account identity, written allowed channels, merchant-generated SKU-specific URL, current checkout offer/returns, refunds, cookie and settlement terms, plus proof of approved reuse of any brand creative. If those remain absent, preserve the drafts and focus on the **existing free Fieldbook funnel** as an auditable lead-quality step, while Commerce investigates an actual rights-cleared FV paid SKU. No speculative sales claims.

## One high-intent audience

Someone arriving from an actual, topic-matched short video about a mind/perception effect who explicitly wants a short, repeatable listening routine—not a visitor drawn only by a curiosity illusion. The creator video must deliver an honest research question; the landing guide must answer an actual buyer's practical questions.

Our article must not say "if you missed the gorilla, you need Zen12." That is an invalid transfer of research. An ethically fitted adjacent question is: "How can I evaluate an audio routine before spending money?" The guide's free twelve-minute baseline is a useful, no-purchase next step.

## Creator-topic-to-destination matrix (not creator instructions)

| Candidate Grok video topic / intent | Currently live landing and real source | Free next step | Optional merchant-fit (HOLD) | Actual media ID |
| --- | --- | --- | --- | --- |
| Change blindness: people miss a visual switch | https://finalvestige.com/2026/11/02/change-blindness/ ; Rensink et al. 1997 / Simons & Levin 1998 as cited on the article | https://finalvestige.com/focus/ for a voluntary source/attention notebook | Zen12 only if viewer also expresses genuine interest in a listening habit; no false attention-repair link | UNKNOWN; Praxxis must check already-published assets |
| Franklin's 1784 commission and mesmerism | https://finalvestige.com/2026/11/02/mesmerism/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Existing free Fieldbook and independent source-audit method | Hypnosis Live may be relevant to a separate buyer guide, but historical mesmerism is not product proof | UNKNOWN; Praxxis must check already-published assets |
| Ideomotor pendulum / involuntary action under suggestion | R470 original manuscript **UNPUBLISHED**, so no live campaign destination; experimental https://pubmed.ncbi.nlm.nih.gov/35184700/ | Existing live Puységur/Focus pages only where hook is accurately matched | Future independent Zen12 format guide; no claim of therapeutic benefit | UNKNOWN; DO NOT invent or route traffic to unapproved draft |

Praxxis coordinates only provenance checks via existing Drive TASK-008. Grok independently owns media production and posting. No queue modifications, forced new creative or inferred links. **A matching published public video is currently unverified.**

## Funnel events, privacy and reconciliation

Preserve the site's already-existing engineering/Jetpack event implementation; this is a **contract for Claude**, not a new script or analytics deployment:

1. `campaign_landing`: permitted standard UTM parameters: `utm_source=tiktok|youtube|...`, `utm_medium=organic_social`, `utm_campaign=mind_guide_2026_11`, `utm_content=<verified-public-asset-id>`. Never substitute an invented ID. Record path, campaign, coarse date and consent status where available. No email, IP, device fingerprint or cross-site profile.
2. `resource_cta_click`: context-specific article → existing /focus/ action. A click is not a lead.
3. `confirmed_lead`: count only confirmed signups if Jetpack confirmation events can be reliably read and deduplicated. Never send a synthetic form submission to production without permission. Delivery of the existing welcome is a separate check.
4. `affiliate_click`: only after an authorized earning link exists; same origin event, no link cloaking or new duplicate script; record product/SKU, campaign, non-identifying cohort, and event count.
5. `verified_affiliate_conversion`: merchant-export or authenticated portal record with timestamp, merchant transaction reference, validated product, commission amount, settled/reversed flag. Do not infer from click.
6. `verified_paid_order`: approved FV-owned product processor settled order and fulfillment evidence, with refunds and fees. Do not infer from checkout start or an invitation to purchase.

**Qualified-human session** must be a defined, defensible, consent-aware unit, filtered for bots, repeats and internally generated tests by Claude's existing analytics. Missing bot-quality or source evidence means label denominator UNKNOWN, not a false zero or a fabricated conversion rate.

`realized_net = settled_paid_order_receipts + settled_affiliate_commissions - payment_processing_fees - refunds - chargebacks - attributable_direct_costs`. Keep currency and reporting period consistent; do not double-count gross order value and affiliate commission for the same external order. `net_rev_per_1000 = 1000 * realized_net / qualified_human_sessions` only if both inputs verified and denominator > 0. Otherwise write **NOT COMPUTABLE**. Report 7- and 30-day cohorts; small n warrants wide uncertainty and no winner declaration.

## Controlled test protocol: text vs original optional film

**Hypothesis only:** A buyer guide that adds an optional, original ~42-second explanatory film could help users understand evidence/claims compared with identical text-only guide, without damaging mobile speed or reducing trust. **No conversion uplift is assumed.**

- Arm A: `ZEN12_A_TEXT_ONLY_UNPUBLISHED.html`.
- Arm B: `ZEN12_B_OPTIONAL_FILM_UNPUBLISHED.html`; currently original inline poster + full six-cue transcript/42-second storyboard, no playable source. The prior R469 sprint generated a silent preview locally but it is not hosted/embedded; therefore film experience is **NOT RELEASE-READY**.
- Primary outcome once eligible: **independently reported settled merchant commissions per qualified human session**, with refund corrections; alternative when true FV-owned SKU exists: confirmed paid orders per qualified session. Do not call clicks the primary outcome.
- Secondary outcomes: manual evidence-guide comprehension, adjacent CTA click, confirmed Focus lead where observable, mobile accessibility, downstream verified merchant acceptance. Interpret them separately from paid orders.
- Allocation: same public audience intent and offer/price, ethically disclosed. Have Claude use a single approved first-party assignment method without external cookies or duplicate code. Avoid session re-randomization.
- Prerequisites: authorized Zen12 URL and terms, original encoded movie rights, accurate captions/transcript and poster, no autoplay, keyboard/reduced motion/no-JS fallback, 360/390/768/1440/1920 browser screenshots, measured payload/LCP, WP sanitizer, FTC and security review, QA and founder approval.
- Decision: pre-register observation window and sample-size logic with a qualified analyst. Small samples or missing orders -> **INCONCLUSIVE**, not a winning variant. Never turn on a public A/B before commercial release approval.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Priority | Offer and step | Blocker | Change/experiment | Current pass/fail evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| P0 | Zen12 / acceptance to paid commission | No named publisher authorization, SKU or earning link | Obtain approval and exact terms from merchant portal, review against checkout | **FAIL / HOLD**; Refersion Aug 24 pending notice only | Founder + Commerce |
| P0 | FV-owned Mind / paid order | No authenticated purchasable rights-cleared SKU | Inventory actual products, ownership, checkout, fulfillment, refunds | **HOLD**; free Focus is NOT a paid SKU | Founder + Claude |
| P1 | Social / qualified landing | No independently authenticated creator media ID | Praxxis verifies published video, rights, real mobile CTA/UTM | **UNTESTED**; three proposed research matches only | Praxxis + Grok |
| P1 | Article / lead | Jetpack confirmed lead and welcome proof incomplete | Read existing list/delivery once, no duplicate subscribe | **UNTESTED** | Claude + Dispatch |
| P1 | Presell / paid conversion | Link unauthorized; B film unhosted; browser QA absent | Preserve A/B copy parity, release only after prerequisites | **SOURCE BUILT; B PLAYBACK NOT VERIFIED; HOLD** | Mind + QA |
| P0 | Merchant settlement / net | No authenticated revenue ledger or human denominator | Reconcile portal/processor with first-party cohorts | **NOT COMPUTABLE** | Commerce + Claude |

## Internal-link and division-of-work plan

Live /explore/ or /free-resources/ → future /mind/ only after QD and release; current live /mesmerism/ → /free-resources/puysegurs-animal-magnetism-files/; /change-blindness/ → /focus/ as an optional practice resource; future ideomotor article → Puységur source, source studies and free Fieldbook; research article → guide only where topic-to-product intent justifies it. Avoid automatic paid widgets inside every article.

The hub prototype is intentionally `noindex`, source-only, not written to WordPress. No menu or homepage takeover. PR #49, Issue #150 and canonical Mind PR #172 are protected; Dispatch #174 and existing Jetpack welcome stay owned by their teams. No publication, email, social post, paid SaaS, merchant acceptance or tracking deployment is authorized by this file.