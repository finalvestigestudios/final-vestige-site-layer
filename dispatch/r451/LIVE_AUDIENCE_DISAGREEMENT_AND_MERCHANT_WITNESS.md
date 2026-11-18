# R451 — Three incompatible audience views; one consent-to-revenue gate

**Observation:** November 18, 2026, 08:39 PT / 16:39 UTC. **READ ONLY.** Site: https://finalvestige.com . Master campaign [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) · release split [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) · predecessor [PR #3016](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/3016) · authoritative [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174).

## New first-party discrepancy that must not be flattened

| Authenticated WordPress surface | Exact observed count | Meaning; **not** a sales metric |
|---|---:|---|
| Newsletter diagnostic `subscribers.total` / `confirmed` | 3 / 3 | Confirmed records shown in newsletter diagnostic |
| Newsletter diagnostic `unconfirmed` | 2 | Additional, explicitly unconfirmed; **excluded** from 3 |
| Subscribers list `filter=all` | 3 | All returned records have `status=Subscribed`, `email_subscriber=true` |
| Subscribers list `filter=unconfirmed_subscriber` | 2 | Separate records in state `Not confirmed`; excluded |
| Stats Followers feed `email` | **0** | A **different first-party metric endpoint**; contradicts eligible-recipient count |
| Stats Followers feed `wpcom` / `total` | 3 / 3 | Reader follower feed; NOT evidence of three new emailed leads |
| Newsletter `paid`, `imported_last_24h` | 0 / 0 | Provider diagnostics, not zero sales revenue |
| Five recent newsletter send records | `never_sent_opted_out` | All `send_subscription=false`; dispatch timestamp null |
| Site delivery enabled? | `site_can_send=true` | Capability only; not proof any email was delivered |
| Welcome text | Configured with direct 52-page PDF | Configuration is **not** inbox receipt |

**Crucial finding:** The read-only follower feed currently returns `email=0` **while** the individual subscriber list reports three `email_subscriber=true` + `Subscribed` records. The two endpoints disagree. It would be equally unsound to call that *zero email subscribers* or *three delivered welcomes*. Preserve both exact figures with endpoint names and open a provider-support reconciliation if still inconsistent; do not sum follower counts with subscriber counts. Five total records visible across confirmed and unconfirmed filters are NOT five subscribers.

Three email-eligible records appear associated with publisher-controlled identities on private inspection. No proof of three independently acquired readers; **no recipient names, addresses, numeric provider IDs or raw subscriber export are stored here**. No observed new confirmed_signup event. The Gmail searches on November 18 found the August 24, 2026 Refersion `pending` message but no named acceptance or email-marketing authorization, and did not establish a received Fieldbook welcome in the checked connected mailbox. Absence in the searched mailbox is not evidence of universal non-delivery.

## Platform promise and rendering blockers

- Newsletter is enabled; `email_new_posts_by_default=false`, full-content format, `from_name=Final Vestige Studios`, `reply_to=no-reply`. Recent posts not emailed. Settings unchanged.
- Live [/dispatch/](https://finalvestige.com/dispatch/) promises investigations by email **when published**, and live [/focus/](https://finalvestige.com/focus/) says the same. That overstates current auto-send practice. Recommend founder-approved copy: **“Selected investigations, source notes and occasional Mind & Perception fieldwork; not every post generates an email.”** The free Fieldbook remains directly downloadable; do not gate the free PDF behind a new list.
- WordPress documents that **Preview email** is available with per-post email sending OFF. Access to that editor preview did not exist in this run's read-only connector tools; no native Preview, received test message, actual rendered Final Vestige postal address, or functioning unsubscribe was witnessed. Do not infer those from an offline HTML preview or Automattic's own corporate postal address.
- WordPress confirmation and welcome delivery have **distinct** evidence requirements. `confirmed_signup` means a new provider-confirmed transition; a welcome receipt needs an actual authorized inbox artifact separately. No founder authority to initiate a test email: **do not send one**.
- FTC commercial email: honest header/subject, conspicuous commercial purpose as applicable, valid **Final Vestige** postal address and effective opt-out; [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business). FTC describes requirements, but only a real Jetpack render/recipient acceptance can demonstrate this campaign's footer/opt-out.

## Merchant identity/source-of-truth check

- **Issue 03 = Zen12.** [Official Zen12 about](https://zen12.com/about) describes 12 levels and four versions of each; its `one hour in twelve minutes` language is a **vendor representation**, not product-specific efficacy evidence. The separately marketed [Zen12 /secret/](https://zen12.com/secret/) displays a coupon, countdown/promotion and bundle; **do not copy its price, expiry, discount or testimonials into Dispatch**. It does not convey affiliate email permission.
- **Issue 05 = Hypnosis Live**, NOT Total Focus. [Official Hypnosis Live FAQ](https://hypnosislive.com/faq) says MP3 downloads, a 14-day seller refund process with a maximum of five sessions/year; these are **seller-stated** and require a checkout and offer-currentness witness, not an efficacy endorsement. Its UK merchant postal address is not Final Vestige's commercial-email address.
- Approval, specific **EMAIL** channel rights, issued earnings URLs, product SKU, approved creative, two live first-party buyer guides, checkout terms and independently settled affiliate commissions remain **NOT VERIFIED**. Mind & Affiliate Studio [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) owns guide and merchant readiness. A product catalog or another product's swipe copy is not authorization.
- Subscriber names and recipient-level tracking must not appear in GitHub, GA events or `utm_content`.

## Per-issue release invariant

Preserve 01 editorial / 02 editorial / 03 Zen12 commercial HOLD / 04 editorial / 05 Hypnosis Live commercial HOLD / 06 editorial. No substitutions without explicit founder approval. No sending, scheduling, publishing, paid services, subscriber imports or settings changes. Original #175, #201 and frozen homepage #49 stay untouched.

The companion `audience_contract.py` accepts **only sanitized, aggregate evidence**; `test_audience_contract.py` uses synthetic fixtures. It records contradictory feeds rather than adjudicating who receives email, refuses new signup counting without a provider confirmation transition, and leaves net revenue per 1,000 qualified sessions NULL until independent denominator and complete settlement attestations exist.

## Required next source-of-truth witness (no automated actions authorized)

1. **Claude / Focus:** Read a newly created provider-confirmed signup transition **with explicit prospective consent** and an independently received welcome/PDF; privacy-safe counts only. Diagnose why Stats Followers email=0 but Subscribers email-eligible=3, preferably with WordPress support documentation or provider support evidence; no subscriber export.
2. **Dispatch / Founder:** Obtain founder-selected original-vs-alternative editions; verify an actual **non-sending** post-editor Preview at mobile and desktop widths and the live email footer/unsubscribe behavior by a separately authorized safe procedure; verify publisher postal before any commercial issue.
3. **Mind / Commerce:** Provide named Inspire3/Refersion acceptance, product + EMAIL rights, issued earning URL, currently published disclosed guide, actual seller offer/checkout terms, reconciled commission settlement.
4. **Grok / Praxxis / Claude:** Carry immutable `asset_id` into consent-respecting first-party campaign attribution; no new tracking scripts. Demonstrate unique qualified-human sessions, merchant-paid orders and refunded/fee-adjusted net revenue on separate 7/30-day cohorts.

**No revenue claim:** net realized revenue / 1,000 qualified-human sessions = **NOT COMPUTABLE**, not `$0`. Missing data is not an observed zero.
