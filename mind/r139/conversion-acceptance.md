# R139: Conversion acceptance, SKU reconciliation, routing & measurement contract
*2026-11-05 · DRAFT · Conversion-first · No production authorization*

## Executive business decision
**Block affiliate activation; do not block an independent reader's ability to learn.** A public Inspire3 affiliate sign-up portal is not an account approval, an authorized offer URL, approved creative, or permissible channel agreement. A targeted mailbox search on 2026-11-05 returned promotional Inspire3-related messages and no authenticated approval/commission-rights record. Search scope is not proof of non-existence. We have not authenticated any FV-owned rights-cleared paid Mind Payhip item, its current price, delivery, or returns. Therefore **no paid CTA goes live**; we must not claim a sellable fallback SKU from a public search. Known live free destination is /focus/.

## The newly observed exact-SKU mismatch
Dispatch R132 comment in #171 says Slot 05 referenced **Hypnosis Live Total Focus** (33-minute focus/priority MP3) while Mind R137's buyer article reviewed **Hypnotize Yourself** (44-minute instructional MP3). Those are separate products and should not share an earning URL, price, sales copy, or evidence ledger. R139 supplies a source-reviewed Total Focus guide and requests Dispatch to choose the SKU deliberately **without editing its drafts**. Seller exact pages:
- https://hypnosislive.com/mental-skills/total-focus
- https://hypnosislive.com/personal-improvement/hypnotize-yourself
- https://hypnosislive.com/faq

**New price-drift evidence:** the opened first-party Total Focus page on 2026-11-05 showed a single-audio display of $24.44, whereas an older search index view showed $17.95 at the identical URL; other comparative/base prices differ too. Different displays may be dynamic or stale. **Pass**: exact checked-out charge + allowed territory and product configuration verified directly before release. **Fail**: a stale asserted price on any FV pre-sell. The FAQ's 14-day requests have a five-refund-sessions/year limit and payment timing caveats. No refund has been tested.

## Creator-topic → source-grounded offer-fit matrix
| Topic / hook (provisional; Grok retains creative) | Existing first-party destination | Reader's reason to care | Useful free route | Optional guide / precise SKU | Immutable asset ID / measured session |
|---|---|---|---|---|---|
| Change Blindness / “what changed while you looked away?” | https://finalvestige.com/2026/11/02/change-blindness/ (published) | Understand an experimental limit on attention | https://finalvestige.com/focus/ (published; article-body link NOT proven) | Independent Zen12 guide; twelve-minute audio format; NOT a proven remedy | UNKNOWN / UNKNOWN |
| History of Suggestion / “what did Puységur actually document?” | https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ (published) | Investigate historical source and modern comparison | https://finalvestige.com/focus/ (published; article-body link NOT proven) | Independent Hypnotize Yourself instructional guide *only if the intent is learning self-hypnosis* | UNKNOWN / UNKNOWN |
| Attentional Blink / “the second item vanished” | Draft PR #1047, **UNPUBLISHED**, no live destination | Understand constraints of temporal attention and suggestibility | Existing /focus/ only via real navigable approved page | Optional **Total Focus** guide (33m concentration SKU); **not** the instructional Hypnotize Yourself SKU | UNKNOWN / NOT ELIGIBLE TO LINK |

**No Grok media production request or campaign ID invention:** Praxxis/Grok TASK-008 must supply immutable IDs, published URLs, caption/pinned/bio link placements, media permissions, and actual destinations. Existing live Change Blindness and Puységur bodies do not yet have verified embedded /focus/ links; the downstream route is a *proposal*, not verified traffic.

## Presell and funnel gate table (priority order)
| OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Total Focus → affiliate purchase | Named approval, exact SKU, link format, channel and buyer-data terms missing | Keep commercial control disabled; request merchant-specific proof; verify live price/refund terms | **HARD HOLD**; first-party merchant snapshot is not checkout | Founder + Mind |
| FV-owned Mind product → Payhip order | Rights-cleared paid SKU, price, delivery, checkout and refund policy not authenticated | Commerce owner retrieves seller product ID and real fulfilled test-order record if approved | **UNKNOWN** (not “product absent”) | Claude + Commerce |
| Grok asset → site landing | Real immutable asset_id/URL and UTM destination not supplied | TASK-008 source inventory, existing first-party landing rules | **UNVERIFIED** | Grok + Praxxis |
| Article → Focus lead | Link in article body and confirmation mapping not verified | Independent Site QA checks article/referrer/Focus native signup; no test person added without permission | **NOT TESTED end-to-end** | Site QA + Dispatch |
| Guide A versus guide B → paid order | B is storyboard, not playable; approval/checkout unavailable | Treat as preregistered **hypothesis**; do not claim winner; match all text, disclosures, CTA and purchase terms | **Structural drafts only** | Mind + QA |
| Confirmed order → realized revenue | Authoritative settled ledger, refunds, fees, qualified humans not obtained | Reconcile merchant settlement per 7/30-day cohort; no PII | **NOT COMPUTABLE** | Commerce + Growth |

## A/B: text-only vs + optional original video
Both Zen12 variants deliberately share the **same buyer-information** block and **same disabled merchant CTA**. B adds one original 40-second **storyboard** with poster, timed captions and complete text. It is NOT a playable video, does NOT autoplay, does NOT require JavaScript and must not be confused with a completed production asset. B is only a hypothesis that an optional brief attention exercise may increase informed product consideration. It could also distract from the plain evidence or slow mobile load.

**Primary outcome if later released and authorized:** merchant-confirmed paid purchases / qualified human sessions for that buyer-intent cohort, and net realized revenue/1,000 qualified humans, adjusted for refunds/fees. Secondary diagnostic: guide engagement and approved outbound CTA clicks; optional Focus lead confirmed only by Jetpack proof. If assignment cannot be reliably randomized using existing tools without added scripts or consent problems, use a documented sequential design with major caveats; do not assert statistical inference from tiny samples. Do not silently change purchase copy between A and B.

**Performance constraints:** zero new remote fonts, third-party scripts or video players; a real future poster should be compressed, have dimensions, and use lazy-loading only below fold. A real future video must offer click-to-play with browser controls, accurate synchronized captions and full transcript, muted/none by default, non-flashing imagery and reduced-motion behavior. A text-first page must work identically without video/JS.

## Privacy-preserving event contract — specification, NOT instrumented
Inputs: platform-issued immutable `asset_id`, approved `utm_source`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=asset_id`. Allowlist/sanitize values; avoid free-text user IDs, names, emails, payment references, IPs or raw referrer query data. Deduplicate if existing first-party analytics supports a privacy-appropriate event key and proper consent; **do not add a second tracking tag**.

**Distinct states:** `qualified_human_landing` (privacy-safe, bot-adjusted, uncertainties documented); `article_to_focus_click`; `confirmed_signup` (only native verified Jetpack receipt); `offer_view`; `affiliate_outbound` (click only); `merchant_confirmed_paid_order` (settled record only); `merchant_confirmed_affiliate_commission` (independent affiliate statement only); `refund`; `fee`. No front-end event should be named `purchase` solely because a button was clicked.

**7/30-day cohorts:** every unique source/tag and placement must point to the original asset ID and audience-intent page. Aggregate only as authorized. When no merchant reconciliation is available, `paid_orders=null`, `realized_net=null`, `net_per_1000=null`, not zeros. When qualified humans are unmeasured, the denominator is *unknown*; reporting zero revenue per thousand is mathematically false. Conditional formula for valid inputs: `net_per_1000 = 1000 × (settled_revenue − refunded_amount − processing_fees − attributable variable costs) / qualified_human_sessions`. If source-specific revenue attribution is absent, do not assign global revenue to the campaign. Record confidence and sample size rather than a misleading significance badge.

## Source / ownership / release
Official sources in `claim-register.json`; FTC affiliate proximity https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and seller-health-claims substantiation https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance . Public affiliate information https://affiliates.inspire3.com/ does not prove acceptance; buyer privacy https://inspire3.com/privacy/ requires special review. No paid service, duplicate list, new tracking script, email, social post, website menu, CMS write, merge or deploy is authorized.

Coordination for review only: #171 owns presell and claims, #174 owns Dispatch drafts and exact-slot correction, #126 owns real browser QA, #150 homepage art is not to be altered, #820 owns conversion instrumentation, and Praxxis/Grok Drive TASK-008 owns creator IDs. Founder retains all production/spending approvals.
