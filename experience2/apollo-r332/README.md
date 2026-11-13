# Apollo Experience 2.0 — R332 whole-Atlas interaction gate (STAGING ONLY)

R332 adds a committed, read-only Chromium browser gate against the exact R331 Apollo PHP/CSS/JS bytes. It tests **every interactive anchor/summary** (46 per case, 1,932 checks), not just a selected NASA source link. The test spans 320/360/390/768/1024/1440/1920 CSS-pixel viewports, 16/32/64px root fonts (up to 400% of 16px), JavaScript and no-JavaScript, mobile touch emulation, reduced motion and a forced-colors scenario. It checks bounded target geometry, non-empty accessible text, native fragment route existence, unique IDs, keyboard focus, actual Chromium accessibility-tree CTA naming, exact 17 official source destinations, three textual claim records, four separate contextual NASA photo records with rights \`not-cleared-for-reuse\`, and exactly one free editorial continuation. Eight deliberate adverse mutations must all be rejected (unapproved Payhip URL, fabricated geolocation, lost documentary record, false photo clearance, extra CTA, collapsed target, offscreen target, broken fragment). A real Chromium screenshot quartet is generated offline.

Run from repository root: \`python experience2/apollo-r332/qa/whole_atlas_gate.py\`. Requires Python Playwright, local Chromium (\`/usr/bin/chromium\`), PHP and Node. SHA-1 Git blob assertions pin the inherited source exactly; no network, cookies, analytics, hosted browsers, social posts or merchant calls. It writes \`experience2/apollo-r332/QA/r332-result.json\` and screenshots (generated outputs are in the evidence archive, not committed).

## Source and attribution boundaries

- Primary interpretive source: [Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). Probable electrical arc **does not** mean a conclusive, precisely identified ignition source.
- NASA photographic accessions are contextual media, not independent proof of a Review Board finding or blanket commercial media clearance.
- Research Desk PR #158 retains two source-label review flags for accessions S67-15717 and S66-58038; this PR does not edit that branch or certify its label correction.
- One on-site link: [free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/). No paid Apollo kit SKU, merchant acceptance, checkout, confirmed orders, fees or refunds verified. No paid CTA should be activated.
- Proposed Grok long-form → verified NASA Atlas → free investigation → **only if independently approved and paid-deliverable** Apollo-appropriate evidence kit. No published matching Grok Apollo asset ID or allowed mobile link authenticated in TASK-008.

## Acceptance boundary

**BUILT**: committed gate. **TESTED**: local real Chromium across 42 configurations with 8 injected negative cases; PHP/Node syntax and source SHA verified. **NOT VERIFIED**: genuine axe-core, assistive-technology screen readers, Firefox/Safari, native browser HTTP and CSP headers (local loopback navigation is blocked by administrator), installed WordPress/theme/Assembler/CDN, hosted CI, NASA commercial media rights, published Grok Apollo campaign, authenticated payable offer, and cohort revenue. Local fixture scores are not production Web Vitals. Independent QD, editorial/rights review, and founder release approval remain mandatory. **HARD HOLD** for production.

Source of truth: Issue #150 for Apollo, #820 for commercial outcomes, #818 for business charter. Do not modify frozen homepage PR #49 or Research Desk #158. No Wordpress/commerce/social/creator queue changes are made in this sprint.
