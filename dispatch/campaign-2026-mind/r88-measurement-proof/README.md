# R88 — measurement provenance before metrics, evidence-only Dispatch scorecard

**Owner:** [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) · [master manuscript PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) · [first release gate #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) · [Mind affiliate owner #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Stacked separately above R87 #762. Homepage frozen #49 untouched.

**Why this is new:** Prior work provides copy, inbox previews, send-proof inspectors, consent diagnostics and a high-level attribution plan. It does **not** provide a machine-validated, provenance-bound and privacy-constrained scorecard that distinguishes *WordPress Reader followers*, *email-eligible Jetpack recipients*, *sent email*, *email clicks*, *article/guide views*, *outbound merchant clicks*, and *verified affiliate sales*. This package does. It keeps every unknown unknown, even when a convenient but incompatible dashboard reports zero.

### Exact live evidence — read-only, 2026-11-03 10:31 UTC

Connected WordPress site 256784396: Jetpack enabled and capable of sending; automatic per-new-post checkbox **defaults off**, not a global hard send lock. Excerpt mode, sender Final Vestige, reply-to no-reply; welcome 52-page PDF configured (actual receipt NOT verified). Newsletter diagnostic counters **total 2 / confirmed 2 / unconfirmed 2**, whereas separate complete follower stats report **total 2 / email 0 / WordPress.com 2**. The first counts are internally incompatible with a naive disjoint sum; the second use different population definitions. Actual opted-in, email-eligible audience is **UNKNOWN**—not zero, two or four established. Latest five individual posts #1926/#1924/#1922/#1920/#1917 show never_sent_opted_out, with no dispatched timestamps; this is **not** a lifetime delivery report.

The source snapshot intentionally contains only source-identifying metadata, aggregate counts and *no* recipients, raw emails, private link tokens, full business postal address or seller links. Customer postal/address proof remains separate, private and unverified. **No email or real test email was sent.**

### Measurement contract (implement now; activate later only with approval)

| Funnel stage | Correct source of truth | Safe claim | Never infer |
| --- | --- | --- | --- |
| Signup interest | Jetpack subscription form, optionally anonymous site pageview analytics | Visits to the two existing signup pages if independently sourced | That a pageview was a new confirmed email subscriber |
| Opted-in eligible | Native Jetpack Subscribers, **Email Subscription** filter plus emails-paused/bounced status | Verified eligible count when independently checked | email0 in followers = no deliverable subscribers |
| WordPress Reader follow | Jetpack follower breakdown | WordPress.com followers separately | That a Reader follow always yields an email |
| Email delivery | Per-edition Jetpack delivery run evidence | Recipients, sends and bounces with a dated proof reference | A draft or never_sent_opted_out record was delivered |
| Opens | Jetpack campaign report | Approximate pixel-observed opens; privacy proxy caveats | Open = human read / statistical significance |
| Email clicks | Jetpack post email campaign reporting | Verified clicks if actually available | That click = guide visit / sale |
| Guide visits | WordPress site stats on exact approved guide post | Article pageviews, not person-level exposure | That a pageview came from newsletter without attribution |
| Guide affiliate CTA clicks | Existing first-party analytics **only if approved and demonstrably measured** | Click count to verified merchant link | That a click is a purchase |
| Partner conversions | Inspire3 account-specific seller reporting **only if accepted** | Approved sales and reversals, tracked to a receipt | Sales from link guesses, catalog EPCs, or merchant promises |

**Campaign/source key proposal only:** `fv_dispatch_pilot_2026`; editions `01,02,03,04,05,06`. After founder permission and native Jetpack inspection, use observable source/referrer and only permitted first-party campaign parameters when they can survive the native excerpt/Read more flow. Avoid inserting UTMs into merchant URLs without private partner rules, and never add pixels, cookies, IP logs or a second signup list to make a small sample look larger. Do not activate links or tracking from this PR.

**Provenance validation:** a metric can be introduced only by a fixed measurement name, source-type enum, nonnegative integer, UTC observation time, and an opaque reference to a real report. Unknown is represented by *missing* metric data, not `0`. This first release scorecard shows counts below five as SUPPRESSED; no individual records. All percentage/conversion/CTR/ROI results deliberately omitted while the list is tiny, denominator unknown and merchant unapproved. A future founder-reviewed change is needed before marking actual metrics as campaign successes. Automated tests are guardrails, not evidence that an event happened.

### Reproduce safely

```bash
python dispatch/campaign-2026-mind/r88-measurement-proof/scorecard.py
python dispatch/campaign-2026-mind/r88-measurement-proof/scorecard.py --output /tmp/fv-dispatch-r88-review
python -m unittest discover -s dispatch/campaign-2026-mind/tests -p test_r88_measurement_provenance.py -v
```

The output is a static, keyboard-readable HTML/plaintext **reviewer**, not an email, website analytics integration or actual inbox preview. Its exact synthetic and live-aggregate observations are marked HOLD. No network calls, WordPress write paths, email-send functions or merchant links. No expenses.

### Actionable founder clearance — no campaign approval implied

Native Jetpack Subscribers tab with **Email Subscription** and suppressed/bounced/paused categories must reconcile the conflicting numbers without exporting addresses. Founder supplies and separately verifies an eligible Final Vestige physical postal address. WordPress **Preview email** must be inspected for the actual excerpt, subject, sender, link and unsubscribe; a genuine received test email is separately permission-gated and not authorized here. Mind #171 owns the published Zen12/Total Focus independent guides and named-account email promo permissions. Issues 03/05 remain HOLD_MERCHANT. Founder eventually reviews and explicitly authorizes the final audience/creative/dates before a single send. Preserve original four-editorial/two-commercial campaign.

### Citations verified Nov 3, 2026

- WordPress subscribers: https://wordpress.com/support/subscribers/
- WordPress subscriber stats: https://wordpress.com/support/stats/view-subscriber-stats/
- WordPress email preview and excerpt: https://wordpress.com/support/newsletter/email-appearance/
- FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Zen12 exact seller page: https://zen12.com/hnp
- Total Focus exact seller page: https://hypnosislive.com/mental-skills/total-focus
- Inspire3 public affiliate portal (NOT private authorization): https://affiliates.inspire3.com/

**Release state: ALL SIX HOLD_UNSENT; 03/05 HOLD_MERCHANT.** Merchant-specific prices, seller guarantees, approved creative, links, email marketing permission, and customer-data rights remain UNVERIFIED. No launch.
