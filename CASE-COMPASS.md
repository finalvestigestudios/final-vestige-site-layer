# FVF-13 — Case Compass

## Visitor job

Help a reader understand the shape of a long Final Vestige investigation, see their current section, and jump to another major turn in the story without opening search, losing their place, or reducing the article to a generic table of contents.

## Interaction principle

Case Compass combines three proven principles while remaining visually and behaviorally native to Final Vestige:

- long-document tables of contents make headings skimmable and directly navigable;
- semantic headings provide a programmatic page outline useful for orientation and accessibility;
- viewport observation can keep the reader's current location synchronized without polling or persistent state.

The feature does not copy another product's visual treatment. It turns Final Vestige's existing H2 story structure into a compact "case map" that also reports exact page-structure clues: passages, figures, and distinct already-linked source notes.

## Qualification and fail-closed boundary

The feature activates only on a `single-post` page when all of the following are true:

- native `<dialog>` is supported;
- the article contains the trusted Final Vestige `h2#sources.fv-source-heading` boundary;
- the article contains `.fv-source-list[data-fv-footnotes]`;
- the trusted Sources heading precedes that source-note list in the same content root;
- at least three story H2 headings occur before Sources;
- at least twelve substantive paragraphs and 2,800 narrative characters occur before Sources;
- an opening narrative passage exists before the first story H2;
- the resulting map contains at least four sections including Opening.

If any requirement fails, Case Compass adds nothing to the page.

## Visitor experience

Case Compass appears immediately before the first story H2 after the opening. It provides:

- a prominent `Open full map` control;
- an inline section rail for one-click jumps;
- a live `You're in` location indicator;
- a full dialog map showing each section's exact passage, figure, and distinct linked-source-note counts;
- keyboard Arrow/Home/End navigation inside the full map;
- visible, focusable story arrival after a jump;
- motion-aware smooth scrolling;
- responsive horizontal section rail on mobile.

Counts are explicitly described as page structure, not an evidence or confidence score.

## Accessibility and performance

- native modal dialog behavior;
- 44px minimum controls;
- logical focus return on ordinary close and focus handoff to the selected story section after navigation;
- `aria-current="location"` for current section;
- polite live current-section announcement;
- forced-colors, reduced-motion, print cleanup, 360px behavior;
- `IntersectionObserver` for asynchronous current-section tracking, with a passive/animation-frame scroll fallback;
- no third-party library.

## Privacy / network / evidence boundary

Case Compass reads only the current page DOM. It does not use cookies, browser persistence, analytics, fetch/XHR/WebSocket/sendBeacon, third-party scripts, account state, or history mutation. It does not change article wording, citations, source destinations, figure pixels, or source records. It does not infer evidence quality or confidence.

## Frozen artifact identity

- payload: `payloads/case-compass-wp-block-v1.txt`
- bytes: `15713`
- SHA-256: `6e4e0a8abb25676924d7a4f7bbfcbe024e7a3a19c1f267854ca16849dd7c37ee`
- deterministic verifier: `tests/verify_case_compass.py`
- dedicated workflow: `.github/workflows/case-compass-ci.yml`

This artifact is intentionally based on the inert `production` branch. It is not merge or deployment authorization. Runtime integration after the governed Site Layer bootstrap will create a new executable identity and requires fresh CI plus independent QD review before deployment.
