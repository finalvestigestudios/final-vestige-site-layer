# Media Recovery #183 — Hebgen 407:1 same historical photograph, separate rendition (November 3, 2026)

## Scope and source verification

This is a nonproduction, **single-image P0 restoration follow-up**. It supplements rather than replaces [the eight-slot primary-USGS audit](./MEDIA-HEBGEN-407-USGS-PRIMARY-PATH-20261103.md). Exact published frozen source: `407:1` from `qa/media-recovery/parts/02.json`, verified Git blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`; WordPress **was not reread** in this pass.

The published URL is:

`https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/img7535.jpg`

The [authoritative USGS catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) labels its **Original** link:

`https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/thumbnails/image/img7535.jpg`

**Critical nuance:** although the destination path contains `thumbnails/image/`, USGS itself labels that destination **Original**, not **Thumbnail**. Its separately labeled **Thumbnail** and **Medium** are distinct rendition URLs under `styles/thumbnail/public/...` and `styles/medium/public/...`. The website's full-width display URL uses `styles/full_width/public/...`. Never infer resolution quality from the word *thumbnails* in a URL path: use the USGS link label and actually decoded binary dimensions.

On November 3 the independent web image renderer visibly displayed the USGS Original, Thumbnail, Medium and full-width renditions. The text retriever rejected the **published** path with a wrapper `400 Unsupported content-type: binary/octet-stream`; that **does not prove** an origin 400 or a logged-out Chrome failure. All guest HTTP, currentSrc, decode and transfer measurements remain null.

## New independent secondary archive: SAME photograph but not identical asset

A second source, [Wikimedia Commons: Red Canyon fault scarp sjr00100.jpg](https://commons.wikimedia.org/wiki/File:Red_Canyon_fault_scarp_sjr00100.jpg), is visually identifiable as the **same August 1959 J. R. Stacy photograph**: the distinctive jeep on the upper-right fault-block road, person by the jeep and the curving scarp across the foreground match the official USGS image. However the image is a **different sized/framed rendition**, and no USGS-versus-Commons master binary hash match is established. Commons supplies source/photographer identity and lists an original **698×700 px, 461,875 bytes**. Its historical description identifies Red Canyon fault scarp east of Blarneystone Ranch, August 19, 1959. The Commons file is **not** automatically interchangeable with USGS's Original.

Proposed sizes:
- **Preferred authoritative USGS Original**: no width/height target until its native JPEG dimensions and exact crop are independently decoded. If native width >= 960, derive <=960px while preserving aspect ratio; otherwise retain native size, no upscaling.
- **Commons secondary fallback only**: maximum **698×700 px** and no upscaling; 960px output is specifically **forbidden**. The 461,875-byte figure is the Commons **source file metadata**, not actual browser network transfer or potential savings.

USGS labels the original **Public Domain** and credits **J. R. Stacy**; Commons independently labels its copy PD-USGS. The item-level rights/credit, resolution quality, crop, historical context and attribution still require review. These archival labels alone do not authorize FV's first-party caching or WordPress production uploads in this workstream.

## Decision and safe repair runbook

1. **Site QA #154 owns the visitor-browser evidence**. Compare the exact published path to the official `Original` path on post 407 (mobile and desktop). Capture final CDP image URL/status/MIME, naturalWidth/Height, decoded pixels, screenshots, and actual transferred bytes, including any Jetpack rewrite. A `binary/octet-stream` wrapper failure from a text retriever is not a visitor broken image.
2. If browser actually fails on the published URL, use **USGS Original** as the **first** candidate. Preserve the same 1959 photograph, complete existing ALT, 1959 chronology, and J. R. Stacy attribution. Use a Commons fallback only if USGS primary fails quality/access and its different crop is explicitly approved; do not use later 1997/2018 fault-scarp photographs as replacements.
3. Following per-image rights and editorial sign-off, stage **one** no-upscale, responsive <=960px first-party derivative, record asset SHA-256 plus reversible published-source mapping, and verify the original/candidate crop against the saved page screenshot. Staging plan only: **no asset downloaded/copied and no production WordPress write**.
4. Require guest desktop/mobile visual test, correct `srcset`, dimensions, ALT/credit, and measured paired cold image GET bytes **before** a release request. Do not rewrite Gutenberg post blocks automatically. Keep homepage/interim-design scope separate.

## Machine evidence and regression tests

- [Machine-readable catalog/transport/rights/geometry ledger](../qa/media-recovery/hebgen_407_secondary_same_photo_20261103.json).
- [Offline validator](../qa/media-recovery/validate_hebgen_407_secondary_20261103.cjs) pins the exact 407:1 published source and frozen census; rejects fabricated guest status, claimed byte transfer, mistaken Thumbnail-as-Original, incorrect Commons dimensions, binary identity assertions, license/production gate bypass, and image upscaling.
- [Positive + adversarial tests](../qa/media-recovery/test_hebgen_407_secondary_20261103.cjs): **28/28 PASS** against the **exact committed GitHub text** in an isolated V8 CommonJS compatibility runner. **Native Node/CI and real guest-browser execution not performed**.

**Established site-wide baseline** remains 61 articles / 355 image references / 288 external-origin source references / 13 WordPress originals over 1.5 MiB. **42 reported failures not verified** in visitor Chrome; **76% transfer reduction not measured**. **Production repairs: 0**. No scraping, image binaries, subscriptions, homepage changes, WordPress writes or duplicated QA scanner scripts.
