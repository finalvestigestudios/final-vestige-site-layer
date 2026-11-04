# R111 — subscriber reachability and private conversion integrity | 2026-11-04
**HOLD_UNSENT • Dispatch master #175 • readiness #201 • stacked on R110 #920 • Issues #174/#129/#171/#820.**

## Highest-impact independent finding: R110 had an overclaim
R110's `evaluateConfirmedSignup()` returned `reachable:true` as soon as native status was `Subscribed`. A valid opt-in is **not** delivery eligibility or a successfully received email. The original R110 aggregate already correctly had `email_reachable_subscriber_count:null`. R111 changes the per-event value to **`reachable:null`** to prevent downstream UI from claiming deliverability, then adds explicit regression tests. This is a correctness/safety patch, not a sending feature. No original six issues or approved creative were touched.

## Authenticated WordPress snapshot: 2026-11-04T10:34 UTC
- Connected `wpcom_jetpack_newsletter.status`: total **2**, confirmed **2**, unconfirmed **2**, suppressed **0**; five recent post sends have `never_sent_opted_out` and `send_subscription flag is false`. No sent/delivered count.
- Connected `wpcom_jetpack_newsletter.get_settings`: enabled; `email_new_posts_by_default=false`; `email_content_format=excerpt`; `reply_to=no-reply`; from name Final Vestige; configured welcome has exact complete 52-page PDF URL.
- Other reported metric: WordPress.com followers **2**, email followers **0**; it is a different report, not two more subscribers and not proof zero reachable recipients.
- Official WordPress subscribers docs say pending/unconfirmed excluded from main total; **2 total + 2 pending is logically possible and not proof 4 distinct people**. Native per-recipient `Email Subscription: Subscribed` eligibility aggregate remains absent. R111 separates all counters and NEVER computes a send audience.
- Connected WordPress read-only `pages.get` IDs 1579 / 523: each contains **one** Jetpack Subscribe block. Focus page already says that occasional recommendations may earn commissions, but Dispatch page currently says only “Unsubscribe anytime”; consent-parity fix in R109 is not live.
- Connected `pages.get` Editorial Standards ID 17: independent primary sources, visible uncertainty/corrections, disclosures; no seller claim may be treated as historical scientific evidence.
- The 2026-10-25 known confirmation email is not proof of an actual welcome. Earlier targeted Gmail finds no matching received Fieldbook welcome in connected mailbox; absence elsewhere is NOT proven.

## Concrete offer → funnel → blocker → experiment → evidence → owner
| Offer & funnel step | Most important blocker | Proposal / change | PASS evidence | Current result | Owner |
| --- | --- | --- | --- | --- | --- |
| **One Zen12 candidate** → email guide → paid order | Named FV email permission, earning link, buyer privacy and first-party live guide NOT verified | Mind owns final eligibility; no direct affiliate hrefs or promotion; R114 #916 guide is draft | Merchant acceptance/email terms + authorized live guide + vendor-confirmed paid sale, fees/refunds | **HOLD_MERCHANT** | Mind / founder / Claude |
| **Fieldbook** → native confirmation | R110 equated opt-in with deliverability | Change `reachable:true` → **null**; keep two native opt-in paths | Native status transition, consent, independent private deliverability filter | **Tested synthetic, live eligibility UNKNOWN** | Dispatch / Site QA |
| **Dispatch/Focus** → welcome and promised download | No original received MIME, PDF access and unsubscribe proof | Read-only R108 inspector on *already received, authorized* evidence only; no new subscriber or email | Real received MIME + correct PDF response, native opt-out + publisher address | **HOLD** | Dispatch / QA / founder |
| **Six original issues (4 editorial/2 commercial)** → inbox | Excerpt setting could truncate source links, CTA and disclosure; exact revised manuscript selection not made | Use #175 master integrity and #201 per-issue gates; verify actual Jetpack preview/received rendering only with separate authorization | Preheader, excerpt, CTA, sender, postal and unsub in actual received MIME | **HOLD_UNSENT** | Dispatch / Claude |
| **Grok asset** → confirmed lead → customer | No verified asset ID, email transition or authoritative purchase/fee/refund join | Honor TASK-008 asset IDs and #820 existing analytics; suppress tiny cohorts in public dashboard | Verified 7/30d qualified-human sessions & independent paid order records | **Not computable (N/A)** | Praxxis/Grok, Claude |

## What was built and tested, not live
- R111 module `eligibility.mjs`: strict offline WordPress count normalization; explicitly nulls actual email eligibility, delivery and opt-out evidence; does NOT add distinct pending+confirmed, and never uses followers as recipients.
- `evidenceReadiness`: eight specific legal/delivery/commercial proofs, with vetted evidence reference format. **Hard-coded sending_authorized=false even if all synthetic proofs passed.** A real campaign can only follow independent human/founder review, not a button in this tool.
- `publicConsentScorecard`: suppresses public lead counts for groups below 20; exposes no person identifiers, email, hashed subscriber digest, event ID or personalized unsubscribe token. Merchant orders/net revenue always null unless independently audited in owner system; do not feed this module fabricated revenue data.
- Changed R110 result `reachable:true` to `reachable:null`; no additional production publisher analytics code.

## Source-specific exact seller / FTC check (2026-11-04)
1. https://zen12.com/hnp — seller describes a 12-minute audio session as equivalent to an hour of meditation and uses efficacy language; **not independently verified for Zen12**.
2. https://hypnosislive.com/mental-skills/total-focus — seller lists **33 min / 47 MB**, with changing listing and bundle price fields; no fixed price, guarantee or efficacy promised in email.
3. https://inspire3.com/privacy/ — explicitly allows referring affiliates to receive **buyer name, email and purchased product details**. Consent, privacy and named partner terms are unresolved.
4. https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business — commercial email valid publisher postal address, clear opt-out, truthful subject/sender and ad disclosure.
5. https://wordpress.com/support/subscribers/ — native subscription status and pending exclusions.
6. https://wordpress.com/support/newsletter-settings/ — existing WP accounts can subscribe without new confirmation email, excerpt mode.
7. https://finalvestige.com/editorial-standards/ — source/evidence integrity and commercial independence.

**No campaign emails, preview/test emails, live site writes, subscriber mutations/imports, merchant links, new services, extra analytics, purchases or spending.** The master 4/2 plan remains draft only. Net revenue per 1,000 qualified human sessions is **N/A**, not zero. Legal proof does not become valid by being simulated; the founder must provide a genuine FV mailing address through an approved private route and approve the exact creative, audience, schedule and sending separately.
