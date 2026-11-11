# Apollo R285 — published synced-pattern asset preflight and printed NASA source custody

Status: STAGING HARD HOLD. This branch is stacked exclusively on Apollo R284 PR #2041 (1acd3c652254d2f25486112796f307bc55a76503). No production deployment, WordPress write, new tracking, new commerce, or social changes. Homepage PR #49 and original Research Desk PR #158 are not edited.

## Reproduced problem / corrective change

R284's wp_enqueue_scripts preflight searched the singular parent post for a direct [fv_apollo_source_experience] shortcode only. It misses the case where a published WordPress synced pattern (core/block ref) contains that shortcode. An existing inline/body stylesheet fallback mitigated some contexts but is not equivalent to head-enqueued CSS or tested installed WordPress/CSP behavior. This is a code-path limitation verified against R284; no live customer breakage is asserted.

R285 adds bounded read-only traversal of published wp_block references, including nested refs. Limits: 8 recursive levels, 128 blocks/references, 250,000 bytes/content; visited-ID cycle protection; reject missing, draft, or non-wp_block content. The same scoped stylesheet is enqueued at the correct pre-head hook when a shortcode is actually detected. The original body fallback remains for unknown dynamic cases. No rendering or execution of referenced blocks occurs during preflight, and no visitor-identifying data is read.

## Executable source-controlled gates

Run on a clean checkout with PHP CLI, Python, Chromium, playwright and PyMuPDF:

    php -l experience2/apollo-r281/apollo-source-experience.php
    php experience2/apollo-r285/verify_preflight.php
    python experience2/apollo-r281/qa/committed_gate.py /tmp/apollo-r285-inherited
    python experience2/apollo-r285/verify_print_export.py /tmp/apollo-r285-print

The PHP fixture has 14 cases for direct, one-/two-hop reusable references, cycles, duplicate references, missing/draft/wrong-type sources, unrelated content, depth and size limits; these are WP API simulations, not installed WordPress.

The inherited Playwright regression checks 10 offline responsive contexts (320,390,768,1440,1920 pixels, JS on/off), touch, reduced motion, forced colors, native keyboard chronology/source navigation, text enlargement, print CSS, source URL/pending status, duplicate IDs and overflow. The R285 print test generates real Chromium print PDFs with source drawers closed and checks that 3 official NASA URLs plus the free investigation are present in the extracted PDF text AND actual PDF hyperlinks at 390px and 1440px. PDF metadata is normalized before SHA-256 recording, so repeated outputs are byte-identical.

Independent supplemental QA archive also includes the exact PHP fixture rendered in 10 Chromium contexts, real PDFs, 390/1440 no-JS screenshots, a source-manifest ledger and a reproducible ZIP builder. Archive receipts are local staging evidence, not CI.

## Source custody & rights

- NASA Apollo 1 mission retrospective: https://www.nasa.gov/mission/apollo-1/
- NASA Safety and Mission Assurance timeline: https://sma.nasa.gov/sma-disciplines/accllp/apollo-1
- NASA Apollo 204 Review Board (1967 primary investigative record): https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
- NASA Brand Center rights: https://www.nasa.gov/nasa-brand-center/

The first two are later institutional summaries, NOT independent eyewitness confirmations. The Board considered an electrical arc the most probable ignition initiator but could not conclusively identify a single ignition source. R285 does not alter any historical text or the SHA-256 pinned evidence corpus and does not add NASA images, logos, speculative map pins or commercial endorsement claims. The three NASA source pages were externally reachable on Nov 11, 2026; the offline browser did not itself navigate NASA.

## Conversion-first continuation and owners

One narrative CTA: the existing free Apollo 1 investigation at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ . A later separately disclosed and optional Mini Museum offer is strictly CONDITIONAL on appropriate product fit, approved/earning merchant terms, verified receipts, and founder authorization; no affiliate button appears in the evidence narrative.

Proposed cohort metric: actual published Grok asset_id and utm_campaign -> qualified human landing sessions -> relevant CTA -> independently confirmed merchant order, less fees/refunds -> realized net revenue per 1,000 qualified human sessions, 7/30-day windows. No asset URL, merchant settlement, sales, or attribution data authenticated by this sprint.

Grok owns creator posting; Praxxis owns external creator QA; Claude owns production/analytics; founder retains approval. Coordination: Apollo Issue #150, business Issue #820, charter #818.

## Outstanding HARD HOLD gates

This run has NOT established: installed WP/Assembler behavior, real browser HTTP/CSP (local browser navigation blocked by administrator), genuine axe-core (npm registry unreachable), independent screen-reader and browser UI zoom acceptance, CI on exact HEAD, field LCP/CLS, independent editorial/media-rights review, merchant status and founder authorization. PerformanceObserver on the offline set_content fixture yielded no usable LCP/CLS values. No production or commercial uplift claim.
