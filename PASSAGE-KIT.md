# FVF-9 — Passage Kit

## Visitor job

Let a reader carry one exact published passage from a Final Vestige investigation into their own notes together with the source notes already linked to that passage, without rebuilding context by hand.

## Final Vestige adaptation

Passage Kit adds one compact, opt-in research control near the beginning of qualifying longform. **Show copy controls** reveals a restrained action beneath each narrative passage. If the passage already contains Final Vestige source-note references, the action copies the published passage, article title, nearest section heading, query-free article URL, and those exact linked source notes. If the passage has no linked note, it copies the passage with article context only.

The interface states: `Copies published wording and linked source notes. It does not rate the evidence.` Passage Kit does not infer missing citations, invent bibliographic fields, score source quality, or claim that a linked source proves a passage.

## Inspiration principle

- **Zotero PDF Reader / notes** makes selected annotations portable while preserving links/citations back to source context.
- **Readwise Reader export** makes captured highlights easy to carry into a notes workflow by clipboard or Markdown export.

Final Vestige adapts the portability principle directly to its existing evidence model: carry the passage and only the source notes already attached to it, without creating a new annotation account, private highlight store, or external service.

## Qualification and failure behavior

The feature activates only on single-post longform with a recognizable Final Vestige Sources/References list, at least two source records, at least 12 qualifying narrative paragraphs, and at least 3,000 narrative characters before the source section. Sources, captions, navigation, forms, sharing UI, and feature controls are excluded from passage extraction.

The feature is off by default. If clipboard permission is unavailable, it falls back to the browser's copy prompt. If a citation marker cannot resolve to a published source record, Passage Kit does not invent or substitute one.

## Privacy and evidence boundary

- no browser persistence
- no account or server state
- no cookies or fingerprinting
- no analytics emission
- no fetch/XHR/WebSocket/sendBeacon
- no third-party scripts
- no modification of article prose, source notes, or citation destinations
- copied page reference uses same-origin path only and excludes query parameters

## Performance budget

- one isolated Gutenberg HTML payload
- under 9 KB uncompressed
- zero network requests
- zero third-party dependencies
- control DOM is created lazily only after the reader opts in
- no media or layout-shifting asset loads

## Accessibility and responsive behavior

Passage Kit uses native buttons, 44px minimum targets, a labelled region, polite status announcements, Escape to hide the opt-in controls and return focus, 360px treatment, forced-colors support, reduced-motion handling, and print cleanup.

## Delivery boundary

This branch is an artifact candidate based on the inert `production` branch. It does not change the frozen Site Layer bootstrap/deployment runtime and must not be merged merely because CI passes. Runtime-manifest integration waits for the governed deployment lane; any later executable integration creates a new SHA and requires fresh CI + independent QD review before deployment and live destination verification.
