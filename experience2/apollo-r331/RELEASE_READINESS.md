# Apollo Evidence Atlas R331 — narrow-width source custody reflow (STAGING ONLY)

**Scope:** CSS/cache-token fix; read-only Chromium replay; no live WordPress/analytics/checkout changes. Base: R330 draft PR #2314, isolated from homepage PR #49 and Research Desk PR #158. Related: #150, #820, #818.

## Reproduced negative control

The R330 stylesheet (Git blob b9441b73ba810af23e59e72f862f2e1f7ea81ccc) places 64px (4× default) root text in a 320px viewport. In the opened native source-custody disclosure, reconciliation and nested authority ledger cards each add 64px per side. Seven linked NASA records yield **0px-wide click rectangles**, although document horizontal overflow is 0. A no-overflow assertion alone cannot detect this broken interaction.

## Actual fix

Bound **only narrow-viewport** (max-width:420px) padding for reconciliation and its two nested documentary record lists to 12px. Preserve exact records and chronological order, link allowlist, media-rights status, native disclosures and the single noncommercial editorial continuation. Bump stylesheet cache token to r331-custody-reflow-20261113.

## Executable acceptance

Run from repo root:

    python experience2/apollo-r331/qa/reflow_release_replay.py

Requirements: PHP, Node, Python Playwright and headless Chromium at /usr/bin/chromium. Script pins PHP, CSS and JS Git blobs and refuses incompatible source; it renders the real shortcode via the existing R320 PHP lifecycle fixture, checks source classifications and allowlisted links, compares against an actual pre-fix CSS negative control, and checks **42 Chromium contexts**: seven widths (320, 360, 390, 768, 1024, 1440, 1920) × root sizes (16, 32, 64px) × JS/no-JS, with reduced motion, touch on mobile, and forced colors in the 390px/32px case. It asserts all seven source-link rectangles are at least 24px wide and 40px tall, fully in viewport, without horizontal overflow or external network requests. No NASA media is loaded.

Expanded local sprint runner (separate evidence ZIP, not committed in this PR): 42 contexts PASS, negative control 7 collapsed links, PDF source annotation audit PASS, native keyboard chronology/source-return PASS, 4 Chromium screenshots. The committed replay independently passed all 42 contexts. Fixture-only performance observations are NOT real-site Core Web Vitals; no production LCP/CLS claims.

## Source and rights boundary

Primary accident analysis: [NASA Apollo 204 Review Board report](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/). The Board identified an electrical arc as the probable initiator but **did not conclusively determine a single ignition source**. NASA image accessions are contextual references, not causation proof or commercial-image clearance. No NASA media download, map coordinate, speculative edge or endorsement claim is added. Research Desk #158 photograph/document labels remain its owner's responsibility.

## Conversion and release contract

**Hypothesis only:** qualifying viewers of a future Grok Apollo film who can inspect readable source documentation will trust the free investigation enough to continue to a separately approved educational kit. One existing action: **Read the free Apollo 1 investigation**. The kit is NOT authenticated as a payable, rights-cleared SKU; no purchase claim or new checkout/merchant link is appropriate.

**Blocked:** genuine axe-core, independent screen readers, Safari/Firefox, installed WordPress/Assembler/CDN, native HTTP/CSP, hosted CI, NASA media-rights/editorial clearance, authenticated Grok asset, payable SKU, reconciled orders/fees/refunds and founder authorization.

**Ownership:** Apollo—staging components/browser QA; Research Desk—source labels; Grok/Praxxis—published asset/source review in TASK-008; Claude—production engineering, checkout verification and measurement; founder—production release and paid terms. KPI verified realized net revenue per 1,000 qualified human sessions for 7/30-day cohorts: **not computable**.
