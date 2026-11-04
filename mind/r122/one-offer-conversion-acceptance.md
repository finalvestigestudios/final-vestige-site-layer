# Mind R122 — One-Offer Conversion Acceptance and Release Dossier (UNPUBLISHED)

**Date:** 2026-11-04 PT. **Owner:** Mind & Perception only. **Status:** Built as isolated candidate; not approved for WordPress, mailing, affiliate or social release. **Canonical coordination:** [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), business charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Dispatch [#174], homepage art [#150], QA [#126], Focus [#129]. Preserve #49 and existing /mind/ PR #172.

## 1. Commercial decision before creative

**Specific possible buyer:** an adult who already wants a short, repeatable meditation-audio routine, is willing to pay for convenience/variety and wants to know whether a bundled MP3 course is materially different from free listening. This is **not** everyone who views a visual-illusion video. Curious visitors do not equal purchase-intent visitors.

**Single candidate:** Zen12 Premium, as described on the exact /hnp merchant page. Eligibility = **HOLD**, not “approved affiliate.” Its packages and different promotional pages have visible price variance ($87.99 vs conditional $37), but neither is verified at FV buyer checkout. The seller's description of files is a factual claim about its own inventory, not our first-hand possession of the files. The advertised 60-minute-equivalent effect and disease/brainwave claims are not established by the reviewed product-specific literature. No merchant offer anchor in the draft and no order-taking by FV.

**Fallback:** an existing FV-owned, rights-cleared paid Mind SKU would be preferred for immediate revenue testing *only after* seller-authenticated Payhip product ID, license/rights, listing status, exact price, tax/return terms, fulfillment test and settlement evidence are available. No such specific SKU is verified today. The published 52-page Focus Fieldbook is a **free** resource and must not be mislabeled as a paid SKU. Public search/Gmail absence is not proof there are no orders.

**Why this sprint's guide is different:** previous R114 buyer guide and R121 insert mainly assessed claims. R122 adds the easy-to-miss **safety and preference-experience boundary**, grounded in adverse-event reviews, and defines measurable acceptance criteria. R122 is an **alternative experimental wrapper**, not a second canonical public page; product owner chooses one canonical guide later. All other drafts stay unmerged.

## 2. Specific offer → step → blocker → change → evidence → owner

| Rank | Offer and funnel step | Actual blocker | One next change or experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 / approved referral link → merchant-confirmed order | No documented named FV partner acceptance, promotion channels, affiliate URLs, privacy-safe reports, checkout total | Send prepared R116 merchant questionnaire **only when founder approves outreach**, get accepted account ID (kept private), exact authorized URL and aggregate-only reporting agreement | **HOLD**. Public signup portal ≠ named approval; Gmail targeted searches surfaced promotional messages, not qualifying acceptance | Founder/commerce; Mind evidence |
| P0 | FV-owned paid Mind product → paid checkout | No authenticated rights-cleared paid SKU | Commerce/Claude read-only seller audit: exact Payhip SKU, permissions/rights, price/fees, delivery, refund, test order under approved conditions | **UNVERIFIED**; never infer no sales from no Gmail matches | Commerce/Claude |
| P1 | Creator video → qualified site session | No reconciled Grok asset ID, post URL, permission inventory or observed human denominator | Praxxis obtains actual immutable IDs under TASK-008; Claude QA maps permitted platform CTA and first-party visit | **NOT OBSERVABLE** | Grok creates/posts; Praxxis QA; Claude attribution |
| P1 | Read guide → informed optional Focus/Dispatch lead | No attributable confirmed lead count, no buyer-specific interest validation | Site QA checks existing /focus/ in staging/browser; verify single Jetpack list, actual confirmation & welcome without unapproved subscriber creation | **LINK CONFIRMED BY WP READ; VERIFIED LEAD MISSING** | QA/Dispatch |
| P1 | Eligible offer view → authorized CTA → checkout | Merchant terms and source-level approval missing | Keep buyer controls natively disabled until written permissions; after approval conduct one browser end-to-end checkout QA without purchase unless founder authorizes | **CLOSED CTA** | Mind/Claude/QA |
| P1 | Purchase → settled revenue | No joined merchant order/refund/fee records to qualified-human sessions | Commerce reconciles source-of-truth seller/affiliate paid reports with dated cohorts | **NOT COMPUTABLE** | Commerce/#820 |
| P2 | A text guide vs B guide + optional 40-second original film | No playable accessible media, tests or sale data | Compare only film variable; review 360/390/768/1440/1920, no-JS, captions, performance, conversion after release approvals | **STRUCTURAL ONLY; NO TEST OF EFFECTIVENESS** | Mind/QA |

**Non-negotiable:** an outbound “affiliate_click”, “checkout_start”, opt-in or even a merchant “pending order” is not a reconciled paid commission; a seller-reported purchase pending return window is not necessarily realized net revenue.

## 3. Three creator-topic paths, reconciled to actual public destinations

The paths below are **proposals to QA against existing Grok media**. The exact media IDs, publication times and platform destinations are unknown. Do not assign fake asset IDs, dictate scripts or change Grok's queue.

| Evidence-supported viewer question and potential hook | REAL published first-party destination | Reader action | Optional buyer guide fit |
|---|---|---|---|
| “Why didn't I notice that an entire object changed?” (Change Blindness; no false claim that everyone fails) | https://finalvestige.com/2026/11/02/change-blindness/ | Follow original evidence; optionally visit https://finalvestige.com/focus/ | **Weak to medium.** Do not force a Zen12 offer on pure curiosity; use independent buyer guide only if visitor explicitly seeks audio practice |
| “What did Franklin's investigators find when they tested suggestion?” (Mesmerism) | https://finalvestige.com/2026/11/02/mesmerism/ and https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Follow the historical source trail; optionally use Focus | **Weak.** Historical hypnosis is NOT proof of Hypnosis Live efficacy; no forced merchant recommendation |
| “Can noticing distraction become a practice?” (mind-wandering/self-observation; connect to existing Focus, not a fictional article) | https://finalvestige.com/focus/ (published). Proposed R122 research manuscript **UNPUBLISHED** | Try free Focus Fieldbook on the single existing list | **Potentially strongest** *once buyer intent is independently observed*. If merchant authorized, guide to seller-described 12-minute audio package; if not, maintain free-only |

**Grok handoff:** Before launching anything, reconcile with original [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit) and [Praxxis dated handoff](https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit). Needed fields: real platform, real unique asset_id, post permalink, date, rights status, permitted link path and verified link clicks/landing sessions. Until then no claim of an implemented campaign.

## 4. Attribution contract, not an extra tracker

Use existing first-party/Jetpack infrastructure, subject to Claude/#820 review. Do NOT add GA, pixels, fingerprinting, geolocation, query-string email, new scripts or a second email form.

Proposed canonical tags for a genuinely posted Grok asset, where platform features allow:
- `utm_source=tiktok|youtube|instagram|facebook|pinterest|x|bluesky` (real platform only)
- `utm_medium=organic_social`
- `utm_campaign=mind_audio_decision_pilot_2026_11`
- `utm_content=<actual immutable Grok asset_id>`
- first-party landing = **existing verified live public page**, never an unpublished /mind/ or R122 draft.

For platforms without clickable caption links, document profile/bio route and resultant attribution uncertainty. No deceptive redirects. Sources, article visit and CTA may be observable separately; **qualified-human sessions** require Claude's documented bot/internal-traffic exclusion method, not raw Jetpack views.

An aggregate 7/30-day record must include: immutable campaign identifier (not visitor fingerprint), dates/time zone, qualified human sessions with method/confidence; optional confirmed lead count with confirmation method; clicks on a vetted offer; independently merchant-reported paid orders and commissions; refunds, transaction fees, chargebacks/adjustments, unsettled pending amount; observed net revenue. Distinguish unknown attribution, missing merchant report and zero in the denominator. Do not store buyer names, emails, IPs, addresses, or individual transaction IDs in a public repo.

**Primary KPI:** realized net revenue per 1,000 qualified human sessions = (settled, attributable paid receipts minus refunds, fees and chargebacks) / qualified human sessions × 1000. Report noncomputed, never zero, if denominator/settlements/attribution missing. Also report purchase conversion rate, paid customer count, lead-to-customer when joins legitimately authorized and observable. Small samples are descriptive, not statistically proven.

## 5. Controlled comparison and usability gates

**A:** evidence-first text guide with exactly one active internal free Focus CTA, disabled merchant button, and one intact source trail. **B:** identical HTML/CSS/copy except one clearly marked **optional forty-second original film storyboard**. B's poster is CSS, its six timed captions form the complete transcript, its disclosure and disabled purchase controls are identical to A. No video was filmed, hosted or played. Therefore no claim yet of video engagement or accessibility.

Hypothesis: original video may help readers understand why a product benefit must be separately evidenced, potentially improving *informed consideration* **without** increasing misleading impressions or page weight. It could just as easily distract, hurt LCP or reduce intent; A is fully usable without JS. Do not report A/B uplift until traffic is randomized ethically, comparable 7/30-day cohorts exist and merchant sales can be reconciled. No fake scarcity, false countdown, urgency or user testimonials.

**Pending live QA:** semantic headings; keyboard; screen-reader and focus behavior; portrait 360/390; tablet 768; desktop 1440/1920; WCAG 2.2 AA contrast, touch targets, reflow, reduced motion, link context; no-JS; no autoplay; VTT and real-media poster rights if actual film is produced; CSP/rel on external links; no user identifiers in requests; lighthouse/CWV and media byte budget. Current checked items are **source structure**, not browser-tested conformance.

**Measurement acceptance:** same client-side scripts = none. Film B added static markup only; if a future real clip exists, use native video `controls`, `preload="none"`, a rights-cleared local poster, `<track kind="captions">`, readable transcript, opt-in play, no automatic streams, no requests before selection. Version A must remain independently useful.

## 6. Permission matrix

The following must be documentary evidence **before** any earning link exists publicly:
1. Accepted FV account and named relationship + permitted domains/caption/email channels.
2. Authorized URL with link-tag rules and no impermissible redirection, masquerading or altered coupon.
3. Approved creatives and exact merchant offer version (no copied swipe).
4. Refund, final price, tax and upsell disclosures independently checked at checkout in a controlled QA session.
5. PII-minimized **written** referral reporting agreement resolving Inspire3 policy allowing names/emails/product details to affiliates.
6. FTC adjacent connection disclosure on guide and any affiliate-containing outbound channel, product-specific claim substantiation, accessibility, privacy review.
7. Founder approval for staging/prod, independent QA and rollback, Grok posting approval, Dispatch owner coordination; no modification of live welcome message.

**Email request:** R116 merchant questionnaire exists as an unsent draft; do not repeat or send it automatically. Do not create a new email list or send to subscribers. Dispatch #174 owns email content, not this lane.

## 7. Exact link/navigation proposal, NOT live edits

- Future /mind/ library feature: “The attention you think you have” → actual Change Blindness article (published).
- “How suggestion became a research question” → the published Puységur archive and Mesmerism article.
- “A quieter comparison before buying an audio routine” → the existing /focus/ first-party free page and only then the independently vetted, separately disclosed guide.
- “Tools under review” independent buying section clearly differentiated from archive conclusions. It can be reached directly without joining Dispatch.
- R122 manuscript and A/B buyer wrapper are **draft assets**, no live or guessed URL. Preserve approved PR #172 and homepage flagship #49; art lead #150 decides whether/how to integrate any future teaser.

## 8. Material new findings

- Official Focus Shot page discloses 15/30-minute formats; Hypnosis Live Total Focus describes a 33-minute recording. These are **not** interchangeable with Zen12's 12-minute library, and direct copy adaptation would be misleading.
- Public Inspire3 privacy terms explicitly allow sharing buyer identity details with affiliates. Aggregate-only language cannot be assumed from a portal signup.
- Independent research on adverse meditation experiences makes “nothing to risk” style claims unsuitable for an independent guide.
- Targeted Gmail searches on 2026-11-04 found promotional/vendor material but **no affirmative Final Vestige-specific affiliate acceptance** in results; a Gmail search cannot prove none exists in a separate merchant account.
- Authenticated read-only WordPress review confirmed /focus/ page ID1579 and Puységur page ID1377 published and the live Change Blindness post ID1922. No CMS writes made.

**Release decision: HARD HOLD. No WordPress, social, paid product, user data, affiliate, Dispatch, Focus, analytics, email or deployment changes authorized here.**
