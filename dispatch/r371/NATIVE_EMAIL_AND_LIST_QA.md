# R371 — WordPress-only non-sending release QA, test specification
**Source:** official WordPress.com newsletter [subscribers](https://wordpress.com/support/subscribers/) (reviewed 2026-11-04) and [email appearance](https://wordpress.com/support/newsletter/email-appearance/) (reviewed 2026-11-09); FTC [CAN-SPAM Q&A](https://www.ftc.gov/business-guidance/blog/2015/08/candid-answers-can-spam-questions). No backend or WordPress writes occurred.

### Recipient and confirmation gate
Open Jetpack → Newsletter → Subscribers **privately** using an appropriately authorized account. Filter **Email Subscription = Subscribed**, distinguish free/paid email recipients from Reader-only followers, exclude not confirmed, bounced, paused and not sending. Record only aggregate counts, observation time, source and filters in private compliance evidence. Do not export names/emails, upload lists, or assert `confirmed_signup` for records without actual provider confirmation. Current status total 3 / confirmed 3 / unconfirmed 2; Stats wpcom 3 / direct email 0 — do **not** add these as a count of deliverable addresses.

### Native preview, no send
Use the WordPress editor's Newsletter sidebar → **Preview email** on an existing *unsent* draft where available. Keep 'Send this post to subscribers' OFF. Observe desktop, tablet and mobile; capture only non-PII QA: subject/preheader, actual full body, CTA, disclaimer beside offer, alt/semantic labels, footer including correct Final Vestige physical mailing address and real rendered unsubscribe affordance. The separate **Send test email** action is explicitly NOT authorized. Do not create/modify/publish even a draft post merely to access the preview under this brief; if unavailable, record UNKNOWN.

### Legal/commercial classification
FTC guidance requires a truthful subject and sender, a valid physical mailing address and effective opt-out in commercial mail, even with recipient opt-in (opt-in removes only the ad-label requirement, not other duties). A *licensed* USPS PO box or qualifying registered private mailbox can satisfy physical-address requirements; **Automattic/WordPress address cannot silently stand in for Final Vestige's address**. Where promotional content changes primary purpose, get a legal/editorial review. A static preview footer containing unresolved placeholders is a FAIL. HTML-only tests cannot verify actual unsubscribe functionality.

### Welcome and free asset
WordPress newsletter settings say a 52-page Fieldbook link is in the configured welcome. A 2026-10-25 confirmation email is NOT received-welcome evidence. No test email, new subscription or download was triggered. Public `/focus/` embeds a real PDF URL, but server delivery from a guest context remains UNVERIFIED. Use founder-authorized existing inbox/recipient test; do not solicit private addresses into GitHub or put confirmation links in logs.

### Explicit no-send release matrix
- All original editions #01, #02, #03, #04, #05, #06: `HOLD_UNSENT`.
- Commercial #03 Zen12 and #05 Total Focus: additional `HOLD_MERCHANT`.
- PR #201 fallback letters and later alternative candidates: `NOT_ADOPTED`.
- Homepage #150 and frozen PR #49: NO TOUCH.
- No send, no test send, no WordPress write, no affiliate activation, no tracking change, no financial expense.
