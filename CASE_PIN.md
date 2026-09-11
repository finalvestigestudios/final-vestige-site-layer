# Case Pin — exact-point sharing contract

Case Pin gives a reader a precise, same-origin link to the part of a published Final Vestige investigation they are actually looking at: a narrative passage, story-section heading, published figure, or published source note.

## Visitor job

Share one exact point in a long investigation without telling another reader to start at the top and hunt for it, and without creating an account, annotation record, tracking parameter, or private note.

## Interaction principle

- GitHub permalinks make a specific line or range directly addressable instead of linking only to a whole file.
- Web fragment identifiers provide a native mechanism for identifying a part or view of a document.
- Annotation systems such as Hypothesis demonstrate the value of attaching reader attention directly to source material rather than separating context from the document.

Case Pin adopts only that addressability principle. It does not copy any external visual treatment or create collaborative annotations.

## Final Vestige adaptation

On a qualifying investigation, an opening Case Pin explainer and a compact `Pin point` launcher are added. When the reader activates the launcher, the feature selects the eligible published element nearest the center of the current viewport and creates a query-free same-origin URL fragment.

Locator forms are intentionally compact and inspectable:

- `s:<section-ordinal>:<fingerprint>` — story section
- `p:<section-ordinal>:<paragraph-ordinal>:<fingerprint>` — narrative passage
- `f:<figure-ordinal>:<fingerprint>` — published figure
- `n:<source-number>:<fingerprint>` — published source note

The fingerprint is a deterministic FNV-1a value over normalized already-public text. It is used only to prevent a structurally shifted page from resolving an old pin to the wrong element. If the recorded ordinal no longer matches, Case Pin may recover only when exactly one eligible element of the same type has the same fingerprint. Otherwise it fails closed and says that the investigation may have changed; it never silently substitutes another passage.

## Qualification and evidence boundary

The feature activates only when all of the following are true:

- exactly one candidate Sources boundary exists and it is the canonical `h2#sources.fv-source-heading`;
- exactly one `[data-fv-footnotes]` list exists and follows that heading;
- 2–10 story H2s appear before Sources;
- 12–160 substantive narrative paragraphs appear before Sources; and
- 3–60 published source-note rows exist.

Figures are optional targets and must be published `figure.wp-block-image` elements before Sources. Case Pin does not infer evidence relationships, source quality, confidence, causation, or editorial significance.

## Privacy and network boundary

Case Pin uses the current DOM and URL only. It creates no account state and performs no fetch/XHR/WebSocket/sendBeacon request. It uses no cookie, localStorage, sessionStorage, IndexedDB, analytics hook, third-party service, query parameter, or History API mutation. Clipboard access occurs only after the visitor presses `Copy precise link`, with an in-dialog manual-copy fallback.

The copied link contains only the current origin/path plus a compact fragment locator. It contains no selected prose, note text, account identifier, tracking token, or behavioral history.

## Accessibility and responsive behavior

- Native `<dialog>` semantics with `aria-labelledby`.
- Focus moves into the generated-link field and returns to the launcher on close.
- Copy feedback is announced through `role=status` / `aria-live=polite`.
- Controls have a minimum 44px target size.
- Dedicated <=600px and <=360px layouts.
- Forced-colors, reduced-motion, and print behavior are explicit.
- Incoming pins focus the exact resolved target and show a visible `Shared point` marker that can be dismissed.

## Performance budget

No external assets, frameworks, observers, background polling, network requests, or persistent state. Qualification and target indexing are one bounded DOM pass at initialization. Viewport-nearest selection runs only when the visitor activates `Pin point`.

## Release boundary

This PR is a frozen feature artifact candidate, not executable merge/deployment authority. The active Case Search runtime release already occupies the governed integration lane. After independent QD, Case Pin must be integrated from then-current `production`, receive a new executable SHA, fresh CI and fresh independent QD, and only then may FVS Execution Dispatch merge/deploy it. Live desktop/mobile/accessibility/network/destination readback is mandatory before `IMPLEMENTED + VERIFIED`.
