# Mind R177 — Conversion-first acceptance dossier, creator fit, editorial navigation and experiment plan
**Date:** 2026-11-06 PT · **Status:** UNPUBLISHED, NO COMMERCIAL AUTHORIZATION, no production write
**Owner:** Mind & Perception only. Coordination: #171, #820, #818. Release authority: founder. Engineering: Claude. Independent release QA: Site QA #126. Grok/Praxxis retain TASK-008 ownership. Dispatch #174 controls emails, not this branch.

## Decision, not another assumption
**NO GO for a Zen12 affiliate launch as of this review.** Reading https://affiliates.inspire3.com/ shows a real affiliate portal, not an FV-specific partner acceptance. A bounded Gmail check returned Inspire3 promotional emails, not named publisher authorization. No authorized dashboard approval, link, website/email permission or FV commission accounting was presented. No exact FV-owned Payhip Mind SKU was verified with rights, product delivery and live checkout. Public website research found an existing Focus Fieldbook and shop/collection content, not an independently authenticated FV Payhip Mind purchase. The commercial absence is a *data limitation*, not evidence of a failed market.

**One high-intent audience** for the future test: people already comparing structured, downloadable meditation-audio libraries because they want twelve-minute guided sessions. This is distinct from viewers casually watching a perception illusion. Their genuine purchase criterion is a usable audio curriculum, not promises of automatic health, wealth or cognitive change.

**One candidate offer**: Zen12 Premium, pending named authorization. Exact seller at https://zen12.com/ presents 12 levels, 48 MP3 files, four styles, optional guides/support, an advertised one-year guarantee and on Nov 6 an $87.99 Premium public display. This is NOT an FV price offer, checked-out total, product test, refund fulfillment, or independently established efficacy. Product page includes broad claims such as an hour of meditation in twelve minutes. *Do not adopt those claims.* See R177 claim-by-claim register and independent essay.

**Fallback**: commerce owner verifies an actually sellable, rights-cleared owned FV Mind product; if none, do not turn the free Focus Fieldbook into an imaginary paid product or use an unrelated product just to create a CTA. Current actions are source-control and QA only.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER
| Priority | Offer / step | Current blocker | Proposed change / experiment | Pass evidence required | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 affiliate → eligible earned commission | FV partner identity, channel permissions, link, attribution and terms unknown | Read authenticated publisher account and match the exact Premium product, permitted presell/email channels, tracking URL and rules | Named current approval, full URL with authenticated FV tracking, signed-off legal/FTC terms, portal screenshots redacted | Founder + Mind |
| P0 | Owned FV product → paid checkout | Verified rights-cleared Payhip Mind SKU not found | Inventory actual Payhip dashboard, delivery rights, final total, live fulfillment, refund policy, any disabled/test checkout | Product/price/rights proof + authorized noncharged test or existing completed purchase proof | Commerce |
| P0 | Landing → authorized merchant CTA | Merchant acceptance unverified; commerce blocked | Keep native disabled button + adjacent prospective commission disclosure; no merchant href | HTML parser/source check rejects any merchant purchasing anchor, enabled button, undisclosed earning link | Mind + Site QA |
| P1 | Grok topic → high-intent article visit | Published asset IDs, real CTA placement/URLs not reconciled | ASK Grok/Praxxis for TASK-008 immutable IDs; map into organic UTM names only after first-party validation | Source post URL, platform placement, campaign ID, authorized QA | Grok/Praxxis + Claude |
| P1 | Article → free Focus | Original article unpublished; one existing route exists | Preserve article independence and one existing Focus invitation | Source-link, viewport/keyboard test and observed user click counts (if existing measurement permits) | Mind + Site QA |
| P1 | Focus → confirmed subscriber | No test of guest consent, email confirmation and delivery | End-to-end authorized existing Jetpack funnel QA; no duplicate list | Consent log and actual delivery record, no inflated list count | Site QA + Dispatch |
| P1 | Partner/Payhip checkout → verified sale | No merchant settlement record, refunds or matched source attribution | Reconcile weekly payouts/orders, cost/refunds, with privacy-safe campaign aggregation | Independently confirmed paid orders/commissions and cleared net amount | Commerce + Growth |
| P2 | Optional short video → purchase | Video not produced; no valid outcome baseline | Test text-only vs original 42s video variant only after earlier P0 gates | 7/30-day qualified cohort order/commission rate with guardrails and power caveats | Mind + Grok creative + Site QA |

## Three proposed social-to-owned-content paths (not assigned publishing)
These hooks are **research suggestions**, not directives to create or publish. Each requires Grok's real immutable asset ID, platform, media URL, source/rights review and CTA approval through the already established TASK-008 handoff and board:
1. **“Why did twenty knots become a mental technique?”** (History of suggestion) → unpublished Coué article → optional existing Focus Fieldbook → separate Zen12 buyer guide for people looking specifically for audio structure. Research: https://www.gutenberg.org/ebooks/27203 ; no medical cure hook.
2. **“The gorilla didn't disappear. Your attention was occupied.”** (Perception) → prior Invisible Gorilla investigation / live hub after approvals → Focus Fieldbook → buyer guide **only if independently relevant**. Foundational: Simons & Chabris 1999; not a promise that listening will prevent inattentional blindness.
3. **“What the 1784 magnetic commission actually found.”** (Historical evidence) → live https://finalvestige.com/2026/11/02/mesmerism/ → published https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ → optional Focus. No automatic commercial offer: educational visitors are not necessarily shopping for hypnosis.

**Metadata contract per asset:** platform, immutable `asset_id`, published UTC and local date, exact platform source URL, `utm_source`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=asset_id`, actual final landing URL and native CTA placement. For a profile/bio link, maintain per-asset mapping where technically possible; mark unresolvable clicks unattributed. Do not inject UTMs in a merchant link before affiliate terms are approved.

## Buyer intent and conversion copy contract
**Hook:** "A recording can keep time. Can it keep a promise?" It speaks to a real buyer objection, not a clinical outcome.
**Story:** Coué's twenty-knotted string is a sourced historical detail, not a "secret trick".
**Demonstration:** Two-minute attention audit gives value without payment.
**Actual value:** Seller-described organized catalog with twelve levels and four listening styles, not magical brainwave promises.
**Objections:** price/checkout total not verified; refund execution untested; free alternatives exist; audio isn't proof of a health effect.
**CTA:** The only active action is to explore the pre-existing Focus page; the future commercial CTA is native-disabled and not instrumented. Disclosure is **next to the future commercial control**, not buried in the footer.
**No paid urgency, testimonials, exact payout, personal product-use claims, medical or wealth guarantees.**

## A/B hypothesis, version boundaries and guardrails
- Control A: evidence guide, sources, free activity, product decision criteria and disabled offer until approved.
- Treatment B: identical guide + one original **optional** 42-second video with light static poster, timed script, captions and full transcript. User-initiated `preload=none` delivery only after production. No added tracking libraries; no autoplay, no scroll hijack, and full no-JS utility.
- **Hypothesis only:** B might improve comprehension and subsequent paid conversion among high-intent shoppers; alternatively it might distract, slow page load or depress conversion. No assumed uplift.
- **Primary decision metric:** `net_realized_FV_revenue_per_1000_qualified_human_sessions = (sum settled FV-owned receipts - net refunds/chargebacks/fees/COGS not already deducted + actual paid attributable affiliate commissions - clawbacks/expenses not already withheld) / qualified_human_sessions * 1000`. Keep negative values; avoid double-counting fees/discounts already netted out.
- Secondary: independently confirmed orders/customers, confirmed paid commission rate, confirmed lead-to-customer conversion where opt-in is observed, qualified CTA clicks and engagement. `affiliate_outbound` and `checkout_started` are NOT `purchase_confirmed`.
- Report both 7- and 30-day attributed cohorts by asset ID and variant; preserve 'UNOBSERVED' instead of substituting zeros. Predeclare basic quality thresholds: no material keyboard/reading regression, no duplicate list or analytics event, no increased privacy exposure or unsupported claims. Tiny N yields descriptive results only: **do not call a winner** on a handful of customers.
- Assign variant on the first eligible first-party view using existing privacy-safe infrastructure if available. Avoid cross-site identifiers, cookies until consent/legal review, new scripts, fingerprinting, session replay, personal health information or unauthorized analytics. Avoid storing raw visitor IP in editorial test artifacts.
- If verified commercial offer is never approved, a text-versus-video experiment may measure comprehension but cannot answer the revenue-conversion question.

## Internal-link and navigation plan; no live edits
- `/mind/` remains a **proposal**. Preserve the approved home flagship #49 and canonical Mind hub PR #172. Draft four-stream hub in `mind/r177/mind-archive-no-sales-inference-HUB-UNPUBLISHED.html`; do NOT publish a seventh front-page historic category.
- Existing live routes (read-only checked): `/focus/`, `/free-resources/puysegurs-animal-magnetism-files/`, `/2026/11/02/mesmerism/`, `/2026/11/02/change-blindness/`, `/free-resources/`, `/affiliate-disclosure/`, `/editorial-standards/`.
- Suggested link flow: future archived Coué article → Puységur/Mesmerism (historical evidence) → Focus (optional free) → independently reviewed Zen12 buyer guide (optional and separate). Keep a direct path to guide for purchase-intent search without requiring email.
- Ask homepage art lead to consider only a bounded thematic feature; no changes to flagship layouts, header or existing slots. Site QA reviews focus order, 360/390/768/1440/1920 rendering, light/dark, screen-reader and real-browser contrast before any launch.
- Metadata: proposed title, original excerpt, source dates, canonical only when published. Prevent preview indexing via `noindex,nofollow` and keep preview out of public navigation/sitemap.
- Security: zero inline JavaScript, zero third-party tracking, no player iframe, no external purchased media, no new form. Never introduce raw merchant URLs as active CTA in the preview.

## Authorization evidence checklist
Before any conversion goes LIVE, owner must fill: publisher approval identity and date; exact authorized earning URL and tracking policy; website and email permitted placements; claim sign-off and seller page check date; current checkout final amount and refund terms; downloadable entitlement/ownership; privacy and consent; responsive browser QA with screenshots; native committed-source test and ideally CI; 42-second original video render plus captions if B; founder exact release approval. Commercial release is **HARD HOLD** while these are absent.

**What was checked this run:** read GitHub issues #171/#820/#818, current draft PR #1304, read-only live Focus and Puységur pages, official Inspire3 catalog and its affiliate portal, the exact Zen12 seller page, primary historical Coué text, Raz et al. primary paper abstract, general clinical hypnosis review, and FTC rules. Existing Grok TASK-008 and dated handoff were read; no takeover. Gmail query found consumer/promotional correspondence but not named FV partner approval; that is not proof that no acceptance exists in an unseen dashboard. WP public inventory did not authenticate Payhip SKU or completed checkout; no sale was tested.

**BUILT:** original investigation, buyer HTML/optional video treatment, hub HTML, evidence matrix, this dossier and source regression. **TESTED:** scope/source checks as reported separately. **NOT TESTED:** actual-browser WCAG, video playback, native storefront checkout, partner dashboard approval, Jetpack signup, verified affiliate sales, revenue. **LIVE:** no R177 changes. **VERIFIED PAID REVENUE:** none established; KPI **NOT COMPUTABLE** with missing authoritative data (not $0).
