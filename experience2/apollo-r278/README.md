# Apollo R278 — malformed sibling fail-open + HTTP/CSP response custody

**DRAFT • HARD HOLD • not deployed.** Isolated follow-up to R277 PR #1998, scoped to Issue #150 and conversion charter #820. This PR targets the R277 staging branch; do not edit homepage PR #49, Research Desk PR #158, live WordPress, Grok's creator queue or Claude's production engineering.

## Proven defect and correction
In R277, if sibling `apollo-r273/review-custody.php` existed but lacked `fv_ex2_r273_review_panel`, the shortcode emitted **empty HTML**. A PHP `ParseError` or thrown exception from a damaged partial installation could also break the page. R278 extracts a shared static historical-reference fallback, catches PHP Throwable during include, and uses fallback for a missing callable. No error messages/paths are leaked to visitors, and untrusted shortcode approval/merchant attributes are still ignored. Original NASA evidence and one free investigation link are retained; no affiliate, analytics or media assets introduced.

## Commands and boundaries
- `php -l experience2/apollo-r277/apollo-review-shortcode.php`
- `php experience2/apollo-r277/qa/wp_contract_gate.php` (inherited WP API simulation, 20/20)
- `python experience2/apollo-r278/qa/failopen_gate.py QA-A`; repeat with `QA-B`: 6 isolated PHP states and 30 Chromium offline contexts including 320–1920px, no-JS, touch and reduced motion. Four image outputs across two executions are comparable by SHA-256.
- `python experience2/apollo-r278/qa/http_response_gate.py`: loopback PHP HTTP content/CSP *response headers*, stylesheet 200, intentional missing stylesheet 404. Python client only, NOT browser-side CSP enforcement.

**Browser HTTP blocker**: An attempted real Chromium `page.goto('http://127.0.0.1:<ephemeral>/atlas')` failed `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Do not mark actual browser HTTP/CSP PASS. Local HTTP headers served to Python are not equivalent to browser enforcement. Genuine axe-core unavailable; installed WordPress/Assembler, CDN/CSP, screen reader, browser-interface zoom, Safari/Firefox, field LCP/CLS/INP, hosted CI, editorial approval and licensing remain untested. No new media, map pins or relationship edges.

## Conversion-first, independently held
Verified Grok Apollo long-form asset_id/UTM → publicly accessible Atlas → free source-based investigation → separately disclosed Mini Museum guide only if merchant payable eligibility/rights/founder approval established → authenticated settled orders less fees/refunds. No Apollo long-form asset, payable affiliate settlement, or net revenue per 1,000 qualified-human sessions has been verified. Cite NASA Apollo 204 Review Board primary source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ ; commercial NASA endorsement restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Readable source links do not prove editorial signoff or rights.

No production/WP/site/post/social/email/affiliate/analytics/spend writes. All release gates remain **HARD HOLD**.
