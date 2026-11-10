# Mind R264 — single-offer conversion acceptance and research/QA handoff

**Date:** 2026-11-10 (Pacific)  
**Scope:** Mind & Perception ONLY. Unpublished source-only experimental artifacts. No production writes, affiliate activation, email sending, social posting, analytics installation, paid service, deploy, or merge.  
**Governance:** [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), business charter #818, homepage PR #49, Mind hub PR #172, art lead Issue #150, Site QA #126, Dispatch #174.

## P0 decision: commercial authorization is the bottleneck

An isolated extra presell page will not produce realized revenue unless a payment-ready, rights-cleared offer is verified. The **current sole conditional partner product** is **Zen12 Premium**, not a claim that we are approved to promote it.

**Already inspected seller pages:** [Inspire3 catalog](https://inspire3.com/), [Zen12 standard](https://zen12.com/?no-popup=1), [Zen12 promotional version](https://zen12.com/secret/). The standard and promotional pitches differ in price framing and urgency; do **not** reproduce the promotional coupon/timer or assert that either is the authenticated price/approved Final Vestige offer. The official catalog also mentions Hypnosis Live and Brainwave Shots; those products have distinct sales pages and permissions and are **not** substitutes for a verified Zen12 affiliate agreement.

The research register contains named independent studies and separate seller-claim categories. None of the perception studies tested Zen12. Do not inherit a seller's assertions about an hour-equivalent meditation, instant clinical benefit or wealth. Read FTC [Endorsement FAQ](https://search.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) and [Health Products Compliance Guidance](https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance) before any final wording.

**Named publisher acceptance, issued tracking destination, website/social/email permissions, authentic checkout details, returns and commission settlement feed have not been evidenced.** All 16 inherited gate identities remain hard hold. This is an evidence-status report, not evidence of refusal or zero commissions.

An FV-owned paid Mind digital SKU would be a better near-term fallback **only if** the actual file, third-party rights, storefront checkout, publisher permission, delivery, current price, refunds and payout records were authenticated. Existing Products 001–015 and Payhip have been mentioned in strategy, but a matching paid Mind SKU was **not independently confirmed this run**. Do not fabricate a new shop product or point readers at an unverified listing. The [52-page free Focus Fieldbook](https://finalvestige.com/focus/) remains the only verified Mind offer for immediate reader use.

## High-intent visitor to one concrete decision

**Audience:** English-language, organically acquired readers who already want to start a short focus/meditation routine and are actively deciding between free tools and a structured guided-audio library. This is *not* the entire paranormal/mystery audience. Avoid putting a generic Zen12 CTA on unrelated investigations.

**Commercial question:** “Is a structured 12-level/48-audio library worth paying for if the available free alternatives meet my needs?”

**Reader benefit before any purchase:** explicit seller-described package, no claim of personal testing, a no-cost seven-session logging experiment, a plain account of missing product-specific evidence, comparison against a free timer, current-price/refund cautions and disabled CTA beside a prospective FTC disclosure.

**Existing comparison:** R257's optional 42-second film was rendered locally for review but not hosted. New R264 Variant A is a text-only buying guide; Variant B includes the same copy plus an optional silent original SVG poster and 7-part transcript representing 42 seconds; no embedded video or forced playback. The original R257 media should be reused only after rights, performance, browser, captions, mobile and production release checks. No expectation that B wins. No one is exposed to an actual A/B trial yet.

## Creator-topic-to-product fit matrix (research-only, NOT posting instructions)

| Proposed already-existing social topic to verify | Source-supported hook (not a quotation of Grok's published copy) | Current article destination | Authentic media ID/date/rights/mobile URL | Existing Focus/Dispatch journey | Conditional product fit |
|---|---|---|---|---|---|
| Change blindness | “A person can change during a conversation and the witness may not notice; how did researchers know?” [Simons & Levin 1998](https://doi.org/10.3758/BF03208840) | [Published change-blindness article](https://finalvestige.com/2026/11/02/change-blindness/) | **UNVERIFIED** — request actual published asset ID and safe link from Praxxis/Grok TASK-008 | Readers may independently choose [Focus Fieldbook](https://finalvestige.com/focus/) and existing [Dispatch](https://finalvestige.com/dispatch/) | Zen12 only for separate reader interest in choosing audio; never infer study supports product |
| Invisible gorilla / experts | “Twenty of twenty-four radiologists did not report an unexpected gorilla inserted in a lab CT task; does that prove expertise makes you blind?” [Drew 2013](https://pubmed.ncbi.nlm.nih.gov/23863753/) and [2024 review](https://pmc.ncbi.nlm.nih.gov/articles/PMC10973299/) | **R264 scientific article UNPUBLISHED**; no live link or false landing | **UNVERIFIED** | Existing free Focus; preserve no mandatory signup | Zen12 would be a separate comparison article ONLY, never a treatment for inattentional blindness |
| Attentional blink | “A second target can go unreported shortly after the first; timing and task matter.” [Raymond et al.](https://pubmed.ncbi.nlm.nih.gov/1500880/) | **R263 scientific article UNPUBLISHED**; use a verified published destination or HOLD | **UNVERIFIED** | Existing free Focus | Only a separate high-intent audio-buying guide when verified; intensive training findings must not transfer |

Historical Puységur can be included as an **editorial** route when an actual Grok asset is documented: [official FV Puységur archive](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/). Hypnosis Live requires a separately audited exact merchant sales page and channel permissions and is NOT ready to activate.

**Praxxis/Grok TASK-008 data request (research, no queue writes):** for each *already published* matching clip, return exact platform, URL, immutable media/asset ID, publish date, recorded hook/caption, asset rights, current tagged destination, signed-out iOS/Android destination and any evidence of genuine human referral. If no matching asset exists, record **NO MATCH**, not an invented planned publication. Grok retains content and posting; Praxxis independently QA's links. Do not interrupt current priority assignments.

## Proposed existing-first attribution contract

No additional script or paid vendor is authorized. Claude/analytics owner should first inventory current native Jetpack, Ahrefs and any existing WP event mechanism. Proposed names/fields are a **contract**, not events that have been installed:

| Event / stage | Required observation | What must NOT count |
|---|---|---|
| `campaign_landing` | Existing-consented first-party session at article/offer guide; `utm_source`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, `utm_content=<verified_asset_id>`, `landing_path`, `variant` (A/B when real assignment exists) | Bots, testing traffic, unmatched or invented asset IDs |
| `resource_click` | Reader clicks to existing /focus/ | NOT a verified lead |
| `confirmed_signup` | Provider-side confirmed opt-in transition, appropriate consent, duplicate-safe record; **no raw email or PII in analytic event** | Gift UI, `?subscribe=`, PDF downloads, button clicks, unconfirmed states |
| `affiliate_click` | Only a later **approved** earning-link outbound event after explicit partner/permission/consent checks | NOT commission, order, customer or settlement |
| `verified_paid_order` | Authenticated merchant order marked paid; scoped source/attribution matched without PII exposure; refunds pending flagged | Checkout starts, page visits, affiliate outgoing clicks |
| `cleared_affiliate_commission` | Authorized merchant network export showing an eligible cleared commission, with audit period and deductions | Pending, clicked, assumed EPC or published vendor conversion claim |
| `realized_net_revenue` | Settled product receipts or cleared commissions minus merchant/platform fees, refunds, chargebacks and applicable attributable costs | Gross revenue or clicks described as net |

**Security/privacy:** only aggregate anonymized metrics, no visitor-level joins in public dashboards, no fingerprinting, no session replay, no raw email, no full query strings with personal information, no silent consent bypass. Standard UTM query values are human-readable campaign metadata, not secrets or identity keys. Log version and owning backend for every metric.

**Critical new false-positive guard, documented by Dispatch R253:** existing Focus gift UI can be revealed by an arbitrary nonnegative `subscribe` query or `is-subscriber` class. This is a UI presentation artifact, not provider-confirmed consent. An `affiliate_click` is not an order, just as a gift reveal is not a subscriber. [Original coordination note](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820#issuecomment-6764124130). Separate this source audit observation from independent live subscriber testing.

**North-star KPI:** `realized net revenue / qualified human sessions × 1,000`. Only compute for 7- and 30-day cohorts when actual qualified-human denominators and independently paid/settled monetary records are available. Use **NOT COMPUTABLE** when missing; use tiny-sample warnings and report all raw denominators. A/B evaluation pre-registers merchant-confirmed paid orders per qualified human session; micro-signals are diagnostics. Randomization, assignment persistence, both variant eligibility, single counted sessions and consent need design/QA before trials; no statistical significance assertions until adequate real exposure.

## P0–P3 OFFER → STEP → BLOCKER → CHANGE/TEST → EVIDENCE → OWNER

| Priority / offer → funnel step | Blocker | Planned isolated change or decision test | Pass/fail evidence needed | Owner |
|---|---|---|---|---|
| **P0** Zen12 → real merchant | Named affiliate acceptance, channel rights, exact issued URL absent | Review partner dashboard/approval notice and promotion terms (not generic emails) | Verified publisher name + account-issued URL + terms; **HARD HOLD** | Founder + Mind; partner |
| **P0** FV-owned paid Mind SKU → actual checkout | Authentic current rights-cleared SKU/fulfillment not established | Commerce read-only inventory of all paid products, inspect best Mind fit before speculative new build | Exact SKU, rights, checkout price/fees/refund/delivery evidence; **UNKNOWN** | Founder + Commerce |
| **P0** Zen12 presell → buyer confidence | Divergent seller landing terms, science ambiguity, disabled CTA | A vs B source-only guide; confirm copy against actual authorized destination only after approval | FTC wording, seller/price/returns crosswalk; **SOURCE DRAFT ONLY** | Mind + independent editorial QA |
| **P0** CTA click → paid conversion | No order/commission evidence | Design event contract; request merchant settlement data from authorized account | Merchant-confirmed paid orders, refunds, net; **NOT COMPUTABLE** | Commerce + Claude |
| **P1** Focus lead → confirmed signup | Gift UI query is spoofable | Provider confirmation audit; preserve one signup/list/welcome | Confirmed opt-in transition, consent, dedupe; **NOT TESTED here** | Claude + Dispatch |
| **P1** Grok media → appropriate article | Genuine media IDs and linked destinations unavailable | Check existing TASK-008, no publishing | Asset ID/date/rights/typed URL, signed-out mobile 360/390px, actual consented sessions; **UNVERIFIED** | Grok + Praxxis |
| **P2** A vs B video experience | Video not hosted, missing independent a11y/browser/hosting QA | Test no-JS, text parity, screen reader, 42s captions, poster, LCP and consent on isolated staging | 360/390/768/1440/1920, forced-colors/200% zoom, keyboard; zero auto-play; **NOT RUN** | Site QA + Claude |
| **P3** Navigation/funnel coherence | /mind/ remains source-controlled and PR #172 not merged | Assess four-stream hub with actual nav/flagship owner | Editorial approval and founder release only, link audits; **NO LIVE CHANGE** | Homepage art #150 + Site QA |

## Specific test matrix and stop conditions

Run `node mind/r264/test_r264.cjs` in a trusted checkout for static fail-closed validation; compare A/B buyer content with film removed from B, confirm identical disclosures, button disabled, only approved external source links, and zero form/script/video/iframe/merchant tracking. Run negative mutations (remove disclosure, activate button, add tracking purchase URL, invent conversion, create email capture, insert video autoplay, mark one gate ready or alter gate identity). This is useful source verification, **not** proof of WordPress sanitizer behavior or commercial authorization.

Then independent review in actual browser/WordPress staging—**no production CMS writes**—with keyboard, focus, contrast, screen reader, reduced motion, non-JS reading, responsive overflow, SVG accessible description, caption equivalence, external-source link intentions, CPC/analytics absence, privacy posture and safe screenshot evidence. Verify selected film binary hash/duration/0 audio and hosted format only if/when release requested.

**HARD STOP:** any unsupported medical/wealth or equivalent-meditation claim; an active merchant URL without named publisher approval; exposed customer PII; a second signup stack; auto-starting video; broken destination; missing proximate disclosure; swapped seller price/offer; unconfirmed subscribed UI represented as lead; an outbound click represented as sale; a purported revenue KPI without merchant records.

## Owner handoff & rights

**Mind** owns source science, product truth, presell variants, disclosure and commercial gates. **Claude** owns underlying website and analytics engineering. **Dispatch Issue #174** owns six editorial emails and Jetpack delivery; **do not** edit or schedule any issue or the existing Focus welcome. **Grok** owns creation/posting; **Praxxis** investigates existing assets and signed-out destinations. **Homepage Issue #150 / PR #49** owns art; **Mind hub PR #172** remains canonical candidate; **Site QA Issue #126** performs independent checks. **Founder** approves release and spend.

No current published conversion experiment, merchant link, settlement proof, generated contact list, new instrumentation or live navigation is authorized.
