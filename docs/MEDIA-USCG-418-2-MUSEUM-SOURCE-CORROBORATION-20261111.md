# Scotch Cap 418:2 — National Coast Guard Museum same-scene source

Evidence date: 2026-11-11. **Isolated research only. No WordPress production, homepage changes, download/cache, deploy, merge or spend.**

## Substantive new evidence

The National Coast Guard Museum article [Standing a deadly watch](https://nationalcoastguardmuseum.org/articles/scotch-cap-lighthouse/), by Coast Guard historian David Rosen (published 2024-10-30), captions a photograph as “Photo of the remains of Scotch Cap Lighthouse taken from the bluff after the 1946 tsunami” and immediately credits **U.S. Coast Guard**. Its displayed image is at:

https://nationalcoastguardmuseum.org/wp-content/uploads/2023/08/5_-Scotch_Cap_debris2_1946-600x463.jpg

Original, frozen WordPress source (post 418, image slot 418:2):

https://www.history.uscg.mil/Portals/6/5_%20Scotch_Cap_debris2_1946.jpg

A [Lighthousefriends copy](https://www.lighthousefriends.com/Scotch_Cap_debris2_1946.jpg) independently displays the same historical bluff/ruins scene. The museum is more authoritative for provenance than that unrelated mirror. There is **no pixel hash match to the inaccessible Coast Guard original** and no original master dimensions. The museum image filename carries a **600×463 thumbnail hint**, not verified original dimensions. The original URL has percent-encoded space; the museum has a different path and a hyphenated normalized filename. This is a *candidate visual correspondence*, not a safe URL rewrite.

## Actual URL observations and classification

- Coast Guard original: web **retriever wrapper 403** on 2026-11-11. NOT established as origin HTTP or visitor Chrome 403.
- Museum preview: web image **displayed** on 2026-11-11, not an independently measured browser GET.
- Lighthousefriends copy: web image **displayed** on 2026-11-11, not an independently measured browser GET.
- Guest Chrome CDP Image requests, network status, caching, intrinsic dimensions and transferred bytes: **all unknown**; Site QA PR #154 retains collection ownership.

## Rights, 960px sizing and staging plan

Museum caption supplies **U.S. Coast Guard attribution**, but no item-level license authorizing Final Vestige to mirror, crop or host the photograph. Coast Guard historical hosting and a non-profit museum's credit are not substitutes for an item-specific rights check. Do not copy from Lighthousefriends or assume their copy grants rights. The related 418:1 photograph is a **portrait of Chief Petty Officer Anthony Pettit**, not the tsunami ruins: never substitute it.

If Site QA actually verifies that 418:2 fails for guests, seek an authorized original master with verified authorship and reproduction policy; confirm scene identity and crop/credit with the editor, calculate output width = minimum of **960px** and verified master width, maintain native aspect ratio without cropping or upscaling, then QA mobile/desktop 1×/2× visual quality and rollback **in staging only**. No production change has been approved.

## Engineering and reproducibility

The source-bound JSON audit is in [uscg_418_2_museum_same_scene_20261111.json](../qa/media-recovery/uscg_418_2_museum_same_scene_20261111.json). It preserves all three exact asset URLs, the wrapper method, candidate credit, sizing unknowns and the rights/WordPress hold. The [validator](../qa/media-recovery/validate_uscg_418_2_museum_20261111.cjs) and [test suite](../qa/media-recovery/test_uscg_418_2_museum_20261111.cjs) reject unsupported guest HTTP and transferred-byte claims, binary identity inflation, inferred licensing, fake 960px derivatives, WordPress writes, and mistaken 76% site-wide measurement. Locally executed **28/28 native Node 22 tests passed**; GitHub checks on the final commit require independent verification.

Historical 61 posts / 355 inline / 288 offsite; 42 originally alleged broken are **guest-unconfirmed**. Expanded 66/361 is a distinct cohort. Fifteen WordPress originals exceed 1.5 decimal MB totaling 47,096,779 **stored** bytes; claimed 76% wire reduction remains **unmeasured**.

**Decision: HOLD.** No collector duplication, no external binary retrieval/caching, no copyrighted asset use, no WordPress writing or subscription spending.
