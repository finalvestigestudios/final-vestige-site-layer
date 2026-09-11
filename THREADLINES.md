# FVF-15 — Threadlines

## Visitor job
Help a reader who finishes one Final Vestige investigation discover the next genuinely connected case without a black-box recommendation widget.

## Final Vestige adaptation
Threadlines reads only the current published post's WordPress categories and tags, then compares them with lightweight metadata for other published Final Vestige posts. Shared editorial tags carry more weight than broad categories. The four strongest matches are shown with the exact shared labels that caused the connection. Readers can filter by those visible threads.

## Interaction contract
- Appears only on a WordPress single post with a resolvable numeric post ID.
- Makes no request until the visitor chooses **Find related investigations**.
- Requests only same-origin `/wp-json/wp/v2/` public REST resources with `credentials: omit`.
- Candidate query is explicitly limited to `status=publish` and lightweight fields.
- Rejects candidate links whose origin differs from the current Final Vestige origin.
- Uses deterministic taxonomy overlap only: shared tag = 100 points, shared category = 10 points. No behavioral profile, inferred topic, hidden ML score, or personalized ranking.
- Keeps at most 12 qualifying candidates in memory and renders at most four at once.
- Gives every rendered card human-readable connection reasons and exposes the ranking method in the interface.
- Stores nothing in browser persistence, sends no analytics, and loads no third-party script, image, frame, or service.
- Fails gracefully if the public REST endpoint is unavailable and offers a retry.

## Accessibility and responsive behavior
- Native buttons and links with 44px minimum targets and visible focus rings.
- `aria-pressed` filter state and polite live result/loading status.
- Keyboard-operable without custom key traps.
- Single-column card layout on narrow screens; horizontally scrollable filter row rather than wrapping into an oversized control block.
- Forced-colors, reduced-motion, and print-specific handling.

## Performance budget
The feature adds no images and performs no background polling. A visitor action triggers two bounded same-origin public REST reads: one current-post taxonomy read and one lightweight published-post metadata read capped at 60 posts. An 8-second abort guard prevents a stalled endpoint from hanging the interface.

## Inspiration principle
- Notion backlinks: expose navigable relationships instead of hiding connections behind opaque ranking.
- ArcGIS StoryMaps Collections: bundle related stories into a cohesive, explorable set.
- Smithsonian collection experiences: reveal useful and sometimes unexpected connections across separately published objects/stories.

The visual design and ranking model are original to Final Vestige; no external trade dress is copied.

## Delivery boundary
This branch is an artifact candidate only. Do not merge or deploy while the Site Layer bootstrap prerequisite remains open. Any later executable integration from then-current `production` creates a new executable identity and requires fresh deterministic CI, independent Quality Director review, governed execution, and live destination readback before `IMPLEMENTED + VERIFIED`.
