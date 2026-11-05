# P1 VISUAL INTEGRITY — live Teton Dam image 291:2 depicts cleanup, not breach

**Read-only evidence captured November 5, 2026.** No WordPress writes, media binary downloads, downloads from publishers, cached copies, automatic content rewrites, homepage design changes, or spend.

## Confirmed source-level visual mismatch, not a Chrome error

Authenticated WordPress `posts.get(id=291, context=edit)` returns the **published** post *One Bulldozer Never Came Back*, modified **2026-11-02T21:36:09**. Its six `img src` elements match the frozen October 30 media inventory in `qa/media-recovery/parts/02.json` at Git blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`.

The exact same Deseret-hosted URL appears in both **291:2** and **291:5**:

`https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG`

An independent image renderer displayed this precise URL. It depicts **cleanup on a town street amid mud and debris, storefronts, people and vehicles**. It does **not** depict the Teton Dam or an opening in its embankment. Thus image **291:2**, whose ALT reads "Growing breach in Teton Dam during the final hour before collapse." and whose caption claims the failure was photographed frame by frame, has a **source-level historical visual-integrity defect**. Image **291:5**, whose ALT reads "Aftermath of the Teton Dam failure and downstream cleanup in Idaho." and whose actual caption reads "The Teton failure became both a disaster scene and a forensic engineering site.", is subject-appropriate. **Do not remove or replace 291:5 automatically.**

This confirms a **retrieved-original-to-caption mismatch** (source media), **not** the visitor's actual Chrome `currentSrc`, origin HTTP status, CDP wire bytes, source hash, or a browser-broken image. The same image may be loaded twice from a shared request; never count it twice to inflate image weight or savings.

## Historically stronger, differently composed candidate for 291:2

The National Archives at Denver's archivist identifies a June 5, 1976 Jerry Dursteller photo as **NAID 28894685**, showing the hole enlarging to the dam crest:
https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/

The exact NARA/DPLA archival item appears at:
https://commons.wikimedia.org/wiki/File:Teton_Dam_Embankment_Leak_-_DPLA_-_7d121ff5023893a03827fcb49b0d4bd4.jpg

Commons displays the master catalog dimensions **2798 × 1966 px**, giving an aspect-preserving conditional derivative of **960 × 675 px**; never upscale, and visually inspect crop/text/subject. Its rights statement, as assigned by National Archives at Denver through DPLA, is **No Copyright — United States**; it explicitly makes no determination for other jurisdictions or noncopyright rights. A different archival photo is an editorial *substitution*, NOT a recovered matching binary. The chosen candidate has catalog-level subject agreement, not an image-level side-by-side comparison with the historical original breach photo. **No caching, uploading or publishing is authorized by this document.**

Another NARA item **NAID 28894688** is a June 6 post-failure photograph, but it depicts the structure *after the water receded*, not June 5 active breach progression. **Do not substitute 28894688 for 291:2.** It also would not establish the downstream *street cleanup* currently illustrated by 291:5.

## Safe isolated release path (requires separate editorial/reuse/release signoff)

1. Site QA #154 independently tests the live article in logged-out desktop and mobile Chrome after full scroll and captures `currentSrc`, matching network Image response/request ID, decoding, full-height screenshot. Keep all visitor status fields NULL until then; add 291:2 to its **P1 queue**, without changing existing P0 priorities (285:5, 285:2, 287:5, 418:1, 418:2, 407:1).
2. Editor checks that **NAID 28894685**'s photograph actually tells the exact breach-sequence story at slot 291:2 and signs off on any necessary caption/ALT changes; confirm item rights/required attribution, copyright and international claims, and whether selected historical source permits local media storage for this use.
3. If explicitly authorized, create a non-upscaled 960px candidate, preserve original URL/ALT/caption and block-serialization as a rollback record; stage in a nonproduction WordPress environment and visually compare responsive mobile and desktop render, LCP/CLS, loss of historical detail, subject and captions.
4. Prepare a minimal single-image approved Gutenberg mutation with backup and rollback. **No production WordPress writes** in this lane.
5. For 76% claims, only compare actual repeated **cold-browser CDP encoded bytes** on 61 matched posts/355 stored source slots, de-duplicated by requestId, with identical viewport/profile and attribution to approved source changes. The 13 Media Library originals >1.5 MiB (**43,522,829 stored bytes**) are **not** actual transferred bytes; claimed 76% remains unmeasured.

## Deliverables / validation

- Machine audit: `qa/media-recovery/teton_291_live_visual_mismatch_20261105.json` with exact URLs, ALT, current Gutenberg captions, archival rights, no-upscale geometry and explicit null browser measurements.
- Fail-closed validator: `qa/media-recovery/validate_teton_291_visual_20261105.cjs`.
- Mutation tests: `qa/media-recovery/test_teton_291_visual_20261105.cjs`, **27/27 native Node tests passed locally**; tested validator and test blobs match the exact committed Git blobs. Browser/production validations pending.
- Site-wide totals are **frozen prior census** (61 posts, 355 stored refs, 288 offsite by media recovery, 286 by Site QA classification). The **42 claimed broken images remain unverified**. Production repairs = **0**.

Keep this P1 visual-integrity finding separate from Site QA's live-browser collector and the interim lead's homepage visual work.
