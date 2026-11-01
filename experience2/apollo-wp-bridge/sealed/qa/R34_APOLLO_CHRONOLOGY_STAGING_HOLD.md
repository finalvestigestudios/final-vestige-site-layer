# Apollo R34 — dated NASA photographic source chronology (STAGING HOLD)

This is a standalone, source-controlled progressive enhancement of the R33 NASA source-custody annex. It is not the Apollo 204 accident telemetry timeline. A photograph's catalogued date is distinct from the accident chronology; one January 1967 portrait is month-precision only and no day is inferred. Two 2017 images are retrospective memorial exhibits, not accident scene evidence.

## Source and behavior
- Six original NASA catalog links, six individual photo-reuse holds, one disputed S67-19766 identity, zero approved geospatial pins or edges. No NASA image bytes are embedded.
- apollo_chronology_r34.py reads the pinned R33 NASA source registry and produces a static, no-JS accessible document and SHA-256 receipt. Its local dependencies are nasa_catalog_custody_r33.py, nasa_catalog_annex_r33.css, and nasa_catalog_primary_r33.json, inherited from the exact R33 parent.
- apollo_chronology_r34.css provides 320–1920 layout, >=46px touch targets, keyboard focus, print and reduced-motion rules.
- apollo_chronology_r34.js adds optional 1966/1967/2017/All filtering only after DOM initialization, and restores all six readable records if it fails.
- test_apollo_chronology_r34.py exercises source/date/rights/geo and negative mutations.
- browser_apollo_chronology_r34.py runs real Chromium at 320/360/390/768/1024/1440/1920 with both JS states, keyboard/pointer/touch, no overflow/outbound resources, screenshots and an injected JS initialization failure. Optional independently acquired verified axe-core can be supplied via --axe-js; without it the receipt says BLOCKED, never PASS.

## Local execution (Python, BeautifulSoup4, Playwright Chromium)
  cd experience2/apollo-wp-bridge/sealed/qa
  python -m unittest -v test_apollo_chronology_r34.py
  python apollo_chronology_r34.py --registry nasa_catalog_primary_r33.json --css apollo_chronology_r34.css --js apollo_chronology_r34.js --out /tmp/apollo-r34.html --receipt /tmp/apollo-r34-source.json
  python browser_apollo_chronology_r34.py --html /tmp/apollo-r34.html --screenshots /tmp/apollo-r34-screens --receipt /tmp/apollo-r34-browser.json

## Actual local evidence from October 31, 2026
- 16/16 Python checks passed.
- 14/14 Chromium configurations passed (seven widths × JS on/off), plus simulated initialization-failure recovery.
- Source annex holds intact. This does NOT establish axe-core WCAG compliance, actual WordPress/Assembler/Jetpack integration, HTTP CSP on a hosted origin, Safari/VoiceOver/NVDA behavior, field LCP/CLS/INP, NASA image rights or QD/CI signoff.

RELEASE HOLD. This branch is stacked solely on R33 and must remain isolated from homepage PR #49, its lead's branches, original Research Desk PR #158, and live WordPress. No production install, navigation/page/theme/settings write, merge, or paid service is authorized. Track release requirements in Issue #150.
