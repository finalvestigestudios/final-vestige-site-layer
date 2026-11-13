# R336 — OFFER → FUNNEL → BLOCKER → CHANGE → PROOF → OWNER

**Operating priorities:** 1) verified settled net revenue; 2) confirmed consented leads; 3) qualified traffic; 4) vanity metrics only as diagnostics. Source-of-truth #820 and #818. This table is a conditional design, NOT authority to send, publish or change the site.

| Offer → step | Blocker | Change or experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|
| Zen12 Premium → vetted buyer guide → commission | No individualized affiliate EMAIL channel permission, assigned earning link or approved LIVE guide | Secure owner-reviewed permission + live guide link before any offer CTA; keep original slot 03 blocked | UNKNOWN/FAIL; #171 must provide exact account evidence and live URL | Mind & Commerce |
| Total Focus → vetted buyer guide → commission | Generic product framing, varied advertised price, FAQ refund cap, no partner email approval | Optional Issue05 product-specific review and balanced guide; **not adopted** | Static candidate built, terms read; no send authorization, guide or link | Dispatch (copy), Mind & Commerce (eligibility) |
| Grok asset → /focus/ landing | Authentic asset IDs / human-session filtration unproven | Standard source/medium/campaign/content UTM naming without extra measurement scripts | UNKNOWN; no unique published asset-to-purchase chain | Grok/Praxxis/Claude |
| Focus → provider confirmed_signup | Site 3 total/3 confirmed/2 unconfirmed overlap; 3 WP.com followers/0 direct email | Provider-origin opaque subscription ID, verified Subscribed status, consent event, one confirmation event per membership | NOT VERIFIED; do not count PDF click or unconfirmed challenge | Claude / Focus #129 |
| Focus → Fieldbook welcome receipt | Configured 52-page PDF message but none actually observed | Only separately founder-authorized test and private receipt | NOT VERIFIED; Oct25 request was confirmation challenge, not completed welcome | Founder/Focus/Dispatch |
| Dispatch → eligible inbox | Valid FV postal footer and working Jetpack unsubscribe not independently checked | Native post preview and separately approved actual received email, examine sanitized MIME headers/body | NOT VERIFIED, no test emails authorized | Dispatch/Founder |
| Earning click → independently settled commission | Affiliate account report, refunds, fees, currency, order-to-campaign joins missing | Read-only reconciliation with seven/30-day cohorts; no private customer fields in GitHub | NOT COMPUTABLE; merchant click or checkout view is not a purchase | Commerce/Claude |

**A single verified event:** `confirmed_signup` is emitted only from an authoritative provider subscription transition (including an already-verified WordPress account subscribed via provider UI), keyed by opaque provider subscription ID + status-transition ID, deduplicated, with explicit consent provenance. A downloaded PDF, an email entered, a Jetpack follower count, a merchant free-offer opt-in or a welcome-email open is not sufficient.

**Email attribution:** `utm_source=platform`, `utm_medium=email` for Dispatch-owned clicks, `utm_campaign=fv_dispatch_pilot_2026_11`, `utm_content=issue_05_total_focus_review` only on a verified live first-party guide URL. Keep original acquisition asset ID as consent-safe campaign context where possible; don't invent visitor identity stitching.

**Revenue:** `realized_net = settled_payouts_or_sales - refunds - actual_fees - directly attributable cash costs`. `net_revenue_per_1000_qualified_human_sessions = 1000 * realized_net / deduplicated_qualified_human_sessions`. If any inputs unobserved or denominator invalid, output **NOT COMPUTABLE**, never 0. With a handful of followers, no statistically meaningful A/B claim.

**Non-sending progression hypothesis:** welcome + 52-page Fieldbook, then source-led editorial, then at most the founder-approved weekly cadence and eligible commercial content only with active individual permissions. No re-subscribe CTA for existing subscribers, no blanket promotional list blasts.

**Release states:** ORIGINAL 01/02/04/06 and 03/05 = HOLD_UNSENT; 03/05 = HOLD_MERCHANT. R336 alternative 05 = NOT_ADOPTED. WordPress auto post email remains OFF. No permission to spend, deploy tracking, contact subscribers, change settings or send.
