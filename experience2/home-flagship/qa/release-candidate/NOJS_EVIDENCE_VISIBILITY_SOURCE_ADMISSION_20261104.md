# P0: No-JavaScript historical evidence must be readable, sourceful, and convertible

## Base and governance
- Parent: draft PR #1030, exact starting SHA `ada172261d348bac51ed36f229da38886e702c8b` (`qa/ex2-archive-case-active-image-admission-20261104`).
- Frozen PR #49, Apollo #158, Mind/Affiliate #171, and production WordPress Page 6 untouched.
- No CMS writes, theme changes, deployment, merge, tracking, affiliate activation, emails, purchases or new subscriptions.

## Source-grounded defect (release harness, not necessarily site)
`chapterState()` required seven **DOM IDs** and all 72 Margins in no-JS mode, but never required the archival evidence panels to be **visible**. A production CSS change accidentally hiding Franklin and Malbone from JS-disabled readers could pass the historical preservation check merely because the hidden elements remain in the DOM.

Read-only WordPress page 6 inspection on November 4 showed a three-case progressive-enhancement model: `[data-fv-case-buttons]` is initially `hidden`; `article[data-fv-case]` entries for Apollo, Franklin, and Malbone are initially unhidden and source-linked. Each has a linked heading (`aria-labelledby` pointing to its own `h3`), substantial text, an original external source, an accessible image alternative and an investigation link. JS later hides inactive cases and reveals the case chooser. Therefore a no-JS release test must verify all three cases are *actually readable*, not count invisible DOM nodes.

## Implementation (read-only browser)
- Export `auditNoJsArchives(page)`: inspect computed CSS and hidden ancestors, unique panel identity, visible box dimensions, in-panel heading/ARIA link, substantial text and a visibly accessible external HTTPS source link. Require three nonduplicated cases; require the JS-only case chooser to remain hidden without JS. Sources are tested as links, not as proof that any linked claim is correct.
- Run the audit inside the actual production anonymous no-JS browser gate; report individual evidence-record failures and HOLD on any missing evidence. Follow the existing visible Focus header link to /focus/ by **GET only** and require the Fieldbook offer text there. Never submit Jetpack signup or checkout.
- Add real-Chromium representative `javaScriptEnabled:false` tests for 320/390/768/1279/1280/1440/1920, with adversarial cases: hidden article, CSS-hidden article, duplicate, wrong heading, truncated text, missing external source, visually hidden source link and erroneously displayed enhancement-only chooser.
- Preserve 72 Margins, original seven chapters, Jetpack and the free 52-page Focus Fieldbook.

## Executed evidence and explicit limits
Before code commit, an independently created **Python Playwright with system Chromium** representative no-JS fixture passed at **7/7 widths and 7/7 negative mutations** (hidden article, missing source, hidden source link, bad heading, truncated text, duplicate, visible chooser), at `/mnt/data/fv_nojs_evidence_gate_20261104/receipt.json`; 390px and 1440px offline screenshots were saved. This is a deliberately synthetic DOM reproduction, NOT published-site screenshot, exact-source WordPress Playground, or proof of hosted rendering. The committed Node browser test additionally includes the CSS-hidden adversarial case; it has **not** been executed in the exact checkout in this sprint.

Still **HOLD** for native exact-checkout Node tests, connected WordPress live Chromium/axe, actual archival byte transfers, 200% zoom, genuine WCAG 2.2 AA review, lab Lighthouse and field CWV, media rights final signoff, owner visual approval, independent QD and hosted Actions/CI. WordPress.com Personal has no native WP.com staging clone; do not recommend an upgrade without CBA. Isolated Playground/Assembler testing is useful but cannot certify WordPress.com-hosted cookies, Jetpack or redirects.

## Conversion contract (Issue #820)
**Offer:** free Seven Day Focus Fieldbook (lead capture, not a paid sale).
**Funnel step:** accessible trust-building archival evidence → visible header Focus CTA → /focus/.
**Blocker:** a JS-disabled visitor could silently lose authentic evidence while source-only tests pass.
**Change:** fail closed on hidden or unsourced no-JS cases and require actual plain-link Focus navigation.
**Evidence:** 7 viewport Chromium fixture positives / 7 negative controls; exact-source live/prod result pending.
**Owner:** Homepage engineering owns view/CTA admission; Claude retains analytics and paid-sale attribution; Grok/Praxxis retain creator acquisition and asset IDs. No new confirmed leads, merchant orders, payouts or net revenue asserted.

**Release decision:** HOLD. This draft only tightens admission; it is not authorization to change the published site.