# Apollo R439 — Evidence Receipt / exportable source-custody pathway

**STAGING-ONLY candidate. NOT installed, merged, live or revenue-verified.** Shortcode `[fv_apollo_evidence_receipt_r439]` is gated by explicit `FV_R439_ENABLED === true`, integer `FV_R439_STAGING_PAGE_ID`, exact queried page ID and WordPress environment `staging`. No homepage PR #49 or original Research Desk PR #158 changes. Descends from R438 draft PR #2912 (exact head `c1f5a0e5e152a45144ac5e2fbb060d4c85cee6e7`) and verifies four R438 Git blobs and two local SHA-256 asset hashes before any enqueue/render; parent recursively verifies R429–R437 ancestry.

## What is built

Educators reviewing NASA sources can export all five sources or only the two selected in R438's side-by-side comparison. User-initiated downloads contain titles, source classes, date/publication labels, NASA URLs, supported findings, limitations and rights caveats. Clipboard copying has a tested read-only textarea fallback on denial, with correct status messaging. Nothing is automatically downloaded or transmitted. No cookies, storage, fetch, analytics, paid CTA or NASA imagery/insignia. No geolocation or speculative edges. Without JavaScript, every source, rights disclosure and the one free Apollo-investigation CTA remain available.

**Conversion hypothesis, not a claim:** A classroom-useful evidence receipt may increase educator trust and follow-through to the free Apollo investigation, which could support a separate, later rights-cleared educator product. A payable SKU, checkout, merchant settlement and any paid orders remain unverified.

## Reproduce

From repository root with R429–R438 ancestry present:

    php -l experience2/apollo-r439/staging-evidence-receipt.php
    python3 experience2/apollo-r439/qa/test_contract.py
    python3 experience2/apollo-r439/qa/browser_qa.py
    python3 experience2/apollo-r439/qa/staging_acceptance.py  # expects HOLD exit 2 without approved HTTPS staging + genuine SHA-pinned axe
    python3 experience2/apollo-r439/qa/package_evidence.py

The local QA used actual PHP-generated HTML in Chromium via `set_content` (NOT WordPress-staging navigation). Browser navigation to HTTPS, localhost and file URLs was blocked by `ERR_BLOCKED_BY_ADMINISTRATOR`. Genuine axe-core was unavailable after package registry DNS error; navigated LCP/CLS, field p75, independent screen-reader/QD, exact-head CI, commercial SKU and founder release authorization are still HOLD.

Official NASA sources, last checked November 17 2026: [Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/), [later flammability testing](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/), [media and endorsement restrictions](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/).
