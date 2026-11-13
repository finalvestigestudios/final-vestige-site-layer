# R322 | Native Jetpack inbox + verified consent witness protocol

**Non-sending review.** No WordPress CMS write, new draft, test message, subscriber contact or newsletter setting change was permitted/executed by this sprint. This document is a proposed QA sequence for the founder and responsible operators; it is **not** authorization to run it.

## 1. Preserve the configured infrastructure

Authenticated 2026-11-13 05:34 UTC: newsletter enabled and send-capable; default new-post email **OFF**, full-text, From **Final Vestige Studios**, Reply-to **no-reply**, welcome text configured with a 52-page Fieldbook link. Do not switch email defaults, activate a new list, import subscribers or silently enable post-specific send flags. Five recent items marked `never_sent_opted_out` are **not** proof of historic lifetime sends.

WordPress official [email preview guide](https://wordpress.com/support/newsletter/email-appearance/): while editing a post, select Newsletter → Email → **Preview email**; preview can work with the post-specific sending toggle OFF. It also has **Send test email**; do not choose that without specific founder authorization. [Send guide](https://wordpress.com/support/newsletter/send-newsletter-emails/) says post publication/scheduling is how a newsletter is actually dispatched; a draft campaign is not an independent time-triggered drip service. An authorized saved draft may be needed to access the genuine preview; this sprint did not create one.

## 2. Exact proof checklist before any final approval

| Step | Evidence to obtain privately | Pass standard | Current |
|---|---|---|---|
| Authenticated provider audience | Site subscription and actual email delivery eligibility, excluding bounced/paused/Reader-only | Recipient population is reconciled without disclosing addresses | UNKNOWN |
| New signup event | Non-account-holder link-confirmation **or** existing WP-account immediate new enrollment | Verifiable unique source event and consent, not form submission/old active snapshot | UNKNOWN |
| Fieldbook welcome | Actual welcome recipient-side message **only after separately authorized safe test** or existing recipient-owned verified record | Received message contains working authorized 52-page PDF link | NOT TESTED |
| PDF | Verified HTTP retrieval and open on desktop/mobile, actual page count and contents | File opens as intended and rights held | NOT VERIFIED |
| Subject/preheader | Actual WordPress sender header and native preview/inbox preheader | No fabricated standalone custom preheader control | NOT VERIFIED |
| Legal footer | Received native email source + desktop/mobile screenshots | Clear Final Vestige valid physical mailing address, sender and effective opt-out | NOT VERIFIED |
| Unsubscribe | Separately authorized safe exercise / documented provider confirmation | Recipient can stop marketing mail, opt-out honored, no unauthorized re-enrollment | NOT VERIFIED |
| Partner email rights | Account-specific Inspire3 approval and channel policy from authenticated partner dashboard/agreement | EMAIL permitted for exact brand/creative/link and destination | NOT VERIFIED |
| Guide + merchant | Mind-owned guide public, independently vetted; issued earning URL and current terms | Guide URL and actual seller checkout align with correct tier | NOT VERIFIED |
| Paid outcome | Merchant settlement/payable commission + refunds/fees with source-linked cohort | Verified net revenue, not clicked links | NOT VERIFIED |

The WordPress support article [last reviewed 26 Oct 2026](https://wordpress.com/support/newsletter-settings/) states existing WordPress.com account holders can skip confirmation email and directly receive the welcome, while other subscribers must confirm first. A failed search for a confirmation email is therefore **not** proof that no valid signup occurred, and a confirmation invitation by itself does **not** prove welcome delivery.

## 3. Actual publisher address versus merchant address

Official FTC [CAN-SPAM compliance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business): commercial email must have accurate headers and nondeceptive subject, identify promotional character where applicable, include the sender's **valid physical postal address**, provide opt-out and honor requests. The Act can also apply to ads for content on commercial websites, requiring primary-purpose review for every final issue, not a blanket editorial exemption. Do not insert the WordPress.com/Automattic sending address or Inspire3's London address as **Final Vestige's** legal postal address.

Do not paste subscriber addresses, raw MIME with email identities, unsub tokens, affiliate publisher IDs, account dashboards or postal information if private into GitHub. If verification is later authorized, keep evidence private and post a redacted attestation (date, roles, outcome, file hash/ref).

## 4. Tiny-sample and revenue safeguards

Current WordPress aggregates total=3, confirmed=3, unconfirmed=2 and WP.com followers=3 versus direct email followers=0; these are **overlapping / different classifications**, not 5, 8 or 0 known deliverable people. No confidence intervals or A/B uplift claims are meaningful for a tiny list. A provider tally alone cannot prove confirmed events were *new this week*. The first-party confirmation event must be deduplicated and timestamped.

For Issue 03, only a future independently researched **Zen12 Premium** guide can serve as the proposed commercial CTA, and for Issue 05 only a vetted **Total Focus** guide. Neither route is currently approved to activate. Seller efficacy assertions remain vendor claims. Neither affiliate outbound click nor checkout start is a settlement. Compute net revenue per 1,000 qualified human sessions only from independently verified actual session counts and settled revenue less refunds/fees; otherwise label NOT COMPUTABLE.

## 5. No-send decision

This package is a protocol, not a production test. It does **not** establish deliverability, native WordPress rendering, list consent, double opt-in for WordPress account holders, affiliate permission or a paid sale. The original six newsletter drafts stay HOLD_UNSENT, with Issues 03 and 05 additionally HOLD_MERCHANT. Founder must separately approve any WordPress draft creation, real received-email test, launch audience, schedule and creative.
