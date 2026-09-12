# Case Pin R1 — nondestructive exact-point sharing contract

Case Pin gives a reader a precise, same-origin link to the part of a published Final Vestige investigation they are actually looking at: a narrative passage, story-section heading, published figure, or published source note.

## R1 repair

Independent QD found that the original candidate removed `tabindex` on Shared point dismissal even when that attribute belonged to the publisher/theme. R1 makes incoming-marker state ownership explicit.

- If the resolved target already has any `tabindex`, Case Pin does not alter it.
- If the target has no `tabindex`, Case Pin may add temporary `tabindex="-1"` for the incoming focus transaction and removes it on marker dismissal only when that exact feature-owned state is still present.
- If the target already carries the `fvcp-target` class, Case Pin does not claim ownership of that class token or remove it later.
- If Case Pin adds `fvcp-target`, it removes only that token on dismissal. When the element originally had no `class` attribute, cleanup restores the attribute to absent rather than leaving `class=""` behind.
- Browser regressions cover absent state, publisher-owned `tabindex="0"`, publisher-owned nondefault `tabindex="-7"`, publisher-owned classes, a pre-owned `fvcp-target` token, and repeated dialog open/close focus return.

## Visitor job and preserved behavior

Share one exact point in a long investigation without telling another reader to start at the top and hunt for it, and without creating an account, annotation record, tracking parameter, or private note.

Locator forms remain compact and inspectable:

- `s:<section-ordinal>:<fingerprint>` — story section
- `p:<section-ordinal>:<paragraph-ordinal>:<fingerprint>` — narrative passage
- `f:<figure-ordinal>:<fingerprint>` — published figure
- `n:<source-number>:<fingerprint>` — published source note

The deterministic fingerprint is computed from already-public normalized text. If the recorded ordinal no longer matches, Case Pin may recover only when exactly one eligible element of the same type has the same fingerprint. Otherwise it fails closed and says the investigation may have changed; it never silently substitutes another passage.

## Qualification and evidence boundary

The feature activates only when the existing Case Pin source/build contract qualifies the investigation: one canonical Final Vestige Sources heading, one subsequent `[data-fv-footnotes]` list, bounded story headings/narrative/source rows, and optional published pre-Sources figures. Case Pin does not infer evidence relationships, source quality, confidence, causation, or editorial significance.

## Privacy / network / SEO

Case Pin uses only the current DOM and URL. It creates no account state and performs no fetch/XHR/WebSocket/sendBeacon request. It uses no cookies, localStorage, sessionStorage, IndexedDB, analytics hook, third-party service, query parameter, or History API mutation. Clipboard access occurs only after an explicit visitor copy action with an in-dialog fallback. Existing article content remains in the page and crawlable; Case Pin adds no hidden SEO text.

## Accessibility / responsive behavior

Native dialog semantics, logical close-focus return, live copy status, minimum 44px controls, <=600px and <=360px layouts, forced-colors, reduced-motion and print handling remain part of the contract. Incoming-pin focus/highlight is temporary and must preserve publisher-owned DOM state exactly after dismissal.

## Acceptance / rollback boundary

R1 is a source/build review candidate only. Exact payload bytes/hash plus dedicated browser CI and repository-wide CI must be green on one frozen head before fresh independent QD review. Green CI does not authorize merge or deployment. If QD later requires executable integration, it must be rebuilt from then-current `production`, receive a new frozen executable identity, fresh CI and fresh independent QD before governed Dispatch.

Rollback is deletion/non-integration of this bounded artifact; R1 makes no production runtime, WordPress content, navigation, Coming Soon/indexing, private-user, billing, account/permission, Scout, or external-commitment change.
