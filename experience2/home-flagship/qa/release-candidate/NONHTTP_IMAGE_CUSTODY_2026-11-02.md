# Homepage image provenance — non-HTTP payload gap (2026-11-02)

**Scope:** Current seven-chapter, rights-safe isolated WordPress/Assembler candidate only. Source base: PR #652 exact `92fdb338ddf6333e95579a110bc5d00ff2e8ea50`. No WordPress.com or frozen PR #49 writes. Release remains **HOLD**.

## Specific finding and correction

The existing media-response gate `media_transfer_admission.py` fails closed on unexpected image HTTP responses, including renamed copies, Jetpack CDN derivatives, CSS URL requests and image MIME returned by `fetch()`. But a browser can render inline `data:image/*`, SVG markup, `blob:` image URLs or a scripted canvas **without making an image HTTP request**. Its 358/358 prior checks alone did not warrant a blanket claim that *no additional unreviewed imagery can ever appear*.

The current first screen intentionally uses **two small, original inline noise SVG textures** in `flagship.css`, based on `feTurbulence`; these are decorative grains, **not reproductions of source archival images**. The new exact-source gate byte-pins these two URL strings at exactly one occurrence each. It rejects additional data/Blob image transports, inline SVG/canvas/object/picture markup, programmatic image/blob/canvas construction, CSS asset `url()` and `image-set()` calls outside those two pins. If someone replaces either texture or inserts a source image as a data URI, source CI must fail for independent review.

The tests exercise the unchanged canonical source plus **12 hostile cases**: inline raster/SVG, canvas, blob, CSS data/external/image-set, JS Image, Blob and canvas/SVG constructors, and changing a pinned original grain. The staging workflow runs these tests and the exact-SHA source gate before expensive WordPress rendering. The browser network-response gate, five-width Chromium checks, axe, no-JS and Lighthouse remain mandatory.

## Asset/provenance review (unchanged)

- Apollo 1: originally selected first-party `s67-19766.webp`; retained only with the existing NASA attribution and historical rights assessment. No edits to this media or source.
- Franklin: first-party / Jetpack derivative of `Franklinexpeditionnote.jpg`; retained with the existing individual scan/source/credit notice. The first-screen folio is expressly editorial typesetting, not a facsimile.
- NYPL map digital capture 5003296: **not rendered** in the PR #650 rights-safe candidate. An original source-chronology plate and NYPL catalog link remain; no copyright clearance is asserted.
- The two encoded CSS textures are original procedural SVG grain, pinned to their exact existing strings; **no additional image, subscription, trademark, purchase or third-party media** is introduced.

## Exact rerun, limits, release custody

From the **exact PR head** on clean checkout:

```sh
node --test experience2/home-flagship/qa/release-candidate/source_gate.test.mjs
node experience2/home-flagship/qa/release-candidate/source_gate.mjs --root experience2/home-flagship --expected-head "$(git rev-parse HEAD)"
```

Then require the existing actual ephemeral WordPress/Assembler five-width Chromium/axe/media/Lighthouse workflow. The source regex barrier covers explicit source expressions, **not arbitrary obfuscated runtime image synthesis or host-injected content**; browser network, DOM, editorial and human rights checks remain distinct. No source-only gate is complete WCAG 2.2 AA or provenance sign-off.

**Outstanding:** manual screen reader, true browser UI zoom / text-only zoom, real iOS/Android interaction, WordPress.com Personal host parity, independent exact-head QD, final rights review and founder release consent. No merging, uploading, publishing, production CMS modifications or subscriber database import/sync are authorized by this work.
