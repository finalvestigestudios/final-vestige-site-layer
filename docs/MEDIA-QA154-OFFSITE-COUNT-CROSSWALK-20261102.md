# Media Recovery — resolve the Site QA 286 vs. Media Recovery 288 external-source discrepancy
**Evidence date:** 2026-11-02 · **Scope:** offline 61-post source inventory; no guest-browser failure or publication change

## Verified cross-branch finding
PR #154's source-only CSV (blob `76aa63ffaa299a6e6878edc1b66e637fa6f058ab`) reports **61 posts, 355 image elements, 286 offsite `src` references**. The eight frozen Media Recovery inventory parts on PR #183 (their exact Git blob SHAs are in the ledger) report **61 posts, 355 images, 288 offsite references**. All **61 post IDs and per-post image counts agree**. The *entire* two-image difference is localized to just two posts:

| Post | Media #183 external | Site QA #154 external | Candidate source slot and origin |
|---|---:|---:|---|
| 291 — *One Bulldozer Never Came Back* (Teton Dam) | 6 | 5 | `291:0` — `https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1` |
| 285 — *The Light Said Closed* (Three Mile Island) | 6 | 5 | `285:1` — `https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1` |

Both stored images are **third-party publisher images served through the Jetpack image proxy**. Their CDN host is `i0.wp.com`, but their *underlying image owners are not* `finalvestige.com`. They are externally sourced assets in the Media Recovery inventory. Source-only classification for both should distinguish **offsite-origin Jetpack** from **first-party WordPress media proxied through Jetpack**.

**Do not claim PR #154 contains a classifier bug:** its published `classify(src)` code already treats offsite-origin Jetpack URLs as `external` when supplied those exact URLs. PR #154's preserved artifact has only **per-post aggregate counts**, not its individual source `src` evidence. The root cause might be different source HTML snapshots, source rewriting, or an earlier capture; it is **not yet demonstrated**. No count or live status has been overwritten. Resolve the difference using the original source markup/dated snapshot for these exact image keys.

## Primary-source archival leads (NOT licensed replacements)
1. **Teton Dam, `291:0`:** The National Archives' [May 31, 2016 article](https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/) documents the June 5, 1976 progression and **NAID 28894685** for the photograph where the dam breach reaches its crest. This is a **strong scene-level lead**, not a proven byte-identical image/crop. The article identifies **Jerry Dursteller, an employee of a construction contractor**, as the photographer, so **do not presume federal-copyright status simply from National Archives custody**. Source master dimensions unavailable: **maximum 960px width, no upscaling; exact derivative dimensions unknown**. Rights, binary identity and any future WordPress caching remain **HOLD**.
2. **Three Mile Island, `285:1`:** NARA **NAID 540034**, *Control room Number 2. Nuclear Regulatory Commission inspector looking at meters*, dated **April 3, 1979**, is a historically contemporary alternate, **not** verified as the same wide control-room photograph from Squawkpoint. [NARA-derived Wikimedia description](https://commons.wikimedia.org/wiki/File:Control_room_Number_2._Nuclear_Regulatory_Commission_inspector_looking_at_meters._-_NARA_-_540034.tif) records the **3000 × 2023 TIFF** and its federal-public-domain rationale; the official NARA identifier still requires primary item-level confirmation. A conditional **960 × 647** derivative would be within the source geometry; it is **not approved for production**. Confirm creator, exact subject/crop, rights and credit.

Neither of these image slots has a verified guest browser failure. They are candidates explaining a **source-count discrepancy**, not additional members of the founder's unverified **42 claimed broken photographs**. Existing higher-priority visitor visual recovery targets remain `285:5` (SayMedia), `287:5` (Skyway), `407:1` (USGS Hebgen) and `418:1–2` (USCG Scotch Cap).

## Machine evidence and tests
- [61-row crosswalk and two item-level primary-source candidates](../qa/media-recovery/qa154_183_origin_count_crosswalk_20261102.json)
- [Offline fail-closed crosswalk validator](../qa/media-recovery/validate_qa154_183_origin_crosswalk_20261102.cjs)
- [34 regression checks](../qa/media-recovery/test_qa154_183_origin_crosswalk_20261102.cjs)

A replay of the **exact committed source** against all eight real inventory parts and the new ledger passed **34/34 cases**, including baseline/negative source-count fixtures, six archival-licensing mutations, and four additional viewer/HTTP evidence safeguards, in isolated V8 with native Node assertions/load behavior shimmed. Independent native Node execution/CI and logged-out Chrome remain pending. The validator's native loader additionally checks each part against its recorded **Git blob SHA**. The Site QA CSV **blob SHA** is pinned but its original per-image HTML is unavailable on the Media Recovery branch.

Specific new commit identifiers:
- Cross-branch 61-row ledger initially: `db143a72013c57477e4ab8553033b3742671fa3d`
- Offline validator initially: `50716782946fbe0843584d9d4b9783d7ae83a649`
- Regression source initially: `2c597f714269848bc6417c94364416824567dce0`
- NARA item-level candidates/rights HOLD: `296c49441ac567cac67c3d6f96b4c1d0146f44aa`
- Strict archival rights/dimension guard: `7677b9ebd8f7c593f2ec19f2b478300fb8c1faf9`
- Additional adverse tests: `1c71cf463562a80260e738e3e03834dc42088929`

## Nov 2 exact-source rendering recheck (no HTTP claim)
Read-only image-viewer retrieval successfully **displayed the actual stored Jetpack images** for both discrepancy slots:
- Teton dam `291:0`: [exact stored `i0.wp.com` URL](https://i0.wp.com/text-message.blogs.archives.gov/wp-content/uploads/sites/5/2016/05/teton_failing_fourth-scaled.jpg?ssl=1) — original breach photograph visibly rendered.
- Three Mile Island `285:1`: [exact stored `i0.wp.com` URL](https://i0.wp.com/www.squawkpoint.com/wp-content/uploads/2019/02/Three-Mile-Island-Control-Centre.jpg?ssl=1) — original wide control-room photograph visibly rendered.

The viewer supplied **no independently verified origin HTTP code, visitor Chrome request/response, transferred bytes, cache state, intrinsic file dimensions, or copyright grant**. This is **positive independent rendering evidence**, not a reliable guarantee that all visitor browsers can load them. The image scene comparison also reinforces the prohibition on silently swapping Squawkpoint's wide view with a distinct NARA image.

Evidence recorded as `independent_source_image_retrieval` in the machine ledger; validator demands browser/copyright fields remain unknown. Four new adversarial tests reject fake browser HTTP, fake byte transfer, fabricated license permission and false viewer result.

Additional exact commits: viewer evidence `fdd262ac7ed8e310e83d59da01d7f8d11494a385`; strict evidence typing `890ddc1855ceca32ca02e1563ce2859186fcead7`; 34-case test suite `42af979be3e89db6c140568d7e8c87efd6ce0705`.

## Release and transfer-weight gates remain CLOSED
The 13 oversized WordPress originals and five 1672×941 inline PNGs remain storage observations, not page-wire measurements. **76% reduction: NOT MEASURED.** Compute valid savings only from complete paired, same-viewport, fully decoded actual CDP transfer-byte traces with exact request IDs and no missing images. **42 broken: NOT verified** in logged-out visitor Chrome. Do not count image retriever 403/404 as visitor status.

**No image downloading, image mirroring, third-party scraping, asset replacement, 960px derivative generation, rights claim, live WordPress write, post-block rewrite, homepage visual change or paid service.** A future approved replacement would require confirmed broken rendering, original-scene visual match, item-specific reproduction rights, attribution, a safe first-party WordPress media/cache path and fresh mobile/desktop before-after QA.
