# R403 · One-offer, non-sending subscriber-to-customer contract

**Hypothesis, not live campaign.** One relevant offer: Zen12 Premium, only *if* Mind and founder obtain the exact product, email-channel and tracking authorization. No list creation, scheduling, post edits, emails, direct affiliate links or revenue estimates. Preserve original 4 editorial / 2 prospective commercial pilot. 

## Who may advance

**Cohort A, consent not authenticated:** visitor clicks Grok's asset-tagged link, lands on /focus/ or /dispatch/, requests Fieldbook, or sees `?subscribe=`. This is **not confirmed_signup**. Fieldbook downloads can remain openly usable, independently of newsletter permission. Avoid preselecting commercial consent; keep site disclosures accurate.

**Cohort B, provider-confirmed subscription:** subscriber record shows completed Jetpack confirmation, is email-eligible, and not suppressed/unsubscribed as of sending time. Only then can server-side privacy-preserving `confirmed_signup_v1` be emitted (one unique confirmation event per opaque provider subscription id; do not log addresses, tokens or hashed addresses in front-end analytics). Provider's `total`, `confirmed`, `unconfirmed`, `wpcom` and direct email follower categories are NOT additive unique recipients; current snapshot 3/3/2, wpcom3/email0, actual recipient count unknown. The UI query value, button click or download alone never establishes this event.

**Cohort C, qualified existing reader:** reader has voluntarily opened a historically sourced editorial investigation and opted to receive the Dispatch. Proposal: Issue01/02 establish the evidence identity; Issue03 offers a *non-promissory practical attention exercise* and only after approved rights, optional verified Zen12 comparison guide. A non-click or failure to opt in is not permission to recontact. The six-issue draft stays weekly and unscheduled.

**Cohort D, verified paid customer:** seller/commerce independently reports a settled attributable paid order. Join to campaign and Grok asset only on a verifiable merchant reference and approved privacy-safe reporting (no guessed cross-domain attribution). Deduplicate recurring orders/adjustments; net is settlement minus refunds, chargebacks, reversals and fees, in a defined currency. A click, checkout view, download, follow or confirmation is not revenue.

## Proposed event contract, owned by Claude/analytics

`source_asset_id` equals immutable Grok `utm_content`; `utm_campaign` from TASK-008 follows `<topic_cluster>_pilot_2026_11`; `utm_medium=organic_social`, `utm_source` exact originating platform. Record qualified-human landing sessions only with filtering, consent, and unique session dedup; missing attribution remains UNKNOWN. `guide_view`, `guide_cta_click`, `confirmed_signup_v1`, and `merchant_settled_order` are **separate** events; never synthesize conversions from upstream events. Email clicks can use `utm_medium=email`, `utm_source=dispatch`, `utm_campaign=dispatch_pilot_2026_11`, `utm_content=issue03_zen12` only after a real verified destination and approved privacy process. Do not attach subscriber email identifiers or partner secrets to URL parameters.

## Seven- and thirty-day cohorts

For each cohort, store actual qualified sessions, independently confirmed leads, paid customers/orders, gross settled receipts, reversals, fees, net, and any opt-outs with separate provenance. Formula when denominator and matched settlements are trustworthy: `1000 * realized_net_attributable_revenue / qualified_human_sessions`. Otherwise report `NOT_COMPUTABLE`; not `$0`. Never invent A/B lift on a tiny audience or express seller's public EPC claim as FV earnings.

## Permissioned progression, not a drip blast

1. Reader arrives via Grok's existing content (Grok owns creative, Claude owns analytics). Present historical investigation or Fieldbook, no commercial claims.
2. User voluntarily confirms Jetpack email subscription. A read-only provider eligibility check, a real (authorized) welcome receipt with 52-page Fieldbook link, and actual suppression/opt-out status must be proven before any campaign send. This is not yet verified.
3. After founder explicitly adopts campaign and the issue's required rights are signed off, editorial-first Issue03 may point to a vetted live Zen12 guide with clear adjacent commission disclosure and independent alternatives. Other issues remain historical/evidence-led. No automatic sending permitted by this document.
4. Purchase attribution can come only from independently supplied seller settlement matched to the approved unique campaign, never from an ad URL, a coupon viewed, or a user's click.

## Owner acceptance

**Mind #171:** exact approved SKU, accepted publisher/account, email-channel rights, issued referral link, verified seller terms and live warm-up guide. **Dispatch #174:** truthful manuscript, subject/preheader checks, consent release guard, legal footer and actual native Jetpack preview. **Focus/Claude #129:** server-authoritative confirmed event, real welcome receipt, qualified session denominator and no double-count. **Grok/Praxxis #820/TASK-008:** asset-to-page mapping and real platform evidence; content ownership stays with Grok. **Founder:** approve physical FV mailing address, all live changes, campaign adoption, audience/time and each send.
