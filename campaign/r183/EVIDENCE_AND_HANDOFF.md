# R183 — conversion-first Dispatch handoff · 2026-11-07 · DRAFT ONLY

**Parent:** #1389 at `29a5f095888ccefc3525e947c2f424cfa6c12f05`. **Source of truth:** #174. Commercial owner #171; Focus engineering #129; overarching conversion charter #820. No changes to original six newsletters (#175), per-issue gate (#201), homepage #49 or production.

## High-impact finding: the 3/3/2 counts are not additive
At 2026-11-07 10:36 UTC, the connected Jetpack newsletter status reported **total 3, confirmed 3, unconfirmed 2**, with zero suppressed or paid and the last five posts explicitly held from email. The independent follower endpoint reported **3 WordPress.com followers / 0 email-only followers**. **Do not add 3+2 or infer there are five people**. WordPress's *Manage your WordPress.com subscribers*, last reviewed 2026-11-04, states **Not confirmed requests are not counted toward total**, and Reader subscribers can lack email subscriptions. The 3/3/2 reading therefore does **not prove a contradiction**, but does not settle eligibility: a WordPress.com follower might receive email or might follow only via Reader. The only authorized answer is a provider **Email Subscription: Subscribed** filtered count, excluding **Not confirmed**, **Not subscribed**, **Bounced**, **Emails paused** and **Not sending**. Never expose addresses; verify only aggregated counts with evidence.

**Official guidance:** https://wordpress.com/support/subscribers/ ; https://jetpack.com/support/jetpack-stats/subscribers-stats/ .

## Why this matters commercially
The current public Focus page can show the Fieldbook panel from a permissive `?subscribe=...` client query without any provider-validated confirmation (R182 isolated exact-source proof). This does **not** prove subscription itself is broken. It proves page-visible success and PDF viewing must not emit `confirmed_signup`. The 52-page Fieldbook is configured in Jetpack's welcome, but no genuine delivered welcome is verified. Do not create a new signup list, write a new analytics script, assign a consumer segment, or email a test recipient.

## Event contract: qualified social audience → real opted-in lead → real customer
- Grok produces an allowed source-tagged URL: `utm_source` (platform), `utm_medium=organic_social`, `utm_campaign` (stable cluster), `utm_content` (individual asset_id). Grok owns publishing; Praxxis owns independent QA. No new pixels or duplicate scripts.
- Count `landing_view` only with available privacy-safe, bot-screened site analytics; it is not a paid transaction.
- Count `signup_attempt` only if observing a permitted form-start event is legitimate; attempts are **not leads**.
- Count `confirmed_signup` only once per provider-confirmed, email-eligible consent transition, with authoritative timestamp and an independently verified **opaque event reference**. A server verifier must check provider provenance; a browser boolean, query parameter, CSS class, auto-download, counts delta or self-reported 'confirmed' is insufficient. Never store/report addresses or raw tokens in GitHub/analytics. The included read-only validator returns review candidates, never actual production events.
- Subscriber segmentation remains a **hypothesis** based on voluntary topic interests, not silently inferred from personal data: historical archive; perception/attention; audio buyer-intent. Editorial messages stay general unless consent and actual platform category tools support preference segmentation.
- Email CTA: `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue_0N`; use only after final release review. Preserve first social asset attribution in an approved privacy-safe session model where genuinely observable; email attribution is a separate touch. If unsupported, mark assisted conversion unknown.
- `affiliate_outbound_click` is diagnostic only. Count a sale only with independently reported paid merchant order/commission ID, settlement, refunds/fees and demonstrable attribution. Main KPI `(realized_net_revenue / qualified_human_sessions) * 1000` across 7/30-day cohorts; null if either numerator or denominator cannot be verified.
- Retain one relevant offer after permission is proved; never use an unapproved earning URL or claim evidence based on vendor prose.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → PROOF → OWNER
1. Fieldbook → opted-in lead: page-visible success is not provider truth → distinguish request/pending/confirmed with Claude's signed-out UI engineering → **UNVERIFIED / R182 client false positive reproduced** → Claude / #129.
2. Opted-in lead → Fieldbook welcome: configured message not a received email → read-only authorized received-message corroboration; no test sends → **UNVERIFIED** → Dispatch / #174.
3. Dispatch → actual recipient: native rendering, publisher postal and unsubscribe not observed → native read-only editor preview and address authorization → **UNVERIFIED** → Dispatch / founder.
4. Zen12 commercial issue 03 → vetted buyer guide → official seller https://zen12.com/hnp has 12 levels/48 MP3 and benefit/guarantee claims, BUT no named affiliate email authorization, approved link, live release or authenticated checkout → **HOLD_MERCHANT** → Mind Studio / #171.
5. Total Focus commercial issue 05 → vetted buyer guide → seller https://hypnosislive.com/mental-skills/total-focus describes a 33-min/47MB MP3 and advertises unverified concentration outcomes; current price and refund are not independently verified → **HOLD_MERCHANT** → Mind Studio / #171.
6. Verified order → net revenue: none independently reported → no sales metric until merchant/Payhip settlements/refunds/fees and qualified sessions reconciled → **NOT COMPUTABLE** → Commerce / Praxxis / #820.

## Deliverable and release interpretation
- One **optional, original, historically grounded Issue 04** on Piri Reis, with subject/preheader, accessible static/email-safe HTML *reviewer*, plaintext, original research summary, **one verified live first-party CTA** (post ID 1917) and bibliography to peer-reviewed Guedes (2009). No earnings link. Alternative not approved to replace Apollo 1 in the 4:2 master.
- New **read-only lead evidence validator** and native Node tests cover the WordPress counter semantics, adversarial fake-browser confirmations, privacy sanitization, duplicate event references and fail-closed release logic.
- Exact native Jetpack MIME, inbox preheader, real confirmation/welcome, valid Final Vestige postal address and functional unsubscribe are still not proven. The OFFLINE HTML is not a legal signoff; no A/B, open-rate or paid conversion claim.
- **ALL SIX: HOLD_UNSENT. COMMERCIAL 03/05: ADDITIONAL HOLD_MERCHANT.** No email, test email, newsletter schedule, platform setting changes, subscriber imports, live posts, partner links, analytics deployments or spending authorized.

Official email platform preview: https://wordpress.com/support/newsletter/email-appearance/
FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
FTC endorsement disclosure: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
