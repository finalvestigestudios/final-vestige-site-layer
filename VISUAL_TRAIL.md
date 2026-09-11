# FVF-18 — Visual Trail

## Purpose

Visual Trail turns the figures already published inside a qualifying Final Vestige investigation into an optional, sequential visual reading experience. It is a storytelling utility, not a gallery template or evidence-scoring system.

**Visitor job:** follow the investigation through its published photographs, maps, diagrams, and explanatory graphics without repeatedly scrolling through a long article or losing the connection between each figure and its surrounding story section.

## Interaction principle

The feature adapts three established interaction principles without copying trade dress:

1. **ArcGIS StoryMaps slideshow / immersive blocks** — media can become a deliberate sequence with minimal narrative context and manual previous/next navigation.
2. **Image-led cultural storytelling** as demonstrated by Google Arts & Culture — published visual objects can carry narrative sequence and contextual meaning when shown with their existing description.
3. **W3C carousel guidance** — the sequence is entirely user-controlled, keyboard operable, semantically named, and never auto-advances.

Final Vestige's adaptation stays inside the current investigation and its already-published media. There is no separate media CMS, recommendation system, autoplay, account state, or inferred evidentiary relationship.

## Qualification contract

Visual Trail fails closed unless all of these are true:

- exactly one canonical trusted Sources heading exists inside an `article` and matches **both** `h2#sources` and `.fv-source-heading`;
- exactly one `[data-fv-footnotes]` source list exists in that article and follows the canonical Sources heading;
- 2–10 story H2 sections occur before Sources;
- 3–12 eligible `figure.wp-block-image` figures occur before Sources;
- every eligible figure has an image with a published HTTP(S) `src` plus published alt text and/or a figcaption.

Partial or ambiguous source-boundary matches do not qualify. Figures after Sources never enter the sequence.

## Visitor experience

A prominent in-flow launcher appears before the first story H2:

- `Visual trail`
- exact figure count
- `Follow the visual trail`

The modal visual sequence provides:

- one published figure at a time;
- original published alt text on the displayed image;
- original published caption (or alt text when no caption exists);
- nearest preceding story-section heading, or `Opening`;
- explicit `Figure N of M` position;
- Previous / Next controls;
- a numbered direct-access rail;
- Arrow Left / Arrow Right / Home / End keyboard navigation;
- `View in story`, which closes the trail, scrolls to the original published figure and places logical focus there;
- native dialog Close/Escape behavior and logical focus return to the launcher.

No automatic rotation is permitted.

## Accessibility

- Native `<dialog>` modal.
- `aria-labelledby` and `aria-describedby`.
- Carousel and live-position semantics.
- Semantic buttons with minimum 44px target height.
- Original image alt text is preserved.
- Explicit focus-visible treatment.
- Full keyboard transport.
- Forced-colors treatment.
- Reduced-motion-aware story return.
- Full-height mobile layout at <=720px and compact tuning at <=360px.
- Feature is hidden in print because the original published figures remain in the article.

## Evidence / editorial boundary

Visible copy states:

> A sequence of the images and diagrams already published in this investigation. It does not rate their evidentiary weight.

Visual Trail does not:

- classify an image as evidence;
- infer that a figure proves surrounding prose;
- change captions, alt text, source notes or article wording;
- introduce a new image origin or external media service;
- create annotations or derived image edits.

The stage reuses only image URLs already present in the page DOM.

## Privacy / network boundary

No:

- localStorage or sessionStorage;
- IndexedDB;
- cookies;
- analytics emission;
- fetch/XHR/WebSocket/sendBeacon;
- history mutation;
- clipboard;
- iframe;
- third-party script.

Normal browser image loading may occur when the visitor explicitly opens/navigates the trail, using the exact image URL already published on the current page.

## Performance budget

Before visitor invocation the feature creates only the compact launcher. The dialog and stage DOM are created lazily on first open. It does not preload a second image set, fetch metadata, or install an external library. No auto-rotation or animation loop exists.

## Exact artifact identity

- Base: `production` at `a2a499455d714c0238241fde9b76188efd1d7b1d`
- Payload: `payloads/visual-trail-wp-block-v1.txt`
- Payload bytes: `12,448`
- Payload SHA-256: `0258e7c18bdcdeb53273801f69cb1fdd3b420e73013917d624b15f2e44155bdc`
- Verifier: `tests/verify_visual_trail.py`
- Workflow: `.github/workflows/visual-trail-ci.yml`

The verifier locks exact bytes/hash, JavaScript syntax, canonical-boundary gating, bounded figure qualification, media-context reuse, manual/keyboard navigation, story return/focus, accessibility media rules, prohibited persistence/API tokens, and headless-browser valid/adversarial fixtures. CI also prints the exact payload byte count and SHA-256 before verification so the frozen identity is visible in the run evidence.

## Delivery boundary

This is an **artifact-review PR only**. Do not merge or deploy it merely because CI passes.

The governed Site Layer bootstrap remains the controlling prerequisite. After that lane is active and independent QD accepts the frozen artifact, create the smallest executable integration from then-current `production`. That integration receives a new SHA and requires fresh CI + independent QD before `FVS Execution Dispatch` may merge/deploy. Live destination readback at desktop/mobile/accessibility widths remains mandatory before `IMPLEMENTED + VERIFIED`.

No direct WordPress footer/template injection, whole-site launch/indexing change, public Scout release, billing/account/permission change, private-user processing, or destructive/high-consequence action is authorized by this feature package.
