# EX2 complete-homepage exact-source Chromium review — November 9, 2026

**DRAFT / RELEASE HOLD.** Source parent: `a11662319963032612964b30f6f65fd15bfd5c54` (PR #1767). Frozen PR #49 at `10495883299d53596992c26a8987f629b2904670` is unchanged. No WordPress write or deploy.

## Verifiable lift

Added `verify_full_7ch_chromium.py`: reconstruct the **existing eleven-file** seven-chapter candidate from tracked Git bytes (verify HEAD and every asset Git blob SHA); replace six linked CSS and four deferred scripts in the same order as sealed render; load complete HTML in genuine headless Chromium. Save responsive screenshots and JSON per-run receipts without additional paid dependencies. This does not duplicate PR #252's CSP-negative harness or introduce visual chapters.

The committed tool blob SHA is `09fac9f89aa886ef78e3d286b183c2148f99bdf0`. For this run, the eleven *parent* source blobs were fetched from GitHub, each independently verified against its declared Git blob SHA, and assembled into the same standalone fixture. This is **not** a checkout of this new branch HEAD, nor a WordPress renderer.

## Verified source and browser results

- **15/15 real Chromium runs** passed: JS at 320 / 360 / 390 / 768 / 1024 / 1440 / 1920 px; no-JS at 320 / 390 / 768 / 1440; reduced motion at 320 / 390 / 768 / 1440. No document-level horizontal overflow in these runs, one H1, all seven chapter anchors, and visible Focus destination.
- **22/22 interaction outcomes** passed at 390 and 1440: three art directions, three evidence cases, three Franklin chronology views, two observer frames at each width. Existing no-JS fallback exposes all three case records.
- **3/3 negative controls** caught missing essential CSS/JS paths. No JavaScript page errors. Media fetches intentionally blocked in the local fixture and must **not** be interpreted as image-delivery success.
- **Real before/after screenshots** at 390 / 1440 compare old first-screen generic FV orbit (PR #1753 index blob `679eb35418dd18842853f7a0faf9db39be116526`, CSS `1ad6d82f57d1a8a6ca29865ffef82c15edbe1a9c`) against the Franklin folio candidate (index `355fa5fb9600f261556b120db138431b54513add`, CSS `1cc3b36f331025dbe596e48aea5092a074efd8f9`). The *after* screen makes a source-linked historical document the first-screen focal point. These are offline exact-source fixture screenshots, **not** live or Playground captures.
- WordPress.com anonymous screenshot service returned ready links for the published page at 320 / 390 / 1440; those links are *not* parity/interaction certification.

## Known blocked release gates (fail closed)

**No real WordPress Playground execution** (CLI/WordPress runtime unavailable in the local execution environment). This suite uses `page.set_content` in `about:blank`, so it cannot certify Assembler rendering, native WordPress auth/CSP behavior, first-party image transfers, Jetpack delivery, cookie/redirect behavior, or exact hosted infrastructure. Axe WCAG 2.2 AA, native browser 200% zoom, Safari, Lighthouse / Core Web Vitals and independent CI/QD have **not passed**. Existing media/rights custody remains in PR #1730; synthetic screenshots cannot prove actual archival image loading.

## Commerce first

**Offer:** free, existing 52-page Focus Fieldbook → **step:** contextual homepage-to-Focus visit → **blocking dependency:** published Focus query-string false-success in PR #1681 and unverified Jetpack confirmation → **change:** reliable review fixture with visible mobile CTA, evidence-first hero, and no-JS case fallbacks → **pass evidence:** 15 real Chromium responsive/motion permutations and 22 interaction outcomes → **owner:** interim homepage engineering; Claude to own production implementation on return, founder authorizes release. No verified subscriber, order, refund, affiliate conversion, qualified sessions or net revenue claimed.

**Release: HOLD.** Next: exact Git checkout on this PR HEAD; run committed harness, build sealed plugin, execute #1767 launcher in an actual isolated WordPress Playground, capture 320/390/768/1440/1920, real network bytes, authenticated/guest access, axe, 200% zoom and lab Lighthouse. Preserve all 72 Margins records, native Jetpack and Focus PDF in live Page 6. Do not merge, install, change WordPress, send email, publish, pay or activate affiliate links without separate approval.
