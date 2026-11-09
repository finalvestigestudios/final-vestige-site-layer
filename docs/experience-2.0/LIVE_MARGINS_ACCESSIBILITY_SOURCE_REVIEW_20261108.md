# EX2 — Published Page 6 Margins: reduced-motion access audit and isolated repair

**8 November 2026 PT · REVIEW ONLY · NO PRODUCTION WRITE, MERGE, DEPLOYMENT OR SPEND.**
Base PR #1667 HEAD be072074459b0b5d78d75e4de5e12782e12b3bb0. Frozen PR #49 remains 10495883299d53596992c26a8987f629b2904670. Separate ownership: Grok social, Claude production/analytics, Apollo #158, Mind #171. Issues #150 and #820.

## Authenticated source finding
A read-only WordPress Page 6 editor inspection on November 8 showed a published homepage (modified 2026-11-05T12:07:24, 150,710 editor characters). Its first Gutenberg HTML block has exactly 72 ordered animated Margins spans (indexes 0–71), a focusable window with aria-live=off, no independently readable disclosure, and CSS animation cycling for 360 seconds. The existing reduced-motion rule sets display:none for every span except first-child. Thus **71 notes are not visually retrievable from the homepage strip by readers with reduced-motion enabled**. This is a source-grounded access gap, NOT an assertion that a production screen-reader test or WCAG 2.2 AA certification was run.

The actual public homepage already contains seven chapters, its image references, native Jetpack subscription block, 72 records and Focus/Dispatch pathways. Do not overwrite it with the staging-only shortcode.

## Isolated proposal
The new read-only Python generator accepts a locally exported authenticated Page 6 JSON object, requires exact ordered note indexes and unchanged source markers, and refuses drift, missing/unsafe note text or already modified markup. It emits ONLY the first editor HTML block. It preserves all 72 existing records, excludes the animated duplicate strip from the accessibility tree, removes its redundant focus stop and adds a native details/summary disclosure with an ordered list of the **same 72 source strings**. The other page blocks, Jetpack, scripts, image URLs, history and Focus are not modified. No new subscription, JS, network asset or affiliate offer is added.

Do not commit the original editor export or the review-generated page. The generator reports a local source-text SHA-256 receipt.

## Actual test evidence and boundaries
- Local synthetic generator controls: **14/14 PASS**, including source-preservation, fail-closed drift, malicious markup, wrong page and removed reduced-motion fallback.
- Repository contains a second **16-case synthetic regression test**, requiring exact-checkout execution before independent approval.
- An **offline isolated Chromium fixture**, using explicitly synthetic (not historical) record text, yielded **112/112 checks PASS** at widths 320/390/768/1440, JavaScript on/off, reduced motion. Before: one displayed note, no disclosure; review candidate: one static displayed note plus keyboard-openable 72-item list. Synthetic browser captures and JSON receipt are supplied separately.
- Candidate computed contrast: gold summary against charcoal ≈10.60:1; parchment list text against panel ≈15.16:1. No axe or independent WCAG acceptance is claimed.
- Not tested: real WordPress+Assembler rendering, actual full-homepage visual impact, 200% zoom, Safari, screen-reader voice output, Lighthouse/CWV, CDNs/Jetpack or production HTML payload. Duplication of the 72 strings adds bytes; mobile first-screen conversion impact needs measurement. No release authorization.

## Required next quality gate and commercial priority
Private WordPress/Assembler QA first; actual live-page mobile and keyboard baseline, then isolated before/after, no-JS, reduced-motion, axe, 200% zoom, native navigation and real measured Lighthouse. Require founder-specific release approval before any Page 6 edit. No native WordPress.com staging clone is available on the Personal plan; do not recommend an upgrade without a cost/benefit review.

The independently reported Focus Page 1579 false subscription-success condition in PR #1613 remains a **higher commercial-conversion blocker**. Never count a success message as a confirmed subscriber or an affiliate click as a paid sale.

**Conversion contract:** OFFER = existing 52-page free Focus Fieldbook; STEP = source reading → contextual Focus action → verified subscriber → paid conversion; BLOCKER = 71 Margins notes inaccessible visually under reduced motion; EXPERIMENT = an accessible 72-note ledger; EVIDENCE = synthetic tests only, not revenue; OWNER = interim homepage engineering, Claude Jetpack/attribution, founder release.

**Decision: retain live homepage, QA and deployment HOLD.** Frozen PR #49 unchanged; no CMS changes, merges, instrumentation, posts or spending.
