# Apollo Experience 2.0 — R381 evidence-to-investigation bridge

**2026-11-15 · Built and locally tested · Draft · NOT deployed or installed in WordPress**

## Source-controlled scope
R381 is a compact staging-only evidence component for a high-intent history/social-studies educator arriving from a Grok-owned Apollo documentary. It presents three selections from R377's SHA-256-sealed six-record NASA custody corpus: the January 1967 ground test; the Board's probable electrical-arc determination with no conclusively identified exact ignition source; and NASA's February 14, 2018 retrospective of 102 *later* deliberately ignited flammability-test specimens in 1967–1968. It does not imply the 102 later tests were January 1967 fires.

Each native source drawer contains the NASA evidence URL, source role, limitation, chronological context and explicit photography/branding-rights caveat. The print view exposes the NASA URLs. There is exactly **one free-investigation next action** and no advertised product, form, popup, map pin, tracking script, payment link, NASA photograph, copyright claim or endorsement.

This is independent of frozen homepage PR #49, core homepage production engineering, Research Desk PR #158 and Grok/Praxxis TASK-008. R381's staging shortcode is distinct and does not overwrite any existing shortcode owner. The pre-head CSS gate covers only the main post's direct shortcode, not reusable/template/dynamic blocks. Missing or modified source records withhold historical claims and retain the free link; wrong host/production never registers this shortcode.

## Sources
Primary: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
Later source: https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/
Free destination: https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/

Source links alone do not grant commercial image-reproduction rights or NASA endorsement.

## Reproduction
From repository root (PHP 7.4+, Python3, Playwright, Chromium at /usr/bin/chromium):

    php experience2/apollo-r381/qa/wp_stub.php
    python3 experience2/apollo-r381/qa/browser_qa.py
    python3 experience2/apollo-r381/qa/package.py
    python3 experience2/apollo-r381/qa/http_qa.py

PHP stub: 23/23 assertions. Actual headless Chromium against PHP-generated set_content fixture: 206/206 assertions across ten modes (320–1920px, no-JS, keyboard/pointer, touch, reduced motion, forced colors, four-times root-font, print). This is NOT native browser 400% zoom or genuine installed WordPress staging. Screenshots, PDF and QA JSON are in the deterministic archive, with a SHA-256 file manifest.

**Critical false-positive prevention:** HTTP acceptance explicitly attempted a genuine loopback browser page navigation. The environment rejected it with ERR_BLOCKED_BY_ADMINISTRATOR. The HTTP gate writes QA/http_gate.json, exits code 2 and does NOT convert the fixture green into an HTTP/CSP approval. Genuine axe-core was not installed; independent screen readers, installed Assembler, staging HTTPS/CSP, hosted exact-SHA CI and production LCP/CLS/INP are also unverified.

## Conversion-first experiment and ownership
The sole proposed pathway is **approved Grok-owned Apollo long-form asset and source-linked campaign → sealed NASA bridge → existing free full investigation → possible rights-cleared educator kit only following authenticated checkout, fulfillment and founder approval**. It is a hypothesis that concise source proof increases qualified educator continuation, not proof of commercial lift.

| Offer / funnel | Blocker | Change, pass/fail evidence | Owner |
| --- | --- | --- | --- |
| Apollo educator kit / paid order | Verified SKU, media rights, purchase and delivery unverified | Withhold payment CTA; founder approval required | Founder / Claude |
| Grok documentary / qualified landing | Published asset_id, approved landing and qualified sessions unavailable | Source-backed landing spec only, no posting | Grok / Praxxis |
| NASA custody / free full investigation | Need shorter trust bridge and installed staging validation | 23 PHP and 206 Chromium fixture checks pass; HTTP gate blocked | Apollo QA |
| Paid customer / net revenue | Confirmed merchant orders, fees, refunds and 7/30-day cohorts missing | Net revenue per 1,000 qualified-human sessions **not computable** | Claude / Commerce |

No sale, affiliate conversion or subscriber is inferred from a click. Do not duplicate analytics tags, invent campaign IDs or forward UTMs to NASA. No WordPress changes, merge, live deploy, social post, email, affiliate activation, paid service or merchant changes. Governed by #150, #820 and #818; founder retains release and spend authority.
