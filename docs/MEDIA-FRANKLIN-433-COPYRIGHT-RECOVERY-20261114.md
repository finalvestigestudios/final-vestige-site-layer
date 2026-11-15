# Franklin expedition images: rights and fallback source audit — November 14, 2026 PT

**DRAFT ONLY — zero WordPress writes, downloaded media, caching, homepage changes, merges or spending.**

Fresh authenticated WordPress **read-only** inspection of published post #433, *All Well Was Written First*, modified `2026-11-02T21:37:26`, found six stored Gutenberg image URLs, **five third-party**. Exact original `src` values, ALT, rights notes and nullable browser/HTTP status fields are recorded in `qa/media-recovery/franklin_433_custody_20261114.json`. External catalog and image reader results are **not** verified visitor or origin HTTP responses.

## High-value copyright finding: Fitzjames photograph (433:5)

The published caption states **“Richard Beard daguerreotype; public domain.”** The [exact Wikimedia Commons file](https://commons.wikimedia.org/wiki/File:L23402-c8qmb-t3-05-rx.jpg) instead describes a **2023 photograph by FabTet** of the historic daguerreotype, licensed **CC BY-SA 4.0**. The 1845 object and the more recent uploaded photograph require distinct consideration; simply labeling the entire displayed file public domain is incomplete. Do **not** infer infringement. Any future derivative or WordPress cache requires review of attribution, link to [license](https://creativecommons.org/licenses/by-sa/4.0/), change indication and share-alike obligations. Submit caption correction through editorial review, **not automated Gutenberg rewrite**.

## Potential recovery lead: Admiralty reward notice (433:6)

The existing [CloudFront-hosted poster](https://d3d0lqu00lnqvz.cloudfront.net/media/media/cea975ac-62ed-4c2f-bf13-67a0f3a90092.jpg) was rendered by an external image reader. No visitor failure was established. A historical [Commons candidate](https://commons.wikimedia.org/wiki/File:Reward_for_finding_Franklin_Expedition.jpg) (726 × 1119 px) and a [British Admiralty document transcript](https://canadianmysteries.ca/sites/franklin/archive/text/RewardPoster_en.htm) give matching notice text and cite archival series **Admiralty 7/187**, with Library and Archives Canada provenance. Exact CloudFront-to-Commons binary, edition, crop and host republication rights are **unverified**. No 960px upscale or asset copying.

## Six image records: candidate, rights and maximum no-upscale dimensions

| Slot | Archive/source catalog | Native | Max 960px derivative | Rights/provenance hold |
|---|---|---:|---:|---|
| 433:1 | [Commons scan from 1869 printed work](https://commons.wikimedia.org/wiki/File:Franklinexpeditionnote.jpg), original [Royal Museums Greenwich HSR/C/9/1](https://www.rmg.co.uk/collections/archive/rmgc-object-504898) | 1576×2506 | 960×1526 | PD assertion on book scan, not museum's object-photo rights |
| 433:2 | [Illustrated London News 1845 engraving](https://commons.wikimedia.org/wiki/File:HMS_Erebus_and_Terror_-_ILN_1845.jpg) | 750×523 | **750×523** | PD assertion; never upscale |
| 433:3 | [University of Washington Special Collections Portraits 2459](https://commons.wikimedia.org/wiki/File:Dr_John_Rae,_with_relics_from_the_Franklin_Expedition,_gold_medal,_and_map,_August_1886_(PORTRAITS_2459).jpg) | 399×600 | **399×600** | PD assertion but Commons warns catalog metadata may need verification |
| 433:4 | [British Library 1860 historical map](https://commons.wikimedia.org/wiki/File:(1860)_Map_of_the_probable_routes_taken_by_HMS_Erebus_and_HMS_Terror_during_Franklin%27s_lost_expedition_%26_results_of_McClintock%27s_Arctic_Expedition.jpg) | 1477×2357 | 960×1532 | PD assertion; small type may become illegible |
| **433:5** | [FabTet's 2023 photo of Fitzjames](https://commons.wikimedia.org/wiki/File:L23402-c8qmb-t3-05-rx.jpg) | 3284×3966 | 960×1159 | **CC BY-SA 4.0**, not an automatically cleared public-domain copy |
| 433:6 | [1850 Admiralty reward candidate](https://commons.wikimedia.org/wiki/File:Reward_for_finding_Franklin_Expedition.jpg) | 726×1119 | **726×1119** | Underlying PD assertion; hosted photo not binary matched or licensed |

These sizes reflect catalog-native dimensions and are **planning ceilings only**. They are not new image files. Test actual rendered CSS width × device pixel ratio against candidate dimensions. Preserve text legibility and caption accuracy, especially the map and posters.

## Release, caching and verification plan

1. Site QA **PR #154 exclusively owns** the original six P0 guest-browser investigations (285:5, 285:2, 287:5, 418:1, 418:2, 407:1). This is an independent archival rights audit, not a second browser collector.
2. Record completed cold visitor DOM state, `currentSrc`, `naturalWidth/Height`, network response and actual transferred bytes before classifying a missing image. The 42 historically reported broken external URLs remain **unconfirmed in a guest browser**.
3. Inspect exact-scene identity, original item rights, author credits, visual crop and CSS × DPR. A public-domain historic work does not always mean a modern photograph/reproduction has the same licensing.
4. If authorized, generate responsive derivatives **at most 960px wide without upscaling**, preview on a reversible nonproduction WordPress staging copy, preserve ALT/caption/source links and rollback before considering any production changes. No third-party binary copied or cached during this investigation.
5. The **76% transferred-byte reduction remains hypothetical**. The latest verified 16 WordPress originals above 1,500,000 decimal bytes total **49,107,665 stored bytes**; this is not the quantity transferred to visitors.

Offline checks: `node --test qa/media-recovery/test_franklin_433_custody_20261114.cjs` and `node qa/media-recovery/validate_franklin_433_custody_20261114.cjs`. Fail-closed result remains `HOLD`. Native Node and full repository CI must be independently checked; isolated tests do not certify guest-browser behavior.

**Worklist note:** `docs/IMAGE-WEIGHT-WORKLIST.md` was not found on the repository default branch, and code search found no corresponding file. This audit uses explicit source snapshots and the Site QA PR #154 census rather than pretending the worklist was reviewed.
