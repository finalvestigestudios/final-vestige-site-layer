# FVF-7 — Reading Focus

## Visitor job

Give readers a deliberate, low-distraction way to work through long Final Vestige investigations while keeping the published article, figures, links, and source trail intact.

## Final Vestige adaptation

Reading Focus appears only on qualifying single-post longform. It inserts one restrained in-article launcher after the opening paragraphs. When activated, a compact dock provides:

- 100%, 115%, and 130% narrative text sizes;
- standard, narrow, and wide reading measures;
- an optional paragraph guide with Previous/Next navigation;
- a one-action Exit that restores the ordinary page and returns focus to the launcher.

The feature does not rewrite, clone, summarize, translate, score, or save article content. It does not alter URLs or existing citations. Source lists and figure captions are excluded from the narrative-text transformation. No preferences persist after the page session.

## Interaction principle

The feature adapts the reader-control principle demonstrated by Microsoft Immersive Reader: give readers explicit control over text presentation and focus rather than assuming one layout fits everyone. The paragraph guide borrows the useful focus-narrowing idea without hiding the rest of the article or lowering text contrast. W3C guidance on visual presentation also motivates adjustable measure, generous line height, and robust zoom/reflow behavior.

## Qualification / fail-closed behavior

The payload activates only when all of the following are true:

1. WordPress identifies the page as a single post;
2. a post-content/article root exists;
3. at least 12 qualifying narrative paragraphs occur before the source section;
4. those paragraphs contain at least 3,000 characters of text.

Otherwise the payload makes no visible change.

## Accessibility and privacy contract

- native buttons only; no custom button roles;
- minimum 44×44 CSS-pixel controls;
- `aria-pressed` for toggle state;
- polite live-region announcements for control changes and guided paragraph position;
- Escape exits Reading Focus unless another open dialog should own Escape;
- exit restores focus to the launcher;
- 360px small-mobile treatment;
- reduced-motion and forced-colors handling;
- print output excludes Reading Focus controls;
- no `fetch`, XHR, browser storage, IndexedDB, or external-script dependency;
- microcopy explicitly says `Nothing is saved.`

## Performance contract

One isolated Gutenberg HTML payload with no dependencies and no network requests. The scroll listener is installed only while Reading Focus is active and is requestAnimationFrame-throttled; paragraph-position work runs only when the optional paragraph guide is enabled.

## Exact artifact

- `payloads/reading-focus-wp-block-v1.txt`
- bytes: `11,622`
- SHA-256: `b37a88379c49774ce05bd4bbdda2cf314af544acbb57f71e2a2547bdba5aeb12`

Deterministic verification: `tests/verify_reading_focus.py` and `.github/workflows/reading-focus-ci.yml`.

## Delivery boundary

This branch is intentionally based on the current inert `production` branch. It is an artifact + deterministic-CI candidate and does not modify the frozen Site Layer bootstrap runtime or other open feature candidates. Runtime-manifest integration waits for the one-time WordPress GitHub Deployment/bootstrap lane to become active. That integration will create a new executable SHA and therefore requires fresh independent QD review before deployment.

Passing CI is not merge authorization. Whole-site launch/indexing, Scout disclosure, spending, accounts/permissions, private-user processing, or destructive actions remain outside this feature.

## Live verification contract after deployment

Verify at desktop plus mobile-relevant widths including 320 CSS px and 200% browser zoom:

1. launcher appears only on qualifying longform;
2. activation/deactivation and focus return work by keyboard;
3. 100/115/130 text sizes remain readable without horizontal text scrolling;
4. narrow/standard/wide measures change narrative measure without damaging figures or sources;
5. paragraph guide highlights only the current narrative paragraph and Previous/Next boundaries disable correctly;
6. Escape exits unless another open dialog owns Escape;
7. source notes, citations, figures, links, Evidence Trace/Evidence Map/Detail Lens behavior remain intact;
8. reduced-motion and forced-colors states remain usable;
9. no console errors, unexpected requests, storage writes, or layout shift occur before activation.
