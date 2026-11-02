# Victory Point Chronicle Reading Lens — Experience 2.0

**UNPUBLISHED stacked feature branch, built on homepage Observer Lab PR #199.** PR #49 is frozen, and live WordPress homepage page 6, the 72 Margins items, the Focus Fieldbook and Jetpack signup must not be modified.

## What visitors gain

The original 1847 “All well” note and the April 1848 marginal update are already both visible in the original HTML. A source-driven, opt-in toolbar now lets readers read the 1847 note alone, the 1848 addition alone, or compare both. Default enhanced state shows **both**—the reading lens never withholds information on initial load. A live accessible sentence tells readers when one part is temporarily hidden. The source-limit disclosure and museum/source links remain visible in all states. Mobile uses full-width 49px buttons at narrow widths. No autoplay, timers, tracking, vendor links, or forced animation.

## Historiography and media custody

Canadian Museum of History official [Victory Point Note transcription](https://www.historymuseum.ca/blog/a-very-special-piece-of-paper) shows an original note dated 28 May 1847, the later addition dated 25 April 1848 and deserted ships dated 22 April. The existing original-object link is [Royal Museums Greenwich](https://www.rmg.co.uk/collections/objects/rmgc-object-504898). RMG cataloguing has referred to 26 April while the written transcription says 25 April; **the existing non-speculative “APRIL 1848” display and existing catalogue-discrepancy note remain unaltered.** The toolbar changes presentation, not factual text.

New visuals are original scoped CSS and semantic HTML. **No historical scans, photographs, image bytes, external fonts or plugins** introduced; all existing homepage image-licensing issues remain in hold. The presentation is explicitly labeled original editorial typesetting, not a facsimile.

## Implementation and guards

- `chronicle-lens.html`: 3 mutually exclusive reading views, aria-pressed buttons, polite live status, controls initially hidden for no-JS.
- `chronicle-lens.css`: gold/teal treatment, mobile layout, print restores **both** notes, reduced-motion override, no state-specific hiding unless the selector is activated.
- `chronicle-lens.js`: optional event handlers, keyboard Arrow/Home/End, fail-open state restoration if initialization throws. No capture/cookie or remote dependency.
- `chronicle.html`, `index.html`: identical toolbar inserted at exact existing source-accuracy label; only standalone index loads new deferred JS and CSS.
- `tests/test_chronicle_lens.py`: source-integrity, accessibility structure, fail-open and commercial-content regressions.
- `qa/CHRONICLE_LENS_BROWSER_RESULTS.json`: actual local Chrome component-fixture measurements; this is NOT full-page staging or CWV.

## Actually executed local QA (2026-10-30)

Tested **8 viewport widths 320, 360, 390, 600, 768, 1024, 1440, 1920** on the exact pre-existing chapter HTML/CSS checked against repository Git blobs, plus the locally authored new module. Every width passed 1847-only/1848-only/compare, keyboard Home/End/ArrowRight, real native detail toggle, all three source links, button-height 49–51px, 0px root horizontal overflow and no console page errors. JavaScript-disabled 390 and 1440 tests exposed both entries. Injected second-listener failure restored the two-entry no-JS reading. CSS 200% zoom 390 and 768 reported no root horizontal overflow; this is a synthetic zoom check, not a WCAG certification. A separate local six-test Python source suite also passed against a representative integration fixture; re-run against **exact new GitHub SHA** before QD.

**Remaining release gates:** exact combined homepage full-browser + rendered WordPress Assembler staging, plugin/script sanitization, 72-Margins and single-Jetpack check, independent 2.2 AA review with axe and assistive technologies, iOS Safari, actual Lighthouse/p75 CWV, full rights audit, GitHub CI recovery and independent exact-head QD PASS. **No production publication, no WordPress writes, no PR #49 changes.**
