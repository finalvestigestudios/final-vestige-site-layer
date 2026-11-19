# Redirect-aware cold image integrity — 17 November 2026, 14:31 PT

## Defect addressed
The 61-post slot-parity gate treated a browser image as broken whenever the response URL differed from HTMLImageElement.currentSrc. Legitimate 301/302/303/307/308 server redirects can leave currentSrc at the authored URL while Chromium receives the final GET at another URL. This creates a false HOLD for redirected third-party imagery, particularly Wikimedia sources.

## Safe correction
For a changed final `request_url`, require `redirect_chain` to be an ordered array of **1–6** `{from_url,to_url,http_status}` hops, starting at currentSrc, ending at the final network response URL, with status limited to the five redirect codes and HTTPS-only non-cycling paths. If URLs match, no chain is necessary or allowed. A shared request ID must present identical redirect evidence for every DOM slot. Existing **HTTP 200 final GET, actual positive wire bytes, decoded positive dimensions, screenshot and visual parity, no cache/service worker**, and 61/355 source constraints are unchanged. A *declared* chain is not independent proof: Site QA #154 must corroborate against CDP Network.requestWillBeSent/redirectResponse.

## Fresh independent public observations
- Skyway slot **287:5** old [St Pete Catalyst original](https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg) returned retriever **404**, while [new publisher media URL](https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg) rendered. **Do not call this an observed redirect**: no 3xx chain was recorded. Publisher attributes source image to University Press of Florida. Rights/binary identity remain unapproved.
- Scotch Cap **418:2** old [USCG Portals source](https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg) returned retriever **403**, while [Coast Guard Museum preview](https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg) rendered at **600×463** (do not upscale). Exact binary identity and rehosting rights unknown.
- [USGS Hebgen catalog](https://www.usgs.gov/media/images/hebgen-lake-fault-scarp-1959) identifies photograph as Public Domain by J. R. Stacy; the catalog is HTML and not the binary replacement or tested guest request.

The external media host swaps above are **not approved replacements and are not presumed redirect destinations**. The six P0 browser queue remains 285:5/2, 287:5, 418:1/2, 407:1.

## Test/release evidence
40 preexisting plus 10 new regression definitions; V8 harness runs with URL/Buffer/crypto/structuredClone shims, **not native Node, GitHub CI, nor a live browser**. No new guest browser statuses, 42 broken images or 76% transfer savings asserted. Historical 61-post/355-image inventory is not equivalent to the newer 66 published posts. Oversized WordPress originals are stored bytes, not measured traffic.

## Reversible plan
Site QA #154 supplies read-only logged-out CDP network event and screenshot evidence. Match decoded displayed image against original and official catalog, verify item-level rights/attribution plus source binary SHA-256 and native dimensions, calculate proportional maximum-width **960px** without enlargement. Only then prepare isolated nonproduction WordPress media staging and a precise post-specific rollback plan for review. No WordPress writes, image download/rehosting, Gutenberg rewrite, homepage design changes, merge, deploy, or spend in this change.
