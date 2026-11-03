# Final Vestige — anonymous hosted homepage admission (NO WRITES)

**2026-11-02 PT / DRAFT / RELEASE HOLD.** Stacked on #725 exact 2a36bdb6755e983d4c9ba1bbe6736f63327b9c77. No modification to frozen #49, Apollo #158, Mind #171 or production CMS.

## Why
Authenticated read-only page-6 retrieval shows the seven-chapter flagship already published on Nov 2 at 17:48:13 PT, but its markup embeds an NYPL Malbone map reproduction excluded from the rights-safe candidate. Image-specific rights and publication authorization are unverified. Local Gutenberg admission cannot prove anonymous WordPress.com hosted rendering.

## What is implemented
The companion source code performs cookie-free, GET-only Chromium observation at 320/390/768/1440/1920px with JS, plus 390px with JS off. Its router aborts non-GET requests; no WordPress credentials, editor calls or CMS writes occur. It verifies seven chapter anchors and targets, 72 unique Hidden in Margins indices, at least two same-origin Focus links, Jetpack subscription markup, and Apollo/Franklin identity. It identifies binary NYPL img/srcset/source reproduction without treating catalog links as copyright infringements.

At 390px, it requests exactly two approved archival images — s67-19766.webp and Franklinexpeditionnote.jpg — into memory, accepting only the direct first-party URL or WordPress.com's strict i0.wp.com resize proxy for that same original and verifies actual response MIME, bytes and SHA-256. It never fetches or saves the disputed NYPL photograph. No raw page HTML, browser cookies, media bytes, personal records or screenshots are retained; the JSON contains allowlisted structure, digests and gate statuses only.

13 offline tests (including Jetpack CDN spoof controls) cover misleading NYPL catalog links, forged Focus hostnames, missing/duplicate Margins, missing chapters/Jetpack, media origin, absent browser widths and unconditional release HOLD. Exact-head GitHub Actions source and Chromium jobs upload a redacted seven-day audit receipt (including on failure). A browser test success is NOT a release pass. If NYPL reproduction remains, the rights gate is HOLD_REPRODUCTION_PRESENT, not a definitive infringement claim.

## Limitations
This does not establish rights permission, publication authorization, WCAG 2.2 AA, live field CWV, Safari/physical-device accessibility, Jetpack submission success, or a WordPress.com staging clone. WordPress.com Personal does not provide native staging and its included wpcomstaging address is not a separate clone. Independent QD and explicit founder exact-SHA approval still govern any site mutation or release. The Site QA, Apollo and Mind editorial agents remain separate.

## Local source tests
From experience2/home-flagship/qa/release-candidate run: python -m unittest -v test_probe_hosted_page6.py

For the public read-only browser probe, install Python playwright 1.56.0 and Chromium, then run: python probe_hosted_page6.py --output HOSTED_PAGE6_ANONYMOUS_AUDIT.json
