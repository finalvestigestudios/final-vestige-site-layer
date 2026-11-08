# Dispatch R145: Exact-offer clarity, consent and merchant-email permission — UNSENT

**Status: DRAFT ONLY.** Dispatch Issue #174; Mind #171; Focus #129; Conversion #820. Stacked on [R144 PR #1139](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1139), which is stacked on R143. Original approved six-letter *draft* in [master PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175); prior source-controlled release gates in #201. Neither original issue allocation nor any production page, setting or subscriber was edited. PR #49 remains untouched. **Founder has not approved sending.**

## What is new

This branch adds two **optional, non-approved** commercially relevant editorial alternatives for original issues 03 (Zen12 Premium) and 05 (Hypnosis Live **Total Focus**, explicitly not Hypnotize Yourself), plus an independent no-network Python checker and 26 native regression tests. There are no active or disguised affiliate links. Each alternative has an honest subject/preheader, original utility, a single unactivated first-party buyer-guide CTA, disclosure immediately adjacent to the CTA, publisher footer hard-stops, and complete official citations. The copy does **not** claim that vendor marketing promises are independently validated. These are **not** substitutions for the approved 4 editorial / 2 commercial draft slots.

## Official product records rechecked November 5, 2026

* **Zen12 Premium** seller's live page: https://zen12.com/?no-popup=1 describes 12 levels and four styles each (48 MP3s). Its assertion that 12 minutes equals an hour's meditation and claims of guaranteed health/cognitive effects are **seller marketing**, not independently verified outcomes. A seller's free MP3 opt-in includes a separate seller newsletter; never mix that with Final Vestige's Jetpack list. Its displayed price and guarantee are **not verified checkout/fulfillment terms**.
* **Hypnosis Live Total Focus** exact SKU: https://hypnosislive.com/mental-skills/total-focus describes a 33-minute/47-MB MP3 and markets concentration improvement; claims remain seller representations, not independent proof. The seller advertises a 14-day refund period (https://hypnosislive.com/faq), but **checkout pricing, discount and actual refund performance not independently verified**.
* **Affiliate permissions:** public https://affiliates.inspire3.com/ does **not** verify named Final Vestige acceptance, the specific offer link, email promotional permissions, approved creative, commissions, or attribution. Mind Issue #171's R150 authorization inquiry is **unsent**. Until named approval and actual commercial rights are independently attested, all commercial issues remain HOLD_MERCHANT.
* Editorial independence and material-connection rules: https://finalvestige.com/editorial-standards/ ; https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking ; https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance.
* Legal send gate: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://wordpress.com/support/newsletter-settings/ . A service provider's postal address is not evidence of a valid **Final Vestige** postal address. Actual Jetpack rendered unsubscribe remains unverified.

## Native WordPress read-only findings, 2026-11-05T20:31Z

Jetpack newsletter enabled; automatic post email **OFF**; `email_content_format=full`; from name **Final Vestige Studios**, reply-to **no-reply**. Welcome message still contains the established 52-page Focus Fieldbook URL. Native aggregate counts **total 3, confirmed 3, unconfirmed 2**, imported last 24 hours **0** — categories overlap and cannot be summed. No verified subscriber-level email eligibility; an authenticated welcome configuration is not a received welcome. The latest five published-post notifications are `never_sent_opted_out`.

WordPress confirms /dispatch/ (page 523) and /focus/ (page 1579) are published. Their content projections show a Subscribe button/link, but a signed-out functional modal/input journey is not browser-verified. No meaningful WordPress *received email preview*, live footer/unsubscribe, or successful Fieldbook receipt was obtained. No source-confirmed revenue was supplied.

## Conversion-first journey and measurable contract

**Qualified Grok audience** with expressed interest in attention → established Focus Fieldbook on the *same* Jetpack list → genuine provider-confirmed signup **only when a native confirmation and appropriate consent record exist** → evidence-led editorial content → optional **one** Zen12 Premium review guide once Mind verifies eligibility → seller checkout → **independently settled** commission/refund/fee reports. Preserve immutable Grok asset_id / utm_campaign where independently available. Proposed Dispatch URL metadata: `utm_source=dispatch&utm_medium=email&utm_campaign=fv_mind_pilot_202611&utm_content=issue03_zen12_guide`; **not implemented or permitted as an earning URL**. Deduplicate provider-verified confirmed_signup by opaque provider confirmation ID, no raw subscriber email or hash as a click-tracking identifier. No fabricated A/B claims on three reported subscribers. Net revenue per 1,000 qualified human sessions in 7/30-day cohorts = **UNKNOWN / NULL**, *not zero*.

## Offer → Funnel step → Blocker → Change → Evidence → Owner

| Offer → funnel | Blocker | Proposed verification or experiment | Current evidence | Owner |
|---|---|---|---|---|
| Focus → confirmed lead | Native consent and signed-out UI unknown | Read-only status-only recipient reconciliation + signed-out modal QA, no submission | UNKNOWN | Dispatch, Claude, Site QA |
| Subscriber → welcome PDF | Actual receipt and download unverified | Authorized already-received welcome + PDF audit, no new email | UNKNOWN | Dispatch |
| Dispatch → article | Actual full Jetpack preview and final footer unknown | Non-sending native WordPress visual email preview; verify subject/body/disclosure/address/unsubscribe | UNKNOWN | Dispatch/Claude |
| Zen12 Premium → buyer guide | Named affiliate acceptance, email channel rights, approved live guide, exact earning link missing | Mind's source-of-truth affiliate authorization, no direct affiliate email until accepted | HOLD_MERCHANT | Mind #171 |
| Total Focus → buyer guide | Exact SKU rights / current terms / guide missing | Seller/partner claim+permission check | HOLD_MERCHANT | Mind #171 |
| Confirmed paid order → net revenue | No attributed completed/settled orders or qualified-human-session records supplied | First-party/partner payment settlement reconciliation less refunds/fees | NOT COMPUTABLE | Commerce/Praxxis/Claude |

## Independently executable QA

`cd dispatch/campaign-2026-mind/r145 && python -m unittest -v test_merchant_email_contract.py && python merchant_email_contract.py`

The checker cannot send email, mutate live WordPress, or authorize a merchant: it ALWAYS returns HOLD_UNSENT/HOLD_MERCHANT on source-only drafts. It explicitly rejects false/truthy permissions, unsupported promises, missing disclosure, unauthorized links, duplicate CTAs, missing publisher postal/unsubscribe attestation, and fabricated financial outcomes. It does **not** replace the per-edition source-control gate in PR #201 or the received-email QA in PR #1098. Each remaining production gate requires a real source-of-truth record and founder's explicit final approval.
