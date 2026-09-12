# FVF-12 — Compare Lens R1

## Repair purpose

R1 is the bounded successor to the independent-QD REVISE on PR #10. It preserves the visitor job—compare two already-published figures side by side—while closing the two release blockers and applying the current nondestructive DOM-state rule.

## Trusted evidence boundary

R1 activates only when the article contains exactly one canonical `h2#sources.fv-source-heading`, no competing `#sources` or `.fv-source-heading` marker, and exactly one `[data-fv-footnotes]` root after that heading. Missing, partial, duplicate, competing, or reversed source boundaries fail closed. Only figures before the canonical boundary are eligible.

## Network contract

Compare Lens itself may assign an image URL only when the literal candidate resolves to the current origin over HTTP(S). Same-origin linked originals are preferred; `srcset`, `currentSrc`, and `src` candidates are separately origin-checked. A figure with no same-origin candidate is excluded. This prevents the feature from initiating a new cross-origin image request merely because published markup contains a remote candidate.

This does not claim the page itself made zero network requests while loading; it constrains network behavior introduced by Compare Lens.

## Nondestructive story return

`View in story` scrolls before mutating the publisher node. It adds temporary `tabindex="-1"` only when focusability is absent, never replaces a pre-owned value, adds the highlight token only when not already owned, restores feature-owned mutations on blur or focus failure, and recovers focus to the launcher when scroll/focus cannot complete. Repeated interactions are browser-regressed.

## Preserved interaction contract

- native dialog with explicit close and logical focus return
- two figure selectors, A/B swap, synchronized zoom/pan with opt-out
- 100–600% bounded zoom
- pointer and keyboard panning
- published caption/alt context
- 44px controls, mobile/360px, forced-colors, reduced-motion, print cleanup
- no browser persistence, analytics, fetch/XHR/WebSocket/sendBeacon, third-party scripts, account state, or history mutation

## Frozen source/build identity

- Base `production`: `3f7841a7c671f9e8e955b417480d853ad0a0a948`
- Payload: `payloads/compare-lens-wp-block-r1.txt`
- Payload bytes: **19,152**
- Payload SHA-256: **`5275862a6a81f5f9e3a093a7a71780e15fa6bbb5e2d6599615ed88867fb5c5e3`**
- Verifier: `tests/verify_compare_lens_r1.py`
- Workflow: `.github/workflows/compare-lens-r1-ci.yml`

The final PR head SHA and exact-head workflow conclusions are frozen only after GitHub CI completes.

## Governance

Source/build repair candidate only. Green CI is evidence, not QD approval. Do not merge or deploy this artifact. Fresh independent QD must review the exact final head, payload identity, browser verifier and workflow. Any code/test/workflow/contract/payload change after freeze creates a new review identity. If a later QD PASS requires executable integration, rebuild from then-current `production`, freeze a new executable SHA/package, run fresh CI, obtain fresh independent QD, and route only through the governed approval/dispatch path.
