# Dispatch R258 — real received-message audit protocol, no sending

**Date:** 2026-11-10 14:31 UTC. **State:** ALL SIX HOLD_UNSENT; commercial 03/05 HOLD_MERCHANT. **Owner:** Issue #174, partner handoff #171, Focus #129, conversion #820.

## New substantive development

R257 introduced a release-evidence ledger and theoretical legal checks. R258 provides a **working, offline RFC5322/MIME inspector** for the day a founder-authorized, opt-in, controlled recipient receives a test message. Unlike a static HTML preview, the tool accepts raw multipart .eml bytes and checks actual **HTML and plaintext MIME parts**, the displayed From name, subject, visible postal-address text matching a separately verified Final Vestige address, visible unsubscribe words and HTML anchors, a List-Unsubscribe header, and off-domain or unsafe links. A header-only unsubscribe is not assumed sufficient for clear visible opt-out. **No real test email is currently authorized or has been examined.**

The summary deliberately suppresses sender and recipient email addresses, subject text, body copy, subscriber IDs, raw links and URL tokens; only a content SHA-256, byte length, booleans, counts and non-sensitive blocking codes leave the inspector. It has no email sending, provider, WordPress, HTTP, subscriber import, or publishing calls. An observed link is **never** evidence that opt-out actually works. The output always says HOLD_UNSENT even if every synthetic structural condition is true; founder approval and real inbox/legal QA remain independent.

Usage (future explicit authorization only): acquire the received .eml securely from the controlled recipient; distinguish **confirmation** vs **welcome** vs **newsletter**; independently verify the **real Final Vestige Studios physical mailing address**, then call inspect_eml(raw_message_bytes, publisher_postal_address=verified_address) in a private local runtime. Do not check in the raw message, mailbox address, tracked URLs or actual business address. Manually test the unsubscribe link only if its recipient owns and authorized the test mailbox; verify displayed address, mobile presentation, claim boundaries, deliverability and publisher identity. Neither this tool nor the attached tests can certify CAN-SPAM compliance or release an email.

## Exact source-of-truth snapshot

GitHub read: campaign master draft [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at d57ccdba3aee8f065e143e101c2945f4f3d01647, separate campaign readiness [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) at ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6, immediately preceding R257 [#1902](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1902) at f93c5fea342c2368ded0ea2000de4d96c6ae7fc9. None are merged; this change stacks only on R257 and does not touch #49 or the original six manuscripts.

Authenticated read-only Jetpack 2026-11-10T14:30:56Z: newsletter enabled, site_can_send=true, no send blockers, automatic new-post email **OFF**, full-post email mode, sender "Final Vestige Studios", reply-to "no-reply", welcome configured with 52-page Focus Fieldbook URL. Last five posts have never_sent_opted_out, not proof of never sending in the entire history. Diagnostics: 3 total, 3 confirmed, 2 unconfirmed, 0 suppressed; separate Jetpack followers: 3 WP.com, **0 email**, partial=false. These populations are not additive and cannot establish actual email-eligible addresses. Need private provider-filtered "Email subscription: Subscribed" count; no recipient PII queried.

Published /dispatch/ (WP page 523) and /focus/ (page 1579) both exist. Dispatch serialized block exposes a self-link Subscribe button; Focus public extraction includes an email input and gift interface. Neither proves real browser form interaction, independent double-opt-in or actual welcome receipt. Published /editorial-standards/ (page 17, reviewed 2026-08-23) requires primary sources, clear fact-versus-inference, careful numbers and disclosed commercial relationships.

## Exact official merchant-page review — no affiliate activation

- [Zen12 standard](https://zen12.com/hnp) advertises 12-minute brainwave MP3 meditation with an "hour of meditation" seller equivalence. NOT a product-specific independently established benefit.
- [Zen12 coupon video route](https://zen12.com/secret/) separately displays $87 struck out, $37 with a coupon, timed urgency, testimonials and a 12-level/48-MP3 package. **Never** copy price, countdown, claims or alleged study aggregate into a Final Vestige letter without specific verification; seller-page quotes are not a named affiliate approval.
- [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus) advertises a 33-minute, 47-MB audio, currently displaying a $24.44 single offer, $39.90 two-recording bundle and seller-stated 14-day refund. "100% focus" and brain "reprogramming" remain vendor promises, not verified outcomes.
- [Inspire3 affiliate portal](https://affiliates.inspire3.com/) describes general program affiliation, NOT Final Vestige account acceptance, email-promotional rights, issued earning URL or approved creative. Nov 10 connected-mail searches produced ordinary Inspire3 promotions and one older **subscription confirmation**, but **no independently verified named approval or post-confirmation welcome**. Absence in those searches is not absence in all account systems.

**Partner handoff:** Mind #171 must supply approved email channel, exact current offer, first-party live and fact-checked warm-up guide, link ownership, price/refund/cart and creative/audio permissions. Only then may Issue 03 or 05 be independently proposed for review. The original four-editorial/two-commercial allocation and all original CTAs remain untouched.

## FTC and evidence hierarchy

The [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) says commercial primary-purpose messages can include promotion of commercial website content. Four editorial slots are not a blanket statutory exemption. Validate message-specific truthful sender/subject, valid **publisher** postal address, clearly described working opt-out and applicable advertising identification for **each** issue. The FTC does not itself mandate a particular one-click mechanism; a compliant accessible opt-out must actually work. No Automattic, merchant or invented postal address substitutes for Final Vestige's address. Static preheader is not proved by delivered inbox text. A confirmation email is not a welcome email.

## Verifiable test evidence and gaps

Run Python standard-library tests with: python -m unittest -v test_inbox_evidence.py. **18/18 native Python tests** executed on the authored module/test source bytes. Fixtures use deliberately fictional .invalid addresses, fake no-action first-party unsubscribe URL, and "TEST ONLY" physical address. Tests include header-only unsub, hidden unsub, missing address, sender mismatch, suspicious external Zen12 link, lookalike hostname, JS scheme, oversize input, PII exclusion, redacted digest, and release immutability. GitHub source read-back must match local Git blob identities; QA is **not** a real WP received-email test, legal advice or permission to send.

**Highest-priority experiment:** founder-authorized *read-only* WordPress native preview without changing send controls. If preview requires setting sending ON, stop. A real single-mail delivery test remains separately unauthorized. Pending: actual subscriber count/consent, actual welcome receipt, actual postal/unsub, approved merchant emails, qualified-human denominator, authenticated settled sales. Report net revenue per 1k qualified sessions as **NOT COMPUTABLE** (not $0).

No WordPress changes, subscriber contact, publisher/test email, signup request, test send, affiliate link, commercial page, paid service, tracking script, merge or deploy.
