# Apollo R263 — actual R224 + R262 source hook-sequence acceptance

**DRAFT / STAGING HARD HOLD.** Tracks Issue #150, commercial governance #820 / #818. Stacks on R262 draft PR #1903 only. Frozen homepage PR #49, Research Desk PR #158 and Claude's homepage/production lane are not touched. This PR adds only QA code and documentation: no plugin, NASA evidence, chronology, map pin, source link, CTA, WordPress, analytics or merchant changes.

## Why this matters

R262's first WordPress hook mock stubbed its R224 asset-verification function. Consequently that mock could not demonstrate whether the actual original R224 plugin and R262 overlay work together in a single PHP execution. R263 is an independent integration contract using the **actual** source-sealed R224 and R262 plugin PHP, with WordPress API functions simulated locally; no R224 integrity functions are stubbed.

The executable PHP harness calls both real plugins, sorts their actual registered hooks and executes original preflight priority 20 then overlay priority 25. The executable Python runner pins the R238 original fixture manifest and source-file hashes, verifies the Git blob IDs of R262's source and its asset SHA-256s, and checks **11 isolated PHP cases**: direct/synced shortcodes, absent shortcode, administration, non-singular, late render, duplicate shortcode, corrupt original CSS, corrupt original fragment, corrupt overlay CSS and corrupt overlay JS. Every deliberate fault is applied to a TEMPORARY COPY, never to source or production.

Overlay failures must preserve the original, accessible Atlas; broken original seals must fail open to the free original investigation; duplicate rendering must not emit duplicate Atlas IDs. The Chromium component test uses the exact PHP-rendered evidence across 320, 390, 768, 1440 and 1920px, JS on/off, keyboard, reduced motion and forced colors, producing reproducible screenshots and JSON receipt hashes.

## Reproduce

Obtain the SHA-pinned source-evidence ZIP attached in Issue #150's R262 engineering handoff. Its original fixture manifest SHA-256 MUST be f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68. Run with PHP >=8, Python Playwright and local Chromium, no paid services:

    php -l experience2/apollo-r263/qa/wp-real-source-sequence.php
    python experience2/apollo-r263/qa/real_source_acceptance.py --fixture /unpacked/fixture/sealed-r238 --r262 /unpacked/experience2/apollo-r262 --out /tmp/apollo-r263-qa --chromium /usr/bin/chromium

The test intentionally **does not claim installed WordPress**. The browser uses Playwright set_content because localhost page.goto returns net::ERR_BLOCKED_BY_ADMINISTRATOR here. Genuine axe-core, independent screen readers, actual HTTP/CSP, 200% browser UI zoom, production Core Web Vitals, independent QA, inherited R198 discrepancy and founder release authorization remain mandatory HOLD gates. Source Git blobs and the exact evidence package hashes are recorded in Issue #150. No CI result is inferred from zero hosted workflow runs.

## Provenance and rights

NASA Apollo 204 Review Board, primary technical source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . The board did **not** identify a single ignition source conclusively; electrical arcing was the most probable initiator. No fresh NASA media license is asserted, and no agency commercial endorsement or speculative Atlas geolocations are permitted.

## Conversion-first bridge (specification only)

Grok/Praxxis must first confirm a published Apollo long-form asset and unique asset_id/utm_campaign. The controlled page follows source evidence to the **single existing free next action**: the original Apollo investigation. A separate, optional, clearly disclosed commerce continuation may be tested ONLY after the founder verifies an existing rights-cleared offer, authorized merchant tracking destination, payout/return conditions and transaction reporting. Mini Museum space/meteorite specimens are a candidate retail product, but they are NOT Apollo mission artifacts, and FV affiliate acceptance and settlement are NOT VERIFIED. No nonexistent Apollo educational SKU, paid CTA or attribution script is added.

Measure qualified human campaign sessions → relevant CTA clicks → verified leads where applicable → authenticated paid orders or merchant-confirmed affiliate conversions → refunds and fees → realized net revenue. Primary KPI: net revenue per 1,000 qualified human sessions over 7/30 days with tiny-sample caveats. Until the authenticated commercial events exist, KPI status is **NOT COMPUTABLE**, never claimed zero or positive.

No deployment, site or settings writes, paid vendor, newsletters, creator production, social posting or affiliate activation under this PR.
