# Apollo R324 — independent browser, source custody and accessibility release gate

**STAGING ONLY — NOT INSTALLED — NOT LIVE — HARD RELEASE HOLD**

Base is Apollo R323 draft PR #2275, commit 9734ecb401a91d184f2a7bc8779845bc119942b5. This sprint adds QA only, no runtime/WordPress/analytics/merchant changes. Homepage PR #49, Research Desk PR #158 and Grok/Praxxis TASK-008 remain owned independently.

## Reproduce

Run from repository root:

    python experience2/apollo-r324/qa/release_readiness.py

Optional genuine axe-core, using a separately obtained official Deque bundle:

    REQUIRE_AXE=1 AXE_CORE_JS=/absolute/path/to/axe.min.js python experience2/apollo-r324/qa/release_readiness.py

Requires Python Playwright, pypdf, local Chromium at /usr/bin/chromium, PHP and Node. The runner verifies exact source Git blobs and PHP/JS syntax, PHP dynamic-shortcode fixture, 14 real offline Chromium contexts at 320/360/390/768/1024/1440/1920px with JavaScript enabled and disabled, official source destinations and source/rights boundaries, the one free editorial continuation, absence of images/geo pins/paid links, native fragment focus and closed-details reveal, actual Chromium CDP accessible link names, two Chrome-generated PDF URI inspections, and offline LCP/CLS observations. Four negative mutations must be rejected: counterfeit NASA media clearance, injected checkout, invented geo pin and inaccessible unnamed link.

**Genuine axe-core was not available locally.** When missing, runner explicitly reports AXE BLOCKED; CDP AX-tree checks are not an axe substitute and cannot satisfy that release gate. When provided, actual axe.run executes and rejects violations. Neither that package nor analytics are injected into public pages. The QA-only diagnostic run reports AXE BLOCKED but does not certify a release. Set REQUIRE_AXE=1 for the fail-closed release gate: without an actual axe bundle, execution exits nonzero. An invalid AXE_CORE_JS path is an error.

Local execution: 14/14 offline Chromium contexts PASS, four deliberately corrupt variants rejected, two printable source PDFs audited, 390px and 1440px screenshots and JSON per-context receipt. Chromium refused native http://127.0.0.1:8764/ with net::ERR_BLOCKED_BY_ADMINISTRATOR. Installed WordPress, Assembler, CDN, CSP and field CWV are unverified; local fixture LCP/CLS are NOT field metrics.

## Separate Research Desk PR #158 source-role finding

Research Desk prototype SHA 250d7f05a4de037e73826dcf0cfaef0ec4c29383; template Git blob 403d128c57b9bc82dac7c619651689070edef86c; PHP blob d1879a90101b5475990132369178f42743f4b57c. The six-card Desk uses photograph accession IDs (including NASA S67-15717 and S66-58038) as record labels and links both an image-detail page and a written narrative. A card marked PRIMARY REVIEW BOARD RECORD has a NASA *photo catalogue* archive link. Photograph accessions do not independently document Board findings or confer promotional-image reuse rights. This is a **review-required provenance classification**, not permission to edit or overwrite PR #158. R324 verifies the Atlas preserves separate documentary versus contextual-media roles and labels all four media records not cleared for reuse. No geospatial claim edges or new photos were added.

## Conversion: no invented sales

Proposed only: Grok documentary (published Apollo asset ID/URL not verified) → original NASA evidence Atlas → existing single free investigation link → a separately founder-approved rights-cleared Apollo classroom evidence kit after an actual payable SKU and working checkout are authenticated. Teacher trust/purchase lift is a testable hypothesis, not an observed result. No commerce link is inserted into the accident narrative. Net realized revenue per 1,000 qualified human sessions is **NOT COMPUTABLE** without qualified-human cohorts, verified paid orders, fees/refunds and reconciled attribution. Grok owns media/distribution, Praxxis creator QA, Claude analytics/merchant engineering and Founder posting, releases and spending.

**Hard release blockers:** genuine axe-core, independent NVDA/VoiceOver and other-browser acceptance, native HTTP/CSP and installed WordPress/CDN, field p75 CWV, historical editorial/media-rights and QD review, hosted CI on exact HEAD, offer checkout proof, real creator campaign ID and founder authorization. GitHub Issue #150 is engineering coordination; Issue #820 and charter #818 govern the creator-to-paid proof contract.
