# Eight live U.S. Navy images — source retriever batch (2026-11-08 Pacific)

**Scope:** Published [USS Pueblo, post 280](https://finalvestige.com/2026/08/19/the-sledgehammers-broke-first-uss-pueblo/) and [Honda Point, post 288](https://finalvestige.com/2026/08/19/the-bearing-was-right-honda-point/), without altering either article or homepage. WordPress `posts.get(context=edit)` confirmed **8/8 verbatim original image URLs still present** across these two published posts. The reproducible [eight-row source and license ledger](../qa/media-recovery/navy_8_live_pueblo_honda_retriever_20261108.json) includes every exact URL, modified date, target catalog accession, and nullable guest HTTP/currentSrc/bytes/dimensions.

## Actual retrieval findings, with strict method separation

Eight independent `web.open` attempts against the **exact published image URLs**: **5 wrapper timeout (reported as 400), 2 wrapper bad gateway (502), 1 inaccessible to the tool (no HTTP code)**. These are *web-tool wrapper error codes*. They **must not be interpreted as actual Navy origin HTTP codes or visitor-visible broken images**. No guest-browser network/decoding results or image binaries were obtained. Navy's HTML catalog pages, however, were accessible separately, so host-wide blocking of the text/binary retriever is a plausible alternative to genuine user breakage.

| Live slot | Image | Web retriever only | Navy catalog / medium image advertised |
|---|---|---|---|
| 280:0 | Pueblo underway 1967 | 400 timeout | 428-GX-USN-1129207 / 215 KB JPEG (1280px max bounding box) |
| 280:1 | Sailor getting coffee | 400 timeout | NH 75559 / 133 KB JPEG |
| 280:2 | Pueblo messing spaces | 400 timeout | NH 75561 / 152 KB JPEG |
| 280:3 | Pueblo release check-in | 400 timeout | K-64683 / 144 KB JPEG |
| 280:4 | USS Banner photo | Tool inaccessible | exact image record unresolved |
| 280:5 | Pueblo crew eating after release | 400 timeout | K-64728 / 124 KB JPEG |
| 288:0 | Honda Point aerial | 502 wrapper | NH 69586 / 279 KB JPEG |
| 288:2 | Mare Island naval radio | 502 wrapper | exact image record unresolved |

The catalog's advertised KB are **not cold-browser transfer measurements**, and 1280×1280 describes the source's download-rendition envelope, not proof of the image's native aspect ratio. Consequently **no exact proportional 960px dimensions** or 76% reduction have been claimed.

## Rights and historical visual accuracy

NHHC's [Photo Archives policy](https://www.history.navy.mil/our-collections/photography.html) states most photos are public domain but identifies donated and unofficial material and expressly leaves item-level rights clearance to researchers. **NH 69586 is credited to the Naval Historical Foundation / Admiral William V. Pratt collection.** A Navy-hosted photo is not automatically a Navy-created public-domain photo. Hold caching and republication until the item's rights are checked. The other seven stay item-level review pending despite official USN markings in several catalogs.

Verified catalog pages:
- [428-GX-USN-1129207](https://www.history.navy.mil/content/history/museums/nmusn/explore/photography/ships-us/ships-usn-p/uss-pueblo-ager-2/428-gx-usn-1129207.html)
- [NH 75559](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75559.html)
- [NH 75561](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-75000/NH-75561.html)
- [K-64683](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64683.html)
- [K-64728](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g-k/80-G-K-60000/K-64728.html)
- [NH 69586](https://www.history.navy.mil/content/history/nhhc/our-collections/photography/numerical-list-of-images/nhhc-series/nh-series/NH-69000/NH-69586.html)

## Safe handoff and release sequence

Existing **Site QA #154** owns guest Chrome/CDP and should sample these two published posts *after* the six established P0 candidates. Record original `src`, rendered `currentSrc`, complete uncached request/response chain, decoded natural dimensions, captured screenshot and transferred bytes. Only if failure is genuinely visitor-visible: verify exact photo/crop identity and item-level use rights/attribution, confirm original pixels and SHA-256, prepare proportional <=960px no-upscale derivative, test readability/caption fidelity, then seek approval for a controlled future upload. **No WordPress post rewrites, media uploads, third-party binary downloads/cache, homepage modifications, PR merge or spending in this batch.**

## Engineering evidence

- [Machine-readable ledger](../qa/media-recovery/navy_8_live_pueblo_honda_retriever_20261108.json): eight confirmed WordPress source records, six Navy catalog accessions, actual `web.open` wrapper outcomes and null actual-browser fields.
- [Fail-closed validator](../qa/media-recovery/validate_navy_8_live_pueblo_honda_20261108.cjs) + [Node regression suite](../qa/media-recovery/test_navy_8_live_pueblo_honda_20261108.cjs): **20/20 isolated V8 control/mutation checks passed**, plus a check against exact committed sources; native Node and cold logged-out Chromium not executed.
- Source ledger/validator/test blob SHAs: `0fe22f816dce9776d447b3ddfc7d7aeeb75ccad0` / `fe826c2037e7f150855ba4888f6f6bef6ab286e5` / `f0378531ba44c1142326e49eb30d4744eba360d1`.

The historic **61 posts / 355 inline image refs** snapshot and **42 alleged broken images** remain *source-level*, not guest-confirmed. The **76% image transfer reduction remains unmeasured**. The separate live media census shows **15 WordPress originals >1.5 decimal MB, 47,096,779 stored-original bytes**, which cannot be used as a visitor-wire denominator.
