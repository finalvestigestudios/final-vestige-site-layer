# R172 — One-offer conversion proof, creator fit and no-release measurement contract
**Mind & Affiliate Studio | November 6, 2026 | Source-controlled DRAFT, not an instruction to deploy.**

## Founder's outcome, not a traffic vanity target

The customer outcome is **FV-net revenue from actual paid orders or independently settled affiliate commissions**. Our denominator is **qualified human sessions** attributable to real creator assets, not total WP views. The primary indicator is

`FV realized net revenue per 1,000 qualified human sessions = 1000 × reconciled FV-net receipts / independently qualified human landing sessions`.

If either input is unknown, publish **NOT COMPUTABLE**, not 0, not a guessed rate. Show 7-day and 30-day cohorts with sample counts, unknowns and refunds/reversals separately. Display purchased customers and merchant-confirmed paid transactions distinctly from email confirmations and affiliate outbound clicks.

FV-owned products: begin with cleared FV customer payments **already net of discounts**; subtract refunds/chargebacks and FV-borne transaction or fulfillment costs **only where not already netted in settlement**. Track taxes appropriately depending on what FV actually retains; merchant-collected tax is not revenue.

Affiliate: begin with **FV's actual received/settled commissions**, never the merchant's total retail order value. Subtract only reversals, withheld adjustments or FV-borne costs not already reflected. If merchant approval/sale is reported but no settlement is shown, label as **pending/unrealized**, not realized revenue.

No native script changes, cookies, user fingerprints or session-ID collection are authorized. Claude and QA should inspect existing WP/Jetpack + Ahrefs instrumentation and reuse it when adequate rather than duplicating scripts.

## Explicit offer decision

**Candidate:** Zen12 Premium. **Why:** among Inspire3 products examined this is a concrete, seller-described audio library: twelve levels, 48 MP3s and four style choices. Exact official homepage: https://zen12.com/ inspected Nov 6, 2026, where Premium showed $87.99 and one-year guarantee. These are seller statements, not checkout, refund, medical or efficacy proof.

**Current decision: HOLD**. Public https://affiliates.inspire3.com/ confirms a program; it does not confirm FV-specific acceptance, current media permissions, approved earning link, approved email channel, account-level conversion reporting or settlements. A bounded Gmail search found promotional messages but no acceptance evidence. Do not extrapolate commission from the portal's generic marketing. Inspect named authenticated account terms before attempting launch.

**Fallback:** FV-owned digital Mind SKU. **Decision: UNKNOWN** rather than pretending an existing paid product matches. Live WP pages show published Focus (free) and Puységur. A live Payhip Mind SKU, the creator's rights, current price, checkout, fulfillment, returns and transaction reporting have not been authenticated. Commerce owner verifies existing Products 001–015 **before** this lane designs a new checkout or claims anything is sellable. The main Mind lane should avoid repetitive speculative pre-sell pages until an eligible offer exists.

## 3 creator-topic-to-offer fit candidates (not posting orders)

| Proposed hook/topic | Current public destination and evidence | Intent and expected action | Offer eligibility | Owner / media proof |
|---|---|---|---|---|
| "You looked at the image. Why did the change vanish?" | Published https://finalvestige.com/2026/11/02/change-blindness/ and original [Simons 2000](https://journals.sagepub.com/doi/10.1068/p3104) | Broad science curiosity; investigation then optional **existing** https://finalvestige.com/focus/ . Do **not** aggressively sell Zen12 to low-intent viewers. | Only later, self-selected buyers requesting audio comparisons | Grok/Praxxis must return actual `asset_id`, platform URL, publish timestamp, caption/allowed link placement; UNKNOWN now. |
| "Could you sense a change but be unable to name it?" | R172 **UNPUBLISHED** investigation; [Salzman 2023, 91 participants](https://pubmed.ncbi.nlm.nih.gov/37263078/) | Source curiosity / evidence education. No public link to non-existent /mind/; only published archive link after approval. | Optional Focus, purchase-intent self-selection only | Grok controls production. Asset ID, creative, permissions and status UNKNOWN. |
| "A nine-month study used attention, socioemotional and sociocognitive modules; working-memory improvement was specific to the attention module" | R172 unpublished investigation; [Böckler & Singer 2022](https://pubmed.ncbi.nlm.nih.gov/34843370/) | High-intent comparison: readers specifically evaluating meditation products may navigate to separate independent Zen12 guide after it is released and link authorized. | Seller facts only; affiliate CTA disabled pending written authorization | Grok/Praxxis coordinate through existing TASK-008; actual media IDs NULL. |

Do not overwrite Grok's TASKS queue or write video scripts for production. This is a research-fit suggestion. The existing dated Praxxis/Grok handoff contains earlier iterations and blocked link status; actual publisher asset IDs still require independent confirmation.

## One high-intent offer landing

The separate R172 HTML **is the proposed buyer page**, not a live WP draft, production preview URL, functional affiliate funnel, endorsement or evidence that FV used the product. The page positions the buyer's decision as "is a library of short guided and unguided sessions worth paying for?" It explains exact seller-listed features, explicit limitations, current dated seller display, questions about checkout and refunds, a free exercise, and alternatives. There is an independent science section; the science is **not** used as proof that Zen12 works.

**CTA policy:** a native disabled `button` with no `href`, no external merchant anchor, no click handler, and a conspicuous adjacent prospective commission disclosure. The active secondary CTA is the existing free Focus Fieldbook URL, not a newly created lead capture form. Once a named approved earning URL and channels are independently verified, a *new* proposed PR may replace the disabled control, with `rel="sponsored noopener noreferrer"` on the legitimate earning link as appropriate and adjacent plain-language disclosure. Never automate that activation from a JSON flag or build script. **Founder release is separate.**

**Optional video variant:** current file contains a no-network 42-second poster/transcript/storyboard concept inside a `details` element. It is explicitly **not playable**, not an experiment, not an asset posted anywhere. Production should use original assets and a caption file, screen-reader-accessible player controls and a tested no-JS fallback. No autoplay, hidden sounds or third-party embeds. Creator owns actual production if it becomes a social asset; approved site implementation is Claude-owned.

## Controlled A/B hypothesis only after offer and release gates

- **Question:** among visitors with demonstrable buyer intent, does a 42-second, optional, original research explainer help *confirmed paid conversions* relative to the otherwise identical text-only buyer guide?
- **A:** text-only guide. **B:** same text and CTA plus user-initiated captioned, transcripted, original video. The media must not load before intent; fast poster, no large render-blocking script.
- **Primary outcome:** merchant-confirmed purchases per qualified human landing session, and FV-net revenue per 1,000 eligible sessions once settled (separate metrics). Secondary: buyer guide progression, CTA activation/click, Focus confirmed leads, support/refund rates.
- **Assignment:** Claude proposes first-party page variant assignment without PII or cross-site identifiers, compliant with consent requirements, stable enough to avoid visitor churn. QA verifies there is no duplicate event emission; unique campaign asset ID + source + variant tags are only aggregate fields when permitted.
- **Guardrail:** comparisons need equal offer/checkout terms, stable channel mix, real sample sizes, accessible playback, no forced video and no conversion manipulation. A/B test stops if receipt matching is impossible or product approval expires. Do not declare a winner based on a handful of clicks.
- **Status:** NOT RUN. No audience allocation, exposed variant, sales, subscriber or incremental revenue data exists.

## Minimal first-party measurement / consent specification

**Canonical proposed Grok URL fields:**
`utm_source=<verified_platform>&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=<verified_immutable_asset_id>`.
Whitelist platform source; escape/validate input; reject unknown asset IDs rather than inventing one. If platform provides only a profile link, document the resulting attribution ambiguity. Never claim a specific video caused a visit without a defensible link mapping.

**Event ladder (design-only, verify existing analytics first):**
`qualified_campaign_landing` → `article_to_focus_click` or `article_to_buyer_guide_click` → `confirmed_focus_subscription` (only a consent/delivery record, not form impression) → `affiliate_outbound_click` (after activation only) → `merchant_confirmed_paid_sale` (only partner authenticated) → `affiliate_commission_settled`. Owned products use `owned_checkout_start_verified` / `owned_paid_order_confirmed` / `owned_net_settled` only with merchant evidence. Event names are a **proposed schema, not installed code**.

Strip or exclude PII (name, email, full IP, user-agent fingerprints, cart IDs, unique customer identifiers). Do not fire tracking merely by visiting the page absent appropriate privacy/legal review. Do not leak campaign IDs into external earning links unless permitted by affiliate terms; no cloaking or fabricated tracking redirects.

**Count reconciliation:** compare merchant paid-order IDs *only in the authorized commerce environment*, aggregate verified sales by cohort with deduplication there, and publish counts only. Exclude canceled/refunded orders appropriately and retain an audit trail. Never reconcile individual customer records in public GitHub issues or shared creator Drive notes.

**Every 7/30-day report:** eligible cohorts, human-session denominator and confidence, actual source/asset IDs, landing → Focus click → lead (confirmed) → outbound (if active) → merchant-confirmed sale → settled FV net, refund rate, acquisition cost (normally $0 paid media), content hours, and reason for every unknown. Impressions, followers and pageviews belong in a separate diagnostic row.

## Funnel blockers → changes → acceptance evidence → owner

| Priority / offer | Funnel step | Blocker | Change/experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| P0 Zen12 | Commercial eligibility | No named approval, authorized earning link, approved channels | Read authenticated affiliate dashboard terms and owner account correspondence | **FAIL/HOLD** until exact publisher approval + allowed website/social/email channels + link saved privately | Founder / Mind |
| P0 FV-owned product | Current sellable alternative | Payhip SKU, rights, current pricing, checkout/delivery, refunds unverified | Commerce read-only authenticated Payhip inventory, not WP landing guesses | **UNKNOWN** until product, pricing, permission, fulfillment and confirmed paid transaction evidence | Commerce |
| P1 Zen12 | Buyer → sale | CTA intentionally disabled | After approval, create separate release PR with correctly disclosed exact approved link | **BLOCKED**, avoid claiming click/commission | Mind / Claude / Site QA / Founder |
| P1 Grok | Creator → landing | Exact media IDs, live URLs and CTA placement missing | Praxxis/Grok TASK-008 reconciliation; use existing published Change Blindness today | **UNKNOWN** until published asset IDs and observable first-party attribution | Grok / Praxxis |
| P1 Focus | Source → opted-in reader | Welcome/delivery and count discrepancy unverified | Site QA guest consented test of existing Jetpack form; no duplicate form or test subscription without approval | **UNKNOWN** | Site QA / Dispatch |
| P1 Measure | Paid order → FV-net | No merchant settlement or qualified denominator | Claude existing-analytics inventory + authorized reconciliation | **NOT COMPUTABLE**, not zero | Commerce / Growth / Claude |
| P2 A/B | Landing → paid conversion | No approved offer/video/browser QA | Text-only versus original video after product/release proof | **NOT RUN** | Mind / Grok / QA |
| P2 IA | Archive → Focus / optional guide | Hub PR #172 unreleased, historic 6 categories must remain | Library/Explore route once released, optional homepage feature designed by art lead | **UNRELEASED** | Homepage #150 / Claude / Site QA |

## Navigation and link map

- Existing **Explore/Library** → future `/mind/` **only after** the canonical hub owner/PR #172 and release signoff; never auto-create a top-level seventh historical tile.
- Live Change Blindness post ↔ future R172 investigation after editorial release; prior direct page remains unchanged.
- Live Mesmerism post → published Puységur archive → future History of Suggestion hub; no commercial conclusion inside the investigation.
- Future /mind/ → live Focus Fieldbook → existing Jetpack/Dispatch; reader can also navigate directly to Tools Under Review without subscribing.
- Separate Zen12 buyer guide → dated seller product facts / free alternatives / Focus; commercial link absent until account authorization and founder release.
- Dispatch #174 owns newsletters, welcome and permissioned sending; this lane **does not** edit/send any issue or list.

## QA and release acceptance

Before any release: independent primary-source review, exact merchant-page capture, dated price/returns verification, named authorization, current permissible earning link, text contrast at 360/390/768/1440/1920, keyboard navigation, skip link, no-JS behavior, reduced-motion, optional video with captions and transcript, no third-party embeds, link integrity, secure external-link attributes, no duplicate tracking scripts, performance/LCP check, privacy policy, no email form duplication, real visitor-path test with explicit consent, and explicit founder release approval.

**Status at commit:** work is BUILT source-only. Structural source-level assertions may be TESTED separately. Everything else—browser, mobile, CI, checkout, earnings, releases, video production—remains UNTESTED/UNKNOWN. No WordPress, social, email, merchant or paid changes.

**References:** https://zen12.com/ ; https://inspire3.com/ ; https://affiliates.inspire3.com/ ; https://pubmed.ncbi.nlm.nih.gov/34843370/ ; https://pubmed.ncbi.nlm.nih.gov/37263078/ ; https://pubmed.ncbi.nlm.nih.gov/24395196/ ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance ; GitHub Issues #171, #820, #818.
