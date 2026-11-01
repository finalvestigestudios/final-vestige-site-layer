# Apollo Evidence Atlas — R45 Bidirectional Source Custody — STAGING / HARD HOLD

Parent: draft PR #467 (R44), exact commit 58220a25e808176c7b51e2a7a374d6e8c369f16a. This implementation changes **only** experience2/evidence-atlas/. Homepage frozen PR #49, PR #158, homepage engineering branches, production WordPress and CMS content/settings are outside scope.

## Engineering change

- Every NASA evidence card links to its own citation register row (#fva-citation-01 through -06); each citation links to its own original card (#fva-record-01 through -06). Native anchors remain usable without JavaScript.
- Clicking a citation return link when its card was filtered out restores records, preserves the native fragment permalink and focuses that source card. All six citations remain visible while filtering; printing restores all six cards. Malformed link pairings disable enhanced controls and fail open.
- External NASA links announce "opens in new tab". All twelve new links have at least 44px-tall targets in the browser-tested fixtures, with keyboard, touch, reduced motion, no-JS and print behavior.
- WordPress compiled fragment SHA-256: c587b66c80ce15cf79c55d84a242d6a257de9fdfeaa4f999e4d4af989888a40b; plugin version 0.0.45-staging; generated schemas use r45.v1.

## Source integrity

- Exact, unchanged R37 custody crosswalk Git blob ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea.
- Six NASA links, original date precision and separate rights warnings retained; S67-19766 is January 1967 with no inferred day.
- NASA source and rights context: https://www.nasa.gov/nasa-brand-center/ ; https://www.nasa.gov/nasa-brand-center/images-and-media/ ; https://www.nasa.gov/image-article/apollo-1-crew-honored/
- Six individual image reviews remain OPEN. No NASA photograph or logo embedded, no invented geographic pins or relationship edges, no NASA endorsement.

## Reproduce

From experience2/evidence-atlas/ run:

    python -m unittest test_atlas.py tests/test_wordpress_stage.py tests/test_chronology_r43.py tests/test_citations_r44.py tests/test_citation_navigation_r45.py -q
    php -l final-vestige-ex2-evidence-atlas.php
    node --check atlas.js
    python tests/browser_regression_r43.py --output /tmp/apollo-r45-r43
    python tests/browser_r44_review.py --output /tmp/apollo-r45-r44
    python tests/browser_r45_navigation.py --output /tmp/apollo-r45-qa
    python tests/build_r45_bundle.py --output /tmp/fv-apollo-r45.zip --qa /tmp/apollo-r45-qa

Playwright tests use actual PHP shortcode-rendered markup with page.set_content, NOT an installed WordPress page. HTTP localhost navigation remains blocked ERR_BLOCKED_BY_ADMINISTRATOR. Chromium synthetic LCP/CLS readings are NOT hosted Core Web Vitals.

## Release: HARD HOLD

The actual WordPress/Assembler staging integration, axe-core WCAG 2.2 AA audit, Safari/NVDA/VoiceOver, hosted LCP/CLS/INP, six individual NASA rights reviews, independent QA, exact-head green CI and founder approval are unverified. Axe wasn't available to execute. No merge, installation, activation, CMS write or deployment.
