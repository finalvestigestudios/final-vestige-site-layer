# Mind R384 — conversion-first acceptance and creator routing

**Date:** 2026-11-14 PT. **Status:** DRAFT / UNPUBLISHED / HARD HOLD. **Scope:** `mind/r384/` only. **Release owner:** Founder.
**Forbidden in this branch:** edits to homepage PR #49, Issue #150 art lane, Mind hub PR #172, existing live WordPress CMS/navigation/settings, Jetpack welcome/list, Dispatch issue drafts, Grok queue/posts, production analytics, affiliate account, commercial activation, deployment, merge or spending.

## 0. Decision that actually matters

Before traffic volume or aesthetic polish: **is there a product the reader can legitimately buy such that Final Vestige is permitted to earn money and can verify a settled transaction?** At this checkpoint the answer is **not yet evidenced**.

- **Candidate:** Zen12 Premium. Public seller page https://zen12.com/ on 2026-11-14 described 12 levels, 48 MP3s, guide/manual and a one-year guarantee; a page display showed $87.99, but older captures disagree, and a named authorized checkout, final price, taxes, refunds/upsells and delivery were not verified. The guide identifies this as a provisional display, not a customer quote or fixed offer.
- **Inspire3 account status:** public signup/login https://affiliates.inspire3.com/ demonstrates a program exists, *not* that FV is accepted. Targeted connected-email search `("inspire3" OR "zen12") ("affiliate" OR "partner") -category:promotions` returned mainly consumer promotions and unrelated older mail. No reliable named Final Vestige partner approval, allowed TikTok/YouTube/website/email channels, issued URL, commission attribution or payout agreement identified. Search absence is not an official rejection.
- **Owned fallback:** the existing Seven Day Focus Fieldbook is a free 52-page Dispatch resource. Public FV library pages disclose the free route. A payable, rights-cleared, deliverable Mind SKU on Payhip or another merchant and its refund terms were NOT authenticated. No claim that it is sellable; no misleading substitute CTA.
- **Net-revenue truth:** This sprint has no authenticated merchant-confirmed paid order, referral commission, refunds or qualified-human denominator. The primary KPI is **NOT COMPUTABLE** (not zero revenue, and not a click proxy).

**Acceptance gate to switch offer from HOLD to ELIGIBLE:** written account-specific authorization and allowed channel terms; issued earning URL for exactly named SKU; exact merchant checkout/return/support verification; publisher-safe claims matrix; release approval. If failed, authenticate a real FV-owned paid SKU with checkout evidence rather than optimizing empty commerce buttons.

## 1. Defined high-intent reader and offer-to-message fit

**Primary reader:** a curious viewer of a grounded perception demonstration who is comparing short guided meditation-audio products but does not want pseudoscientific guarantees. They value convenient structured recordings, transparent format and an independent buyer checklist. The specific offer, if permissions are later satisfied, is **Zen12 Premium as a listening library**, never a solution to the gorilla experiment.

| Creator topic / source / status | Editorial destination / reality | Resource pathway | Commercial suitability |
|---|---|---|---|
| **Unexpected gorilla / 2013 expert search**. Original DOI https://doi.org/10.1177/0956797613479386. Grok media ID/URL **NOT VERIFIED**. | *The Gorilla the Experts Missed* is a **draft** in this PR, NOT a public landing. Do not route published social traffic to it. Existing live alternative https://finalvestige.com/2026/11/02/change-blindness/ is related, not equivalent; explicitly label that distinction. | Existing https://finalvestige.com/focus/ → optional reader guide once source-controlled draft is approved, not a required signup. | Zen12 suitable **only for explicitly audio-shopping visitors**, not everyone watching the gorilla video. Exclude "improves inattentional blindness." |
| **Change blindness/flicker or person swap**. Rensink et al. 1997; Simons & Levin 1998 as cited by live FV investigation. Published Grok asset ID **NOT VERIFIED**. | LIVE article https://finalvestige.com/2026/11/02/change-blindness/ ; verify mobile load and exact hook before tagging. | The same Focus Fieldbook and single Jetpack/Dispatch list. | More natural to free focus method than immediate paid Zen12. Avoid forced affiliate detour. |
| **Franklin/mesmerism and Puységur history**. Historical evidence-led lens. Published Grok media ID **NOT VERIFIED**. | LIVE https://finalvestige.com/2026/11/02/mesmerism/ → live route https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ (429 rate-limited this run; ask Site QA to validate). | Optional Focus → optional independent suggestion/hypnosis guide without claiming nineteenth-century science validates recordings. | Hypnosis Live or Zen12 only after exact product-level eligibility and intent review. No claim that early magnetizers were clinically effective. |

**Coordination:** Supply topic/source/URL match to Praxxis in existing TASK-008; Praxxis checks real published media URL, ID, platform, hook, referral permission and mobile destination and coordinates with Grok. Mind writes no Grok posting scripts or creator queue tasks. Dispatch Issue #174 already manages editorial emails; only product-link clearance belongs to Mind.

## 2. Buyer-experiment contract

**A =** standalone evidence-first buyer guide (HTML) with sourced research micro-story, seller-described inclusions, current price/returns caveat, five purchase questions, original free 12-minute practice, near-CTA plain commission disclosure, and natively disabled merchant control.

**B =** same content plus one original optional 42-second film **concept**. The treatment includes original standalone SVG poster, complete transcript and six WebVTT cues. It is **not encoded, hosted, or playable**. It cannot yet be a tested video conversion variant. There is no autoplay, embed, JavaScript, external poster, or tracking pixel. No-JS leaves the textual buyer guide fully readable, and a native `details/summary` transcript is accessible in principle. Prior to testing any video variant, produce a rights-cleared media file, closed captions, poster text alternative, keyboard-operable controls, reduced-motion behavior and actual browser/assistive technology proof.

**Explicit hypothesis:** for comparable eligible sessions from the same approved creator asset and buying intent, optional original short-film context *may* improve the **independently verified paid conversion rate and net revenue per 1,000 qualified sessions** versus A, while preserving accessibility and mobile performance. The null is equal/no lift; B could perform worse.

**Do not randomize now.** After approval, have Claude/site QA implement a privacy-reviewed, stable, anonymous first-party variant assignment inside the EXISTING measurement path if feasible, with one assignment per session (not fingerprinting) and consistent CTA/offer/price/disclosure in both arms. Persist only if permitted by existing consent mechanisms. No new paid SaaS or duplicate pixel.

**Sample caution:** with 10 or 20 paid events, a large-looking percentage lift is noisy. Predefine experiment window and minimum sample before deciding; avoid significance claims from tiny cohorts. Segment by platform + verified asset_id, browser/device, and 7/30-day lag without collecting user PII. If no merchant/order-level attribution to an arm is independently available, the paid-conversion A/B outcome is **UNMEASURABLE**, not a win from clicks.

## 3. Event specification for Claude; paper schema, no installed tracking

| Event | Evidence source | Required non-PII fields | MUST NOT be called |
|---|---|---|---|
| `qualified_human_landing` | first-party privacy-safe analytics, after reasonable bot/internal filtering and consent | time-window, verified `asset_id` in approved allowlist, `utm_source`, `utm_medium=organic_social`, `utm_campaign`, path, arm, aggregate human-qualification version | a lead or a purchase |
| `article_to_focus_click` | existing site first-party event if observable and approved | aggregate session/asset campaign, destination, arm | confirmed subscriber |
| `provider_confirmed_lead` | actual Jetpack/Dispatch provider confirmation with lawful consent | confirmed aggregate count by cohort; only join to campaign if an approved, privacy-respecting mechanism supports it | a sale or anonymous inferred impression |
| `affiliate_outbound` | **only after actual approved URL activation**, first-party click event | approved offer ID, source campaign, arm, time bucket | merchant purchase |
| `merchant_confirmed_paid_purchase` | authenticated Payhip/merchant order/affiliate report | opaque merchant order reference retained in restricted accounting, sale/commission amount, FX/tax context, sale date, attribution confidence | inferred from browser visits or CTA clicks |
| `merchant_settled_commission` | trusted merchant settlement statement | paid/cleared amount net of reversals | advertising gross |
| `refund_or_chargeback` | verified commerce settlement or reported return | refunded amount/fees/period | negative site click |
| `realized_net_revenue` | reconciled settlement minus fees/refunds/chargebacks and applicable charges | net currency and cohort reconciliation metadata | gross checkout intent |

**No emails, names, phone numbers, personal order IDs, IPs, cross-site fingerprints, or exact location in analytic payloads.** Merchant order identifiers, if legally necessary for bookkeeping, remain in restricted accounting and not events. Consent and attribution joins must be documented before implementation. Use `utm_source=tiktok|youtube|instagram|facebook`, `utm_medium=organic_social`, `utm_campaign=mind_gorilla_2026_11` only on a verified genuine asset, and `utm_content=<actual_grok_asset_id>` copied from Grok/Praxxis; never invent a published media ID. All proposed labels are examples, not deployed tracking.

**KPI equations** for approved 7- and 30-day cohorts:
- `net_revenue_per_1000_qualified_human_sessions = 1000 × realized_net_revenue / qualified_human_sessions` if denominator > 0 and net revenue independently reconciled.
- `paid_conversion_rate = merchant_confirmed_paid_orders / qualified_human_sessions` only with compatible attribution and period.
- `confirmed_lead_to_customer_rate = paid_customers_with_verified_join / provider_confirmed_leads_with_verified_join` only when the join is lawful and observable; otherwise report unknown.
- Keep refund rate, chargebacks, fees, unattributed revenue and source-confidence flags separate. Empty or unverified numerators/denominators ⇒ **NOT COMPUTABLE**. Do not substitute zero or clicks.

**Existing baseline from #820:** earlier WP/Jetpack metrics included anomalously many views per visitor and too few attributable Focus visits. This is not current qualified-human traffic. Do not present views or followers as sales.

## 4. UX, SEO and accessibility acceptance

Source-only pages are `noindex,nofollow`; public indexing is founder-controlled. The CSS is self-contained, no remote fonts or JavaScript. Mobile single-column layout applies before 720 px. Check actual screenshots/keyboard/touch at widths 360, 390, 768, 1440, 1920. Run axe/WCAG 2.2 AA, contrast inspection, reduced motion, slow network, no-JS, screen reader and native disabled CTA; establish LCP, INP and CLS on both variants *after* an actual video asset exists. Film cost budget: poster should be small, lazy; video must be `preload=none`, opt-in controls, transcript/captions, never forced playback. Stop if B harms performance, accessibility or trust.

FTC acceptance: reviewer sees plain prospective commission disclosure **immediately adjacent to the disabled merchant button**. Upon eventual authorized active link, test the same real visible disclosure at the moment of choice on desktop and phone, not merely the global disclosure page. This is the FTC's clear/conspicuous material-connection principle, not legal approval. Explicitly reject “guaranteed focus”, “one hour in twelve minutes” as independent claims, clinical benefit, diagnosis and wealth promises. The research narrative must never become a backdoor endorsement.

Security: zero scripts, iframes, embedded third-party media, new forms, auto-redirects, outbound merchant href, cloaking, query injection, and no secret values. On WordPress integration, re-review sanitized content and links in staging; original source-only HTML is NOT an installed CMS draft.

## 5. Source and permission ledger

Read on 2026-11-14:
- Research: https://doi.org/10.1068/p281059 ; https://doi.org/10.1068/i0386 ; https://pmc.ncbi.nlm.nih.gov/articles/PMC3964612/ ; https://doi.org/10.1177/17470218211064903 .
- Seller exact offer and catalog: https://zen12.com/ ; https://inspire3.com/ ; https://hypnosislive.com/ ; https://brainwaveshots.com/ ; https://affiliates.inspire3.com/ .
- FTC disclosure/health rules: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .
- Existing FV: https://finalvestige.com/focus/ ; https://finalvestige.com/dispatch/ ; https://finalvestige.com/2026/11/02/change-blindness/ ; https://finalvestige.com/2026/11/02/mesmerism/ ; https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ (HTTP 429 when directly inspected). Issue #171 inventory says 61 published investigations; this run sampled and reviewed relevant live content, not all 61 individual posts.

**Approved affiliate swipe/creatives:** none authenticated. Do not adapt vendor ad copy beyond factual package description; all hero, micro-story, film poster and buyer copy here original.

## 6. OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

| Offer | Funnel step | Blocker | Change / experiment | Present evidence | Owner |
|---|---|---|---|---|---|
| Zen12 Premium | Approved commission | Named acceptance, terms, URL and checkout unknown | Verify actual partner dashboard and permitted website/video/email channels | **HOLD** public portal is insufficient | Founder/Commerce |
| FV-owned Mind product | Paid order | No authenticated SKU, rights or paid receipt | Audit paid inventory, product/delivery/refund rights; choose only an actual sellable SKU | **HOLD** free Focus is not paid | Commerce |
| Grok Mind clip | Qualified visit | Real media ID, hook and mobile URL unverified | Praxxis verify 3 live assets, not take over Grok production | **UNKNOWN** no claimed asset attribution | Praxxis/Grok |
| Live article | Confirmed lead | Jetpack form attribution/delivery not validated | QA existing single list only with provider confirmation | **UNTESTED** no synthetic subscribers | Claude/Dispatch |
| Zen12 buyer A/B | Paid conversion | B storyboard only, no approved merchant URL | Encode B after approval, browser/performance review, balanced trial | **SOURCE-ONLY** no outcome | Mind/Site QA/Claude |
| Any paid offer | Net realized revenue | No attributable merchant settlements, refunds, fees, qualified denominator | Reconcile 7/30-day cohorts via accounting | **NOT COMPUTABLE** | Commerce/Claude |

## 7. Isolation and ownership handoff

Files are proposed in new `mind/r384/` path only. Main/homepage PR #49, art #150, Mind hub PR #172 and Dispatch #174 are protected. Site QA #126 should review structural claims, research citations, A/B parity, accessibility, and link safety. Art #150 can review only the *idea* of a homepage Mind portal in a separate branch; no changes here. Dispatch #174 should not insert a merchant offer in email until explicit channel permission and an approved live guide are verified. Praxxis Task-008 is for independent creator asset match, no social queue edits.

After exact branch SHA finalization, record comparison and actually run reproducible checks, distinguish executed from untested, and log receipts in GitHub Issues #171 and #820. No live CMS write, newsletter send, social publication, merchant connection, merge or deployment.
