# R375 | Conversion acceptance, design experiment and cross-team release handoff
**Final Vestige Studios — Mind & Perception · 14 November 2026 · UNPUBLISHED / HARD HOLD**

## Executive decision
The only independently observed sellable candidate is a seller-described Zen12 Premium product with **unverified FV partner eligibility and earning URL**. The existing Focus Fieldbook is verified as free; it must not be misrepresented as a paid FV-owned SKU. A rights-cleared, currently payable FV-owned Mind product has **not** been authenticated and cannot be substituted as a confirmed sellable offer. Therefore there is **no active paid CTA**. A/B designs are decision tools, not a live revenue experiment.

This cycle improves the *quality of the commercial decision*, rather than claiming a benefit from another prototype. Priority: (1) prove an offer FV can legally be paid for; (2) prove the purchase path works; (3) launch with adequate independent substantiation and paid-return attribution; (4) only then optimize A/B copy or film.

## What was actually read
- Canonical [Mind Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [commercial Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818), and Dispatch [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174).
- Current [official Inspire3 catalog](https://inspire3.com/), [Zen12 exact public Premium page](https://zen12.com/), public [affiliate portal](https://affiliates.inspire3.com/), [Hypnosis Live](https://hypnosislive.com/), [Brainwave Shots](https://brainwaveshots.com/).
- Published [Puységur master archive](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/), [Focus Fieldbook](https://finalvestige.com/focus/), [Dispatch](https://finalvestige.com/dispatch/), [Franklin/Mesmer investigation](https://finalvestige.com/2026/11/02/mesmerism/), [change-blindness investigation](https://finalvestige.com/2026/11/02/change-blindness/). Issue #171 describes 61 live investigations; do not claim to have individually reread all 61 this cycle.
- [FTC endorsement FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) and [health-claims guidance](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance); primary Loftus–Palmer paper and modern meta/scoping reviews listed in R375 investigation.

## One high-intent product and buyer
**Audience:** Research-minded reader from a perception/suggestion video who is trying to start a short, sustainable quiet routine and evaluating whether a structured 12-minute audio course is worth paying for.

**Offer:** Zen12 Premium, seller-described twelve levels, four listening options at each level, 48 MP3s and associated guide/support. Public page displayed $87.99 on Nov 14 and advertised one-year refund protection; those are page observations and seller promises, **not authenticated checkout charge/returns**. Material benefit claims including one-hour equivalence, better focus, health, relaxation outcomes and brainwave entrainment remain independently unsubstantiated for this specific SKU. If FV partner rights remain unverified, **keep merchant controls disabled and first test the free Focus route**; do not pretend free leads are sales.

**User need → bounded promise:** "Know what the audio package includes, what it cannot prove, and how to try a twelve-minute no-cost routine before deciding." Measured purchase objective remains eventual confirmed paid order/commission, not time-on-page or clicks.

## Three creator-topic → evidence → existing Focus/Dispatch → vetted offer journeys
These are planning candidates **ONLY**, not assigned Grok posts or proof that matching published assets exist.

| Proposed video intent for Grok/Praxxis to match to an ALREADY PUBLISHED actual asset | Actual live editorial landing destination | Existing free bridge | Optional commercial fit / limit |
|---|---|---|---|
| A visible scene changes while the viewer fails to notice: change blindness | https://finalvestige.com/2026/11/02/change-blindness/ | Existing https://finalvestige.com/focus/ | Zen12 format only if viewer expresses interest in a regular short listening routine; change-blindness evidence is NOT audio efficacy |
| Franklin's 1784 blindfold and sham magnetism tests: what expectation explains | https://finalvestige.com/2026/11/02/mesmerism/ | Existing https://finalvestige.com/dispatch/ or /focus/ | Hypnosis Live requires exact product page, permitted rights, and independent claim review first; NO current affiliate CTA |
| Puységur archival case: when signed witness statements don't establish cause | https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Existing https://finalvestige.com/focus/ | Zen12 buyer guide as separate independent reading, NEVER evidence of magnetism/hypnosis success |

Praxxis must verify immutable published `asset_id`, published URL/date, exact promise, original Grok caption/hook, mobile landing match, consent/link placement; no guessed IDs or retroactive attribution. Send source/hook candidates through existing TASK-008 only. Grok owns creation/posting. No repurposing of video clips or reassignments.

## One offer CTA: implementation contract
**Pre-approval copy:** "Merchant purchase unavailable — approval pending" in a natively `disabled` `button`, preceded immediately by "Prospective affiliate disclosure: If you purchase through a future qualifying link on Final Vestige, Final Vestige may earn a commission at no additional cost to you. No earning link is active here."

**Activation preconditions (all need affirmative evidence):** authenticated named Final Vestige affiliate account, permitted site/social/email channels, issued approved exact product tracking link, merchant campaign-specific landing and final checkout, clear refund terms, product claims reviewed, founder commercial approval, founder production release approval, independent Site QA, working native keyboard CTA, no misleading link cloaking, consent-respecting analytics.

**Once approved:** replace the disabled control on a separate release-authorized branch with one real `<a href="ISSUED_VERIFIED_URL" rel="sponsored noopener noreferrer">` appropriately labeled "See the seller's current Zen12 Premium offer" beside a clear commission disclosure. The placeholder in this memo is notation **not a real URL**; never insert it into rendered HTML or analytics. Do not hardcode price until exact authorized checkout is checked. An outbound click is only an outbound click.

## A/B design: useful guide vs useful guide + optional original 42s film
- **A/control:** comprehensive evidence-led Zen12 buyer guide; text stands alone and the single disabled merchant decision point remains visible. This is already a useful source guide.
- **B/test:** exact same substantive buyer content with an original SVG poster and 42-second storyboard panel. The six timed VTT captions and full transcript are source-controlled. **There is no playable encoded film today**; B cannot be called a finished video variant.
- **Hypothesis:** for an intent-qualified visitor, a user-initiated 42-second explainer may improve understanding and *paid purchase* decisions without harming trust, speed or accessibility. Could hurt conversion; do not claim an uplift.
- **Primary analysis (after approval):** independently confirmed, refund-adjusted net revenue per 1,000 qualified-human sessions, reported separately for A and B by 7-day and 30-day acquisition cohort, with uncertainty intervals and low-sample caveats.
- **Secondary diagnostics:** confirmed orders/customers, paid conversion rate; confirmed Jetpack leads and lead-to-customer rate only where identity is privacy-safely reconciled; useful guide completion/self-reported decision clarity in an opt-in, separately consented study if ever approved; CTA outbounds counted only as behavior, not purchase.
- **Assignment:** one stable privacy-safe first-party experiment bucket per anonymous consenting session using an existing site system; do not add fingerprinting, new persistent IDs or outside SaaS. If existing system cannot do it, hold A/B rather than install a second analytics script. First visit must see text even without JS.
- **Quality gates:** 360/390/768/1440/1920 widths, keyboard-only, focus-visible, no-JS, semantic order, reduced-motion, WCAG 2.2 AA color/contrast review, no autoplay/third-party embed, static poster fallbacks, native captions, readable transcript, WebVTT timing, under-one-megabyte *target* for encoded video (not measured), responsive LCP/CLS checks, WordPress sanitization and plugin compatibility.
- **Stop criteria:** missing partner authorization, incorrect checkout or refund terms, missing disclosure, health claim leakage, social-video claim mismatch, inaccessible media or CTA, significant LCP regression, undelivered product, unexplained settlement mismatch, missing consent handling. Do not run until cleared.
- **No tiny-sample winner:** avoid selecting a winning variant on a few unverified clicks; publish sample sizes, window and uncertainty.

## Privacy-safe first-party measurement contract (design only; Claude owns engineering)
1. `qualified_landing`: approved source `platform`, unique verified `asset_id`, `utm_campaign`, 7/30-day cohort date, internal page/variant, bot filtering evidence, anonymous consent class. Never store email/IP/user agent or URLs containing personal strings in this custom event.
2. `focus_cta_click`: explicit click on **existing** /focus/ route. Not a subscription.
3. `focus_provider_confirmed_lead`: Jetpack provider-confirmed status, if and only if the provider permits lawful aggregate matching; signup attempt ≠ lead; preserve welcome; aggregate where matching cannot be lawfully done.
4. `affiliate_outbound`: only after approved link activated, explicit click on issued destination; user-friendly no redirect cloaking and vendor-terms compliance. Not a paid event.
5. `merchant_paid_order` or `paid_affiliate_conversion`: authenticated merchant/payments/affiliate report with transaction-level deduplication, correctly joined where permitted, excluding canceled/unpaid; never infer from UTM, thank-you page or outbound.
6. `refund_or_chargeback` and `merchant_fees`: official post-settlement adjustments. Keep a separate data-quality ledger of unmatched transactions and missing evidence.

Canonical UTM proposal: `utm_source=platform`, `utm_medium=organic_social`, `utm_campaign=mind_suggestion_2026_11`, `utm_content=VERIFIED_REAL_ASSET_ID`. `VERIFIED_REAL_ASSET_ID` is a placeholder, not an observed value. Use a simple owned canonical URL; no cookies required for reading, no trackers deployed in this draft.

**Formula:** `net_revenue_per_1000 = 1000 * (settled_gross_revenue - refunds - chargebacks - attributable processing/platform fees) / qualified_human_sessions`. If either amount or denominator is unauthenticated, display **NOT COMPUTABLE**, not zero and not an estimate. A zero applies only to independently established zero actual net revenue with a measured valid denominator. For affiliate commissions, count **settled payable commission actually due** rather than seller's gross order value.

## OFFER → FUNNEL STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER
| Offer and step | Missing blocker | Change/experiment | Evidence | Owner |
|---|---|---|---|---|
| Zen12 → paid commission | Named FV acceptance, channels, issued tracking link | Private affiliate-account validation of campaign-specific link, actual checkout and refund policy | **HOLD — not authenticated** | Founder / Commerce |
| FV-owned alternative → paid order | No independently verified active, rights-cleared, fulfillable paid Mind SKU | Read-only Payhip/catalog SKU, rights, live checkout, delivery, refund and receipt check | **HOLD — not authenticated** | Commerce |
| Grok video → verified article landing | Three immutable published matching IDs unknown | Praxxis confirms already-existing posts and mobile URL accuracy | **UNKNOWN — no asset proof** | Praxxis / Grok |
| Article → provider-confirmed free lead | Existing Jetpack confirmation + attribution untested | Consent-aware QA via existing subscription and welcome | **UNTESTED — no duplicate form** | Claude / Dispatch |
| A/B presell → actual paid conversion | Video not playable, merchant locked, no browser QA | One controlled film production + browser/performance tests when authorized | **DESIGN ONLY** | Site QA / Claude |
| Merchant purchase → net / 1,000 | Paid orders, qualified humans, refunds and fees not reconciled | 7/30-day independently reported cohort ledger | **NOT COMPUTABLE** | Commerce / Claude |

## Cross-team scope and release
- **Homepage art lead (#150):** research-only note on one perception portal; do not touch frozen homepage PR #49.
- **Canonical Mind hub PR #172:** leave unchanged; this draft is an alternative review artifact, not a competing CMS implementation.
- **Site QA #126:** independent a11y, claim, disclosure, link, legal/rights, performance and sanitized CMS preview review. No fake sign-off.
- **Dispatch #174:** may refer to relevant investigations under its own editorial permission; do not edit the Jetpack welcome, issue drafts, or send email.
- **Grok/Praxxis TASK-008:** research-only three-topic handoff; no media production, scheduling, posting or task reassignment.
- **Founder:** alone approves commercial partnership, production release and any spending.
- **Claude:** alone owns production site and measurement engineering; do not add scripts here.

**Scope guard:** All R375 files belong only to `mind/r375/`. No live WordPress, menus, homepage, PR #49/172, issue #150, Jetpack, marketing emails, paid SaaS, merchant activation, order, merge or deploy. Source-control and deterministic isolated assertions are **not** browser UX proof, actual playable film, paid purchase, commission or revenue.
