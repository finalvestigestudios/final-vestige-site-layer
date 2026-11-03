# EX2 — SAVED ASSEMBLER LAYOUT GATE / RELEASE HOLD (2026-11-03)

**Status: DRAFT / ISOLATED / NOT FOR PUBLICATION.** This is a review-only amendment stacked on PR #831; frozen #49, Apollo #158 and Mind #171 are untouched. There are **no WordPress.com writes or production theme changes**.

## Why this change exists

Real hosted GitHub-run WordPress Playground/Assembler screenshots from PR #823, run 41692157470, artifact 13261740450 (independently verified ZIP sha256 `800c39d30b78ebbe2ea099476154f74f31f47b9e0d36795db87185bc080a2e0a`), show a **620 CSS-pixel** unmodified flagship width at a **1440 CSS-pixel** viewport, and 72 synthetic Margins elements occupying a long, unstyled column before the flagship. The same runner's *browser-only* injected CSS expanded that canvas to 1440 px, but this is NOT proof of saved WordPress styling. The PR #823 test timed out at 20 min; it did not verify no-JS, media transfer bodies or cleanup. It also observed a serious axe `list` failure on `.wp-block-navigation__container` at 1440px. None of this means the actual live production homepage is broken in the same way.

## Actual engineering difference

1. `assembler_saved_layout_playground_only.css` holds a **visibly labeled, stage-only** adaptation of the previous browser study's working full-bleed geometry. Scoped through `body:has([data-fv-home-flagship])`; loaded inside the **Gutenberg candidate source** before editor Save, never injected by Chromium. It has no external imports, URLs, fonts or media dependencies. It is **not** a proposed general/global WordPress theme override.
2. The synthetic first Gutenberg block gets a labeled `role=region`, `tabindex=0` scrollable list, keeping all 72 invented test fragments visible to keyboard/touch/screen readers without JS; it explicitly does not represent the 72 genuine production Margins records.
3. The offline assembler records the stage stylesheet fingerprint separately from the eleven genuine source-controlled flagship assets. It rejects CSS HTML breakout, script tags, imports, external URLs and changed/missing expected stage selector/marker.
4. The real Assembler screenshot gate now requires a persisted `style[data-fv-stage-only="assembler-saved-layout"]`, actual canvas geometry within 2px of each **320 / 390 / 768 / 1440 / 1920px** viewport, a keyboard-labeled 72-fragment region, and **390px no-JS** evidence of the same layout. It captures unmodified screenshots **before** full-document axe; no browser-only visual bridge is permitted. The inherited #831 gate still fails on any whole-page WCAG-tagged axe finding.

## Verification honesty

The isolated WordPress/Gutenberg pipeline has previously verified exact 120,064-byte source persistence under #816, **before this modification**. Changing the saved Gutenberg candidate changes its digest: do NOT recycle prior #816's `020f455...` result as the new candidate proof. All source regression tests and the complete actual Assembler preview **must run again at this branch's exact commit**. The known Assembler theme-navigation axe issue is **not waived or fixed** by these layout styles. Browser screenshots, WordPress core/Assembler theme version and first-party image transfer SHA/bytes require a fresh receipt. If real browser/axe fails or hangs, mark FAIL/HOLD (not PASS).

### The environment's hard boundary

This fixture uses free isolated Playground WordPress, synthetic Margins/Jetpack, eleven authentic source-controlled flagship assets and downloaded free Assembler. It cannot demonstrate WordPress.com Personal plan host/global-styles parity, real Jetpack subscription, original page-6 CSS, browser Safari/physical zoom, field CWV or NYPL capture-specific rights. WordPress.com lists only production ID 256784396, and Personal does not provide native staging clone. Do not install a plugin or run any test draft on the live site.

## Must be true before release decision

- [ ] Exact-head isolated WordPress Save/readback + cleanup and complete Assembler 320/390/768/1440/1920 screenshots (persisted CSS, not injected).
- [ ] Whole-document axe and component axe all clear or independently reviewed/fixed, including Assembler navigation list issue.
- [ ] Separate no-JS, reduced-motion, touch, keyboard, physical 200% zoom/reflow, and manual WCAG 2.2 AA verification.
- [ ] Actual first-party image-body SHA/byte/MIME verification; NYPL image-specific permission resolved or rights-safe fallback retained.
- [ ] True page-6 Gutenberg source (read-only) + Focus Fieldbook/Jetpack signup and authentic 72 Margins preserved with tested release candidate; synthetic fixtures alone cannot release.
- [ ] Honest lab Lighthouse values/CWV evidence and independent QD exact SHA review.
- [ ] Founder reviews actual screenshot set and explicitly approves production release. **No implied approval from this PR.**

## Coordination

Issue #150 is primary homepage authority. Apollo #158 and Mind #171 remain separate lanes. PR #49 remains frozen SHA `10495883299d53596992c26a8987f629b2904670`. PR #823 was the browser-only bridge reference; PR #826/#831 is the active real saved-source/full-document axe test chain. Avoid resurrecting competing mockups or chapters.
