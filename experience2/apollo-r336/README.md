# Apollo R336 — browser accessibility-tree and provenance gate

**STAGING ONLY · LOCAL PASS · NOT LIVE · HARD RELEASE HOLD**

This draft builds independently atop Apollo R335 PR #2344 (exact parent HEAD 61914389e62fe9e948354a1b54ef4fe080d0919b), under issue #150 and revenue charter #820/#818. Only this new QA runner and documentation are added. No changes to frozen homepage #49, Research Desk #158, overlapping R334 branches #2340/#2342, the live website, the Grok queue or merchant/tracking systems.

## Why this is different from screenshot/DOM-only testing

qa/ax_source_contract.py invokes the **actual R281 PHP shortcode** through the pinned R320 WordPress lifecycle fixture and reads **Chromium's computed accessibility tree** using Chrome DevTools Protocol Accessibility.getFullAXTree. A DOM link is not counted as accessible merely because it exists in HTML: this runner checks the browser-exposed link names, disclosure names and chronology/source region names, even with two copies of the shortcode. An unstyled JS-disabled case is inspected separately to protect fail-open semantics.

Execute from the repository root with PHP, Python Playwright and local /usr/bin/chromium:

    python experience2/apollo-r336/qa/ax_source_contract.py

Git blob pins (stop on drift):
- experience2/apollo-r281/apollo-source-experience.php — f59a083de8d0774ed7210bfe4e18726feea73f76
- experience2/apollo-r281/assets/apollo-source-experience.css — 577a5d33518baec6e1beff1517779264d342bc50
- experience2/apollo-r320/qa/wp_late_shortcodes.php — f8987327fd6b49afcf8996c695100e3e7471c831

## Executed local findings (2026-11-13)

15 actual Playwright Chromium accessibility-tree contexts PASS: 13 viewport/mode configurations across 320, 360, 390, 768, 1024, 1440 and 1920px, 320px/400% root type, JS disabled, forced colors, reduced motion and touch emulation; one two-instance case; one unstyled/no-JS case. Per Atlas instance, 39 browser-accessible named links, seven native named disclosure controls, one named chronology navigation and one named source region. Keyboard Enter on a closed summary opens the source record. Seven separately injected negative mutations were caught: unnamed link, merchant impersonating a source, false media reuse, duplicate ID, fabricated geographic pin, extra CTA and anonymous region.

Official NASA documentary links (13 instances per Atlas) and four contextual NASA image-detail links retain different proof/rights classifications. No speculative pins or relationship edges, loaded NASA photographs, unapproved merchant links, paid CTA or tracker were added. Full receipts and screenshots were produced in an offline deterministic evidence archive; screenshots are not claimed to be installed WordPress.

## NASA provenance and commercial-media rule

- NASA Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — most probable initiator was an electrical arc; no single ignition source was conclusively identified.
- NASA Brand Center: https://www.nasa.gov/nasa-brand-center/ and advertising guidance: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — historic source linking does not imply NASA endorsement, promotional reuse clearance, logo permission or rights in recognizable persons. NASA publicly released media have conditional reuse rules; staging "not-cleared-for-reuse" is a local review status, NOT a claim that every NASA image is copyrighted.
- Research Desk PR #158 still needs its owner to resolve photograph-first versus documentary evidence labels, especially cards 02/03/04/06. Do not silently merge the two incompatible R334 implementation drafts.

## One controlled conversion hypothesis, not a live sale

Grok's **actual published Apollo film**, once its asset_id/post URL/mobile destination is verified through TASK-008 and Praxxis, can attract a research-minded audience to the NASA Evidence Atlas. Their one next action is the existing free Apollo investigation at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/. An optional Apollo educator kit is **not an authenticated, payable, rights-cleared FV product**; Claude/Commerce and founder must independently validate the SKU, checkout, delivery and permissions before any merchant CTA. No unrelated sales prompt in the accident narrative.

Commercial KPI is reconciled settled net revenue (paid orders less fees/refunds) per 1,000 qualified human first-party sessions in 7/30-day cohorts. No campaign asset ID, actual attributed human sessions, confirmed orders, merchant fees or refunds were authenticated here. A tracked click is not a sale.

## Remaining hard release gates

Genuine axe-core was NOT executed (not locally available); CDP AX tree is not an axe audit or screen-reader test. Independent NVDA/VoiceOver, Firefox/Safari, physical touch, installed WordPress/Assembler/CDN, native browser HTTP-header CSP, production LCP/INP/CLS, NASA media/brand and editorial review, actual offer checkout, hosted exact-HEAD CI, independent QD and founder release approval remain **unverified**.

No production, WordPress content/settings, homepage, creator-queue, analytics, affiliate, email, merchant or paid-service writes were made.
