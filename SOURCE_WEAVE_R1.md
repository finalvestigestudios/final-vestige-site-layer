# FVF-17 — Source Weave R1

## Repair purpose

This successor closes the QD provenance-boundary defect in the original Source Weave artifact. The visitor-facing matrix may only initialize when the article contains exactly one canonical Final Vestige Sources heading matching both `h2#sources` and `.fv-source-heading`, plus exactly one `[data-fv-footnotes]` root ordered after that exact heading.

ID-only and class-only half-matches are not trusted boundaries. A misleading earlier half-match is ignored if one later exact canonical boundary exists. Multiple exact canonical candidates, multiple source roots, an absent exact canonical heading, or reversed heading/root order all fail closed before UI creation.

## Evidence behavior retained

Source Weave uses only already-published `.fv-fn-ref[data-fv-fn]` relationships and numbered source records under the bound source root. It does not infer semantic similarity, evidence strength, reliability, confidence, proof, or support for uncited text. Visitor copy states that matrix counts are counts of existing footnote links only.

Qualification remains bounded: 2–8 story H2 sections, 6–120 in-story citations, 4–40 numbered source records, at least 3 cited source notes, and at least 5 distinct source-to-story relationships.

## Accessibility and state safety

The desktop view is a semantic table with caption, row headers and column headers. Narrow screens receive an equivalent grouped list. Controls remain keyboard reachable with visible focus and 44px minimum targets; reduced-motion, forced-colors, small-screen and print behavior are defined.

Story/source jumps scroll before mutation. Temporary arrival class/tabindex state is feature-owned and restored exactly: pre-owned class/tabindex values survive, originally absent attributes return to absent, repeated jumps clean prior temporary state, and scroll/focus failure returns usable focus to the feature opener without leaving publisher DOM mutations behind.

## Privacy / performance boundary

The feature is current-DOM only. It performs no fetch/XHR/WebSocket/sendBeacon requests, loads no third-party scripts or frames, writes no local/session/indexed storage or cookies, emits no analytics, mutates no browser history, and does not use the clipboard.

## Frozen payload identity

- Payload: `payloads/source-weave-wp-block-r1.txt`
- Expected bytes: `17,101`
- Expected SHA-256: `6b4a5295eadbec5ec17cccc240bbc33c4bd182c8c0390d469554436b6bab8f27`
- Deterministic verifier: `tests/verify_source_weave_r1.py`
- Dedicated workflow: `.github/workflows/source-weave-r1-ci.yml`
- Base for this repair branch: `production` at `3f7841a7c671f9e8e955b417480d853ad0a0a948`

## Adversarial regression set

The headless-browser suite covers a valid canonical page, ID-only boundary, class-only boundary, misleading earlier half-match plus later canonical boundary, duplicate canonical boundaries, duplicate source roots, reversed boundary order, explicit relationship counts/filtering, citation jump, source jump, absent attribute restoration, publisher-owned nondefault class/tabindex preservation, and repeated interaction cleanup.

## Delivery boundary

Artifact/source-build review only. Do not merge or deploy from this package without fresh exact-head CI and independent QD PASS. Any source change after the frozen identity invalidates prior QD approval. Platform-required WordPress confirmation, destination readback and separate-gate controls remain controlling.
