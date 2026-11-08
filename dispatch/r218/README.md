# Dispatch R218 — Focus gift visibility is not confirmed signup (draft, no deployment)

**Priority: revenue truth and consent.** New finding, not a replacement for R215–R217. The issue is not that the PDF is accessible: it is that the live browser unlock cue is independent of provider-verified opt-in, making it **invalid as a confirmed_signup conversion event**. The browser-only code should not establish audience growth or eligibility for commercial nurture.

## Read-only sources checked Nov 8, 2026
- WordPress published Focus page #1579, modified `2026-11-05T17:44:02`, authenticated content (including actual JavaScript).
- Published Dispatch page #523, modified `2026-11-05T20:01:31`; separate Jetpack signup.
- Editorial Standards #17; original newsletter issue #174 and Mind issue #171.
- Newsletter status as of `2026-11-08T21:32:44Z`: total=3, confirmed=3, unconfirmed=2, suppressed=0; five recent posts `never_sent_opted_out`. Settings at 21:32:45Z: subscriptions ON, auto email new posts OFF, FULL text, Fieldbook welcome configured. Follower API: WordPress.com=3, email-only=0. None can independently establish *email-eligible recipients* or successful Fieldbook delivery.
- Canonical six-issue PR #175 remains at `d57ccdba3aee8f065e143e101c2945f4f3d01647`; readiness #201 and R217 #1635 unchanged.

## Finding: confirmed-lead false positive risk
Focus page JavaScript reveals the PDF gift card for any **nonempty** `subscribe` URL value except five known errors, or for any subscription container class matching `/\bis-subscriber\b/`. Examples `?subscribe=pending`, `?subscribe=failed`, and `?subscribe=arbitrary` render the gift as visible according to the current script; no provider confirmation is checked. A hyphen-wrapped matching class also matches the regex, though whether this occurs on real visitors is unknown.

This is **verified program behavior under synthetic inputs**, **not evidence of actual inaccurate lead events or of real subscriber counts**. No signup analytics event implementation was observed in this inspected Focus snippet. Nothing was tested on real visitors and no evidence of user exploitation is claimed. The PDF can be freely accessed from a published link; the gift's visibility is not proof of consent.

## Delivered, scope
- `focus_client_gate.cjs`: an offline reproduction of visible browser conditions, a report that NEVER counts a confirmed lead, a structural-only sample provider-record validator, de-duplication with all actual confirmed-lead values withheld, and unconditional HOLD.
- `test_focus_client_gate.cjs`: native Node synthetic test suite, 27/27 PASS locally. Exact source Git blob hashes verified against committed code.
- `SOURCE_REPRO.md`: precise evidence, negative cases and scope limits.
- `OWNER_REMEDIATION.md`: no-send conversion/consent correction with an implementation-review acceptance matrix.
- `review_board.html`: locally reviewable static demonstration of query/DOM vs provider evidence (not live Jetpack render).

**No WordPress, email, subscriber, merchant, payment, analytics, social or homepage writes.**

## Ownership / next decision
Claude/Focus #129 owns audited implementation if the founder separately approves it. Dispatch #174 specifies the confirmed_signup truth rule, Mind #171 owns the not-live warm-up guides and merchant acceptance, #820 owns net paid-conversion aggregation. Grok retains distribution ownership. All six hold unsent, with issues 03 and 05 additional HOLD_MERCHANT. No paid conversions verified; net revenue per 1,000 qualified human sessions is NOT COMPUTABLE.

## Public references
- [WordPress newsletter email appearance and preview](https://wordpress.com/support/newsletter/email-appearance/) (reviewed Oct 6, 2026)
- [WordPress sending notifications](https://wordpress.com/support/newsletter/send-newsletter-emails/) (reviewed Oct 19, 2026)
- [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [Final Vestige Editorial Standards](https://finalvestige.com/editorial-standards/)
- [Final Vestige Focus](https://finalvestige.com/focus/)
