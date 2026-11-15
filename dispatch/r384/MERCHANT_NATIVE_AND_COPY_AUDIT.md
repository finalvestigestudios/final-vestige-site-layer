# Dispatch R384 — Original-copy, native email and exact-merchant discrepancy audit

Read-only review: 2026-11-15 18:36 UTC. Owner [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Original draft [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) unchanged at d57ccdba3aee8f065e143e101c2945f4f3d01647; QA [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) unchanged; parent [#2647](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2647) at e431bcea34d5dade1f8b13733afbe7b9f8e091bf.

## Snapshot: Jetpack owns the only newsletter/list

Authenticated WordPress newsletter status: enabled, automatic new-post emails OFF, email format FULL, from name "Final Vestige Studios", reply-to "no-reply", welcome message configured with the 52-page Fieldbook PDF URL. Site reports `site_can_send=true` but that is technical capability, **not authorization**. Subscriber dashboard total **3**, confirmed **3**, unconfirmed **2**, suppressed **0**, paid **0**; do not add 3 + 2 or assert three deliverable email inboxes. Separate followers endpoint reports WordPress.com **3** and direct email **0**, so those categories do not identify an actual deliverable audience. Five latest post records `never_sent_opted_out`; no delivered campaign email established. Native WordPress Preview email, genuine received email, legal footer and opt-out all unverified.

WordPress `/dispatch/` page ID 523 remains public with native subscribe block; `/focus/` page ID 1579 presents one existing Jetpack signup and Fieldbook gift panel. Focus client-side code responds to a `subscribe` URL query value and DOM state. This is a **UI convenience**, not proof of provider-confirmed signup or successful welcome delivery; count only a provider-authoritative confirmation and verify a genuinely received PDF link before attributing subscribers to a traffic source. No page settings changed.

Editorial Standards `/editorial-standards/` page ID 17 requires documentary sourcing, uncertainty, qualified claims and financial independence.

## Specific seller page comparison (volatile, not publisher referral checkout)

| Product and exact page | Read-only observation | What this does NOT prove |
|---|---|---|
| Zen12 standard https://zen12.com/getstarted | Seller lists 12 levels, 48 MP3s, manuals, bonuses, support; price reported $87.99 in other recent snapshots | No named FV referral price, product-specific efficacy, or publisher affiliate EMAIL permission |
| Zen12 separate promotion https://zen12.com/secret/ | Public seller copy explicitly advertises $37 coupon against an $87 reference, plus unsubstantiated general '3000 studies' claim | Neither applicable referral price nor independent randomized test of Zen12 |
| Total Focus exact SKU https://hypnosislive.com/mental-skills/total-focus | Current fetched HTML shows **$2** next to **$22.95** reference and a two-audio bundle at **$4**; seller describes **33 min**, **47 MB**, author J.A. Amos | Previous R379/R383 snapshots displayed **$17.95** and **$24.44**. Price differences demonstrate volatile presentations, not universal price or referral checkout; no product-specific efficacy established |
| Inspire3 public network https://affiliates.inspire3.com/ | Public sign-up/marketing page describes a special link and promotional commission expectations | This is not evidence of account acceptance, allowed EMAIL placement, issued earning URL, approved creative, exact-SKU approval or an actual paid commission |

**Claim alignment:** Total Focus seller promises '100% razor-sharp concentration' and 'reprogram your brain'; these are vendor promotional claims and **must not** appear as fact. Zen12 sales page refers to a '5000-year old brain hack' and thousands of studies, not independent evidence for the specific SKU. Even wider meditation/hypnosis literature cannot be imported as proof of either recording's advertised results. Avoid fixed prices in draft Issues 03/05 until authenticated final referred checkout and applicable refund terms are reviewed.

Connected Gmail exact searches found historical general seller marketing but no named Final Vestige publisher acceptance or EMAIL creative/link approval. A focused exact Fieldbook/Dispatch welcome search found no match in the connected mailbox; that **does not** prove welcome failure for other subscribers. No private addresses, headers, tokenized links or message bodies are copied here.

## Original six: honest conversion review, no modifications

| Issue | Kind | Current principal content/action | Highest impact bottleneck |
|---|---|---|---|
| 01 | Editorial | Puységur archive | Same destination as 02; reader lacks immediate concrete test. R384 Cottingley optional *not adopted* |
| 02 | Editorial | Puységur source archive | Valuable three-question rubric but near-duplicate landing destination and promise |
| 03 | Commercial | Zen12 guide placeholder | No live guide, exact SKU earning link or email permission; near-offer disclosure present; HOLD_MERCHANT |
| 04 | Editorial | Live Apollo 1 article | Subject 'Fourteen seconds' ambiguously asserts a duration; HOLD_COPY |
| 05 | Commercial | Hypnosis Live guide placeholder | Exact Total Focus SKU/price/claims not settled, partner EMAIL permission and live guide absent; HOLD_MERCHANT |
| 06 | Editorial | /focus/ opt-in landing | Existing subscribers risk returning to signup instead of directly using the already-delivered free PDF |

## Platform/compliance requirements

WordPress [send documentation](https://wordpress.com/support/newsletter/send-newsletter-emails/) reviewed 2026-08-06 states **post title becomes email subject**; [email appearance docs](https://wordpress.com/support/newsletter/email-appearance/) reviewed 2026-07-08 separate **Preview email** (non-sending visual) from **Send test email** (real send). A custom speculative preheader has no verified native mapping. Do not claim HTML specimens reproduce a WordPress MIME email.

FTC [CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful headers/subjects, appropriate marketing identification, valid **Final Vestige** postal location (not merchant or Automattic postal address), a functioning opt-out path and compliance with suppression. A synthetic footer does not comply.

**DECISION:** Six original issues HOLD_UNSENT, two HOLD_MERCHANT, Issue 04 HOLD_COPY. No native preview, send/test-send, publisher legal address, actual unsub, subscriber confirmation or independently settled commission verified. Founder approval remains required for every send.
