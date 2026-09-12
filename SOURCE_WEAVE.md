# FVF-17 — Source Weave

## Visitor job
Let a reader see the provenance shape of a long Final Vestige investigation: which already-published source notes are linked from which major story areas, which sources recur, and where each relationship appears in the article.

## Final Vestige adaptation
Source Weave is a visitor-initiated, read-only relationship view built entirely from the investigation's existing footnote markup. It adds a prominent `Map the sources` launcher before the first story section, then presents the explicit source-to-story relationships as an accessible desktop matrix and a mobile grouped list.

It does not infer semantic similarity, claim that a source proves a passage, score reliability, rate confidence, or treat an uncited passage as unsupported. The feature's visible copy states that its connections reflect existing page links and that counts are structural rather than quality/confidence scores.

## Inspiration principle
- **ProPublica Explore Sources:** make reporting provenance inspectable from the story rather than hiding source context elsewhere.
- **Connected Papers:** give readers a legible overview of relationships, while Final Vestige deliberately avoids inferred similarity or force-directed graph logic and uses only explicit editorial citation links.
- **W3C accessible table guidance:** relationships expressed in a grid use a caption plus explicit row/column headers with `scope`; the narrow-screen representation preserves the same relationships in a grouped list.

No visual trade dress or proprietary ranking/graph algorithm is copied.

## Qualification and bounds
The feature fails closed unless the page contains:
- a trusted Final Vestige Sources heading before `[data-fv-footnotes]`;
- 2–8 story H2 sections before Sources;
- 6–120 in-story `.fv-fn-ref[data-fv-fn]` references;
- 4–40 numbered published source-note records;
- at least 3 actually cited source notes; and
- at least 5 distinct source-to-story relationships.

An opening story area is included only when valid source links occur before the first story H2. No more than nine story areas are rendered.

## Interaction
- `Map the sources` opens a native dialog.
- Desktop: semantic source × story-area matrix, with source rows and story-area columns.
- A populated cell reports the exact number of existing citation links for that source in that story area.
- `All cited sources` and `Reused across story areas` expose a simple, explainable filter.
- Selecting a matrix/list relationship closes the workspace and focuses the first corresponding published citation.
- Selecting a source label closes the workspace and focuses the original published source note.
- Escape and Close dismiss the workspace and return focus to the launcher.
- At narrow widths the matrix becomes a section-grouped list rather than forcing a dense grid into the viewport.

## Accessibility
- native `<dialog>` with explicit labelled heading and predictable Escape/focus return;
- 44px primary/filter/relationship controls;
- semantic `<table>`, `<caption>`, `<th scope="col">`, and `<th scope="row">` desktop representation;
- equivalent relationship list at <=720px;
- visible focus treatment, forced-colors support, reduced-motion-aware jumps, 360px behavior, and print cleanup.

## Performance / privacy boundary
The relationship map is derived only from the current DOM. There is no fetch/XHR/WebSocket/sendBeacon call, third-party script or frame, browser storage, cookie, account state, analytics event, clipboard access, or history mutation. No published article prose, source note, citation destination, figure, taxonomy, Coming Soon state, indexing state, or Scout surface is modified.

## Delivery boundary
This branch is an artifact-review package based on the inert `production` baseline. Passing CI is evidence, not merge authority. Do not merge or deploy while the Site Layer bootstrap/deployment prerequisite remains open.

After the governed deployment lane is active, any executable Site Layer integration must be created from then-current `production`. That integration produces a new executable SHA and requires fresh exact-head CI, fresh independent QD, governed FVS Execution Dispatch, and live destination readback before `IMPLEMENTED + VERIFIED`.
