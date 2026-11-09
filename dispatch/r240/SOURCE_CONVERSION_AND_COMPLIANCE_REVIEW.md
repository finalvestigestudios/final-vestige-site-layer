# R240 — Subscriber-to-customer proof and release ledger

**Status: BUILT for review, NOT APPROVED, NOT LIVE, NOT SENT.** Derived from master Issue #174, Mind #171, conversion Issue #820, and source master PR #175. This does not replace an approved issue or modify any original manuscript. PR #201 and R230–R239 already contain numerous QA/alternative files; R240 specifically fixes repeat-signup friction in the last editorial issue and explicitly separates lead proof from paid-sales proof.

## Fresh read-only evidence, November 9, 2026 20:36 UTC
- Jetpack Newsletter enabled; `site_can_send=true`; `email_new_posts_by_default=false`; full-content email mode; sender display `Final Vestige Studios`; reply-to `no-reply`.
- The existing **52-page** Fieldbook is already linked in the welcome content. This is configuration evidence, **not** delivery evidence.
- Dashboard reports `total=3`, `confirmed=3`, `unconfirmed=2`, `suppressed=0`; do not add counters or equate them to recipients. Actual email-eligible people UNKNOWN. Five recent post sends show `never_sent_opted_out`.
- /focus/ shows a subscribe form and the direct downloadable book; it explicitly says confirmation is required to join Dispatch. A `?subscribe=...` visibility switch is **not** a verified confirmation event.
- /dispatch/ published page 523; /focus/ page 1579; Editorial Standards page 17. Final Vestige standards distinguish primary evidence/inference and independent editorial judgement.
- Official Jetpack documentation (updated Nov 4): new **post** publication triggers eligible newsletter sending; there is a native `Preview email` distinct from transmitting a `Send test email`. We did neither. https://jetpack.com/support/newsletter/
- Original Issue06 CTA `https://finalvestige.com/focus/` asks someone already subscribed to encounter the signup form again. Optional R240 direct-PDF CTA removes that avoidable journey repetition without displacing the existing lead-generation landing page for **new** visitors.
- Source Harkin et al. 2016, PMID 26479070: 138 randomized progress-monitoring studies, combined n=19,951; association of increased monitoring with better goal attainment on average. **Not** efficacy evidence for the proprietary Fieldbook, meditation audio, hypnosis, or an individual person. https://pubmed.ncbi.nlm.nih.gov/26479070/

## Conversion bridge (not an automated drip)

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL evidence | OWNER |
| --- | --- | --- | --- | --- | --- |
| Free Fieldbook | Existing subscriber → useful action | Original Issue06 CTA returns to new-signup form | Optional direct-PDF primary CTA; collect only allowed **aggregated** click counts using existing infrastructure | Static CTA proof PASS. Real click tracking and user behavior **NOT VERIFIED** | Dispatch / Claude |
| Zen12 Premium (provisional, not approved) | Interested opt-in reader → approved guide | Named FV affiliate acceptance, email-promotion rights, issued earning URL, live buyer guide unverified | Gate issue03; offer only to voluntary high-intent guide readers after merchant clearance, never infer buyer intent from science clicks | Merchant **HOLD** and no credited sales | Mind |
| Total Focus (provisional, not approved) | Interested opt-in reader → guide | Same merchant/checkout/refund issues | Preserve optional issue05 placement, **no direct merchant link** | Merchant **HOLD** | Mind |
| Focus lead | Social asset → /focus/ → confirmed signup | Jetpack counters and browser UI not authoritative | Canonical `confirmed_signup` only after authenticated provider state transition; dedupe by internal opaque key, not URL switch, preserve consent | Logic defined. Provider events **NOT LIVE/VERIFIED** | Claude / Focus |
| Dispatch subscriber | WordPress post → email → open/CTA | Native email preview, preheader, publisher postal address and actual unsubscribe unknown | One explicitly authorized unpublished draft and native preview; later separately approved inbox proof | **HOLD** | Dispatch / Site QA |
| Customer | Eligible affiliate conversion → net revenue | No commissioned paid orders or qualified-session denominator | Join independently reported settled paid orders with refund/fee data to source-tagged campaign cohorts; omit unmatchable rows from attributed numerator, report unattributed separately | Revenue per 1,000 **NOT COMPUTABLE** | Commerce / Praxxis |

## Data contract for existing instrumentation only
Grok assets maintain `utm_source=<actual platform>`, `utm_medium=organic_social`, `utm_campaign=<topic_cluster>_pilot_2026_11`, `utm_content=<unique_asset_id>`. Dispatch editorial click candidates would use `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue_06`; do **not** add parameters to direct PDF until Claude verifies that the server/CDN and consent controls can attribute them without a script or leaking recipient IDs. An untagged direct PDF link is acceptable for the **draft** and should not be represented as measurable.

For each 7/30-day acquisition cohort, `net_revenue_per_1000 = 1000 * (independently settled attributable gross - refunds - fees) / qualified_human_sessions` only when denominator >0 and paid order attribution is verified. Unknown is `null` rather than zero. Do not infer sales from emails/clicks, do not infer A/B significance with a tiny list. Never commit recipient email addresses, tokens, raw exports, or probabilistic individual attribution.

**Research note for prospective Zen12 placement:** The seller at https://zen12.com/hnp advertises 12 levels/48 Premium recordings and a 12-minute-to-one-hour equivalence; the latter is a **seller claim, not product-specific established evidence**. Full named partner approval, channel-specific email rights, final checkout, refund enforcement, creatives and earning link remain NOT VERIFIED.

## CAN-SPAM and transactional caution
The editorial email is not automatically exempt merely because it has no direct merchant link: its primary purpose and content matter. The FTC requires truthful identity/subjects, valid physical publisher postal location, conspicuous opt-out for applicable commercial messages, prompt honoring of opt-outs, and clear commercial disclosure. https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business. The Automattic address in a WordPress confirmation email does not prove the Final Vestige publisher address is present in commercial sends. A locally rendered HTML preview cannot verify this. These are release blockers until genuine approved received-email evidence exists.

**Hard hold:** No WordPress edits, posts or drafts; no email/test email; no subscriber read/export; no affiliate activation, tracking deployment, social posts, purchases or spend. Founder approves final creative and send; Claude does production instrumentation; Mind owns merchant eligibility and pre-sell guides; Grok owns acquisition videos.