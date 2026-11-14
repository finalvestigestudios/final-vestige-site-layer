# R363 — Commercial acceptance, creator fit and release constraints
*Founder-facing source-controlled review · November 13, 2026 · UNPUBLISHED · NO_TRADE / NO_COMMERCE*

## Decision first: is there a payable offer?

**Zen12 affiliate:** Public Inspire3 affiliate program exists at https://affiliates.inspire3.com/. Connected Gmail queries for Inspire3 affiliate acceptance, issued dashboard/link and partner onboarding found consumer marketing messages but **no account-specific proof of acceptance**. Do not infer denial or approval; status is **unverified**. No earning link or commission promise is authorized.

**Owned alternative:** The site's live `/focus/` fieldbook is free and linked to one Jetpack/Dispatch list. A rights-cleared, purchasable, deliverable FV-owned Mind-specific Payhip SKU has **not** been authenticated. A generic earlier list of FV products is not evidence of a relevant active Mind product, completed checkout or entitlement. Therefore no paid owned-product CTA can be enabled.

**Authorized near-term action:** retain a disabled Zen12 offer control and prominent free existing Fieldbook link until evidence arrives. This is an offer-readiness experiment, *not* a running commercial A/B experiment.

## One high-intent audience → one conditional offer

**Audience:** A person actively comparing short, structured meditation recordings because they want a repeatable practice format, not a guaranteed cure or cognitive performance shortcut.

**Seller's product:** Zen12 **Premium**; official page describes 12 levels, 48 MP3 files, manuals, audio guides, bonus support, one-year advertised refund promise, and a November 13 seller-displayed $87.99 price. Re-check final checkout terms and product exactness before activation. Do not imply that FV listened to, owns, or tested the recordings.

**Problem → insight:** “A recording can give the next twelve minutes structure, but the science has to match the recording—not just the surrounding idea of meditation.”

**Micro-story:** Rubber-hand studies demonstrate how a dramatic, sincere perceptual experience can coexist with scientific debate about its cause. This is a metaphor about evidence; **not** a product mechanism, effectiveness proof or hypnosis test.

**What the buyer receives:** Seller-described progressive downloads and guides; describe them clearly and link to accurate terms only after approval. **What is not established:** equivalence to long meditation, brainwave control, health or performance gains. The optional **free alternative** is the existing 52-page Fieldbook.

**CTA status:** native disabled button; adjacent prospective compensation disclosure. No active earning URL, tracking pixel, signup form, countdown, price promise, health claim or personal product endorsement.

## Controlled A/B hypothesis — conditional only

A = same evidence-first buyer guide and decision box, no video. B = **identical buyer guide core** plus original 42-second film with poster, captions and transcript. Hypothesis: optional visual context might improve **verified paid net revenue per 1,000 qualified human sessions**, without damaging trust or mobile performance. This is unproven. No A/B outcome exists.

When the offer becomes authorized, allocate 50/50 using existing first-party consent-respecting exposure logic owned by Claude. No new script or service. Record immutable `experiment_id`, `variant`, `asset_id`, `utm_campaign` **without PII**. Block bot traffic; treat unknown automation as unqualified until reviewed. Avoid querystrings with names, email addresses, device fingerprints or full referrer URLs. No experiment until reviewed by Site QA and founder.

### Preflight checks and rejection conditions

- Present the same full buyer copy and CTA in A and B. B's 42s original captions/transcript must remain readable without a video player, without JavaScript and with disabled autoplay.
- Under 390px width, disclosure and purchase control must be adjacent, in reading order. Keyboard navigation, reduced motion, contrast, screen readers, mobile browser and WCAG 2.2 AA require **actual** QA.
- A video may only be embedded after original rights, video and captions, responsive poster and lazy load are verified. Default no playback; no third-party trackers.
- Claim/price drift check must compare exact seller offer page on release day; record archived evidence and checkout screenshot privately, not in production.
- Merchant links never activate unless founder signs off with FV-specific program acceptance, channel authorization, exact earning URL, privacy terms, and refund/settlement details.
- Reject misleading urgency, fake visitor counts, proprietary brainwave guarantees or any health/wealth promise.
- Do not overwrite homepage PR #49, Mind hub PR #172, Issue #150, Dispatch Issue #174, Jetpack welcome, or Grok's production board.

## Three source-grounded creator pathways — proposed, not asserted posted

| Theme and hook for Praxxis/Grok verification | Research article destination | Free nurture | Conditional buyer review | Identity requirement |
| --- | --- | --- | --- | --- |
| Change blindness: “The stranger changed. Why didn't anyone notice?” | existing live Journal Change Blindness investigation (confirm exact canonical permalink) | /focus/ + existing Dispatch | independently reviewed Zen12 page, once partner approved | Grok must supply published `asset_id`, date, URL, allowed exact CTA path |
| Invisible gorilla: “The radiologist looked for nodules. What else was in the scan?” | existing source-grounded Mind investigative draft, UNPUBLISHED; do not direct to live until released | /focus/ | optional independent audio guide only after eligibility | No media ID yet verified |
| Rubber hand: “Can a hand that isn't yours feel like yours?” | this unpublished `THE_HAND_THAT_BECAME_YOURS.md`, not a live URL | /focus/ | Zen12 buyer guide, deliberately disabled | No media ID yet verified |

**Grok maintains creator production and posting; Praxxis maintains independent media/link QA; Claude maintains site route and first-party measurement; founder retains release/spend control.** TASK-008 is a coordination reference, not permission to queue a video.

## Attribution contract: clicks are not sales

**Events allowed only after consent/QA where applicable:** `landing_visit` (eligible human session, campaign/topic + A/B label), `focus_cta_click` (intent only), `focus_lead_confirmed` (Jetpack provider backed, if actual consent+correlation available), `affiliate_click` (outbound click, NOT order), `merchant_paid_conversion_verified` (partner report), `owned_order_paid_verified` (Payhip record), `refund_confirmed`, `fees_reconciled`.

**Consent:** do not create new cookies, local storage IDs, IP logs, new trackers, Facebook pixels or a second subscriber table. Reuse Claude's approved existing analytics pipeline if one has been validated; otherwise report attribution as unavailable. No email address in event payloads; aggregate counts and anonymized campaign IDs are sufficient.

**Primary KPI:** `net_realized_revenue_per_1000_qualified_sessions = 1000 * (gross_confirmed_paid - refunds - payment_fees - documented_variable_costs) / eligible_qualified_human_sessions`. For affiliate money use **actual settled, reportable commission** rather than total retail transaction. Do not include an affiliate click as a sale. In each 7-day/30-day cohort show numerator, denominator, number of paid transactions, refunds, source coverage, unsettled balance, and warnings for tiny samples or unattributed conversions. If missing, **NOT COMPUTABLE**, never $0.

**Secondary:** paid conversion rate, confirmed orders/customers (deduped from merchant records), lead-to-customer (only if consented reliable match), confirmed email opt-ins, and qualified topic visits. Views/followers are diagnostic.

## Owner-facing priority acceptance table

| Offer | Funnel step | Blocker | Change/experiment | Pass/fail evidence now | Owner |
| --- | --- | --- | --- | --- | --- |
| Zen12 | Referral → commission | FV-specific acceptance, allowed channels, issued link missing | Authenticate account and agreement; no link activated | **HOLD**; public program ≠ acceptance | Founder / Commerce |
| FV-owned Mind SKU | Checkout → paid receipt | relevant right-cleared sellable SKU/fulfillment not verified | Private inventory, checkout, returns and delivery audit | **HOLD**; no matching authenticated order | Commerce |
| Grok Mind assets | Social → article | three published immutable asset IDs missing | Praxxis verify existing posts and mobile-safe canonical paths | **HOLD**; proposed topics only | Grok / Praxxis |
| Existing Focus | Article → confirmed lead | Jetpack campaign-level confirmation not authenticated | test existing consent, opt-in and download delivery privately | **NOT TESTED** | Claude / Dispatch |
| Zen12 A/B | Buyer guide → paid customer | lack of authorization; B not encoded film; native browser QA | staging-only A/B after gates, no extra JS | **NOT RUN**; static drafts only | Claude / Site QA |
| Verified settlement | Paid → net | no merchant paid/refund/fee ledger | cohort reconciliation and paid-source custody | **NOT COMPUTABLE** | Commerce / Claude |

## Sources and independent checks

[Rubber hand original](https://doi.org/10.1038/35784) · [Nature Communications 2022](https://doi.org/10.1038/s41467-022-28177-z) · [Frontiers 2022](https://doi.org/10.3389/fnhum.2022.834492) · [Puységur](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) · [official Zen12 sales page](https://zen12.com/) · [Inspire3 affiliate program](https://affiliates.inspire3.com/) · [FTC endorsements](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) · [FTC health claims](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance).

**Unexecuted acceptance:** native Node verifier, hosted CI, browser WCAG/CSP/performance/CTA click, WordPress sanitizer, existing Jetpack lead and email delivery, merchant checkout, partner settlement, founder authorization. Nothing here establishes a live event, sale or revenue.

**Immutable source-control contract:** branch-specific additions under `mind/r363/` only. Draft PR; never merge/deploy/publish as part of this workstream.
