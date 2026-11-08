# One offer, one legitimate customer — conversion contract (NO DEPLOYMENT)
Owner: Dispatch consent/attribution planning. Social asset sourcing belongs to Grok/Praxxis TASK-008; Mind Studio #171 owns guide/merchant eligibility, Claude owns production analytics, founder controls releases. This is a **proposal**, not an assertion of capabilities currently operating in Jetpack.

## Audience and optional progression
**High-intent visitor:** watches a specific Grok-created perception or history story; clicks to an already LIVE article; voluntarily opts into the existing `/focus/` Fieldbook and newsletter (optional; free article/guide also accessible without signup); receives an actually confirmed welcome; reads a weekly proof-led Dispatch issue; optionally visits the independently vetted Zen12 buyer guide **only after** authorization and publication; chooses whether to follow an approved earning link; purchase counts ONLY when seller reports an eligible paid conversion; subtract refund and fees from attributable realized commission.
No one is targeted for wellness vulnerabilities, no guaranteed mental improvements, no pressure tactics. **Do not** presume subscribers to history articles consented to promotional serial targeting; check Jetpack consent scope before any promotional send. No unapproved segmentation or new platform.

## Tracking fields (specification; no scripts added)
- Social acquisition: `asset_id` (Grok immutable identifier, NOT fabricated), `platform`, `utm_source`, `utm_medium=social`, `utm_campaign`, `utm_content`, source post URL and click destination; redact all user identifiers.
- Landing: first-party privacy-safe `qualified_human_session`, timestamp, destination and marketing source, based on tested bot/noise exclusion rules; if unknown, do not compute per-1000.
- CTA: `focus_signup_attempt` is a click/form-submit diagnostic, NEVER a lead. `confirmed_signup` is allowed only on *provider-authoritative transition to subscribed*, deduplicated by private stable provider subscription ID (hashing must not leak a re-identifiable email), at most once per active consent episode; suppressed/re-opted-in requires a separate consent episode identifier. A visual URL `?subscribe=pending`, focus download/asset access, CSS class, Reader follow, unconfirmed or aggregate counts cannot prove it.
- Delivery: `fieldbook_welcome_received` only from independently authorized received-message evidence or provider delivery evidence that supports the narrower claim being made; configured text ≠ delivered/read/downloaded.
- Journey: `dispatch_issue` (01–06), `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=fv_dispatch_pilot_2026`, `utm_content=issueNN_primary`, landing guide canonical URL. Use only one primary call to action per issue, no recipient PII embedded in URLs. **Commercial #03/#05 links remain inactive until Mind source of truth is complete**.
- Paid: `order_id` and `partner_conversion_id` retained **only in private permitted accounting**; `paid_conversion` requires a merchant-verified settled order or independently reported paid affiliate conversion. Click, add-to-cart, order-created and email open do not imply paid. `realized_net` is cleared commission (or FV product receipts) less attributable fees/refunds/chargebacks; unresolved pending commissions explicitly excluded. Avoid treating absence of evidence as zero.

## Reporting contract
One 7-day and one 30-day **cohort** measured from first qualified human landing, deduplicated per qualified human session; conversion lookback requires a documented attribution window and independently matchable source/commerce report. Show revenue paid verification, unknown attribution and minuscule denominator warnings. `net_revenue_per_1000_qualified_human_sessions = 1000 * realized_net / verified_qualified_human_sessions`; if denominator or settlement evidence missing, display `NOT_COMPUTABLE`, not $0.00. Never aggregate from scraped click totals into claimed revenue.
A 3-confirmed / 2-unconfirmed / 3-total Jetpack counter snapshot is a **diagnostic only**, not 3 permissioned recipient records or 3 deliverable addresses. No A/B inference with an audience this small.

## Six pilot issues — preserve original allocation
Editorial #01 (perception) → live archival evidence page; #02 (Puységur) → existing primary source investigation (duplicate #01 CTA should be diversified in separately approved copy); #03 (Zen12) → **future vetted warm-up guide, HOLD**; #04 (Apollo) → existing historical investigation; #05 (Total Focus) → **future vetted warm-up guide, HOLD**; #06 (Fieldbook) → evidence log for existing subscribers, avoid redundant re-signup instruction. Weekly sequence is editorial, **not** a native per-subscriber triggered follow-up flow. Replacing any original issue requires separate founder creative approval.

## Prioritized offer → funnel → blocker → experiment → proof → owner
|Offer|Step|Blocker|Proposed specific remedy|Pass/fail|Owner|
|---|---|---|---|---|---|
|Zen12|Permission to guide|No FV-specific acceptance/email right/earning link|Verify written permissions and public qualified page|FAIL: no account-bound proof|Mind #171|
|Focus Fieldbook|Signup → consent|Success panel not provider proof, counters conflict|Provider-filtered aggregate & consent transition validation|FAIL: current proof unavailable|Claude / Dispatch #129|
|Fieldbook welcome|Consent → nurture|Received final welcome unknown|Existing authorized received receipt+PDF inspection|UNKNOWN|Dispatch|
|Dispatch|Email compliance|Own postal line + native preview + functional optout unknown|Native no-send preview, later founder-authorized real delivery|HOLD|Dispatch / Site QA|
|Zen12|Guide → paid buyer|No independently reconciled paid commissions or traffic denominator|Only after legitimate purchase reporting, reconcile with human sessions and refunds|NOT_COMPUTABLE|Commerce / Praxxis #820|

**No automatic sends, no subscriber writes, no live CMS links, no social posts, no production changes, no spending.**
