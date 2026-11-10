# Site QA handoff bridge — authoritative worklist recovered, source-only (2026-11-10)

**Draft PR #1703; DO NOT MERGE, DEPLOY, PUBLISH, DOWNLOAD, CACHE OR MODIFY HOMEPAGE.**

## Correction: IMAGE-WEIGHT-WORKLIST.md DOES exist in draft #183
Earlier notes said `docs/IMAGE-WEIGHT-WORKLIST.md` was unavailable on main and PR #1703. Those branch-local statements were correct but incomplete: the file is present in **draft PR #183**, branch `qa/media-recovery-reviewed-20261030-1158`, Git blob **`2acd06a4ca4317646006eb6591face3fe76fedec`**. It documents a fresh Nov 8 **66-post / 361 inline** cohort and **122** media-image originals, separate from the frozen Oct 30 **61-post / 355 inline / 288 external** research cohort. Do **not** merge counts or compare different cohorts as if paired.

## Machine-readable source handoff
[`browser_handoff_6_p0_15_oversize_20261110.json`](../qa/media-recovery/browser_handoff_6_p0_15_oversize_20261110.json) binds exactly **six P0** stored URLs and catalog candidates, source-retriever-only wrapper outcomes (not origin HTTP), and **15 oversized WordPress originals**, their original URLs, original dimensions, proposed <=960px candidates, item-level rights observations, subsize counts and current-inline post use. Source of truth [43-source/15-media ledger](../qa/media-recovery/cross_ledger_43_source_15_oversize_20261109.json) blob `8526557c7a5138e1ca22a347e3f9839503d48b2c`; full 288 archival register blob `4965a862f7de7de46c1f4a1e26f3ca70a8c38805`.

All **six** P0 statuses, guest currentSrc, browser dimensions and wire bytes remain null. Reuse permission, binary identity, cache and upload approval remain false. A catalog candidate is **not** automatically an exact photograph or approved commercial asset. The historical claim of 42 broken images is not independently guest confirmed.

## Ranked handoff (browser verification is Site QA #154's exclusive responsibility)
1. **P0 (six):** 285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1. Use the **existing collector** in QA #154: actual logged-out `currentSrc`, redirect/status and error, positive intrinsic width+height, response cache flags, cold encoded transferred image bytes, screenshot at mobile+desktop, visual scene integrity.
2. **P1 performance within the 15 stored originals:** current inline originals **11 in eight posts**, especially no-subsize PNG originals **39–43 (posts 34–38)**, Vasa **388/389/382 (post 299; Jetpack fit=1024 already)**, Malbone **1257/1258 (post 621)** and map **1714 (post 269; preserve labels/zoom)**. Remaining four originals **482/405/293/2148** are *not found as inline sources in the 66-post census*; this does not prove they are unused on pages, featured templates or custom blocks.
3. **Historical source reconciliation:** archive research is now **288/288 researched**, not **288/288 verified loaded**. Determine actual missing visitor images before any repair; preserve exact scene, item copyright, crop, caption and accessibility. Historical maps, archival diagrams and schematics may require zoomable original rather than a destructive 960px resize.

## Weight math, exactly what can and cannot be concluded
The **15 originals exceed 1,500,000 decimal bytes each** and total **47,096,779 stored original bytes**, while the **11 inline-matched attachments** total **38,480,915 stored original bytes**. Those are disk sizes **not visitor requests**, and repeated Gutenberg image instances or Jetpack `fit=1024` links may transfer a different byte count. The proposed **76% cold image-transfer reduction has not been measured**.

Do not use unconditional compression claims. The preexisting comparator / CDP components and their tests are owned in **draft PR #183**; this sprint did **not** duplicate or modify those or Site QA's collector (#154). Once actual guest runs are available, evaluate same article/slot source binding, full-scroll same cohort, cold cache flags, successful image MIME, decoded native geometry, source rights and stable visual identity. Only then calculate `100 × (baseline image encoded wire bytes - candidate image encoded wire bytes) / baseline`, and separately report image-load failures, LCP and CLS.

## Safety / tests
[`validate_browser_bridge_20261110.cjs`](../qa/media-recovery/validate_browser_bridge_20261110.cjs) is a pure offline **handoff snapshot integrity** gate (not a collector or general browser comparator). Regression file [`test_browser_bridge_20261110.cjs`](../qa/media-recovery/test_browser_bridge_20261110.cjs) exercises forged guest statuses, invented 76% savings, reordered P0 sources, false rights/cache authorization, media URL/size swaps, source SHA drift and image upscaling. Isolated V8 tests executed during commit; native Node and Chrome not exercised in this runner.

**No source imagery downloaded, no WordPress media or post blocks modified, no production/homepage edits, no new subscription spend.**
