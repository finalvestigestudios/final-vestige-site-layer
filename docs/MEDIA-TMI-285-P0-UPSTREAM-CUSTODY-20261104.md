# Media Recovery — Three Mile Island 285, P0 upstream custody and visual truth (2026-11-04)

Scope: Post 285, *The Light Said Closed*. This is independent of homepage design and Site QA PR #154. All CMS access was **read-only**; no WordPress writes, media downloads, CDN operations, subscriptions, or live layout edits occurred.

## Verified source inventory and live CMS

The Oct 30 frozen source-inventory part `qa/media-recovery/parts/03.json` has Git blob `49183f66f880f7c4dfd363acca906876877f2e5e`. Fresh read-only WordPress `posts.get(id:285)` returned **publish**, modified **2026-11-02T21:39:59**. All **six original sources** match the frozen inventory after correctly interpreting WordPress `i0.wp.com` image-proxy paths, HTML `&#038;` query separators, and transform URL percent encoding; all **six ALT strings** match. **All six `<img>` tags lack width+height**, so potential layout shift requires CLS testing. Jetpack-transformed `src` is **not necessarily** the visitor's `currentSrc` or final CDP network destination.

The full exact-source, as-published, conditional rights, and status evidence ledger is [tmi_285_p0_live_wp_source_custody_20261104.json](../qa/media-recovery/tmi_285_p0_live_wp_source_custody_20261104.json).

## Independent retrieval, not visitor status

| Slot | Exact original source host | Independent retrieval | Provenance conclusion |
|---|---|---|---|
| 285:0 | live.staticflickr.com | retriever 403 | Not proof original Flickr or visitor returns 403 |
| 285:1 | i0.wp.com / squawkpoint.com | **displayed** | No transfer-size, runtime decode, CLS evidence |
| **285:2** | blog.ucsusa.org | retriever wrapper 500 with **redirect to blog.ucs.org** | P0 canonical-host drift; no verified origin HTTP 500 |
| 285:3 | i.insider.com | **displayed** when exact `auto=webp&format=jpeg&width=800` used | A visiting group in suits/yellow booties, not the initial shift: historical caption review |
| 285:4 | images.pixels.com | **displayed** labeled TMI-2 end-state **illustration** | Publishing from a commercial image seller does not grant republication rights |
| **285:5** | images.saymedia-content.com | retriever 404 for **original transformed URL** | Highest-priority candidate; still NOT a confirmed guest-visitor 404 |

The live article embeds `i0.wp.com` proxies for 0/1/2/4/5, including the transformed SayMedia URL. Tool `open` of the proxied 285:2/5 variants did not expose readable binary status. No actual visitor browser was available here, and the container networking cannot resolve domains. Therefore all origin/guest HTTP codes, `currentSrc`, `naturalWidth`, decode success, CDP transferred bytes and CLS remain **null**, not inferred.

## Historical imagery alternatives — no silent substitutions

| Proposed for | Archivally cataloged candidate | Intrinsic size → no-upscale maximum | Rights / temporal safeguard |
|---|---|---|---|
| 285:0 | [President's Commission TMI-2 control-room photograph](https://commons.wikimedia.org/wiki/File:TMI-2_control_room.png) | 597×578 → **597×578** | Catalog says government PD; photo depicts **days after incident**, not March 28 operator shift |
| 285:2 | [NRC Carter visit panel detail](https://commons.wikimedia.org/wiki/File:Nuclear_power_plant_control_room_panel_detail,_from-_President_Carter_in_the_TMI-2_Control_Room_(cropped).jpg) | 645×1,013 → **645×1,013** | Different photo/crop; federal PD on catalog; re-caption as Apr 1 rather than imply exact original panel |
| 285:3 | [NRC Carter visit, Commons archival rendition](https://commons.wikimedia.org/wiki/File:President_Carter_in_the_TMI-2_Control_Room.jpg) | 1,267×1,024 → **960×776** | Apr 1 visit; do not call this "personnel during accident response" unless explicitly contextualized |
| 285:5 | [Marque1313's June 2010 TMI photo](https://commons.wikimedia.org/wiki/File:Three_mile_island_062010.jpg) | 819×614 → **819×614** | Photographer-declared PD-self; distinct image and era; **not verified same aerial angle** as publisher image |

All four remain **NOT APPROVED** for upload. Rights review must verify each individual work, underlying photographer/organization and desired reuse; Government-archive presence alone is not enough. Image subject, crop, scene/date and attribution must match the intended narration. Neither upscale <960px source masters nor invent a 960px derivative height.

A separate finding affects 285:3: the displayed image shows suited figures wearing yellow overshoes. Contemporaneous and later accounts identify **President Carter's visit on April 1, 1979**, four days after the initial incident, as taking place in that control room. This supports an **editorial-check hypothesis**, not a facial identification or exact-photo archival match. Avoid presenting visiting dignitaries as the control operators during the March 28 accident. References: [Commons NRC photo](https://commons.wikimedia.org/wiki/File:President_Carter_in_the_TMI-2_Control_Room.jpg), [PBS American Experience transcript](https://cgi.pbs.org/wgbh/amex/three/filmmore/transcript/transcript1.html), [WGAL Dec 30 2024 Carter visit retrospective](https://www.wgal.com/article/pennsylvania-jimmy-carter-three-mile-island/63306612).

## Guest-Chrome acceptance and safe WordPress release sequence

Site QA #154 owns browser-only P0 and should keep **285:5 → 285:2 → 287:5 → 418:1/2 → 407:1**. For 285:5 and 285:2 capture from a logged-out desktop and mobile cold browser: exact document image `src`, browser `currentSrc`, response redirect chain, final GET HTTP status, MIME, byte body, `naturalWidth`/`naturalHeight`, `decode()` result, screenshot, post CLS and CDP `Network.loadingFinished.encodedDataLength` attributable to image requests. Compare the final CDN hosts, not merely original HTML host names. Check a working control image 285:1. Mark `BROKEN` only when the actual rendered image fails and response/decode evidence agrees.

After that, prefer correcting the **existing upstream URL** if source publisher provides an exact legally embeddable replacement and the same visual scene survives. If that is impossible, obtain item-specific reuse rights and a suitable archival master; stage a credited, non-upscaled derivative at max 960px through reviewed WordPress media, preserving image location, caption, alt semantics and responsive dimensions. Verify in staging both cold and warm browser loads and visual comparison before separately authorizing a production write. Do **not** rewrite raw Gutenberg blocks indiscriminately or mirror third-party binaries absent rights.

The 61-post/355-image frozen cohort and 288 external origins are source metadata, not visitor network evidence. Original WordPress Media Library's 13 oversized files are **stored** originals, not page-wire transfers. The reported **42 broken images** and **76% reduction** remain unverified. The evaluator's strict claim must continue to require matching 61 posts/355 slots, full image identities, 3 cold comparable repeats and pooled bytes (not median of per-run percentages). **Production repairs: 0.**

## Regression

- [Validator](../qa/media-recovery/validate_tmi_285_20261104.cjs) checks six pinned original URLs, live proxy normalization, ALT integrity, tool/error semantics, null browser data, 960px and source-size caps, historical nonidentity, rights/release holds and no fabricated performance claims.
- [24-case adversarial test suite](../qa/media-recovery/test_tmi_285_20261104.cjs): **24/24 passed on the exact committed GitHub sources in an isolated V8 Node-compatible harness**; this is **not native Node CI** and not real Chrome testing. The native `node --test qa/media-recovery/test_tmi_285_20261104.cjs` and `node qa/media-recovery/validate_tmi_285_20261104.cjs` are required before release.

No edits to Site QA #154, the homepage, production WordPress, or any image binaries.
