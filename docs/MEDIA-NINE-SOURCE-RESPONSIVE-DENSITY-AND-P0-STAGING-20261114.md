# FV Media Recovery: nine-source density/release preflight (14 Nov 2026)

**Draft-only engineering; no production, browser collector or image writes.** Source audit: [nine-source matrix](../qa/media-recovery/image_density_preflight_nine_20261114.json), [offline guard](../qa/media-recovery/image_density_release_gate_20261114.cjs), [42 native Node test cases](../qa/media-recovery/test_image_density_release_gate_20261114.cjs). This is a *new downstream responsive-density and release safeguard*, not a replacement for Site QA #154's existing cold-browser collector or the larger wire-byte comparator in draft #183.

## Why this batch matters

A 960px derivative is **not automatically fit for a 1024px-wide image slot**. At DPR 2 it covers at most **480 actual CSS pixels** without undersampling. At CSS width 500px/DPR2, the browser needs at least 1000 intrinsic horizontal pixels. This guard now rejects that specific false-positive while separately enforcing exact known source URLs, item identity, no upscale, intact aspect, rights HOLD, and provenance. It never claims that a candidate actually exists on WordPress or that the 76% network reduction is real.

## Audited sources and conditional dispositions

| Original slot | Candidate pixels | Max CSS width at DPR2 | Rights/scene release blocker |
|---|---:|---:|---|
| 34:0–38:0 (five 1672×941 AI-assisted reconstruction PNGs; media 39–43) | 960×540 each | 480px | Original 1024×576 HTML attributes are NOT real CSS width; preserve AI reconstruction labels, visual fidelity; rights review |
| 621:0 (Malbone tunnel image, media 1257) | 960×720 | 480px | GeneralPunger/Commons CC BY-SA 4.0 catalog and derivative attribution unresolved |
| 621:1 (1903 NYPL BRT map, media 1258) | 960×649 | 480px | Exact binary identity, item-level usage and high-density map-label readability / zoom HOLD |
| 285:5 (Three Mile Island, exact Commons catalog) | 819×614 | 409.5px | PD-self catalog; original publisher uses 16:9 crop vs full-frame ~4:3; **not an equivalent drop-in** |
| 418:2 (Scotch Cap museum rendition) | 600×463 | 300px | Museum 600px file is not proven identical to original Coast Guard master or cleared for mirroring |

TMI catalog: https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg (photograph dated June 2010, original 819×614, uploader PD dedication). Hebgen #407:1 has an official USGS public-domain catalog: https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959 — **not included** in geometry cohort because native/currently decoded dimensions are unverified. Likewise, Navy, Coast Guard and Florida Memory catalogs in existing worklist are archival leads, **not blanket republication permission**. Florida Memory scene alternatives for Skyway 287:5 depict different moments and cannot be swapped silently. All items are still HOLD.

## Read-only QA contract

```bash
node --check qa/media-recovery/image_density_release_gate_20261114.cjs
node --test qa/media-recovery/test_image_density_release_gate_20261114.cjs
node qa/media-recovery/image_density_release_gate_20261114.cjs qa/media-recovery/image_density_preflight_nine_20261114.json
# Optional: pass a separate sanitized guest-observations JSON as second argument
```

Observation object keys are exact frozen image slots. Example, for a **synthetic** candidate only:

```json
{"34:0":{"css_width_px":500,"css_height_px":281,"dpr":2,"cold_browser_verified":true,"candidate_http_status":200,"candidate_decoded":true,"candidate_current_src":"https://finalvestige.com/wp-content/example.webp","candidate_natural_width_px":960,"candidate_natural_height_px":540,"asset_identity_verified":true}}
```

The guard returns `INSUFFICIENT` due to 500×2 >960, even if bytes drop by 76% in an independent synthetic fixture. It returns `NOT_MEASURED` without guest evidence. Even a measured `DENSITY_SCREEN_PASS` **never** grants asset caching, rights, scene parity, WordPress edits, deployment, or a site-wide performance claim. It cannot itself verify that CDP evidence is genuine; Site QA must establish actual cold-browser response and identity before supplying observations.

Source matrix is grounded in previously authenticated read-only WordPress image and media inspection at commit `99efdd9fab845d6812c62eb14b31683d1edd0d1d`. **Stored original bytes are not actual network transfers.** Historical frozen 61 posts/355 inline images, later expanded 66/361, 42 alleged browser failures unconfirmed, 76% network savings unmeasured, and latest 16 >1,500,000-byte stored originals totaling 49,107,665 bytes remain distinct.

## Staging/WordPress plan (authorization not granted)

1. **P0 first:** Site QA #154 runs its existing cold guest queue (285:5, 285:2, 287:5, 418:1, 418:2, 407:1) recording actual final request URL/status, decoded intrinsic dimensions, cache provenance, `currentSrc`, CSS width/height, DPR and transfer bytes. Our tool does not run that collector.
2. For a genuinely missing image, identify the **exact historical scene/crop** and authoritative primary catalog (NHHC/Navy, USCG, USGS, Florida Memory/archives), verify item-level rights/attribution and any transformation conditions. Do not download, mirror, or publish unclear media.
3. In an expressly authorized **reversible staging environment only**, make an approved first-party WordPress Media asset with originals preserved; generate appropriate `srcset` widths only up to rights/quality limits, never upscale. For mobile DPR2, a 960px resource is appropriate only when actual CSS width is 480px or less; preserve maps' readable labels and reconstructed-image labels.
4. Capture source-bound baseline and candidate cold-browser evidence (including all same-image CDP transfer aliases), compare after visual review, and retain a rollback by media ID/URL and Gutenberg slot. No bulk post rewrites or automatic production substitutions.

**All source URLs, copyright/crop uncertainties and candidate dimensions are in the machine-readable matrix.** No new guest image HTTP, asset bytes, page weight, or real-site repair was measured during this batch. No homepage ownership conflict, WP write, image download/copy, merge, deployment or spend.
