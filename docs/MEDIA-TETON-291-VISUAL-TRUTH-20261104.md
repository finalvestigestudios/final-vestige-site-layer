# Media Recovery — Teton Dam post 291: confirmed wrong scene (2026-11-04)

## Concrete editorial/visual integrity incident
Read-only authenticated WordPress `posts.get(id=291,context=edit)` confirms the article remains published, last modified **2026-11-02T21:36:09**, with **six exact src+ALT matches** to the SHA-pinned October 30 inventory (`qa/media-recovery/parts/02.json`, blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`).

**291:2 and 291:5 contain precisely the same source URL:**
`https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG`

An independent visual image viewer **displayed the original photograph**: a commercial street with debris piled up and workers cleaning up after the flood. The Deseret News article contextualizes this photo as flood aftermath: https://www.deseret.com/the-west/2024/06/05/deseret-news-archives-devastation-after-teton-dam-collapse-could-have-been-much-worse/

**Slot 291:2's ALT is demonstrably false** (“Growing breach in Teton Dam during the final hour before collapse.”), and its current caption claims that the failure was photographed frame by frame. **Slot 291:5** uses the same image with a generally appropriate aftermath/cleanup ALT. Six image tags thus contain **five distinct original URLs**, and one illustration materially contradicts the historical narrative. This is a confirmed live **source/subject editorial error**, **not** a confirmed broken image.

## Authoritative candidate mapping, not permission to publish
U.S. National Archives (Record Group 115) describes Jerry Dursteller's exact historical *subject*: a June 5, 1976 photograph showing the breach grow to the crest of the dam, **NAID 28894685**: https://catalog.archives.gov/id/28894685 . Primary archival explanation: https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/

The NARA photograph is an **alternative historical scene, not the same photographic image/crop**. Dursteller was a private contractor; federal archival custody alone **does not establish** 17 U.S.C. § 105 public-domain status. A separate Bureau of Reclamation image from https://www.usbr.gov/pn/snakeriver/dams/uppersnake/teton/8.html documents a different stage and should not be swapped without editorial approval. Deseret's existing photograph also has no established rehosting rights.

**Possible remedies for editorial signoff**: replace 291:2 with a rights-cleared historically correct breach photograph, or correct the ALT/caption to the actual street-cleanup photo and resolve duplicate imagery. Both require staging and before/after visual review; **neither is approved for live WordPress**.

## Six actual source URLs and status methodology
Machine-readable six-row audit: `qa/media-recovery/teton_291_visual_mismatch_20261104.json`. Exact published images **291:0, 291:1, 291:2/5 and 291:4 displayed through independent image viewing**. Complex BYU-Idaho CDN transform **291:3** was inaccessible through the independent retriever, not evidence of visitor failure. All origin HTTP codes, guest `currentSrc`, image decode, browser transfer bytes, and broken-image flags remain **null**. No logged-out Chromium run has occurred.

All six published Gutenberg `img` tags lack width/height attributes. This may cause CLS but **no CLS measurement** exists. Derivatives remain capped at **960 px width without upscaling**; original intrinsic pixel geometry is unverified, so target heights must not be invented.

## Isolated engineering and handoff
Validator: `qa/media-recovery/validate_teton_291_visual_mismatch_20261104.cjs`, tests: `qa/media-recovery/test_teton_291_visual_mismatch_20261104.cjs`. **37/37 isolated V8 regression assertions passed on the exact committed GitHub source** (one baseline, 36 adversarial mutants). Native Node CI and real Chrome remain unexecuted.

Site QA PR #154 owns the existing P0 guest-browser queue (285:5/285:2, 287:5, 418:1/2, 407:1). The Teton item is **P1 editorial**, not a new P0 browser failure; do not alter or duplicate Site QA scripts.

Site-wide baseline is **61 published posts, 355 original image slots, 288 external-source URLs, and 13 WordPress originals >1.5 MiB**. The reported **42 broken** images and **76% transfer reduction** remain unverified by guest-browser/CDP measurements. **Zero** production image repairs, third-party media downloads/caches, WordPress writes, homepage edits or subscription spend.

## Safe future WordPress workflow
Confirm item-specific license, source and attribution; obtain visual editorial signoff; only lawfully retrieve the chosen master; decode intrinsic dimensions; create an aspect-preserving derivative at max 960px, no upscale; test in an isolated staging media library; verify live-fallback/rollback and compare guest-browser screenshots and cold image-wire bytes. No speculative Gutenberg block rewrites or media uploads.
