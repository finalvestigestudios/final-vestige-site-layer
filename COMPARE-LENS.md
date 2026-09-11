# FVF-12 — Compare Lens

Compare Lens is a bounded, opt-in side-by-side image inspection feature for evidence-rich Final Vestige investigations.

## Visitor job

Let a reader compare two figures already published in the same investigation without opening multiple tabs, losing narrative context, or treating image comparison as a claim about evidentiary equivalence.

## Interaction principle

The feature adapts the research value of multi-window cultural-heritage viewers such as IIIF/Mirador: bring two source images into one workspace, preserve their identity, and give the reader direct zoom/pan control. Final Vestige deliberately implements a smaller same-article tool rather than importing a viewer framework or requiring IIIF manifests.

## Qualification and placement

The payload runs only on single-post pages that contain at least two eligible published image figures before the article's Sources & Further Reading boundary. Feature-owned UI is excluded from qualification. When the contract is not satisfied, the payload is inert.

A compact Compare Lens launcher is inserted before the first story H2 (or first eligible figure when no H2 exists). Original article figures and links remain untouched.

## Inspection behavior

- Choose any two eligible published figures as A and B.
- Resolve the best already-published image candidate lazily when the dialog opens, preferring a same-origin original image link, then the largest `srcset` candidate, then the rendered image source.
- Zoom from 100% to 600% in bounded increments.
- Pan by pointer drag or keyboard arrow keys.
- Synchronize zoom and normalized pan between A and B by default, with an explicit opt-out.
- Swap A/B in one action.
- Reset either view independently.
- Display each figure's existing published caption (or alt text fallback).
- `View in story` closes the comparison and returns the reader to the original figure with logical focus placement.

Compare Lens does not edit pixels, create annotations, infer relationships between figures, score evidence, or imply that two figures are equivalent evidence.

## Accessibility and responsive contract

- Native `<dialog>` modal capability gate.
- Visible keyboard focus states and 44px minimum button targets.
- Polite status announcements for selection, zoom, synchronization, and swaps.
- Keyboard pan plus zoom/reset controls.
- Escape/native close behavior and logical focus return.
- At widths below 760px, A and B stack vertically with bounded viewport heights; at 360px controls remain usable without horizontal overflow.
- Forced-colors, reduced-motion, and print behavior are explicit.

## Performance and privacy boundary

The payload is dependency-free. It does not use browser persistence, cookies, analytics, `fetch`, XHR, WebSockets, `sendBeacon`, or third-party scripts. Larger image candidates are assigned only after the visitor opens Compare Lens. No original figure markup is cloned into the article or mutated at rest.

## Artifact identity

- Payload: `payloads/compare-lens-wp-block-v1.txt`
- Bytes: `17,616`
- SHA-256: `b78476ffd1732c78f35e33a3ca7af7433bcc3abe087e37ac0581ab997a1e53ef`

`tests/verify_compare_lens.py` locks the byte/hash identity and verifies qualification, progressive behavior, interaction controls, accessibility hooks, banned persistence/network dependencies, and JavaScript syntax. `.github/workflows/compare-lens-ci.yml` runs that verifier for the feature surface.

## Delivery boundary

This artifact branch is based on the current inert `production` baseline. It does not alter the Site Layer bootstrap/deployment runtime or any other open feature PR.

Passing feature CI is evidence, not merge authority. Runtime-manifest integration must wait for the governed Site Layer bootstrap/deployment lane. Any later executable integration creates a new SHA and therefore requires fresh CI and independent QD review before deployment and live destination verification.
