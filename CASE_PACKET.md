# FVF-21 — Case Packet

## Purpose

Case Packet is a visitor-initiated research handoff for evidence-rich Final Vestige investigations. It solves a common failure mode in longform research: readers can find the passages they need, but when they move those passages into a class packet, meeting notes, research binder, or PDF they often lose the source notes and visual context that were attached to those parts of the story.

The feature lets a reader select story areas from the current investigation, preview a bounded packet, and invoke the browser's native print flow to print it or save it as a PDF. The packet contains the published passage text from the selected areas, only the source notes those selected passages already cite, and optional text-only figure references built from the figure's existing caption and alt text. It does not create citations, infer bibliography, rate evidence, or create a separate Final Vestige edition.

## Interaction principle

Case Packet adapts several strong research and export principles without copying visual trade dress:

- Zotero Reports can generate an HTML report from selected research items and associated notes, then print or save that report.
- Notion lets people export/print a page for offline handoff, including browser-based Save as PDF.
- Modern browser print APIs and `@media print` styles allow a web product to create a purpose-built printable representation without a server-side document service.
- W3C's native modal-dialog guidance establishes contained focus, Escape dismissal, and logical focus return.

Final Vestige narrows those ideas to one investigation and its already-published provenance. Selection is by story area, and source inclusion is derived only from exact footnote relationships already present on the page.

## Visitor behavior

On a qualifying investigation, a prominent **Case Packet** band appears immediately before the first major story section. It offers **Build case packet**.

The native dialog provides:

- one checkbox per story area, including opening context only when it contains substantive narrative;
- exact per-area counts for passages, published figures, and distinct linked source notes;
- **Select all** and **Clear** controls;
- an optional **Include figure references** control that uses published captions/alt text only and never clones the image;
- **Preview packet**, which renders only the selected story areas;
- a linked-source section containing only source notes already cited from those selected passages;
- published external source URLs when a source note already contains one;
- a query-free, fragment-free source-page URL;
- **Print / Save PDF**, which invokes the browser's native print flow and print-isolates only the generated packet.

The packet states that it is built from the current published page and is a reading aid, not a separate edition, revision history, or evidence score.

## Hardened source-boundary contract

The feature fails closed unless all of the following are true:

1. Exactly one element inside the article matches either `#sources` or `.fv-source-heading`.
2. That sole candidate is an `H2` carrying **both** `id="sources"` and class `fv-source-heading`.
3. Exactly one `[data-fv-footnotes]` source-note list exists inside the article.
4. The source-note list follows the canonical heading.
5. The article has 2–8 pre-Sources story H2s and 10–140 substantive narrative paragraphs.
6. The source list contains 3–40 uniquely numbered `li#fv-fn-N` records.
7. There are 6–60 pre-Sources citations using the exact `sup.fv-fn-mark > a.fv-fn-ref[data-fv-fn]` structure.
8. Every participating citation has numeric `data-fv-fn`, exact `href="#fv-fn-N"`, and exactly one matching published source note.
9. At least three distinct published source notes are actually cited.
10. No more than 16 eligible pre-Sources `figure.wp-block-image` figures participate in packet metadata.

Rules 1–2 deliberately reject the mixed exact-plus-partial Sources-boundary defect previously identified by independent QD. An exact canonical Sources heading cannot coexist with an ID-only, class-only, duplicate, earlier, or later competing boundary candidate.

## Packet integrity

Narrative text is derived from the current page DOM at invocation. Existing inline citation markers are normalized to bracketed source numbers such as `[3]` in the packet so the relationship remains legible in plain printed text. Source notes are collected by those exact numbers in first-use order across the selected story areas.

Figure references are text-only. Case Packet does not clone `<img>` elements, request image assets, or imply that an image carries a particular evidentiary weight. A figure reference uses only the already-published caption and alt text.

The print representation uses a dedicated `.fvcp-print-root` and print-only CSS. When the visitor chooses **Print / Save PDF**, the rest of the webpage is excluded only for the duration of the native browser print flow. No server-side PDF generator or third-party export service is introduced.

## Accessibility and mobile

- Native modal `dialog`.
- Static dialog title receives initial focus for a large semantic workspace.
- Escape/Close behavior and logical focus restoration to the launcher.
- Standard checkboxes with visible labels and per-section context.
- `aria-live="polite"` selection count.
- 44px minimum interactive targets.
- Full-height mobile dialog at <=700px and dedicated 360px tuning.
- Forced-colors and reduced-motion handling.
- Purpose-built print stylesheet with paged-media margins, heading break protection, and widows/orphans controls.

## Privacy and performance boundary

Case Packet is current-DOM only. It introduces no `fetch`, XHR, WebSocket, `sendBeacon`, cookies, local/session storage, IndexedDB, analytics, third-party scripts/frames, clipboard writes, or browser-history mutation. The packet DOM is built lazily after visitor invocation. No images are cloned into the packet.

The only external URLs exposed are literal published `http://` or `https://` links already present in a selected source note; same-origin utility/backlink URLs are not promoted as external source links.

## Artifact identity

- Repository: `finalvestigestudios/final-vestige-site-layer`
- Target: `production`
- Base at build: `a2a499455d714c0238241fde9b76188efd1d7b1d`
- Branch: `feature/case-packet-v1`
- Payload: `payloads/case-packet-wp-block-v1.txt`
- Payload bytes: **19,974**
- Payload SHA-256: **`3eea754c68ea5b0d782829304e4d5fe54febd7fcfd66398af1b0484726e7cd7e`**
- Deterministic verifier: `tests/verify_case_packet.py`
- Dedicated workflow: `.github/workflows/case-packet-ci.yml`

The verifier locks payload identity, JavaScript syntax, one-block packaging, hardened mixed-boundary behavior, exact citation-to-note mapping, bounded qualification, section selection, provenance filtering, figure-reference rules, query-free source URL construction, print isolation, accessibility/mobile controls, absence of network/persistence APIs, and headless-browser valid/fail-closed fixtures.

## Live-source compatibility target

The published **Six Miles an Hour** investigation currently provides the expected model: one exact `h2#sources.fv-source-heading`, one later `[data-fv-footnotes]` list, three major pre-Sources story H2 sections plus substantive opening context, six published figures before Sources, ten in-story citation links across four actually cited source notes, and seven numbered source records. No editorial rewrite is required.

## Delivery boundary

This is an artifact candidate only. Do not merge or deploy merely because CI passes. Independent QD must review the exact frozen PR head SHA. Any code/workflow/payload change after freeze invalidates that review identity.

The governed Site Layer bootstrap remains controlling. Once that lane is active and this exact artifact is accepted, create the smallest executable integration from then-current `production`; the executable integration receives a new SHA and requires fresh CI + fresh independent QD before FVS Execution Dispatch may merge/deploy. Live deployment must then receive desktop/mobile/320–360px/200%-zoom, keyboard/focus, print-preview/PDF, source-integrity, console/network, and destination-readback verification before `IMPLEMENTED + VERIFIED`.
