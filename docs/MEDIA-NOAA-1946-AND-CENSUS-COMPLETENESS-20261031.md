# NOAA catalog recovery — Hilo tsunami image 418:4 (2026-10-31)

**Status: DOCUMENTARY CANDIDATE ONLY. No browser failure, rights clearance, binary equivalence, media download, WordPress upload or published-article rewrite has been established or authorized.**

This closes the *source catalog candidate* gap for the last unmatched original external image in the six-article P0 queue. There are now **36/36 offsite P0 slots with catalog/publisher candidate leads** and **0 additional rights-cleared or visitor-verified replacements** from this finding. A linked archival record is not proof of an identical photograph or its licensing.

## Exact site source and documentary trail

- **Stored key 418:4**, article `The Lighthouse Was Gone at Dawn`:
  `https://www.hawaiimagazine.com/wp-content/uploads/2020/12/Tsunami1946NOAA2.jpg`.
  Stored alt: “Tsunami water inundating the Hilo waterfront in April 1946, with a person visible near the advancing water.”
- **NOAA Historic Coast & Geodetic Survey** image ID **theb2705**, catalog title **pl23_theb2705.jpg**: [NOAA catalog record](https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg). NOAA's indexed record describes the 1946 Hilo tsunami with **a man on the pier**, NOAA credit and April 1946 date. The catalog mentions a **265 KB downloadable item**, which is **not** a measured FinalVestige visitor transfer size.
- **Primary documentary visual:** [2013 Hawaii Boater's Hurricane and Tsunami Safety Manual, printed p. 33 / PDF p. 37](https://repository.library.noaa.gov/view/noaa/41185/noaa_41185_DS3.pdf#page=37) reproduces a photograph of the tsunami over **Pier No. 1, Hilo Harbor**, an arrow pointing to a man, and credits **NOAA/NGDC and Pacific Tsunami Museum**. The PDF image was visually inspected on page index 36, not inferred from text alone.
- **Publisher cross-check:** [HAWAI‘I Magazine's historical article](https://www.hawaiimagazine.com/three-tsunamis-that-changed-hilo-and-hawaiis-big-island/), published November 25, 2009, explicitly credits its Pier 1 photograph to NOAA and describes the arrow/person. This is a **high-confidence historical scene/catalog candidate**; the current WordPress binary and NOAA catalog master were **not** downloaded/hashed/compared.

## Copyright and visual-integrity hold

NOAA's [image usage guidance](https://www.omao.noaa.gov/image-licensing-usage-info) says NOAA-created materials generally are not copyrighted, **but** materials credited to others and identifiable-person/endorsement uses require their own review. The manual adds the **Pacific Tsunami Museum** to the credit chain. A [Getty/Corbis editorial listing](https://www.gettyimages.com.br/detail/foto-jornal%C3%ADstica/view-from-the-ss-brigham-victory-of-a-tsunami-foto-jornal%C3%ADstica/615289258) markets a photograph with the same Pier No. 1/arrow description with **© Corbis** labeling. This is not a determination of ownership of NOAA's original photograph; it is an item-level licensing conflict to resolve **before** any copy or derivative. Never infer a public-domain grant from the presence of NOAA branding alone.

**Localization plan, only after source and rights verification:** Obtain an authorized archival master, record its SHA-256 and actual intrinsic dimensions; choose `min(960, original width)`, compute height preserving aspect ratio, no upscaling/no cropping; retain source credits and historical chronology; create a reviewed, responsive first-party WordPress Media Library derivative with caching, preserve original captions and compare logged-out mobile/desktop rendered `currentSrc`, HTTP response/MIME, natural width, screenshots, LCP/CLS and encoded transfer bytes. **All release and production-write gates remain CLOSED.**

## Separate browser census completeness fix

The earlier runner could publish a **numeric zero broken images** after reaching the bottom of a post even when its stored images were unmatched, alt-only, pending lazy decode or otherwise lacked trustworthy `currentSrc`/network proof. This is a **reproduced logical audit defect, not evidence of live image breakage**.

`qa/media-recovery/image_census_coverage_core.cjs` now requires each stored slot to be conclusively classified as loaded or broken and rejects duplicate/missing slots, incomplete scroll scans, unverified pages and contradictory statuses. The browser runner emits per-page `image_census`, partial `known_broken_count` and top-level `image_census_coverage`; it returns **null** for `confirmed_broken_count` and nonzero exit status unless **every** requested page and slot is fully evidenced. Partial known failures remain visible without being promoted to a full 42-image census.

**Test evidence:** 18/18 local native Node tests for the coverage module passed, and the exact committed module/test pair passed 18/18 in isolated V8. NOAA rights/provenance ledger passed 16/16 exact committed-source V8 regression checks. The full Chromium runner was syntax-parsed after integration; native CI and live browser HTTP/waterfall evidence remain outstanding. No subscriptions, downloads, WordPress writes, third-party copying or homepage design changes occurred.

**Scope baseline unchanged:** 61 articles, 355 source image references, 288 offsite newer inventory (Site QA #154's 286 delta is described in the worklist), 13 originals above 1.5 MiB, and founder-reported 42 broken/76% saving both unverified. The NOAA catalog 265 KB figure is **not** a visitor-side media-weight measurement.
