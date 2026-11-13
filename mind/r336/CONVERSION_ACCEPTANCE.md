# Conversion-first pilot contract — R336 (unpublished)

**Audience:** A viewer of a *published, source-matched* Final Vestige Mind video who wishes to build a repeatable brief meditation habit, is curious about structured recordings, and wants an evidence-first evaluation before purchase.

**One intended offer, NOT YET ELIGIBLE:** Zen12 **Premium** only, the seller-described full 12-level, 48-MP3 course. Beginner (first 6 levels/24 files) and Advanced (final 6 levels/24 files) must not be mislabeled; no live merchant URL, assumed account approval, guaranteed final price, financial benefit, medical benefit, paid commission or sale. Seller sales page: https://zen12.com/ ; affiliate partner eligibility is an account-specific private check, **not** https://affiliates.inspire3.com/ public recruitment.

**Fallback:** An FV-owned Mind digital product becomes the pilot only after Finance/Commerce authenticates a currently active exact Payhip SKU, Final Vestige ownership or licensed rights, fulfillment, refund terms, test checkout and complete final price. Public listing alone is insufficient. No such SKU authenticated in this sprint; do not substitute an unrelated or third-party listed product.

## Two controlled experiences

A: source-based no-JS HTML guide. B: same exact article, price/refund language, field exercise, tier distinctions, disclosure and disabled offer, plus original optional 42-second film treatment. Current B is an accessible **static poster and transcript, not video**. Before an A/B paid-conversion test, encode an original low-byte WebM/MP4 42s clip, poster and accurate captions; validate normal-control-only playback, no autoplay or preload, keyboard, transcript, screen reader, 360/390/768/1440, reduced motion and no-JS. Compare page load and Core Web Vitals with A. No paid test or tagging until released by founder.

**Hypothesis (NOT a result):** An optional 42s source-reconstruction may improve informed paid conversions among qualified visitors with purchase intent without imposing material LCP/CLS/INP regressions. A can win; beware novelty effects and small samples. Randomize subject to founder consent, avoid persistently identifying visitors; use same offer, same pricing and same acquisition cohort in each arm. Prefer server-side coarse assignment after privacy review; no new tracking vendor or third-party pixels.

## Offer → funnel step → blocker → change/experiment → acceptance → owner

| Offer / step | Blocker | Proposed change | PASS/FAIL evidence needed | Owner |
| --- | --- | --- | --- | --- |
| Zen12 Premium / purchase | Publisher acceptance and issued link absent | Authenticate signed account-specific acceptance, channel rights, commission/tracking terms | Screenshot/export or signed account notice, not inferred from promo email | Founder/Commerce |
| FV-owned Mind / checkout | Rights-cleared active product unconfirmed | Private Payhip inventory audit and controlled checkout QA | SKU ID, ownership/delivery/refund proof; otherwise fail | Commerce |
| Grok Mind / article landing | Exact published assets and allowed click targets unconfirmed | Check TASK-008; no creator queue edit | asset_id, platform public URL, timestamp, CTA placement, exact landing URL and rights QA | Grok/Praxxis |
| Article / /focus/ | Front-end ?subscribe parameter is not proof of consent | Preserve existing one Jetpack form; verify provider-side double-opt-in/confirmation without fake signup counts | Jetpack verified confirmation and delivery test under authorized QA | Claude/Dispatch |
| Guide / offer CTA | No live approved warm-up URL, no merchant authorization | Stage A/B, ensure near-CTA disclosure | Mobile WCAG, no-JS, clean navigation, accurate merchant terms, founder release | Site QA/Claude |
| Affiliate click / commission | Click != sale | Existing privacy-safe first-party event distinct from merchant report | Authenticated merchant commission/order/refund report; no inferred joins | Commerce/Claude |
| Settlement / net | No matching 7/30 cohort data | Ledger monthly/weekly after production approval | Settled order net of refunds/fees + qualified human denominator | Commerce/Claude |

## Three *proposed*, not asserted live, creator-topic paths

1. Change blindness: use only an actual approved Grok post ID, then the **published** https://finalvestige.com/2026/11/02/change-blindness/ → optionally existing https://finalvestige.com/focus/ → Zen12 only if intent is independently demonstrated and link authorized.
2. Mesmerism / hypnotic suggestion: published https://finalvestige.com/2026/11/02/mesmerism/ → public historical https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ → optional /focus/; do not exploit a history audience by forcing hypnosis sales.
3. Attention tests / meditation buyer: only if Grok has an actual published topic-matched video, first an **approved live** source page or guide (R336 remains draft) → existing /focus/ optional → same precise Premium offer, when cleared.

TASK-008 source of truth: https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit ; dated handoff: https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit . **No verified matching post IDs or UTM targets for this sprint.** Do not invent social media URLs. Grok retains full content/posting ownership.

## Measurement (specification only, no deployed script)

Store only valid first-party UTM/source metadata and coarse events under the existing audited analytics implementation:
- \`campaign_landing\` and \`qualified_human_session\`: tag with genuine platform, known asset_id, \`utm_medium=organic_social\`, \`utm_campaign=mind_pilot_2026_11\`, \`utm_content=<actual_asset_id>\`; classify bots/unknowns explicitly. No PII, no custom visitor fingerprinting, no duplicate tags.
- \`article_to_focus\`: existing Fieldbook path click; not a lead.
- \`lead_confirmed\`: only provider-confirmed consent/opt-in; never infer from \`?subscribe\` param or PDF presentation.
- \`guide_view\` / \`affiliate_click\`: separate relevant CTA and outbound event; never substitute for commission.
- \`paid_order_confirmed\` / \`affiliate_commission_confirmed\`: only from authoritative merchant or partner reporting, with reconciliation quality grade. Note when platform-to-merchant linkage is impossible rather than inventing it.
- \`refund\`, \`fee\`, \`chargeback\`, \`net_realized_revenue\`: aggregate consent-compliant accounting outputs; publish only totals if authorized.

Primary KPI: \`1000*(settled sales + paid affiliate commissions - refunds - fees - chargebacks - defensible variable costs)/qualified_human_sessions\`, calculated separately for 7- and 30-day cohorts. Report sample size, consent, incomplete attribution, statistical uncertainty and **NOT COMPUTABLE** if counts/settlement are unknown. Qualified and purchased cohorts must not be mixed carelessly.

## Release protections
Homepage PR #49 and art #150 untouched; canonical Mind hub draft #172 untouched; this new /mind/ candidate is only source-controlled review HTML and NOT a CMS saved draft. Do not edit newsletter issue drafts or replace the current Focus welcome email. No live WordPress/nav/settings, affiliate URLs, social posting, email send, spending, merge, CI release or deployment. Commerce remains HARD HOLD pending verifiable named acceptance + founder release.
