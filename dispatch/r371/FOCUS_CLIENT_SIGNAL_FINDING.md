# R371 — Focus client-visible gift state is NOT a confirmed subscriber receipt
**2026-11-14 PT / source-only, HOLD / no live changes.** This is a scoped clarification to Issue #129 and the Dispatch #174 consent gate, not a new email platform or a claim that the free PDF must be paywalled.

## What was inspected, not inferred
Authenticated WordPress **read-only** page response at `https://finalvestige.com/focus/`, page **1579**, last modified **2026-11-05T17:44:02**: inline script `id="fvf-gift-v2"` controls the previously hidden "Your fieldbook is ready to download" element. Current client logic reads `URLSearchParams(window.location.search).get('subscribe')`; it shows the gift whenever that parameter is nonempty and *not* one of five explicitly blocked strings: `invalid_email`, `error`, `blocked_email`, `opted_out`, `blocked`. It also shows the gift for a container class with `is-subscriber`. **No provider-side email confirmation or unique eligible-recipient receipt is consulted by this client logic.**

Offline tests of this verbatim script fixture demonstrate that `?subscribe=unconfirmed`, `?subscribe=failed` and any unrelated nonempty value reveal the gift. That is **a visible-content transition**, not evidence that someone signed up, confirmed an email, opened a welcome message, or could receive newsletters. The PDF is a free public asset; this is **not** a security breach or claim that the PDF should be hidden behind consent. The issue is *misinterpreting browser presentation as a real marketing conversion* and possibly showing a success-sounding label before confirmation.

The actual browser-resolved Jetpack form/redirect behavior has **not** been verified. WordPress's page-content API serializes a Subscribe block differently from an active browser form. No form was submitted and no subscription created during this investigation.

## Independent authenticated newsletter state — Nov 15, 2026 05:39 UTC
- Jetpack newsletter `subscriptions=true`, `site_can_send=true` and `email_new_posts_by_default=false`.
- Newsletter classified `total=3; confirmed=3; unconfirmed=2; suppressed=0`; **do not add 3+2 as unique eligible inboxes**.
- WordPress Stats follower breakdown `wpcom=3; email=0`. This is a distinct provider surface, not a confirmation that recipients are zero. **Actual direct email eligibility remains UNKNOWN.**
- Email content `full`, sender name Final Vestige Studios, reply-to `no-reply`. Welcome *configured* with PDF asset URL, receipt **not observed**.
- Five recent post notifications `never_sent_opted_out` — not evidence that newsletter delivery is working.

WordPress explicitly excludes unconfirmed subscribers from its total and recommends filtering **Email Subscription = Subscribed** to determine eligible email recipients: https://wordpress.com/support/subscribers/ (last reviewed 2026-11-04).

## Required correction, owner and release line
**Owner Claude/Focus (#129):** keep the free Fieldbook free and accessible; redesign gift state copy as an *available download* rather than a confirmed-subscription receipt; treat browser `subscribe` query and CSS class as UX only. If tracking a real `confirmed_signup`, it must originate from a deduplicated authoritative WordPress/Jetpack provider confirmation record, with a source timestamp and recipient eligibility, and must be verified privately (no published email or names). The client cannot forge `confirmed_signup` by URL or class changes.

**Owner Dispatch (#174):** email copy must not conditionally promote purchasers based on a browser gift state. Do not count `focus_pdf_click`, `subscribe=anything`, pageviews or follower classifications as a confirmed lead. The new tests measure client behavior offline, **not** live browser signups, email delivery or a usable recipient list.

**Owner Founder / Dispatch:** validate real unsub + Final Vestige qualifying physical mailing address through a non-sending *native* Jetpack preview; do not infer those from static HTML. A real test email needs separate approval.

**Owner Mind/Commerce (#171):** both reserved commercial slots, #03 Zen12 and #05 Total Focus, require SKU-specific Final Vestige EMAIL-channel approval, issued earning URL, approved live independent guide, actual referred checkout terms and valid disclosure before activation.

**Release state:** `HOLD_UNSENT` all six; `HOLD_MERCHANT` #03/#05. Original PR #175 unchanged. No emails, test emails, new subscriber contacts, WordPress mutations, spending, merge or publication.
