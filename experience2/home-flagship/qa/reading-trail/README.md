# Chapter Reading Trail — release-candidate design/UX note

**HOLD / DRAFT / NO PUBLISH.** Adds one additive progressive wayfinding layer to the seven-chapter **source-controlled** Experience 2.0 homepage, stacked on draft PR #212. Frozen homepage PR #49 and separate Apollo 1 R&D PR #158 are unchanged.

## What visitors gain

The existing seven native fragment links become a cohesive **reading trail**: the current chapter receives an accessible `aria-current="location"`, and a subtle 3-pixel antique-gold trail records progress through the seven original chapters. The bar is visual-only; it is not a timer, a completion score, an analytics event, or a gate. Desktop retains all seven chapter links; on narrow screens the native horizontal link row remains scrollable and keyboard navigable. The line is original CSS—not copied media or visual branding. Native links, all historical findings, linked source records and substantive content remain available with JavaScript disabled.

JavaScript checks the exact seven canonical IDs before enhancing. Scroll/resize/hash updates use passive listeners and requestAnimationFrame, and assign one `aria-current` attribute without announcing updates continuously. Keyboard-activated fragment links move focus programmatically to a destination marked `tabindex=-1`; pointer clicks preserve native behavior. Missing or duplicated target IDs fail closed to the original working anchors. Reduced-motion and print styles are provided. `--fv-trail-top` allows later WordPress integration to account for a hosting theme's fixed header without hard-coding offsets.

## Source custody and independence

No new image, CSS texture download, fonts, tracking, merchant URL, affiliate attribution, historic quote or factual claim. Existing original source links in the Franklin, NASA Apollo 1 and NYPL gallery remain unchanged. NYPL image reuse and scan-specific rights holds in prior PRs remain unresolved and **not waived**. Existing 72 WordPress Margins records, live Focus Fieldbook and Jetpack signup are untouched. Mind & Perception commercial separation follows Issue #171, with zero earning links in this feature.

## Executed local test scope — not production certification

- Actual new `reading-trail.css` and `reading-trail.js` were exercised in real Chromium/Playwright against the **existing representative combined-page fixture** from PR #212, augmented with seven chapter anchors. At 320, 360, 390, 600, 768, 1024, 1440 and 1920 CSS px: 80 assertions passed across native navigation, single active/current chapter, scroll progress, sticky nav, keyboard focus destination, JS-disabled native links and injected missing-chapter fail-closed state. Zero observed page errors/root horizontal overflow in that fixture.
- Source SHA-256 locally: JS `cb9e8897f35ca0248ddf37a8caf9d51c71bdf1057e1b01c028e995890423543e`; CSS `93d8fcac2b6b2015f4037b12c67963c3d2c6906995c6f7a1cc0cc9674323a585`. Recheck against the current GitHub head before independent review.
- The parent PR #212's source manifest has been extended to include these **two** assets so the private WordPress staging ZIP cannot silently omit them. It must pass its existing full-browser and PHP checks on the **new exact head** before release.
- These results are not whole-github checkout Chromium proof, WordPress/Assembler staging, real hosted network media delivery, axe/screen-reader/Safari certification or field Core Web Vitals. Synthetic screenshots do not prove actual deployment LCP/INP/CLS.

## Required next gates

1. Re-run `qa/integration/check_contract.py`, `verify_full_browser.py`, `tests/test_release_gates.py` on exact PR checkout.
2. Test native Wayfinding sticky offset under the *real Assembler* header, 200% zoom, Safari, forced colors, VoiceOver/NVDA. Confirm original 72 Margins and subscription block remain unaffected.
3. Realistic staging Lighthouse / source-rights review, independent exact-SHA QD, hosted CI recovery (Issue #75), branch protections (Issue #191), and explicit founder authorization before any publication.

**No WordPress write, theme edit, deployment, merge, new subscription or user telemetry was performed.**
