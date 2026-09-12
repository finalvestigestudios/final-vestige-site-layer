# FVF-18 Visual Trail R2 — published-alt fidelity + nondestructive story-focus repair

## Scope
Bounded repair successor to independently reviewed Visual Trail R1. This artifact is source/build only and is not merge or deployment authority.

## Visitor contract preserved
Visual Trail activates only on qualifying Final Vestige investigations with:
- exactly one canonical `h2#sources.fv-source-heading`;
- no competing in-article `#sources` or `.fv-source-heading` marker;
- exactly one `[data-fv-footnotes]` root after that canonical boundary;
- 2–10 pre-Sources story H2 sections;
- 3–12 qualifying pre-Sources figures.

It remains manual, non-autoplay, source-bound and explicitly does not rate evidentiary weight.

## R2 accessibility fidelity repair
For each qualified source image:
- the source image's `alt` attribute presence and exact string value are captured without trimming or fallback rewriting;
- the modal image reproduces that attribute exactly, including intentional `alt=""`;
- caption-only figures with empty alt keep the image decorative while the published caption remains visible and available to assistive technology;
- alt-only figures keep the exact alt on the image and show the same text visually as contextual fallback, but that duplicate visible fallback is `aria-hidden="true"` to avoid duplicate assistive-tech announcement;
- alt+caption figures keep the exact image alt and expose the published caption normally.

No new description is invented.

## Nondestructive DOM state
`View in story` now treats existing article nodes as publisher-owned:
- `scrollIntoView` occurs before temporary focus mutations;
- a missing `tabindex` may receive temporary `-1`, then is removed on cleanup;
- a pre-existing/nondefault `tabindex` is preserved exactly;
- a pre-existing `fvvt-story-focus` class is never removed by the feature;
- feature-added focus class state is removed on cleanup;
- failure during focus restores any feature-owned mutation before rethrowing;
- repeated jumps may not drift owned state.

## Automated proof
`tests/verify_visual_trail_r2.py` browser-executes the exact payload and asserts:
- caption-only `alt=""` fidelity;
- alt-only visible fallback with duplicate AT suppression;
- alt+caption exact alt whitespace/value fidelity;
- absent `tabindex` restoration;
- pre-owned `tabindex="-7"` preservation;
- pre-owned focus-class preservation;
- repeated story jumps without state drift;
- every R1 canonical/partial/duplicate/reversed Sources-boundary regression;
- bounded pre-Sources figure qualification;
- no local/session storage, IndexedDB, cookies, analytics, history/clipboard mutation, iframe, external script, fetch/XHR/sendBeacon/WebSocket token.

## Frozen payload identity
- Path: `payloads/visual-trail-wp-block-r2.txt`
- Bytes: `13261`
- SHA-256: `20000f451ca59962b77bb24db7ffaae84b5de4693dddf32751e47b98b83d9992`

Any payload change invalidates this identity and requires a fresh verifier lock, CI run and QD review.

## Governance
Do not merge or deploy merely because CI passes. Return the exact frozen PR head, payload identity and both feature + repository CI evidence to independent QD. No whole-site launch/indexing, private-user processing, spending, account/permission change, Scout release or other separately gated action is authorized.
