# Apollo R189 — cache-invariant creator campaign handoff (DRAFT, NOT LIVE)

Governance: Experience 2.0 #150, conversion #820, business charter #818. Additive child of R188 PR #1397. Frozen homepage #49 and Research Desk #158 untouched. No WordPress writes, merchant writes, creator posting or paid services.

## Verified risk and implementation

R188's PHP emits a different first-party CTA destination per incoming GET query. If WordPress/CDN caches HTML without varying on those parameters, viewer B can receive viewer A's campaign tags. A PHP WordPress-function mock reproduced different R188 HTML for two visitors. R189 eliminates all query-sensitive PHP rendering: every visitor receives the same source-pinned HTML and clean free-investigation CTA.

A separate SHA-256-pinned, local, optional JS asset adjusts that one DOM link using validated public visitor-local UTM parameters. The script rejects missing/duplicated values, unexpected source, non-organic medium, malformed campaign and potentially personal asset identifiers. Only the source/medium/campaign/asset tuple is forwarded. No storage, cookies, analytics scripts, reporting beacons, merchant links or new historical claims. Without JavaScript, the historical source trail and original investigation link work, but campaign continuity is intentionally lost.

Seven allowed platforms: youtube/tiktok/instagram/facebook/pinterest/x/bluesky. utm_medium=organic_social; utm_campaign=history_pilot_YYYY_MM; utm_content is a public non-personal 4–64-character ID. Never put any visitor identity into asset IDs. The optional asset is enqueued in the existing pre-head WordPress detection path, including bounded Gutenberg reusable block scanning.

## Reproducible QA (offline only)

Build documented R183–R188 dependencies first; then run the R189 builder, Python unittest discovery in qa/, the qa/chromium_gate.py script with an output directory, PHP -l on generated dist PHP, and Node --check on generated JS.

Generated dist/ contains the PHP adapter, unchanged pinned HTML/CSS, optional JS and manifest. The local PHP shim is NOT installed WordPress. Real Playwright/Chromium fixture tests operate on real DOM with a synthetic window URL, not actual navigation or CDN. Reproducible screenshots and hash receipts are in the evidence archive. No real axe-core or production CWV were measured. Exact-head CI and installed WordPress staging remain outstanding.

## Historical sources and commercial conditions

The Atlas preserves four chronology entries, four technical findings, eight source disclosures, four NASA-linked archival records, uncertainty, and one free Read original investigation CTA. No invented map pins or NASA image files embedded. NASA's Apollo 204 Review Board did not conclusively establish an ignition source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA's advertising policy restricts implied endorsement and astronaut likenesses: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . No NASA media cleared for paid-product promotions.

Commercial hypothesis: Grok Apollo history long-form/Shorts → Atlas → free original investigation → original educator evidence dossier only after a genuinely purchasable, rights-cleared product is verified. This is not a confirmed SKU. Grok owns script/distribution, Praxxis creator review, Claude production commerce and analytics, founder release approval. TASK-008 asset IDs and published Apollo videos remain unverified here.

Prioritized blockers: educator dossier → purchase → no authenticated SKU/rights/checkout → audit inventory/delivery/refunds → BLOCKED / Claude-Commerce; Grok source → landing → asset IDs unverified → reconcile TASK-008 → UNKNOWN / Grok-Praxxis; Atlas → investigation → R188 cross-cache attribution contamination → R189 server-invariant + browser-local enhancement → LOCAL PHP/CHROMIUM PASS, INSTALLED UNKNOWN / Apollo; merchant orders → realized net revenue → no independently verified session/order/fee/refund data → 7/30-day reconciliation → NOT COMPUTABLE / Analytics.

KPI after independent validation: net revenue per 1,000 qualified human sessions and verified orders, net fees/refunds, lead-to-paid conversion. UTMs, website clicks, inferred signups and affiliate outbound traffic are not paid sales. No new analytics event scripts are installed by R189.

STAGING HOLD: real Gutenberg/Assembler installation and asset delivery; cache/CDN isolation for two users; true CSP JS delivery; genuine axe-core and screen readers; responsive 320–1920, keyboard/touch/no-JS/zoom/reduced-motion; real-page LCP/CLS; exact-head CI, independent QA and founder authorization. Nothing merged or published.
