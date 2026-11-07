# R178 | Consent-to-revenue operating delta (review only)

**Status: HOLD_UNSENT.** Owner: Dispatch Issue #174. Canonical original manuscript PR #175, source-locked preflight PR #201; parent draft PR #1354. No substitution of existing copy, new platforms, tracking scripts, mail, posts, subscriber imports, merchant links or paid experiments.

## What the read-only site actually established on 2026-11-07 at 05:29 UTC

Authenticated WordPress Newsletter: subscriptions enabled, publish-to-email default **off**, full-content format, sender display “Final Vestige Studios,” reply-to **no-reply**, configured welcome with 52-page Seven Day Focus Fieldbook URL. Subscriber overview: **total 3 / confirmed 3 / unconfirmed 2**; these are **nonadditive** counters. Five most recent posts explicitly report `never_sent_opted_out`. The app says `site_can_send=true`, which is **capability**, not evidence of a sent message or any eligible audience.

Page **/dispatch/** (#523) contains a native `jetpack/subscriptions` block in edit markup. Page **/focus/** (#1579) contains live opt-in and a previously identified client-side gift-panel risk. Neither source alone proves a signed-out user can complete a verified confirmation or that a real welcome email reaches the inbox. WordPress site standards require archival-primary source checking, labeled uncertainty, editorial-commercial separation and corrections.

A bounded connected-mailbox search for merchant authorization surfaced three generic Inspire3-style promotional messages in September, **not Final Vestige partner acceptance or permission to advertise by email**; a separate search located the October 25 “Confirm your subscription” email, not a confirmed recipient status or Fieldbook welcome delivery. No private identifiers, email addresses, raw MIME or tokens are committed here.

## Native Jetpack preview: zero-send acceptance sequence

Do **not** create a WordPress post as a shortcut. The native Jetpack **Preview email** UI is available on an unpublished post in the WordPress editor, independently of **Send test email**; unlike a standalone HTML mockup, it tests the actual Jetpack output. A site editor with authorized existing unpublished post access can capture the UI *without publishing or dispatching*. Do not click Send test email, Publish or Schedule. If using an existing draft, do not save altered content or disturb other engineering owners. No existing appropriate unpublished editor document was established in this sprint.

Capture and review **subject**, **actual inbox preview/preheader behavior**, **brand display**, **full vs excerpt**, **main CTA**, **responsive/mobile rendering**, **footer postal address**, **unsubscribe affordance and destination**, and **affiliate disclosure beside CTA** (when applicable). A browser Preview does not prove actual received MIME, link functionality in a recipient client, or legal sufficiency; those need separately approved authorized proof. Fail closed until documented.

Official Jetpack guide (updated 2026-11-04): https://jetpack.com/support/newsletter/
FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## Source-aware traffic and privacy contract (proposal, not deployed)

Social creator Grok keeps platform asset ownership; before attributing, require the *actual* published URL, immutable `asset_id`, post timestamp, approved landing URL and platform's permitted CTA placement. Example planning convention: `utm_source=<channel>&utm_medium=organic_social&utm_campaign=<existing_approved_campaign>&utm_content=<real_asset_id>`. Do not fabricate IDs or count impressions as qualified-human sessions.

An email editorial link might subsequently use `utm_source=dispatch&utm_medium=email&utm_campaign=fv_dispatch_pilot_2026_11&utm_content=issue04_lycurgus` **only** after the existing attribution contract is approved and a native Jetpack test confirms the final link. The current review copy instead links to the already published, untagged first-party Lycurgus investigation.

The event `confirmed_signup` MUST only come from an authoritative provider transition confirming the address and valid consent. Use one salted or opaque person key, a stable provider event identifier, an event timestamp and source campaign if legitimately preserved. Deduplicate across runs; consent reactivation is not a newly acquired lead. Do not persist email addresses in public GitHub or send raw subscriber data to GitHub issues. Focus page visual gift success, submission clicks, counts and WordPress.com followers do not establish the event.

For the commercial numerator, use independently settled paid orders or final merchant reports, net refunds/fees/adjustments, and attribution to an actual campaign and asset. Denominator = qualified human sessions over matched 7-day/30-day cohorts. KPI = 1000 × **realized net revenue / qualified-human sessions**. If either component lacks trustworthy evidence, print **NOT_COMPUTABLE**; never substitute clicks, submissions, or order starts. With three *counted* subscriptions, do not infer email reach, A/B lift, or statistical significance.

## OFFER → STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER

| Offer | Funnel step | Blocker | Change / experiment | Evidence today | Owner |
|---|---|---|---|---|---|
| Seven Day Focus Fieldbook | Confirmed opt-in | UI gift panel not authoritative | Signed-out native provider status and controlled QA, without contacting list | **UNVERIFIED** | Claude / Site QA |
| Fieldbook | Welcome receipt | Only configured, no received welcome | Read-only received-message proof if appropriately authorized | **UNVERIFIED** | Dispatch |
| The Dispatch editorial | Native email preview | Manuscript HTML ≠ Jetpack MIME; preheader/footer unknown | Genuine non-sending native preview of authorized unpublished post | **UNVERIFIED** | Dispatch / WordPress editor |
| Zen12 Premium | Reader → approved independent guide | Guide not live; partner email permission, earning URL and acceptance unknown | Mind Studio verifies authenticated merchant terms and founder-approved live warm-up guide | **HOLD_MERCHANT** | Mind & Affiliate Studio |
| Dispatch commercial | Lawful send | Publisher postal/unsubscribe not verified | Genuine Jetpack preview then separately approved received-email/footer check | **HOLD_UNSENT** | Founder / Dispatch |
| Paid customer | Independently settled revenue | No qualified-human denominator, order/commission or refund feed | Commerce reconciliation using 7/30-day cohorts and real asset IDs | **NOT_COMPUTABLE** | Commerce / Praxxis |

## Fresh editorial candidate

R178's optional Issue 04 links to the *published* Lycurgus investigation rather than sending historical readers to an unrelated affiliate offer. It draws on the British Museum's curated collection record and October 2026 Sheffield research announcement. **Sheffield reproduced an optical effect; it did not establish the full original Roman manufacture procedure or historical intent.** The existing original Apollo 1 Issue 04 remains unchanged. No commercial offer, approval, live feature or revenue claimed.

**Required release decisions:** founder must separately approve final editorial copy, final sender identity/postal address, actual eligible list, timing, audience, preflight results and mail; Mind Studio must independently substantiate exact affiliate account and permissible email channel. Until then all six are **HOLD_UNSENT** and original commercial Issues 03/05 **HOLD_MERCHANT**.
