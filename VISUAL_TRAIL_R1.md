# FVF-18 — Visual Trail R1

## QD repair

Visual Trail R1 preserves the v1 storytelling, accessibility, performance, privacy and evidence boundaries while hardening the trusted Sources boundary.

Activation now requires exactly one canonical `h2#sources.fv-source-heading` **and** exactly one total in-article element matching either `#sources` or `.fv-source-heading`; that sole candidate must be the canonical H2. This deliberately fails closed when a canonical Sources heading coexists with any ID-only, class-only, duplicate exact, earlier/later partial, or otherwise misleading candidate.

The unique `[data-fv-footnotes]` list must still follow the canonical heading. Only qualifying pre-Sources figures enter the sequence.

## Adversarial browser contract

The exact R1 payload is browser-executed against:

- one valid canonical boundary;
- ID-only boundary;
- class-only boundary;
- exact canonical + ID-only competitor;
- exact canonical + class-only competitor;
- earlier non-H2 `#sources` competitor;
- later non-H2 `.fv-source-heading` competitor;
- duplicate canonical boundaries;
- reversed source-list ordering;
- too few figures.

Only the valid canonical fixture may activate. The valid path also verifies bounded pre-Sources figure count, dialog opening, keyboard End navigation, and `View in story` focus return.

## Preserved boundaries

- no autoplay;
- published alt/caption context preserved;
- no local/session storage, IndexedDB, cookies or analytics;
- no fetch/XHR/WebSocket/sendBeacon or third-party scripts;
- no history or clipboard mutation;
- 44px controls, native dialog, reduced-motion/forced-colors/mobile/print handling preserved;
- visible disclosure continues to state that Visual Trail does not rate evidentiary weight.

## Artifact identity

- Repository: `finalvestigestudios/final-vestige-site-layer`
- PR: `#16`
- Target: `production`
- Branch: `feature/visual-trail-v1`
- Production baseline when repair began: `8afbdeeb34a775e7ea9b0d3220923354797844b7`
- R1 payload: `payloads/visual-trail-wp-block-r1.txt`
- R1 verifier: `tests/verify_visual_trail_r1.py`
- R1 workflow: `.github/workflows/visual-trail-r1-ci.yml`

Exact head SHA, payload bytes and SHA-256 are frozen only after the final identity-lock update and successful exact-head CI. CI evidence is not merge/deploy authority.

## Delivery boundary

R1 is an artifact candidate only. Do not merge or deploy it merely because CI passes. After independent QD accepts the exact frozen R1 identity, any executable integration must be derived from then-current `production`, receive a new executable SHA, fresh CI and fresh independent QD, then route through `FVS Execution Dispatch`. Live destination readback remains mandatory before `IMPLEMENTED + VERIFIED`.
