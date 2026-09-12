# Source Route R1 — provisional feature identity

## Purpose

Source Route is a visitor-initiated citation reading path for evidence-rich Final Vestige investigations. It keeps the published passage and its already-linked source note together while a reader moves through citations in story order. It does not create citations, infer evidence, rate reliability, or claim that a linked source proves nearby prose.

This is a provisional feature identity. Canonical FVF-20 remains Case Packet; Source Route must not reuse that ledger ID.

## Interaction job

The interaction adapts the research-context job behind reference previews and anchored document/source navigation without copying another product's trade dress. A reader can choose **All citations** or **First use per source**, see the nearest story section, read the published passage with citation UI removed, inspect the published source-note text, and jump back to the original passage or source note.

## Trusted source boundary

Source Route fails closed unless:

1. Exactly one article element matches either `#sources` or `.fv-source-heading`.
2. That sole candidate is an `H2` carrying both `id="sources"` and class `fv-source-heading`.
3. Exactly one `[data-fv-footnotes]` `UL`/`OL` exists and follows that heading.
4. The article contains 2–10 pre-Sources story H2s and 10–140 substantive narrative paragraphs.
5. The source list contains 3–40 uniquely numbered `li#fv-fn-N` records.
6. There are 6–60 pre-Sources citation anchors using the live `.fv-fn-ref[data-fv-fn]` contract.
7. Every participating citation has numeric `data-fv-fn`, exact `href="#fv-fn-N"`, and a matching published source note.
8. At least three distinct published source notes are actually cited.

No `.fv-fn-mark` wrapper is required. Wrapper-present markup remains compatible because the anchor is authoritative. Mixed exact/partial, duplicate exact, reversed source-list, duplicate note-root, missing-note, and insufficient-citation fixtures fail closed.

## Nondestructive DOM-state contract

`View passage` and `View source note` obey the current Site Sprint invariant:

- scrolling is attempted before any mutation of the destination node;
- feature-owned `tabindex="-1"` is added only when the publisher node had no tabindex;
- that temporary tabindex is retained only while the destination owns focus and is restored on blur;
- existing/nondefault tabindex values are preserved exactly;
- temporary `fvsr-flash` is ownership-tracked and a pre-owned token is never removed;
- a node that originally had no `class` attribute returns to having no `class` attribute after cleanup;
- repeated jumps clean the prior feature-owned transaction before beginning another;
- forced scroll or focus failure restores publisher state and recovers usable focus to the launcher;
- no destination IDs, inline styles, ARIA attributes, or publisher-owned classes are rewritten.

## Accessibility / responsive behavior

- Native modal `dialog` with named title and logical launcher focus return.
- `aria-live="polite"` route-position updates.
- 44px minimum controls and explicit route-mode pressed states.
- Left / Right / Home / End keyboard transport.
- <=680px full-height mobile dialog plus 360px tuning.
- Reduced-motion, forced-colors, and print handling.
- Browser regression includes wrapper-free and wrapper-present valid paths, absent state, pre-owned/nondefault state, repeated jumps, scroll failure, focus failure, and all boundary fail-closed fixtures.

## Privacy / SEO / performance

Current DOM only. No fetch/XHR/WebSocket/sendBeacon, cookies, local/session storage, IndexedDB, analytics, third-party scripts/frames, clipboard writes, or history mutation. The feature does not hide or replace crawlable article/source content; it is a progressive enhancement over published HTML. Dialog construction is lazy after visitor invocation.

## Frozen source/build identity

- Repository: `finalvestigestudios/final-vestige-site-layer`
- Target: `production`
- Build base: `3f7841a7c671f9e8e955b417480d853ad0a0a948`
- Branch: `repair/source-route-r1-live-citation-state`
- Payload: `payloads/source-route-wp-block-v1.txt`
- Payload bytes: **15,089**
- Payload SHA-256: **`8ba39dbca28b99c8c555923cc0b8e42729fe80106efba624de87dea269cf6d3c`**
- Verifier: `tests/verify_source_route.py`
- Workflow: `.github/workflows/source-route-ci.yml`

The exact PR head is frozen only after GitHub creates the four-file bounded successor. Any payload/test/workflow/contract change creates a new identity and requires fresh verification.

## Governance boundary

This is source/build repair work only. Green CI is evidence, not QD approval. Do not merge or deploy from this candidate. Fresh independent QD must review one exact frozen head and exact executed CI. Any later executable integration must start from then-current `production`, receive a new executable identity, fresh CI, fresh independent QD, and then use the governed Decision Queue → Chief → FVS Execution Dispatch path. No whole-site launch/indexing, spending, payment activation, private-user processing, account/permission change, public Scout release, or external commitment is included.
