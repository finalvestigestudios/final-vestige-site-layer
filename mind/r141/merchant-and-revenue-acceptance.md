# Mind R141 · Conversion-First Decision Record / Founder Gate Sheet
**2026-11-05 · Source-controlled, unmerged, unpublished · Issue #171 / #820**

## Priority zero: authorize an actual sale or stop treating clicks as outcomes

The conversion target is not an attractive landing-page view, a subscriber, an outbound affiliate click, or a reported “EPC” on a public marketing page. It is a merchant-confirmed paid order or paid affiliate commission, reconciled to refunds, fees and the correct cohort of qualified human visitors. So far there is **no authoritative Final Vestige-specific evidence** for the required paid events or a complete qualified-human-session denominator. Net revenue per 1,000 qualified human sessions is **NOT COMPUTABLE**, not $0 and not an estimated uplift.

The [public Inspire3 portal](https://affiliates.inspire3.com/) describes a network open to applicants. Its marketing page is not a signed, approved Final Vestige account, and the general claims it makes about payouts are not the commission terms of this business. A targeted read of available Gmail matches retrieved promotional Inspire3 messages, not a verifiable acceptance/terms package. That negative result is **search-scope-limited**; it is not evidence that Inspire3 rejected Final Vestige. Product checkout eligibility remains a separate question.

The fallback must be an **existing**, paid, rights-cleared Final Vestige digital product with verified order acceptance and downloadable delivery. Public search and the available Gmail query did not establish an eligible Mind Payhip SKU. The absence of proof is **not proof of absence**. Do not invent a replacement price, URL, invoice or product.

### One high-intent buyer, one candidate offer

**Reader:** An adult searching for a short, structured, downloadable meditation-audio routine, who is willing to compare formats without expecting treatment or guaranteed concentration.

**Conditional primary offer:** Zen12 Premium (seller describes 12 levels, 48 MP3 files across four listening styles at [the exact page](https://zen12.com/hnp)). The format could match this buyer; the evidence does *not* validate the merchant's hour-equivalence or neurological benefit claims. The seller advertises $87.99 on the reviewed page and a one-year guarantee; neither is an independently authenticated checkout amount/refund result.

**Next step:** KEEP DISABLED pending named written acceptance, specific approved earning URL, channel-level permissions, current checkout and return-term review, and aggregate-only/no-personally-identifying reporting.

**Owned-product fallback:** Select no SKU until Commerce can show Payhip product ID, current live paid listing, FV distribution/asset rights, fulfillment test proof, return/refund terms, and at least one source-confirmed purchase. This avoids building a fictional sales funnel. If verified, prepare a separate rights-cleared landing page for that exact SKU and obtain founder release approval.

## Offer → Funnel step → Blocker → Change/experiment → Evidence → Owner

| Priority | Offer + step | Blocker | Change / controlled test | Current evidence / decision | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → affiliate paid order | FV-specific approval, exact authorized URL, permitted social/email/web channels absent | Authenticate named account, written offer eligibility, permitted link and reporting | **FAIL / HARD HOLD**. Public signup only. | Founder + Mind |
| P0 | FV owned Mind product → paid checkout | Eligible SKU, rights, delivery, refund rules unverified | Inspect existing 001–015 Payhip catalog against source of truth; do authorized checkout/fulfillment smoke test | **UNKNOWN**: no authenticated checkout. | Commerce + Claude |
| P0 | Paid order → realized net revenue | Merchant orders, refunds/fees, qualified visitors unverified | Reconcile 7/30-day settled order export with privacy-safe qualified sessions | **NOT COMPUTABLE**, not zero. | Commerce + #820 |
| P1 | Grok asset → landing article | Actual published media IDs, platform link path, destination verification missing | Praxxis/Grok TASK-008 reconcile exact media ID and link placement; don't edit their queue | **NOT VERIFIED**, no attribution claim. | Grok / Praxxis |
| P1 | Published article → existing Focus | Body-level CTA to /focus/ not confirmed in Change Blindness/Puységur | Site QA checks full rendered path, voluntary Jetpack confirmation and welcome without adding test subscribers | **INCOMPLETE**. | QA/#129 |
| P1 | Buyer guide → qualified purchase | Authorized CTA disabled, no privacy-safe assignment | Evaluate text-only A versus same guide + optional original film B *only* once gates pass | **NO A/B RUN OR UPLIFT EVIDENCE**. | Mind + QA |
| P2 | /mind/ hub → archive/buyer guide | Canonical PR #172 unmerged; draft proposals exist | Consolidate proposals under source-owned #172; review hierarchy on 360/390/768/1440/1920 | **DRAFT ONLY**. | Mind + homepage art + QA |

## Three creator-to-archive mappings (research-only)

**Path 1 — Change blindness:** Grok-owned original asset (immutable media ID currently unknown) → published [Final Vestige Change Blindness article](https://finalvestige.com/2026/11/02/change-blindness/) → *optional*, separately verified Focus CTA → independently written Zen12 guide if approved. The perception effect should never be presented as evidence that the recording works.

**Path 2 — Mesmerism / Puységur:** Grok-owned historical video (actual ID unknown) → [Puységur's Animal Magnetism Files](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) → optional Focus → independently qualified Hypnosis Live Total Focus guide only where the product is relevant and accepted. Historical accounts of animal magnetism do not validate hypnotherapy product claims. The buyer must be able to read the historical archive without facing a sales conclusion.

**Path 3 — Hypnosis and memory confidence:** A *proposed* Grok editorial angle requiring Grok's decision → **unpublished** R141 `hypnosis-memory-confidence-investigation.md` → optional Focus after any approved release, with **no product CTA inside the investigation**. Do **not** invent a public URL or claim Grok has posted this. Any product guide is a separate, voluntary navigation step.

Use `utm_source=<actual platform>&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=<verified media asset_id>` only where a clickable, valid link exists and owner/production engineering authorizes it. The platform may require a profile-link pathway instead of a caption CTA. Do not change TASK-008 task assignments or author Grok scripts.

## Zero-PII measurement and independently reconciled revenue

**Event contract:** qualified_human_landing → article_to_resource_click → confirmed_signup_if_observable → offer_guide_view → (after authorization only) affiliate_click → independently reported merchant_confirmed_paid_order / affiliate_settled_commission → refunds and fees → realized_net_revenue.

Keep campaign identifiers and aggregate daily/source/asset counts; do not collect names, emails, IPs, full user-agent strings, individual buyer IDs or raw long query strings. Use existing native measurement where practical, not a new pixel or paid SaaS. The seller's [privacy policy](https://inspire3.com/privacy/) explicitly contemplates sharing buyer name/email/purchased-product details with referring affiliates; this requires a documented data-minimization agreement or a safe alternative before activation. A first-party `affiliate_click` event establishes **only** an outbound action.

**Formula:** net revenue per 1,000 qualified humans = (merchant-confirmed realized gross revenue or commissions - refunds - fees - applicable direct costs) / qualified-human sessions * 1,000. Affiliate reporting requires distinguishing pending attribution from final commission actually paid. Use **separate** seven- and thirty-day cohorts and record missing links in the chain; treat a small denominator as a warning, not evidence of an exact effect size. Do not reconstruct a buyer identity by joining personal data.

**Required ledger row fields:** cohort window, platform, exact asset_id, destination, human-qualified landing count, offer-view count, approved CTA click count, native confirmed lead count (if observable), merchant-confirmed orders, gross amount, final affiliate commission paid, refunds, fees, net amount, missing attribution flag, source of proof, owner signoff.

If an event count is unavailable, store `null`, never `0` or a fabricated estimate. A confirmed signup is not a paid sale. A merchant checkout start is not a settled order.

## Controlled text-versus-film experiment: precise release condition

The existing unpublished R139 prototypes `mind/r139/zen12-variant-a.html` and `zen12-variant-b.html` should be preserved. Variant B adds a six-caption original 40-second **storyboard** (not a video file). The guide body, seller claims, disclosures, disabled CTA and free route must remain equivalent. A complete playable B asset must pass independent rights, subtitle/caption, transcript, keyboard, pause/no-autoplay, reduced-motion and real mobile performance testing before any actual A/B launch. Any test should vary **only** the presence of video, not price, offer, routing, channel or signup.

**Primary success criterion:** source-confirmed realized net revenue per 1,000 qualified-human sessions, with paid conversion per qualified session as a companion; not button clicks. Show confidence intervals and sample sizes, mark tiny cohorts inconclusive, and only conclude causality when randomization and comparable traffic sources are confirmed. Don't deploy randomization scripts or new analytics under this draft.

## FTC and release QA

- [FTC Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) require clear, conspicuous material-connection disclosure close to any compensated recommendation. **Proposed adjacent copy:** “If you purchase through this link, Final Vestige may earn a commission at no additional cost to you.” Add only after a real, authorized link exists; pre-approval draft must still explain that it is inactive.
- [FTC Health Products Compliance Guidance](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance) requires independent, pertinent substantiation for express and implied product claims. Do not borrow general binaural/meditation research to imply proof of Zen12 efficacy.
- Require exact URL/offer/tier matching, independent source ledger, final terms, text/video copy parity, 360/390/768/1440/1920 responsive QA, native keyboard/screen-reader/reduced-motion/no-JS, consent, source-linked claims, and scope-specific founder signoff. No unapproved CMS/nav/email/social/merchant/analytics/deploy writes.
- Coordinate review with homepage design #150 (without touching flagship PR #49), site QA #126, Dispatch #174 (no newsletter copy edits), #820 and Praxxis/Grok TASK-008 (research-only). Canonical Mind hub PR #172 untouched.

## Decision to the founder

**HARD HOLD on all commercial activation.** Most valuable next action is NOT another hero animation or article; it is the merchant-identity/eligible-offer verification and the completed paid-sale evidence chain. This sprint adds distinct source-grounded research and a more reproducible refusal-to-invent decision record while preserving the existing draft landing test. **No claim of a live buyer, authorized commission, conversion rate or revenue improvement is made.**
