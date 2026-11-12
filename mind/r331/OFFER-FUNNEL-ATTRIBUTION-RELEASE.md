# R331 — OFFER → FUNNEL → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

**Not live.** This is a privacy-first test contract, not a new analytics deployment.

## Three creator-topic paths (Grok owns exact assets/posting)

| Proposed Grok topic | Research destination | Real asset / post proof | Next step | Offer fit |
| --- | --- | --- | --- | --- |
| Attentional blink / second target | Canonical article selected from Mind R327 and older drafts, unpublished | asset_id, URL, platform, post date **UNVERIFIED** | Existing /focus/; optional independent Zen12 tier guide | Medium, not product efficacy |
| Change blindness / changed detail | Verified public FV Change Blindness investigation https://finalvestige.com/2026/11/02/change-blindness/ (published 2026-11-02; mobile link QA still needed) | asset_id and published link **UNVERIFIED** | Existing /focus/; independent audio guide optional | Medium |
| Thatcher illusion / inverted face | One canonical page **not selected** among 20+ draft PRs | asset_id and destination **UNVERIFIED** | Editorial science first, Fieldbook; no coerced product pitch | Low-to-medium |

Praxxis/Grok must verify IDs and approved exact URLs through the existing TASK-008 and handoff docs. No new video, posting queue or CTA placement is approved.

## Attribution contract for Claude (use existing first-party instrumentation, not duplicate scripts)

At permitted link placements use `utm_source=<platform>`, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11`, and `utm_content=<verified_asset_id>`. Avoid manufactured TikTok caption clickability, campaign parameters in cached HTML that leak across visitors, sensitive identifiers, raw IPs, fingerprinting, third-party trackers or cross-site hidden cookies.

Stage event names: `campaign_landing` (qualified/bot-filtered where feasible); `article_to_focus_click`; `confirmed_signup` only from Jetpack/provider evidence; `offer_guide_view`; `affiliate_click` only when verified approved link clicked; `merchant_confirmed_purchase` only from trusted merchant export/report with order ID appropriately pseudonymized; `refund`, `fee`, `settled_commission`. **Never turn a click into a sale.** Do not attach reader email/health or browsing profile to analytics.

If partner reporting lacks per-order asset attribution, mark affiliate revenue `UNATTRIBUTED`; do not fabricate joining keys. Match 7/30-day cohorts only at available authorized aggregate resolution. Net realized revenue = verified settled gross receipts or commission less actual platform/transaction fees, refunds, chargebacks, and any directly attributable costs; avoid assuming zero when missing. Headline KPI = 1000 × net realized revenue / **qualified human sessions** (when denominator measurable), alongside paid conversion rate, confirmed orders, and lead-to-customer rate.

## Controlled A/B: guide A vs guide + optional 42-second film B

**Primary experiment question:** among high-intent *human* visitors arriving from the same verified Grok asset/campaign, does adding a useful, original accessible 42s film to an otherwise identical source guide increase verified **net revenue per qualified visitor**, without harming trust, accessibility or CWV?

**Hold constant:** tier offered (Premium 48 recordings), copy, order page, disclosure, CTA label and placement, source citations, free Fieldbook route, price/return terms and campaign classification. **Change only:** the optional film element. Avoid user-level cross-site identity tracking. Film B is currently a **nonplayable storyboard**. No visitor A/B assignment or real traffic exists.

**Pre-launch PASS** requires: account-specific approval and issued link, explicit permitted media channels, checkout tier/price/returns tested, truthful claim matrix, no-duplicate-list proof, original film rights and accessible captions/transcript, lightweight responsive media with poster and preload=none, keyboard and no-JS usable, 360/390/768/1440 manual browser QA, CSP/security/WP sanitization QA, consent and privacy review, independent site QA, founder release approval.

**Fail if:** an unapproved link activates, seller/brand claims are promoted as established science, subscription gate is coercive, ad creative copied, video autoplays, link changes across variants, responsive navigation fails, or FTC disclosure is hidden.

**Revenue-decision rule:** report cohorts with sampling uncertainty. Do not declare uplift or statistical significance on a handful of orders. Stop or revert only with actual authorized production release process.

## Offer-first plan

| Offer | Funnel step | Current blocker | Change / experiment | Pass/fail evidence today | Owner |
| --- | --- | --- | --- | --- | --- |
| Zen12 Premium | Article → correct tier → settled affiliate commission | No FV-specific approval/earning link/channel permission | Authenticate authorization; stage text vs film | FAIL/HOLD: public enrollment only | Founder/Commerce |
| Existing FV-paid Mind SKU | Mind page → paid Payhip order | Private inventory, rights, delivery unverified | Inspect merchant account; pick only authenticated SKU | UNKNOWN/HOLD | Commerce |
| Existing Focus Fieldbook | Article → optional email opt-in → provider-confirmed lead | Exact campaign/provider linkage missing | Existing Jetpack QA only | UNKNOWN; no second form | Claude/Dispatch |
| Grok content | Verified asset → relevant article | No 3 verified asset IDs | Praxxis/Grok TASK-008 reconciliation | UNKNOWN/HOLD | Praxxis/Grok |
| Commercial outcome | Qualified session → verified paid order → net settled | Transactions/refunds/fees unavailable | 7/30-day merchant/first-party reconciliation | NOT COMPUTABLE | Commerce/Claude |
