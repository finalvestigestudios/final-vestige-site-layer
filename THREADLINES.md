# FVF-15 — Threadlines

## Visitor job
Help a reader who finishes one Final Vestige investigation discover the next genuinely connected case without a black-box recommendation widget.

## Final Vestige adaptation
Threadlines reads only the current published post's WordPress categories and tags, then compares them with lightweight metadata for other published Final Vestige posts. Shared editorial tags carry more weight than broad categories. The four strongest matches are shown with the exact published labels that caused the connection. Readers can filter by those visible threads.

## Interaction contract
- Appears only on a WordPress single post with a resolvable numeric post ID.
- Makes no request until the visitor chooses **Find related investigations**.
- Requests only same-origin `/wp-json/wp/v2/` public REST resources with `credentials: omit`.
- Candidate query is explicitly limited to `status=publish` and lightweight fields.
- Rejects candidate links whose origin differs from the current Final Vestige origin.
- Uses deterministic taxonomy overlap only: each shared tag adds 100 points and each shared category adds 10; ties break by publication date, then title. The same ranking contract is disclosed in the visitor interface.
- Requires an exact resolved editorial name for every current-post tag/category before ranking. If embedded taxonomy metadata is missing or partial, Threadlines fails closed after the current-post read and explicitly says it will not guess; it never substitutes generic `Shared tag` / `Shared category` reasons.
- Keeps at most 12 qualifying candidates in memory and renders at most four at once.
- Gives every rendered card exact human-readable connection labels and drops any candidate whose reason labels cannot be fully resolved.
- Stores nothing in browser persistence, sends no analytics, and loads no third-party script, image, frame, or service.
- Fails gracefully if the public REST endpoint is unavailable and offers a retry.

## Accessibility and responsive behavior
- Native buttons and links with 44px minimum targets and visible focus rings.
- `aria-pressed` filter state and polite live result/loading status.
- Keyboard-operable without custom key traps.
- Single-column card layout on narrow screens; horizontally scrollable filter row rather than wrapping into an oversized control block.
- Forced-colors, reduced-motion, and print-specific handling.

## Performance budget
The feature adds no images and performs no background polling. A successful visitor action triggers two bounded same-origin public REST reads: one current-post taxonomy read and one lightweight published-post metadata read capped at 60 posts. If exact current taxonomy labels are incomplete, Threadlines fails closed after the first read. An 8-second abort guard prevents a stalled endpoint from hanging the interface.

## R1 adversarial contract
The browser regression suite must cover complete taxonomy metadata, wholly missing embedded term labels, partially missing embedded term labels, public REST failure/retry, and no-post-ID fail-closed behavior. Missing/partial taxonomy fixtures must prove there is exactly one public REST read, zero rendered candidates, no generic taxonomy fallback label, and a visible no-guess explanation. Existing same-origin, credentials-omit, `status=publish`, origin rejection, ranking, filtering, accessibility, privacy, responsive, forced-colors, reduced-motion and print assertions remain required.

## Inspiration principle
- Notion backlinks: expose navigable relationships instead of hiding connections behind opaque ranking.
- ArcGIS StoryMaps Collections: bundle related stories into a cohesive, explorable set.
- Smithsonian collection experiences: reveal useful and sometimes unexpected connections across separately published objects/stories.

The visual design and ranking model are original to Final Vestige; no external trade dress is copied.

## Delivery boundary
This branch is an artifact candidate only. Do not merge or deploy until a fresh independent Quality Director review passes the exact frozen R1 head. Any later executable integration from then-current `production` creates a new executable identity and requires fresh deterministic CI, independent QD review, governed execution, and live destination readback before `IMPLEMENTED + VERIFIED`.
