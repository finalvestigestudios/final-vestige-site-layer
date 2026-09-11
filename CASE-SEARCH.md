# FVF-10 — Case Search

## Visitor job

Let a reader relocate a person, place, date, mechanism, source, or figure inside a long Final Vestige investigation without flattening the page into undifferentiated browser-Find matches or losing the surrounding section/evidence context.

## Final Vestige adaptation

Case Search adds one prominent **Search this investigation** launcher near the beginning of qualifying longform. The modal searches only material already published on that page and separates results into four useful result types across three scopes:

- **Story** — narrative passages plus section headings, with the nearest section name.
- **Sources** — published Final Vestige source-note records, retaining their source number.
- **Figures** — published captions plus image alt text, tied back to their surrounding story section.

The reader can scope the query to All / Story / Sources / Figures, search multiple terms, move through result buttons by keyboard, and jump directly to the matching published block. The destination receives a temporary bronze focus treatment and keyboard focus so the jump is perceivable rather than merely visual.

Case Search does **not** replace or intercept normal browser Find. It adds evidence-aware structure that browser Find cannot infer from Final Vestige's article DOM.

## Inspiration principle

- **DocumentCloud reader** keeps full-text document search directly beside page navigation so a researcher can find a term and move back into the primary record rather than into a detached search-results page.
- **GitHub scoped search / command palette** demonstrates the value of making current context an explicit search scope and letting users narrow what is being searched without rebuilding a query elsewhere.
- **W3C modal-dialog guidance** informs contained focus, Escape dismissal, visible close controls, and logical focus placement after a modal task.

Final Vestige adapts those principles to its own evidence model: one current investigation, typed result context, no external search service, and no claim that a matching source proves the surrounding prose.

## Qualification and failure behavior

The feature activates only on single-post longform with a recognizable Final Vestige Sources/References list, at least two source records, at least 12 qualifying narrative paragraphs, and at least 3,000 narrative characters before the source section. Existing Final Vestige feature UI, figures/captions, navigation, forms, sharing controls, and non-narrative chrome are excluded from Story extraction.

If native HTML dialog support is unavailable or the page does not meet the thresholds, Case Search remains inert. Search requires at least two typed characters. Rendering is capped at the first 60 matching blocks while the live status message retains the total match count.

## Privacy and content boundary

- query processing occurs entirely against the current page DOM
- no browser persistence
- no cookies, fingerprinting, account, or server state
- no analytics emission
- no fetch/XHR/WebSocket/sendBeacon
- no third-party scripts
- no content mutation or inferred citations
- no interception of Ctrl/Cmd+F
- published article/source/figure text remains the source of truth

## Performance budget

- one isolated Gutenberg HTML payload
- 16,098 bytes uncompressed / SHA-256 `1c9e61ccf0614f02e3b46cb3c16040a00dc6d9ac346fa710aef8c62255baa3f6`
- zero network requests and zero third-party dependencies
- full searchable index is built lazily on first launch and then reused
- result rendering is bounded to 60 buttons
- no media loads and no background polling

## Accessibility and responsive behavior

Case Search uses a native modal dialog, a visible labelled close control, immediate focus in the search field, live result-count announcements, 44px minimum interactive targets, Arrow Up/Down plus Home/End result navigation, and a deliberate focus handoff to the selected story/source/figure block. Ordinary close returns focus to the launcher. It includes 360px treatment, forced-colors support, reduced-motion behavior, and print cleanup.

## Delivery boundary

This branch is an artifact candidate based on the current inert `production` branch. It does not modify the Site Layer bootstrap/deployment runtime or any open feature PR and must not be merged merely because CI passes. Runtime-manifest integration waits for the governed deployment lane. Any later executable integration creates a new SHA and requires fresh CI + independent QD review before deployment and live destination verification.
