# Sunshine Skyway 287 — two observed editorial visual mismatches (2026-11-14 PT)

Scope: **media visual accuracy only**. Read-only authenticated WordPress `context=edit` on published post #287, last modified 2026-11-02 21:40:01, plus independent image retriever visual observations. This is an editorial change proposal, **not a publication authorization or demonstration of guest browser failure**.

## Two confirmed source-image/description disagreements

1. **287:4, federal court-hosted image**: Published ALT says the photograph shows the *Summit Venture*, and its figure caption names that ship. Image actually shows dislodged steel bridge sections, a crane/work barge and other work vessels alongside. None can responsibly be labeled Summit Venture from this evidence. Review proposed ALT: `Oblique aerial view of broken Sunshine Skyway Bridge spans with cranes and work vessels during recovery operations.` Review proposed caption: `Broken Sunshine Skyway spans with cranes and work vessels during recovery operations. Federal court-hosted image.` The original exact image URL and publisher provenance are in the JSON. Web retriever rendered the image; actual guest image HTTP remains unknown. **Do not assume government site hosting makes the photo public-domain**.
2. **287:5, St Pete Catalyst image**: Published ALT says a *later replacement bridge* appears, but the publisher's currently accessible same-filename image shows the 1980 damaged bridge and the ship identified by the publisher as **Summit Venture**. Proposed ALT: `The freighter Summit Venture beside the collapsed original Sunshine Skyway Bridge following the May 1980 collision.` The existing contextual figcaption is not proposed for alteration. The stored original `stpetecatalyst.com/wp-content/uploads/...` returned independent web-retriever **404 wrapper**; the publisher's newer `media.stpetecatalyst.com/uploads/...` rendition displayed. Neither is a guest-browser HTTP test, binary/crop hash comparison, or license. Publisher credits **University Press of Florida**, so copying/caching/rehosting is on HOLD.

## Source records

- Published post: https://finalvestige.com/2026/08/19/the-warning-was-a-man-waving-sunshine-skyway/
- Federal court-hosted image (visual observation): https://www.flmd.uscourts.gov/sites/flmd/files/images/figure-9-sunshine-skyway-bridge-3.jpg
- Publisher's article and credit: https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/
- Publisher's displayed rendition: https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg

## Safe isolated review and staging plan

- This PR contains proposed ALT/caption **text as data only**; no Gutenberg block rewrites and no WordPress production writes. Have an editor approve before independently drafting a reversible, single-image-figure staging patch with before/after screenshots. Re-read post modified timestamp immediately before any authorized edit; preserve neighboring Gutenberg markup and existing source/credit.
- Site QA PR #154 retains exclusive browser collector and original six-image P0 queue (285:5, 285:2, 287:5, 418:1, 418:2, 407:1). If 287:5 is a real visitor failure, collect exact currentSrc, image error, response/redirect and cache provenance, natural pixel dimensions, viewport/DPR and bytes; the 404 web-retriever wrapper is not enough.
- Do not mirror or download the publisher/court images until item-level copyright/republication rights, scene, composition/crop and true source dimensions are verified. If later approved, a 960px maximum derivative with no upscaling is *conditional*, not an order to create it. Compare rendered CSS width against DPR, preserve figure legibility and avoid mixed-scene substitutes. WordPress media localization would be a separate, reversible staging proposal with correct credit and rollback.
- Historical frozen 61-post/355-inline cohort is separate from later 66/361. The 42 alleged broken sources are still guest-unconfirmed; 76% visitor network savings remain unmeasured. Latest read-only media inventory is 123 original image records; 16 originals strictly over 1,500,000 bytes total **49,107,665 stored original bytes**. These are not visitor transfer bytes. No production image repairs or performance reduction claimed.

## QA

Run `node --test qa/media-recovery/test_skyway_visual_fidelity_287_20261114.cjs` and `node qa/media-recovery/validate_skyway_visual_fidelity_287_20261114.cjs`. Validation fails closed on 26 adverse mutations: fabricated visitor HTTP/dimensions/bytes, false rights/caching/960px permissions, mismatched exact published source, wrong scene descriptions, or production write authorization. Do not modify homepage design or Site QA files; do not merge, deploy, rehost, scrape or spend.
