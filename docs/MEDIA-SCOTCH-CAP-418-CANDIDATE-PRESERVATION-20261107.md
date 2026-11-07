# Scotch Cap / Hilo — six-image source recovery gate (2026-11-07)

**Scope:** WordPress post **418**, *The Lighthouse Was Gone at Dawn*, published and last CMS-modified **2026-08-28T03:11:08**. Read-only authenticated `posts.get(context=edit)` identified six inline `<img src>` references. Every exact published image source, ALT, caption and risk caveat is in [the machine-readable audit](../qa/media-recovery/scotch_cap_418_six_archive_cursors_20261107.json). No WordPress production writes, image bytes downloaded, media cached, new browser collector, homepage redesign or subscription spend.

## High-value priority evidence

**418:2 — USCG 1946 Scotch Cap destruction photograph.** The published USCG original `https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg` produced a retrieval-wrapper **403**; the local read-only HTTP HEAD failed DNS before reaching the origin. Neither result establishes a visitor failure. The [National Coast Guard Museum](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/) visibly serves a 600×463 photo preview at `https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg`. Its distinctive filename and described subject correspond to the article's original. **This is a recovery candidate and positive rendering observation, not a confirmed pixel-identical replacement or a right to republish the museum's image.** The museum labels the historical photograph U.S. Coast Guard.

**418:1 — official portrait, photo VIRIN preserved.** The existing `media.defense.gov` image URL includes `210330-G-DE713-0002.JPG`, identical to the official [USCG gallery entry](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/). That entry indicates public domain / cleared for release **subject to credit and DoD visual-information restrictions**. A retrieval-wrapper **403** is not a Chrome failure. A historical-accuracy problem needs human review: the photo gallery caption says **Anthony Pettit**, but the [Coast Guard lighthouse history](https://www.history.uscg.mil/Browse-by-Topic/Assets/Land/All/Article/1988680/scotch-cap-light/) and existing Final Vestige text say **Anthony Petit**. Do not change names or images without verification and editorial signoff.

**418:0 / 418:3 — two other USCG historical views.** The Museum visibly renders normalized-filename 600×480 (old/new light towers) and 600×474 (overhead aftermath) previews. These are **preview** pixels only; different crops/source masters are possible. No 960px copies may be derived from 600px thumbnails and no independent rehosting permission is inferred.

**418:4 — NOAA's 1946 Hilo inundation.** The published Hawaii Magazine image visibly rendered in an independent image retriever. [NOAA item `pl23_theb2705.jpg`](https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg) describes Hilo inundation and specifically the **man on the pier**. Its individual digital image and legal status still require review. A commercial image URL is not permission to mirror it. Match the composition with the NOAA item before choosing a first-party replacement.

**418:5 — USGS Hilo disaster street photograph.** The exact published USGS S3 image visibly rendered in the independent image retriever; the [USGS primary catalog](https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946) matches the buried vehicle and identifies it as **Public Domain**, but says the original photo **source is unknown**. Preserve that uncertainty in attribution.

## Implementation gates — none passed for publication

1. **Do not duplicate browser work.** Site QA draft [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) and its existing browser evidence gate [#1395](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1395) own logged-out Chrome/CDP capture. Leave six-source P0 order **285:5, 285:2, 287:5, 418:1, 418:2, 407:1** intact. Request actual `currentSrc`, post-scroll `naturalWidth/naturalHeight`, HTTP/MIME, redirects, encoded data length, cache flags, and 360px/1440px screenshots for Scotch Cap. A 403 or 404 from a *retriever wrapper* is not the visitor response.
2. **Rights and identity.** Verify native original pixels, exact photograph/crop, credible author or institution, individual reuse conditions and credit requirements. Museum-supplied 600px previews establish a candidate but not republication rights. No download/cache or first-party upload until rights and exact image identity are documented.
3. **Sizing.** For rights-cleared, verified original `W×H`, conditional safe staging rule is `newWidth = min(960,W)` and `newHeight = round(H * newWidth / W)`. Do **not** infer original size from URL `1200x984` or from previews; preserve composition and ALT/caption. No output dimensions have been approved for the six *published original* files.
4. **Safe isolated WordPress staging, after an additional explicit approval:** produce one approved optimization, record binary SHA256, image quality / alpha check and required credit, add to staging WP Media, change only the affected image block using an expected block hash, compare before/after desktop/mobile and link click, and retain original block content for rollback. This draft makes **zero** production changes.
5. **Wire metrics, not storage:** preserve the frozen 61-post / 355-source reference cohort, media census **288** external versus Site QA **286** (classifier difference) and later 66/361 as a distinct population. The reported **42 broken** lacks guest-browser proof. Thirteen >1.5MiB originals represent **43,522,829 stored bytes**, not downloads. The purported **76% transferred-image-weight savings remains unmeasured**. Reuse existing cold-browser image-wire comparator; enforce equal viewport/cache/full scroll and no visual crop drift.

## Exact committed-source QA

```sh
node --check qa/media-recovery/validate_scotch_cap_418_20261107.cjs
node qa/media-recovery/validate_scotch_cap_418_20261107.cjs
node --test qa/media-recovery/test_scotch_cap_418_20261107.cjs
```

The validator fails closed on invented Chrome status/decode, false transfers, premature copyright clearance, invented dimensions, unsafe upscaling, missing image captions and historical spelling/photographer uncertainties. **Native Node CI against the GitHub checkout and real guest browser results are pending.** The work is an evidence-backed preservation plan, not a live image repair.
