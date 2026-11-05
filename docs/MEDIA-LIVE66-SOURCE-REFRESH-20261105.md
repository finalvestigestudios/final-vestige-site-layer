# November 5 live-source census refresh — 66 published posts / 361 stored inline images

**Owner:** FV Media Recovery. **Status:** isolated read-only evidence and offline QA; NOT deployed. **Scope exclusion:** interim homepage art direction and Site QA #154's actual Chrome collector.

## Fresh evidence, not the historical October 30 denominator

Read WordPress **posts.list(status=publish, per_page=100)** and verified that the collection is complete: **66 posts, 1 page**. Then independently read **all 66** with **posts.get(context=edit)** and parsed stored Gutenberg `<img src>` elements into six 12/12/12/12/12/6-page JSON parts in `qa/media-recovery/live66_parts/`. Counted and recorded original source URLs, host, original ALT, declared geometry, source URL requested width, and exact WordPress post IDs. These are editorial HTML source references, NOT runtime browser `currentSrc`, CSS background images, featured media, CDN transfers or image responses.

| Fresh source census (2026-11-05) | Value |
|---|---:|
| Published posts (complete read) | **66** |
| Stored inline `img[src]` slots | **361** |
| Unique exact source URLs | **359** |
| Direct first-party sources | **60** |
| First-party Jetpack proxy | **7** |
| External origins, including foreign Jetpack proxies | **294** |
| Wikimedia Commons Special:Redirect/file | **124** (subset of 294) |
| <img> without both numeric width and height | **311** (NOT proven CLS) |
| Original URL `width=` queries over 960px | **79** (all `1280`; NOT actual browser pixel/byte proof) |
| Missing ALT in stored inline tags | **0** |
| Visitor-browser-confirmed broken images | **UNKNOWN** (reported 42 NOT verified) |
| Visitor image-wire reduction | **UNKNOWN** (reported 76% NOT verified) |
| WordPress changes / file binary copies in this sprint | **ZERO** |

**Drift result:** All **355** source URLs in the previous **61** frozen posts were matched by exact **post:slot** identity to the fresh WordPress content; **zero old-source URL drifts**. Six **new** external URLs appear in five posts added November 2 (one of the five, Change Blindness post 1922, contains no stored inline `<img>` and this is not necessarily a visitor-facing missing image). The fresh 294 external refs are precisely the frozen 288 plus six new Wikimedia redirect sources. Earlier Site QA #154 historical 286 vs 288 difference came from two offsite Jetpack upstream URLs; **use host identity, not proxy host alone**. Original full 61-post baseline is linked in summary JSON; upstream audit blob `921e09ec4a26f69cc5063e867efacbc16070a36a`.

## Six new images — primary catalog and rights work remains

| Image | Content | Exact source URL | URL width request | Proposed ceiling |
|---|---|---|---:|---|
| 1926:0 | Crystal skull, British Museum display | https://commons.wikimedia.org/wiki/Special:Redirect/file/Crystal%20Skull%20British%20Museum%2026072013%2005.jpg?width=900 | 900 | max 900 from requested rendition, binary dimensions UNKNOWN |
| 1924:0 | *Le Baquet de Mesmer*, Wellcome engraving | https://commons.wikimedia.org/wiki/Special:Redirect/file/%22Le%20Baquet%20de%20Mesmer%22%20Wellcome%20M0006352.jpg?width=900 | 900 | max 900 from requested rendition, binary dimensions UNKNOWN |
| 1920:0 | Lycurgus Cup frontal museum photograph | https://commons.wikimedia.org/wiki/Special:Redirect/file/Front%20of%204th%20century%20CE%20Roman%20Lycurgus%20Cup%2C%20British%20Museum%20%281958%2C1202.1%29.jpg?width=1280 | 1280 | <=960 conditional, source master dimensions UNKNOWN |
| 1920:1 | Lycurgus Cup green/red top view | https://commons.wikimedia.org/wiki/Special:Redirect/file/Top%20view%20of%20the%20famed%20Lycurgus%20Cup%20in%20the%20British%20Museum%2C%20showing%20the%20glass%20both%20green%20and%20ruby%20red.jpg?width=1280 | 1280 | <=960 conditional, source master dimensions UNKNOWN |
| 1917:0 | Piri Reis 1513 chart detail | https://commons.wikimedia.org/wiki/Special:Redirect/file/Piri%20reis%20world%20map%2001.jpg?width=1280 | 1280 | <=960 conditional, cartographic readability HOLD |
| 1917:1 | Cantino 1502 planisphere | https://commons.wikimedia.org/wiki/Special:Redirect/file/Cantino%20planisphere%20%281502%29.jpg?width=1280 | 1280 | <=960 conditional, cartographic readability HOLD |

All are **exact published original source URLs**, NOT verified redirects, binaries, positive browser loads or approved copies. **Rights/rehosting HOLD**: the Wikimedia redirect service is not a blanket license, and museum/archive-hosted material may carry photo-specific terms. Check each Commons file page's attribution/licensing and original custodial metadata; British Museum/Wellcome/source institutions are candidates for provenance research, not pre-cleared replacement media. No downloading, scraping or rehosting. For technical maps, evaluate whether 960px inline and a separately permitted legible zoom are appropriate, rather than silently degrading historical evidence.

## Six existing P0 targets still unchanged in fresh WordPress source

Site QA #154 owns actual logged-out browser CDP checks for **285:5, 285:2, 287:5, 418:1, 418:2, 407:1** in that order. Fresh complete source scan did **not** find original URL drift at those slots. The earlier reported 42 failures are a **hypothesis**, not a verified browser count. A web retriever's 404/403/500 wrapper must not be promoted to a visitor-browser HTTP result. One genuine P1 source/caption mismatch, **291:2 vs 291:5**, remains separate from browser failure.

For each suspected missing asset the independent browser QA must provide final `currentSrc`, CDP Image request ID, redirect chain, actual response MIME/status or failure, `naturalWidth/naturalHeight` and `complete`, desktop/mobile screenshot plus CDN/referrer/caching conditions. Do not launch duplicate Site QA collectors.

## Weight / >1.5 MiB original file backlog, separate from browser transfer

The last read-only Media Library recheck on November 4 identified **13 WordPress original media binaries >1,572,864 bytes**, total **43,522,829 bytes of stored originals**. This is **not** 43.5MB of visitor traffic. Priority after verified breakage: posts 34–38 have five no-registered-subsize first-party 1672×941 PNGs, totaling **13,267,538 stored bytes**; Malbone post 621 directly references two high-resolution JPEG originals, totaling **10,352,064 stored bytes**; Vasa post 299 has three large JPEG originals but currently routes through Jetpack `fit=` derivatives, so it may already be right-sized. Three more >1.5MiB media files lack live-post mapping from selected previous read; never assume unused or delete.

**76% claim protocol:** collect representative cold, uncached, identical viewport + article-scroll desktop/mobile guest-browser baselines; validate image identities, fetch completion and positive encodedDataLength per unique CDP request ID; separate browser memory/disk/Jetpack caches and retries; preserve aspect ratio, ALT, actual image content and readable diagrams; stage appropriately licensed <=960px derivatives only after rights review; collect paired after-runs with identical profiles; compute `100*(baseline_encoded_bytes - candidate_encoded_bytes)/baseline_encoded_bytes` only on matched evidence. Do not count original WordPress file sizes or URL width selectors as transferred bytes. Existing comparator in Media Recovery #183 can adjudicate laboratory pairs; it never permits a sitewide 76% inference from a single pair.

## Publication and rollback release gate — no production writes here

1. Confirm an actual guest-browser failure and specific historically correct image identity. If current source works, avoid unnecessary replacements.
2. Verify creator/custodian, item-specific rights, credit/attribution, color/crop/chronology, and sufficient original pixel dimensions. No upscale; conditional 960px maximum, except explicit approved legibility use.
3. Obtain and hash media lawfully, stage locally or in a *separately authorized* WordPress media workflow, preserve original post source and record prechange screenshot.
4. Before any separately approved reversible edit, validate both viewports, ALT/captions, layout shift, source identity and paired bytes; preserve rollback original URL/media IDs.
5. On regressions, restore original post blocks/media references and rerun guest-browser visual and link checks.

**This PR does not authorize steps 3–5.** Existing Site QA and homepage branches untouched. No subscriptions/spend. Media Recovery PR #183 remains the original archive/candidate work; this **new** PR only refreshes the entire source census and provides an evidence-reconciliation validator.

## Reproduction

```bash
node --test qa/media-recovery/test_validate_live66_source_drift_v1.cjs
node qa/media-recovery/validate_live66_source_drift_v1.cjs qa/media-recovery/live66_parts/{01,02,03,04,05,06}.json
# Optional strict historical zero-drift crosscheck: append the exact previous 61-post audit JSON from PR #1131
```

**22/22 isolated V8 checks passed** using exact current six GitHub JSON files and prior audit: one valid full reconciliation + 20 unsafe/current-data mutations + one forged older source. Native Node CI and guest Chromium remain pending; do not misrepresent them as run.
