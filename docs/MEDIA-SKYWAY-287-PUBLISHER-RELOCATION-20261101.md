# Sunshine Skyway (post 287) — six-source publisher-relocation and rights-gated image recovery

**Audited 2026-11-01. Draft-only Media Recovery PR #183. No production changes.** This batch advances missing-media identification, not homepage design or Site QA #154's owned guest-browser tooling.

## Highest-value new discovery: 287:5 exact hotlink retriever 404; official publisher has moved the photo

Read-only authenticated WordPress `posts.get(id=287,context=edit)` confirms all **six** image `src` URLs and full `alt` attributes exactly match the frozen census (`qa/media-recovery/parts/03.json`, blob `49183f66f880f7c4dfd363acca906876877f2e5e`); article modified **2026-10-29T18:42:40**.

- **Current stored 287:5:** `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg` → independent **web retriever returned (404) Not Found** on 2026-11-01. This is **NOT a confirmed logged-out Final Vestige browser HTTP 404**.
- **Publisher-linked current candidate:** `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg` → independent retriever **displayed image**, on the same publisher's [April 10, 2020 article](https://stpetecatalyst.com/skyway-disaster-documentary-available-for-streaming/). Identical basename and depicted collapse aftermath strongly support source continuity; **source binary equality, hash, original dimensions and guest-browser response are unknown**.
- **Rights warning:** The publisher explicitly credits **University Press of Florida** for that photograph. Updating the hotlink alone does not establish permission to reproduce or permanently cache it. **Rights HOLD** and no copied asset, first-party upload, post edit, or production change.

This is a candidate for a targeted, reversible editorially authorized fix **after** a genuine browser-visible failure and source/reproduction rights checks.

## All six exact original source observations

| Slot | Stored origin | Independent web retriever (2026-11-01) | Action and rights |
|---|---|---|---|
| 287:0 | `arc-anglerfish-washpost-prod-washpost.s3.amazonaws.com` | Image displayed | Washington Post photo; private photographer/reuse rights **HOLD**; avoid replacing with different car photo. |
| 287:1 | `cloudfront-us-east-1.images.arcpublishing.com/tbt` | Image displayed | Regional newspaper aerial ship photo; exact alternate and photo license **unverified**. |
| 287:2 | `skywaydisaster.com` | Image displayed | Timeline infographic visibly carries **St. Petersburg Times** mark. Publisher copyright **HOLD**; not government artwork. |
| 287:3 | `img.connatix.com` | Image displayed | Overhead black-and-white automobile image differs from 287:0's color roadway photo; never deduplicate by ALT topic. Video thumbnail rights unknown. |
| 287:4 | `www.flmd.uscourts.gov` | Image displayed | Exact image hosted by federal court. Government hosting alone does not establish photographer rights. Current ALT specifically names Summit Venture, whereas visible crane/barge recovery scene does not independently establish vessel identity; **editorial review**. |
| **287:5** | `stpetecatalyst.com/wp-content` | **Retriever 404** | Same-publisher moved URL displayed under `media.stpetecatalyst.com/uploads`; University Press of Florida credit; published ALT claiming *later bridge replacement* deserves correction; **rights and guest-proof HOLD**. |

**Source status methodology:** These six results are independent image-viewer/retriever observations only. No actual browser `currentSrc`, decoded `naturalWidth`, final network HTTP status, MIME, Content-Length/encoded transfer bytes, cache headers, screenshot, LCP or CLS was observed. The web retriever's 404 cannot be promoted to a public origin or guest-browser 404. The old-to-new URL relation is not a proven byte-for-byte match.

## Primary-source and archive crosswalks — do not invent replacements

- [NTSB DCA80AM050 / MAR-81-03](https://www.ntsb.gov/investigations/Pages/DCA80AM050.aspx) is the official collision/safety investigation for **May 9, 1980**. It validates chronology, not ownership of any journalism photo.
- [U.S. District Court, Middle District of Florida — Maritime Matters](https://www.flmd.uscourts.gov/maritime-matters) hosts 287:4's exact photo within its federal maritime case account. The image's photographer/reuse terms still need individual determination.
- [University of South Florida, Gandy 21_0982](https://digitalcommons.usf.edu/gandy/4754/) offers a **separate** documented **January 28, 1982** bridge photo with a stated **CC BY 3.0** license. It is a potential *editorially redesigned context photograph*, not an exact May 1980 collision image and not an automatic substitution.
- [Manatee County digital archive p16681coll1/29937](https://mymanatee.contentdm.oclc.org/digital/collection/p16681coll1/id/29937/) is a separate historical aerial photograph credited to Baldwin; individual item rights and detailed date remain subject to review.
- [Florida Memory DGM0237 (1969)](https://floridamemory.com/items/show/267896) and [DGM0236 (February 1982)](https://floridamemory.com/items/show/267897) are genuine State Archives **before/after contextual views**. Neither is a May 9, 1980 eyewitness disaster photograph or a validated exact replacement.

## Image geometry and safe caching plan

WordPress's stored HTML records **287:0 at 1024×672**; its arithmetic-only width-cap proposal is **960×630**. This is *not verified master pixel geometry* or browser transfer evidence. For **287:1–5, master pixel dimensions are unknown**, so target dimensions remain **null**, not assumed 960px. Keep original aspect ratios, never upscale, and never treat an on-page preview as a verified archival master.

For the relocated 287:5 photograph, the release order is:
1. Site QA #154 independently checks logged-out desktop and mobile viewport/lazy-load of **287:5**, recording actual decoded `currentSrc`, image GET status/MIME/redirects, `naturalWidth`/`naturalHeight`, encoded transfer bytes, screenshot and ALT; test candidate endpoint separately and distinguish anti-bot behavior.
2. Obtain and log permission from the rights holder or choose a *different, properly licensed* image with a separately approved caption. Compare existing and candidate photograph/crop and compute master SHA-256 if authorized to obtain the asset.
3. Prepare a maximum **960px** wide derivative preserving master aspect ratio (no upscale), record exact credit/license/creator/creation date and master/derivative hashes; **do not scrape or mirror unlicensed images**.
4. Stage as a new WordPress Media Library item **outside production**, preserve the live post until editorial/signoff, avoid bulk Gutenberg/source rewrites, and capture screenshot + waterfall against a stable baseline. Reversible per-asset source change only with explicit production approval.
5. Validate mobile transfer and visible render regression before claiming any byte savings; retain rollback original source, ALT and caption.

## Broader 61-post image-performance accounting

The census still covers **61 published posts, 355 stored source slots, 288 external references (286 distinct external URLs)**. **13** WordPress originals exceed **1.5 MiB** and together hold **43,522,829 original bytes**, not transferred bytes; five 1672×941 featured PNG originals have no WordPress subsizes but Jetpack could already serve smaller derivatives. The reported **42 broken photos** remain **unverified by guest browser**, and **76% weight reduction** remains **unmeasured**. Any claimed reduction must compare before/after **same-page, same-device, same-cache policy, decoded-source-identical image GET encoded transferred bytes**, with coverage of all intended image slots, and track LCP/CLS. No production images repaired.

## Machine ledger and regression controls

[`qa/media-recovery/skyway_287_source_relocation_20261101.json`](../qa/media-recovery/skyway_287_source_relocation_20261101.json) preserves exact stored URLs and ALT, separately scoped independent retriever results, documented publisher candidate, primary archive references, rights/caching holds, conditional geometry and **all NULL visitor HTTP/bytes**. [Validator](../qa/media-recovery/validate_skyway_287.cjs) cross-checks the immutable census, exact six identities and guest-proof/release gates; [tests](../qa/media-recovery/test_skyway_287.cjs) use adversarial mutations. **45/45 isolated V8 Node-shim tests PASS on the actual GitHub-committed source** (see engineering log); native Node/hosted CI and guest Chrome remain outstanding.

**Site QA division of labor:** #154 owns logged-out browser acceptance and existing classifier. Media Recovery owns provenance, copyright, source-identification and safe caching/960px plans. No Site QA code was copied or altered.
