# R432 — the recipient reality and post-broadcast constraint (read-only)

**Status:** DRAFT / HOLD_UNSENT / no WordPress writes, emails, test emails, subscriber inspection/export, or paid links. **Owner:** [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); affiliate terms owned by [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Stacked on [R431 PR #2911](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2911); untouched campaign master [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) and release gate [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201). The frozen homepage PR #49 is not involved.

## Authentic November 17, 2026 snapshot (21:38 UTC)

Authenticated WordPress newsletter status and settings for `https://finalvestige.com` returned: subscriptions **true**; site_can_send **true** (a platform capability, **not evidence of eligible recipients**); automatic email on new post **false**; email content format **full**; featured image in email **true**; author byline **false**; reply-to **no-reply**; newsletter categories **disabled**; welcome message includes the existing **52-page Focus Fieldbook**. The last five post records are `never_sent_opted_out`, not a lifetime send count.

Newsletter dashboard: **total 3, confirmed 3, unconfirmed 2, suppressed 0**. Jetpack Stats Followers: **Reader/WordPress.com 3, direct email 0, comment 0, publicize 0**. These are different account/scopes and **cannot be summed**. They do **not** establish a deliverable list, actual eligible receiving addresses or proof that three people will receive emails. Zero in the direct-email follower metric is **a reported metric, not a validated distinct-inbox count or proof no human has ever signed up**.

Full page read confirmed /dispatch/ still promises alerts when investigations publish, while automatic notifications are OFF; /focus/ offers the Fieldbook. Welcome is **configured, not receipt verified**. No native Jetpack email Preview, real postal footer, operating unsubscribe, or confirmed subscriber eligibility was witnessed.

## New high-priority blocker: segmentation is not currently a deliverable transport

**WordPress.com documents newsletter categories as an opt-in way to receive only selected topics.** Final Vestige's `newsletter_categories_enabled=false` and `newsletter_categories=[]` mean there is presently no demonstrated category-addressable audience for a tailored "Mind interested" vs "History interested" email sequence. **No subscriber-specific automation or private-interest segmentation is authorized, and this sprint does not enable categories.** WordPress.com also notes that subscribers choosing "All content" receive all categories even when enabled. Turning categories on would be a separate founder/consent/settings decision, not an innocent preview change.

A **hypothesis about on-site visitor source** (Grok asset -> focus/investigation -> link click) is feasible for aggregate editorial planning once Claude's privacy/analytics contract is approved, but must **not** be represented as a subscriber-specific send list or proof of consent. The safe existing campaign remains **six weekly unscheduled editorial-post candidates**, all HELD. A post newsletter requires an explicit editor release and is not a standalone email campaign.

## How to reconcile recipient counts privately, without exporting addresses

1. Under Jetpack → Newsletter → Subscribers, use the built-in **Email subscription = Subscribed** filter. Record **only the aggregate number** of currently eligible subscriptions, not usernames, addresses or profile exports. A Reader-only follower is **not proof of receiving email**.
2. Compare to **Not confirmed**, **Emails paused**, **Bounced** and **Not sending** filters; categories may overlap, so preserve definitions and read-only timestamps. If totals remain contradictory, request WordPress support documentation rather than invent a union.
3. For a consenting, authorized owned test identity only, prove WordPress's actual confirmation or platform-authenticated eligibility, then the **received welcome email with working PDF link**. This run did **not** generate a test signup or send a confirmation.
4. On a specifically authorized future editor draft, use WordPress's **Preview email**, verify its desktop/tablet/mobile first paint, subject, preheader behavior, featured image and actual legal-footer layout. "Preview email" is not "Send test email". Neither was used here. Test a real received commercial message/unsubscribe **only with separate founder permission**, and never unilaterally contact the list.
5. Ask the founder for the **Final Vestige business postal address appropriate under CAN-SPAM**. The postal address in a WordPress.com subscription confirmation or a merchant's London footer is **not a substitute**. Confirm a functional unsub mechanism in actual generated mail, not an invented placeholder.

## Commercial one-offer boundary

Zen12 promotional statements (e.g., "an hour in twelve minutes") are merchant claims not proven independent outcomes, and its About and Secret sales pages display different bundles/promotions. Hypnosis Live's official FAQ states a **14-day** refund request period with a **maximum five refunded sessions per year**, without establishing the terms of an authorized FV referral. Neither official website nor consumer marketing email grants **named Final Vestige email-promotion authorization**, an issued affiliate URL, a live vetted guide, a referred checkout or a settlement. Issues 03/05 remain **HOLD_MERCHANT** with null earning links.

If Mind eventually proves a SKU, guide, account/EMAIL permission and checkout, conduct **one-offer-at-a-time** founder review; do not broadcast both products opportunistically or treat a merchant's promotion as permission to copy its creative. No send follows from a source-only test passing.

## Documentation and standards

- [WordPress subscribers, last reviewed Nov 4 2026](https://wordpress.com/support/subscribers/) — Reader vs email, confirmation, paused/bounced, eligibility filters, count troubleshooting
- [WordPress newsletter categories, last reviewed Oct 6 2026](https://wordpress.com/support/newsletter-settings/enable-newsletter-categories/) — disabled default, All content, no subgroup resend
- [WordPress email appearance](https://wordpress.com/support/newsletter/email-appearance/) — independent native Preview versus Send test
- [WordPress post-based send control](https://wordpress.com/support/newsletter/disable-newsletter-emails/) — default and per-post toggle
- [FTC CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) — sender postal, truthfulness, opt-out and obligations
- [Zen12 official About](https://zen12.com/about), [Zen12 official Secret offer](https://zen12.com/secret/)
- [Hypnosis Live official FAQ](https://hypnosislive.com/faq)
- [Final Vestige Editorial Standards](https://finalvestige.com/editorial-standards/) — evidence, original sourcing, uncertain claims, dated corrections and disclosure

## R432 exact-source proof limitations

The code under `dispatch/r432/broadcast_consent_gate.cjs` is **pure, offline, synthetic evidence classification**, not a production permission checker, subscriber lookup, checkout validator, or sending interface. It returns `sendAuthorized:false` even if every synthetic flag is true. 92 native Node assertions test both current held status and dangerous mock counterexamples. The source-level assertions cannot prove delivery, consent, merchant terms, compliance, conversion lift or revenue. Keep established 4 editorial / 2 commercial allocation. No subscriber PII stored.
