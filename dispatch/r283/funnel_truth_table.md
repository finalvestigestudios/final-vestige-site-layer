# R283 — verified surface vs conversion event truth table

**Read-only observations November 11, 2026:** Live https://finalvestige.com/focus/ displays both an email subscription flow and a direct **Download the Seven Day Focus Fieldbook** link. That establishes availability of a download affordance, not a recipient-confirmed lead or a successfully transferred PDF. Live https://finalvestige.com/dispatch/ contains its own subscription form to the same Jetpack list.

Authenticated Jetpack (15:33 UTC): newsletter enabled and sendable; automatic post notifications default off; welcome configured with same 52-page PDF; format full; categories off; diagnostic total 3, confirmed 3, unconfirmed 2; follower category WordPress.com 3, email 0. These counters **cannot be added or treated as currently email-eligible people**. Five recent posts opted out of new-post sends; this does not prove complete historical send volume.

| Surface/event | Supported interpretation | Unsafe inference |
|---|---|---|
| Focus page loaded | Page requested | Human qualified, person subscribed, lead established |
| PDF link displayed/clicked | Download offered, maybe reader interest | Confirmed lead, verified binary delivery, welcome email receipt |
| Subscribe button pressed | Attempt to subscribe | Confirmation or email eligibility |
| Confirmation email generated | Invitation to verify | Confirmation clicked or welcome received |
| Verified Jetpack subscribed and currently email-eligible with consent provenance | Deduplicated confirmed_signup once across both pages | Every confirmed dashboard count eligible; all had to click |
| Guide CTA clicked | Interest in prospective offer | Merchant authorization or sale |
| Merchant link clicked | Outbound traffic | Paid order, net commission |
| Checkout initiated | Intent to purchase | Settled sale |
| Merchant statement reports attributed settled order | Possible independently verified paid conversion | Final net without refunds and fees |

**Proposed source convention, NOT live or deployed:** verified Grok published asset_id → owned landing /focus/ with source/campaign → authenticated provider consent → relevant helpful historical nurture → only after authorization vetted Zen12 guide in reserved Issue 03 → independently reported merchant settlement/refund/fees. Do not infer a person-level join from anonymous visits without authorized consent. Reconcile mind_pilot_2026_11 vs mind_proposed_2026_11 before any deployment. Issue 05 stays commercially blocked.

**KPI:** qualified human sessions, actual consented confirmed leads, guide CTA clicks, real paid orders/settlements, fees/refunds, realized net revenue, net per 1k qualifying sessions and 7-/30-day cohorts, each reported separately. If real human sessions or settled paid financial values are absent, output **NOT COMPUTABLE**, not zero; no tiny-sample A/B claims.

No existing settings or attribution scripts altered. Sources: https://wordpress.com/support/newsletter-settings/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
