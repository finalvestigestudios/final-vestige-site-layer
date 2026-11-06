# EX2 archival motion: conversion-safe, consent-based interaction review

Status: **ISOLATED DRAFT / RELEASE HOLD**. No production WordPress writes.
Base: draft PR #1276, exact SHA `bddc087666ee10f7eec602862947216a56973bfa`.

## Actual source change

The seven-chapter Playground Blueprint now renders all **72 published-source** historical notes as a horizontally browseable evidence rail **by default**, even with JavaScript disabled. Previously the source used a CSS 360-second automatic rotator with pause only on hover/focus. Motion is now explicitly optional via a native checkbox. Modern CSS `:has` enables animation only after the visitor selects the checkbox **and** only when `prefers-reduced-motion: no-preference`. Unsupported browsers stay static. Reduced-motion visitors see the static scrollable record rail without a misleading animation control. Scrolling is keyboard accessible via the existing focusable window and ArrowRight/ArrowLeft, and touch scroll is native.

This specifically addresses **visitor agency, no-JS meaning and reading access**, rather than an aesthetic redesign. The opening chapters, hero, source text, images, destinations, 52-page Focus Fieldbook and production Jetpack signup are unchanged. No evidence claim or external URL is introduced. The overlay is inside the private source-controlled WordPress Playground candidate only.

## Verifications actually performed

- **Exact committed source test:** `verify_opt_in_margins_motion.cjs`, invoked by a V8-compatible `require` shim over both GitHub-returned **exact committed UTF-8 blobs**. **1 positive source / 8 negative mutants PASS**. This is *not native Node CI*.
- **Source-integration comparison:** all **72/72 record strings identical** before/after, seven chapter anchors unchanged, two image tags unchanged, underlying JavaScript unchanged, review-marker and WordPress import admission unchanged; valid JSON.
- **Real Chromium, representative fixture ONLY:** **18/18 PASS** (320/360/390/768/1440/1920 times no-JS static, opted-in, reduced-motion no-JS). Four desktop/mobile screenshots and additional scenario images are preserved in the user-facing evidence ZIP. No document horizontal overflow, card contents visible in the static state, toggle hidden for reduced motion, focus CTA target meets 44px in the fixture.
- **Keyboard check:** a focused fragment window responded to ArrowRight with horizontal movement at 390px (scrollLeft 12 to 289 in the representative fixture). Home/End did *not* navigate the horizontal region; do not claim that behavior.
- **Representative before/after at 390px:** before: 72 items present, `animationName=fvMarginReveal`, `overflowX=hidden`, strip height 121px; after: 72 items present, `animationName=none`, `overflowX=auto`, strip height 186px. These values are fixture observations, not the WordPress/Assembler baseline.

## Outstanding HOLD gates

Actual WordPress Playground boot with pinned Assembler, full seven-chapter Chromium screenshots and first-party image transfer/decode, keyboard/touch/no-JS across real rendering, genuine axe-core WCAG 2.2 AA, 200% zoom, Lighthouse/CWV and rights/Jetpack confirmations. A source-level check cannot establish WCAG or conversion lift. WordPress.com Personal does not offer a native clone. GitHub Actions/independent QD must qualify the final exact SHA.

## Conversion contract

**Offer**: Free 52-page Focus Fieldbook. **Funnel step**: audience homepage evidence → trust/reading control → Focus CTA → confirmed lead → independently verified paid order. **Blocker**: non-optional moving notes can compete with visitor reading and reduce control, particularly with touch. **Experiment**: default-static evidence rail versus existing rotating notes; measure qualified Focus clicks and verified conversion only after separately approved deployment/attribution. **Evidence**: source change plus fixtures, not paid conversion. **Owner**: interim homepage engineering (review candidate), independent Site QA (acceptance), Claude (live attribution/backend), founder (release). No inferred sales.

No new history, affiliate claims, marketing events, plugins, subscriptions, fees or public CMS actions.
