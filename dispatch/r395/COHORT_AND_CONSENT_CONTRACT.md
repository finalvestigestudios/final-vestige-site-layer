# R395 — Grok → Focus → Dispatch → one permitted offer → independently settled net

**Scope:** non-sending analysis contract for a future, fully consented six-week pilot. No new customer records, scripts, vendors or tracking cookies. Owner [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) may implement only after independent release approval; this source-only contract is not authorization to instrument the live site.

## 1. Real-world step, evidence and proof owner
| Funnel step | Grounded positive evidence | Explicitly NOT evidence | Owner / state |
|---|---|---|---|
| Social interest | Grok inventory gives actual published platform link, stable `asset_id`, channel and destination | draft Shorts, invented ID, video views, Grok summary without URL | Grok/Praxxis / UNKNOWN |
| Qualified landing | Claude/analytics audited human session tied to that `asset_id`, `utm_source`, `utm_campaign`, `utm_content` within a real UTC window | raw Jetpack views, referrer guesses, preview QA or bot requests | Claude/#820 / UNKNOWN |
| CTA click | observed click to actual `/focus/` or relevant source article; keep separate from signup | browser event merely saying PDF button shown | Claude / UNKNOWN |
| Confirmed lead | Jetpack provider transition to email `Subscribed`, deduped with *opaque* key, supported consent | pending subscriber, Reader follower, PDF request, existing subscriber stock, confirmation bypass presumed to be new | Focus/#129 / UNKNOWN |
| Welcome/Fieldbook | configured welcome with working PDF plus **actual received final welcome** after provider confirmation | October 25 confirmation mail, mere settings text, public PDF URL | Focus/Founder / UNKNOWN |
| Intent / buyer guide | voluntary, topic-relevant click to published vetted Mind guide | inference from opened email, medical/psychological profile, inactive guide slug | Mind / NOT LIVE |
| Paid commission | merchant's exact issued earning link, settled publisher commission & refund/fee/reversal reconciliation | consumer checkout, coupon page, clicks, alleged payout rate, generic merchant email | Mind/Commerce / UNKNOWN |

One confirmed_signup event must be emitted **only on provider-authoritative newly eligible status transition**, with opaque ID and source confidence. Existing WordPress.com account holders may bypass a confirmation email; **do not treat absence of that message as refusal or as proof of new confirmed signup**. Deduplicate repeats/retries by opaque subscriber and source event ID. Never store list addresses in this repo, event stream, QA screenshots, or issue comments.

## 2. Accepted attribution conventions
Use existing campaign UTM convention from TASK-008: `utm_source` is the actual platform, `utm_medium=organic_social`, `utm_campaign=mind_pilot_2026_11` only when Grok/Claude explicitly approve that exact campaign, and `utm_content` is the real unique asset ID (e.g. the fictional `yt_history_001` in unit tests is **not a real asset**). Never generate a clickable campaign URL from an imaginary video. Track actual bio-link mediation if platform has no tappable caption links, and mark chain broken when original asset cannot be resolved.

For future email guide CTA, only after approval, preserve conventional `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_pilot_2026_11`, `utm_content=issue_03_zen12` or `issue_05_total_focus` as proposed naming; do not claim subscriber identity, send or link exists. The user asked for no duplicate tracking scripts: use standard query args and existing native collection only if verified. Coordinate owners before enabling.

## 3. New failed integrity checks (R394 → R395)
- **Global settlement misattribution:** a real paid commission for another campaign must *never* be divided by this cohort's qualified sessions. Join via actual asset ID, campaign ID, and first-party session timestamp in a 7 or 30 day UTC interval.
- **Conflicting duplicate settlement:** identical repeated source rows may be deduplicated. Same settlement ID with different cents/status is a reconciliation **FAIL**, not a quiet duplicate. A distinct later refund/reversal needs its own immutable merchant settlement ID and the same opaque paid order key.
- **Merchant acceptance is independent:** a public seller price, promo coupon, Limitless Labs swipe pack or consumer receipt is NOT proof of named FV Zen12/Total Focus email rights, issued earning URL or referred terms.
- **Unqualified denominators:** Jetpack pageviews, impressions, bot traffic, zero session denominator and duplicated session report IDs cannot become unique human sessions.
- **Unsettled funnel:** checkout-start and affiliate-outbound events never become paid orders, commissions or revenue.
- **Coherence:** prove the 7/30-day attribution window and separate settlement-as-of cutoff. New refunds may later revise revenue and must be reflected at each future reporting date; no fake finality claims.
- **PII:** raw email, name, phone, IP forbidden in input to the standalone verifier. Reporting is aggregate and small-sample caveated.

## 4. Output rule
`NET_USD_PER_1000_QUALIFIED_SESSIONS = (sum independently settled publisher commissions - refunds - fees - reversals) / validated qualified human sessions * 1000`.
Use integer cents and audited 7/30-day cohorts. **Return NOT_COMPUTABLE** unless both the exact-session cohort and complete independently reconciled issuer/merchant ledger are available and joins succeed. A true $0 requires positive audited sessions plus explicit complete *empty* merchant report from authenticated account; absent merchant rights/report is UNKNOWN, not $0. Count unique paid orders by opaque order key, not settlement rows. Test fixtures may yield fake dollars to exercise logic but are never FV metrics.

**Known current state (authenticated 2026-11-16 05:32 UTC):** Jetpack total 3 / confirmed 3 / unconfirmed 2; WordPress.com followers 3 / direct email followers 0, categories not additive. Zero recent sends (five recent posts opted out). Unique eligible inboxes, actual welcome delivery, real social visits and reconciled publisher commissions remain unknown. Thus current real KPI **NOT_COMPUTABLE**.

## 5. Review / release stages
1. Mind/Commerce supplies exact offer proof and published approved guide, or the commercial issues remain inert.
2. Focus/Founder supplies private recipient status result, actual received welcome and PDF receipt; consent legal reviewed.
3. Dispatch/Founder supplies non-sending native email Preview screenshot and **verified publisher address and functional unsub**, and approves subject/copy per issue. No test send.
4. Grok/Praxxis and Claude supply actual asset inventory and audited source report; merchant supplies settlement export without consumer PII. Independent QA executes this verifier on appropriately **redacted** data in a protected environment.
5. Only founder can give separate final send/audience/schedule consent. No automation or code path sends. All publication/production changes remain held.
