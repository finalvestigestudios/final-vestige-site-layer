# Dispatch R138 — actual received-email evidence gate (NOT SENT)

**Owner:** Final Vestige Dispatch Studio · 2026-11-05 · [Campaign #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) · original manuscripts [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) · independent gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201).

## Purpose and scope

This new proof harness closes the **methodological** gap between synthetic newsletter HTML and a genuine received Jetpack newsletter. It cannot close the **evidentiary** gap until an authorized genuine email becomes available. It accepts explicitly provided RFC5322 .eml bytes in memory; checks relevant sender, plain/html alternatives, one expected first-party CTA, HTML hazards, commercial disclosure in each provided MIME body and its textual proximity to the intended CTA (300-character conservative limit), a publisher-address match supplied by an authorized reviewer, and the existence of a visible unsubscribe URL and List-Unsubscribe header. It returns **boolean-only findings**, never raw email content, recipient, Message-ID, unsub token, address or personal identifier; it sends no email, calls no external URL and modifies nothing.

Run: `cd dispatch/campaign-2026-mind/r138-received-email-proof && python -I -m unittest discover -s . -p 'test_received_email_gate.py' -v`

**Native Python 3.13.5:** 20/20 synthetic regression checks PASS. Original master #175 Python test suite independently rerun 6/6 PASS against archived original exact head `d57ccdba3aee8f065e143e101c2945f4f3d01647`. The local fixture postal address and recipient are obviously **synthetic**, not actual Final Vestige identities. A positive structural result never sets release-ready or proves native receipt, subscription consent, merchant email authorization, unsubscribe functionality, purchase or realized revenue.

**Internal extra requirement:** List-Unsubscribe is a conservative deliverability gate, not an independently required CAN-SPAM header. A link being present cannot prove that unsubscribing works. Do NOT click real opt-out URLs without a founder-authorized controlled procedure. A valid **Final Vestige** physical postal mailing address is required for applicable commercial email, **not the Automattic postal address** appearing on a WordPress service confirmation. Publisher address must be independently attested; never invent one or commit it to repo.

## Actual authenticated findings, 2026-11-05

- Native WordPress Jetpack newsletter status at **13:33:23 UTC**: enabled and site_can_send, but latest five shown post notifications **never_sent_opted_out**; subscriber aggregate total 3, confirmed 3, unconfirmed 2, suppressed 0, paid 0, imported_last_24h 1. **Do not add or interpret these numbers as unique eligible people**; import provenance and consent remain unknown.
- Native settings at **13:33:25 UTC**: email_new_posts_by_default **false**, email_content_format **excerpt**, reply_to no-reply, sender display Final Vestige. Existing welcome message contains 52-page Seven Day Focus Fieldbook PDF link. Settings **unchanged**. Configuration does NOT prove delivery.
- Independent WP Stats follower result: **3 WordPress.com followers; 0 legacy email followers**, a distinct counting system. It does not settle Jetpack's email-eligible recipient count.
- Read-only Gmail targeted review: a 2026-10-25 subscription **confirmation** is present, but no completed Focus Fieldbook welcome or named FV affiliate-acceptance mail was found among targeted messages. Evidence may exist elsewhere; no claim of global absence.
- Published /dispatch/ (ID 523), /focus/ (ID 1579) and Editorial Standards (ID 17) inspected read-only through WordPress connector. Serialized Subscribe block HTML alone cannot prove genuine signed-out modal behavior. Public page fetch remained inaccessible in the external web/browser environment, so signed-out, received-email and actual PDF retrieval remain unverified.
- Mind Studio #171's latest handoff/#1093: edition **03** Zen12 Premium; edition **05** Hypnosis Live **Total Focus** (seller describes 33min/47MB), NOT different Hypnotize Yourself. Affiliation/permission, current checkout/refunds, exact earning link and approved live same-SKU guide remain unverified.

## Source-specific release process, without changing live systems

1. **Native consent/recipients:** privacy-preserving site-admin read of the actual WordPress `Email subscription` eligibility/status filter and import audit. Deduplicate `confirmed_signup` only on an independently verified native confirmation transition; never from an aggregate counter, landing view, submit click or `subscribe=success` URL. Keep any subscriber identity privately inside the platform; don't export or put it in source control.
2. **Visual preview, not a send:** with separate authorization to use an already existing unpublished editor draft, open Jetpack **Preview email** on desktop/mobile. Inspect both intended editorial and commercial presentations in the currently configured **excerpt** mode; record whether one CTA, source links, commercial disclosure and legally appropriate footer actually survive. Do NOT create/change WordPress posts or switch format without founder approval.
3. **Actual test delivery, only with distinct explicit final approval:** Jetpack supports **Send test email** to a user-approved recipient. An authenticated received RFC5322 copy can be privately tested through `audit(...)` and the boolean output recorded; do not upload the raw email or subscriber addresses to GitHub. The presence of an unsubscribe URL is not evidence it works; functionality needs an authorized opt-out-safe procedure. Current run **did not send any email**.
4. **Welcome/Fieldbook:** inspect a genuine *post-confirmation* welcome from an authorized inbox, compare configured URL, fetch and check actual PDF bytes/HTTP and readable 52-page contents. Media registration ID #1737, size 599,946 bytes, does not prove successful download or welcome receipt.
5. **Commercial-specific:** obtain named FV affiliate acceptance, explicit *email* promotional rights, approved exact SKU/link/tracking/refund/checkout evidence and a live vetted pre-sell buyer guide from Mind Studio before activating either of two commercial CTAs. Zen12 claims one-hour meditation equivalent and Total Focus effectiveness descriptions are **seller claims only**, not independently established FV assertions.
6. **Revenue:** Grok source `utm_content=asset_id`, `utm_medium=organic_social`, campaign `<topic_cluster>_pilot_2026_11`; email use `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_mind_pilot_2026_11`, `utm_content=issue_03_zen12` / `issue_05_total_focus` **only after CTA approval**. No names/emails in tags. Count 7/30-day settled, independently confirmed orders/commissions minus refunds/fees; clicks and leads are *not* sales. Net revenue/1,000 qualified human sessions is **NOT COMPUTABLE**.

## Conversion-first priority table

| Offer → step | Blocker | Change / experiment | Evidence/status | Owner |
| --- | --- | --- | --- | --- |
| Focus Fieldbook → confirmed lead | total/confirmed/unconfirmed/import nonadditive; eligible recipients unknown | Private source-of-truth status + consent reconciliation | **UNKNOWN** | Dispatch + Claude |
| Welcome → promised PDF | no genuine received post-confirmation message or PDF HTTP evidence | Authorized inbox review and PDF validation | **NOT VERIFIED** | Dispatch |
| Dispatch → article/guide | excerpt risks missing CTA, sources, footer and disclosure | Native non-sending email preview, then separately authorized received test | **NOT VERIFIED** | Dispatch + site QA |
| Zen12 and Total Focus guides → buyer | merchant approval/email rights and two live approved guides missing | Same-SKU partner approval and claim/price/refund QA | **HOLD_MERCHANT** | Mind Studio |
| Commercial email → lawful recipient | FV publisher postal address/unsubscribe rendering unverified | Privately attest address and inspect authorized received email | **NOT VERIFIED** | Dispatch + site admin |
| Settled payment → realized net revenue | no linked paid orders, commissions, refunds or fees | Payment/partner records joined only with consented, verified data | **NOT COMPUTABLE** | Commerce/Praxxis |

**Campaign allocation:** 4 editorial issues / 2 reserved affiliate issues; six letters remain HOLD_UNSENT. PR #49 frozen homepage remains outside scope. No new provider, email list, sends, schedules, imports, tracking scripts, affiliate activation, website edits, spending, or posting.

## Primary references, checked 2026-11-05

- [Jetpack Newsletter native preview/test distinction](https://jetpack.com/support/newsletter/)
- [WordPress newsletter appearance/excerpt and sender](https://wordpress.com/support/newsletter/email-appearance/)
- [Jetpack welcome, confirmation and button-only modal](https://jetpack.com/support/newsletter/customize-the-newsletter-experience/)
- [FTC CAN-SPAM commercial email guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [Zen12 seller's exact landing page](https://zen12.com/hnp)
- [Hypnosis Live Total Focus seller listing](https://hypnosislive.com/mental-skills/total-focus)
- [Mind Studio source handoff #1093](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1093)
