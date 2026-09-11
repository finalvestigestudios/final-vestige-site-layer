# FVF-8 — Return Trail

## Visitor job

Help a reader leave a long investigation and return later to the same place without creating an account, rebuilding context, or treating a skimmed position as a verified “read” state.

## Final Vestige adaptation

Return Trail stores a deliberately small, device-local trail for up to three qualifying longform investigations. It records only the same-origin path, article title, nearest in-story marker index, nearest preceding section heading, approximate page position, and update timestamp. Records expire after 30 days and are removed automatically when the visitor reaches the end of the article.

On a qualifying article revisit, an inline Return Trail card offers **Return to last place**. On the homepage, Journal, Archive, and Investigations landing surfaces, a compact **Continue reading** card resumes the most recent unfinished investigation in one click. **Forget** removes that page's saved trail immediately.

The UI says `saved only in this browser for up to 30 days.` No account, server sync, analytics emission, external request, cookie, fingerprint, or third-party service is involved.

## Inspiration principle

- **Readwise Reader** distinguishes reading progress from last location and gives readers an explicit way to return to a prior position after navigating elsewhere.
- **Instapaper** treats continuity across reading sessions as a core reading-product job.

Final Vestige intentionally does less: no account sync and no claim to infer what the visitor truly read. Return Trail saves a last place, not a comprehension or completion score.

## Qualification and failure behavior

The feature activates on single-post longform only when the article contains at least 12 narrative paragraphs, 3,000 narrative characters, and 10 usable story markers before the Sources section. Source lists, footnotes, captions, navigation, sharing UI, and footer content are excluded from position tracking.

If local storage is blocked or unavailable, the feature silently degrades to no persistence. It never blocks reading. If a record is older than 30 days, below 5%, at or above 95%, or no longer maps to the current article structure, it is not offered as a resume point.

## Performance budget

- one isolated Gutenberg HTML payload
- under 10 KB uncompressed
- zero network requests
- zero third-party dependencies
- scroll persistence throttled to 850 ms
- at most three local records
- no layout-shifting media

## Accessibility and responsive behavior

Controls are native links/buttons with at least 44px target height, an ARIA-labelled region, polite status announcements, explicit keyboard focus placement after resume, reduced-motion handling, forced-colors support, 360px treatment, and print cleanup.

## Delivery boundary

This branch is an artifact candidate based on the inert `production` branch. It does not change the frozen Site Layer bootstrap runtime and must not be merged merely because CI passes. Runtime-manifest integration waits for the governed Site Layer deployment lane; any later executable integration creates a new SHA and requires fresh CI + independent QD review.
