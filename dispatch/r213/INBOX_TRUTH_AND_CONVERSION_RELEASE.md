# Dispatch R213 — Six preheaders are NOT verified inbox previews
**Date:** 2026-11-08 08:35 PT. **Release:** HOLD_UNSENT. **Source-of-truth:** Issue #174, Mind #171, Focus #129, conversion #820. Stacked on PR #1603 exact head fe592c637fe25fbb8a2add53c21d09dde9bdace7. No canonical copy, website or recipient edits.

## New, directly evidenced defect: intent is not presentation
The R212 offline MIME fixtures place the proposed preheader in the nonstandard X-FV-Intended-Preheader header. That field does NOT establish that Gmail, Outlook or Jetpack will use it as an inbox snippet. R211 HTML has the declared preheader as a visible paragraph, but BEFORE IT displays (1) FINAL VESTIGE STUDIOS · THE DISPATCH, (2) REVIEW ONLY · UNSENT · NOT APPROVED, and (3) the visible subject heading. On exact GitHub source, the intended preheader is first visible text in **zero of six** HTML bodies. All six R211 HTML file identities matched the six R212 manifest identities.

This is a proven **source-preview assumption defect**, not evidence of an actual delivered-mail problem. Neither the offline HTML nor synthetic .eml was produced by Jetpack. Do not remove the review warning or unresolved legal placeholders until legal, platform, partner and founder approvals are in hand. Never label a cosmetic fix as an actual inbox test.

| Issue | R211 subject | First approximated source-visible text | Declared preheader first? | Release |
| --- | --- | --- | --- | --- |
| 01 | The stranger they didn't see change | FINAL VESTIGE STUDIOS / REVIEW ONLY / H1 | NO | HOLD |
| 02 | What Puységur's witnesses could actually know | Same review banner | NO | HOLD |
| 03 | What twelve minutes can—and cannot—tell you | Same review banner | NO | HOLD + MERCHANT |
| 04 | Apollo 1: the cause was bigger than a spark | Same review banner | NO | HOLD |
| 05 | Before buying a hypnosis recording, read the terms | Same review banner | NO | HOLD + MERCHANT |
| 06 | The notebook is not the verdict | Same review banner | NO | HOLD |

The new isolated source-only inspector (inbox_truth.cjs) exposes source-first-text, subject/H1 alignment, X-header metadata-only status, legal placeholders, synthetic sender, withheld commercial links and hard release blocks. Native test_inbox_truth.cjs contains offline regression cases across all six editions, unsafe UTM payloads and nonadditive subscriber counters. These tests, even if they pass, can never authorize email distribution.

## Actual provider preview — precise, consent-preserving route
Official Jetpack support says **Preview email** is available on UNPUBLISHED posts whether the per-post Send this post to subscribers toggle is on or off: https://jetpack.com/support/newsletter/ . This differs from the separately controlled Send test email action, which actually transmits a message. The present connected WordPress API exposes newsletter diagnostics and post/page read/write, but no verified native-editor preview operation. We have not created an unpublished post to gain editor access; WordPress changes are explicitly forbidden absent founder sign-off.

Only AFTER separate authorization for a WordPress editor draft: Claude/WordPress owner verifies per-post sending OFF, uses Preview email (NOT Send test), captures full mobile/desktop view and the email wrapper/actual first body text, and keeps the post unpublished. A visual preview still cannot prove delivery or effective opt-out. An actually RECEIVED test email to a founder-authorized mailbox would require separate permission. Verify a valid Final Vestige publisher mailing address and a working unsubscribe in qualifying commercial mail; Automattic's postal address from a confirmation email is not Final Vestige's. Do not store or show recipient personal information in public issues.

## Fresh live read-only WordPress evidence, 2026-11-08 16:36 UTC
Newsletter subscriptions ON; site_can_send TRUE; **new-post default auto-email OFF**; FULL content; sender name Final Vestige Studios; reply_to NO-REPLY; Fieldbook welcome message configured; five recent posts never_sent_opted_out, not delivered Dispatch campaigns.

Status counters: total 3, confirmed 3, unconfirmed requests 2, suppressed 0. Separate follower report: WordPress.com 3, email-only 0. **These measures are not additive. Unique eligible recipients and provider-confirmed new signups UNKNOWN.** /dispatch/ page 523 still does not clearly mention possible commission-earning recommendations, unlike /focus/ page 1579; /focus/ still tells people with in-app PDF difficulty to sign up again. Claude owns proposed copy changes; none was made. Published Editorial Standards page 17 requires primary sources, historical uncertainty and editorial independence from commercial relationships. Real final welcome receipt, Fieldbook external download and functional opt-out remain unverified. The older WordPress subscription-confirmation email does not establish delivery of the current welcome.

## Offer, actual merchant claims and reasons to hold
**Zen12, Issue 03:** official https://zen12.com/hnp describes 12 progressive levels and Premium 48 MP3s, with advertised refund promise. Any twelve-minutes-equals-one-hour meditation claim is seller language, not independent proof. Exact checkout/returns in practice, account-specific earning URL and permission to promote to emails are NOT VERIFIED. Mind #171's presell sources are drafts, not a live verified guide.

**Total Focus, Issue 05:** https://hypnosislive.com/mental-skills/total-focus describes 33 minutes and 47 MB. Seller advertises a 14-day refund; its FAQ at https://hypnosislive.com/faq adds five refunded sessions per year. Seller brain-reprogramming benefits are not independently proved for this product. Checkout, genuine use, issued affiliate URL and email rights remain UNKNOWN. Mind's latest R220 PR #1605 has unpublished guides and an unrendered video concept, not a sendable offer.

**Legal:** FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business requires truthful sender and subject, commercial-message transparency when applicable, valid publisher postal address and operative opt-out. Static reviewer placeholders do NOT prove compliance.

## One-offer conversion sequence and measurement
Grok's verified social asset_id and platform-supported link → real tagged Focus visit → provider-confirmed unique subscription/consent → actual welcome/Fieldbook access → four evidence-based editorial installments and at most two held commercial editions → approved Mind-owned buyer guide → permitted affiliate click → independently reported PAID order and settled commission → verified refunds/fees → realized net revenue per 1,000 qualified HUMAN sessions, 7/30-day cohorts. Mere clicks, downloads, follower counts, merchant newsletters and checkout initiation are NOT orders.

Email guide proposed UTM, inactive: source dispatch; medium email; campaign dispatch_pilot_2026_11; content issue_03_zen12 or issue_05_total_focus. Never include subscriber emails, hashes, recipient IDs, tokens, or nonapproved parameters. Grok owns actual asset IDs and distribution. Claude owns production analytics. Official YouTube documentation says URLs in Shorts description/comments are not clickable: https://support.google.com/youtube/answer/13748639?hl=en . Do not promise a clickable acquisition route without examining real profile/long-form links.

## Conversion-first blocker burn-down

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Zen12 → buyer | Named approval, EMAIL rights, issued URL, published guide missing | Verify private partner documentation and launch guide only after founder approval | PUBLIC SALES PAGE DOES NOT PASS | Mind / Founder |
| Focus → subscribed lead | 3/3/2 counters not a deduplicated email list | Provider-filtered eligible aggregate and consistent disclosure, no duplicate signup | UNKNOWN | Claude / Focus |
| Subscriber → Fieldbook | Configured welcome is not actual receipt | Inspect owned existing welcome + PDF without new opt-in | UNKNOWN | Dispatch / Focus |
| Dispatch → inbox | All six intended preheaders appear after review banner; native wrapper unknown | Founder-authorized unpublished draft and provider Preview email ONLY | SOURCE FAIL 0/6; ACTUAL INBOX UNTESTED | Dispatch / Claude |
| Email → compliant delivery | No verified FV mailing address, actual unsubscribe | Authorized received-mail legal and operational QA | UNKNOWN | Dispatch / Site QA |
| Reader → paid customer | No settled partner reports, fees/refunds or qualified denominator | Reconcile paid orders and 7/30-day qualified sessions | NOT COMPUTABLE (not zero) | Commerce / Praxxis |

## Release and ownership
Master #175, readiness #201, review alternatives #1597, source-synced MIME #1603, frozen homepage #49 and live WordPress were left intact. Founder approved development of a 4-editorial/2-optional-commercial draft, NOT sending. **ALL SIX HOLD_UNSENT; ISSUES 03/05 ALSO HOLD_MERCHANT.** No test email, subscriber contact, new list, WordPress write, social post, affiliate activation, payment or spending. This deliverable is a source-verifiable audit and code, not a native preview, legal signoff or paid-conversion claim.
