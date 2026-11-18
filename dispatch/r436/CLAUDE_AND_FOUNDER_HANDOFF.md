# R436 surgical Focus conversion repair — deployment acceptance (NOT permission)
**Target owned by Focus/Claude: https://finalvestige.com/focus/ , WordPress page ID 1579.** Dispatch owns only consent language and no-send QA. Founder approval is required to change this live page. No overlap with frozen homepage PR #49.

## Before → after
**Current:** existing Jetpack subscribe block; `#fvf-gift` hidden with `role=status`; inline `fvf-gift-v2` script reveals the panel from arbitrary `?subscribe=` values or a subscriber-looking class; `focus_pdf_click` has location `after_signup`. The visible text is reasonable after a real confirmation but the browser alone does not establish one.

**Candidate:** existing Jetpack subscribe block stays byte-identical. The 52-page public PDF download section is a visible named region by default, with no URL/class eligibility check. CTA stays a PDF link and the same `focus_pdf_click` semantic, but its location changes to `public_fieldbook`. Near-copy explicitly distinguishes downloading from joining The Dispatch. Existing consent statement beneath the panel stays untouched. No invented confirmed_signup is fired.

## Operational plan for Claude, if founder later approves a site change
1. Re-read current page ID 1579 in edit context and compare `modified` to 2026-11-16T14:54:58. If changed, STOP and manually reconcile; **never blindly replace live content**.
2. Run `proposeFocusPatch(currentRaw, currentModified)` **locally only**. It must match one exact gift fragment and one exact reveal script. Test evidence is not a deploy authorization.
3. Diff returned text. Only two substrings should change: named gift panel and its inline query/class script. Retain all other Gutenberg blocks, one Jetpack form, live links, styles, and analytics event counts. Assess whether to remove the now-inert CSS selector `.fvf-gift[hidden]` separately.
4. Founder decides whether direct free access better preserves trust and long-term net conversion than conditional display; **no pseudo A/B with three total followers**. Site QA reviews 320/360/390/768/1440px, keyboard, screen reader heading/region, reduced motion and no JS. Test actual PDF HTTP open on mobile. Do not use real subscriber addresses.
5. Separately verify provider's **Email subscription = Subscribed** aggregate, recipient frequency/suppression, actual welcome receipt where consent authorizes a test, and correct double-opt-in flow. The presently available newsletter connector provides aggregated dashboard counts, not individual eligible inbox verification.
6. If a live change is eventually approved, log exact WP post revision ID, QA captures and dates in Focus #129 and Dispatch #174. New code/trackers remain Claude's production engineering lane; never introduce a second `confirmed_signup` pixel.

## What the patch CANNOT establish
A URL query or CSS state is **not** a cryptographic proof of subscriber consent. Conversely, making an accessible free PDF visible does not magically verify that Jetpack emailed a welcome or that anyone purchased. A distinct eligible lead needs a server/provider-authoritative transition and deduplication. Any user-level evidence stays private, never in Issue #174/Drive/source control.

## Failure/rollback contract
Reject stale page modified date, missing form, duplicated old gift block, duplicated script or unsupported current source. No automatic overwrites, no sending, no marketing list imports. Roll back only through WordPress's approved version workflow after an authorized publication, never through this script.

## Sources
- Live authenticated WordPress pages/settings read at 2026-11-18 01:33 UTC; ID 1579 last modified 2026-11-16 14:54:58 (site-reported).
- WP subscriber status reference: https://wordpress.com/support/subscribers/
- WP welcome/confirmation distinctions: https://wordpress.com/support/newsletter-settings/
- FTC commercial mail: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business