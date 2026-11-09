# Issue 06 | Subscriber-reentry correction candidate — NO SEND / NOT APPROVED
**Original source:** PR #175 `dispatch/campaign-2026-mind/issues/06-the-evidence-log.md`. **Revised source:** stacked draft R223. This file is a small review proposal, NOT an issue replacement.

### Actual observed funnel mismatch
The current Issue 06 ends with a sole CTA to `https://finalvestige.com/focus/`. The reader would already be a Dispatch subscriber, and the live Focus page's primary journey asks the visitor to subscribe again. The welcome message already includes the exact public PDF URL. Counting the reader's PDF click or a second subscription attempt as a new confirmed lead would inflate lead acquisition.

### Alternative (one CTA, no repeated signup)
> You've already joined The Dispatch, so you don't need to subscribe again to use the Fieldbook. Your welcome message has the 52-page edition, and you can open that same free PDF here.
>
> **[Open your Seven Day Focus Fieldbook](https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf)**
>
> Use the log to compare what happened across your week. It isn't a diagnosis, a product trial, or proof that a particular practice works.

### Release criteria
- Confirm the public PDF directly resolves on mobile and within in-app browsers, is the same COMPLETE 52-page edition, and has no sensitive customer data embedded.
- Sender and unsubscribe and publisher address verified in a genuine received Jetpack email; no real email without separate founder approval.
- Do not add an email address, token, user_id, PII, or unsupported tracking query to the PDF.
- If future analytics are approved, count separately: `email_cta_click` (tracked when actually supported), `pdf_access` (if accurately measured), and `confirmed_signup` only on provider-authoritative unique transition. None is a paid sale.
- Do not report new leads from a CTA that is explicitly serving existing newsletter readers.
- Obtain final editorial approval for substitution; keep original 4:2 / six-week pilot untouched.
