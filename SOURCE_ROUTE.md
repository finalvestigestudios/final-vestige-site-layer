# FVF-20 — Source Route

## Purpose

Source Route is a visitor-initiated, citation-by-citation reading path for evidence-rich Final Vestige investigations. It solves a specific longform problem: a reader can inspect a source note, but repeated footnote jumping makes it easy to lose the passage, section, and sequence that used that source.

The feature creates a bounded linear route through the citations already published on the page. It does not create citations, infer evidence, rate reliability, or claim that a linked source proves nearby prose.

## Interaction principle

Source Route adapts several strong research/accessibility principles without copying visual trade dress:

- Wikimedia Reference Previews keeps reference content close to the citation that invoked it.
- Hypothesis connects anchored text to a sidebar record and provides keyboard operations that move focus between document context and the anchored record.
- DocumentCloud treats annotations/notes as navigable context attached to primary-source material.
- W3C's modal-dialog pattern requires contained keyboard focus, Escape dismissal, and logical focus return.

Final Vestige turns those principles into a read-only citation route: passage context and the exact linked source note stay together while Previous/Next transport walks the published citation sequence.

## Visitor behavior

On a qualifying investigation, a prominent **Source Route** band appears immediately before the first major story section. It reports the number of published citations and distinct cited source notes and offers **Follow source route**.

The native dialog provides:

- **All citations** — every published citation in article order.
- **First use per source** — only the first story occurrence of each cited source note.
- Citation position, source number, and repeated-use position, e.g. `Citation 4 of 10 · Source 1 · use 3 of 4`.
- Nearest major story-section heading.
- Published passage context with footnote markers removed from the reading copy.
- Published linked source-note text with backlink UI removed.
- Previous / Next controls plus Left / Right / Home / End keyboard transport.
- **View passage** and **View source note**, both returning focus to the original published DOM object rather than a clone.

The tool does not expose uncited source records as if they were cited and does not characterize uncited prose.

## Hardened source-boundary contract

The feature fails closed unless all of the following are true:

1. Exactly one element inside the article matches either `#sources` or `.fv-source-heading`.
2. That sole candidate is an `H2` carrying **both** `id="sources"` and class `fv-source-heading`.
3. Exactly one `[data-fv-footnotes]` list exists inside the article.
4. The source-note list follows the canonical heading.
5. The article has 2–10 pre-Sources story H2s and 10–140 substantive narrative paragraphs.
6. The source list contains 3–40 uniquely numbered `li#fv-fn-N` records.
7. There are 6–60 pre-Sources citation anchors with the exact `sup.fv-fn-mark > a.fv-fn-ref[data-fv-fn]` structure.
8. Every participating citation has numeric `data-fv-fn`, exact `href="#fv-fn-N"`, and exactly one matching published source note.
9. At least three distinct published source notes are actually cited.

The first two rules intentionally reject the mixed exact-plus-partial boundary condition identified by independent QD on FVF-18 and FVF-19. An exact canonical Sources heading may not coexist with an ID-only, class-only, duplicate, or otherwise competing Sources candidate.

## Accessibility and mobile

- Native modal `dialog`.
- Visible dialog title receives initial focus because the dialog contains multiple semantic text regions.
- Close control and logical focus restoration to the launcher.
- `aria-live="polite"` route-position updates.
- 44px minimum interactive targets.
- Explicit pressed state for route-mode controls.
- Keyboard transport: Left, Right, Home, End.
- Original citation/source objects receive visible temporary focus treatment after a jump.
- At <=680px the dialog becomes a full-height mobile surface.
- Dedicated 360px tuning.
- Reduced-motion, forced-colors, and print handling.

## Privacy, evidence, and performance boundary

Source Route is current-DOM only. It introduces no `fetch`, XHR, WebSocket, `sendBeacon`, cookies, local/session storage, IndexedDB, analytics, third-party scripts/frames, clipboard writes, or browser-history mutation. Dialog construction is lazy and occurs only after visitor invocation.

The tool exposes structural facts only: citation order, source number, source reuse count, nearest story section, published passage wording, and published source-note wording. Repetition is not treated as source quality or evidentiary weight.

## Artifact identity

- Repository: `finalvestigestudios/final-vestige-site-layer`
- Target: `production`
- Base at build: `a2a499455d714c0238241fde9b76188efd1d7b1d`
- Branch: `feature/source-route-v1`
- Payload: `payloads/source-route-wp-block-v1.txt`
- Payload bytes: **13,722**
- Payload SHA-256: **`56071cf735140176a3782f24d03a3bc8a8cbba738c2e75cf50410481b2e6177b`**
- Deterministic verifier: `tests/verify_source_route.py`
- Dedicated workflow: `.github/workflows/source-route-ci.yml`

The verifier locks payload identity, JavaScript syntax, one-block packaging, the hardened mixed-boundary contract, exact citation-to-note mapping, bounded qualification, route modes, original-DOM focus return, accessibility/mobile controls, absence of network/persistence APIs, and headless-browser success/fail-closed fixtures.

## Live-source compatibility target

The published **Six Miles an Hour** investigation currently provides the expected model: one exact `h2#sources.fv-source-heading`, one subsequent `[data-fv-footnotes]` list, three major pre-Sources story sections, ten in-story citation links across four actually cited source notes, and seven numbered source records. No editorial rewrite is required.

## Delivery boundary

This is an artifact candidate only. Do not merge or deploy merely because CI passes. Independent QD must review the exact frozen PR head SHA. Any code/workflow/payload change after freeze invalidates that review identity.

The existing governed Site Layer bootstrap remains controlling. Once that lane is active and this exact artifact is accepted, create the smallest executable integration from then-current `production`; the executable integration receives a new SHA and requires fresh CI + fresh independent QD before FVS Execution Dispatch may merge/deploy. Live deployment must then receive desktop/mobile/320–360px/200%-zoom, keyboard/focus, source-integrity, console/network, and destination-readback verification before `IMPLEMENTED + VERIFIED`.
