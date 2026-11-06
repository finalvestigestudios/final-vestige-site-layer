# R162 | 2026-11-06 05:37–06:00 PT | Dispatch email-eligibility truth audit

**Status:** DRAFT / source-controlled / read-only. Parent: draft PR #1254 at `b6d46c08b49699b987cac4c2579bf4c8dc480c2e`. The six original weekly issues in #175, readiness #201, and frozen homepage PR #49 must not change.

## A newly significant, measurable discrepancy

Live authenticated WordPress read-only snapshots at **2026-11-06 13:37 UTC** returned:

| Source | Value | Correct interpretation |
| --- | --- | --- |
| Jetpack Newsletter status | total **3**, confirmed **3**, unconfirmed **2** | Dashboard aggregates, **not five independent addresses**; not a recipient manifest |
| Jetpack Newsletter status | suppressed **0**, imported last 24h **0**, paid **0** | No suppression/import reported in this surface; does **not** attest per-recipient eligibility |
| Jetpack followers breakdown | `email: 0`, `wpcom: 3`, total **3** | **Zero legacy/email-only followers** in this breakdown; **not proof of zero email-eligible WP.com subscribers** |
| WordPress newsletter | `subscriptions=true`, `site_can_send=true` | Infrastructure can send; **not approval** and not delivery evidence |
| WordPress newsletter defaults | `email_new_posts_by_default=false`, `email_content_format=full` | Posting does not auto-send by default, but per-post override still possible |
| Sender/welcome | Final Vestige Studios; no-reply; configured Fieldbook PDF URL | Message configured, NOT received-email proof |
| Five recent post records | `never_sent_opted_out` | **Zero observed sends among these five**, not proof of zero lifetime sends |
| Provider media record #1737 | application/pdf; exact configured URL; 599,946 bytes | Media-record alignment, NOT actual successful file download or 52-page visual verification |

**Decisive unresolved question:** For the three WordPress.com-account followers, how many rows in **Jetpack → Newsletter → Subscribers → Email subscription** read exactly *Subscribed*? WordPress's November 4, 2026-reviewed guide states *Subscribed* means email, while *Not subscribed* means Reader-only, *Not confirmed* is not counted in the newsletter total; *Bounced*, *Emails paused* and *Not sending* are ineligible. See https://wordpress.com/support/subscribers/ . All 3 may be Reader-only, all 3 could be email-eligible, or a mixture; **do not report any as a verified reachable email audience**. Do not export, quote, or expose subscriber identities.

## Production funnel findings and limitations

1. Published Dispatch page #523 at https://finalvestige.com/dispatch/ contains a rendered Jetpack Subscribe anchor referring back to `?post_type=page&p=523` and no literal email input in the WordPress API rendering. Published Focus #1579 has a similar API artifact. Jetpack may hydrate differently to actual signed-out visitors: this is **a suspected first-click problem, not a confirmed broken form**.
2. Public WordPress mshots for both pages returned status **ready** at 390px; **pixels and actual user interactions were not inspected**. The earlier R160 no-submit Playwright probe is the correct handoff for Claude/Site QA in a browser-capable environment. Do not type, submit, create subscriber, or make POST.
3. Focus has an untrusted success URL parameter capable of displaying a success state without provider-confirmed email eligibility (prior code finding). Do **not** emit `confirmed_signup` from this URL, form display, button click, or thanks screen.
4. The only approved signup measurement **proposal** is a **single, provider-attested transition to Email subscription=Subscribed**, deduplicated by a privacy-safe opaque account key. Two legitimate paths: unconfirmed address → Subscribed after mail confirmation; existing verified WordPress.com Reader-only → Subscribed without an extra confirmation email. Never collect raw email, confirmation tokens, or cross-device identifiers in public analytics. Reconcile to provider's 7/30-day native counts using authorized private access.
5. The existing 52-page Fieldbook link matches media #1737, but **a delivered welcome** and a received actual email with functional unsubscribe plus the **Final Vestige** postal address remain unverified. Automattic's footer in a 2026-10-25 confirmation message is not Final Vestige's commercial address.

## Exact merchant alignment (non-commercial until authorized)

Primary proposed purchase: **Zen12 Premium** only; reserve Issue #05 for Hypnosis Live Total Focus under separate independent authorization. Seller's Zen12 sales page advertises **12 levels / 48 MP3s**; published offers are inconsistent, including aggressive '5,000-year-old brain hack' wording, scientific efficacy rhetoric, coupon/price drift. **None is adopted as independently demonstrated.** Inspect exact https://zen12.com/secret/ and relevant Premium page and account-specific approved promotional material, where legitimately accessible. Total Focus's exact https://hypnosislive.com/mental-skills/total-focus page describes **33 minutes / 47MB**, alongside unverified 'reprogramming' and '100% focus' claims. Do not repeat those claims as facts. Pricing, checkout, guarantee performance, email permissions, unique earning URL and any authorized creative **NOT VERIFIED**. Public affiliate portal existence is not Final Vestige account acceptance. Relevant Mind Studio issue #171 and draft PR #1256 remain separate owners.

## CAN-SPAM and disclosure release hold

Official FTC guidance https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires accurate identity/subjects, clear ad identification when commercial, valid **FV publisher** physical postal address, functional opt-out, and timely honoring of opt-outs. The FTC's https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking explains why a material relationship needs clear, hard-to-miss disclosure. **An independent static email footer is not evidence of genuine Jetpack email rendering.** Before any real send: separately inspect a legitimate non-sending *Preview email*; validate conditional link and final redirect, actual opt-out/address in authorized receiving context; get final founder sign-off for precise issue, audience and date.

## PRIORITIZED OFFER → FUNNEL STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER

| Offer | Funnel step | Blocker | Change / experiment | Pass / fail evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Focus Fieldbook | Guest arrival → native subscribe | API self-link, real guest interaction unknown | Execute R160 no-submit Playwright and inspect hydrated control | **UNKNOWN**; mshot ready only | Claude / Site QA |
| Focus Fieldbook | Signup → confirmed eligible | total3/confirmed3/unconfirmed2 vs email0/wpcom3 | Private provider-native counts by **Email subscription** statuses, no PII output | **UNKNOWN**; aggregates don't prove recipients | Dispatch |
| Fieldbook | Confirmed eligible → actual receipt | Email received not established | Read only existing consented received-mail evidence and safe download test | **PARTIAL** media URL matched; delivery UNKNOWN | Dispatch |
| Editorial Dispatch | Newsletter → reading | Footer/preheader rendering unknown | Native non-sending preview, postal+opt-out acceptance, no test send | **UNKNOWN** | Dispatch / Claude |
| Zen12 Premium | Relevant reader → verified guide → purchase | Approval, email permission, live guide, final redirect missing | Mind Studio submits dated account-specific proof and buyer-appropriate guide | **HOLD_MERCHANT** | Mind Studio |
| Paid transaction | Buyer → net revenue | No independently settled order, fees, refunds or qualified-human denominator | Weekly 7/30-day first-party/partner reconciliation | **NOT COMPUTABLE** | Commerce / Praxxis |

**Governance:** All six weekly newsletters **HOLD_UNSENT**; Issues 03 and 05 **HOLD_MERCHANT**. No sends, test messages, settings changes, new signup list, publishing, affiliates activated, spending, social posts, or changes to homepage PR #49. This work is a non-live test and documentation branch only.

## Independent executable QA

`node --test dispatch/campaign-2026-mind/r162/test_provider_truth.cjs` exercises privacy, count non-additivity, empty evidence, existing WP verified account enrollment, true double opt-in transition, duplicate attempts, misleading success URL, and revenue truth. The source never fetches URLs, contacts recipients, posts, or sends mail. **Synthetic unit-test counts MUST NOT be reported as current eligible recipients, subscribers or commercial conversions.** This is a gate implementation, not an event installed in WordPress.

## Additional source-of-truth links

- Canonical campaign and master approvals: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 ; PR #175 and readiness #201.
- Mind commercial approval owner: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171
- Focus owner: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129
- Conversion charter: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820 and #818.
- Published Editorial Standards: https://finalvestige.com/editorial-standards/
- WordPress provider: https://wordpress.com/support/subscribers/ and https://wordpress.com/support/newsletter/send-newsletter-emails/
