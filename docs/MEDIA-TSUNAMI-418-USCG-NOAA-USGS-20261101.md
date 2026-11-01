# Scotch Cap / 1946 Hilo tsunami: six-image recovery and rights-held cache plan — 2026-11-01

**Scope:** [*The Lighthouse Was Gone at Dawn*, published post 418](https://finalvestige.com/2026/08/20/the-lighthouse-was-gone-at-dawn-1946-tsunami/). Fresh **authenticated, read-only WordPress `posts.get(context=edit)`** returned status `publish`, modified `2026-08-28T03:11:08`, and all **six image URLs plus six full ALT descriptions match** immutable census `qa/media-recovery/parts/01.json` (the frozen file's exact Git blob SHA is recorded in the JSON ledger). No Gutenberg post block rewrites or image downloads.

[Machine-readable exact-URL/source/viewer/browser/rights/size audit](../qa/media-recovery/tsunami_418_uscg_noaa_usgs_20261101.json). [Independent offline validator](../qa/media-recovery/validate_tsunami_418.cjs); [53 adversarial cases](../qa/media-recovery/test_tsunami_418.cjs).

## Actual observations: web retrieval is NOT visitor HTTP verification

| Current published image slot | External origin | Exact-source independent web-viewer observation (2026-11-01) | Guest browser / Image request |
| --- | --- | --- | --- |
| 418:0 | `www.history.uscg.mil` Scotch Cap two-lighthouse JPEG | Tool says URL **not accessible**; no numeric HTTP code returned | **Unknown** |
| 418:1 | `media.defense.gov` officer service portrait `210330-G-DE713-0002.JPG` | Retriever **(403) Forbidden** | **Unknown** |
| 418:2 | `www.history.uscg.mil` Scotch Cap debris JPEG | Retriever **(403) Forbidden** | **Unknown** |
| 418:3 | `www.history.uscg.mil` Scotch Cap ruins JPEG | Tool says URL **not accessible**; no numeric code | **Unknown** |
| 418:4 | `www.hawaiimagazine.com` NOAA-attributed tsunami JPEG | **Displayed** by the independent viewer | **Unknown** |
| 418:5 | `d9-wret.s3.us-west-2.amazonaws.com` USGS derived JPEG | **Displayed** by the independent viewer | **Unknown** |

A media retriever's 403 can be anti-bot/cookie/referrer behavior and does not prove that the browser-visible article image is broken. **No logged-out Chrome `currentSrc`, decoded `naturalWidth`, complete redirect chain, actual Image response status/MIME, encoded transferred bytes, screenshot or LCP/CLS captured.** Container `requests.get` to multiple hosts also failed DNS resolution before any origin response. Do **not** count these as four broken photos, six browser successes, or measured page weight.

## Exact archival/candidate identification and publisher-level rights

| Slot | Primary authority/candidate | Identity confidence | Rights and chronology hold |
| --- | --- | --- | --- |
| **418:0** | [USCG historian Scotch Cap account](https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/) | Direct file hosted on USCG origin and used in historian story; **no separately verified negative/accession** | Government photo collection usually PD **unless otherwise indicated**. Confirm individual photo and credit. |
| **418:1** | [USCG photo gallery](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) — **VIRIN 210330-G-DE713-0002.JPG** | Exact identifier encoded in published DoD JPEG | USCG specifically labels photo **public domain/cleared for release**, requests credit, and warns about DoD image/person/endorsement restrictions. **Conflicting spelling:** photo-page and 2021 historian caption say **Anthony Pettit**; the published FV ALT and namesake cutter use **Anthony Petit**. Keep an editorial review flag; do not silently correct either spelling. |
| **418:2** | [USCG historical Scotch Cap account](https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/) | Direct USCG-hosted `Scotch_Cap_debris2_1946.jpg`, standalone accession unknown | Historical debris subject consistent; individual creator and reuse conditions unverified. |
| **418:3** | [USCG historical Scotch Cap account](https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/) | Direct USCG-hosted `Scotch Cap remains.jpg`; accession and source crop unverified | Exact aerial viewpoint and creator still need comparison against the original; do not change ALT without proof. |
| **418:4** | [NOAA Historic C&GS `pl23_theb2705.jpg` catalog](https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg) | **Only same-event/scene candidate**: NOAA says tsunami inundating Hilo, man on pier. Existing Hawai‘i Magazine photograph displayed; **NOT proven identical** to NOAA candidate. | Source attributed to NOAA but current file is publisher-hosted. Confirm scene, crop, rights/credit before any substitution. |
| **418:5** | [USGS Hilo 1946 damage record](https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946) | Its official **Original** link uses basename `19460401_UNKNOWN_37-012_copy.jpg`; FV uses same basename through USGS `styles/full_width` derivative. **Binary/pixel match not proven.** | USGS page labels **Public Domain** but also names the **original source unknown**. Preserve that caveat, individual photographic authorship check and attribution. |

Source pages: [Coast Guard public-domain-unless-otherwise-indicated photo notice](https://www.history.uscg.mil/Our-Collections/Photos/), [Coast Guard photographer credit and DoD reuse notice](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/), [NOAA historic photograph](https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg), [USGS specific image/rights record](https://www.usgs.gov/media/images/damage-hilo-tsunami-struck-april-fools-day-1946).

**Copyright disposition:** `HOLD` on all six staging/publication actions pending individual identity, terms, credit, crop and authorized editorial review. Even where individual USCG pages indicate public domain, no downloaded binaries or WordPress publication has been authorized.

## Precise ≤960px / first-party caching strategy

1. **Proof before replacement:** Site QA #154's existing logged-out Chrome/mobile probe captures *each exact slot* and the actual decoded `currentSrc` identity, Image response chain/status/content-type, `naturalWidth`/`naturalHeight`, transferred bytes and screenshot. This media-recovery lane owns historical source/rights, not the Site QA classifier.
2. **Acquire only authorized exact master** from publisher's official per-item download once independent rights review permits it, and record master file URL, content hash SHA-256, legal basis, credit, original pixel dimensions and photographic identity. Never scrape at scale, copy a third-party rehost, or equate a different historical photo with the published image.
3. **Derive losslessly reproducible geometry:** `output_width = min(master_width,960)`; `output_height = round(master_height*output_width/master_width)`. Preserve aspect, orientation, documentary detail and **never upscale**. Slot **418:0** filename includes `1200x984`, suggesting **960×787** *if* the verified master really has that geometry. This is an **unverified filename hint, not a measured or approved rendition**. For the other five images, master geometry and output dimensions remain `null` until file inspection.
4. **After editorial signoff only:** stage a first-party WordPress Media Library asset with documented credit/caption and per-image license metadata, confirm generated responsive `srcset`, HTTP `image/*` MIME, cache headers, mobile/browser visual fidelity and unmodified article permalink; obtain separate permission before a minimal scoped block edit (no raw Gutenberg mass rewrite). Third-party original remains available as citation, not as a performance-critical hotlink.
5. **Weight claim verification:** The 13 WordPress originals **>1.5 MiB** are *storage bytes*, not actual visitor image transfers. The reported **76% reduction** would require per-URL and per-slot before/after desktop/mobile encoded network Image bytes on the same pages, successful source identity, fixed cache state, and LCP/CLS comparison; unmeasured savings remain `null` and must not be promoted to a result. The alleged **42 broken images** similarly need logged-out failing Image request and decoded-image evidence.

## Independent tests and coordination

The offline exact-source validator requires all six published URLs, complete ALTs, correct archival IDs and viewer-observation classes while **rejecting fabricated browser HTTP/status/bytes, historic-copyright clearance, unverified dimensions, 42/76% claims, source swaps, wrong photo IDs and any WordPress write authorization**. The 53-case Node test suite was also replayed in an isolated V8 runtime against exact precommit source, **53/53 passed**. Hosted Node Actions and visitor Chrome remain outstanding. No Site QA or homepage files touched.

**P0 handoff to Site QA:** attempt **418:1** and **418:2** first (web retriever 403), then **418:0** and **418:3** (retriever inaccessible without numeric status). Control images **418:4** and **418:5** displayed in viewer, but still require guest browser proof to compare with failing slots. Return actual rendered `currentSrc`, GET Image status/redirects, MIME, encoded wire bytes, decoded dimensions and screenshot; keep all conclusions **unknown** until then.

**Production WordPress changes: 0. Assets downloaded/rehosted: 0. Homepage and Site QA PR edits: 0. Spend: $0.** PR #183 remains independent and draft.
