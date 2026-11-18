# Dispatch R435 — Lead truth before email volume
**Review-only; six canonical issues HOLD_UNSENT.** Stacked on [draft PR #2930](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2930), owner [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), consent [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), revenue [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Frozen PR #49 and production WordPress untouched.

## Finding that changes the conversion analysis
Authenticated, READ-ONLY live /focus/ source contains a gift display script: any nonempty `?subscribe=` parameter not in the short blocked-value list can reveal the PDF download panel; a Jetpack `is-subscriber` CSS class may also reveal it. These are **browser/UI conditions, not a provider-confirmed, unique, deliverable email subscription**. A frontend event named `focus_pdf_click` marks a click, not an email opt-in. No `confirmed_signup` string appeared in the live Focus page's stored markup during the inspected read.

The 52-page PDF **is recorded** as WordPress Media ID 1737, `application/pdf`, size 599,946 bytes, with the same source URL present in the configured welcome and Focus page. The public HTTP/PDF download and delivered welcome remain unobserved, and a PDF-access click cannot stand in for a consent transition.

## Files and read-only acceptance
- `FOCUS_UI_VS_CONSENT_WITNESS.md`: exact observed UI logic, separate provider categories and privacy-safe acceptance.
- `confirmed_signup_contract.cjs` and `test_confirmed_signup_contract.cjs`: pure, no-network evidence classifier and rejection tests. Not deployed. Distinguishes WordPress.com Reader followers, UI events, provider-confirmed transitions, actual deliverable inbox eligibility.
- `ONE_OFFER_PROGRESS_PATH.md`: no-sending subscriber-to-buyer path with the founder's six-issue 4:2 allocation and one verified product as a precondition; segmentation is a hypothesis only.
- `MERCHANT_EMAIL_RIGHTS_DOCKET.md`: product/FTC source-linked commercial hard HOLD.
- `OFFLINE_FOUNDER_WITNESS.html`: accessible offline six-issue review and decision board. NOT an actual email preview.
- `QA_RECEIPT.md`: test and GitHub source-readback results, limitations.

## Immutable boundary
No canonical issue is adopted or rewritten. No post/email/test-email, platform or subscriber setting mutation, new signup list, subscriber contact, affiliate link, commercial publication, tracking-script installation, social-content scheduling, PR merge, or money spent. A passed test **never releases an email**. Founder final copy/audience/issue/date authorization is a distinct gate after legal, deliverability, merchant and native preview evidence.

**Source of live reads:** authenticated WordPress Jetpack status/settings, pages /focus/, /dispatch/, /editorial-standards/, Media read and posts; captured 2026-11-18 00:31–00:45 UTC. Public search source fetch limitations noted in the witness.
