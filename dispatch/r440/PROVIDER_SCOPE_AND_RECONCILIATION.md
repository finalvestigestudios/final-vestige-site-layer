# R440 — first verified recipient-eligibility read, not a delivery audit

**Result: three (3) current WordPress subscriber rows are in the authoritative email_subscriber filter.** The returned three records each have status Subscribed and email_subscriber=true; the Reader-only filter returns zero. This is a material correction to R438/R439's "eligible inbox count UNKNOWN". No names, email addresses, person-level dates or subscription IDs are reproduced here.

## What we can and cannot say

* Authenticated Subscriber-tab aggregate at 2026-11-18 05:44 UTC: all=3, confirmed in separate Newsletter dashboard=3, unconfirmed (excluded)=2; filtered email subscribers=3, all 3 flagged Subscribed/email_subscriber=true; filtered Reader-only=0.
* A separate Jetpack Stats Followers view earlier showed 0 "direct email" and 3 "WordPress.com Reader"; those classifications are not equivalent to the Subscribers page's Email subscription status. Do not subtract or add the two dashboards. The authoritative current email eligibility evidence is 3 rows; it does not show successful delivery or reach into an external audience.
* The Subscriber filter establishes configured delivery eligibility, not individual receipt, the 52-page welcome message, opening, verified opt-in scope for additional affiliate marketing, or a paid customer. This is a tiny list with no inference about significance, engagement, purchase intent or A/B results.
* The confirmed_signup event requires provider-authoritative transition plus permission for the subscribed content; it is not an attempt, a PDF reveal, a Reader follow, or a speculative join to a Grok click. Event cardinality for the same provider subscription identity must be one, with PII kept server-side and absent from analytics/GitHub.
* In the connected Gmail account, a targeted Oct-Nov search found no receipt containing the configured Dispatch welcome or Fieldbook. That only restricts claims about that mailbox; other inboxes were neither inspected nor contacted.

## WordPress transport and editorial boundary

WordPress newsletter on, manual per-post email default off, full-content format, no-reply, categories off, configured Fieldbook welcome; recent post records opted out of sending. Live /dispatch/ says readers receive emails when investigations are published: an inaccurate expectation if readers infer all publications. R439 offers founder-review copy replacements. Adopting one requires separate site-owner approval and Claude/site coordination.

A native WordPress editor Preview email is documented independently of Send test email, and can be viewed while sending is off. Connector does not expose that rendered email preview. Offline simulations in the PR stack do not prove a native preview or postal/unsubscribe behavior. Commercial sending stays on hold under FTC CAN-SPAM regardless of WordPress's technical ability to email.

Read-only site evidence: /dispatch/ page 523, /focus/ page 1579, /editorial-standards/ page 17. Published standards require primary evidence, explicit uncertainty, correction transparency and independence from commercial relationships.

## Practical next accepted source evidence

1. Dispatch/Founder + Claude: non-sending native Jetpack Preview on a never-published staging/editorial draft, capture subject, actual snippet, mobile first paint, sender, Final Vestige's legally valid postal address and unsubscribe. No test mail without explicit approval.
2. Focus/Claude: observe the actual configured welcome with the Fieldbook PDF link from a consented internal account; do not add a subscriber or trigger new emails in this run.
3. Mind/Commerce: return dated partner-supplied account-specific permission explicitly allowing email marketing for **Zen12 issue 03** and **Hypnosis Live issue 05**, the exact SKU, approved landing guide, issued commission link format, and current price/refund/seller claims. Total Focus is not canonical issue 05.
4. Founder: select/approve subject fix for issue 04 and honest signup promise for /dispatch/; original campaign and all alternatives remain unadopted.
5. Praxxis/Grok/Claude: verified asset_id and consent-safe attribution; paid conversions require partner-confirmed settlements and matured 7/30-day net after fees/refunds.

Sources: https://wordpress.com/support/subscribers/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171 .

**No sending / test sending / schedules / CMS changes / list exports / merchant activation / new paid services.**
