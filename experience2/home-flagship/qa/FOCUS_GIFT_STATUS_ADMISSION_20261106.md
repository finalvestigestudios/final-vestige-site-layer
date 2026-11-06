# FV EX2 — Focus Fieldbook post-submission gift state (REVIEW ONLY)

**2026-11-06 PT. RELEASE HOLD.** WordPress Page 1579, site 256784396, source modified 2026-11-05 17:44:02. Parent branch: PR #1270 at 2fe502b1af484c91f94502d9e6d256ab19645346. Does not modify frozen PR #49, the seven-chapter homepage, the 72 Hidden in the Margins records, Jetpack, or live WordPress.

## Verified source defect

The published `<script id="fvf-gift-v2">` uses a **negative status list**: every non-empty `?subscribe=...` value other than five hard-coded errors displays the initially hidden `#fvf-gift` panel with “Your fieldbook is ready to download.” Consequently `?subscribe=banana`, `?subscribe=true`, and `?subscribe=blocked_mail` all show the post-submission panel **without any signup**. Exact verbatim live script is pinned as `focus_gift_live_20261106.js`, 587 characters excluding its trailing newline, SHA-256 `f5b7a56cf46a17b350a6245684cc222d59ce4b7da62650515d208169f89426a7`.

This is a misleading *presentation state*, NOT proof that anyone has been counted as a lead. The PDF itself is a public resource; **not a PDF access-control vulnerability**. No evidence has been found of existing analytics interpreting this client-side state as confirmed lead conversion.

## Candidate behavior

The proposed `focus_gift_review_candidate.js` uses **only** documented/reproduced query value `subscribe=success` or the existing Jetpack widget class `is-subscriber` as panel-display triggers, retaining the observed MutationObserver. No new cookies, tags, network requests, forms, data collection, affiliate links, tracking, login checks or payment interactions. The script does not gate direct PDF access. Jetpack status `success` means submission accepted, **not email confirmed**. Any unexplained Jetpack state must be investigated before release, so this is **NOT a production patch**.

## Native Chromium reproducible evidence

`python test_focus_gift_state_browser.py` — native Playwright/Chromium: **59/59 PASS** across published and candidate code, 320/390/1440 viewport widths, valid/invalid/arbitrary query values, MutationObserver state changes, no-JavaScript behavior, and the existing review-only `<noscript>` fallback from parent PR #1270.

- Published code exposes the panel for `subscribe=banana`; candidate keeps it hidden.
- Both show the panel for `subscribe=success`, but never count this as a confirmed subscriber.
- Both detect Jetpack `is-subscriber` class on DOM mutation.
- With JS disabled, candidate's post-submission panel stays hidden while PR #1270's separate transparent direct-PDF fallback renders.
- Source witness hash is asserted and fails closed if modified; missing/altered parent fallback fails closed too.
- Fixture before/after screenshots are demonstrative state tests, **not** true WordPress/Assembler or homepage screenshots.
- `release_qualified=false`; no real Jetpack form submission, email delivery, genuine axe-core/WCAG claim, Lighthouse/CWV, merchant verification or QD/CI pass is asserted.

## Required exact release gates

1. Refresh Page 1579 *immediately* before integration; verify full page revision and exact script bytes. No blind replacement if different.
2. Establish actual Jetpack status variants and behavior in isolated WordPress/Assembler, including no-JS fallback, anonymous JS form, confirmation and welcome-delivery checks only with founder permission. A `subscribe=success` URL by itself is **not** a verified subscriber.
3. Verify keyboard, touch, no-JS, reduced motion, 200% zoom, 320–1920 layouts, actual PDF transfer and genuine WCAG/Lighthouse before release.
4. Retain existing Focus and Jetpack/signup, chapters, archival assets, all 72 Margins, and independent source rights review. WordPress Personal plan has no separate native staging clone; use isolated Playground for development and maintain hosted-acceptance HOLD.
5. Claude/Focus owner integrates after review; homepage Site QA verifies click-through; Grok/Praxxis retain TASK-008 content/acquisition; founder controls production approval. No changes to analytics are proposed.

## Offer → step → blocker → experiment → evidence → owner

**Offer:** free 52-page Seven Day Focus Fieldbook. **Step:** historical homepage CTA → Focus form submission → independently confirmed email lead → paid purchase. **Blocker:** arbitrary query values produce a misleading post-submission state. **Experiment:** fail-closed presentation trigger + transparent no-JS free download. **Evidence:** exact WordPress source and 59 passing native Chromium fixture scenarios, not production acceptance or commercial uplift. **Owner:** Claude/Focus implementation, homepage QA, founder release. **Revenue:** unknown; no new verified orders, confirmed leads or commissions.
