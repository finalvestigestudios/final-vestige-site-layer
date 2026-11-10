# Page 6 / EX2 — narrow-viewport reflow proxy (2026-11-10)
**Draft-only; release HOLD.** Parent: PR #1892 exact commit `fac3a3b755643b30eedff22c7b52bb5985a7c81c`. Frozen PR #49 unchanged.

## Reason for this isolated check
PR #1892's prior exploratory 200% **CSS zoom** at a 768px viewport reported a 13.64px-wide footer disclosure link. CSS `zoom` changes element scaling without reliably changing media-query viewport breakpoints; it must not be presented as a genuine 200% browser-zoom finding. New script independently exercises the CSS-width side of reflow using narrower viewports, including 384px (768px ÷ 2) and 720px (1440px ÷ 2), across all three art directions, JS disabled/enabled, and reduced-motion. It checks no horizontal root overflow, seven chapter anchors, unblocked Focus link, 44px Focus rail, undersized standalone interactive rectangles, and keyboard activation of evidence disclosure.

## Evidence and applicability
- A source-equivalent local Chromium study against the pinned 11 flagship files and offline composer produced **60/60 PASS** cases at 320/360/384/390/480/720/768/960/1440/1920 widths, 3 art directions and JS enabled/disabled. **Not an exact-HEAD GitHub CI/QD run.**
- No WordPress runtime was executed. Official Playground CLI is not installed and npm registry DNS resolution is unavailable in the executing environment. WordPress.com Personal has no native clone; the only connected site is production 256784396.
- The new committed script is a reproducible acceptance probe **not yet independently executed from this new commit**. It uses real local Chromium and fails closed if the pinned files, expected controls or chapter anchors differ.
- No source creative edits, further conceptual chapters, image changes or affiliate/tracking changes; no production writes, merges or deploys.

## Read-only live WordPress observation
Read-only Page 6 editor output (last-modified Nov 5) still carries the 72 original Margin snippets, the original Gutenberg Jetpack block, and a native `/focus/` action outside the flagship swap. Its **rendered** Jetpack button links back to `/?post_type=page&p=6`, with no form element in page-rendered block markup. This may depend on Jetpack client scripts for activation; it is **not proof subscription is broken**, but functional keyboard/touch/no-JS fallback and a genuine confirmed signup remain an acceptance gate under #820 / #1681. Do not create test subscribers without approval.

## Release work still required
1. Genuine isolated WordPress/Assembler (free Playground or local) with **public-only** Page 6 content; verify actual Gutenberg `parse_blocks()`, private preview and Jetpack output. Simulated theme and PHP mocks do not count.
2. Manual genuine browser zoom at 200%/400%, keyboard navigation, axe (fail closed), Safari when available, mobile network transfer of Apollo/Franklin/NYPL, manual visual founder review.
3. Measured Lighthouse/CWV, rights acceptance, native Jetpack confirmation and exact-HEAD independent CI/QD.
4. Preserve the 72 Margins, native Jetpack block, original `/focus/`, seven chapters, three art directions and editorial source attribution.
5. No release, WordPress CMS edits, production/plugin install, unapproved social posts, spending, or affiliate links.

**Conversion impact:** Existing 52-page Focus Fieldbook → contextual link → confirmed subscriber → later verified purchase. This probe establishes only local UI reflow behavior, not improved conversion, sales, or revenue.
